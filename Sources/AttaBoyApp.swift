import SwiftUI

@main
struct AttaBoyApp: App {
    @StateObject private var appState = AttaBoyState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .preferredColorScheme(.dark)
        }
    }
}
