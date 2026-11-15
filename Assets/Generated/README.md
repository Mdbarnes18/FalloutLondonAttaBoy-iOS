# Generated ATTA-Boy asset staging

This branch stages the first integration slice from the uploaded `ATTA-Boy-Complete-Asset-Pack.zip`.

## Included in this staging pass

- iOS: Xcode image sets using the original SVG masters for AutoDoc, Doctor's Bag, Stimpak, RadAway, and both world identities.
- Android: native vector drawables for the same six symbols.
- Windows and Linux: separate SVG resource copies under platform-specific resource folders.
- Shared: editable SVG source masters under `Assets/Generated/Shared/SVG`.

The existing AppIcon and established application branding are untouched.

## Color handling

The source artwork uses phosphor green. iOS asset sets are marked as template images so SwiftUI can tint them amber to match `PipTheme`. Android and desktop UI apply their existing phosphor tint at render time.

## Scope

This is an integration slice, not the entire 6,345-file archive. It deliberately starts with the medical controls and world-identity graphics that can be wired into the current Status and shell UI and reviewed before bulk-importing every density export, texture, and sound.

The complete uploaded archive remains the source of the remaining assets. The 300 MB app budget is not treated as a limit; future integration should prioritize fidelity and usefulness, then optimize packaging after platform builds.
