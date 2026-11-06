import SwiftUI

private struct InventoryRow: Identifiable {
    let id: String
    let name: String
    let category: ItemCategory
    let count: Int
    let weight: Double
    let value: Int
    let detail: String
    let equipped: Bool
    let favorite: Bool
    let legendary: Bool
    let gameItem: LiveGameItem?
}

struct InventoryView: View {
    @EnvironmentObject private var state: AttaBoyState
    @State private var category: ItemCategory = .all
    @State private var search = ""
    @State private var favoriteSlot = 0
    @State private var selectedItemID: String?

    private var rows: [InventoryRow] {
        let source: [InventoryRow]
        if state.isLiveData {
            source = state.liveInventory.map { item in
                InventoryRow(id: item.id, name: item.name, category: item.category,
                    count: item.count, weight: item.weight, value: item.value,
                    detail: item.detail ?? "", equipped: item.equipped,
                    favorite: item.isFavorited, legendary: item.legendary, gameItem: item)
            }
        } else if state.demoModeEnabled {
            let samples = state.gameWorld == .london ? InventoryItem.samples : InventoryItem.commonwealthSamples
            source = samples.map { item in
                InventoryRow(id: item.id, name: item.name, category: item.category,
                    count: 1, weight: item.weight, value: item.value,
                    detail: item.detail, equipped: state.equippedItemIDs.contains(item.id),
                    favorite: false, legendary: false, gameItem: nil)
            }
        } else {
            source = []
        }
        return source.filter {
            (category == .all || $0.category == category) &&
            (search.isEmpty || $0.name.localizedCaseInsensitiveContains(search))
        }.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    private var selectedRow: InventoryRow? { rows.first { $0.id == selectedItemID } }


    private func categoryAssetName(_ category: ItemCategory) -> String {
        switch category {
        case .weapons: return "pack_cat_weapons"
        case .apparel: return "pack_cat_apparel"
        case .aid: return "pack_cat_aid"
        case .ammo: return "pack_cat_ammo"
        case .misc, .junk, .mods, .all: return "pack_cat_misc"
        }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "INVENTORY", subtitle: state.isLiveData ? "LIVE GAME INVENTORY" : (state.demoModeEnabled ? "DEMO INVENTORY PREVIEW" : "AWAITING LIVE GAME DATA"))
                    PipPanel(title: "CARRY WEIGHT") {
                        HStack {
                            Text(String(format: "%.1f / %.1f", state.carriedWeight, state.maxWeight))
                                .font(.system(size: 17, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
                            Spacer()
                            Text("LB").font(.system(size: 9, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        }
                        MeterRow(title: "CAPACITY", value: state.maxWeight > 0 ? Int(state.carriedWeight / state.maxWeight * 100) : 0)
                    }
                    TextField("SEARCH INVENTORY", text: $search)
                        .font(.system(size: 10, design: .monospaced)).padding(9)
                        .background(PipTheme.panel)
                        .overlay(Rectangle().stroke(PipTheme.amberDim.opacity(0.5)))
                        .foregroundStyle(PipTheme.pale)
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 6) {
                            ForEach(ItemCategory.allCases) { option in
                                Button(option.rawValue) { category = option; selectedItemID = nil }
                                    .font(.system(size: 8, weight: .bold, design: .monospaced))
                                    .padding(.horizontal, 9).padding(.vertical, 7)
                                    .foregroundStyle(category == option ? PipTheme.background : PipTheme.amber)
                                    .background(category == option ? PipTheme.amber : PipTheme.panel)
                                    .overlay(Rectangle().stroke(PipTheme.amberDim))
                            }
                        }
                    }
                    PipPanel(title: "ITEMS // \(rows.count)") {
                        if rows.isEmpty {
                            Text(state.isLiveData ? "NO ITEMS IN THIS CATEGORY" : (state.demoModeEnabled ? "PREVIEW INVENTORY · DEMO MODE" : "CONNECT TO THE SELECTED GAME TO LOAD INVENTORY"))
                                .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        }
                        ForEach(rows) { row in
                            Button { selectedItemID = row.id } label: {
                                HStack(spacing: 9) {
                                    Image(categoryAssetName(row.category))
                                        .resizable().scaledToFit().frame(width: 23, height: 23).foregroundStyle(PipTheme.amberDim)
                                    VStack(alignment: .leading, spacing: 3) {
                                        Text(row.name.uppercased())
                                            .font(.system(size: 10, weight: .bold, design: .monospaced))
                                            .foregroundStyle(PipTheme.pale).lineLimit(1)
                                        Text("\(row.category.rawValue) · x\(row.count) · WT \(String(format: "%.1f", row.weight)) · £\(row.value)")
                                            .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                    }
                                    Spacer()
                                    if row.equipped { Text("E").foregroundStyle(PipTheme.amber) }
                                    if row.favorite { Text("★").foregroundStyle(PipTheme.amber) }
                                    if row.legendary { Text("L").foregroundStyle(PipTheme.amber) }
                                    Image(systemName: selectedItemID == row.id ? "chevron.down" : "chevron.right")
                                        .font(.system(size: 8)).foregroundStyle(PipTheme.muted)
                                }
                                .padding(.vertical, 7).contentShape(Rectangle())
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    if let row = selectedRow {
                        PipPanel(title: "ITEM INSPECTOR") {
                            Text(row.name.uppercased()).font(.system(size: 13, weight: .black, design: .monospaced)).foregroundStyle(PipTheme.pale)
                            Text(row.detail.isEmpty ? "NO DESCRIPTION PROVIDED" : row.detail)
                                .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                            Text("COUNT \(row.count) · WEIGHT \(String(format: "%.2f", row.weight)) · VALUE £\(row.value)")
                                .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.amberDim)
                            if let item = row.gameItem {
                                if let damage = item.damage { detailLine("DAMAGE", value: String(format: "%.0f", damage)) }
                                if let armor = item.armor { detailLine("ARMOR", value: String(format: "%.0f", armor)) }
                                if let resistance = item.radiationResistance { detailLine("RAD RES", value: String(format: "%.0f", resistance)) }
                                if let resistance = item.energyResistance { detailLine("ENG RES", value: String(format: "%.0f", resistance)) }
                                HStack {
                                    Button("USE") { state.useItem(item) }.disabled(item.handleID == nil || item.stackIDs.isEmpty)
                                    Button("DROP 1") { state.dropItem(item) }.disabled(item.handleID == nil || item.stackIDs.isEmpty)
                                }
                                .font(.system(size: 9, weight: .black, design: .monospaced))
                                .buttonStyle(.borderedProminent).tint(PipTheme.amber)
                                HStack {
                                    Picker("FAVORITE SLOT", selection: $favoriteSlot) {
                                        ForEach(0..<12, id: \.self) { slot in Text("SLOT \(slot + 1)").tag(slot) }
                                    }.font(.system(size: 8, design: .monospaced))
                                    Button("SET FAVORITE") { state.favoriteItem(item, slot: favoriteSlot) }
                                        .font(.system(size: 8, weight: .bold, design: .monospaced))
                                        .disabled(item.handleID == nil || item.stackIDs.isEmpty)
                                }
                            } else {
                                Text("PREVIEW ONLY · ACTIONS REQUIRE A LIVE GAME CONNECTION")
                                    .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                            }
                            if let status = state.lastActionStatus {
                                Text(status).font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.amber)
                            }
                        }
                    }
                }.padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
    }

    private func detailLine(_ title: String, value: String) -> some View {
        HStack {
            Text(title).foregroundStyle(PipTheme.muted)
            Spacer()
            Text(value).foregroundStyle(PipTheme.pale)
        }.font(.system(size: 9, design: .monospaced))
    }

    private func symbol(for category: ItemCategory) -> String {
        switch category {
        case .weapons: "scope"
        case .apparel: "tshirt"
        case .aid: "cross.case"
        case .ammo: "circle.grid.2x2"
        case .junk: "shippingbox"
        case .mods: "wrench"
        case .misc, .all: "shippingbox"
        }
    }
}
