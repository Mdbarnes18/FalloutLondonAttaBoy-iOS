# PyPipboy / PyPipboyApp Feature-Parity Audit

This is the acceptance tracker for functional parity with the upstream
[PyPipboyApp](https://github.com/matzman666/PyPipboyApp) widgets and
[PyPipboy protocol library](https://github.com/matzman666/PyPipboy).

A screen is not considered complete merely because it exists. Each feature must
consume the correct live Pip-Boy data, perform the correct game RPC where
applicable, handle missing/changed data safely, and have platform tests.

## Platform scope

- iOS
- Android
- Windows
- Linux

The target is one coherent feature set across all four platforms. Native UI
patterns are allowed; missing functionality is not.

## Upstream widget inventory

| Upstream widget / subsystem | Current state | Acceptance work |
|---|---|---|
| Data Browser | Partial | Hierarchical node inspection and diagnostic TXT export exist. Verify search, arrays/objects, safe export and parity of navigation on every platform. |
| Data Update Logger | Implemented on parity branch; CI pending | Opt-in event capture, new/update/delete classification, connection events, clear and TXT export. Confirm all four builds/tests before marking complete. |
| Auto Doc | Not implemented | Port the complete policy engine, per-chem enable/threshold/reserve settings, active-effect detection, cooldowns and safe item-use RPC. |
| Doctor's Bag | Not implemented | Aid inventory filters (drugs/food/drink/all/custom), item effect tooltips, custom list persistence, use action and item availability updates. |
| Quick Aid | Partial | Manual Stimpak/RadAway actions exist. Match upstream count/availability behavior and expand only where supported by the game protocol. |
| Inventory Browser | Partial | Categories and basic use/drop/favorite actions exist. Complete sorting, item metadata, stack handling, categories and action feedback. |
| Player Condition | Partial | Six-region condition meters exist. Add upstream BodyFlags/HeadFlags decoding and matching body/head condition artwork/states. |
| Limb Status | Partial | Six limb values are displayed. Validate exact field names, injury flags and crippled state against live game data. |
| Player Info / Small Player Info | Partial | Core status values exist. Complete the upstream fields, display modes and refresh behavior. |
| Player Stats / SPECIAL | Partial | SPECIAL values and some stats exist. Complete stats and widget behavior. |
| Effects | Partial | Active effects can be listed. Complete effect source/type decoding, duration and value display. |
| Game Stats | Not implemented | Implement the upstream game-stat fields and formatting. |
| Ammo Count | Not implemented | Implement current ammo and reserve counts using the live equipped weapon/ammo data. |
| Equipped Items / Grenades | Partial | Some equipped/favorite metadata exists. Complete equipped weapon, armor, grenade and quick-slot behavior. |
| Date / Time | Not implemented | Implement the game-provided date/time display and formatting. |
| Location Browser | Not implemented | Implement live location data, discovery state and selection behavior. |
| Local Map | Partial | Local-map packets are decoded and retained. Implement pixel rendering, coordinate transforms and map overlays on all platforms. |
| Global Map | Partial | Live coordinate plotting exists. Complete map assets, POIs, notes, markers, editing, and location actions. |
| Workshops | Partial / unverified | Data inspection exists. Implement workshop status, resource data and workshop actions. |
| Quests | Partial | Quest data and basic marker actions exist. Complete objective, stage, status and tracking behavior. |
| Perks | Partial | Basic perk data exists. Complete rank, description, SPECIAL requirements and navigation. |
| Radio | Partial | Station data and RPC control exist. Complete state synchronization and platform behavior. |
| Hotkeys / Relay | Not implemented | Implement the upstream hotkey/relay protocol and platform-specific keyboard integration where supported. |

## Cross-platform acceptance gates

- [ ] iOS build and unit tests pass.
- [ ] Android build and unit tests pass.
- [ ] Windows build and tests pass.
- [ ] Linux build and tests pass.
- [ ] Live Fallout: London session verified.
- [ ] Live Fallout 4 Commonwealth session verified.
- [ ] RPC actions checked against the actual game response and resulting database update.
- [ ] Missing, partial, stale and reordered database updates do not crash the app.
- [ ] Demo mode never sends game-changing RPC actions.
- [ ] Diagnostic and update-log exports work on every platform.
- [ ] No placeholder controls or fake live data remain in completed features.

## Asset and package budget

The requested maximum package size is approximately **300 MB**. Treat this as a
ceiling, not a target. Preserve the existing ATTA-Boy artwork and source assets;
do not regenerate branding. Prefer optimized, licensed map data and compressed
platform-appropriate assets. Do not bundle copyrighted game archives or
unlicensed game-derived map assets. Track the installed package size for each
platform independently because store packaging and compression differ.
