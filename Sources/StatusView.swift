import SwiftUI

struct StatusView: View {
    @EnvironmentObject private var state: AttaBoyState
    @State private var hostAddress = ""

    private var connectionColor: Color {
        if case .connected = state.connectionState { return PipTheme.amber }
        if case .failed = state.connectionState { return PipTheme.danger }
        return PipTheme.muted
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "STATUS", subtitle: "VAULT-TEC PERSONAL DATA TERMINAL")
                    PipPanel(title: "GAME LINK") {
                        HStack {
                            Circle().fill(connectionColor).frame(width: 7, height: 7)
                            Text(state.connectionLabel)
                                .font(.system(size: 9, weight: .bold, design: .monospaced))
                                .foregroundStyle(PipTheme.pale)
                            Spacer()
                            if state.isLiveData {
                                Text("LIVE").font(.system(size: 8, weight: .black, design: .monospaced)).foregroundStyle(PipTheme.amber)
                            }
                        }
                        HStack(spacing: 8) {
                            Button("AUTO DISCOVER") { state.discoverGame() }
                                .font(.system(size: 8, weight: .black, design: .monospaced))
                                .buttonStyle(.borderedProminent).tint(PipTheme.amber)
                            Button("DISCONNECT") { state.disconnectGame() }
                                .font(.system(size: 8, weight: .bold, design: .monospaced))
                                .buttonStyle(.bordered).tint(PipTheme.amber)
                        }
                        HStack(spacing: 7) {
                            TextField("GAME PC IP ADDRESS", text: $hostAddress)
                                .textInputAutocapitalization(.never)
                                .autocorrectionDisabled()
                                .keyboardType(.decimalPad)
                                .font(.system(size: 10, design: .monospaced))
                                .padding(7)
                                .overlay(Rectangle().stroke(PipTheme.amberDim.opacity(0.45)))
                            Button("CONNECT") { state.connectToGame(host: hostAddress) }
                                .font(.system(size: 8, weight: .black, design: .monospaced))
                                .buttonStyle(.bordered).tint(PipTheme.amber)
                        }
                        Text("PHONE AND GAME PC MUST BE ON THE SAME LOCAL NETWORK. ENABLE THE PIP-BOY APP OPTION IN FALLOUT 4 / FALLOUT: LONDON.")
                            .font(.system(size: 8, design: .monospaced))
                            .foregroundStyle(PipTheme.muted)
                    }
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
                            ForEach(Array(SpecialStat.all.enumerated()), id: \.element.id) { index, stat in
                                let value = state.specialValues.indices.contains(index) ? state.specialValues[index] : stat.value
                                VStack(spacing: 7) {
                                    Text(stat.name).font(.system(size: 9, weight: .black, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                    Text("\(value)").font(.system(size: 18, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
                                    HStack(spacing: 2) {
                                        ForEach(0..<10, id: \.self) { tick in
                                            Rectangle().fill(tick < value ? PipTheme.amber : PipTheme.background).frame(height: 4)
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
                    Text(state.isLiveData ? "LIVE GAME DATA RECEIVED · STAT / INVENTORY STREAM" : "AWAITING LIVE GAME DATA · DISPLAY VALUES ARE PLACEHOLDERS")
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
