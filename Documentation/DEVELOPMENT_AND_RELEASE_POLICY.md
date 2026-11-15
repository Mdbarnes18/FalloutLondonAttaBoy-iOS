# ATTA-Boy Development and Release Policy

**Effective:** 2026-11-15

## Project objective

Deliver the most intuitive, reliable Fallout: London / Fallout 4 companion experience across iOS, Android, Windows, and Linux. iOS is the behavioral reference where platform-native conventions differ, but feature scope and status must be documented consistently on every platform.

## Definition of a complete build

A build is complete only when all of the following are true:

1. The same source commit and shared application version are used by all four platform builds.
2. iOS simulator tests and the required protocol/fixture checks pass.
3. Android unit tests and packaging pass.
4. Windows tests and installer/portable packaging pass.
5. Linux tests and DEB/RPM/AppImage/Flatpak packaging pass.
6. Required assets are present in the built platform packages and resource lookups are validated.
7. The release is published with all nine installable packages, SHA-256 checksums, a detailed versioned changelog, and a build-provenance JSON manifest.
8. Release notes clearly identify unsigned/debug packages and disclose live-game verification limitations.

A partial platform build is a CI artifact, not a complete coordinated release.

## Release attachments

Every complete release must include:

- iOS unsigned IPA
- Android APK
- Windows MSI installer
- Windows portable EXE\n- Windows portable ZIP archive
- Linux AppImage
- Linux DEB
- Linux RPM
- Linux Flatpak
- SHA256SUMS text file
- Versioned Markdown changelog with direct download links and detailed changes
- JSON build manifest containing source commit, platform workflow run IDs, package sizes, and SHA-256 digests

Do not overwrite an existing release tag. If the release pipeline detects a version/tag collision, stop and require a new version.

## Visual integration standard

Assets must be used by visible application UI, not merely copied into repositories or build bundles. Each screen should communicate its function and each interactive control should communicate its state. Verify normal, selected, pressed/active, disabled, warning, and error states where applicable.

Keep the supplied original app icon and established ATTA-Boy branding unchanged.

## Safety and honesty

- Demo/cached data must be clearly marked and must not issue live-game commands.
- A command is not successful until the game confirms it or a subsequent database update demonstrates the expected change.
- Keep unverified commands experimental and disabled by default.
- Visual-reference artwork must be labelled as such while its underlying feature is not implemented.
- Do not describe passing CI as proof of live-game compatibility or full feature parity.

## Branch and review discipline

- `dev` is the active development and coordinated-release branch; all four platform workflows and release automation run from `dev`.\n- Keep `main` stable; promote tested, release-ready `dev` work to `main` only through an intentional integration/release step.\n- Integrate substantial work through a focused pull request targeting `dev`.
- Preserve source asset packs and their manifest/provenance.
- Keep broad cross-platform changes reviewable and avoid direct-to-main changes.
- Do not merge a draft PR or declare a complete build until the acceptance gates above are satisfied.
