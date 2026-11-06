# Android package

* `drawable-mdpi ... drawable-xxxhdpi/` - PNG exports (24dp icon = 24/36/48/72/96 px). Sliced UI assets are **9-patch** `.9.png` (reference as `@drawable/panel_clean`).
* `vector-drawable/` - the same icons as `VectorDrawable` XML (round caps/joins, even-odd fills). Copy into `res/drawable` instead of the PNGs when you prefer vectors; tint with `android:tint` / `ImageViewCompat`. They were converted programmatically; open one in Android Studio to confirm.
* `drawable/` - state-list selectors (`selector_button`, `selector_toggle`, `selector_checkbox`, `selector_radio`, `selector_tab`) and tiled bitmaps for the seamless textures (`tile_*.xml`).
* `drawable-nodpi/` - 512 seamless textures and 1024 overlays (not density-scaled). `bg_terminal_mobile` / `bg_industrial_mobile` are in the density folders (360x800 dp).
* `raw/` - WAV sound effects (`R.raw.terminal_startup`, ...).
* `SVG/` - source masters. Adaptive launcher icons are not included (existing branding is untouched).
