# ASSET CATALOG

185 icons and 45 UI components (all authored as SVG), 9 seamless textures, 11 overlays, 8 backgrounds, 17 sound effects.

Colour tokens (see `SHARED/SOURCE/palette.py`): phosphor `#4CFF7F`, dim phosphor `#2F9E58`, olive `#7A8A3C`, military green `#4B5A32`, charcoal `#23261F`, black `#0B0D0A`, industrial grey `#7B7F73`, aged brass `#B08D3E`, muted amber `#E3A12F` (warnings).

Naming: lowercase snake_case, identical across platforms (`nav_stat`, `med_stimpak`, `panel_clean`). Prefix = family. Scale suffixes follow each platform: iOS `@2x/@3x`, Android density folders, Windows/Linux scale folders.

## Application shell / Navigation (6)

Section navigation (STAT, INV, DATA, MAP, RADIO) and the menu glyph.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `nav_stat` | 24x24 | All | Shared |  |
| `nav_inventory` | 24x24 | All | Shared |  |
| `nav_data` | 24x24 | All | Shared |  |
| `nav_map` | 24x24 | All | Shared |  |
| `nav_radio` | 24x24 | All | Shared |  |
| `nav_menu` | 24x24 | All | Shared |  |

## Connection (8)

Header/status bar connection state and the connect screen (PC / device / signal strength).

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `conn_connected` | 24x24 | Header | Shared |  |
| `conn_connecting` | 24x24 | Header | Shared |  |
| `conn_disconnected` | 24x24 | Header | Shared |  |
| `conn_host_pc` | 24x24 | Connect | Shared |  |
| `conn_device` | 24x24 | Connect | Shared |  |
| `conn_signal_full` | 24x24 | Header | Shared |  |
| `conn_signal_low` | 24x24 | Header | Shared |  |
| `conn_signal_none` | 24x24 | Header | Shared |  |

## Status & diagnostics (10)

Generic status badges (ok, warning, error, info), data-flow and protocol indicators.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `status_ok` | 24x24 | All | Shared |  |
| `status_warning` | 24x24 | All | Shared |  |
| `status_error` | 24x24 | All | Shared |  |
| `status_info` | 24x24 | All | Shared |  |
| `status_unavailable` | 24x24 | DATA | Shared |  |
| `status_busy` | 24x24 | Connect | Shared |  |
| `status_data_received` | 24x24 | DATA | Shared |  |
| `status_data_sent` | 24x24 | DATA | Shared |  |
| `status_protocol` | 24x24 | DATA | Shared |  |
| `status_heartbeat` | 24x24 | Header | Shared |  |

## Controls (19)

Chevrons, expand/collapse, search, filter, settings, copy, save and other small controls.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `ctl_chevron_up` | 24x24 | All | Shared |  |
| `ctl_chevron_down` | 24x24 | All | Shared |  |
| `ctl_chevron_left` | 24x24 | All | Shared |  |
| `ctl_chevron_right` | 24x24 | All | Shared |  |
| `ctl_expand` | 24x24 | DATA | Shared |  |
| `ctl_collapse` | 24x24 | DATA | Shared |  |
| `ctl_close` | 24x24 | All | Shared |  |
| `ctl_check` | 24x24 | All | Shared |  |
| `ctl_plus` | 24x24 | All | Shared |  |
| `ctl_minus` | 24x24 | All | Shared |  |
| `ctl_search` | 24x24 | INV, DATA | Shared |  |
| `ctl_filter` | 24x24 | INV, DATA | Shared |  |
| `ctl_settings` | 24x24 | All | Shared |  |
| `ctl_refresh` | 24x24 | All | Shared |  |
| `ctl_copy` | 24x24 | DATA | Shared |  |
| `ctl_save` | 24x24 | DATA | Shared |  |
| `ctl_more` | 24x24 | All | Shared |  |
| `ctl_back` | 24x24 | All | Shared |  |
| `ctl_sort` | 24x24 | INV | Shared |  |

## Indicators (14)

Selection markers, progress rings (0-100%), loading spinner and status LEDs.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `sel_arrow` | 24x24 | All | Shared |  |
| `sel_bracket` | 24x24 | All | Shared |  |
| `sel_cursor_block` | 24x24 | All | Shared |  |
| `sel_dot` | 24x24 | All | Shared |  |
| `progress_ring_0` | 24x24 | Medical, All | Shared |  |
| `progress_ring_25` | 24x24 | Medical, All | Shared |  |
| `progress_ring_50` | 24x24 | Medical, All | Shared |  |
| `progress_ring_75` | 24x24 | Medical, All | Shared |  |
| `progress_ring_100` | 24x24 | Medical, All | Shared |  |
| `loading_spinner` | 24x24 | All | Shared |  |
| `led_off` | 24x24 | Header | Shared |  |
| `led_green` | 24x24 | Header | Shared |  |
| `led_amber` | 24x24 | Header | Shared |  |
| `led_alert` | 24x24 | Header | Shared |  |

## Inventory actions (5)

Use / Drop / Equip / Favorite actions.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `act_use` | 24x24 | INV | Shared |  |
| `act_drop` | 24x24 | INV | Shared |  |
| `act_equip` | 24x24 | INV | Shared |  |
| `act_favorite` | 24x24 | INV | Shared |  |
| `act_favorite_on` | 24x24 | INV | Shared |  |

## Inventory properties (5)

Weight, value, quantity, condition and equipped markers for item rows.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `inv_weight` | 24x24 | INV | Shared |  |
| `inv_value` | 24x24 | INV | Shared |  |
| `inv_quantity` | 24x24 | INV | Shared |  |
| `inv_condition` | 24x24 | INV | Shared |  |
| `inv_equipped` | 24x24 | INV | Shared |  |

## World & navigation (17)

Local/global map controls, player/quest/custom markers, compass, location browser, workshop and perk glyphs. Interface elements only; no map data.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `map_local` | 24x24 | MAP | Shared |  |
| `map_global` | 24x24 | MAP | Shared |  |
| `map_player` | 24x24 | MAP | Shared |  |
| `map_quest` | 24x24 | MAP | Shared |  |
| `map_custom` | 24x24 | MAP | Shared |  |
| `map_location_browser` | 24x24 | MAP | Shared |  |
| `map_workshop` | 24x24 | MAP | Shared |  |
| `map_quest_indicator` | 24x24 | MAP | Shared |  |
| `map_perk` | 24x24 | STAT | Shared |  |
| `map_select` | 24x24 | MAP | Shared |  |
| `map_zoom_in` | 24x24 | MAP | Shared |  |
| `map_zoom_out` | 24x24 | MAP | Shared |  |
| `map_center` | 24x24 | MAP | Shared |  |
| `map_rotate` | 24x24 | MAP | Shared |  |
| `map_north_up` | 24x24 | MAP | Shared |  |
| `map_layers` | 24x24 | MAP | Shared |  |
| `map_compass` | 48x48 | MAP | Shared |  |

## Radio (4)

Radio screen glyphs (station, tuner, waveform, speaker).

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `radio_station` | 24x24 | RADIO | Shared |  |
| `radio_tuner` | 24x24 | RADIO | Shared |  |
| `radio_wave` | 24x24 | RADIO | Shared |  |
| `radio_speaker` | 24x24 | RADIO | Shared |  |

## Data & diagnostics (8)

Data Browser, Data Update Logger, export/import and tree-hierarchy glyphs.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `data_browser` | 24x24 | DATA | Shared |  |
| `data_logger` | 24x24 | DATA | Shared |  |
| `data_export` | 24x24 | DATA | Shared |  |
| `data_export_file` | 24x24 | DATA | Shared |  |
| `data_import` | 24x24 | DATA | Shared |  |
| `tree_branch` | 24x24 | DATA | Shared |  |
| `tree_node` | 24x24 | DATA | Shared |  |
| `tree_leaf` | 24x24 | DATA | Shared |  |

## Body status (47)

Full-body silhouette and six parts in five states, limb-condition glyphs, health/radiation indicators and injury marker.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `limb_ok` | 24x24 | STAT | Shared |  |
| `limb_wounded` | 24x24 | STAT | Shared |  |
| `limb_damaged` | 24x24 | STAT | Shared |  |
| `limb_critical` | 24x24 | STAT | Shared |  |
| `limb_crippled` | 24x24 | STAT | Shared |  |
| `ind_health_ok` | 24x24 | STAT | Shared |  |
| `ind_health_low` | 24x24 | STAT | Shared |  |
| `ind_health_critical` | 24x24 | STAT | Shared |  |
| `ind_rad_none` | 24x24 | STAT | Shared |  |
| `ind_rad_low` | 24x24 | STAT | Shared |  |
| `ind_rad_high` | 24x24 | STAT | Shared |  |
| `marker_injury` | 24x24 | STAT | Shared |  |
| `body_head_healthy` | 128x128 | STAT | Shared |  |
| `body_head_wounded` | 128x128 | STAT | Shared |  |
| `body_head_damaged` | 128x128 | STAT | Shared |  |
| `body_head_critical` | 128x128 | STAT | Shared |  |
| `body_head_crippled` | 128x128 | STAT | Shared |  |
| `body_torso_healthy` | 128x128 | STAT | Shared |  |
| `body_torso_wounded` | 128x128 | STAT | Shared |  |
| `body_torso_damaged` | 128x128 | STAT | Shared |  |
| `body_torso_critical` | 128x128 | STAT | Shared |  |
| `body_torso_crippled` | 128x128 | STAT | Shared |  |
| `body_arm_left_healthy` | 128x128 | STAT | Shared |  |
| `body_arm_left_wounded` | 128x128 | STAT | Shared |  |
| `body_arm_left_damaged` | 128x128 | STAT | Shared |  |
| `body_arm_left_critical` | 128x128 | STAT | Shared |  |
| `body_arm_left_crippled` | 128x128 | STAT | Shared |  |
| `body_arm_right_healthy` | 128x128 | STAT | Shared |  |
| `body_arm_right_wounded` | 128x128 | STAT | Shared |  |
| `body_arm_right_damaged` | 128x128 | STAT | Shared |  |
| `body_arm_right_critical` | 128x128 | STAT | Shared |  |
| `body_arm_right_crippled` | 128x128 | STAT | Shared |  |
| `body_leg_left_healthy` | 128x128 | STAT | Shared |  |
| `body_leg_left_wounded` | 128x128 | STAT | Shared |  |
| `body_leg_left_damaged` | 128x128 | STAT | Shared |  |
| `body_leg_left_critical` | 128x128 | STAT | Shared |  |
| `body_leg_left_crippled` | 128x128 | STAT | Shared |  |
| `body_leg_right_healthy` | 128x128 | STAT | Shared |  |
| `body_leg_right_wounded` | 128x128 | STAT | Shared |  |
| `body_leg_right_damaged` | 128x128 | STAT | Shared |  |
| `body_leg_right_critical` | 128x128 | STAT | Shared |  |
| `body_leg_right_crippled` | 128x128 | STAT | Shared |  |
| `body_full_healthy` | 128x128 | STAT | Shared |  |
| `body_full_wounded` | 128x128 | STAT | Shared |  |
| `body_full_damaged` | 128x128 | STAT | Shared |  |
| `body_full_critical` | 128x128 | STAT | Shared |  |
| `body_full_crippled` | 128x128 | STAT | Shared |  |

## Player statistics (17)

SPECIAL attributes and player statistics (experience, level, health, AP, radiation, carry weight, effects, game stats, ammo count, equipped weapons).

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `special_strength` | 48x48 | STAT | Shared |  |
| `special_perception` | 48x48 | STAT | Shared |  |
| `special_endurance` | 48x48 | STAT | Shared |  |
| `special_charisma` | 48x48 | STAT | Shared |  |
| `special_intelligence` | 48x48 | STAT | Shared |  |
| `special_agility` | 48x48 | STAT | Shared |  |
| `special_luck` | 48x48 | STAT | Shared |  |
| `stat_experience` | 48x48 | STAT | Shared |  |
| `stat_level` | 48x48 | STAT | Shared |  |
| `stat_health` | 48x48 | STAT | Shared |  |
| `stat_action_points` | 48x48 | STAT | Shared |  |
| `stat_radiation` | 48x48 | STAT | Shared |  |
| `stat_carry_weight` | 48x48 | STAT, INV | Shared |  |
| `stat_active_effects` | 48x48 | STAT | Shared |  |
| `stat_game_stats` | 48x48 | STAT | Shared |  |
| `stat_ammo_count` | 48x48 | STAT, INV | Shared |  |
| `stat_equipped_weapons` | 48x48 | STAT, INV | Shared |  |

## World identity (2)

Two generic world badges (London / Commonwealth).

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `world_london` | 48x48 | Identity | Fallout: London |  |
| `world_commonwealth` | 48x48 | Identity | Fallout 4 Commonwealth |  |

## Inventory categories (11)

Generic category icons (weapons, apparel, armor, aid, food, drink, misc, ammunition, grenades, favorites, equipped). Generic by design; no specific game items.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `cat_weapons` | 128x128 | INV | Shared |  |
| `cat_apparel` | 128x128 | INV | Shared |  |
| `cat_armor` | 128x128 | INV | Shared |  |
| `cat_aid` | 128x128 | INV | Shared |  |
| `cat_food` | 128x128 | INV | Shared |  |
| `cat_drink` | 128x128 | INV | Shared |  |
| `cat_misc` | 128x128 | INV | Shared |  |
| `cat_ammo` | 128x128 | INV | Shared |  |
| `cat_grenades` | 128x128 | INV | Shared |  |
| `cat_favorites` | 128x128 | INV | Shared |  |
| `cat_equipped` | 128x128 | INV | Shared |  |

## Medical systems (12)

AutoDoc, Doctor's Bag, Quick Aid, Stimpak, RadAway, cross, scanner, treatment/healing/progress and warning/critical states.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `med_cross` | 128x128 | STAT, Medical | Shared |  |
| `med_stimpak` | 128x128 | STAT, INV, Medical | Shared |  |
| `med_radaway` | 128x128 | STAT, INV, Medical | Shared |  |
| `med_autodoc` | 128x128 | Medical | Shared |  |
| `med_doctors_bag` | 128x128 | Medical | Shared |  |
| `med_quick_aid` | 128x128 | Medical | Shared |  |
| `med_scanner` | 128x128 | Medical | Shared |  |
| `med_treatment` | 128x128 | Medical | Shared |  |
| `med_healing` | 128x128 | Medical | Shared |  |
| `med_treatment_progress` | 128x128 | Medical | Shared |  |
| `med_warning` | 128x128 | Medical | Shared |  |
| `med_critical_alert` | 128x128 | Medical | Shared |  |

## Panels, frames & dividers (18)

Nine-slice panels, CRT/map frames, dividers, corner ornaments, hazard band and label plate.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `panel_clean` | 128x128 | All | Shared | Clean industrial panel; centre is semi-opaque charcoal. nine-slice (20, 20, 20, 20) |
| `panel_worn` | 128x128 | All | Shared | Worn variant: scuffs, brass edge wear, rivets. nine-slice (20, 20, 20, 20) |
| `panel_inset` | 128x128 | All | Shared | Recessed well for lists and data readouts. nine-slice (16, 16, 16, 16) |
| `panel_warning` | 128x128 | All | Shared | Warning panel with hazard band across the top. nine-slice (20, 26, 20, 20) |
| `panel_notification` | 128x64 | All | Shared | Notification toast; accent bar on the left. nine-slice (22, 16, 12, 12) |
| `frame_screen_clean` | 256x192 | All | Shared | CRT bezel; the inside is fully transparent so screen content shows through. nine-slice (40, 40, 40, 40) |
| `frame_screen_worn` | 256x192 | All | Shared | Worn CRT bezel with rivets and scuffs. nine-slice (40, 40, 40, 40) |
| `frame_map_local` | 256x256 | MAP | Shared | Interface frame only; the app supplies the map image. nine-slice (40, 40, 40, 40) |
| `frame_map_global` | 256x256 | MAP | Shared | Graduated border; carries no coordinates or labels. nine-slice (24, 24, 24, 24) |
| `divider_h` | 128x8 | All | Shared |  nine-slice (12, 0, 12, 0) |
| `divider_v` | 8x128 | All | Shared |  nine-slice (0, 12, 0, 12) |
| `divider_dotted_h` | 128x8 | All | Shared |  |
| `divider_london` | 256x20 | All | Fallout: London | Pointed-arch motif (generic Gothic arch). nine-slice (100, 0, 100, 0) |
| `divider_commonwealth` | 256x20 | All | Fallout 4 Commonwealth | Stepped chevron motif. nine-slice (100, 0, 100, 0) |
| `corner_london` | 64x64 | All | Fallout: London | Top-left corner ornament; rotate 90/180/270 for other corners. |
| `corner_commonwealth` | 64x64 | All | Fallout 4 Commonwealth | Top-left corner ornament; rotate for other corners. |
| `label_plate` | 96x32 | All | Shared | Brass label plate; add text on top. nine-slice (12, 8, 12, 8) |
| `band_hazard` | 64x16 | All | Shared | Tiles horizontally. |

## Buttons & tabs (8)

Button states and tabs (nine-slice).

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `button_normal` | 96x40 | All | Shared |  nine-slice (14, 14, 14, 14) |
| `button_pressed` | 96x40 | All | Shared |  nine-slice (14, 14, 14, 14) |
| `button_selected` | 96x40 | All | Shared | Selected state; use dark text on top. nine-slice (14, 14, 14, 14) |
| `button_disabled` | 96x40 | All | Shared |  nine-slice (14, 14, 14, 14) |
| `button_normal_worn` | 96x40 | All | Shared | Worn variant of button_normal. nine-slice (16, 14, 16, 14) |
| `tab_active` | 96x36 | All | Shared |  nine-slice (14, 12, 14, 0) |
| `tab_inactive` | 96x36 | All | Shared |  nine-slice (14, 12, 14, 0) |
| `selection_highlight` | 96x32 | All | Shared |  nine-slice (12, 10, 12, 10) |

## Toggles & mechanical controls (9)

Toggles, checkboxes, radios, dials and lever switches.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `toggle_off` | 48x24 | Settings | Shared |  |
| `toggle_on` | 48x24 | Settings | Shared |  |
| `checkbox_off` | 24x24 | Settings | Shared |  |
| `checkbox_on` | 24x24 | Settings | Shared |  |
| `radio_off` | 24x24 | Settings | Shared |  |
| `radio_on` | 24x24 | Settings | Shared |  |
| `knob_dial` | 48x48 | All | Shared |  |
| `switch_lever_up` | 24x48 | Settings | Shared |  |
| `switch_lever_down` | 24x48 | Settings | Shared |  |

## Progress & scrollbars (7)

Progress bars and scrollbars (nine-slice).

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `progress_bar_track` | 128x16 | All | Shared |  nine-slice (8, 0, 8, 0) |
| `progress_bar_fill` | 128x16 | All | Shared |  nine-slice (8, 0, 8, 0) |
| `progress_bar_segments` | 128x16 | Medical | Shared |  |
| `scrollbar_track_v` | 12x64 | All | Shared |  nine-slice (0, 6, 0, 6) |
| `scrollbar_thumb_v` | 12x40 | All | Shared |  nine-slice (0, 6, 0, 6) |
| `scrollbar_track_h` | 64x12 | All | Shared |  nine-slice (6, 0, 6, 0) |
| `scrollbar_thumb_h` | 40x12 | All | Shared |  nine-slice (6, 0, 6, 0) |

## Decor (3)

Rivets, screws and badge dot.

| ID | Grid | Screen | World | Notes |
|---|---|---|---|---|
| `rivet_round` | 16x16 | All | Shared |  |
| `screw_slot` | 16x16 | All | Shared |  |
| `badge_dot` | 16x16 | All | Shared |  |

## Seamless textures (512x512, opaque unless `_alpha`)

| ID | Description |
|---|---|
| `tex_metal_brushed_clean` | Clean brushed industrial grey metal. |
| `tex_olive_paint_clean` | Clean olive-drab painted metal. |
| `tex_olive_paint_worn` | Olive paint with chips exposing bare metal and grime. |
| `tex_charcoal_plate` | Scuffed charcoal plate. |
| `tex_perforated_steel` | Perforated steel sheet (speaker / vent grille). |
| `tex_crt_phosphor` | Dark phosphor-green CRT glass base with banding and grain. |
| `tex_hazard_stripes` | Worn amber/black hazard stripes (diagonal). |
| `tex_rust_grime_alpha` | Transparent rust/grime layer to blend over any surface. |
| `tex_scratches_alpha` | Transparent fine-scratch layer. |

Tile with `repeat` wrapping. Android: use the matching `tile_*.xml` bitmap drawable. iOS: draw as a pattern from the 256pt imageset.

## Overlays (1024x1024 RGBA)

| ID | Description |
|---|---|
| `overlay_scanlines_fine` | Fine 4px scanline pattern (stretch or tile vertically). |
| `overlay_scanlines_coarse` | Coarse 8px scanline pattern. |
| `overlay_screen_glow` | Phosphor glow bloom centred on the screen. |
| `overlay_vignette` | Dark CRT edge falloff. |
| `overlay_glass_reflection` | Soft glass highlight, top-left. |
| `overlay_scratches` | Random fine scratches (light and dark). |
| `overlay_grime_edges` | Dirty edges / corner build-up. |
| `overlay_noise_grain` | Sparse static grain. |
| `overlay_crt_distortion_map` | RG displacement map for barrel distortion in a shader (128 = no shift). Opaque data texture. |
| `overlay_reticle_grid` | Generic reticle/graticule grid with centre ticks. Interface element only; contains no map data. |
| `overlay_compass_ring` | Compass bezel ring with degree ticks and a north pointer (no letters). |

Stretch over a panel or screen with normal alpha blending. `overlay_crt_distortion_map` is an opaque data texture for shaders (R/G = x/y offset, 128 = no shift).

## Backgrounds

| ID | Description |
|---|---|
| `bg_terminal_clean_1920x1080` / `bg_terminal_clean_2560x1440` | Clean dark CRT screen with faint phosphor glow, scanlines and vignette. |
| `bg_terminal_worn_1920x1080` / `bg_terminal_worn_2560x1440` | Aged CRT screen with grime at the edges and uneven brightness. |
| `bg_industrial_olive_1920x1080` / `bg_industrial_olive_2560x1440` | Riveted olive-drab panel wall with chipped paint. |
| `bg_terminal_mobile` | Portrait phone background (360x800 dp / 390x844 pt). |
| `bg_industrial_mobile` | Portrait phone background, riveted olive panels. |

## Sound effects (WAV, 48 kHz, 16-bit PCM, mono)

| ID | Group | Description |
|---|---|---|
| `terminal_startup` | Terminal | Power-on: relay clunk, degauss thump, hum swell, data blips and a bell. |
| `terminal_shutdown` | Terminal | Power-off: falling sweep, CRT collapse zap, thunk. |
| `connection_established` | Terminal | Relay click, two rising chirps, soft bell. |
| `connection_lost` | Terminal | Falling chirps with static burst and thunk. |
| `data_received` | Terminal | Tiny tick plus two blips; unobtrusive. |
| `notification` | Terminal | Two-note mechanical bell. |
| `menu_navigate` | Navigation | Very short tick; subtle. |
| `button_confirm` | Navigation | Relay click with rising chirp. |
| `button_cancel` | Navigation | Relay click with falling chirp. |
| `inventory_select` | Navigation | Two-stage mechanical switch clack. |
| `medical_treatment` | Medical | Pneumatic hiss, pressure thump and soft confirmation tones. |
| `autodoc_start` | Medical | Servo spin-up, latch clicks, scanner sweep. |
| `autodoc_complete` | Medical | Servo wind-down then three rising chimes. |
| `medical_warning` | Medical | Three dual-tone pulses. |
| `warning` | System | Two-tone alternating beeps. |
| `error` | System | Low descending double buzzer. |
| `critical_warning` | System | Urgent two-tone alarm with thumps. |

All sounds are synthesized from scratch (oscillators, filtered noise, resonant bells); no samples or recreations of existing game audio. Loudness is normalised to about -19 dBFS RMS over the active part; peaks stay below 0.9 FS.

## Nine-slice guidance

Sliced assets are listed with `(left, top, right, bottom)` insets in logical units. iOS: insets are written into each `Contents.json` (pixels per scale). Android: shipped as `.9.png` (stretch markers only, no padding markers). Windows/Linux: see `nine_slice.json`; multiply the insets by the scale you load.

## Not generated / known limits

- **No game-specific artwork.** No item, creature, faction, location or quest icons, no borough/district marks, no map tiles or labels - the brief forbids inventing or copying them. Category icons are generic.
- **World identity** is limited to two generic glyphs (`world_london`: clock-tower silhouette; `world_commonwealth`: domed hall) and matching dividers/corner ornaments. They are original and generic, not claimed to match anything in either game.
- **Sound effects were verified numerically and by spectrogram, not by ear.** Please audition them; tune `SHARED/SOURCE/audio.py` if any feel wrong.
- **Not opened in Xcode / Android Studio / aapt2.** Contents.json, VectorDrawables and 9-patches are generated to spec and structurally validated, but should be built once on a real project.
- **Loading indicator** is a static arc plus progress rings; animate by rotating it in the app.
- **Colour theme.** Icons ship in phosphor green. The app's current `PipTheme` is amber; iOS monochrome icons are template images (tint freely), Android VectorDrawables can be tinted, desktop PNGs can use a tint colour filter. Re-colouring at source: edit `palette.py` and re-run the build.
- Category icons exist at 128 only; no 24px small variants. No high-contrast / reduced-motion variants.
- The existing application icon and branding are untouched and not part of this pack.
