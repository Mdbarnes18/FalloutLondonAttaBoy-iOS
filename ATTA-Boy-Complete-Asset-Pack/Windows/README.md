# Windows package

* `PNG-1x`, `PNG-1.5x`, `PNG-2x`, `PNG-3x` - per-family folders; identical filenames across scales (24 px icon -> 24/36/48/72 px). Pick the folder from the display scale (100/150/200/300 %).
* `TEXTURES/Seamless` (512), `TEXTURES/Overlays` (1024, RGBA), `TEXTURES/Backgrounds` (1920x1080 and 2560x1440).
* `nine_slice.json` - insets in logical px for panels, frames, buttons, tabs, bars and scrollbars (multiply by the scale you load).
* `TrayIcons/*.ico` - notification-area icons (16/24/32/48) for connected, disconnected, connecting, ok, warning, error.
* `AUDIO/` WAV effects, `SVG/` masters. No application `.ico` is provided (the existing icon is untouched).
