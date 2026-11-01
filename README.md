# Atta-Boy: London Companion

An independent, Fallout: London-inspired Pip-Boy-style companion for iPhone. This is a fan-made interface project and is not affiliated with or endorsed by Bethesda or Team FOLON.

## Build an unsigned IPA for SideStore

Every push to `main` (and manual workflow run) triggers the macOS build workflow.

1. Open **Actions** in this repository.
2. Select **Build unsigned iOS IPA**.
3. Run the workflow, or wait for a push to `main` to finish.
4. Open the successful run and download the `AttaBoy-unsigned-IPA` artifact.
5. Import the downloaded `.ipa` into SideStore and let SideStore sign it with your Apple ID.

The artifact is an **unsigned, device-installable IPA package**. It is not signed by this project. SideStore performs signing on your device/computer as part of installation.

## Local build (macOS required)

Requirements: Xcode with the iOS 17 SDK, Homebrew, and XcodeGen.

```sh
brew install xcodegen
xcodegen generate
xcodebuild -project AttaBoy.xcodeproj -scheme AttaBoy -sdk iphoneos -configuration Release -derivedDataPath build CODE_SIGNING_ALLOWED=NO build
mkdir -p Payload
cp -R build/Build/Products/Release-iphoneos/AttaBoy.app Payload/
ditto -c -k --sequesterRsrc --keepParent Payload AttaBoy-unsigned.ipa
rm -rf Payload
```

## Features

- Amber monochrome terminal-inspired interface with scanline treatment.
- Status dashboard, SPECIAL attributes, health, action points, and equipment.
- Interactive schematic London district map.
- Inventory browsing and equipment toggles.
- Radio station selector and playback-state controls (station audio is currently a UI simulation; no copyrighted broadcast audio is bundled).
- Quest list with completion tracking.
- Local preferences and quest/equipment state persisted on device.

## Project notes

- Minimum deployment target: iOS 17.0.
- SwiftUI, MVVM-style observable app state.
- Uses mock companion data; it does not connect to a Fallout: London game save.
- No third-party assets, game files, or broadcast recordings are included.
- Bundle identifier: `com.coagulantchip.attaboy` (change it in `project.yml` if desired).

## Build output

The workflow creates `AttaBoy-unsigned.ipa` and uploads it as a GitHub Actions artifact. No Apple signing secrets are required for this unsigned build.


## Live Fallout: London connection

The iOS client now uses the verified transport and binary database implementation from the main Fallout London Companion project:

- UDP broadcast discovery on port 28000 using the `autodiscover` request.
- Direct TCP connection to the game host on port 27000.
- Five-byte little-endian packet framing (UInt32 payload length + message type).
- Heartbeat handling and automatic rediscovery/reconnect.
- Binary value, array, and object update decoding into a navigable game-data tree.
- Live STAT fields mapped from the game database: current HP, current AP, carry weight, and S.P.E.C.I.A.L.
- Inventory tree parsing for item names, counts, categories, weight, and value.
- Manual IP connection is available if UDP discovery is blocked.

### Game-side setup

1. Start Fallout 4 / Fallout: London and load into the game world.
2. Enable **Pip-Boy App** in the game's Gameplay settings (restart the game if the setting was just changed).
3. Allow the game through the computer's firewall for the local network.
4. Put the iPhone/iPad and game PC on the same LAN/Wi-Fi.
5. Open Atta-Boy. It starts autodiscovery automatically; use **AUTO DISCOVER** to retry or enter the PC's LAN IP and tap **CONNECT**.

The iOS app requests local-network access because the companion protocol is LAN-only. The connection is not a cloud service and does not require sending game data to a third party.

### Current live-data boundary

The transport, packet decoder, database graph, STAT values, and inventory parser are connected to the live game stream. The London schematic currently remains a presentation map, and the RADIO / DATA quest screens still contain presentation/demo content; their live game paths and action RPCs are not yet wired into this iOS interface. Item use/equip/drop actions are also not exposed as active controls in this build. These are intentionally not represented as working game actions until their database paths and RPC arguments are verified.
