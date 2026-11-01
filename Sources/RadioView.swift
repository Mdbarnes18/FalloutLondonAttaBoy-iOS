import SwiftUI

struct RadioView: View {
    @EnvironmentObject private var state: AttaBoyState

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "RADIO", subtitle: "LIVE IN-GAME RADIO CONTROL")
                    if !state.isLiveData {
                        PipPanel(title: "RECEIVER OFFLINE") {
                            Text("CONNECT TO FALLOUT TO READ THE GAME'S RADIO STATIONS.")
                                .font(.system(size: 10, design: .monospaced)).foregroundStyle(PipTheme.muted)
                            Text("This screen does not stream or simulate broadcast audio.")
                                .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.amberDim)
                        }
                    } else if state.liveRadioStations.isEmpty {
                        PipPanel(title: "RADIO DATA UNAVAILABLE") {
                            Text("The current game database has not exposed a Radio station list.")
                                .font(.system(size: 10, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        }
                    } else {
                        let active = state.liveRadioStations.first(where: \.active)
                        PipPanel(title: "TUNER") {
                            VStack(spacing: 10) {
                                Text(active?.frequency ?? "—")
                                    .font(.system(size: 48, weight: .black, design: .monospaced))
                                    .foregroundStyle(PipTheme.pale)
                                Text(active?.name.uppercased() ?? "NO ACTIVE STATION")
                                    .font(.system(size: 13, weight: .black, design: .monospaced))
                                    .foregroundStyle(PipTheme.amber)
                                Text(active == nil ? "SELECT A STATION BELOW" : "ACTIVE IN FALLOUT")
                                    .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                            }.frame(maxWidth: .infinity)
                        }
                        PipPanel(title: "AVAILABLE GAME STATIONS // \(state.liveRadioStations.count)") {
                            ForEach(state.liveRadioStations) { station in
                                Button { state.toggleLiveRadio(station) } label: {
                                    HStack(spacing: 9) {
                                        Image(systemName: station.active ? "dot.radiowaves.left.and.right" : "circle")
                                            .foregroundStyle(station.active ? PipTheme.pale : PipTheme.amberDim)
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(station.name.uppercased())
                                                .font(.system(size: 10, weight: .bold, design: .monospaced))
                                                .foregroundStyle(station.active ? PipTheme.pale : PipTheme.amber)
                                            Text(station.inRange ? "IN RANGE" : "OUT OF RANGE")
                                                .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                        }
                                        Spacer()
                                        Text(station.frequency)
                                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                                            .foregroundStyle(PipTheme.pale)
                                        Text(station.active ? "ON" : "TUNE")
                                            .font(.system(size: 8, weight: .black, design: .monospaced))
                                            .foregroundStyle(PipTheme.amberDim)
                                    }.padding(.vertical, 8).contentShape(Rectangle())
                                }.buttonStyle(.plain)
                                Rectangle().fill(PipTheme.amberDim.opacity(0.25)).frame(height: 1)
                            }
                        }
                        Text("TAPPING A STATION SENDS THE GAME'S TOGGLE-RADIO COMMAND. AUDIO PLAYS THROUGH THE GAME.")
                            .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                            .multilineTextAlignment(.center)
                    }
                    if let status = state.lastActionStatus {
                        Text(status).font(.system(size: 8, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.amber)
                    }
                }.padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
    }
}
