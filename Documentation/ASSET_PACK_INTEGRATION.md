# Complete Asset Pack Integration

The source archive remains preserved at `ATTA-Boy-Complete-Asset-Pack/`. Platform build resources are copied from that immutable source using Git blob references, so the app can consume platform-native formats without deleting or rewriting the source pack.

## iOS

- The 1,003 files in the pack's iOS asset catalog are included under `Assets.xcassets/Pack/`.
- Every imported image-set directory is prefixed with `pack_` to avoid collisions with existing project assets.
- Navigation tabs use the pack's STAT, MAP, INVENTORY, RADIO, DATA, and quest glyphs.
- The body-condition panel selects the matching body-part illustration from the live condition state.
- Medical controls use the imported Stimpak, RadAway, AutoDoc, and Doctor's Bag illustrations.
- The existing application icon and original brand assets are not replaced.

## Android

- All 230 Android vector drawables are included in `Android/app/src/main/res/drawable/` with the `pack_` resource prefix.
- All 17 WAV effects are included in `Android/app/src/main/res/raw/` with the `pack_` resource prefix.
- `AssetPack.kt` provides resource-safe icon lookup and sound playback with MediaPlayer cleanup.
- The navigation row uses the imported glyphs; the body-condition cells resolve the matching injury-state illustration.
- Medical action taps play the bundled confirmation sound. This is interaction feedback, not a claim that the game accepted the action.

## Desktop

- The 47 Linux and 47 Windows body-condition SVGs are installed as namespaced resources in their respective platform resource folders.
- The existing Skia SVG renderer now prefers the imported `pack_` resources and falls back to the original six SVGs.
- The body-condition panel renders the matching illustration for each known body-part state.

## Validation and known boundaries

- GitHub Actions Android and Linux build workflows are triggered by the integration commits. Their results must be checked before calling those targets build-verified.
- iOS asset catalog compilation still requires the macOS workflow result.
- Windows CI is triggered separately; a successful run is required before calling Windows build-verified.
- AutoDoc and Doctor's Bag remain visual references only. Their artwork does not create new game-side functionality.
- Textures, overlays, backgrounds, and the remaining sound effects remain preserved in the source pack; they are not yet enabled as global visual/audio effects.
