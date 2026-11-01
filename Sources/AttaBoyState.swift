import Foundation
import SwiftUI
import AudioToolbox

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

    @Published private(set) var completedQuestIDs: Set<String> {
        didSet { UserDefaults.standard.set(Array(completedQuestIDs), forKey: "completedQuestIDs") }
    }
    @Published private(set) var equippedItemIDs: Set<String> {
        didSet { UserDefaults.standard.set(Array(equippedItemIDs), forKey: "equippedItemIDs") }
    }

    init() {
        completedQuestIDs = Set(UserDefaults.standard.stringArray(forKey: "completedQuestIDs") ?? [])
        equippedItemIDs = Set(UserDefaults.standard.stringArray(forKey: "equippedItemIDs") ?? ["service-rifle", "leather-coat"])
    }

    var selectedDistrict: District {
        District.all.first(where: { $0.id == selectedDistrictID }) ?? District.all[0]
    }
    var selectedStation: RadioStation {
        RadioStation.all.first(where: { $0.id == selectedStationID }) ?? RadioStation.all[0]
    }
    var completedQuestCount: Int { completedQuestIDs.count }

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
}
