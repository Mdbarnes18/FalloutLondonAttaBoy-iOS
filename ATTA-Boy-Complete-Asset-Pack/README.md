# ATTA-Boy Complete Asset Pack

Original, production-ready interface assets and sound effects for **Fallout London ATTA-Boy** (iOS, Android, Windows, Linux). No application source code was changed, and the existing app icon / logo / branding is **not** included or modified.

## What is inside

| Folder | Contents |
|---|---|
| `SHARED/SVG` | 230 editable SVG masters (24 / 48 / 128 grids, plus UI components), grouped by family |
| `SHARED/TEXTURES` | seamless 512 textures, 1024 overlays, 1920x1080 and 2560x1440 backgrounds |
| `SHARED/AUDIO` | 17 WAV effects (48 kHz / 16-bit / mono) |
| `SHARED/SOURCE` | the generator source, palette and nine-slice data (everything is reproducible) |
| `iOS` | `Assets.xcassets` (imagesets + valid `Contents.json`), `PNG-1x/2x/3x`, `SVG`, `Sounds` |
| `Android` | `drawable-mdpi..xxxhdpi` PNG/9-patch, `drawable-nodpi`, `drawable` (selectors, tiled bitmaps), `vector-drawable`, `raw` audio |
| `Windows` | `PNG-1x/1.5x/2x/3x`, `SVG`, `TEXTURES`, `AUDIO`, `TrayIcons` (.ico), `nine_slice.json` |
| `Linux` | `PNG-1x/1.5x/2x/3x`, `SVG`, `TEXTURES`, `AUDIO`, `DesktopResources` (hicolor tray icons), `nine_slice.json` |
| `PREVIEW` | overview, interface, medical, inventory and per-platform previews (built from the exported files) |

Every file in the pack is listed in `ASSET_MANIFEST.csv`. See `ASSET_CATALOG.md` for each asset family and how to use it, and `QA_REPORT.md` for the verification run.

## Design system

Retro-industrial portable computer: phosphor-green CRT ink on charcoal/olive painted metal, aged-brass labels, muted-amber warnings. Monochrome icons use one stroke weight per grid (24: 1.5, 48: 2.5, 128: 5), round caps and joins. Icon and UI exports are rendered natively at every scale from the SVG masters (not enlarged copies); mobile gets phone-sized backgrounds and tiles, desktop gets 1080p/1440p backgrounds.

## Quick start

* **iOS** - merge the groups from `iOS/Assets.xcassets` into your catalog (it contains no AppIcon). Monochrome icons are *template* images: `Image("nav_stat").foregroundStyle(PipTheme.amber)`.
* **Android** - copy the `drawable-*`, `drawable`, `raw` folders (and optionally `vector-drawable/*.xml` into `res/drawable`) into `app/src/main/res`. Use either the PNG or the vector version of an icon, not both.
* **Windows / Linux (Compose Desktop)** - load PNGs from the scale folder that matches the display density; tint monochrome icons with a colour filter if you want the amber theme.

Each platform folder has its own README with details.

## Verification and limits

Structure, sizes, SVG validity, transparency, seamless-texture edges, audio format/clipping and the manifest were checked automatically (`QA_REPORT.md`). **Not done:** opening the catalogs/drawables in Xcode or Android Studio, and listening to the sounds - please do both once. Nothing game-specific (items, factions, locations, map data) was created. Details in `ASSET_CATALOG.md` > "Not generated / known limits".

## Theme note

The app currently renders in **amber** (`PipTheme`); the brief's palette is green. Icons are green by default and designed to be tinted. To rebuild in another colour, change the `C` entry in `SHARED/SOURCE/palette.py` and run the build scripts.

## Licensing / provenance

Everything here was generated procedurally for this project: no third-party, wiki, game or Bethesda assets were copied or traced. Licensing of the pack is the project owner's decision (none is attached). Reference research: the PyPipboyApp feature list (widgets only; its repository ships no graphics), the PyPipboy protocol notes already in the app repository, and public descriptions of Fallout: London (the wiki itself blocked automated access, so only secondary sources were read).
