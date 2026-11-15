# Changelog

## 1.03 — 2026-11-15

- Establish sequential release numbering: each coordinated release advances the shared version by exactly one hundredth (1.03, 1.04, 1.05, and onward); existing release tags are never overwritten.
- Require the release workflow to verify that the candidate version is the immediate successor to the latest published release before packaging or publishing.
- Correct coordinated release workflow filtering so release orchestration follows successful platform builds on the active `dev` branch.
- Make an existing release-tag collision a hard failure instead of reporting a successful workflow without publishing a new release.
- Keep the four platform packages, nine installable formats, checksums, detailed changelog and provenance manifest tied to one source commit.

## 1.02 — 2026-11-15

- Integrate the complete generated ATTA-Boy asset pack as preserved source material, with platform-native resource copies for iOS, Android, Windows and Linux; retain the existing approved app icon and branding.
- Connect generated medical, body-condition, inventory-category and world-identity artwork to the relevant application screens; add interface navigation/button sound effects where supported.
- Add manual game-PC IP connection controls to Android and Windows/Linux desktop as a reliable fallback when UDP discovery is unavailable; retain the existing TCP companion endpoint and demo-mode safety boundary.
- Guard Android and desktop database graph traversal against cyclic object references and cover the behavior with protocol contract tests.
- Default Auto-Stimpak to disabled on Android and Windows/Linux, matching iOS; require users to explicitly opt in before automatic healing can consume inventory.
- Guard decoded database flattening against cyclic/shared node references on iOS, Android and desktop, with regression tests for each implementation.
- Make iOS simulator tests a required CI gate rather than allowing a failed test run to pass the build.
- Generate version-specific release notes directly from this changelog after all four platform workflows succeed for the same dev-branch commit; attach all nine installable packages (including a Windows portable ZIP), the detailed Markdown changelog, SHA-256 checksums and a JSON build-provenance manifest to every coordinated release.
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
