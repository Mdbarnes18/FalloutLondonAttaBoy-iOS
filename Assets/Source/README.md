# Complete asset-pack import

The complete source pack is intentionally retained as source material rather than
flattened into one shared runtime folder. It contains platform-specific exports,
density variants, source artwork, textures, audio, and previews that should not
all be copied into every app bundle.

## Import

From the repository root, run:

```bash
bash scripts/import-complete-asset-pack.sh ~/Downloads/ATTA-Boy-Complete-Asset-Pack.zip
```

The script extracts the archive, preserving its internal directory layout, into:

```
Assets/Source/ATTA-Boy-Complete-Asset-Pack/
```

It also creates `ASSET-MANIFEST.json` with each imported path, byte size, and
SHA-256 checksum. It rejects unsafe archive paths and symlinks, and it will not
overwrite an existing import unless explicitly asked:

```bash
bash scripts/import-complete-asset-pack.sh --replace /path/to/ATTA-Boy-Complete-Asset-Pack.zip
```

## Integration policy

- Keep the complete original pack intact under `Assets/Source`.
- Treat `iOS`, `Android`, `Windows`, `Linux`, and `SHARED` exports as source pools.
- Integrate only the appropriate platform assets into runtime resource directories.
- Prefer the platform's supplied density variants and native formats where present.
- Keep original SVG/source artwork and previews available for future edits.
- Do not replace the existing app icon or established app identity as part of a bulk import.
- Do not bundle every source file into every platform binary. The repository can retain
  the full pack while each platform build packages only resources it actually uses.
- Review audio licensing/attribution and confirm formats before wiring sound playback.

## Current status

The first six medical/world identity symbols are already represented in the app's
platform resource trees and UI. This import utility is the reproducible handoff for
bringing the remaining archive contents into the repository without losing source
variants. The archive itself still needs to be extracted and committed from a
machine that has the local ZIP and a Git remote connection; the GitHub connector
used for this session can write repository text and Git objects but cannot stream
a 128 MiB local binary archive into GitHub in one operation.
