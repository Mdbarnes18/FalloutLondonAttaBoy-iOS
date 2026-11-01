import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var state: AttaBoyState

    var body: some View {
        ZStack {
            PipTheme.background.ignoresSafeArea()
            TabView(selection: $state.selectedTab) {
                StatusView().tabItem { Label("STATUS", systemImage: "waveform.path.ecg") }.tag(AppTab.status)
                LondonMapView().tabItem { Label("MAP", systemImage: "map") }.tag(AppTab.map)
                InventoryView().tabItem { Label("ITEMS", systemImage: "backpack") }.tag(AppTab.inventory)
                RadioView().tabItem { Label("RADIO", systemImage: "dot.radiowaves.left.and.right") }.tag(AppTab.radio)
                QuestView().tabItem { Label("DATA", systemImage: "text.book.closed") }.tag(AppTab.quests)
            }
            .tint(PipTheme.amber)
            .toolbarBackground(PipTheme.panel, for: .tabBar)
            .toolbarBackground(.visible, for: .tabBar)
        }
    }
}
