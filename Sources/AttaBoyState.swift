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
}

@MainActor
final class AttaBoyState: ObservableObject {
    @Published var selectedTab: AppTab = .status
    @Published var selectedDistrictID = District.all[0].id
    @Published var selectedCategory: ItemCategory = .all
    @Published var selectedStationID = RadioStation.all[0].id
    @Published var isRadioPlaying = false

    @Published var health = 82
    @Published var actionPoints = 76
    @Published var caps = 248
    @Published var carriedWeight = 34.5
    @Published var specialValues = SpecialStat.all.map(\.value)

    @Published var connectionState: ConnectionState = .disconnected
    @Published var connectionHost = ""
    @Published var liveInventory: [LiveGameItem] = []
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
        case .connected: isLiveData ? "CONNECTED · LIVE DATA" : "CONNECTED · WAITING FOR DATA"
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
        if completedQuestIDs.contains(quest.id) {
            completedQuestIDs.remove(quest.id)
        } else {
            completedQuestIDs.insert(quest.id)
        }
        click()
    }
    func toggleEquipment(_ item: InventoryItem) {
        if equippedItemIDs.contains(item.id) {
            equippedItemIDs.remove(item.id)
        } else {
            equippedItemIDs.insert(item.id)
        }
        click()
    }
    func toggleRadio() {
        isRadioPlaying.toggle()
        click()
    }
    func click() {
        AudioServicesPlaySystemSound(1104)
    }

    private func apply(_ update: PipboyUpdate) {
        database.apply(update)
        guard case .data = update else { return }

        func number(_ path: String) -> Double? {
            switch database.value(at: path) {
            case .float32(let v): return Double(v)
            case .int32(let v): return Double(v)
            case .uint32(let v): return Double(v)
            case .int8(let v): return Double(v)
            case .uint8(let v): return Double(v)
            default: return nil
            }
        }
        func integer(_ path: String, fallback: Int) -> Int {
            guard let value = number(path), value.isFinite else { return fallback }
            return Int(value)
        }

        health = integer("playerinfo.currhp", fallback: health)
        actionPoints = integer("playerinfo.currap", fallback: actionPoints)
        caps = integer("playerinfo.caps", fallback: caps)
        carriedWeight = number("playerinfo.currweight") ?? carriedWeight
        specialValues = (0..<7).map { index in
            integer("special[\(index)].value", fallback: specialValues.indices.contains(index) ? specialValues[index] : 5)
        }
        liveInventory = parseInventory()
        isLiveData = true
    }

    private func parseInventory() -> [LiveGameItem] {
        guard let root = database.nodeID(at: "inventory") else { return [] }
        var result: [LiveGameItem] = []
        walkInventory(nodeID: root, path: "inventory", inherited: .misc, depth: 0, into: &result)
        var unique: [String: LiveGameItem] = [:]
        for item in result { unique[item.id] = item }
        return unique.values.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    private func walkInventory(nodeID: UInt32, path: String, inherited: ItemCategory, depth: Int, into result: inout [LiveGameItem]) {
        guard depth < 8 else { return }
        let name = stringValue("\(path).text") ?? stringValue("\(path).name")
        if let name, !name.isEmpty {
            let weight = numberValue("\(path).weight") ?? 0
            let value = Int(numberValue("\(path).value") ?? 0)
            let count = Int(numberValue("\(path).count") ?? numberValue("\(path).quantity") ?? 1)
            let category: ItemCategory
            if inherited != .all { category = inherited }
            else if database.nodeID(at: "\(path).paperdollsection") != nil { category = .apparel }
            else if database.nodeID(at: "\(path).currenthpgain") != nil { category = .aid }
            else if database.nodeID(at: "\(path).damage") != nil { category = .weapons }
            else { category = .misc }
            let rawID = database.value(at: "\(path).handleid").map(String(describing:)) ?? path
            result.append(LiveGameItem(id: rawID + category.rawValue, name: name, category: category, count: max(1, count), weight: weight, value: value))
            return
        }

        for (key, childID) in database.objectChildren(atNode: nodeID) {
            let category = categoryFor(key) ?? inherited
            walkInventory(nodeID: childID, path: "\(path).\(key)", inherited: category, depth: depth + 1, into: &result)
        }
        for (index, childID) in (database.arrayChildren(at: nodeID) ?? []).enumerated() {
            walkInventory(nodeID: childID, path: "\(path)[\(index)]", inherited: inherited, depth: depth + 1, into: &result)
        }
    }

    private func categoryFor(_ key: String) -> ItemCategory? {
        switch key.lowercased() {
        case "weapons", "weapon": .weapons
        case "apparel", "armor", "armour": .apparel
        case "aid", "medical": .aid
        case "misc", "miscellaneous", "junk", "ammo", "ammunition": .misc
        default: nil
        }
    }

    private func stringValue(_ path: String) -> String? {
        if case .string(let value) = database.value(at: path) { return value }
        return nil
    }

    private func numberValue(_ path: String) -> Double? {
        switch database.value(at: path) {
        case .float32(let value): Double(value)
        case .int32(let value): Double(value)
        case .uint32(let value): Double(value)
        case .uint8(let value): Double(value)
        case .int8(let value): Double(value)
        default: nil
        }
    }
}
