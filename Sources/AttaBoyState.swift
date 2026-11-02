import Foundation
import SwiftUI
import AudioToolbox

struct LiveGameItem: Identifiable {
    let id: String
    let name: String
    let category: ItemCategory
    let count: Int
    let weight: Double
    let value: Int
    let handleID: UInt32?
    let formID: UInt32?
    let stackIDs: [UInt32]
    let favoriteSlot: Int?
    let equipped: Bool
    let legendary: Bool
    let damage: Double?
    let armor: Double?
    let radiationResistance: Double?
    let energyResistance: Double?
    let detail: String?
    var isFavorited: Bool { favoriteSlot != nil }
}

struct LiveQuestObjective: Identifiable {
    let id: String
    let text: String
    let completed: Bool
    let failed: Bool
    let active: Bool
}

struct LiveGameQuest: Identifiable {
    let id: String
    let title: String
    let detail: String
    let enabled: Bool
    let active: Bool
    let formID: UInt32?
    let instance: UInt32?
    let type: UInt32?
    let objectives: [LiveQuestObjective]
}

struct LiveRadioStation: Identifiable {
    let id: UInt32
    let name: String
    let frequency: String
    let active: Bool
    let inRange: Bool
}

struct LiveMapLocation: Identifiable {
    let id: UInt32
    let name: String
    let x: Double
    let y: Double
    let discovered: Bool
    let visible: Bool
    let cleared: Bool
    let markerType: Int
}

struct LivePerk: Identifiable {
    let id: Int
    let name: String
    let rank: Int
    let maxRank: Int
    let nextRankDescription: String
}

struct LiveDatabaseEntry: Identifiable {
    let path: String
    let value: String
    var id: String { path }
}

enum GameWorld: String, CaseIterable, Identifiable {
    case london = "FALLOUT_LONDON"
    case commonwealth = "COMMONWEALTH"
    var id: String { rawValue }
    var title: String { self == .london ? "FALLOUT: LONDON" : "FALLOUT 4 // COMMONWEALTH" }
    var mapTitle: String { self == .london ? "LONDON MAP" : "COMMONWEALTH MAP" }
}

@MainActor
final class AttaBoyState: ObservableObject {
    @Published private(set) var gameWorld: GameWorld = GameWorld(rawValue: UserDefaults.standard.string(forKey: "gameWorld") ?? "") ?? .london
    @Published private(set) var demoModeEnabled = UserDefaults.standard.object(forKey: "demoMode_FALLOUT_LONDON") as? Bool ?? true
    @Published var selectedTab: AppTab = .status
    @Published var selectedDistrictID = District.all[0].id
    @Published var selectedCategory: ItemCategory = .all
    @Published var selectedStationID = RadioStation.all[0].id
    @Published var isRadioPlaying = false

    @Published var health = 82
    @Published var maxHealth = 100
    @Published var actionPoints = 76
    @Published var maxActionPoints = 100
    @Published var radiation = 0
    @Published var caps = 0
    @Published var level = 1
    @Published var perkPoints = 0
    @Published var xpProgress = 0.0
    @Published var carriedWeight = 34.5
    @Published var maxWeight = 180.0
    @Published var specialValues = SpecialStat.all.map(\.value)
    @Published var limbConditions: [String: Int] = [:]
    @Published var activeEffects: [String] = []

    @Published var connectionState: ConnectionState = .disconnected
    @Published var connectionHost = ""
    @Published var serverVersion = ""
    @Published var serverLanguage = ""
    @Published var lastActionStatus: String?
    @Published var autoStimpakEnabled = UserDefaults.standard.object(forKey: "autoStimpakEnabled") as? Bool ?? false
    @Published var autoStimpakThreshold = UserDefaults.standard.object(forKey: "autoStimpakThreshold") as? Double ?? 0.35
    @Published var liveInventory: [LiveGameItem] = []
    @Published var liveQuests: [LiveGameQuest] = []
    @Published var liveRadioStations: [LiveRadioStation] = []
    @Published var liveMapLocations: [LiveMapLocation] = []
    @Published var livePerks: [LivePerk] = []
    @Published var databaseEntries: [LiveDatabaseEntry] = []
    @Published var localMap: PipboyLocalMapUpdate?
    @Published var playerPosition: (x: Double, y: Double, rotation: Double)?
    @Published private(set) var isLiveData = false

    private let connectionService = ConnectionService()
    private let database = PipboyDatabase()
    private var lastMedicalUse = Date.distantPast
    private let medicalCooldown: TimeInterval = 2.0

    @Published private(set) var completedQuestIDs: Set<String> {
        didSet { UserDefaults.standard.set(Array(completedQuestIDs), forKey: "completedQuestIDs") }
    }
    @Published private(set) var equippedItemIDs: Set<String> {
        didSet { UserDefaults.standard.set(Array(equippedItemIDs), forKey: "equippedItemIDs") }
    }

    init() {
        completedQuestIDs = Set(UserDefaults.standard.stringArray(forKey: "completedQuestIDs") ?? [])
        equippedItemIDs = Set(UserDefaults.standard.stringArray(forKey: "equippedItemIDs") ?? ["service-rifle", "leather-coat"])

        connectionService.onStateChange = { [weak self] newState in
            Task { @MainActor in
                guard let self else { return }
                self.connectionState = newState
                if newState != .connected { self.isLiveData = false }
                if newState == .connected {
                    self.database.reset()
                    self.isLiveData = false
                    self.liveInventory = []
                    self.liveQuests = []
                    self.liveRadioStations = []
                    self.liveMapLocations = []
                    self.livePerks = []
                    self.databaseEntries = []
                    self.localMap = nil
                    self.playerPosition = nil
                    self.serverVersion = ""
                    self.serverLanguage = ""
                    self.lastActionStatus = nil
                }
            }
        }
        connectionService.onUpdate = { [weak self] update in
            Task { @MainActor in self?.apply(update) }
        }
    }

    var selectedDistrict: District {
        District.all.first(where: { $0.id == selectedDistrictID }) ?? District.all[0]
    }
    var selectedStation: RadioStation {
        RadioStation.all.first(where: { $0.id == selectedStationID }) ?? RadioStation.all[0]
    }
    var completedQuestCount: Int { completedQuestIDs.count }
    var hasPlayerPosition: Bool {
        if case .some = playerPosition { return true }
        return false
    }

    var connectionLabel: String {
        switch connectionState {
        case .disconnected: "NOT CONNECTED"
        case .discovering: "SEARCHING FOR GAME"
        case .connecting: "CONNECTING"
        case .connected:
            if !serverVersion.isEmpty { "CONNECTED · FALLOUT \(serverVersion)" }
            else { isLiveData ? "CONNECTED · LIVE DATA" : "CONNECTED · WAITING FOR DATA" }
        case .reconnecting: "RECONNECTING"
        case .failed(let reason): "CONNECTION ERROR · \(reason.uppercased())"
        }
    }

    func selectGameWorld(_ world: GameWorld) {
        guard gameWorld != world else { return }
        gameWorld = world
        UserDefaults.standard.set(world.rawValue, forKey: "gameWorld")
        demoModeEnabled = UserDefaults.standard.object(forKey: "demoMode_\(world.rawValue)") as? Bool ?? true
        connectionService.disconnect()
        connectionState = .disconnected
        isLiveData = false
        database.reset()
        liveInventory = []
        liveQuests = []
        liveRadioStations = []
        liveMapLocations = []
        livePerks = []
        databaseEntries = []
        localMap = nil
        playerPosition = nil
        lastActionStatus = "GAME PROFILE CHANGED · RECONNECT TO THE SELECTED GAME"
    }

    func setDemoModeEnabled(_ enabled: Bool) {
        demoModeEnabled = enabled
        UserDefaults.standard.set(enabled, forKey: "demoMode_\(gameWorld.rawValue)")
        if enabled {
            disconnectGame()
            lastActionStatus = "DEMO MODE ENABLED · LIVE GAME ACTIONS DISABLED"
        } else {
            lastActionStatus = "DEMO MODE DISABLED · CONNECT TO THE SELECTED GAME"
        }
    }

    func discoverGame() {
        guard !demoModeEnabled else {
            lastActionStatus = "DISABLE DEMO MODE BEFORE CONNECTING"
            return
        }
        connectionService.disconnect()
        connectionService.discoverAndConnect()
    }

    func connectToGame(host: String) {
        let trimmed = host.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        connectionHost = trimmed
        connectionService.connect(host: trimmed)
    }

    func disconnectGame() {
        connectionService.disconnect()
        connectionState = .disconnected
        isLiveData = false
    }

    func selectDistrict(_ district: District) {
        selectedDistrictID = district.id
        click()
    }
    func selectStation(_ station: RadioStation) {
        selectedStationID = station.id
        isRadioPlaying = false
        click()
    }
    func toggleQuest(_ quest: Quest) {
        if completedQuestIDs.contains(quest.id) { completedQuestIDs.remove(quest.id) }
        else { completedQuestIDs.insert(quest.id) }
        click()
    }
    func toggleEquipment(_ item: InventoryItem) {
        if equippedItemIDs.contains(item.id) { equippedItemIDs.remove(item.id) }
        else { equippedItemIDs.insert(item.id) }
        click()
    }
    func toggleRadio() {
        isRadioPlaying.toggle()
        click()
    }
    func toggleLiveRadio(_ station: LiveRadioStation) {
        guard requireLiveConnection("RADIO") else { return }
        connectionService.sendRPC(type: 12, args: [Int(station.id)])
        lastActionStatus = "RADIO REQUEST SENT"
        click()
    }
    func toggleLiveQuest(_ quest: LiveGameQuest) {
        guard requireLiveConnection("QUEST ACTION") else { return }
        guard let formID = quest.formID, let instance = quest.instance, let type = quest.type else {
            lastActionStatus = "QUEST ACTION UNAVAILABLE · MISSING GAME IDS"
            return
        }
        connectionService.sendRPC(type: 5, args: [formID, instance, type])
        lastActionStatus = "QUEST MARKER REQUEST SENT"
        click()
    }
    func requestLocalMapSnapshot() {
        guard requireLiveConnection("LOCAL MAP REQUEST") else { return }
        connectionService.sendRPC(type: 13, args: [])
        lastActionStatus = "LOCAL MAP REQUEST SENT"
        click()
    }
    func setCustomMapMarker(x: Double, y: Double) {
        guard requireLiveConnection("MAP MARKER") else { return }
        connectionService.sendRPC(type: 6, args: [x, y, true])
        lastActionStatus = "MAP MARKER REQUEST SENT"
        click()
    }
    func fastTravel(to location: LiveMapLocation) {
        guard requireLiveConnection("FAST TRAVEL") else { return }
        connectionService.sendRPC(type: 9, args: [Int(location.id)])
        lastActionStatus = "FAST TRAVEL REQUEST SENT · WAITING FOR GAME RESPONSE"
        click()
    }
    func clearCustomMapMarker() {
        guard requireLiveConnection("CLEAR MAP MARKER") else { return }
        connectionService.sendRPC(type: 7, args: [])
        lastActionStatus = "MAP MARKER CLEAR REQUEST SENT"
        click()
    }
    func useItem(_ item: LiveGameItem) {
        guard requireLiveConnection("USE ITEM") else { return }
        guard let handle = item.handleID,
              let stack = item.stackIDs.first,
              let version = uint32(database.value(at: "inventory.version")) else {
            lastActionStatus = "USE ITEM UNAVAILABLE · GAME IDS NOT PRESENT"
            return
        }
        connectionService.sendRPC(type: 0, args: [handle, stack, version])
        lastActionStatus = "USE ITEM REQUEST SENT"
        click()
    }
    func dropItem(_ item: LiveGameItem, count: Int = 1) {
        guard requireLiveConnection("DROP ITEM") else { return }
        guard let handle = item.handleID,
              !item.stackIDs.isEmpty,
              let version = uint32(database.value(at: "inventory.version")) else {
            lastActionStatus = "DROP UNAVAILABLE · GAME IDS NOT PRESENT"
            return
        }
        connectionService.sendRPC(type: 1, args: [handle, min(max(1, count), item.count), version, item.stackIDs])
        lastActionStatus = "DROP REQUEST SENT"
        click()
    }
    func favoriteItem(_ item: LiveGameItem, slot: Int) {
        guard requireLiveConnection("FAVORITE ITEM") else { return }
        guard (0...11).contains(slot),
              let handle = item.handleID,
              !item.stackIDs.isEmpty,
              let version = uint32(database.value(at: "inventory.version")) else {
            lastActionStatus = "FAVORITE UNAVAILABLE · GAME IDS NOT PRESENT"
            return
        }
        connectionService.sendRPC(type: 2, args: [handle, item.stackIDs, slot, version])
        lastActionStatus = "FAVORITE REQUEST SENT"
        click()
    }

    func setAutoStimpakEnabled(_ enabled: Bool) {
        autoStimpakEnabled = enabled
        UserDefaults.standard.set(enabled, forKey: "autoStimpakEnabled")
    }
    func setAutoStimpakThreshold(_ value: Double) {
        autoStimpakThreshold = min(max(value, 0.10), 0.90)
        UserDefaults.standard.set(autoStimpakThreshold, forKey: "autoStimpakThreshold")
    }
    func useStimpak() {
        useMedicalItem(objectIDPath: "inventory.stimpakobjectid", validPath: "inventory.stimpakobjectidisvalid", bypassCooldown: true)
    }
    func useRadAway() {
        useMedicalItem(objectIDPath: "inventory.radawayobjectid", validPath: "inventory.radawayobjectidisvalid", bypassCooldown: true)
    }

    private func requireLiveConnection(_ action: String) -> Bool {
        guard case .connected = connectionState, isLiveData else {
            lastActionStatus = "\(action) REQUIRES LIVE GAME DATA"
            return false
        }
        return true
    }

    private func useMedicalItem(objectIDPath: String, validPath: String, bypassCooldown: Bool = false) {
        guard requireLiveConnection("MEDICAL ACTION") else { return }
        guard bypassCooldown || Date().timeIntervalSince(lastMedicalUse) >= medicalCooldown else { return }
        guard bool(validPath) == true,
              let objectID = uint32(database.value(at: objectIDPath)),
              let handleID = uint32(database.objectValue(atNode: objectID, key: "handleid")),
              let stackNodeID = database.objectNodeID(atNode: objectID, key: "stackid"),
              let stackChild = database.arrayChildren(at: stackNodeID)?.first,
              let stackID = uint32(database.value(atNode: stackChild)),
              let version = uint32(database.value(at: "inventory.version")) else {
            lastActionStatus = "ITEM UNAVAILABLE · GAME DID NOT PROVIDE REQUIRED IDS"
            return
        }
        connectionService.sendRPC(type: 0, args: [handleID, stackID, version])
        lastMedicalUse = Date()
        lastActionStatus = "MEDICAL ITEM REQUEST SENT"
        click()
    }

    func click() { AudioServicesPlaySystemSound(1104) }

    private func apply(_ update: PipboyUpdate) {
        switch update {
        case .connectionAccepted(let handshake):
            serverVersion = handshake.version ?? ""
            serverLanguage = handshake.language ?? ""
            lastActionStatus = "GAME HANDSHAKE RECEIVED"
            return
        case .connectionRefused:
            connectionState = .failed("GAME REFUSED COMPANION CONNECTION")
            return
        case .commandResponse(let response):
            lastActionStatus = commandResponseMessage(response.json)
            return
        default:
            break
        }

        database.apply(update)
        switch update {
        case .data(let data):
            if !data.records.isEmpty { refreshLiveData() }
        case .localMap(let map):
            localMap = map
        default:
            break
        }
    }

    private func refreshLiveData() {
        health = integer("playerinfo.currhp", fallback: health)
        maxHealth = integer("playerinfo.maxhp", fallback: maxHealth)
        actionPoints = integer("playerinfo.currap", fallback: actionPoints)
        maxActionPoints = integer("playerinfo.maxap", fallback: maxActionPoints)
        radiation = integer("status.rads", fallback: radiation)
        caps = integer("playerinfo.caps", fallback: caps)
        level = integer("playerinfo.xplevel", fallback: level)
        perkPoints = integer("playerinfo.perkpoints", fallback: perkPoints)
        xpProgress = number("playerinfo.xpprogresspct") ?? xpProgress
        carriedWeight = number("playerinfo.currweight") ?? carriedWeight
        maxWeight = number("playerinfo.maxweight") ?? maxWeight
        specialValues = (0..<7).map { index in
            integer("special[\(index)].value", fallback: specialValues.indices.contains(index) ? specialValues[index] : 5)
        }
        let limbValues = [
            "HEAD": integer("stats.headcondition", fallback: -1),
            "TORSO": integer("stats.torsocondition", fallback: -1),
            "LEFT ARM": integer("stats.larmcondition", fallback: -1),
            "RIGHT ARM": integer("stats.rarmcondition", fallback: -1),
            "LEFT LEG": integer("stats.llegcondition", fallback: -1),
            "RIGHT LEG": integer("stats.rlegcondition", fallback: -1)
        ]
        limbConditions = Dictionary(uniqueKeysWithValues: limbValues.filter { $0.value >= 0 })
        activeEffects = parseActiveEffects()
        playerPosition = {
            guard let x = number("map.world.player.x"), let y = number("map.world.player.y") else { return nil }
            return (x, y, number("map.world.player.rotation") ?? 0)
        }()
        liveInventory = parseInventory()
        liveQuests = parseQuests()
        liveRadioStations = parseRadioStations()
        liveMapLocations = parseMapLocations()
        livePerks = parsePerks()
        databaseEntries = database.flattenedValues()
            .map { LiveDatabaseEntry(path: $0.key, value: describe($0.value)) }
            .sorted { $0.path.localizedStandardCompare($1.path) == .orderedAscending }
        isLiveData = true
        if autoStimpakEnabled, maxHealth > 0, health > 0,
           Double(health) / Double(maxHealth) <= autoStimpakThreshold {
            useMedicalItem(objectIDPath: "inventory.stimpakobjectid", validPath: "inventory.stimpakobjectidisvalid")
        }
    }

    private func parseInventory() -> [LiveGameItem] {
        guard let root = database.nodeID(at: "inventory") else { return [] }
        var result: [LiveGameItem] = []
        walkInventory(nodeID: root, path: "inventory", inherited: nil, depth: 0, into: &result)
        var unique: [String: LiveGameItem] = [:]
        for item in result { unique[item.id] = item }
        return unique.values.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    private func walkInventory(nodeID: UInt32, path: String, inherited: ItemCategory?, depth: Int, into result: inout [LiveGameItem]) {
        guard depth < 8 else { return }
        if let item = makeInventoryItem(path: path, nodeID: nodeID, inherited: inherited) {
            result.append(item)
            return
        }
        for (key, childID) in database.objectChildren(atNode: nodeID) {
            walkInventory(nodeID: childID, path: "\(path).\(key)", inherited: categoryFor(key) ?? inherited, depth: depth + 1, into: &result)
        }
        for (index, childID) in (database.arrayChildren(at: nodeID) ?? []).enumerated() {
            walkInventory(nodeID: childID, path: "\(path)[\(index)]", inherited: inherited, depth: depth + 1, into: &result)
        }
    }

    private func makeInventoryItem(path: String, nodeID: UInt32, inherited: ItemCategory?) -> LiveGameItem? {
        guard let name = string("\(path).text") ?? string("\(path).name"), !name.isEmpty else { return nil }
        let filter = number("\(path).filterflag")
        let category = inherited ?? categoryFromFilterFlag(filter) ?? {
            if database.nodeID(at: "\(path).paperdollsection") != nil { return .apparel }
            if database.nodeID(at: "\(path).currenthpgain") != nil { return .aid }
            if database.nodeID(at: "\(path).damagerating") != nil || database.nodeID(at: "\(path).damage") != nil { return .weapons }
            return .misc
        }()
        let handle = uint32(database.value(at: "\(path).handleid")) ?? uint32(database.value(at: "\(path).handleID"))
        let form = uint32(database.value(at: "\(path).formid")) ?? uint32(database.value(at: "\(path).formID"))
        let count = max(1, integer("\(path).count", fallback: integer("\(path).quantity", fallback: 1)))
        let favoriteRaw = integer("\(path).favorite", fallback: -1)
        let favorite = (0...11).contains(favoriteRaw) ? favoriteRaw : nil
        let equipped = (number("\(path).equipstate") ?? number("\(path).equipped") ?? 0) != 0
        let stackNode = database.nodeID(at: "\(path).stackid")
        let stacks = (stackNode.flatMap { database.arrayChildren(at: $0) } ?? []).compactMap { uint32(database.value(atNode: $0)) }
        let id = "\(handle ?? form ?? nodeID)-\(category.rawValue)"
        return LiveGameItem(
            id: id, name: name, category: category, count: count,
            weight: number("\(path).weight") ?? 0,
            value: integer("\(path).value", fallback: 0),
            handleID: handle, formID: form, stackIDs: stacks,
            favoriteSlot: favorite, equipped: equipped,
            legendary: (number("\(path).islegendary") ?? 0) != 0,
            damage: number("\(path).damagerating") ?? number("\(path).damage"),
            armor: number("\(path).armorrating"),
            radiationResistance: number("\(path).radiationresistance"),
            energyResistance: number("\(path).energyresistance"),
            detail: string("\(path).description")
        )
    }

    private func categoryFor(_ key: String) -> ItemCategory? {
        switch key.lowercased() {
        case "weapons", "weapon": .weapons
        case "apparel", "armor", "armour": .apparel
        case "aid", "medical": .aid
        case "junk": .junk
        case "ammo", "ammunition": .ammo
        case "mods", "mod": .mods
        case "misc", "miscellaneous": .misc
        default: nil
        }
    }

    private func categoryFromFilterFlag(_ value: Double?) -> ItemCategory? {
        guard let value else { return nil }
        switch Int(value) {
        case 2: return .weapons
        case 4: return .apparel
        case 8: return .aid
        case 512, 1024: return .junk
        case 4096: return .ammo
        case 640: return .misc
        default: return nil
        }
    }

    private func parseQuests() -> [LiveGameQuest] {
        guard let root = database.nodeID(at: "quests") else { return [] }
        let objectNodes = database.objectChildren(atNode: root)
        let entries: [(String, String)] = objectNodes.isEmpty
            ? (database.arrayChildren(at: root) ?? []).enumerated().map { (String($0.offset), "quests[\($0.offset)]") }
            : objectNodes.keys.sorted().map { ($0, "quests.\($0)") }
        return entries.compactMap { key, path in
            let title = string("\(path).text") ?? string("\(path).name") ?? key
            let enabled = bool("\(path).enabled") ?? false
            let active = bool("\(path).active") ?? false
            let objectives = parseObjectives(path: "\(path).objectives")
            return LiveGameQuest(
                id: key, title: title,
                detail: string("\(path).desc") ?? "",
                enabled: enabled, active: active,
                formID: uint32(database.value(at: "\(path).formid")),
                instance: uint32(database.value(at: "\(path).instance")),
                type: uint32(database.value(at: "\(path).type")),
                objectives: objectives
            )
        }.filter { $0.enabled }
    }

    private func parseObjectives(path: String) -> [LiveQuestObjective] {
        guard let root = database.nodeID(at: path) else { return [] }
        let objects = database.objectChildren(atNode: root)
        let entries: [(String, String)] = objects.isEmpty
            ? (database.arrayChildren(at: root) ?? []).enumerated().map { (String($0.offset), "\(path)[\($0.offset)]") }
            : objects.keys.sorted().map { ($0, "\(path).\($0)") }
        return entries.map { key, itemPath in
            return LiveQuestObjective(
                id: key,
                text: string("\(itemPath).text") ?? key,
                completed: bool("\(itemPath).completed") ?? false,
                failed: bool("\(itemPath).failed") ?? false,
                active: bool("\(itemPath).active") ?? false
            )
        }
    }

    private func parseActiveEffects() -> [String] {
        guard let sourcesRoot = database.nodeID(at: "stats.activeeffects") else { return [] }
        let sources = database.arrayChildren(at: sourcesRoot) ?? []
        var effects: [String] = []
        for (sourceIndex, _) in sources.enumerated() {
            let effectsPath = "stats.activeeffects[\(sourceIndex)].effects"
            guard let effectsRoot = database.nodeID(at: effectsPath) else { continue }
            for (effectIndex, _) in (database.arrayChildren(at: effectsRoot) ?? []).enumerated() {
                let path = "\(effectsPath)[\(effectIndex)]"
                guard bool("\(path).isactive") ?? true else { continue }
                let name = string("\(path).name") ?? "UNKNOWN EFFECT"
                let value = number("\(path).value")
                let percent = bool("\(path).showaspercent") ?? false
                if let value, value != 0 {
                    let suffix = percent ? "%" : ""
                    effects.append("\(name) \(value > 0 ? "+" : "")\(String(format: "%.2f", value))\(suffix)")
                } else {
                    effects.append(name)
                }
            }
        }
        return effects
    }

    private func parseRadioStations() -> [LiveRadioStation] {
        guard let root = database.nodeID(at: "radio") else { return [] }
        let children = database.arrayChildren(at: root) ?? []
        return children.enumerated().map { index, nodeID in
            let path = "radio[\(index)]"
            return LiveRadioStation(
                id: nodeID,
                name: string("\(path).text") ?? "STATION \(index + 1)",
                frequency: string("\(path).frequency") ?? number("\(path).frequency").map { String(format: "%.1f", $0) } ?? "—",
                active: bool("\(path).active") ?? false,
                inRange: bool("\(path).inrange") ?? false
            )
        }
    }

    private func commandResponseMessage(_ json: Any) -> String {
        guard let object = json as? [String: Any] else { return "ACTION RESPONSE RECEIVED" }
        if let error = object["error"] as? String, !error.isEmpty { return "ACTION ERROR: \(error)" }
        if let message = object["message"] as? String, !message.isEmpty { return "ACTION: \(message)" }
        if let status = object["status"] as? String, !status.isEmpty { return "ACTION: \(status.uppercased())" }
        if let success = object["success"] as? Bool { return success ? "ACTION COMPLETE" : "ACTION FAILED" }
        if let allowed = object["allowed"] as? Bool, !allowed { return "ACTION NOT ALLOWED" }
        return "ACTION RESPONSE RECEIVED"
    }

    private func parsePerks() -> [LivePerk] {
        guard let root = database.nodeID(at: "perks") else { return [] }
        let children = database.arrayChildren(at: root) ?? []
        return children.enumerated().compactMap { index, _ in
            let path = "perks[\(index)]"
            guard bool("\(path).listvisible") ?? false,
                  let name = string("\(path).name"), !name.isEmpty else { return nil }
            let rank = integer("\(path).rank", fallback: 0)
            let maxRank = integer("\(path).maxrank", fallback: 0)
            let description = rank > 0 ? string("\(path).perks[\(rank - 1)].description") ?? "" : ""
            return LivePerk(id: index, name: name, rank: rank, maxRank: maxRank, nextRankDescription: description)
        }
    }

    private func parseMapLocations() -> [LiveMapLocation] {
        guard let root = database.nodeID(at: "map.world.locations") else { return [] }
        let children = database.arrayChildren(at: root) ?? []
        return children.enumerated().compactMap { index, nodeID in
            let path = "map.world.locations[\(index)]"
            guard let x = number("\(path).x"), let y = number("\(path).y") else { return nil }
            return LiveMapLocation(
                id: nodeID,
                name: string("\(path).name") ?? "LOCATION \(index + 1)",
                x: x, y: y,
                discovered: bool("\(path).discovered") ?? false,
                visible: bool("\(path).visible") ?? false,
                cleared: bool("\(path).clearedstatus") ?? false,
                markerType: integer("\(path).type", fallback: -1)
            )
        }
    }

    private func describe(_ value: PipboyValue) -> String {
        switch value {
        case .null: "null"
        case .bool(let v): v ? "true" : "false"
        case .int8(let v): String(v)
        case .uint8(let v): String(v)
        case .int32(let v): String(v)
        case .uint32(let v): String(v)
        case .float32(let v): String(format: "%.6g", v)
        case .string(let v): v
        }
    }

    private func string(_ path: String) -> String? {
        if case .string(let value) = database.value(at: path) { return value }
        return nil
    }
    private func number(_ path: String) -> Double? {
        switch database.value(at: path) {
        case .float32(let v): Double(v)
        case .int32(let v): Double(v)
        case .uint32(let v): Double(v)
        case .int8(let v): Double(v)
        case .uint8(let v): Double(v)
        default: nil
        }
    }
    private func integer(_ path: String, fallback: Int) -> Int {
        guard let value = number(path), value.isFinite else { return fallback }
        return Int(value)
    }
    private func bool(_ path: String) -> Bool? {
        switch database.value(at: path) {
        case .bool(let value): value
        case .uint8(let value): value != 0
        case .int8(let value): value != 0
        case .int32(let value): value != 0
        case .uint32(let value): value != 0
        default: nil
        }
    }
    private func uint32(_ value: PipboyValue?) -> UInt32? {
        switch value {
        case .uint32(let v): v
        case .int32(let v) where v >= 0: UInt32(v)
        case .uint8(let v): UInt32(v)
        case .int8(let v) where v >= 0: UInt32(v)
        default: nil
        }
    }
}
