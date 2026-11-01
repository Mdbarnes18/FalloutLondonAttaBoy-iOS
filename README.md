# Fallout London Companion

A multi-platform native companion for Fallout 4 / Fallout: London, with an ATTA-Boy interface and a local-network connection to the game's Pip-Boy companion service. This is an independent fan project and is not affiliated with or endorsed by Bethesda or Team FOLON.

## Consolidated project

This repository brings together the current iOS implementation and the Android/desktop implementations from the companion project:

| Platform | Implementation | Build output |
|---|---|---|
| iPhone / iPad | SwiftUI | Unsigned IPA for SideStore |
| Android phone / tablet | Kotlin + Jetpack Compose | APK |
| Windows | Kotlin/JVM + Compose Multiplatform | MSI installer + portable EXE |
| Linux | Kotlin/JVM + Compose Multiplatform | AppImage, Flatpak, DEB, RPM |

The iOS app remains the primary protocol and product reference. Android and desktop are native companion clients ported from the parallel project. The implementations are not yet proven to have complete feature parity; see `Documentation/SCAFFOLDING_CHECKLIST.md` and the per-platform build workflows.

## Core interface

- **STAT** — HP/AP, radiation, carry weight, level/XP, SPECIAL, limb condition and active effects where exposed by the live database.
- **INV** — live inventory categories and item metadata, with platform-specific item presentation.
- **DATA** — quest/objective records and searchable database values; the iOS browser supports nested navigation and full TXT/copy export.
- **MAP** — game-provided player coordinates, discovered/visible locations and local-map snapshots. A curated Fallout: London world-map basemap is still a separate work item.
- **RADIO** — station name/frequency/range/active state and supported station commands.
- **MEDICAL** — manual Stimpak/RadAway actions and opt-in Auto-Stimpak where the verified game data exposes the required item references.

The game remains authoritative. The app sends supported commands and waits for game responses or subsequent data updates; it must not display an unconfirmed action as successful.

## Protocol contract

The clients implement the established Pip-Boy companion protocol:

- UDP discovery: port 28000.
- TCP connection: port 27000.
- Five-byte little-endian frame header: UInt32 payload size + UInt8 channel.
- Data updates, local-map updates, command requests and command responses.
- Incremental binary database/object graph decoding.
- JSON RPC command envelope and capability-gated gameplay actions.

See `Documentation/PROTOCOL.md`, `Documentation/REFERENCE_SOURCES.md` and `Shared/README.md`. Protocol claims are tied to upstream reverse-engineering references; platform-specific networking, lifecycle, UI, audio, haptics and rendering remain native.

## Build and release

Every push or pull request targeting `main` runs the applicable platform workflows:

- `Build Fallout London Companion IPA`
- `Build Fallout London Companion Android`
- `Build Fallout London Companion Windows`
- `Build Fallout London Companion Linux`

The numbered combined release workflow creates a GitHub Release only after successful artifacts exist for all four platform groups.

### iOS / iPadOS

1. Open **Actions** and select **Build Fallout London Companion IPA**.
2. Download the `Fallout-London-Companion-ipa` artifact.
3. Install through SideStore or another supported signing workflow.

The IPA is unsigned. Physical-device testing is still required. Apple's multicast entitlement may be required for UDP broadcast discovery; manual TCP connection by the gaming PC's private LAN IP is the fallback. Keep the game and phone on a trusted private network and do not expose ports 27000/28000 to the public internet.

### Android

The Android workflow builds a debug APK. Install it on a device on the same trusted LAN as the game PC and verify discovery, connection, live data, and command responses.

### Windows and Linux

The desktop workflows package the Compose Multiplatform client. Test networking and package installation on the target operating systems; successful compilation alone does not prove runtime behavior.

## Verification boundary

The implementations provide protocol, data, UI and packaging foundations, but they still require live testing against the target Fallout: London runtime and fresh game captures. In particular:

- physical-device connection and reconnect behavior;
- UDP discovery and manual-IP fallback;
- inventory actions and game-side result reconciliation;
- quest activation, fast travel and radio commands;
- local-map rendering and London location coverage;
- app lifecycle behavior when the game reloads or network changes.

The MAP view plots coordinates exposed by the running game and can display local-map snapshots. It does not currently bundle a hand-authored Fallout: London world map or Bethesda/Team FOLON map artwork.

## Assets and credits

The approved project icon is treated as locked artwork. The Android and desktop CI workflows retrieve the exact source PNG from the original companion repository at a pinned commit; the workflows do not regenerate or recolor it. The SVG artwork and asset provenance are documented in `Documentation/ASSETS.md`.

**WITH THANKS TO TEAM FOLON**

Fallout: London is a Team FOLON project. This companion is a separate application and does not imply endorsement or affiliation.
