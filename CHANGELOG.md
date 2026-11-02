# Changelog

## Unreleased — Commonwealth support

- Add a persistent Fallout: London / Fallout 4 Commonwealth selector to iOS, Android, Windows and Linux without changing ATTA-Boy branding.
- Clear stale live database state on profile changes; Android and desktop reconnect automatically when live mode is active.
- Give Android and desktop the same live world-coordinate map plot and location register as iOS.
- Keep London demo inventory samples out of Commonwealth mode and add Fallout 4-specific sample inventory.
- Add independent per-world demo-mode preferences and per-world cached database snapshots on Android and desktop; add a per-world demo toggle on iOS.
- Document Commonwealth Cartography as a research reference. Its game-derived raster and marker artwork are not redistributed because the upstream GPL license does not establish rights to Bethesda-owned assets.
- Live-game validation and a redistributable offline Commonwealth basemap remain outstanding; see Documentation/MULTI_GAME_SUPPORT.md.

## 1.01 — 2026-11-01

- Align iOS marketing/build metadata, Android version code, and desktop native package metadata with the shared 1.01 release version.
- Keep platform icon builds sourced from the canonical `Assets/AppIcon-Original.png` asset in this repository.
- Remove Android CI's obsolete download from the retired companion repository; Android's existing Gradle icon-copy task now supplies the launcher artwork from the checked-in canonical asset.
- **Fix (Windows and Linux builds):** `Desktop/build.gradle.kts` assigned Gradle's untyped project `version` directly to the native `packageVersion` (a `String`), so the desktop packaging step failed on both platforms. The build now reads `VERSION` as a string and derives numeric `MAJOR.MINOR.PATCH` installer metadata from it (`1.01` becomes `1.1.0`, `1.10` becomes `1.10.0`) and fails with a clear message if `VERSION` is malformed.
- No gameplay, networking, or companion-protocol behavior changes.

Note: Android adaptive foreground/background PNGs supplied separately are not included in this release; the Android launcher still uses the existing square drawable until those binary resources are integrated.
