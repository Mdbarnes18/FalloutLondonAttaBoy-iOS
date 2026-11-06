# Complete asset-pack import and integration

The complete generated pack is committed at `ATTA-Boy-Complete-Asset-Pack/`
(6,345 files; 137,701,487 uncompressed bytes). Preserve this folder as the
unaltered source of truth. Platform runtime resources are copied into their
native project locations; the source archive is not flattened or discarded.

## Integration map

- **iOS:** the supplied asset catalog is integrated under
  `Assets.xcassets/Pack/`. Image-set directory names are prefixed with
  `pack_` to avoid collisions with the approved app icon and existing assets.
  The Xcode project includes the supplied WAV sound effects as bundle resources.
- **Android:** vector drawables and WAV files are integrated under
  `Android/app/src/main/res/drawable` and `res/raw`. `AssetPack.kt` exposes
  namespaced image and audio helpers.
- **Windows and Linux:** SVG artwork and WAV resources are integrated under
  `Desktop/src/main/resources/assets/atta-boy/{windows,linux,audio}`.
  Desktop asset loading selects the matching OS-specific SVG directory.
- **All platforms:** the original generated pack remains available for audit,
  source edits, density variants, and future integrations.

## Import / refresh

For a new checkout or a future replacement of the source archive, run from the
repository root:

```bash
bash scripts/import-complete-asset-pack.sh /path/to/ATTA-Boy-Complete-Asset-Pack.zip
```

The script preserves archive paths, rejects unsafe paths and symlinks, and writes
an `ASSET-MANIFEST.json` with each extracted file's size and SHA-256 checksum.
It refuses to overwrite an existing import unless `--replace` is supplied.

## Integration policy

- Keep the complete original pack intact under `ATTA-Boy-Complete-Asset-Pack/`.
- Bundle only the assets each platform actually uses; do not blindly package the
  entire source archive into every application binary.
- Keep the existing app icon and approved brand identity unchanged.
- Use the supplied platform-specific formats and scale variants where applicable.
- Treat AutoDoc and Doctor's Bag artwork as interface assets only. Do not imply
  that a medical action works unless the game protocol action is implemented,
  verified, and confirmed by a game response.
- Verify all platform builds and inspect the rendered UI before merging the PR.
- Review asset licensing and attribution requirements before public release.

## Verification status

The source pack and native resource copies are present in the development branch.
The latest four-platform GitHub Actions run is currently the build gate for the
latest integration commits. A successful build verifies packaging and compilation,
not visual correctness or live-game protocol behavior. Those still require device
and in-game validation.
