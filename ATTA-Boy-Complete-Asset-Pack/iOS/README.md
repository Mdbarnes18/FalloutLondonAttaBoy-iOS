# iOS package

* `Assets.xcassets/` - one `.imageset` per asset (`name.png`, `name@2x.png`, `name@3x.png`) grouped into folders (Navigation, Connection, Status, Controls, Indicators, Inventory, Categories, World, Radio, Data, Body, Medical, Stats, Identity, UI, Textures). Groups are plain folders (not namespaced), so use the bare asset name: `Image("nav_stat")`. **It contains no AppIcon; nothing here overwrites it.**
* Monochrome icons have `template-rendering-intent: template`; colour icons (warnings, LEDs, body states) are `original`.
* Sliced UI assets carry `resizing` data (9-part / 3-part) per scale. Use `Image("panel_clean").resizable(capInsets: .init(top: 20, leading: 20, bottom: 20, trailing: 20))` or rely on the catalog slicing. **Open the Slicing inspector once in Xcode to confirm the values** (they were generated, not authored in Xcode).
* `PNG-1x/2x/3x/<Group>/` hold flat copies of the icon/UI exports (same files as in the catalog). Textures, overlays and phone backgrounds live only in the catalog (`Textures`).
* `SVG/` - source masters. `Sounds/` - 17 WAV effects; use `AudioServicesCreateSystemSoundID` for the short ones, `AVAudioPlayer` for longer ones.
* Point sizes: 24-grid icons are 24 pt, 48-grid 48 pt, 128-grid 128 pt (1x/2x/3x = 1x/2x/3x pixels).
