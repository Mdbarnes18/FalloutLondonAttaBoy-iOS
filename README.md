# Fallout London Companion

An independent, multi-platform ATTA-Boy-style companion for Fallout 4 / Fallout: London. It connects over a trusted local network to the game's Pip-Boy companion service and presents player status, inventory, data, map and radio interfaces.

This project is not affiliated with, endorsed by, or sponsored by Bethesda or Team FOLON.

## Platforms and deliverables

| Platform | Native implementation | Release package |
|---|---|---|
| iPhone / iPad | SwiftUI | Unsigned IPA |
| Android phone / tablet | Kotlin + Jetpack Compose | APK (debug build) |
| Windows | Kotlin/JVM + Compose Multiplatform | MSI installer and portable EXE |
| Linux | Kotlin/JVM + Compose Multiplatform | AppImage, DEB, RPM and Flatpak |

The iOS implementation is the primary product/protocol reference. Android and desktop are parallel native clients. A successful build does not establish complete feature parity or live-game compatibility; the verification boundaries below are intentional.

## Interface

- **STAT** — HP/AP, radiation, carry weight, level/XP, SPECIAL, limb condition, effects and medical controls where the live database exposes the required data.
- **INV** — inventory categories, search, item detail and supported item metadata/actions.
- **DATA** — quest/objective information and a searchable database browser. iOS supports nested navigation and full TXT/copy export.
- **MAP** — game-provided coordinates, discovered/visible locations and local-map snapshots. A curated Fallout: London world-map basemap is not yet bundled.
- **RADIO** — station state and supported station controls.
- **MEDICAL** — manual Stimpak/RadAway controls and opt-in Auto-Stimpak where verified item references are available.

The game remains authoritative. An action is not successful until the game confirms it or subsequent game data reflects it.

## Connection and protocol

The current target is the **PC Pip-Boy companion service on a private LAN**.

| Service | Port | Purpose |
|---|---:|---|
| UDP | 28000 | PC companion autodiscovery |
| TCP | 27000 | Companion data and command stream |

The documented frame header is five bytes: a little-endian UInt32 payload length followed by a UInt8 message type. The clients handle the established handshake, busy/refusal, heartbeat, data-update, local-map and command-response channels, plus incremental binary database/object-graph updates.

Protocol behavior is based on public community reverse-engineering references, not copied wholesale. The references describe the Fallout 4 companion protocol; Fallout: London-specific paths, IDs, item/quest/radio structures and map geography still require verification against actual London sessions.

**Xbox discovery is not currently supported.** Its separate UDP/5050 discovery format is not sufficiently verified for this project.

See:
- [Protocol contract and verification limits](Documentation/PROTOCOL.md)
- [Reference-source register and audit findings](Documentation/REFERENCE_SOURCES.md)
- [Shared cross-platform contract](Shared/README.md)
- [UI scaffolding checklist](Documentation/SCAFFOLDING_CHECKLIST.md)
- [Asset provenance and usage](Documentation/ASSETS.md)

## Reference sources

These are research references for understanding and cross-checking the public Pip-Boy companion protocol:

1. [PyPipboy](https://github.com/matzman666/PyPipboy) — discovery, TCP framing, handshake, keep-alive, binary updates, local-map packets and RPC transport.
2. [Pipboy specification](https://github.com/mattbaker/pipboyspec) — human-readable discovery, communication, channel and RPC documentation.
3. [pipboylib](https://github.com/RobCoIndustries/pipboylib) — independent JavaScript constants, binary database parsing, map parsing and command IDs.
4. [NimVek/pipboy](https://github.com/NimVek/pipboy) — independent protocol implementation and packet investigation.
5. [MrPippy](https://github.com/ekimekim/mrpippy) — Python encoding/decoding and data-management reference.
6. [PipBoyClient](https://github.com/cpopp/PipBoyClient) — minimal discovery, framing, heartbeat and RPC experiment.
7. [Pipboy Explorations](https://github.com/mattbaker/pipboy-explorations) — earlier protocol exploration.
8. [Pip-Boy Companion App Enabler (AE)](https://www.nexusmods.com/fallout4/mods/108133) — context on companion-service availability in modern Fallout 4 runtimes; not a protocol specification or Fallout: London compatibility guarantee.

The source register records scope, limitations and the local audit conclusions. Upstream projects retain their own licenses. This repository does not import their implementation code wholesale; GPL-licensed code must not be copied here without a deliberate license-compatibility review.

## Build, CI and automatic releases

All development and repository edits are made directly on **`main`**. The four platform workflows run on pushes to `main` and on pull requests targeting `main`:

- **Build Fallout London Companion IPA** — macOS/Xcode simulator tests and unsigned IPA packaging.
- **Build Fallout London Companion Android** — JVM unit tests and debug APK.
- **Build Fallout London Companion Windows** — JVM tests, MSI and portable EXE.
- **Build Fallout London Companion Linux** — JVM tests, DEB, RPM, AppImage and Flatpak.

### Coordinated release gate

A numbered GitHub Release is created automatically after all four platform workflows succeed for the **same main commit**. The release job:

1. Confirms that successful iOS, Android, Windows and Linux build runs exist for the same source SHA.
2. Downloads the eight installable packages.
3. normalizes the asset names to the version in the root `VERSION` file.
4. Generates a SHA-256 checksum file.
5. Publishes one combined release with project-authored notes, package descriptions, installation notes, known limitations and source revision.

No autogenerated contributor roll call is included in release notes. Existing legal notices, upstream licenses and required attributions remain in place.

The release version format is `major.minor` with a two-digit minor component (for example `1.00`, `1.01`, `1.10`). Update `VERSION` on `main` when intentionally preparing the next release. A version already published is never silently overwritten.

### Release package names

For version `X.YY`, the combined release contains:

- `Fallout-London-Companion-X.YY-iOS-unsigned.ipa`
- `Fallout-London-Companion-X.YY-Android.apk`
- `Fallout-London-Companion-X.YY-Windows-Installer.msi`
- `Fallout-London-Companion-X.YY-Windows-Portable.exe`
- `Fallout-London-Companion-X.YY-Linux-x86_64.AppImage`
- `Fallout-London-Companion-X.YY-Linux-amd64.deb`
- `Fallout-London-Companion-X.YY-Linux-x86_64.rpm`
- `Fallout-London-Companion-X.YY-Linux.flatpak`
- `SHA256SUMS-X.YY.txt`

The iOS IPA is unsigned and requires a compatible signing/sideloading workflow. The Android APK is a debug build, not a Play Store production release.

### Installation and network safety

- **iOS / iPadOS:** install the unsigned IPA only after signing it with a compatible workflow such as SideStore. Physical-device testing is required. If UDP broadcast discovery is unavailable, use the gaming PC's private LAN IP for manual connection.
- **Android:** install the debug APK on a device on the same trusted LAN as the game PC.
- **Windows:** use the MSI installer or portable self-extracting EXE.
- **Linux:** install the DEB/RPM, run the AppImage, or install the Flatpak bundle with the appropriate package tooling.

Keep the phone/PC on a trusted private network. Do not expose TCP/27000 or UDP/28000 to the public internet.

## Verification boundary and known gaps

The repository contains unit tests, synthetic protocol fixtures and CI build/package checks. These establish only the behavior those tests exercise. They are **not** a substitute for a real Fallout: London session capture.

Still requiring live-game/device validation:

- physical-device discovery, connect, reconnect and game reload behavior;
- Fallout: London database paths, item IDs, quest structures and radio state;
- item action RPC arguments and result reconciliation;
- quest activation, fast travel, radio and other gameplay commands;
- map marker extraction, coordinate placement and local-map pixel rendering;
- a curated London world-map basemap;
- cross-platform feature parity and platform lifecycle behavior.

The app must not invent London geography or mark an RPC action as supported merely because its numeric command ID appears in a Fallout 4 reference.

## Assets, attribution and legal

The approved project icon is treated as locked artwork. Android and desktop CI retrieve the exact PNG from the original companion repository at pinned commit `b2e544f4279ddfbe3184b573de04b4104906f7f3`. See [ASSETS.md](Documentation/ASSETS.md) for asset provenance and boundaries.

Do not commit Bethesda game assets, decompiled proprietary code, private Team FOLON material, private Discord conversations or permission correspondence. Confirm redistribution rights for each third-party asset before including it.

**WITH THANKS TO TEAM FOLON**

Fallout: London is a Team FOLON project. Fallout, Pip-Boy and related marks and assets belong to their respective owners. This independent companion does not imply endorsement or affiliation.
