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
    let id: Int
    let name: String
    let frequency: String
    let active: Bool
    let inRange: Bool
}

@MainActor
final class AttaBoyState: ObservableObject {
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

    @Published var connectionState: ConnectionState = .disconnected
    @Published var connectionHost = ""
    @Published var serverVersion = ""
    @Published var serverLanguage = ""
    @Published var lastActionStatus: String?
    @Published var liveInventory: [LiveGameItem] = []
    @Published var liveQuests: [LiveGameQuest] = []
    @Published var liveRadioStations: [LiveRadioStation] = []
    @Published var localMap: PipboyLocalMapUpdate?
    @Published var playerPosition: (x: Double, y: Double, rotation: Double)?
    @Published private(set) var isLiveData = false

    private let connectionService = ConnectionService()
    private let database = PipboyDatabase()

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
                if newState == .connected {
                    self.database.reset()
                    self.isLiveData = false
                    self.liveInventory = []
                    self.liveQuests = []
                    self.liveRadioStations = []
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

    func discoverGame() {
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
        connectionService.sendRPC(type: 12, args: [station.id])
        lastActionStatus = "RADIO REQUEST SENT"
        click()
    }
    func toggleLiveQuest(_ quest: LiveGameQuest) {
        guard let formID = quest.formID, let instance = quest.instance, let type = quest.type else {
            lastActionStatus = "QUEST ACTION UNAVAILABLE · MISSING GAME IDS"
            return
        }
        connectionService.sendRPC(type: 5, args: [formID, instance, type])
        lastActionStatus = "QUEST MARKER REQUEST SENT"
        click()
    }
    func requestLocalMapSnapshot() {
        connectionService.sendRPC(type: 13, args: [])
        lastActionStatus = "LOCAL MAP REQUEST SENT"
        click()
    }
    func setCustomMapMarker(x: Double, y: Double, local: Bool) {
        connectionService.sendRPC(type: 6, args: [x, y, local])
        lastActionStatus = "MAP MARKER REQUEST SENT"
        click()
    }
    func clearCustomMapMarker() {
        connectionService.sendRPC(type: 7, args: [])
        lastActionStatus = "MAP MARKER CLEAR REQUEST SENT"
        click()
    }
    func useItem(_ item: LiveGameItem) {
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
        guard let handle = item.handleID,
              let stack = item.stackIDs.first,
              let version = uint32(database.value(at: "inventory.version")) else {
            lastActionStatus = "DROP UNAVAILABLE · GAME IDS NOT PRESENT"
            return
        }
        connectionService.sendRPC(type: 1, args: [handle, min(max(1, count), item.count), version, stack])
        lastActionStatus = "DROP REQUEST SENT"
        click()
    }
    func favoriteItem(_ item: LiveGameItem, slot: Int) {
        guard (0...11).contains(slot),
              let handle = item.handleID,
              let stack = item.stackIDs.first,
              let version = uint32(database.value(at: "inventory.version")) else {
            lastActionStatus = "FAVORITE UNAVAILABLE · GAME IDS NOT PRESENT"
            return
        }
        connectionService.sendRPC(type: 2, args: [handle, stack, slot, version])
        lastActionStatus = "FAVORITE REQUEST SENT"
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
        case .data:
            refreshLiveData()
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
        playerPosition = {
            guard let x = number("map.world.player.x"), let y = number("map.world.player.y") else { return nil }
            return (x, y, number("map.world.player.rotation") ?? 0)
        }()
        liveInventory = parseInventory()
        liveQuests = parseQuests()
        liveRadioStations = parseRadioStations()
        isLiveData = true
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
        case 2: .weapons
        case 4: .apparel
        case 8: .aid
        case 512, 1024: .junk
        case 4096: .ammo
        case 640: .misc
        default: nil
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
            let enabled = bool("\(path).enabled") ?? true
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

    private func parseRadioStations() -> [LiveRadioStation] {
        guard let root = database.nodeID(at: "radio") else { return [] }
        let children = database.arrayChildren(at: root) ?? []
        return children.enumerated().map { index, _ in
            let path = "radio[\(index)]"
            return LiveRadioStation(
                id: index,
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
