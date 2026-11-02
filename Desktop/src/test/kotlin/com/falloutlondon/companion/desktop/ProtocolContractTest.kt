package com.falloutlondon.companion.desktop

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ProtocolContractTest {
    @Test fun decodesLittleEndianBooleanRecord() {
        val payload = byteArrayOf(0) + u32(0x12345678L) + byteArrayOf(1)
        assertEquals(PipboyUpdate.Data(listOf(PipboyRecord.Value(0x12345678L, PipboyValue.Bool(true)))), PipboyPacketDecoder.decode(3, payload))
    }
    @Test fun decodesCommandResponseAsUtf8() {
        assertEquals(PipboyUpdate.CommandResponse("""{"ok":true}"""), PipboyPacketDecoder.decode(6, """{"ok":true}""".toByteArray()))
    }
    @Test fun preservesUnknownMessageTypes() {
        val payload = byteArrayOf(4, 5, 6)
        val decoded = PipboyPacketDecoder.decode(99, payload)
        assertTrue(decoded is PipboyUpdate.Unknown)
        assertEquals(99, (decoded as PipboyUpdate.Unknown).type)
        assertTrue(payload.contentEquals(decoded.payload))
    }
    @Test fun rejectsTruncatedLocalMapHeader() {
        assertTrue(PipboyPacketDecoder.decode(4, byteArrayOf(1, 2, 3)) is PipboyUpdate.Unknown)
    }
    @Test fun rejectsTruncatedDataUpdateWithoutApplyingPrefix() {
        val validPrefix = byteArrayOf(0) + u32(7L) + byteArrayOf(1)
        val malformed = validPrefix + byteArrayOf(3, 1)
        val decoded = PipboyPacketDecoder.decode(3, malformed)
        assertTrue(decoded is PipboyUpdate.Unknown)
    }
    @Test fun preservesUndocumentedTypeNineAsUnknown() {
        val decoded = PipboyPacketDecoder.decode(3, byteArrayOf(9) + u32(7L))
        assertTrue(decoded is PipboyUpdate.Unknown)
    }
    @Test fun rejectsLocalMapWithMismatchedPixelCount() {
        val header = u32(1L) + u32(1L) + ByteArray(24)
        val decoded = PipboyPacketDecoder.decode(4, header)
        assertTrue(decoded is PipboyUpdate.Unknown)
    }
    @Test fun appliesIncrementalObjectGraphUpdatesToPaths() {
        val database = PipboyDatabase()
        database.apply(PipboyUpdate.Data(listOf(
            PipboyRecord.Object(0L, listOf("playerinfo" to 10L), emptyList()),
            PipboyRecord.Object(10L, listOf("currhp" to 11L), emptyList()),
            PipboyRecord.Value(11L, PipboyValue.Float32(87.5f))
        )))
        assertEquals(PipboyValue.Float32(87.5f), database.value("playerinfo.currhp"))
    }
    @Test fun decodesHandshakeAndBusyMessages() {
        assertEquals(PipboyUpdate.Handshake("""{"lang":"en","version":"1.11.0"}"""),
            PipboyPacketDecoder.decode(1, """{"lang":"en","version":"1.11.0"}""".toByteArray()))
        assertEquals(PipboyUpdate.Refused, PipboyPacketDecoder.decode(2, ByteArray(0)))
    }

    @Test fun decodesValidLocalMap() {
        val payload = u32(2L) + u32(2L) + ByteArray(24) + byteArrayOf(1, 2, 3, 4)
        val decoded = PipboyPacketDecoder.decode(4, payload)
        assertTrue(decoded is PipboyUpdate.LocalMap)
        val map = (decoded as PipboyUpdate.LocalMap).map
        assertEquals(2, map.width)
        assertEquals(2, map.height)
        assertTrue(byteArrayOf(1, 2, 3, 4).contentEquals(map.pixels))
    }

    @Test fun rejectsLocalMapWithZeroDimension() {
        assertTrue(PipboyPacketDecoder.decode(4, u32(0L) + u32(5L) + ByteArray(24)) is PipboyUpdate.Unknown)
    }

    @Test fun rejectsUnterminatedString() {
        val payload = byteArrayOf(6) + u32(1L) + "abc".toByteArray()
        assertTrue(PipboyPacketDecoder.decode(3, payload) is PipboyUpdate.Unknown)
    }

    @Test fun decodesObjectDeltaAdditionsAndRemovals() {
        val payload = byteArrayOf(8) + u32(0L) + u16(2) +
            u32(10L) + "playerinfo".toByteArray() + byteArrayOf(0) +
            u32(11L) + "stats".toByteArray() + byteArrayOf(0) +
            u16(1) + u32(99L)
        val decoded = PipboyPacketDecoder.decode(3, payload)
        assertEquals(
            PipboyUpdate.Data(listOf(PipboyRecord.Object(0L, listOf("playerinfo" to 10L, "stats" to 11L), listOf(99L)))),
            decoded
        )
    }

    @Test fun objectRemovalDropsKeyFromGraph() {
        val database = PipboyDatabase()
        database.apply(PipboyUpdate.Data(listOf(
            PipboyRecord.Object(0L, listOf("playerinfo" to 10L), emptyList()),
            PipboyRecord.Object(10L, listOf("currhp" to 11L), emptyList()),
            PipboyRecord.Value(11L, PipboyValue.Float32(87.5f))
        )))
        database.apply(PipboyUpdate.Data(listOf(PipboyRecord.Object(10L, emptyList(), listOf(11L)))))
        assertEquals(null, database.value("playerinfo.currhp"))
    }

    @Test fun childMayBeReferencedBeforeItsValueArrives() {
        val database = PipboyDatabase()
        database.apply(PipboyUpdate.Data(listOf(PipboyRecord.Object(0L, listOf("x" to 5L), emptyList()))))
        assertEquals(null, database.value("x"))
        database.apply(PipboyUpdate.Data(listOf(PipboyRecord.Value(5L, PipboyValue.UInt32(3L)))))
        assertEquals(PipboyValue.UInt32(3L), database.value("x"))
    }

    @Test fun diagnosticExportIncludesWorldSourceAndCurrentTreeValues() {
        val database = PipboyDatabase()
        database.apply(PipboyUpdate.Data(listOf(
            PipboyRecord.Object(0L, listOf("playerinfo" to 10L), emptyList()),
            PipboyRecord.Object(10L, listOf("currhp" to 11L), emptyList()),
            PipboyRecord.Value(11L, PipboyValue.Float32(87.5f))
        )))
        val export = database.exportText("COMMONWEALTH", "LIVE SESSION")
        assertTrue(export.contains("Game world: COMMONWEALTH"))
        assertTrue(export.contains("Data source: LIVE SESSION"))
        assertTrue(export.contains("playerinfo.currhp = 87.5"))
        assertTrue(export.contains("Decoded value paths: 1"))
    }
    private fun u16(value: Int) = byteArrayOf(value.toByte(), (value shr 8).toByte())
    private fun u32(value: Long) = byteArrayOf(value.toByte(), (value shr 8).toByte(), (value shr 16).toByte(), (value shr 24).toByte())
}
