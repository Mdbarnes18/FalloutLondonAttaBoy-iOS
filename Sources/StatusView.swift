import SwiftUI

struct StatusView: View {
    @EnvironmentObject private var state: AttaBoyState
    @State private var hostAddress = ""

    private var connectionColor: Color {
        if case .connected = state.connectionState { return PipTheme.amber }
        if case .failed = state.connectionState { return PipTheme.danger }
        return PipTheme.muted
    }
    private var hpPercent: Int { state.maxHealth > 0 ? Int(Double(state.health) / Double(state.maxHealth) * 100) : 0 }
    private var apPercent: Int { state.maxActionPoints > 0 ? Int(Double(state.actionPoints) / Double(state.maxActionPoints) * 100) : 0 }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "STATUS", subtitle: "LIVE PLAYER STATUS TERMINAL")
                    PipPanel(title: "GAME LINK") {
                        HStack {
                            Circle().fill(connectionColor).frame(width: 7, height: 7)
                            Text(state.connectionLabel)
                                .font(.system(size: 9, weight: .bold, design: .monospaced))
                                .foregroundStyle(PipTheme.pale)
                            Spacer()
                            if state.isLiveData { Text("LIVE").font(.system(size: 8, weight: .black, design: .monospaced)).foregroundStyle(PipTheme.amber) }
                        }
                        if !state.serverLanguage.isEmpty || !state.serverVersion.isEmpty {
                            Text("SERVER \(state.serverVersion) · LANG \(state.serverLanguage)")
                                .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
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
                                .textInputAutocapitalization(.never).autocorrectionDisabled()
                                .keyboardType(.decimalPad)
                                .font(.system(size: 10, design: .monospaced)).padding(7)
                                .overlay(Rectangle().stroke(PipTheme.amberDim.opacity(0.45)))
                            Button("CONNECT") { state.connectToGame(host: hostAddress) }
                                .font(.system(size: 8, weight: .black, design: .monospaced))
                                .buttonStyle(.bordered).tint(PipTheme.amber)
                        }
                        Text("SAME PRIVATE LAN REQUIRED · ENABLE THE GAME-SIDE COMPANION SERVICE. iOS BROADCAST DISCOVERY NEEDS APPLE MULTICAST ENTITLEMENT; MANUAL IP CONNECTION DOES NOT.")
                            .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                    }
                    PipPanel(title: "VITAL SIGNS") {
                        HStack(spacing: 18) {
                            VStack(alignment: .leading, spacing: 13) {
                                MeterRow(title: "HEALTH · \(state.health)/\(state.maxHealth)", value: hpPercent, color: PipTheme.danger)
                                MeterRow(title: "ACTION POINTS · \(state.actionPoints)/\(state.maxActionPoints)", value: apPercent)
                                MeterRow(title: "RADIATION", value: state.radiation)
                            }
                            VStack(spacing: 4) {
                                Image(systemName: "person.crop.circle").font(.system(size: 42, weight: .ultraLight))
                                Text("WANDERER").font(.system(size: 8, weight: .bold, design: .monospaced))
                            }.foregroundStyle(PipTheme.amberDim)
                        }
                    }
                    PipPanel(title: "GENERAL") {
                        HStack(spacing: 9) {
                            ValueTile(label: "LEVEL", value: "\(state.level)", symbol: "arrow.up.circle")
                            ValueTile(label: "PERKS", value: "\(state.perkPoints)", symbol: "star.circle")
                            ValueTile(label: "WEIGHT", value: String(format: "%.1f/%.1f", state.carriedWeight, state.maxWeight), symbol: "scalemass")
                        }
                        VStack(alignment: .leading, spacing: 5) {
                            Text("XP PROGRESS · \(Int(state.xpProgress * 100))%")
                                .font(.system(size: 9, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
                            ProgressView(value: min(max(state.xpProgress, 0), 1)).tint(PipTheme.amber)
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
                                }.frame(maxWidth: .infinity)
                            }
                        }
                    }
                    if !state.livePerks.isEmpty {
                        PipPanel(title: "PERKS // \(state.livePerks.count)") {
                            ForEach(state.livePerks) { perk in
                                VStack(alignment: .leading, spacing: 3) {
                                    HStack {
                                        Text(perk.name.uppercased())
                                            .font(.system(size: 9, weight: .bold, design: .monospaced))
                                            .foregroundStyle(PipTheme.pale)
                                        Spacer()
                                        Text("\(perk.rank)/\(perk.maxRank)")
                                            .font(.system(size: 8, design: .monospaced))
                                            .foregroundStyle(PipTheme.amberDim)
                                    }
                                    if !perk.nextRankDescription.isEmpty {
                                        Text(perk.nextRankDescription)
                                            .font(.system(size: 8, design: .monospaced))
                                            .foregroundStyle(PipTheme.muted)
                                    }
                                }
                                .padding(.vertical, 4)
                            }
                        }
                    }
                    PipPanel(title: "MEDICAL") {
                        HStack(spacing: 8) {
                            Button { state.useStimpak() } label: {
                                Label("STIMPAK", image: "pack_med_stimpak")
                            }
                            Button { state.useRadAway() } label: {
                                Label("RADAWAY", image: "pack_med_radaway")
                            }
                        }
                        .font(.system(size: 9, weight: .black, design: .monospaced))
                        .buttonStyle(.borderedProminent).tint(PipTheme.amber)
                        HStack(spacing: 18) {
                            Label("AUTODOC", image: "pack_med_autodoc")
                            Label("DOCTOR'S BAG", image: "pack_med_doctors_bag")
                        }
                        .font(.system(size: 8, weight: .bold, design: .monospaced))
                        .foregroundStyle(PipTheme.muted)
                        Text("VISUAL REFERENCES ONLY · THESE SYSTEMS ARE NOT YET ACTIVE")
                            .font(.system(size: 6, design: .monospaced))
                            .foregroundStyle(PipTheme.muted)
                        Toggle("AUTO-STIMPAK", isOn: Binding(
                            get: { state.autoStimpakEnabled },
                            set: { state.setAutoStimpakEnabled($0) }
                        ))
                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                        .tint(PipTheme.amber)
                        Text("TRIGGER AT \(Int(state.autoStimpakThreshold * 100))% HP")
                            .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        Slider(value: Binding(
                            get: { state.autoStimpakThreshold },
                            set: { state.setAutoStimpakThreshold($0) }
                        ), in: 0.10...0.90, step: 0.05).tint(PipTheme.amber)
                        Text("AUTO USE IS OFF BY DEFAULT. ENABLE IT TO ALLOW THE APP TO USE A STIMPAK WHEN HP FALLS BELOW THE THRESHOLD.")
                            .font(.system(size: 7, design: .monospaced)).foregroundStyle(PipTheme.muted)
                    }
                    LimbConditionPanel(conditions: state.limbConditions)
                    if !state.activeEffects.isEmpty {
                        PipPanel(title: "ACTIVE EFFECTS") {
                            ForEach(state.activeEffects, id: \.self) { effect in
                                Text("· \(effect)").font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.pale)
                            }
                        }
                    }
                    if let status = state.lastActionStatus {
                        Text(status).font(.system(size: 9, weight: .bold, design: .monospaced))
                            .foregroundStyle(PipTheme.amber).frame(maxWidth: .infinity, alignment: .leading)
                    }
                    Text(state.isLiveData ? "VALUES REFRESH FROM THE GAME DATABASE" : "DEMO VALUES ONLY · CONNECT TO LOAD YOUR CHARACTER")
                        .font(.system(size: 8, weight: .medium, design: .monospaced))
                        .foregroundStyle(PipTheme.muted).multilineTextAlignment(.center)
                }.padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
    }
}
