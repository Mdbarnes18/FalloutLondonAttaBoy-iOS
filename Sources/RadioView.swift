import SwiftUI

struct RadioView: View {
    @EnvironmentObject private var state: AttaBoyState
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "RADIO", subtitle: "LONDON FREQUENCY RECEIVER")
                    PipPanel(title: "TUNER") {
                        VStack(spacing: 14) {
                            HStack(alignment: .firstTextBaseline, spacing: 5) {
                                Text(state.selectedStation.frequency).font(.system(size: 52, weight: .black, design: .monospaced)).foregroundStyle(PipTheme.pale).contentTransition(.numericText())
                                Text("FM").font(.system(size: 13, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.amberDim)
                            }
                            HStack(spacing: 3) {
                                ForEach(0..<31, id: \.self) { index in
                                    Capsule().fill(index % 5 == 0 ? PipTheme.amber : PipTheme.amberDim.opacity(0.65))
                                        .frame(height: index % 5 == 0 ? 19 : 10)
                                }
                            }
                            Text(state.selectedStation.name).font(.system(size: 16, weight: .black, design: .monospaced)).tracking(1).foregroundStyle(PipTheme.amber)
                            Text(state.selectedStation.description.uppercased()).font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                            Button {
                                withAnimation(.easeInOut(duration: 0.2)) { state.toggleRadio() }
                            } label: {
                                Label(state.isRadioPlaying ? "STOP RECEIVER" : "ACTIVATE RECEIVER", systemImage: state.isRadioPlaying ? "stop.fill" : "play.fill")
                                    .font(.system(size: 11, weight: .black, design: .monospaced))
                                    .frame(maxWidth: .infinity).padding(13)
                            }
                            .buttonStyle(TerminalButtonStyle())
                            Text(state.isRadioPlaying ? "RECEIVER ACTIVE · AUDIO DEMO NOT CONNECTED" : "RECEIVER STANDBY")
                                .font(.system(size: 8, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.amberDim)
                        }
                    }
                    PipPanel(title: "AVAILABLE FREQUENCIES") {
                        ForEach(RadioStation.all) { station in
                            Button {
                                state.selectStation(station)
                            } label: {
                                HStack {
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text(station.name).font(.system(size: 11, weight: .bold, design: .monospaced))
                                        Text(station.description).font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                    }
                                    Spacer()
                                    Text(station.frequency).font(.system(size: 15, weight: .bold, design: .monospaced))
                                    Image(systemName: state.selectedStationID == station.id ? "largecircle.fill.circle" : "circle").padding(.leading, 5)
                                }
                                .foregroundStyle(state.selectedStationID == station.id ? PipTheme.pale : PipTheme.amberDim)
                                .padding(.vertical, 8)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    Text("NO BROADCAST AUDIO IS INCLUDED IN THIS BUILD")
                        .font(.system(size: 8, weight: .medium, design: .monospaced)).foregroundStyle(PipTheme.muted)
                }
                .padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
    }
}
