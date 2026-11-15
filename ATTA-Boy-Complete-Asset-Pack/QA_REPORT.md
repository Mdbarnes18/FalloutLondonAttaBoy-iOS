# QA REPORT

Run on the build directory before packaging (the final archive is re-extracted and re-verified separately; see the delivery message).

```
files: 6343
PASS  no empty files (smallest 60 bytes)
PASS  1156 SVG files well-formed, self-contained, no embedded raster/script/metadata
PASS  269 Contents.json valid (252 imagesets), every referenced file exists
PASS  no AppIcon / existing branding files in the pack
PASS  every asset present for all 4 platforms at every scale (230 assets x 3/5/4/4 scales + vectors)
PASS  exported pixel sizes match logical size x scale for iOS 1x/2x/3x, Android mdpi-xxxhdpi (+2px for 9-patch), Windows/Linux 1x/1.5x/2x/3x
PASS  all icons/UI have transparent backgrounds (corner pixel alpha 0; band_hazard is an intentional opaque tile)
PASS  230 VectorDrawable XML files well-formed
PASS  9-patch files carry stretch markers on top and left borders
PASS  texture dimensions: seamless 512, overlays 1024, backgrounds 1920x1080 / 2560x1440 on SHARED, Windows and Linux
PASS  seamless textures: wrap-around edge difference is no larger than normal neighbouring-pixel difference
PASS  10 alpha overlays contain real transparency
PASS  17 WAV effects x 5 locations: 48 kHz / 16-bit / mono, 0.05-3.0 s, no clipping, no silence
      audio peak range 0.16-0.81 FS; active-RMS range -19.0 to -19.0 dBFS
total size on disk: 136.5 MB
```

Issues: none
