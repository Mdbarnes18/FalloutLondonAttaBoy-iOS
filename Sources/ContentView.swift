import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var state: AttaBoyState
    @State private var bootComplete = false

    var body: some View {
        ZStack {
            PipTheme.background.ignoresSafeArea()
            if bootComplete {
                mainInterface
                    .transition(.opacity)
            } else {
                AttaBoyBootView {
                    withAnimation(.easeInOut(duration: 0.35)) {
                        bootComplete = true
                    }
                }
                .transition(.opacity)
            }
        }
        .preferredColorScheme(.dark)
    }

    private var mainInterface: some View {
        VStack(spacing: 0) {
            HStack(alignment: .firstTextBaseline) {
                Text("ATTA-BOY")
                    .font(.system(size: 16, weight: .black, design: .monospaced))
                    .tracking(2)
                    .foregroundStyle(PipTheme.amber)
                Spacer()
                Text("FALLOUT // LONDON")
                    .font(.system(size: 8, weight: .bold, design: .monospaced))
                    .tracking(1)
                    .foregroundStyle(PipTheme.amberDim)
            }
            .padding(.horizontal, 14)
            .padding(.top, 8)
            .padding(.bottom, 7)

            HStack(spacing: 7) {
                Circle()
                    .fill(connectionColor)
                    .frame(width: 7, height: 7)
                    .shadow(color: connectionColor.opacity(0.6), radius: 4)
                Text(state.connectionLabel)
                    .font(.system(size: 8, weight: .bold, design: .monospaced))
                    .tracking(0.5)
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
                    .foregroundStyle(connectionColor)
                Spacer(minLength: 0)
                Text(state.isLiveData ? "LIVE" : "STANDBY")
                    .font(.system(size: 7, weight: .black, design: .monospaced))
                    .foregroundStyle(state.isLiveData ? PipTheme.amber : PipTheme.muted)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 7)
            .background(PipTheme.panel)
            .overlay(alignment: .bottom) {
                Rectangle().fill(PipTheme.amberDim.opacity(0.5)).frame(height: 1)
            }

            TabView(selection: $state.selectedTab) {
                StatusView()
                    .tabItem { Label("STATUS", systemImage: "waveform.path.ecg") }
                    .tag(AppTab.status)
                LondonMapView()
                    .tabItem { Label("MAP", systemImage: "map") }
                    .tag(AppTab.map)
                InventoryView()
                    .tabItem { Label("ITEMS", systemImage: "backpack") }
                    .tag(AppTab.inventory)
                RadioView()
                    .tabItem { Label("RADIO", systemImage: "dot.radiowaves.left.and.right") }
                    .tag(AppTab.radio)
                QuestView()
                    .tabItem { Label("DATA", systemImage: "text.book.closed") }
                    .tag(AppTab.quests)
            }
            .tint(PipTheme.amber)
            .toolbarBackground(PipTheme.panel, for: .tabBar)
            .toolbarBackground(.visible, for: .tabBar)
        }
        .background(PipTheme.background)
        .overlay {
            RoundedRectangle(cornerRadius: 15)
                .stroke(PipTheme.amberDim.opacity(0.35), lineWidth: 1)
                .padding(4)
                .allowsHitTesting(false)
        }
        .overlay {
            ScanlineOverlay()
                .allowsHitTesting(false)
        }
    }

    private var connectionColor: Color {
        switch state.connectionState {
        case .connected: PipTheme.amber
        case .failed: PipTheme.danger
        case .disconnected, .discovering, .connecting, .reconnecting: PipTheme.muted
        }
    }
}

private struct ScanlineOverlay: View {
    var body: some View {
        GeometryReader { proxy in
            Path { path in
                stride(from: 0, to: proxy.size.height, by: 4).forEach { y in
                    path.move(to: CGPoint(x: 0, y: y))
                    path.addLine(to: CGPoint(x: proxy.size.width, y: y))
                }
            }
            .stroke(PipTheme.amber.opacity(0.025), lineWidth: 0.6)
        }
    }
}
