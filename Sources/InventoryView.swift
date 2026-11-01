import SwiftUI

private struct InventoryDisplayItem: Identifiable {
    let id: String
    let name: String
    let detail: String
    let category: ItemCategory
    let weight: Double
    let value: Int
    let symbol: String
    let equipped: Bool
    let live: Bool
}

struct InventoryView: View {
    @EnvironmentObject private var state: AttaBoyState
    @State private var category: ItemCategory = .all

    private var visibleItems: [InventoryDisplayItem] {
        let items: [InventoryDisplayItem]
        if state.isLiveData {
            items = state.liveInventory.map { item in
                InventoryDisplayItem(
                    id: item.id,
                    name: item.name.uppercased(),
                    detail: "LIVE GAME DATA · COUNT \(item.count)",
                    category: item.category,
                    weight: item.weight,
                    value: item.value,
                    symbol: symbol(for: item.category),
                    equipped: false,
                    live: true
                )
            }
        } else {
            items = InventoryItem.samples.map { item in
                InventoryDisplayItem(
                    id: item.id,
                    name: item.name,
                    detail: item.detail,
                    category: item.category,
                    weight: item.weight,
                    value: item.value,
                    symbol: item.symbol,
                    equipped: state.equippedItemIDs.contains(item.id),
                    live: false
                )
            }
        }
        return items.filter { category == .all || $0.category == category }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "INVENTORY", subtitle: state.isLiveData ? "LIVE GAME INVENTORY STREAM" : "PERSONAL PROPERTY REGISTER · DEMO")
                    PipPanel(title: "CARRY WEIGHT") {
                        HStack {
                            Text(String(format: "%.1f / 180", state.carriedWeight)).font(.system(size: 17, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
                            Spacer()
                            Text("LB").font(.system(size: 9, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        }
                        MeterRow(title: "CAPACITY", value: Int(state.carriedWeight / 180 * 100))
                    }
                    Picker("Category", selection: $category) {
                        ForEach(ItemCategory.allCases) { item in
                            Text(item.rawValue).tag(item)
                        }
                    }
                    .pickerStyle(.segmented)
                    .tint(PipTheme.amber)
                    PipPanel(title: "ITEMS // \(visibleItems.count)") {
                        if visibleItems.isEmpty {
                            Text(state.isLiveData ? "NO INVENTORY ITEMS RECEIVED YET" : "NO ITEMS IN THIS CATEGORY")
                                .font(.system(size: 9, design: .monospaced))
                                .foregroundStyle(PipTheme.muted)
                        }
                        ForEach(visibleItems) { item in
                            HStack(spacing: 12) {
                                Image(systemName: item.symbol).font(.system(size: 20)).frame(width: 30).foregroundStyle(PipTheme.amberDim)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(item.name).font(.system(size: 11, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
                                    Text(item.detail).font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                    Text("WT \(String(format: "%.1f", item.weight))  ·  VALUE £\(item.value)").font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.amberDim)
                                }
                                Spacer()
                                if item.live {
                                    Text("LIVE").font(.system(size: 8, weight: .black, design: .monospaced)).foregroundStyle(PipTheme.amber)
                                } else if item.category == .weapons || item.category == .apparel {
                                    Button(item.equipped ? "EQUIPPED" : "EQUIP") {
                                        if let sample = InventoryItem.samples.first(where: { $0.id == item.id }) {
                                            state.toggleEquipment(sample)
                                        }
                                    }
                                    .font(.system(size: 8, weight: .black, design: .monospaced))
                                    .padding(.horizontal, 8).padding(.vertical, 7)
                                    .background(item.equipped ? PipTheme.amber : PipTheme.panelRaised, in: RoundedRectangle(cornerRadius: 4))
                                    .foregroundStyle(item.equipped ? PipTheme.background : PipTheme.amber)
                                }
                            }
                            .padding(.vertical, 7)
                            if item.id != visibleItems.last?.id { Rectangle().fill(PipTheme.amberDim.opacity(0.25)).frame(height: 1) }
                        }
                    }
                }
                .padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
    }

    private func symbol(for category: ItemCategory) -> String {
        switch category {
        case .weapons: "scope"
        case .apparel: "tshirt"
        case .aid: "cross.case"
        case .misc, .all: "shippingbox"
        }
    }
}
