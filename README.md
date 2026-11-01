# Fallout London Companion

An independent, multi-platform **ATTA-Boy-style companion app** for Fallout 4 / **Fallout: London**. It connects to your game over your home network and presents your Pip-Boy data on a second screen: status, inventory, quests and data, map, and radio.

> **Not affiliated with, endorsed by, or sponsored by Bethesda or Team FOLON.** See [Legal](#legal-and-attribution).

| | |
|---|---|
| **Platforms** | iPhone / iPad, Android, Windows, Linux |
| **Game** | Fallout 4 / Fallout: London on **PC** (same private network as your device) |
| **Status** | Early release line (**1.00**). Builds target all four platforms; **not yet verified end-to-end against a live Fallout: London session**. See [Status](#status-what-works-and-what-is-unverified). |

## Features

- **STAT** – HP and AP, radiation, carry weight, level and XP, SPECIAL, limb condition, active effects.
- **INV** – inventory by category, search, item details.
- **DATA** – quests and objectives, plus a searchable browser over the raw live database (copy or save as text on iOS).
- **MAP** – game-provided coordinates, discovered locations, local-map snapshots.
- **RADIO** – station list and state.
- **Medical** – manual Stimpak / RadAway buttons and an opt-in **Auto-Stimpak** (see [Safety notes](#safety-notes)).

The game is always the authority. The app only reports an action as done when the game confirms it or the next game update shows it.

## Install

Download the latest package from the [Releases](../../releases) page and verify it against `SHA256SUMS-X.YY.txt`.

| Platform | File | How |
|---|---|---|
| **iPhone / iPad** | `…-iOS-unsigned.ipa` | The IPA is **unsigned**. Sign it with a compatible sideloading tool before installation. Signing requirements and renewal periods depend on the tool and Apple account used. |
| **Android** | `…-Android.apk` | Allow installation from your browser/file manager, then open the APK. This is a **debug build**, not a Play Store release. |
| **Windows** | `…-Windows-Installer.msi` or `…-Windows-Portable.exe` | Run the installer, or run the portable self-extracting EXE directly. |
| **Linux** | `.AppImage`, `.deb`, `.rpm`, `.flatpak` | Make the AppImage executable and run it, or install the package for your distribution. |

## Connect to your game

1. Start Fallout 4 / Fallout: London on your PC and load into the game.
2. Put your phone/PC on the **same private network** as the gaming PC (home Wi-Fi, not a guest network).
3. Open the app and tap **Auto Discover**. If nothing is found, type the gaming PC's local IP address (for example `192.168.1.40`) and tap **Connect**. The last IP you used is remembered on iOS.

Find the PC's IP on Windows with `ipconfig` in a terminal and look for the IPv4 address of your active adapter.

**How discovery works:** the app sends a small UDP request to port **28000**, and the game answers from its own address. The iOS implementation also probes hosts on the local /24 subnet because plain network broadcast is restricted for sideloaded apps.

### Troubleshooting

- **Nothing found / cannot connect.** Check that the game is running and loaded, that both devices are on the same subnet, and that your router isn't isolating Wi-Fi clients ("AP isolation" / "guest network").
- **Windows Firewall.** Allow the game through on **private** networks. The companion service uses **UDP 28000** and **TCP 27000**.
- **iPhone: "Local Network" prompt.** If access was denied, check the app's permission under **Settings → Privacy & Security → Local Network**.
- **Game says it's busy / connection refused.** The Pip-Boy service may already have a companion attached. Close the official app or other companion clients and retry.
- **The companion service doesn't start.** Some modern Fallout 4 runtimes may need a compatible companion-service enabler. See reference 8 in [Reference sources](#reference-sources); this is not a guarantee of Fallout: London compatibility.
- **A different subnet** (for example, PC on Ethernet and phone on an isolated Wi-Fi range) may prevent automatic discovery. Enter the PC's IP manually if routing permits.

## Safety notes

- **Use only on a trusted private network.** The Pip-Boy protocol has **no authentication and no encryption**; anyone who can reach the game on those ports may be able to read its data and send commands. Never expose TCP 27000 or UDP 28000 to the internet (no port-forwarding).
- **Auto-Stimpak** is off by default. The iOS audit implementation includes rate limits, waits for an HP increase before another use, and disables itself after a game-reported error. Confirm the behavior in your build before relying on it.
- **Fast Travel and Radio control** are experimental and disabled by default where implemented, because their command arguments have not been verified against a real Fallout: London session.

## Status: what works and what is unverified

Automated tests and CI cover selected protocol decoder behavior, the object graph, synthetic fixtures, and packaging on the platforms. They **do not replace testing against a real Fallout: London session**. The iOS simulator test step is currently configured as non-blocking in CI; a successful IPA build must not be read as proof that those tests passed.

| Area | State |
|---|---|
| Packet framing, handshake, heartbeat, binary database updates | Implemented and covered by selected unit tests / synthetic fixtures |
| UDP discovery and TCP connect | Implemented; physical-device validation still required |
| STAT / INV / DATA / MAP / RADIO screens | Interface foundations implemented; London-specific paths and IDs unverified |
| Stimpak / RadAway actions | Command support requires live validation of RPC arguments and game responses |
| Fast travel, radio toggle, quest and map-marker commands | **Experimental / unverified** |
| Local-map pixel rendering | Decoder validates dimensions and payload; live packet rendering unverified |
| London world-map basemap | **Not bundled yet** |
| Xbox | **Not supported** |
| Feature parity across platforms | iOS is the reference; Android and desktop do not yet have full parity |

The app does not invent London geography or treat a command as supported just because the same numeric ID exists in a Fallout 4 reference.

**Want to help verify?** A legally obtained capture of a real Fallout: London session (handshake, a few minutes of updates, and a local-map packet) is the single most valuable contribution. Do not include private Team FOLON material or personal data.

## Platform technology

| Platform | UI / language | Package |
|---|---|---|
| iPhone / iPad | SwiftUI | Unsigned IPA |
| Android | Kotlin + Jetpack Compose | APK (debug) |
| Windows | Kotlin/JVM + Compose Multiplatform (Desktop) | MSI and portable EXE |
| Linux | Kotlin/JVM + Compose Multiplatform (Desktop) | AppImage, DEB, RPM, Flatpak |

The iOS app is the protocol reference implementation. Android and desktop currently carry separate copies of the protocol code; keep behavior aligned until they are consolidated into a shared module.

## Protocol

| Service | Port | Purpose |
|---|---:|---|
| UDP | 28000 | PC companion auto-discovery |
| TCP | 27000 | Data and command stream |

Frames use a 5-byte header (little-endian `UInt32` length + `UInt8` type) followed by the payload. See the documents below for details.

- [Protocol contract and verification limits](Documentation/PROTOCOL.md)
- [Reference-source register](Documentation/REFERENCE_SOURCES.md)
- [Shared cross-platform contract](Shared/README.md)
- [UI scaffolding checklist](Documentation/SCAFFOLDING_CHECKLIST.md)
- [Asset provenance](Documentation/ASSETS.md)
- [Release process](Documentation/RELEASING.md)
- [Security policy](SECURITY.md)

### Reference sources

Community reverse-engineering references used for research and cross-checking (not copied wholesale):

1. [PyPipboy](https://github.com/matzman666/PyPipboy)
2. [Pipboy specification](https://github.com/mattbaker/pipboyspec)
3. [pipboylib](https://github.com/RobCoIndustries/pipboylib)
4. [NimVek/pipboy](https://github.com/NimVek/pipboy)
5. [MrPippy](https://github.com/ekimekim/mrpippy)
6. [PipBoyClient](https://github.com/cpopp/PipBoyClient)
7. [Pipboy Explorations](https://github.com/mattbaker/pipboy-explorations)
8. [Pip-Boy Companion App Enabler (AE)](https://www.nexusmods.com/fallout4/mods/108133) – context on companion-service availability in modern Fallout 4 runtimes; not a protocol specification.

These describe the Fallout 4 protocol. Upstream projects keep their own licenses; GPL-licensed code must not be copied here without a deliberate license-compatibility review. See [REFERENCE_SOURCES.md](Documentation/REFERENCE_SOURCES.md) for source scope and audit notes.

## Building from source

CI builds the platform targets on pushes to `main` (see [`.github/workflows`](.github/workflows)). All repository edits are made directly on **`main`**; this project does not use feature branches or pull requests as its development workflow.

- **iOS:** macOS with Xcode and [XcodeGen](https://github.com/yonaskolb/XcodeGen). Run `xcodegen generate`, open `AttaBoy.xcodeproj`, and run the `AttaBoy` scheme. Unit tests: `AttaBoyTests`.
- **Android:** open `Android/` in Android Studio, or run `./gradlew testDebugUnitTest assembleDebug` inside it if the Gradle wrapper is present; CI uses a pinned Gradle installation.
- **Desktop (Windows/Linux):** open `Desktop/` in IntelliJ IDEA, or use the Gradle version configured for CI to run tests and packaging tasks.
- **Protocol fixtures:** `python3 Shared/tools/generate_and_verify_fixtures.py` checks the shared test packets against the fixture verifier.

## Contributing

Bug reports and carefully scoped protocol captures are welcome. Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml) and include your platform, app version, Fallout version and relevant mods. **Do not post** private Team FOLON material, Bethesda assets, private Discord conversations or permission correspondence. Maintainers apply repository changes directly to `main`; CI must pass on all four platform workflows before a coordinated release.

## Legal and attribution

The approved project icon is locked artwork. Android and desktop CI retrieve the exact PNG from the original companion repository at pinned commit `b2e544f4279ddfbe3184b573de04b4104906f7f3`; see [ASSETS.md](Documentation/ASSETS.md).

Do not commit Bethesda game assets, decompiled proprietary code, private Team FOLON material, private Discord conversations or permission correspondence. Confirm redistribution rights for each third-party asset before including it.

**WITH THANKS TO TEAM FOLON**

Fallout: London is a Team FOLON project. Fallout, Pip-Boy and related marks and assets belong to their respective owners. This independent companion does not imply endorsement or affiliation.
