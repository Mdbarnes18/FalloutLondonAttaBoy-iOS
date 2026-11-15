# ATTA-Boy Asset Integration Audit

**Audited revision:** `1334a6df6250ec137878e100e4dca6ed3fa848df`  
**Audit date:** 2026-11-15  
**Source:** `ATTA-Boy-Complete-Asset-Pack/`

## Purpose

The complete asset pack is the visual vocabulary for the companion. It must be visible in the actual application screens so developers and testers can identify the selected control, screen, state, and action while troubleshooting.

The pack is not considered integrated merely because files are checked into the repository. Integration has two distinct gates:

1. **Packaging:** native resources are present in the app bundle for the platform.
2. **Runtime use:** app screens resolve and display the assets in the relevant interaction/state.

## Current evidence

| Platform | Pack resources | Runtime wiring verified in source | CI |
|---|---|---|---|
| iOS | `Assets.xcassets/Pack`, medical, identity, and navigation catalogs | Navigation, world identity, inventory categories, medical actions/references, and limb-condition illustrations | iOS build, asset-reference validation, simulator tests pass on audited PR head |
| Android | 237 native drawable resources and bundled raw audio | Navigation, world identity, medical visuals/actions, limb-condition visuals, and UI sounds | Android unit tests and APK build pass on audited PR head |
| Windows | Platform SVG resources and audio in desktop resources | World identity, medical visuals/actions, limb-condition visuals, and navigation/audio hooks | Desktop tests and Windows MSI/portable packaging pass on audited PR head |
| Linux | Platform SVG resources and audio in desktop resources | Same Compose Desktop implementation as Windows, with Linux resource folder selection | Desktop tests and Linux DEB/RPM/AppImage/Flatpak packaging pass on audited PR head |

## Important visual/debugging gaps

- Several screens still use generic system glyphs or text-only content rather than the pack's dedicated controls and UI components.
- The Android/Desktop map code reports that local-map pixel rendering is not implemented yet; the UI currently indicates the decoder limitation.
- The Android/Desktop medical area explicitly labels AutoDoc and Doctor's Bag as visual references only. Those controls must not be presented as functioning medical systems.
- Asset tinting and palette differ by platform: iOS is currently amber-tinted; Android/Desktop use phosphor green. This is permitted only if it is intentional and consistent with the product design. The asset pack's authored colors should not be silently discarded where the artwork is meant to convey a state.
- CI asset validation must cover Android/Desktop runtime lookups and missing resource IDs, not only successful packaging.

## Acceptance criteria for a complete visual integration

- Every primary tab has recognizable pack navigation artwork.
- Every screen title/header and important panel has a consistent frame/panel/divider treatment.
- All tappable controls have distinct normal, pressed, selected, disabled, and focus/feedback states where the platform supports them.
- Connection status and signal states visibly change with the connection state.
- Inventory category and item actions use their dedicated icon family.
- Body-condition artwork updates from live values, including healthy, wounded, damaged, critical, and crippled states.
- World identity visibly changes when switching between Fallout: London and Fallout 4 / Commonwealth.
- Medical actions distinguish implemented Stimpak/RadAway functionality from AutoDoc/Doctor's Bag visuals that are not yet wired.
- UI sounds are used selectively for navigation, confirmation, cancellation, connection, alerts, and medical feedback. Sound failure must never interrupt a game action.
- Automated checks fail when a UI lookup refers to a missing resource or when a required asset family is absent from a platform build.
- Visual verification captures each platform's screens in demo mode and a connected/live state where a real game session is available.

## Verification boundary

The passing GitHub Actions workflows establish that the configured automated build/test/package steps completed successfully on the audited PR revision. They do not prove visual rendering on a physical device, live-game protocol compatibility, or full feature parity.

The pack's own `QA_REPORT.md` records structural/image/audio validation and explicitly notes that opening catalogs/drawables in Xcode/Android Studio and listening to the sounds were not completed during the pack's original QA. These remain manual review items.
