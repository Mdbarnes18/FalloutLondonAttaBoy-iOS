# PyPipboy Feature-Parity Audit

This is the implementation checklist for bringing ATTA-Boy into functional parity with the original [PyPipboy](https://github.com/matzman666/PyPipboy) protocol library and [PyPipboyApp](https://github.com/matzman666/PyPipboyApp) widget collection.

The source project is GPL-3.0. This project uses it as a behavioral and protocol reference; Bethesda-owned artwork and assets are not copied.

## Reference feature inventory

The original PyPipboyApp README lists the following widgets and application features:

- Data Browser and Data Update Logger
- Player Info and Player Condition / limb damage
- Date / Time
- Global and local maps
- Windows hotkeys
- Equipped weapons and grenades
- Small Player Info
- Active Effects
- Radio
- Location Browser
- Quests, Perks, Workshops, Player Status and Statistics
- Doctor's Bag
- Inventory Browser
- Auto Doc
- Ammo Count
- User POI markers, marker sizing, location notes, collectible tracking, relay mode, import/export

PyPipboy itself provides UDP autodiscovery, connection handling, the decoded object-tree update stream, local-map updates, and RPC commands.

## Current ATTA-Boy audit

Status is based on repository code inspection, not on a claim that the feature has been live-tested against every game/platform.

| Capability | iOS | Android | Windows / Linux | Parity gap |
|---|---|---|---|---|
| Game discovery / connection / decoded data / RPC | Partial | Partial | Partial | Protocol and live game validation required for both supported worlds |
| Inventory categories and item details | Partial | Present | Present | iOS category coverage and item-property parity; verify category mappings |
| Inventory use / drop / favorite actions | Present | Present | Present | Confirm RPC response handling and edge cases live |
| Ammo count / equipped weapons / grenades | Partial | Partial | Partial | Dedicated views and complete data mapping |
| Player status, SPECIAL, XP, perks | Present | Present | Present | Verify all source fields and perk actions |
| Limb condition | Partial | Partial | Partial | Current UI exposes numeric conditions; original also has body/head condition visualization and flags |
| Auto-Stimpak | Partial | Present | Present | Existing threshold behavior is not the full configurable Auto Doc rules engine |
| Auto Doc | Missing | Missing | Missing | Configurable Stimpak, RadAway, Rad-X, Med-X, Addictol policies, inventory limits, active-effect/radiation state, cooldown and safety guards |
| Doctor's Bag / aid browser | Partial | Partial | Partial | Aid inventory exists; dedicated treatment-oriented browser and filters are incomplete |
| Active effects | Partial | Partial | Partial | Full effect/source interpretation and status display parity |
| Data Browser | Added | Present | Present | iOS browser added in this branch; hierarchy/metadata parity and live validation remain |
| Plain-text diagnostic export | Added | Present | Present | iOS file export added in this branch; standardize metadata and verify saved files on all platforms |
| Data Update Logger | Missing | Missing | Missing | Update event history, filters, pause/clear and export |
| Global / local map | Partial | Partial | Partial | Live coordinate plot exists on desktop/mobile; proper map rendering, layers and local-map decoder remain |
| Location Browser / notes / POI / collectibles | Missing | Partial | Partial | Full location list, notes, custom markers, collectible tracking and persistence |
| Quests | Present | Present | Present | Objective/action parity and game-specific schema verification |
| Radio | Partial | Partial | Partial | Live game station/control parity; static UI is not equivalent |
| Workshops | Missing | Partial | Partial | Dedicated settlement/workshop browser and data/actions |
| Date / Time | Partial | Partial | Partial | Live in-game clock/weather/date presentation |
| Windows hotkeys | N/A | N/A | Missing | Windows-only key binding and command mapping |
| Relay mode | Missing | Missing | Missing | Optional multi-instance protocol relay |
| Data import | Missing | Missing | Missing | Original app import capability and format compatibility |

## Implementation order

1. **Diagnostics and data inspection:** complete cross-platform plain-text export, searchable data browser, update logger, stable metadata, and tests using captured protocol fixtures.
2. **Inventory and aid:** normalize all inventory categories and properties, equipped weapons/grenades, ammo, aid filters, item actions, and Doctor's Bag.
3. **Medical automation:** implement Auto Doc as an opt-in rules engine, preserving the original configurable triggers while adding strict live-session, inventory, cooldown, and duplicate-action guards. Keep automatic Rad-X, RadAway, Med-X, and Addictol disabled by default.
4. **Player condition:** expose body/head flags and six limb conditions with a consistent visual layout on every platform.
5. **World systems:** finish map layers/local map decoding, location browser, notes, POI/collectibles, quests, perks and workshops.
6. **Platform features:** Windows hotkeys, relay mode, date/time, import/export compatibility and platform-specific file handling.

## Acceptance criteria

- Each feature is implemented on every applicable platform or explicitly documented as platform-specific.
- No sample/demo data is represented as live game data.
- Every game-changing action is disabled outside a verified live session and only reports success after a confirmed response.
- Auto Doc never repeats an action while a previous use is pending and never uses an item when the inventory count is unknown or below its configured reserve.
- Diagnostic exports contain the complete decoded value tree, useful build/game/session metadata, and no credentials. The UI warns that save-specific player data may be present.
- Unit tests cover parsing, data traversal, export formatting, medical decision rules and RPC argument construction.
- CI is green for iOS, Android, Windows and Linux; live-session validation is separately recorded for Fallout: London and Fallout 4.
