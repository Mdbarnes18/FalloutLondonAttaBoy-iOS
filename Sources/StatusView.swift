import SwiftUI

struct StatusView: View {
    @EnvironmentObject private var state: AttaBoyState
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "STATUS", subtitle: "VAULT-TEC PERSONAL DATA TERMINAL")
                    PipPanel(title: "VITAL SIGNS") {
                        HStack(spacing: 18) {
                            VStack(alignment: .leading, spacing: 13) {
                                MeterRow(title: "HEALTH", value: state.health, color: PipTheme.danger)
                                MeterRow(title: "ACTION POINTS", value: state.actionPoints)
                            }
                            VStack(spacing: 4) {
                                Image(systemName: "person.crop.circle").font(.system(size: 42, weight: .ultraLight))
                                Text("WANDERER").font(.system(size: 8, weight: .bold, design: .monospaced))
                            }
                            .foregroundStyle(PipTheme.amberDim)
                        }
                    }
                    PipPanel(title: "GENERAL") {
                        HStack(spacing: 9) {
                            ValueTile(label: "CAPS", value: "\(state.caps)", symbol: "sterlingsign.circle")
                            ValueTile(label: "LEVEL", value: "12", symbol: "arrow.up.circle")
                            ValueTile(label: "WEIGHT", value: String(format: "%.1f", state.carriedWeight), symbol: "scalemass")
                        }
                    }
                    PipPanel(title: "S.P.E.C.I.A.L.") {
                        HStack(spacing: 0) {
                            ForEach(SpecialStat.all) { stat in
                                VStack(spacing: 7) {
                                    Text(stat.name).font(.system(size: 9, weight: .black, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                    Text("\(stat.value)").font(.system(size: 18, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
                                    HStack(spacing: 2) {
                                        ForEach(0..<10, id: \.self) { index in
                                            Rectangle().fill(index < stat.value ? PipTheme.amber : PipTheme.background).frame(height: 4)
                                        }
                                    }
                                }
                                .frame(maxWidth: .infinity)
                            }
                        }
                    }
                    PipPanel(title: "CURRENT EQUIPMENT") {
                        equipmentLine("SERVICE RIFLE", detail: "PRIMARY", icon: "scope")
                        equipmentLine("LEATHER COAT", detail: "APPAREL", icon: "tshirt")
                    }
                    Text("NO OFFICIAL GAME CONNECTION · MOCK COMPANION DATA")
                        .font(.system(size: 8, weight: .medium, design: .monospaced))
                        .foregroundStyle(PipTheme.muted)
                        .multilineTextAlignment(.center)
                }
                .padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
    }

    private func equipmentLine(_ name: String, detail: String, icon: String) -> some View {
        HStack {
            Image(systemName: icon).frame(width: 24).foregroundStyle(PipTheme.amberDim)
            Text(name).font(.system(size: 11, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
            Spacer()
            Text(detail).font(.system(size: 9, weight: .medium, design: .monospaced)).foregroundStyle(PipTheme.muted)
        }
    }
}
