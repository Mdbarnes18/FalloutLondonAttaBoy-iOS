package com.falloutlondon.companion

import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.DataInputStream
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.Socket
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject

sealed interface PipboyUpdate {
    data class Data(val records: List<PipboyRecord>) : PipboyUpdate
    data class LocalMap(val map: PipboyLocalMapUpdate) : PipboyUpdate
    data class CommandResponse(val json: String) : PipboyUpdate
    data class Handshake(val json: String) : PipboyUpdate
    data object Refused : PipboyUpdate
    data class Unknown(val type: Int, val payload: ByteArray) : PipboyUpdate
}

data class PipboyLocalMapUpdate(
    val width: Int,
    val height: Int,
    val northWest: Pair<Float, Float>,
    val northEast: Pair<Float, Float>,
    val southWest: Pair<Float, Float>,
    val pixels: ByteArray
)

sealed interface PipboyRecord {
    data class Value(val nodeId: Long, val value: PipboyValue) : PipboyRecord
    data class Array(val nodeId: Long, val children: List<Long>) : PipboyRecord
    data class Object(val nodeId: Long, val added: List<Pair<String, Long>>, val removed: List<Long>) : PipboyRecord
}

sealed interface PipboyValue {
    data object Null : PipboyValue
    data class Bool(val value: Boolean) : PipboyValue
    data class Int8(val value: Byte) : PipboyValue
    data class UInt8(val value: Int) : PipboyValue
    data class Int32(val value: Int) : PipboyValue
    data class UInt32(val value: Long) : PipboyValue
    data class Float32(val value: Float) : PipboyValue
    data class StringValue(val value: String) : PipboyValue
}

object PipboyPacketDecoder {
    fun decode(type: Int, payload: ByteArray): PipboyUpdate? = when (type) {
        1 -> PipboyUpdate.Handshake(payload.toString(Charsets.UTF_8))
        2 -> PipboyUpdate.Refused
        3 -> decodeDataUpdate(payload)?.let(PipboyUpdate::Data)
            ?: PipboyUpdate.Unknown(type, payload)
        4 -> decodeLocalMap(payload)?.let(PipboyUpdate::LocalMap)
            ?: PipboyUpdate.Unknown(type, payload)
        6 -> PipboyUpdate.CommandResponse(payload.toString(Charsets.UTF_8))
        else -> PipboyUpdate.Unknown(type, payload)
    }

    // Decode atomically: a malformed tail must never apply a valid-looking prefix.
    private fun decodeDataUpdate(bytes: ByteArray): List<PipboyRecord>? {
        val input = DataInputStream(ByteArrayInputStream(bytes))
        val records = mutableListOf<PipboyRecord>()
        fun u8() = input.readUnsignedByte()
        fun u16() = u8() or (u8() shl 8)
        fun u32() = u8().toLong() or (u8().toLong() shl 8) or (u8().toLong() shl 16) or (u8().toLong() shl 24)
        fun i32() = u32().toInt()
        fun f32() = Float.fromBits(i32())
        fun cstring(): String {
            val out = ByteArrayOutputStream()
            while (true) {
                val byte = u8()
                if (byte == 0) break
                out.write(byte)
            }
            return out.toByteArray().toString(Charsets.UTF_8)
        }

        return try {
            while (input.available() > 0) {
                when (val type = u8()) {
                    0 -> records += PipboyRecord.Value(u32(), PipboyValue.Bool(u8() != 0))
                    1 -> records += PipboyRecord.Value(u32(), PipboyValue.Int8(u8().toByte()))
                    2 -> records += PipboyRecord.Value(u32(), PipboyValue.UInt8(u8()))
                    3 -> records += PipboyRecord.Value(u32(), PipboyValue.Int32(i32()))
                    4 -> records += PipboyRecord.Value(u32(), PipboyValue.UInt32(u32()))
                    5 -> records += PipboyRecord.Value(u32(), PipboyValue.Float32(f32()))
                    6 -> records += PipboyRecord.Value(u32(), PipboyValue.StringValue(cstring()))
                    7 -> {
                        val id = u32()
                        records += PipboyRecord.Array(id, List(u16()) { u32() })
                    }
                    8 -> {
                        val id = u32()
                        val added = List(u16()) { u32() to cstring() }.map { it.second to it.first }
                        val removed = List(u16()) { u32() }
                        records += PipboyRecord.Object(id, added, removed)
                    }
                    // Type 9 is not in the documented 0–8 baseline. Preserve it as unknown.
                    else -> return null
                }
            }
            records
        } catch (_: Exception) {
            null
        }
    }

    private fun decodeLocalMap(bytes: ByteArray): PipboyLocalMapUpdate? = runCatching {
        val b = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
        require(b.remaining() >= 32) { "Truncated local map header" }
        val width = b.int
        val height = b.int
        require(width in 1..4096 && height in 1..4096) { "Invalid local map dimensions" }
        val nw = b.float to b.float
        val ne = b.float to b.float
        val sw = b.float to b.float
        val expectedPixels = width.toLong() * height.toLong()
        require(expectedPixels <= 16_777_216L && b.remaining().toLong() == expectedPixels) {
            "Local map pixel payload does not match dimensions"
        }
        val pixels = ByteArray(expectedPixels.toInt()).also(b::get)
        PipboyLocalMapUpdate(width, height, nw, ne, sw, pixels)
    }.getOrNull()
}class PipboyDatabase {
    data class Node(
        val id: Long,
        var value: PipboyValue? = null,
        val objectChildren: MutableMap<String, Long> = mutableMapOf(),
        var arrayChildren: List<Long> = emptyList()
    )

    val nodes = mutableMapOf(0L to Node(0L))
    var localMap: PipboyLocalMapUpdate? = null
        private set

    var loggingEnabled: Boolean = false
    val updateLog: MutableList<String> = mutableListOf()

    private fun appendLog(message: String) {
        if (!loggingEnabled) return
        val stamp = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", java.util.Locale.US)
            .format(java.util.Date())
        updateLog.add("$stamp: $message")
        if (updateLog.size > 10_000) updateLog.removeAt(0)
    }

    fun logConnectionEvent(message: String) = appendLog(message)
    fun clearUpdateLog() { updateLog.clear() }

    private fun pathForNode(target: Long): String? {
        val visited = mutableSetOf<Long>()
        fun walk(id: Long, path: String, depth: Int): String? {
            if (id == target) return path.ifEmpty { "ROOT" }
            if (depth > 64 || !visited.add(id)) return null
            val current = nodes[id] ?: return null
            for ((key, child) in current.objectChildren) {
                val found = walk(child, if (path.isEmpty()) key else "$path.$key", depth + 1)
                if (found != null) return found
            }
            current.arrayChildren.forEachIndexed { index, child ->
                val found = walk(child, "$path[$index]", depth + 1)
                if (found != null) return found
            }
            return null
        }
        return walk(0L, "", 0)
    }

    private fun valueType(value: PipboyValue): String = when (value) {
        is PipboyValue.Null -> "null"
        is PipboyValue.Bool -> "bool"
        is PipboyValue.Int8 -> "int8"
        is PipboyValue.UInt8 -> "uint8"
        is PipboyValue.Int32 -> "int32"
        is PipboyValue.UInt32 -> "uint32"
        is PipboyValue.Float32 -> "float"
        is PipboyValue.StringValue -> "string"
    }

    private fun valueText(value: PipboyValue): String = when (value) {
        is PipboyValue.Null -> "null"
        is PipboyValue.Bool -> value.value.toString()
        is PipboyValue.Int8 -> value.value.toString()
        is PipboyValue.UInt8 -> value.value.toString()
        is PipboyValue.Int32 -> value.value.toString()
        is PipboyValue.UInt32 -> value.value.toString()
        is PipboyValue.Float32 -> value.value.toString()
        is PipboyValue.StringValue -> value.value.replace("\n", "\\n").replace("\r", "\\r")
    }

    fun reset() {
        appendLog("Root Object resetted.")
        nodes.clear()
        nodes[0L] = Node(0L)
        localMap = null
    }

    fun apply(update: PipboyUpdate) {
        when (update) {
            is PipboyUpdate.Data -> update.records.forEach(::apply)
            is PipboyUpdate.LocalMap -> {
                localMap = update.map
                appendLog("Updated Local Map: ${update.map.width}x${update.map.height}")
            }
            is PipboyUpdate.CommandResponse -> appendLog("Command response received: ${update.json.take(240)}")
            is PipboyUpdate.Handshake -> appendLog("Connection handshake received.")
            is PipboyUpdate.Refused -> appendLog("Connection refused by game.")
            is PipboyUpdate.Unknown -> appendLog("Unknown packet type ${update.type} (${update.payload.size} bytes)")
        }
    }

    private fun node(id: Long) = nodes.getOrPut(id) { Node(id) }

    private fun apply(record: PipboyRecord) {
        when (record) {
            is PipboyRecord.Value -> {
                val previous = nodes[record.nodeId]
                val action = if (previous == null) "New" else "Updated"
                val path = pathForNode(record.nodeId) ?: "node${record.nodeId}"
                node(record.nodeId).value = record.value
                appendLog("$action Record(${record.nodeId}): $path => ${valueType(record.value)}( ${valueText(record.value)} )")
            }
            is PipboyRecord.Array -> {
                val action = if (nodes[record.nodeId] == null) "New" else "Updated"
                val path = pathForNode(record.nodeId) ?: "node${record.nodeId}"
                node(record.nodeId).apply { arrayChildren = record.children; value = null }
                appendLog("$action Record(${record.nodeId}): $path => array( ${record.children.size} children )")
            }
            is PipboyRecord.Object -> {
                val n = node(record.nodeId)
                val path = pathForNode(record.nodeId) ?: "node${record.nodeId}"
                record.removed.forEach { id ->
                    val removedPath = pathForNode(id) ?: "node$id"
                    appendLog("Deleted Record($id): $removedPath => removed")
                    n.objectChildren.entries.removeIf { it.value == id }
                }
                record.added.forEach { (key, id) ->
                    val action = if (nodes[id] == null) "New" else "Updated"
                    n.objectChildren[key] = id
                    appendLog("$action Record($id): $path.$key => object child")
                }
                appendLog("Updated Record(${record.nodeId}): $path => object( +${record.added.size}/-${record.removed.size} )")
                n.value = null
            }
        }
    }

    fun snapshotJson(): String {
        val root = JSONObject()
        val nodeArray = JSONArray()
        nodes.values.forEach { n ->
            val o = JSONObject().put("id", n.id)
            when (val v = n.value) {
                null -> Unit
                is PipboyValue.Null -> o.put("kind", "null")
                is PipboyValue.Bool -> o.put("kind", "bool").put("value", v.value)
                is PipboyValue.Int8 -> o.put("kind", "int8").put("value", v.value.toInt())
                is PipboyValue.UInt8 -> o.put("kind", "uint8").put("value", v.value)
                is PipboyValue.Int32 -> o.put("kind", "int32").put("value", v.value)
                is PipboyValue.UInt32 -> o.put("kind", "uint32").put("value", v.value)
                is PipboyValue.Float32 -> o.put("kind", "float32").put("value", v.value.toDouble())
                is PipboyValue.StringValue -> o.put("kind", "string").put("value", v.value)
            }
            val children = JSONObject()
            n.objectChildren.forEach { (k,id) -> children.put(k,id) }
            o.put("objectChildren", children)
            o.put("arrayChildren", JSONArray(n.arrayChildren))
            nodeArray.put(o)
        }
        root.put("nodes", nodeArray)
        localMap?.let { m ->
            root.put("localMap", JSONObject()
                .put("width", m.width).put("height", m.height)
                .put("nwX", m.northWest.first).put("nwY", m.northWest.second)
                .put("neX", m.northEast.first).put("neY", m.northEast.second)
                .put("swX", m.southWest.first).put("swY", m.southWest.second)
                .put("pixels", android.util.Base64.encodeToString(m.pixels, android.util.Base64.NO_WRAP)))
        }
        return root.toString()
    }

    fun restoreSnapshot(json: String): Boolean = runCatching {
        val root = JSONObject(json)
        reset()
        val array = root.getJSONArray("nodes")
        for (i in 0 until array.length()) {
            val o = array.getJSONObject(i)
            val n = node(o.getLong("id"))
            if (o.has("kind")) {
                n.value = when (o.getString("kind")) {
                    "bool" -> PipboyValue.Bool(o.optBoolean("value"))
                    "int8" -> PipboyValue.Int8(o.optInt("value").toByte())
                    "uint8" -> PipboyValue.UInt8(o.optInt("value"))
                    "int32" -> PipboyValue.Int32(o.optInt("value"))
                    "uint32" -> PipboyValue.UInt32(o.optLong("value"))
                    "float32" -> PipboyValue.Float32(o.optDouble("value").toFloat())
                    "string" -> PipboyValue.StringValue(o.optString("value"))
                    else -> PipboyValue.Null
                }
            }
            val children = o.optJSONObject("objectChildren")
            if (children != null) children.keys().forEach { k -> n.objectChildren[k] = children.getLong(k) }
            val ids = o.optJSONArray("arrayChildren")
            if (ids != null) n.arrayChildren = List(ids.length()) { ids.getLong(it) }
        }
        root.optJSONObject("localMap")?.let { m ->
            localMap = PipboyLocalMapUpdate(
                m.getInt("width"), m.getInt("height"),
                m.getDouble("nwX").toFloat() to m.getDouble("nwY").toFloat(),
                m.getDouble("neX").toFloat() to m.getDouble("neY").toFloat(),
                m.getDouble("swX").toFloat() to m.getDouble("swY").toFloat(),
                android.util.Base64.decode(m.optString("pixels"), android.util.Base64.NO_WRAP)
            )
        }
        true
    }.getOrDefault(false)

    fun value(path: String): PipboyValue? = nodeId(path)?.let { nodes[it]?.value }

    fun objectChildren(path: String = ""): Map<String, Long> {
        val id = if (path.isEmpty()) 0L else nodeId(path) ?: return emptyMap()
        return nodes[id]?.objectChildren?.toMap() ?: emptyMap()
    }

    fun objectValue(id: Long, key: String): PipboyValue? =
        nodes[id]?.objectChildren?.get(key)?.let { nodes[it]?.value }

    fun objectNodeId(id: Long, key: String): Long? = nodes[id]?.objectChildren?.get(key)
    fun objectChildrenAtNode(id: Long): Map<String, Long> = nodes[id]?.objectChildren?.toMap() ?: emptyMap()

    fun valueAtNode(id: Long): PipboyValue? = nodes[id]?.value
    fun arrayChildren(id: Long): List<Long> = nodes[id]?.arrayChildren.orEmpty()

    fun firstObjectPath(arrayPath: String, key: String, expected: PipboyValue): String? {
        val arrayId = nodeId(arrayPath) ?: return null
        arrayChildren(arrayId).forEachIndexed { index, childId ->
            val valueId = objectNodeId(childId, key) ?: return@forEachIndexed
            if (valueAtNode(valueId) == expected) return "$arrayPath[$index]"
        }
        return null
    }

    fun flattenedValues(prefix: String = ""): Map<String, PipboyValue> {
        val result = mutableMapOf<String, PipboyValue>()
        fun walk(id: Long, path: String) {
            val node = nodes[id] ?: return
            node.value?.let { if (path.isNotEmpty()) result[path] = it }
            node.objectChildren.forEach { (key, child) -> walk(child, if (path.isEmpty()) key else "$path.$key") }
            node.arrayChildren.forEachIndexed { index, child -> walk(child, "$path[$index]") }
        }
        walk(0L, prefix)
        return result
    }

    fun nodeId(path: String): Long? {
        if (path.isBlank()) return 0L
        var current = 0L
        for (token in path.split(".")) {
            var key = token
            while (key.contains("[")) {
                val open = key.indexOf('[')
                val base = key.substring(0, open)
                if (base.isNotEmpty()) current = nodes[current]?.objectChildren?.get(base) ?: return null
                val close = key.indexOf(']', open)
                if (close < 0) return null
                val index = key.substring(open + 1, close).toIntOrNull() ?: return null
                current = nodes[current]?.arrayChildren?.getOrNull(index) ?: return null
                key = key.substring(close + 1)
            }
            if (key.isNotEmpty()) current = nodes[current]?.objectChildren?.get(key) ?: return null
        }
        return current
    }
}

class PipboyConnection {
    var onState: ((String) -> Unit)? = null
    var onUpdate: ((PipboyUpdate) -> Unit)? = null

    private var socket: Socket? = null
    private var rpcId = 1L
    private var heartbeatJob: Job? = null
    private var reconnectJob: Job? = null
    private var manualDisconnect = false
    private var reconnectAttempt = 0
    @Volatile private var manualHost: String? = null

    suspend fun discoverAndConnect() = withContext(Dispatchers.IO) {
        manualDisconnect = false
        reconnectAttempt = 0
        manualHost = null
        reconnectJob?.cancel()
        discoverOnce()
    }

    suspend fun connect(host: String) = withContext(Dispatchers.IO) {
        manualDisconnect = false
        reconnectAttempt = 0
        manualHost = host
        reconnectJob?.cancel()
        connectOnce(host)
    }

    suspend fun disconnect() = withContext(Dispatchers.IO) {
        manualDisconnect = true
        reconnectJob?.cancel()
        reconnectJob = null
        heartbeatJob?.cancel()
        heartbeatJob = null
        socket?.close()
        socket = null
        onState?.invoke("DISCONNECTED")
    }

    suspend fun sendRPC(type: Int, args: List<Any?>) = withContext(Dispatchers.IO) {
        val json = JSONObject().apply {
            put("id", rpcId++)
            put("type", type)
            put("args", JSONArray(args))
        }.toString().toByteArray()
        runCatching { sendFrame(5, json) }
            .onFailure { handleConnectionFailure("RPC: " + (it.message ?: "send failed")) }
    }

    private suspend fun discoverOnce() {
        if (manualDisconnect) return
        onState?.invoke("DISCOVERING")
        runCatching {
            DatagramSocket().use { udp ->
                udp.broadcast = true
                udp.soTimeout = 5000
                val request = """{"cmd":"autodiscover"}""".toByteArray()
                udp.send(DatagramPacket(request, request.size, InetAddress.getByName("255.255.255.255"), 28000))
                val buffer = ByteArray(8192)
                val packet = DatagramPacket(buffer, buffer.size)
                udp.receive(packet)
                val response = String(packet.data, packet.offset, packet.length, Charsets.UTF_8)
                val json = runCatching { JSONObject(response) }.getOrNull()
                require(json != null) { "Unrecognized autodiscovery response" }
                require(!json.optBoolean("IsBusy", false)) { "Fallout is already connected to another companion" }
                val host = packet.address?.hostAddress
                require(!host.isNullOrBlank()) { "Autodiscovery reply had no source address" }
                connectOnce(host)
            }
        }.onFailure { error ->
            handleConnectionFailure("Discovery: " + (error.message ?: "failed"))
        }
    }

    private suspend fun connectOnce(host: String) {
        if (manualDisconnect) return
        onState?.invoke(if (reconnectAttempt == 0) "CONNECTING" else "RECONNECTING")
        heartbeatJob?.cancel()
        socket?.close()
        val newSocket = Socket()
        socket = newSocket
        try {
            newSocket.connect(java.net.InetSocketAddress(host, 27000), 5000)
            if (manualDisconnect) {
                newSocket.close()
                return
            }
            reconnectAttempt = 0
            onState?.invoke("CONNECTED")
            startHeartbeat()
            receiveLoop(newSocket)
        } catch (error: Exception) {
            handleConnectionFailure("TCP: " + (error.message ?: "connection failed"))
        } finally {
            if (socket === newSocket) {
                runCatching { newSocket.close() }
                socket = null
            }
            heartbeatJob?.cancel()
        }
    }

    private fun startHeartbeat() {
        heartbeatJob?.cancel()
        heartbeatJob = CoroutineScope(Dispatchers.IO).launch {
            while (isActive) {
                delay(20_000)
                runCatching { sendFrame(0, ByteArray(0)) }
                    .onFailure { handleConnectionFailure("Heartbeat: " + (it.message ?: "failed")) }
            }
        }
    }

    private fun sendFrame(type: Int, payload: ByteArray) {
        val out = socket?.getOutputStream() ?: error("Socket unavailable")
        val header = ByteBuffer.allocate(5).order(ByteOrder.LITTLE_ENDIAN)
            .putInt(payload.size).put(type.toByte()).array()
        out.write(header)
        out.write(payload)
        out.flush()
    }

    private fun receiveLoop(s: Socket) {
        val input = s.getInputStream()
        while (!manualDisconnect && !s.isClosed) {
            val header = input.readNBytes(5)
            if (header.size < 5) break
            val h = ByteBuffer.wrap(header).order(ByteOrder.LITTLE_ENDIAN)
            val size = h.int
            val type = h.get().toInt() and 0xFF
            if (size !in 0..(16 * 1024 * 1024)) {
                handleConnectionFailure("Invalid packet size")
                break
            }
            val payload = input.readNBytes(size)
            if (payload.size != size) break
            if (type == 0) {
                runCatching { sendFrame(0, ByteArray(0)) }
                    .onFailure { handleConnectionFailure("Heartbeat response: " + (it.message ?: "failed")) }
            } else {
                PipboyPacketDecoder.decode(type, payload)?.let { update ->
                    if (update is PipboyUpdate.Refused) onState?.invoke("FAILED: GAME REFUSED COMPANION CONNECTION")
                    onUpdate?.invoke(update)
                }
            }
        }
        if (!manualDisconnect) handleConnectionFailure("Connection closed")
    }

    private fun handleConnectionFailure(reason: String) {
        if (manualDisconnect) return
        heartbeatJob?.cancel()
        onState?.invoke("FAILED: $reason")
        scheduleReconnect()
    }

    private fun scheduleReconnect() {
        if (manualDisconnect || reconnectJob?.isActive == true) return
        reconnectAttempt += 1
        val delayMs = minOf(30_000L, 1_000L shl minOf(reconnectAttempt - 1, 5))
        onState?.invoke("RECONNECTING")
        reconnectJob = CoroutineScope(Dispatchers.IO).launch {
            delay(delayMs)
            if (!manualDisconnect) {
                reconnectJob = null
                val host = manualHost
                if (host != null) connectOnce(host) else discoverOnce()
            }
        }
    }
}
