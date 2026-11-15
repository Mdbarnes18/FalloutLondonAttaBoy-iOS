from geo import *
# Each entry: (id, body, color_token, screen)  -- 24x24 grid, stroke 1.5, round caps/joins.
TRAY = '<path d="M4 15v3.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V15"/>'
ARCS3 = '<path d="M4.5 9.2a11 11 0 0 1 15 0"/><path d="M7.5 12.6a6.8 6.8 0 0 1 9 0"/><path d="M10.4 15.9a2.8 2.8 0 0 1 3.2 0"/>'
def arcs(n):  # n bright arcs (1..3), others dim
    parts = ['<path d="M10.4 15.9a2.8 2.8 0 0 1 3.2 0"/>', '<path d="M7.5 12.6a6.8 6.8 0 0 1 9 0"/>', '<path d="M4.5 9.2a11 11 0 0 1 15 0"/>']
    return ''.join(p if i < n else p.replace('/>', ' stroke-opacity="0.3"/>') for i, p in enumerate(parts))
DOT = '<circle cx="12" cy="19.2" r="1.1" fill="@C"/>'
LIMB = '<rect x="7.5" y="3" width="9" height="18" rx="4.5"/>'
BRK = 'M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5'
I24 = [
 # ---- navigation ----
 ('nav_stat', '<circle cx="12" cy="7.5" r="3.5"/><path d="M5 20.5c0-4.2 3-7 7-7s7 2.8 7 7"/>', 'C', 'All'),
 ('nav_inventory', '<path d="M5 9h14a1.5 1.5 0 0 1 1.5 1.5V19a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 19v-8.5A1.5 1.5 0 0 1 5 9z"/><path d="M8.5 9V7a3.5 3.5 0 0 1 7 0v2"/><path d="M3.5 14h17M10.5 14v2h3v-2"/>', 'C', 'All'),
 ('nav_data', '<rect x="5" y="3.5" width="14" height="17" rx="2"/><path d="M9 8.5h6M9 12h6M9 15.5h3.5"/>', 'C', 'All'),
 ('nav_map', '<path d="M3.5 6.5l5.5-2.5 6 2.5 5.5-2.5v13.5l-5.5 2.5-6-2.5-5.5 2.5z"/><path d="M9 4v13.5M15 6.5V20"/>', 'C', 'All'),
 ('nav_radio', '<rect x="3" y="9" width="18" height="11" rx="2"/><path d="M7 9l9.5-5.5"/><circle cx="8.5" cy="14.5" r="2.5"/><path d="M14 13h4.5M14 16.5h4.5"/>', 'C', 'All'),
 ('nav_menu', '<path d="M4 7h16M4 12h16M4 17h16"/>', 'C', 'All'),
 # ---- connection ----
 ('conn_connected', ARCS3 + DOT, 'C', 'Header'),
 ('conn_connecting', arcs(2) + DOT, 'C', 'Header'),
 ('conn_disconnected', arcs(0).replace('<path', '<path', 1) + '<circle cx="12" cy="19.2" r="1.1" fill="@C" fill-opacity="0.3"/><path d="M4 4l16 16"/>', 'C', 'Header'),
 ('conn_host_pc', '<rect x="3" y="4.5" width="18" height="12" rx="1.5"/><path d="M9 20h6M12 16.5V20"/>', 'C', 'Connect'),
 ('conn_device', '<rect x="7" y="3" width="10" height="18" rx="2"/><path d="M10.5 18h3"/>', 'C', 'Connect'),
 ('conn_signal_full', '<path d="M5 19v-3M10 19v-6M15 19V9.5M20 19V5" stroke-width="2.2"/>', 'C', 'Header'),
 ('conn_signal_low', '<path d="M5 19v-3M10 19v-6" stroke-width="2.2"/><path d="M15 19V9.5M20 19V5" stroke-width="2.2" stroke-opacity="0.3"/>', 'C', 'Header'),
 ('conn_signal_none', '<path d="M5 19v-3M10 19v-6M15 19V9.5M20 19V5" stroke-width="2.2" stroke-opacity="0.3"/>', 'C', 'Header'),
 # ---- status ----
 ('status_ok', '<circle cx="12" cy="12" r="9"/><path d="M7.5 12.5l3 3 6-6.5"/>', 'C', 'All'),
 ('status_warning', '<path d="M12 3.5l9.5 16.5h-19z"/><path d="M12 10v4.5M12 17.4v.1"/>', 'A', 'All'),
 ('status_error', '<path d="M8.5 3h7L21 8.5v7L15.5 21h-7L3 15.5v-7z"/><path d="M9 9l6 6M15 9l-6 6"/>', 'A', 'All'),
 ('status_info', '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.6v.1"/>', 'C', 'All'),
 ('status_unavailable', f'<path d="{dashed_circle(12, 12, 9, 10)}"/><path d="M8.5 12h7"/>', 'G', 'DATA'),
 ('status_busy', '<path d="M6.5 3.5h11M6.5 20.5h11M7.5 3.5c0 5 3 6 4.5 8.5-1.5 2.5-4.5 3.5-4.5 8.5M16.5 3.5c0 5-3 6-4.5 8.5 1.5 2.5 4.5 3.5 4.5 8.5"/>', 'C', 'Connect'),
 ('status_data_received', '<path d="M12 3.5v11M7.5 10.5l4.5 4.5 4.5-4.5"/>' + TRAY, 'C', 'DATA'),
 ('status_data_sent', '<path d="M12 15V4M7.5 8.5L12 4l4.5 4.5"/>' + TRAY, 'C', 'DATA'),
 ('status_protocol', '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5"/><path d="M13.5 5.5l-3 13"/>', 'C', 'DATA'),
 ('status_heartbeat', '<path d="M2.5 12h5l2.2-5.5 3.6 11 2.2-5.5h6"/>', 'C', 'Header'),
 # ---- controls ----
 ('ctl_chevron_up', '<path d="M6 15l6-6 6 6"/>', 'C', 'All'),
 ('ctl_chevron_down', '<path d="M6 9l6 6 6-6"/>', 'C', 'All'),
 ('ctl_chevron_left', '<path d="M15 6l-6 6 6 6"/>', 'C', 'All'),
 ('ctl_chevron_right', '<path d="M9 6l6 6-6 6"/>', 'C', 'All'),
 ('ctl_expand', '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M12 8.5v7M8.5 12h7"/>', 'C', 'DATA'),
 ('ctl_collapse', '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8.5 12h7"/>', 'C', 'DATA'),
 ('ctl_close', '<path d="M6 6l12 12M18 6L6 18"/>', 'C', 'All'),
 ('ctl_check', '<path d="M4.5 12.5l5 5L19.5 7"/>', 'C', 'All'),
 ('ctl_plus', '<path d="M12 5v14M5 12h14"/>', 'C', 'All'),
 ('ctl_minus', '<path d="M5 12h14"/>', 'C', 'All'),
 ('ctl_search', '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/>', 'C', 'INV, DATA'),
 ('ctl_filter', '<path d="M3.5 5h17l-6.5 8v6l-4-2v-4z"/>', 'C', 'INV, DATA'),
 ('ctl_settings', '<path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/>', 'C', 'All'),
 ('ctl_refresh', '<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3"/><path d="M19.5 4v4.5H15"/>', 'C', 'All'),
 ('ctl_copy', '<rect x="8.5" y="8.5" width="12" height="12" rx="2"/><path d="M15.5 8.5v-3a2 2 0 0 0-2-2h-8a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h3"/>', 'C', 'DATA'),
 ('ctl_save', '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4h11L20 7.5v11a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18.5z"/><path d="M8 4v5h7V4M8 20v-6h8v6"/>', 'C', 'DATA'),
 ('ctl_more', '<circle cx="5.5" cy="12" r="1.4" fill="@C"/><circle cx="12" cy="12" r="1.4" fill="@C"/><circle cx="18.5" cy="12" r="1.4" fill="@C"/>', 'C', 'All'),
 ('ctl_back', '<path d="M20 12H4M10 6l-6 6 6 6"/>', 'C', 'All'),
 ('ctl_sort', '<path d="M7 20V5M3.5 8.5L7 5l3.5 3.5M17 4v15M13.5 15.5L17 19l3.5-3.5"/>', 'C', 'INV'),
 # ---- indicators ----
 ('sel_arrow', '<path d="M7 5l11 7-11 7z" fill="@C"/>', 'C', 'All'),
 ('sel_bracket', f'<path d="{BRK}"/>', 'C', 'All'),
 ('sel_cursor_block', '<rect x="7" y="5" width="10" height="14" fill="@C"/>', 'C', 'All'),
 ('sel_dot', '<circle cx="12" cy="12" r="4" fill="@C"/><circle cx="12" cy="12" r="8.5"/>', 'C', 'All'),
 ] + [
 (f'progress_ring_{p}', f'<circle cx="12" cy="12" r="8.5" stroke-opacity="0.25"/>' + (f'<path d="{ring_d(12, 12, 8.5, p/100)}"/>' if p else ''), 'C', 'Medical, All')
 for p in (0, 25, 50, 75, 100)
 ] + [
 ('loading_spinner', '<path d="M12 3a9 9 0 1 1-9 9"/><path d="M3 12a9 9 0 0 1 9-9" stroke-opacity="0.25"/>', 'C', 'All'),
 ('led_off', '<circle cx="12" cy="12" r="8" stroke="@G" stroke-opacity="0.6"/><circle cx="12" cy="12" r="5" fill="@H" stroke="none"/>', 'C', 'Header'),
 ('led_green', '<circle cx="12" cy="12" r="8" stroke="@G" stroke-opacity="0.6"/><circle cx="12" cy="12" r="5.2" fill="@C" stroke="none"/><circle cx="10.2" cy="10.2" r="1.5" fill="@W" stroke="none"/>', 'C', 'Header'),
 ('led_amber', '<circle cx="12" cy="12" r="8" stroke="@G" stroke-opacity="0.6"/><circle cx="12" cy="12" r="5.2" fill="@A" stroke="none"/><circle cx="10.2" cy="10.2" r="1.5" fill="#FFE2A6" stroke="none"/>', 'C', 'Header'),
 ('led_alert', '<circle cx="12" cy="12" r="5" fill="@A" stroke="none"/><circle cx="12" cy="12" r="8.5" stroke="@A" stroke-opacity="0.7"/><path d="M12 10v2.4M12 14.2v.1" stroke="@K" stroke-width="1.8"/>', 'C', 'Header'),
 # ---- inventory actions / properties ----
 ('act_use', '<path d="M4 12h11M10.5 7l5 5-5 5M19.5 4v16"/>', 'C', 'INV'),
 ('act_drop', '<path d="M12 4v11M7 10.5l5 5 5-5M5 20h14"/>', 'C', 'INV'),
 ('act_equip', '<path d="M12 8.5a2.2 2.2 0 1 0-2.2-2.2"/><path d="M12 8.5v2L20 15.2a1.2 1.2 0 0 1-.6 2.3H4.6a1.2 1.2 0 0 1-.6-2.3L12 10.5"/>', 'C', 'INV'),
 ('act_favorite', f'<path d="{STAR24}"/>', 'C', 'INV'),
 ('act_favorite_on', f'<path d="{STAR24}" fill="@C"/>', 'C', 'INV'),
 ('inv_weight', '<circle cx="12" cy="6.2" r="2.7"/><path d="M5.5 21l2.2-11h8.6l2.2 11z"/>', 'C', 'INV'),
 ('inv_value', '<path d="M3.5 12.5v-8a1 1 0 0 1 1-1h8l8 8-9 9z"/><circle cx="8" cy="8" r="1.3" fill="@C"/>', 'C', 'INV'),
 ('inv_quantity', '<path d="M12 4l8.5 4.5L12 13 3.5 8.5z"/><path d="M3.5 12.5L12 17l8.5-4.5M3.5 16.5L12 21l8.5-4.5"/>', 'C', 'INV'),
 ('inv_condition', '<path d="M4 17a8.5 8.5 0 1 1 16 0"/><path d="M12 17l4-5.5"/><circle cx="12" cy="17" r="1.2" fill="@C"/><path d="M6.5 11l1 .8M12 7.5v1.3M17.5 11l-1 .8"/>', 'C', 'INV'),
 ('inv_equipped', '<path d="M12 3l7.5 3v6c0 4.5-3.2 7.8-7.5 9.5C7.7 19.8 4.5 16.5 4.5 12V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>', 'C', 'INV'),
 # ---- map / world ----
 ('map_local', '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.8"/><path d="M12 12l6-6"/><circle cx="12" cy="12" r="1" fill="@C"/>', 'C', 'MAP'),
 ('map_global', '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c-3.6 3-3.6 15 0 18M12 3c3.6 3 3.6 15 0 18"/>', 'C', 'MAP'),
 ('map_player', '<path d="M12 3l6.5 17-6.5-4-6.5 4z" fill="@C"/>', 'C', 'MAP'),
 ('map_quest', '<path d="M12 2.5l9.5 9.5-9.5 9.5L2.5 12z"/><path d="M12 8v5M12 16.2v.1"/>', 'C', 'MAP'),
 ('map_custom', '<path d="M12 21.5s-6.5-6-6.5-11.2a6.5 6.5 0 0 1 13 0c0 5.2-6.5 11.2-6.5 11.2z"/><circle cx="12" cy="10.3" r="2.3"/>', 'C', 'MAP'),
 ('map_location_browser', '<circle cx="4.5" cy="5.5" r="1.2" fill="@C"/><circle cx="4.5" cy="12" r="1.2" fill="@C"/><circle cx="4.5" cy="18.5" r="1.2" fill="@C"/><path d="M9 5.5h11.5M9 12h11.5M9 18.5h11.5"/>', 'C', 'MAP'),
 ('map_workshop', f'<path d="{gear_d(12, 12, 9.5, 7, 8)}"/><circle cx="12" cy="12" r="2.8"/>', 'C', 'MAP'),
 ('map_quest_indicator', '<path d="M6 21V3.5M6 4.5h12l-3 4 3 4H6"/>', 'C', 'MAP'),
 ('map_perk', '<circle cx="12" cy="9" r="5.5"/><path d="M8.5 13.5L6.5 21l5.5-3 5.5 3-2-7.5"/>', 'C', 'STAT'),
 ('map_select', f'<path d="{BRK}"/>', 'C', 'MAP'),
 ('map_zoom_in', '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21M10.5 7.8v5.4M7.8 10.5h5.4"/>', 'C', 'MAP'),
 ('map_zoom_out', '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21M7.8 10.5h5.4"/>', 'C', 'MAP'),
 ('map_center', '<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="7.5"/><path d="M12 2v3.5M12 18.5V22M2 12h3.5M18.5 12H22"/>', 'C', 'MAP'),
 ('map_rotate', '<path d="M5 12a7 7 0 0 1 12.5-4.3M18.5 4.5v3.7h-3.7M19 12a7 7 0 0 1-12.5 4.3M5.5 19.5v-3.7h3.7"/>', 'C', 'MAP'),
 ('map_north_up', '<path d="M12 3l5 18-5-4-5 4z"/>', 'C', 'MAP'),
 ('map_layers', '<path d="M12 3.5l9 4.5-9 4.5L3 8z"/><path d="M3 12l9 4.5 9-4.5M3 16l9 4.5 9-4.5"/>', 'C', 'MAP'),
 # ---- radio ----
 ('radio_station', '<path d="M12 12v9"/><circle cx="12" cy="10" r="2"/><path d="M7.5 5.8a6.2 6.2 0 0 0 0 8.4M16.5 5.8a6.2 6.2 0 0 1 0 8.4M4.7 3.2a10 10 0 0 0 0 13.6M19.3 3.2a10 10 0 0 1 0 13.6"/>', 'C', 'RADIO'),
 ('radio_tuner', '<circle cx="12" cy="12" r="8.5"/><path d="M12 12l4-4M5.5 12H7M17 12h1.5M12 5.5V7M7.4 7.4l1 1M16.6 7.4l-1 1"/>', 'C', 'RADIO'),
 ('radio_wave', '<path d="M2.5 12h2l2-5 3 10 3-13 3 11 2-3h4"/>', 'C', 'RADIO'),
 ('radio_speaker', '<path d="M4 9.5v5h3.5L12.5 19V5l-5 4.5z"/><path d="M16 9a4.2 4.2 0 0 1 0 6M18.8 6.3a8 8 0 0 1 0 11.4"/>', 'C', 'RADIO'),
 # ---- diagnostics / data ----
 ('data_browser', '<rect x="3" y="3.5" width="6" height="5" rx="1"/><path d="M6 8.5V18h4M6 13h4"/><rect x="10" y="11" width="11" height="4" rx="1"/><rect x="10" y="16" width="11" height="4" rx="1"/>', 'C', 'DATA'),
 ('data_logger', '<rect x="3.5" y="3.5" width="17" height="17" rx="2"/><path d="M7.5 8h9M7.5 12h4"/><circle cx="16" cy="16" r="3"/><path d="M16 14.6V16l1 .8"/>', 'C', 'DATA'),
 ('data_export', '<path d="M12 15V3.5M7.5 8L12 3.5 16.5 8"/>' + TRAY, 'C', 'DATA'),
 ('data_export_file', '<path d="M14 3.5H7a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8.5z"/><path d="M14 3.5v5h5M12 17.5v-6M9.5 14L12 11.5l2.5 2.5"/>', 'C', 'DATA'),
 ('data_import', '<path d="M14 3.5H7a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8.5z"/><path d="M14 3.5v5h5M12 11.5v6M9.5 15l2.5 2.5 2.5-2.5"/>', 'C', 'DATA'),
 ('tree_branch', '<path d="M6 4v10a3 3 0 0 0 3 3h10"/>', 'C', 'DATA'),
 ('tree_node', '<circle cx="12" cy="12" r="3.5"/><path d="M12 3v5.5M12 15.5V21"/>', 'C', 'DATA'),
 ('tree_leaf', '<rect x="8" y="8" width="8" height="8" rx="1.5"/><path d="M3 12h5"/>', 'C', 'DATA'),
 # ---- body-status glyphs (24) ----
 ('limb_ok', LIMB + '<path d="M9.5 12.5l1.8 1.8 3.2-3.6"/>', 'C', 'STAT'),
 ('limb_wounded', LIMB + '<path d="M10 12h4"/>', 'C', 'STAT'),
 ('limb_damaged', LIMB + '<path d="M10 10.5h4M10 13.5h4"/>', 'A', 'STAT'),
 ('limb_critical', LIMB + '<path d="M12 8.5v4.5M12 15.7v.1"/>', 'A', 'STAT'),
 ('limb_crippled', '<path d="M7.5 9V7.5a4.5 4.5 0 0 1 9 0V9"/><path d="M7.5 15v1.5a4.5 4.5 0 0 0 9 0V15"/><path d="M9 12l2-1.800 2 3.200 2-1.400"/>', 'G', 'STAT'),
 ('ind_health_ok', f'<path d="{HEART24}" fill="@C"/>', 'C', 'STAT'),
 ('ind_health_low', f'<path d="{HEART24}"/><path d="M9 10.5l3 3 3-3"/>', 'C', 'STAT'),
 ('ind_health_critical', f'<path d="{HEART24}"/><path d="M12 9.5v4M12 16v.1"/>', 'A', 'STAT'),
 ('ind_rad_none', f'<path d="{trefoil_d(12, 12, 2.2, 9)}" fill="@C" fill-opacity="0.3" stroke="none"/><circle cx="12" cy="12" r="1.5" fill="@C" fill-opacity="0.3" stroke="none"/>', 'C', 'STAT'),
 ('ind_rad_low', f'<path d="{trefoil_d(12, 12, 2.2, 9)}" fill="@C" stroke="none"/><circle cx="12" cy="12" r="1.5" fill="@C" stroke="none"/>', 'C', 'STAT'),
 ('ind_rad_high', f'<path d="{trefoil_d(12, 12, 2.2, 7)}" fill="@A" stroke="none"/><circle cx="12" cy="12" r="1.4" fill="@A" stroke="none"/><path d="{BRK}" stroke="@A"/>', 'A', 'STAT'),
 ('marker_injury', '<circle cx="12" cy="12" r="8"/><path d="M12 7.5v9M7.5 12h9"/>', 'A', 'STAT'),
]
