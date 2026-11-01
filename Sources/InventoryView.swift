import SwiftUI

struct InventoryView: View {
    @EnvironmentObject private var state: AttaBoyState
    @State private var category: ItemCategory = .all

    private var visibleItems: [InventoryItem] {
        InventoryItem.samples.filter { category == .all || $0.category == category }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "INVENTORY", subtitle: "PERSONAL PROPERTY REGISTER")
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
                        ForEach(visibleItems) { item in
                            HStack(spacing: 12) {
                                Image(systemName: item.symbol).font(.system(size: 20)).frame(width: 30).foregroundStyle(PipTheme.amberDim)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(item.name).font(.system(size: 11, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
                                    Text(item.detail).font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                    Text("WT \(String(format: "%.1f", item.weight))  ·  VALUE £\(item.value)").font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.amberDim)
                                }
                                Spacer()
                                if item.category == .weapons || item.category == .apparel {
                                    Button(state.equippedItemIDs.contains(item.id) ? "EQUIPPED" : "EQUIP") {
                                        state.toggleEquipment(item)
                                    }
                                    .font(.system(size: 8, weight: .black, design: .monospaced))
                                    .padding(.horizontal, 8).padding(.vertical, 7)
                                    .background(state.equippedItemIDs.contains(item.id) ? PipTheme.amber : PipTheme.panelRaised, in: RoundedRectangle(cornerRadius: 4))
                                    .foregroundStyle(state.equippedItemIDs.contains(item.id) ? PipTheme.background : PipTheme.amber)
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
}
