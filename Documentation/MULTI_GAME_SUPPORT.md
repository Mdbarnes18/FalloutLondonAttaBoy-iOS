# Multi-game support

ATTA-Boy keeps its existing visual identity and supports two selectable game profiles:

- **Fallout: London** (FALLOUT_LONDON)
- **Fallout 4 — Commonwealth** (COMMONWEALTH)

The selection is stored locally and controls the map title, map-world profile and whether London-only demo inventory samples are shown. Changing profiles disconnects the current session, clears the in-memory database and local cache, and starts a fresh connection on Android and desktop. On iOS the user can reconnect from Settings.

## Live data contract

Both profiles use the Fallout 4 Pip-Boy companion transport (UDP discovery on 28000, TCP on 27000). The map plot uses map.world.player.x/y and the map.world.locations[] array from the connected game's database. It does not fabricate player coordinates or location markers.

Fallout 4's base-game companion protocol is the documented reference. Fallout: London's data paths and game-specific RPC behavior still require validation against a live London session. The selected profile is a user-selected context; it is not automatic game detection.

## Map presentation and source assets

The map canvas is a coordinate plot of live game-provided world locations and the player position. Local-map pixel packets are decoded by the protocol layer; platform-specific pixel-image rendering remains a separate parity task on Android and desktop.

[Commonwealth Cartography](https://github.com/Mappalachia/Commonwealth_Cartography) is used as a research reference for Fallout 4's Commonwealth map-data workflow, including its background rendering and marker/data extraction documentation. Its repository is GPL-3.0. Its Commonwealth.jpg and marker imagery are game-derived assets; the upstream README describes them as extracted from a purchased copy of Fallout 4 and shared under its author's fair-use position. A repository GPL license is not, by itself, proof that Bethesda's underlying game imagery is freely redistributable. Therefore this app does not copy or bundle those images. No Bethesda map artwork, extracted icon, or third-party map raster is redistributed by this change.

The companion currently renders the same live coordinate-plot experience on iOS, Android, Windows and Linux. A licensed/authorized Commonwealth basemap can be added later without changing the app branding or the live coordinate source.

## Switching behavior

- The default remains Fallout: London for existing installations.
- The selection persists across app restarts.
- Switching profiles clears stale game data so London inventory/locations cannot leak into Commonwealth mode.
- Android and desktop reconnect automatically after a profile change when live mode is enabled.
- iOS exposes Auto Discover and Disconnect in Settings after changing the profile.
- The selected profile does not alter the network protocol or guarantee that a particular Fallout 4 runtime/mod has enabled the companion service.

## Verification checklist

- [ ] Android debug build and unit tests
- [ ] Windows desktop build and unit tests
- [ ] Linux desktop build and unit tests
- [ ] iOS unsigned IPA build and simulator tests
- [ ] Live Fallout 4 session: status, inventory, quests, map coordinates, local-map packet and radio
- [ ] Live Fallout: London session regression
- [ ] Verify no stale cache after switching profiles on each platform
