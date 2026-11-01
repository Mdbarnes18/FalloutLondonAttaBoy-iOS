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
