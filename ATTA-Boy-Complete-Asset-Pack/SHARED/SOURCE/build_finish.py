import os, sys, json, csv, pickle, time, zipfile, wave, shutil, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import xml.etree.ElementTree as ET
from core import ROOT, P, REG, reg, save_text
from build_assets import IOS, AND, DESK, T, A, TRAY
ZIP_OUT = '/mnt/user-data/outputs/ATTA-Boy-Complete-Asset-Pack.zip'
def count(pred): return sum(1 for r, m in REG.items() if pred(r, m))
USAGE = {
 'Application shell / Navigation': 'Section navigation (STAT, INV, DATA, MAP, RADIO) and the menu glyph.',
 'Connection': 'Header/status bar connection state and the connect screen (PC / device / signal strength).',
 'Status & diagnostics': 'Generic status badges (ok, warning, error, info), data-flow and protocol indicators.',
 'Controls': 'Chevrons, expand/collapse, search, filter, settings, copy, save and other small controls.',
 'Indicators': 'Selection markers, progress rings (0-100%), loading spinner and status LEDs.',
 'Inventory actions': 'Use / Drop / Equip / Favorite actions.',
 'Inventory properties': 'Weight, value, quantity, condition and equipped markers for item rows.',
 'Inventory categories': 'Generic category icons (weapons, apparel, armor, aid, food, drink, misc, ammunition, grenades, favorites, equipped). Generic by design; no specific game items.',
 'World & navigation': 'Local/global map controls, player/quest/custom markers, compass, location browser, workshop and perk glyphs. Interface elements only; no map data.',
 'Radio': 'Radio screen glyphs (station, tuner, waveform, speaker).',
 'Data & diagnostics': 'Data Browser, Data Update Logger, export/import and tree-hierarchy glyphs.',
 'Body status': 'Full-body silhouette and six parts in five states, limb-condition glyphs, health/radiation indicators and injury marker.',
 'Medical systems': 'AutoDoc, Doctor\'s Bag, Quick Aid, Stimpak, RadAway, cross, scanner, treatment/healing/progress and warning/critical states.',
 'Player statistics': 'SPECIAL attributes and player statistics (experience, level, health, AP, radiation, carry weight, effects, game stats, ammo count, equipped weapons).',
 'World identity': 'Two generic world badges (London / Commonwealth).',
 'Panels, frames & dividers': 'Nine-slice panels, CRT/map frames, dividers, corner ornaments, hazard band and label plate.',
 'Buttons & tabs': 'Button states and tabs (nine-slice).',
 'Toggles & mechanical controls': 'Toggles, checkboxes, radios, dials and lever switches.',
 'Progress & scrollbars': 'Progress bars and scrollbars (nine-slice).',
 'Decor': 'Rivets, screws and badge dot.',
}
def write_docs(assets, log):
    n_icon = sum(1 for a in assets if a['kind'] == 'icon'); n_ui = len(assets) - n_icon
    png = lambda plat: count(lambda r, m: m.get('platform') == plat and r.endswith('.png'))
    # ---------------- catalog ----------------
    cat = ['# ASSET CATALOG', '', f'{n_icon} icons and {n_ui} UI components (all authored as SVG), {len(T.SEAMLESS)} seamless textures, {len(T.OVERLAYS)} overlays, {len(T.BACKGROUNDS)*2 + 2} backgrounds, {len(A.SOUNDS)} sound effects.', '',
           'Colour tokens (see `SHARED/SOURCE/palette.py`): phosphor `#4CFF7F`, dim phosphor `#2F9E58`, olive `#7A8A3C`, military green `#4B5A32`, charcoal `#23261F`, black `#0B0D0A`, industrial grey `#7B7F73`, aged brass `#B08D3E`, muted amber `#E3A12F` (warnings).', '',
           'Naming: lowercase snake_case, identical across platforms (`nav_stat`, `med_stimpak`, `panel_clean`). Prefix = family. Scale suffixes follow each platform: iOS `@2x/@3x`, Android density folders, Windows/Linux scale folders.', '']
    by_cat = {}
    for a in assets: by_cat.setdefault(a['category'], []).append(a)
    for c, lst in by_cat.items():
        cat += [f'## {c} ({len(lst)})', '', USAGE.get(c, ''), '', '| ID | Grid | Screen | World | Notes |', '|---|---|---|---|---|']
        for a in lst:
            sl = f' nine-slice {a["slice"]}' if a['slice'] else ''
            cat.append(f'| `{a["id"]}` | {a["w"]}x{a["h"]} | {a["screen"]} | {a["world"]} | {(a.get("note") or "").strip()}{sl} |')
        cat.append('')
    cat += ['## Seamless textures (512x512, opaque unless `_alpha`)', '', '| ID | Description |', '|---|---|']
    cat += [f'| `{i}` | {d} |' for i, f, d in T.SEAMLESS]
    cat += ['', 'Tile with `repeat` wrapping. Android: use the matching `tile_*.xml` bitmap drawable. iOS: draw as a pattern from the 256pt imageset.', '',
            '## Overlays (1024x1024 RGBA)', '', '| ID | Description |', '|---|---|']
    cat += [f'| `{i}` | {d} |' for i, f, d, a in T.OVERLAYS]
    cat += ['', 'Stretch over a panel or screen with normal alpha blending. `overlay_crt_distortion_map` is an opaque data texture for shaders (R/G = x/y offset, 128 = no shift).', '',
            '## Backgrounds', '', '| ID | Description |', '|---|---|']
    cat += [f'| `{i}_1920x1080` / `{i}_2560x1440` | {d} |' for i, f, d in T.BACKGROUNDS]
    cat += ['| `bg_terminal_mobile` | Portrait phone background (360x800 dp / 390x844 pt). |', '| `bg_industrial_mobile` | Portrait phone background, riveted olive panels. |', '',
            '## Sound effects (WAV, 48 kHz, 16-bit PCM, mono)', '', '| ID | Group | Description |', '|---|---|---|']
    cat += [f'| `{n}` | {c} | {d} |' for n, f, c, d in A.SOUNDS]
    cat += ['', 'All sounds are synthesized from scratch (oscillators, filtered noise, resonant bells); no samples or recreations of existing game audio. Loudness is normalised to about -19 dBFS RMS over the active part; peaks stay below 0.9 FS.', '',
            '## Nine-slice guidance', '',
            'Sliced assets are listed with `(left, top, right, bottom)` insets in logical units. iOS: insets are written into each `Contents.json` (pixels per scale). Android: shipped as `.9.png` (stretch markers only, no padding markers). Windows/Linux: see `nine_slice.json`; multiply the insets by the scale you load.', '',
            '## Not generated / known limits', '']
    cat += [
        '- **No game-specific artwork.** No item, creature, faction, location or quest icons, no borough/district marks, no map tiles or labels - the brief forbids inventing or copying them. Category icons are generic.',
        '- **World identity** is limited to two generic glyphs (`world_london`: clock-tower silhouette; `world_commonwealth`: domed hall) and matching dividers/corner ornaments. They are original and generic, not claimed to match anything in either game.',
        '- **Sound effects were verified numerically and by spectrogram, not by ear.** Please audition them; tune `SHARED/SOURCE/audio.py` if any feel wrong.',
        '- **Not opened in Xcode / Android Studio / aapt2.** Contents.json, VectorDrawables and 9-patches are generated to spec and structurally validated, but should be built once on a real project.',
        '- **Loading indicator** is a static arc plus progress rings; animate by rotating it in the app.',
        "- **Colour theme.** Icons ship in phosphor green. The app's current `PipTheme` is amber; iOS monochrome icons are template images (tint freely), Android VectorDrawables can be tinted, desktop PNGs can use a tint colour filter. Re-colouring at source: edit `palette.py` and re-run the build.",
        '- Category icons exist at 128 only; no 24px small variants. No high-contrast / reduced-motion variants.',
        '- The existing application icon and branding are untouched and not part of this pack.', '']
    save_text('ASSET_CATALOG.md', '\n'.join(cat), id='ASSET_CATALOG', category='Documentation', screen='n/a', world='Shared', platform='Shared', logical='n/a', scale='n/a', source='build_finish.py', notes='Catalog')
    # ---------------- root README ----------------
    readme = f"""# ATTA-Boy Complete Asset Pack

Original, production-ready interface assets and sound effects for **Fallout London ATTA-Boy** (iOS, Android, Windows, Linux). No application source code was changed, and the existing app icon / logo / branding is **not** included or modified.

## What is inside

| Folder | Contents |
|---|---|
| `SHARED/SVG` | {len(assets)} editable SVG masters (24 / 48 / 128 grids, plus UI components), grouped by family |
| `SHARED/TEXTURES` | seamless 512 textures, 1024 overlays, 1920x1080 and 2560x1440 backgrounds |
| `SHARED/AUDIO` | {len(A.SOUNDS)} WAV effects (48 kHz / 16-bit / mono) |
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
"""
    save_text('README.md', readme, id='README', category='Documentation', screen='n/a', world='Shared', platform='Shared', logical='n/a', scale='n/a', source='build_finish.py', notes='Pack overview')
    # ---------------- platform READMEs ----------------
    plat = {
'iOS': """# iOS package

* `Assets.xcassets/` - one `.imageset` per asset (`name.png`, `name@2x.png`, `name@3x.png`) grouped into folders (Navigation, Connection, Status, Controls, Indicators, Inventory, Categories, World, Radio, Data, Body, Medical, Stats, Identity, UI, Textures). Groups are plain folders (not namespaced), so use the bare asset name: `Image("nav_stat")`. **It contains no AppIcon; nothing here overwrites it.**
* Monochrome icons have `template-rendering-intent: template`; colour icons (warnings, LEDs, body states) are `original`.
* Sliced UI assets carry `resizing` data (9-part / 3-part) per scale. Use `Image("panel_clean").resizable(capInsets: .init(top: 20, leading: 20, bottom: 20, trailing: 20))` or rely on the catalog slicing. **Open the Slicing inspector once in Xcode to confirm the values** (they were generated, not authored in Xcode).
* `PNG-1x/2x/3x/<Group>/` hold flat copies of the icon/UI exports (same files as in the catalog). Textures, overlays and phone backgrounds live only in the catalog (`Textures`).
* `SVG/` - source masters. `Sounds/` - 17 WAV effects; use `AudioServicesCreateSystemSoundID` for the short ones, `AVAudioPlayer` for longer ones.
* Point sizes: 24-grid icons are 24 pt, 48-grid 48 pt, 128-grid 128 pt (1x/2x/3x = 1x/2x/3x pixels).
""",
'Android': """# Android package

* `drawable-mdpi ... drawable-xxxhdpi/` - PNG exports (24dp icon = 24/36/48/72/96 px). Sliced UI assets are **9-patch** `.9.png` (reference as `@drawable/panel_clean`).
* `vector-drawable/` - the same icons as `VectorDrawable` XML (round caps/joins, even-odd fills). Copy into `res/drawable` instead of the PNGs when you prefer vectors; tint with `android:tint` / `ImageViewCompat`. They were converted programmatically; open one in Android Studio to confirm.
* `drawable/` - state-list selectors (`selector_button`, `selector_toggle`, `selector_checkbox`, `selector_radio`, `selector_tab`) and tiled bitmaps for the seamless textures (`tile_*.xml`).
* `drawable-nodpi/` - 512 seamless textures and 1024 overlays (not density-scaled). `bg_terminal_mobile` / `bg_industrial_mobile` are in the density folders (360x800 dp).
* `raw/` - WAV sound effects (`R.raw.terminal_startup`, ...).
* `SVG/` - source masters. Adaptive launcher icons are not included (existing branding is untouched).
""",
'Windows': """# Windows package

* `PNG-1x`, `PNG-1.5x`, `PNG-2x`, `PNG-3x` - per-family folders; identical filenames across scales (24 px icon -> 24/36/48/72 px). Pick the folder from the display scale (100/150/200/300 %).
* `TEXTURES/Seamless` (512), `TEXTURES/Overlays` (1024, RGBA), `TEXTURES/Backgrounds` (1920x1080 and 2560x1440).
* `nine_slice.json` - insets in logical px for panels, frames, buttons, tabs, bars and scrollbars (multiply by the scale you load).
* `TrayIcons/*.ico` - notification-area icons (16/24/32/48) for connected, disconnected, connecting, ok, warning, error.
* `AUDIO/` WAV effects, `SVG/` masters. No application `.ico` is provided (the existing icon is untouched).
""",
'Linux': """# Linux package

* `PNG-1x`, `PNG-1.5x`, `PNG-2x`, `PNG-3x` - per-family folders (24 px icon -> 24/36/48/72 px).
* `TEXTURES/Seamless`, `TEXTURES/Overlays`, `TEXTURES/Backgrounds` as on Windows; `nine_slice.json` for sliced assets.
* `DesktopResources/icons/hicolor/` - freedesktop status icons for tray/indicator use: scalable `*-symbolic.svg` (recoloured by the toolkit) and PNGs at 16/22/24/32/48. Copy under `/usr/share/icons/hicolor` or bundle with the Flatpak/AppImage.
* `AUDIO/` WAV effects, `SVG/` masters. The application icon is not part of this pack.
"""}
    for p, t in plat.items():
        save_text(f'{p}/README.md', t, id=f'{p}_README', category='Documentation', screen='n/a', world='Shared', platform=p, logical='n/a', scale='n/a', source='build_finish.py', notes='Integration notes')
    # source
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), '*.py'))):
        if os.path.basename(f) in ('review.py', 'run_all.py'): continue
        shutil.copyfile(f, P('SHARED/SOURCE/' + os.path.basename(f))); reg('SHARED/SOURCE/' + os.path.basename(f), id=os.path.basename(f), category='Source', screen='n/a', world='Shared', platform='Shared', logical='n/a', scale='n/a', source='(source)', notes='Generator source')
    save_text('SHARED/SOURCE/README.md', 'Reproduce: `python3 build_assets.py` then `python3 build_finish.py` (needs Python 3, numpy, Pillow). `core.py` has an absolute output path in `ROOT`; change it first. Edit `palette.py` to re-theme, `icons_a.py` / `icons_b.py` / `ui_def.py` for artwork, `textures.py` / `audio.py` for textures and sound.\n', id='SOURCE_README', category='Source', screen='n/a', world='Shared', platform='Shared', logical='n/a', scale='n/a', source='build_finish.py', notes='')
    log('  docs written')
# ---------------------------- QA ----------------------------
def qa(root, assets=None, check_manifest=False):
    R = []; issues = []; ok = lambda s: R.append('PASS  ' + s); bad = lambda s: (issues.append(s), R.append('FAIL  ' + s))
    files = [os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs]
    R.append(f'files: {len(files)}'); sizes = [os.path.getsize(os.path.join(root, f)) for f in files]
    (ok if min(sizes) > 0 else bad)(f'no empty files (smallest {min(sizes)} bytes)')
    # svg
    svgs = [f for f in files if f.endswith('.svg')]; badsvg = []
    for f in svgs:
        s = open(os.path.join(root, f), encoding='utf-8').read()
        try: ET.fromstring(s)
        except Exception as e: badsvg.append((f, 'xml')); continue
        if re.search(r'<image|<script|href=|xlink|<metadata|<style|url\(', s): badsvg.append((f, 'forbidden'))
        if 'viewBox' not in s: badsvg.append((f, 'viewBox'))
    (ok if not badsvg else bad)(f'{len(svgs)} SVG files well-formed, self-contained, no embedded raster/script/metadata' + (f' - problems: {badsvg[:3]}' if badsvg else ''))
    # ios
    cj = [f for f in files if f.endswith('Contents.json')]; badc = []; n_sets = 0
    for f in cj:
        try: d = json.load(open(os.path.join(root, f)))
        except Exception: badc.append(f); continue
        for im in d.get('images', []):
            if not os.path.exists(os.path.join(root, os.path.dirname(f), im['filename'])): badc.append((f, im['filename']))
        if f.endswith('.imageset/Contents.json'): n_sets += 1
    (ok if not badc else bad)(f'{len(cj)} Contents.json valid ({n_sets} imagesets), every referenced file exists' + (f' - {badc[:3]}' if badc else ''))
    if any('AppIcon' in f for f in files): bad('pack contains an AppIcon')
    else: ok('no AppIcon / existing branding files in the pack')
    if assets:
        wrong = []; missing = []
        for a in assets:
            g, i, w, h = a['group'], a['id'], a['w'], a['h']; ext = '9.png' if a['slice'] else 'png'
            for s, f, d in IOS:
                fn = f'{i}.png' if s == '1x' else f'{i}@{s}.png'
                for rel in (f'iOS/{d}/{g}/{fn}', f'iOS/Assets.xcassets/{g}/{i}.imageset/{fn}'):
                    if not os.path.exists(os.path.join(root, rel)): missing.append(rel)
                    elif Image.open(os.path.join(root, rel)).size != (int(w*f+.5), int(h*f+.5)): wrong.append(rel)
            for dn, f, d in AND:
                rel = f'Android/{d}/{i}.{ext}'
                if not os.path.exists(os.path.join(root, rel)): missing.append(rel)
                else:
                    sz = Image.open(os.path.join(root, rel)).size; exp = (int(w*f+.5) + (2 if a['slice'] else 0), int(h*f+.5) + (2 if a['slice'] else 0))
                    if sz != exp: wrong.append(rel)
            for plat in ('Windows', 'Linux'):
                for s, f, d in DESK:
                    rel = f'{plat}/{d}/{g}/{i}.png'
                    if not os.path.exists(os.path.join(root, rel)): missing.append(rel)
                    elif Image.open(os.path.join(root, rel)).size != (int(w*f+.5), int(h*f+.5)): wrong.append(rel)
            if not os.path.exists(os.path.join(root, f'Android/vector-drawable/{i}.xml')): missing.append(f'vector {i}')
        (ok if not missing else bad)(f'every asset present for all 4 platforms at every scale ({len(assets)} assets x 3/5/4/4 scales + vectors)' + (f' - missing {missing[:3]}' if missing else ''))
        (ok if not wrong else bad)('exported pixel sizes match logical size x scale for iOS 1x/2x/3x, Android mdpi-xxxhdpi (+2px for 9-patch), Windows/Linux 1x/1.5x/2x/3x' + (f' - wrong {wrong[:3]}' if wrong else ''))
        # transparency
        opaque = []; allow = {'band_hazard'}
        for a in assets:
            im = Image.open(os.path.join(root, f'Windows/PNG-1x/{a["group"]}/{a["id"]}.png')).convert('RGBA'); w, h = im.size
            if a['id'] in allow: continue
            if im.getchannel('A').getextrema()[0] != 0 or im.getpixel((0, 0))[3] > 8:
                opaque.append(a['id'])
        (ok if not opaque else bad)('all icons/UI have transparent backgrounds (corner pixel alpha 0; band_hazard is an intentional opaque tile)' + (f' - check {opaque[:5]}' if opaque else ''))
        # vector validity
        badv = []
        for a in assets:
            try: ET.fromstring(open(os.path.join(root, f'Android/vector-drawable/{a["id"]}.xml'), encoding='utf-8').read())
            except Exception: badv.append(a['id'])
        (ok if not badv else bad)(f'{len(assets)} VectorDrawable XML files well-formed')
        # 9-patch borders
        bp = []
        for a in assets:
            if a['slice']:
                im = Image.open(os.path.join(root, f'Android/drawable-xhdpi/{a["id"]}.9.png')).convert('RGBA')
                top = [im.getpixel((x, 0)) for x in range(im.width)]; left = [im.getpixel((0, y)) for y in range(im.height)]
                if not any(p == (0, 0, 0, 255) for p in top) or not any(p == (0, 0, 0, 255) for p in left): bp.append(a['id'])
        (ok if not bp else bad)('9-patch files carry stretch markers on top and left borders' + (f' - {bp}' if bp else ''))
    # textures
    tex = []
    for i, f, d in T.SEAMLESS:
        for plat in ('SHARED', 'Windows', 'Linux'):
            if Image.open(os.path.join(root, f'{plat}/TEXTURES/Seamless/{i}.png')).size != (512, 512): tex.append((plat, i))
    for i, f, d, a in T.OVERLAYS:
        for plat in ('SHARED', 'Windows', 'Linux'):
            if Image.open(os.path.join(root, f'{plat}/TEXTURES/Overlays/{i}.png')).size != (1024, 1024): tex.append((plat, i))
    for i, f, d in T.BACKGROUNDS:
        for plat in ('SHARED', 'Windows', 'Linux'):
            for w, h in ((1920, 1080), (2560, 1440)):
                if Image.open(os.path.join(root, f'{plat}/TEXTURES/Backgrounds/{i}_{w}x{h}.png')).size != (w, h): tex.append((plat, i, w))
    (ok if not tex else bad)('texture dimensions: seamless 512, overlays 1024, backgrounds 1920x1080 / 2560x1440 on SHARED, Windows and Linux' + (f' - {tex[:3]}' if tex else ''))
    seam = []
    for i, f, d in T.SEAMLESS:
        a = np.asarray(Image.open(os.path.join(root, f'SHARED/TEXTURES/Seamless/{i}.png')).convert('RGBA'), dtype=np.float32)
        # seam continuity: edge-to-edge difference vs typical adjacent-pixel difference
        e = np.abs(a[:, 0, :3] - a[:, -1, :3]).mean() + np.abs(a[0, :, :3] - a[-1, :, :3]).mean(); inner = np.abs(a[:, 1:, :3] - a[:, :-1, :3]).mean() + np.abs(a[1:, :, :3] - a[:-1, :, :3]).mean()
        if e > inner*1.6 + 1.0: seam.append((i, round(float(e), 2), round(float(inner), 2)))
    (ok if not seam else bad)('seamless textures: wrap-around edge difference is no larger than normal neighbouring-pixel difference' + (f' - {seam}' if seam else ''))
    alpha_ok = [i for i, f, d, a in T.OVERLAYS if a and Image.open(os.path.join(root, f'SHARED/TEXTURES/Overlays/{i}.png')).convert('RGBA').getchannel('A').getextrema()[0] == 0]
    (ok if len(alpha_ok) == sum(1 for o in T.OVERLAYS if o[3]) else bad)(f'{len(alpha_ok)} alpha overlays contain real transparency')
    # audio
    aud = []; peaks = []; rmss = []
    for n, f, c, d in A.SOUNDS:
        for rel in (f'SHARED/AUDIO/{n}.wav', f'iOS/Sounds/{n}.wav', f'Android/raw/{n}.wav', f'Windows/AUDIO/{n}.wav', f'Linux/AUDIO/{n}.wav'):
            with wave.open(os.path.join(root, rel)) as w:
                if (w.getframerate(), w.getsampwidth(), w.getnchannels()) != (48000, 2, 1): aud.append((rel, 'format'))
                dur = w.getnframes()/w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32)/32768
            if not (0.05 <= dur <= 3.0): aud.append((rel, f'duration {dur:.2f}'))
            if np.abs(x).max() >= 0.99: aud.append((rel, 'clipping'))
            if np.sqrt(np.mean(x**2)) < 0.01: aud.append((rel, 'near silent'))
            if rel.startswith('SHARED'):
                act = np.abs(x) > 0.05*np.abs(x).max(); peaks.append(np.abs(x).max()); rmss.append(20*np.log10(np.sqrt(np.mean(x[act]**2))))
    (ok if not aud else bad)(f'{len(A.SOUNDS)} WAV effects x 5 locations: 48 kHz / 16-bit / mono, 0.05-3.0 s, no clipping, no silence' + (f' - {aud[:3]}' if aud else ''))
    R.append(f'      audio peak range {min(peaks):.2f}-{max(peaks):.2f} FS; active-RMS range {min(rmss):.1f} to {max(rmss):.1f} dBFS')
    if check_manifest:
        rows = list(csv.DictReader(open(os.path.join(root, 'ASSET_MANIFEST.csv'), encoding='utf-8')))
        listed = {r['Filename'] for r in rows}; actual = {f.replace(os.sep, '/') for f in files if f != 'ASSET_MANIFEST.csv'}
        m1, m2 = sorted(actual - listed), sorted(listed - actual)
        (ok if not (m1 or m2) else bad)(f'manifest lists exactly the {len(actual)} files on disk (rows: {len(rows)})' + (f' - unlisted {m1[:3]}, ghost {m2[:3]}' if (m1 or m2) else ''))
    total = sum(sizes)
    R.append(f'total size on disk: {total/1e6:.1f} MB')
    return R, issues
def write_manifest():
    cols = ['Asset ID', 'Filename', 'Category', 'Intended Screen', 'Game World', 'Platform', 'Pixel Dimensions', 'Logical Dimensions', 'Scale', 'Format', 'Transparency', 'File Size', 'Source Master', 'Notes']
    rows = []
    files = sorted(os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, '/') for d, _, fs in os.walk(ROOT) for f in fs)
    for rel in files:
        if rel == 'ASSET_MANIFEST.csv': continue
        m = REG.get(rel); full = os.path.join(ROOT, rel); ext = rel.rsplit('.', 1)[-1].lower()
        if m is None: raise SystemExit('unregistered file: ' + rel)
        pxd = trans = ''
        if ext == 'png':
            im = Image.open(full); pxd = f'{im.width}x{im.height}'
            if im.mode in ('RGBA', 'LA', 'P'):
                a = im.convert('RGBA').getchannel('A').getextrema(); trans = 'Yes (alpha used)' if a[0] < 255 else 'RGBA (fully opaque)'
            else: trans = 'No (opaque)'
        elif ext == 'ico': trans = 'Yes (alpha)'
        elif ext == 'svg': trans = 'Yes (no background)'; pxd = 'vector'
        elif ext == 'xml' and '/vector-drawable/' in rel: trans = 'Yes (no background)'; pxd = 'vector'
        elif ext == 'wav':
            with wave.open(full) as w: pxd = f'{w.getnframes()} samples @ {w.getframerate()} Hz'
            trans = 'n/a'
        else: trans = 'n/a'
        fmt_ = {'png': '9-patch PNG' if rel.endswith('.9.png') else 'PNG', 'svg': 'SVG', 'xml': 'Android XML', 'json': 'JSON', 'wav': 'WAV 48kHz 16-bit mono', 'ico': 'ICO', 'md': 'Markdown', 'py': 'Python source'}.get(ext, ext.upper())
        rows.append([m.get('id', ''), rel, m.get('category', ''), m.get('screen', ''), m.get('world', ''), m.get('platform', ''), pxd, m.get('logical', ''), m.get('scale', ''), fmt_, trans, os.path.getsize(full), m.get('source', ''), m.get('notes', '')])
    with open(os.path.join(ROOT, 'ASSET_MANIFEST.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f); w.writerow(cols); w.writerows(rows)
    return len(rows)
def make_zip():
    if os.path.exists(ZIP_OUT): os.remove(ZIP_OUT)
    base = os.path.dirname(ROOT)
    with zipfile.ZipFile(ZIP_OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for d, _, fs in sorted(os.walk(ROOT)):
            for f in sorted(fs): z.write(os.path.join(d, f), os.path.relpath(os.path.join(d, f), base))
    return os.path.getsize(ZIP_OUT)
def run(log=print):
    from build_docs import previews
    assets = pickle.load(open('/tmp/assets.pkl', 'rb')); [REG.update(json.load(open(p))) for p in sorted(glob.glob('/tmp/reg_*.json'))]
    previews(assets, log); write_docs(assets, log)
    R, issues = qa(ROOT, assets)
    qa_text = '# QA REPORT\n\nRun on the build directory before packaging (the final archive is re-extracted and re-verified separately; see the delivery message).\n\n```\n' + '\n'.join(R) + '\n```\n\nIssues: ' + (str(len(issues)) if issues else 'none') + '\n'
    save_text('QA_REPORT.md', qa_text, id='QA_REPORT', category='Documentation', screen='n/a', world='Shared', platform='Shared', logical='n/a', scale='n/a', source='build_finish.py', notes='Verification log')
    for pth in glob.glob(os.path.join(ROOT, 'PREVIEW', '**', '*.png'), recursive=True):
        rel = os.path.relpath(pth, ROOT).replace(os.sep, '/')
        assert rel in REG, rel
    n = write_manifest(); R2, issues2 = qa(ROOT, assets, check_manifest=True)
    log('\n'.join(R2)); log(f'manifest rows {n}')
    if issues2: log('ISSUES: ' + str(issues2)); return
    log(f'zip {make_zip()/1e6:.1f} MB')
if __name__ == '__main__': run()
