package com.falloutlondon.companion.desktop

import androidx.compose.foundation.Image
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorFilter
import org.jetbrains.skia.Data
import org.jetbrains.skia.Surface
import org.jetbrains.skia.svg.SVGDOM
import androidx.compose.ui.graphics.toComposeImageBitmap
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.delay
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import javax.swing.JFileChooser
import javax.swing.filechooser.FileNameExtensionFilter
import java.util.prefs.Preferences

import kotlinx.coroutines.launch
private val prefs = Preferences.userRoot().node("fallout-london-companion")

private val Phosphor = Color(0xFF00FF44)
private val ScreenBlack = Color(0xFF020A04)

@Composable
fun FalloutLondonApp() {
    val scope = rememberCoroutineScope()
    val connection = remember { PipboyConnection() }
    val db = remember { PipboyDatabase() }
    val inventory = remember { InventoryStore() }
    val medical = remember { MedicalController() }

    var player by remember { mutableStateOf(PlayerState()) }
    var selectedTab by remember { mutableStateOf(MainTab.STAT) }
    var selectedCategory by remember { mutableStateOf(InventoryCategory.WEAPONS) }
    var boot by remember { mutableStateOf("OFF") }
    var connectionState by remember { mutableStateOf("DISCONNECTED") }
    var selectedGame by remember { mutableStateOf(loadSelectedGame()) }
    var demoMode by remember { mutableStateOf(loadDemoMode(selectedGame)) }
    var autoStimpak by remember { mutableStateOf(loadAutoStimpak()) }
    var stimpakThreshold by remember { mutableStateOf(loadAutoStimpakThreshold()) }
    var showingSettings by rememberSaveable { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        if (demoMode) {
            loadCachedDatabase(db, selectedGame)
            player = PlayerState.from(db, player)
            inventory.refresh(db)
        }
        connection.onState = { state ->
            scope.launch {
                connectionState = state
                when {
                    state == "CONNECTED" -> db.logConnectionEvent("New connection established.")
                    state.startsWith("FAILED") -> db.logConnectionEvent("Connection Error: " + state.removePrefix("FAILED: "))
                    state == "DISCONNECTED" -> db.logConnectionEvent("Connection Lost.")
                }
                if (state == "CONNECTED" && !demoMode) {
                    // A new TCP session starts a fresh live database stream.
                    // Drop stale values from the previous session before applying
                    // the first live update.
                    db.reset()
                    player = PlayerState()
                    inventory.refresh(db)
                }
            }
        }
        connection.onUpdate = { update ->
            scope.launch {
                db.apply(update)
                saveCachedDatabase(db, selectedGame)
                player = PlayerState.from(db, player)
                inventory.category = selectedCategory
                inventory.refresh(db)
                medical.consume(player, db, connection)
            }
        }

        delay(450)
        boot = "ATTA-BOY\nPOSITIONING..."
        delay(700)
        boot = "DISPLAY INITIALIZING..."
        delay(650)
        boot = "ATTA-BOY SYSTEM\nINITIALIZING"
        delay(900)
        boot = "SYSTEM CHECK ........ OK\nMEMORY ............. OK\nLINK ............... OK"
        delay(750)
        boot = "SYSTEM READY\n\nWITH THANKS TO TEAM FOLON"
        delay(1400)
        boot = "READY"

        scope.launch {
            runCatching { if (!demoMode) connection.discoverAndConnect() }
                .onFailure { connectionState = "FAILED: " + (it.message ?: "DISCOVERY ERROR") }
        }
    }

    if (boot != "READY") {
        BootScreen(boot)
        return
    }

    Box(
        Modifier.fillMaxSize()
            .background(Color.Black)
            .padding(10.dp)
    ) {
        AttaBoyShell {
            Column(Modifier.fillMaxSize()) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 4.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text((if (selectedGame == "COMMONWEALTH") "COMMONWEALTH" else "FOLON") + " // ATTA-BOY", color = Phosphor, fontFamily = FontFamily.Monospace, fontSize = 11.sp)
                    Spacer(Modifier.weight(1f))
                    Text(if (showingSettings) "MAIN" else "SETTINGS", color = Phosphor, fontFamily = FontFamily.Monospace, fontSize = 8.sp,
                        modifier = Modifier.clickable { showingSettings = !showingSettings }.padding(5.dp))
                }
                ConnectionStatusBanner(connectionState, demoMode)
                CrtFrame {
                    if (showingSettings) {
                        SettingsPanel(
                            demoMode = demoMode, autoStimpak = autoStimpak, threshold = stimpakThreshold, connectionState = connectionState, selectedGame = selectedGame,
                            onSelectedGame = { game ->
                                if (selectedGame != game) {
                                    selectedGame = game; saveSelectedGame(game)
                                    demoMode = loadDemoMode(game)
                                    scope.launch {
                                        connection.disconnect()
                                        db.reset()
                                        player = PlayerState()
                                        if (demoMode) loadCachedDatabase(db, selectedGame)
                                        player = PlayerState.from(db, player)
                                        inventory.refresh(db)
                                        if (!demoMode) runCatching { connection.discoverAndConnect() }
                                    }
                                }
                            },
                            onDemoMode = { enabled ->
                                demoMode = enabled; saveDemoMode(enabled, selectedGame)
                                if (enabled) { scope.launch { connection.disconnect() }; db.reset(); loadCachedDatabase(db, selectedGame); player = PlayerState.from(db, player); inventory.refresh(db) }
                                else scope.launch { runCatching { connection.discoverAndConnect() } }
                            },
                            onAutoStimpak = { enabled -> autoStimpak = enabled; medical.autoStimpakEnabled = enabled; saveAutoStimpak(enabled) },
                            onThreshold = { value -> stimpakThreshold = value; medical.threshold = value; saveAutoStimpakThreshold(value) },
                            onReconnect = { scope.launch { connection.disconnect(); if (!demoMode) runCatching { connection.discoverAndConnect() } } },
                            onClearCache = { clearCachedDatabase(selectedGame); db.reset(); player = PlayerState(); inventory.refresh(db) }
                        )
                    } else when (selectedTab) {
                        MainTab.STAT -> StatusScreen(player, medical, db, connection, scope, autoStimpak, stimpakThreshold,
                            onAutoStimpakChanged = { enabled ->
                                autoStimpak = enabled
                                saveAutoStimpak(enabled)
                            },
                            onThresholdChanged = { value ->
                                stimpakThreshold = value
                                saveAutoStimpakThreshold(value)
                            }
                        )
                        MainTab.INV -> InventoryScreen(
                            store = inventory,
                            category = selectedCategory,
                            onCategory = {
                                selectedCategory = it
                                inventory.category = it
                                inventory.refresh(db)
                            }
                        )
                        MainTab.DATA -> DataScreen(db, connection, scope, demoMode, selectedGame) { enabled ->
                            demoMode = enabled
                            saveDemoMode(enabled, selectedGame)
                            if (enabled) {
                                scope.launch { connection.disconnect() }
                                db.reset()
                                loadCachedDatabase(db, selectedGame)
                                player = PlayerState.from(db, player)
                                inventory.refresh(db)
                            } else {
                                scope.launch { runCatching { connection.discoverAndConnect() } }
                            }
                        }
                        MainTab.MAP -> MapScreen(db, connection, scope, selectedGame)
                        MainTab.RADIO -> RadioPanel(db, connection, scope)
                    }
                }

                Row(
                    Modifier.fillMaxWidth().padding(top = 10.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    MainTab.entries.forEach { tab ->
                        Text(
                            text = tab.label,
                            modifier = Modifier.weight(1f).clickable { showingSettings = false; selectedTab = tab },
                            color = if (selectedTab == tab) Phosphor else Color.Gray,
                            fontFamily = FontFamily.Monospace,
                            fontSize = 12.sp
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun DataSummarySection(db: PipboyDatabase, title: String, path: String) {
    val children = db.objectChildren(path)
    Column(Modifier.fillMaxWidth().padding(vertical = 4.dp).border(1.dp, Phosphor.copy(alpha = .25f)).padding(7.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(title, color = Phosphor, fontFamily = FontFamily.Monospace, fontSize = 11.sp)
            Spacer(Modifier.weight(1f))
            Text(children.size.toString() + " NODES", color = Phosphor.copy(alpha = .6f), fontFamily = FontFamily.Monospace, fontSize = 8.sp)
        }
        if (children.isEmpty()) Text("NO DATA RECEIVED", color = Phosphor.copy(alpha = .5f), fontFamily = FontFamily.Monospace, fontSize = 8.sp)
        else children.keys.sorted().take(6).forEach { Text("• " + it.uppercase(), color = Phosphor.copy(alpha = .8f), fontFamily = FontFamily.Monospace, fontSize = 8.sp) }
    }
}

@Composable
fun QuestPanel(db: PipboyDatabase, connection: PipboyConnection, scope: kotlinx.coroutines.CoroutineScope) {
    val questNode = db.nodeId("quests")
    val questIds = questNode?.let { db.arrayChildren(it) }.orEmpty()
    Column(Modifier.fillMaxWidth().padding(bottom = 8.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("QUESTS", color = Phosphor, fontFamily = FontFamily.Monospace, fontSize = 13.sp)
            Spacer(Modifier.weight(1f))
            Text("${questIds.size} ACTIVE/AVAILABLE", color = Phosphor.copy(alpha = .6f), fontFamily = FontFamily.Monospace, fontSize = 8.sp)
        }
        questIds.forEachIndexed { index, _ ->
            val path = "quests[$index]"
            val name = db.value("$path.text").asString() ?: return@forEachIndexed
            val form = db.value("$path.formid").asUInt() ?: return@forEachIndexed
            val instance = db.value("$path.instance").asUInt() ?: return@forEachIndexed
            val type = db.value("$path.type").asUInt() ?: return@forEachIndexed
            val active = db.value("$path.active").asBool() ?: false
            val enabled = db.value("$path.enabled").asBool() ?: true
            Column(Modifier.fillMaxWidth().padding(vertical = 4.dp).border(1.dp, Phosphor.copy(alpha = if (active) .5f else .2f)).padding(7.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(if (active) "ACTIVE" else "SET", color = Phosphor, fontFamily = FontFamily.Monospace, fontSize = 8.sp,
                        modifier = Modifier.clickable { scope.launch { connection.sendRPC(5, listOf(form, instance, type)) } }.padding(end = 7.dp))
                    Text(name, color = Phosphor, fontFamily = FontFamily.Monospace, fontSize = 11.sp)
                    Spacer(Modifier.weight(1f))
                    if (!enabled) Text("DISABLED", color = Phosphor.copy(alpha = .5f), fontFamily = FontFamily.Monospace, fontSize = 7.sp)
                }
                val objNode = db.nodeId("$path.objectives")
                val objIds = objNode?.let { db.arrayChildren(it) }.orEmpty()
                objIds.forEachIndexed { oi, _ ->
                    val op = "$path.objectives[$oi]"
                    val text = db.value("$op.text").asString() ?: return@forEachIndexed
                    val done = db.value("$op.completed").asBool() ?: false
                    val failed = db.value("$op.failed").asBool() ?: false
                    Text((if (done) "✓ " else if (failed) "✗ " else "· ") + text, color = Phosphor.copy(alpha = if (done) .5f else .82f), fontFamily = FontFamily.Monospace, fontSize = 8.sp)
                }
            }
        }
    }
}

private fun PipboyValue?.asDouble(): Double? = when (this) {
    is PipboyValue.Float32 -> value.toDouble()
    is PipboyValue.Int32 -> value.toDouble()
    is PipboyValue.UInt32 -> value.toDouble()
    is PipboyValue.UInt8 -> value.toDouble()
    is PipboyValue.Int8 -> value.toDouble()
    else -> null
}

private fun PipboyValue?.asString() = (this as? PipboyValue.StringValue)?.value
private fun PipboyValue?.asBool() = (this as? PipboyValue.Bool)?.value
private fun PipboyValue?.asUInt(): Long? = when (this) {
    is PipboyValue.UInt32 -> value
    is PipboyValue.Int32 -> value.toLong().takeIf { it >= 0 }
    is PipboyValue.UInt8 -> value.toLong()
    is PipboyValue.Int8 -> value.toLong().takeIf { it >= 0 }
    else -> null
}

private fun PipboyValue?.asNumberText(): String = when (this) {
    is PipboyValue.Float32 -> format2(value)
    is PipboyValue.Int32 -> value.toString()
    is PipboyValue.UInt32 -> value.toString()
    else -> "--"
}

private fun format0(value: Double) = String.format("%.0f", value)
private fun format1(value: Double) = String.format("%.1f", value)
private fun format2(value: Float) = String.format("%.2f", value)


private fun loadSelectedGame(): String = prefs.get("selectedGame", "LONDON")
private fun saveSelectedGame(value: String) { prefs.put("selectedGame", value) }
private fun loadDemoMode(game: String)=prefs.getBoolean("demoMode_$game",false)
private fun saveDemoMode(v:Boolean, game: String){prefs.putBoolean("demoMode_$game",v)}
private fun loadAutoStimpak()=prefs.getBoolean("autoStimpak",true)
private fun saveAutoStimpak(v:Boolean){prefs.putBoolean("autoStimpak",v)}
private fun loadAutoStimpakThreshold()=prefs.getDouble("autoStimpakThreshold",0.35)
private fun saveAutoStimpakThreshold(v:Double){prefs.putDouble("autoStimpakThreshold",v)}
private fun saveCachedDatabase(db:PipboyDatabase, game: String){prefs.put("cache_$game",db.snapshotJson())}
private fun loadCachedDatabase(db:PipboyDatabase, game: String){prefs.get("cache_$game",null)?.let{db.restoreSnapshot(it)}}
private fun clearCachedDatabase(game: String){prefs.remove("cache_$game")}
