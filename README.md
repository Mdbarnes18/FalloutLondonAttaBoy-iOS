# Atta-Boy: Fallout London Companion

A native SwiftUI companion interface for Fallout 4 / Fallout: London. The app uses the established Pip-Boy companion protocol over a private local network. It is an independent fan project and is not affiliated with or endorsed by Bethesda or Team FOLON.

## Build an unsigned IPA for SideStore

Every push to `main` triggers the macOS GitHub Actions build.

1. Open the repository's **Actions** tab.
2. Select **Build unsigned iOS IPA**.
3. Wait for a successful run.
4. Download the `AttaBoy-unsigned-IPA` artifact.
5. Import the IPA into SideStore and let SideStore sign it with your Apple ID.

The artifact is unsigned. The build does not contain an Apple signing identity or provisioning profile.

## Current implementation

### Protocol and connection

- UDP 28000 discovery request using `{"cmd":"autodiscover"}`.
- TCP connection on port 27000.
- Five-byte little-endian frame header (UInt32 payload size + UInt8 channel).
- Connection accepted/refused messages (channels 1 and 2).
- Data updates, local-map snapshots, and command responses (channels 3, 4, and 6).
- Incremental binary database/object graph.
- Reference-client keep-alive behavior: echo received keep-alives and send one after ordinary traffic when the two-second interval has elapsed.
- Reconnection after connection loss.
- Manual IP connection as a direct unicast fallback.

### ATTA-Boy presentation

- Startup sequence with hardware-style initialization and Team FOLON credit.
- Amber CRT presentation, scanline treatment, and persistent connection/live-data indicator across the main tabs.
- Adapted from the earlier FalloutLondonCompanion project while preserving the current app's newer live-data and protocol implementation.

### Live game data

- STAT: HP/AP, radiation, carry weight, level, XP progress, perk points, SPECIAL, limb condition, active effects when present in the stream.
- INV: live item list, categories, count, weight, value, favorite/equipped/legendary indicators, and available item metadata.
- DATA: live quests and objectives, quest marker activation, and searchable flattened database values.
- MAP: live player world coordinates, a coordinate plot of game-provided discovered/visible locations, fast-travel confirmation, custom marker controls, and the local-map snapshot viewer with the player marker transformed from the snapshot's world-coordinate corners.
- RADIO: live station name/frequency/range/active state and ToggleRadioStation command.
- MEDICAL: manual Stimpak/RadAway actions and opt-in Auto-Stimpak using the verified object-ID/handle/stack/version database references.

The game remains the authority. Gameplay RPCs are gated until the connection is established and live game data has arrived. The app sends commands and displays game updates; it does not locally pretend that an action succeeded. A command response or subsequent game-data update is needed to confirm the result.

## iOS networking limitation

Fallout's legacy discovery mechanism uses UDP broadcast. Apple requires the restricted `com.apple.developer.networking.multicast` entitlement to send or receive broadcast traffic on physical iOS/iPadOS devices. Apple must approve this entitlement; SideStore signing cannot create it if the provisioning profile does not contain it.

- **Manual IP connection uses TCP unicast** and does not require the multicast entitlement.
- The app includes `NSLocalNetworkUsageDescription` for local-network access.
- Auto-discovery may fail on a physical iPhone/iPad without Apple's multicast entitlement. In that case, enter the gaming PC's private LAN IP address in STATUS and tap CONNECT.
- Do not expose TCP 27000 or UDP 28000 to the public internet. Keep the game and phone on a trusted private network.

Apple references:
- [Choosing the right networking API (TN3151)](https://developer.apple.com/documentation/technotes/tn3151-choosing-the-right-networking-api)
- [Understanding local network privacy (TN3179)](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Multicast networking entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.multicast)

## Game-side setup

1. Launch Fallout: London through the supported game/F4SE setup and load a save.
2. Enable the Pip-Boy companion service using the option/configuration supported by your installed Fallout 4 runtime.
3. Allow the game through the PC firewall on the **Private** network profile.
4. Connect the phone and PC to the same private LAN/Wi-Fi.
5. In Atta-Boy, use AUTO DISCOVER if your iOS build has the multicast entitlement; otherwise enter the PC's LAN IP and tap CONNECT.

The old Gameplay toggle is not present on every Fallout 4 runtime. Anniversary Edition and other updated runtimes may require a runtime-specific companion-service enabler. Verify that any F4SE plugin you install explicitly supports your exact runtime and Fallout: London setup; do not assume a generic Fallout 4 plugin is compatible.

## Feature verification boundary

The protocol implementation and screen integrations are based on the user's companion implementation plus public protocol references such as PyPipboy, PyPipboyApp, and the Pip-Boy protocol specification. These references establish the packet layout, message channels, RPC identifiers, and observed data paths. They do not prove that every field or command behaves identically in every Fallout 4/Fallout: London runtime.

The following still require physical-device testing against the user's running Fallout: London game and fresh database captures:

- Actual TCP handshake/data stream on the target game runtime.
- Auto-discovery on iOS, which depends on Apple's multicast entitlement.
- Inventory action acceptance and game-side result reconciliation.
- Quest activation and fast-travel responses in the user's save/runtime.
- Radio station toggling and local-map image appearance.
- London-specific map artwork, quest overlays, and location coverage. The world plot uses coordinates supplied by the running game; it is not a hand-authored geographic basemap, and its completeness depends on the location records exposed by the current runtime.
- Device lifecycle behavior when the app is backgrounded, the game reloads a save, or Wi-Fi changes.

The MAP screen plots live game-provided world coordinates and overlays the player on local-map snapshots using the snapshot's corner coordinates. It does not bundle a hand-authored Fallout: London world-map basemap or Bethesda/Team FOLON map assets; location coverage depends on what the running game exposes.

## Research references

- [PyPipboy](https://github.com/matzman666/PyPipboy) — reference client, discovery, framing, data manager and RPC methods.
- [PyPipboyApp](https://github.com/matzman666/PyPipboyApp) — observed STAT, inventory, quest, radio, and map data paths.
- [Pip-Boy protocol specification](https://github.com/NimVek/pipboy/blob/master/PROTOCOL.md) — channel framing, packet types and RPC identifiers.
- [Pipboy protocol notes](https://github.com/mattbaker/pipboyspec) — discovery and communication write-up.
- [FalloutLondonCompanion](https://github.com/Mdbarnes18/FalloutLondonCompanion) — companion project's Swift protocol/database implementation and feature documentation.

## Technical details

- SwiftUI / MVVM-style observable state.
- iOS 17.0 minimum deployment target.
- Bundle identifier: `com.coagulantchip.attaboy`.
- No cloud relay. Game data is exchanged over the local network.
- No bundled Bethesda/Team FOLON assets, game files, or copyrighted broadcast recordings.

## Build output

The workflow packages `AttaBoy-unsigned.ipa` and uploads it as the `AttaBoy-unsigned-IPA` artifact. The IPA is not considered verified until the macOS build passes and the app has been installed and exercised on a physical device.
