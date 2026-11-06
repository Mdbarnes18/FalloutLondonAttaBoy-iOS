import random
from geo import *
from palette import tokens, PAL
def scuffs(seed, n, x0, y0, x1, y1, col='@G', op=0.28, sw=1.2, maxlen=18):
    rng = random.Random(seed); d = ''
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1); a = rng.uniform(-0.9, 0.9); L = rng.uniform(4, maxlen)
        d += f'M{fmt(x)} {fmt(y)}l{fmt(L*math.cos(a))} {fmt(L*math.sin(a))}'
    return f'<path d="{d}" stroke="{col}" stroke-opacity="{op}" stroke-width="{sw}" fill="none"/>'
def rivet(x, y, r=3):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="@G" stroke="@K" stroke-width="0.8"/>'
            f'<circle cx="{fmt(x-r*0.3)}" cy="{fmt(y-r*0.3)}" r="{fmt(r*0.35)}" fill="@W" fill-opacity="0.55" stroke="none"/>')
def screw(x, y, r=3.2):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="@G" stroke="@K" stroke-width="0.8"/>'
            f'<path d="M{fmt(x-r*0.65)} {fmt(y-r*0.2)}L{fmt(x+r*0.65)} {fmt(y+r*0.2)}" stroke="@K" stroke-width="1.1"/>')
G = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
# Each: (id, w, h, body, slice(l,t,r,b) or None, screen, world, variant)
UI = []
def add(i, w, h, body, sl=None, screen='All', world='Shared', note=''):
    UI.append(dict(id=i, w=w, h=h, body=body, slice=sl, screen=screen, world=world, note=note))

# ---- panels (128x128, 9-slice 20) ----
add('panel_clean', 128, 128,
    f'<path d="{rr(2, 2, 124, 124, 8)}" fill="@H" fill-opacity="0.9" stroke="@D" stroke-width="2"/>'
    f'<path d="{rr(8, 8, 112, 112, 4)}" stroke="@C" stroke-opacity="0.3" stroke-width="1.5"/>'
    f'<path d="{corners(0, 0, 128, 128, 16, 13)}" stroke="@C" stroke-width="2.5"/>', (20, 20, 20, 20), 'All', note='Clean industrial panel; centre is semi-opaque charcoal.')
add('panel_worn', 128, 128,
    f'<path d="{rr(2, 2, 124, 124, 8)}" fill="#2A2E22" fill-opacity="0.94" stroke="@G" stroke-width="2"/>'
    f'<path d="{rr(8, 8, 112, 112, 4)}" stroke="@M" stroke-opacity="0.9" stroke-width="1.5"/>'
    + scuffs(11, 26, 10, 10, 118, 118) + scuffs(5, 10, 8, 8, 120, 120, '@K', 0.35, 1.6, 12) +
    '<path d="M2 10L10 2M118 2l8 8" stroke="@B" stroke-opacity="0.5" stroke-width="1.5"/>'
    + rivet(14, 14) + rivet(114, 14) + rivet(14, 114) + rivet(114, 114), (20, 20, 20, 20), 'All', note='Worn variant: scuffs, brass edge wear, rivets.')
add('panel_inset', 128, 128,
    f'<path d="{rr(2, 2, 124, 124, 6)}" fill="@K" fill-opacity="0.72" stroke="@D" stroke-opacity="0.55" stroke-width="2"/>'
    '<path d="M6 122V6h116" stroke="@K" stroke-width="2.5"/><path d="M8 124h116V8" stroke="@G" stroke-opacity="0.45" stroke-width="1.5"/>', (16, 16, 16, 16), 'All', note='Recessed well for lists and data readouts.')
add('panel_warning', 128, 128,
    f'<path d="{rr(2, 2, 124, 124, 8)}" fill="@H" fill-opacity="0.92" stroke="@A" stroke-width="2"/>'
    f'<path d="{rr(4, 4, 120, 18, 4)}" fill="@K" stroke="none"/>' + hazard(4, 4, 120, 18, 22, '@A') +
    f'<path d="{rr(4, 4, 120, 18, 4)}" stroke="@A" stroke-width="1.5"/>', (20, 26, 20, 20), 'All', note='Warning panel with hazard band across the top.')
add('panel_notification', 128, 64,
    '<path d="M16 2H122a4 4 0 0 1 4 4V58a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V16z" fill="@H" fill-opacity="0.92" stroke="@C" stroke-opacity="0.75" stroke-width="2"/>'
    '<path d="M2 16L16 2" stroke="@C" stroke-width="2.5"/><path d="M12 14v36" stroke="@C" stroke-width="3" stroke-opacity="0.8"/>', (22, 16, 12, 12), 'All', note='Notification toast; accent bar on the left.')
# ---- frames (centre transparent) ----
FR_OUT, FR_IN = rr(2, 2, 252, 188, 24), rr(26, 26, 204, 140, 10)
add('frame_screen_clean', 256, 192,
    f'<path d="{FR_OUT}{FR_IN}" fill="@H" fill-rule="evenodd" stroke="@G" stroke-width="2"/>'
    f'<path d="{rr(28, 28, 200, 136, 9)}" stroke="@K" stroke-width="3"/><path d="{rr(30, 30, 196, 132, 8)}" stroke="@C" stroke-opacity="0.35" stroke-width="1.2"/>',
    (40, 40, 40, 40), 'All', note='CRT bezel; the inside is fully transparent so screen content shows through.')
add('frame_screen_worn', 256, 192,
    f'<path d="{FR_OUT}{FR_IN}" fill="#2A2E22" fill-rule="evenodd" stroke="@G" stroke-width="2"/>'
    f'<path d="{rr(28, 28, 200, 136, 9)}" stroke="@K" stroke-width="3"/><path d="{rr(30, 30, 196, 132, 8)}" stroke="@C" stroke-opacity="0.3" stroke-width="1.2"/>'
    + scuffs(21, 40, 6, 6, 250, 24, '@G', 0.3) + scuffs(22, 40, 6, 168, 250, 186, '@G', 0.3) + scuffs(23, 24, 6, 24, 24, 168, '@G', 0.3) + scuffs(24, 24, 232, 24, 250, 168, '@G', 0.3)
    + rivet(14, 14, 3.5) + rivet(242, 14, 3.5) + rivet(14, 178, 3.5) + rivet(242, 178, 3.5)
    + '<path d="M2 26L26 2M230 2l24 24" stroke="@B" stroke-opacity="0.45" stroke-width="1.5"/>', (40, 40, 40, 40), 'All', note='Worn CRT bezel with rivets and scuffs.')
def ticks(x0, y0, x1, y1, n, ln, horiz=True):
    d = ''
    for k in range(n+1):
        t = k/n
        if horiz: x = x0+(x1-x0)*t; d += f'M{fmt(x)} {fmt(y0)}v{fmt(ln if k % 4 else ln*1.8)}'
        else: y = y0+(y1-y0)*t; d += f'M{fmt(x0)} {fmt(y)}h{fmt(ln if k % 4 else ln*1.8)}'
    return d
add('frame_map_local', 256, 256,
    f'<path d="{corners(0, 0, 256, 256, 36, 3)}" stroke="@C" stroke-width="3.5"/>'
    f'<path d="{rr(10, 10, 236, 236, 4)}" stroke="@C" stroke-opacity="0.35" stroke-width="1.2"/>'
    f'<path d="{ticks(48, 14, 208, 14, 16, 5)}{ticks(48, 242, 208, 242, 16, -5)}" stroke="@C" stroke-opacity="0.7" stroke-width="1.2"/>', (40, 40, 40, 40), 'MAP', note='Interface frame only; the app supplies the map image.')
add('frame_map_global', 256, 256,
    f'<path d="{rr(3, 3, 250, 250, 6)}" stroke="@C" stroke-width="2.5"/><path d="{rr(14, 14, 228, 228, 2)}" stroke="@C" stroke-opacity="0.5" stroke-width="1.2"/>'
    f'<path d="{ticks(14, 3, 242, 3, 38, 7)}{ticks(14, 253, 242, 253, 38, -7)}" stroke="@C" stroke-opacity="0.8" stroke-width="1.2"/>'
    f'<path d="{ticks(3, 14, 3, 242, 38, 7, False)}{ticks(253, 14, 253, 242, 38, -7, False)}" stroke="@C" stroke-opacity="0.8" stroke-width="1.2"/>', (24, 24, 24, 24), 'MAP', note='Graduated border; carries no coordinates or labels.')
# ---- buttons ----
BTN = lambda fill, fo, st, so=1.0, sw=2: f'<path d="{rr(2, 2, 92, 36, 6)}" fill="{fill}" fill-opacity="{fo}" stroke="{st}" stroke-opacity="{so}" stroke-width="{sw}"/>'
add('button_normal', 96, 40, BTN('@H', 0.92, '@C') + f'<path d="{rr(6, 6, 84, 28, 3)}" stroke="@C" stroke-opacity="0.22" stroke-width="1.2"/>', (14, 14, 14, 14), 'All')
add('button_pressed', 96, 40, BTN('@C', 0.2, '@C') + '<path d="M5 35V5h86" stroke="@K" stroke-opacity="0.6" stroke-width="2.5"/>', (14, 14, 14, 14), 'All')
add('button_selected', 96, 40, BTN('@C', 0.88, '@C') + f'<path d="{rr(6, 6, 84, 28, 3)}" stroke="@K" stroke-opacity="0.35" stroke-width="1.2"/>', (14, 14, 14, 14), 'All', note='Selected state; use dark text on top.')
add('button_disabled', 96, 40, BTN('@K', 0.5, '@G', 0.55) + f'<path d="{rr(6, 6, 84, 28, 3)}" stroke="@G" stroke-opacity="0.2" stroke-width="1.2"/>', (14, 14, 14, 14), 'All')
add('button_normal_worn', 96, 40, BTN('#2A2E22', 0.95, '@G') + scuffs(31, 9, 6, 6, 90, 34, '@G', 0.35, 1.1, 10) + '<path d="M2 8L8 2" stroke="@B" stroke-opacity="0.6" stroke-width="1.5"/>' + rivet(10, 20, 2) + rivet(86, 20, 2), (16, 14, 16, 14), 'All', note='Worn variant of button_normal.')
# ---- tabs ----
add('tab_active', 96, 36, '<path d="M2 36V10a8 8 0 0 1 8-8h76a8 8 0 0 1 8 8v26" fill="@H" fill-opacity="0.95" stroke="@C" stroke-width="2"/><path d="M8 34h80" stroke="@C" stroke-width="3"/>', (14, 12, 14, 0), 'All')
add('tab_inactive', 96, 36, '<path d="M2 36V12a8 8 0 0 1 8-8h76a8 8 0 0 1 8 8v24" fill="@K" fill-opacity="0.55" stroke="@D" stroke-opacity="0.75" stroke-width="1.8"/>', (14, 12, 14, 0), 'All')
# ---- toggles / checks (no slice) ----
add('toggle_off', 48, 24, f'<path d="{rr(2, 2, 44, 20, 10)}" fill="@K" fill-opacity="0.6" stroke="@G" stroke-width="2"/><circle cx="12" cy="12" r="6" fill="@G" stroke="none"/><circle cx="10.5" cy="10.5" r="1.8" fill="@W" fill-opacity="0.5" stroke="none"/>', None, 'Settings')
add('toggle_on', 48, 24, f'<path d="{rr(2, 2, 44, 20, 10)}" fill="@C" fill-opacity="0.22" stroke="@C" stroke-width="2"/><circle cx="36" cy="12" r="6" fill="@C" stroke="none"/><circle cx="34.5" cy="10.5" r="1.8" fill="@W" fill-opacity="0.7" stroke="none"/>', None, 'Settings')
add('checkbox_off', 24, 24, f'<path d="{rr(3.5, 3.5, 17, 17, 3)}" stroke="@C" stroke-width="1.8" fill="@K" fill-opacity="0.5"/>', None, 'Settings')
add('checkbox_on', 24, 24, f'<path d="{rr(3.5, 3.5, 17, 17, 3)}" stroke="@C" stroke-width="1.8" fill="@C" fill-opacity="0.2"/><path d="M7.5 12.5l3 3 6-6.5" stroke="@C" stroke-width="2"/>', None, 'Settings')
add('radio_off', 24, 24, '<circle cx="12" cy="12" r="8.5" stroke="@C" stroke-width="1.8" fill="@K" fill-opacity="0.5"/>', None, 'Settings')
add('radio_on', 24, 24, '<circle cx="12" cy="12" r="8.5" stroke="@C" stroke-width="1.8" fill="@C" fill-opacity="0.15"/><circle cx="12" cy="12" r="4.2" fill="@C" stroke="none"/>', None, 'Settings')
# ---- progress / scrollbars ----
add('progress_bar_track', 128, 16, f'<path d="{rr(2, 2, 124, 12, 4)}" fill="@K" fill-opacity="0.65" stroke="@D" stroke-width="1.8"/>', (8, 0, 8, 0), 'All')
add('progress_bar_fill', 128, 16, f'<path d="{rr(4, 4, 120, 8, 2.5)}" fill="@C" stroke="none"/><path d="M8 6h112" stroke="@W" stroke-opacity="0.45" stroke-width="1.2"/>', (8, 0, 8, 0), 'All')
add('progress_bar_segments', 128, 16, '<path d="' + ''.join(rr(4+i*10, 4, 8, 8, 1.5) for i in range(12)) + '" fill="@C" stroke="none"/>', None, 'Medical')
add('scrollbar_track_v', 12, 64, f'<path d="{rr(3, 1.5, 6, 61, 3)}" fill="@K" fill-opacity="0.55" stroke="@D" stroke-width="1.2"/>', (0, 6, 0, 6), 'All')
add('scrollbar_thumb_v', 12, 40, f'<path d="{rr(2.5, 1.5, 7, 37, 3.5)}" fill="@C" fill-opacity="0.85" stroke="none"/>', (0, 6, 0, 6), 'All')
add('scrollbar_track_h', 64, 12, f'<path d="{rr(1.5, 3, 61, 6, 3)}" fill="@K" fill-opacity="0.55" stroke="@D" stroke-width="1.2"/>', (6, 0, 6, 0), 'All')
add('scrollbar_thumb_h', 40, 12, f'<path d="{rr(1.5, 2.5, 37, 7, 3.5)}" fill="@C" fill-opacity="0.85" stroke="none"/>', (6, 0, 6, 0), 'All')
# ---- dividers & ornaments ----
add('divider_h', 128, 8, '<path d="M8 4H120" stroke="@C" stroke-opacity="0.6" stroke-width="1.5"/><path d="M2 4l4-3 4 3-4 3zM118 4l4-3 4 3-4 3z" fill="@C" stroke="none"/>', (12, 0, 12, 0), 'All')
add('divider_v', 8, 128, '<path d="M4 8V120" stroke="@C" stroke-opacity="0.6" stroke-width="1.5"/><path d="M4 2l3 4-3 4-3-4zM4 118l3 4-3 4-3-4z" fill="@C" stroke="none"/>', (0, 12, 0, 12), 'All')
add('divider_dotted_h', 128, 8, '<path d="' + ''.join(f'M{6+i*8} 4h.01' for i in range(16)) + '" stroke="@C" stroke-opacity="0.7" stroke-width="2.4"/>', None, 'All')
add('divider_london', 256, 20,
    '<path d="M4 12H106M150 12H252" stroke="@C" stroke-opacity="0.65" stroke-width="1.5"/>'
    '<path d="M112 18V12C112 7 119 3 128 2C137 3 144 7 144 12V18" stroke="@C" stroke-width="1.8"/><path d="M120 18V13C120 10 124 7 128 6C132 7 136 10 136 13V18" stroke="@C" stroke-opacity="0.6" stroke-width="1.5"/>',
    (100, 0, 100, 0), 'All', 'Fallout: London', 'Pointed-arch motif (generic Gothic arch).')
add('divider_commonwealth', 256, 20,
    '<path d="M4 12H108M148 12H252" stroke="@C" stroke-opacity="0.65" stroke-width="1.5"/>'
    '<path d="M112 14l8-8 8 8 8-8 8 8" stroke="@C" stroke-width="1.8"/><path d="M118 18h20" stroke="@C" stroke-opacity="0.6" stroke-width="1.5"/>',
    (100, 0, 100, 0), 'All', 'Fallout 4 Commonwealth', 'Stepped chevron motif.')
add('corner_london', 64, 64, '<path d="M4 60V12C4 8 8 4 12 4H60" stroke="@C" stroke-width="2.5"/><path d="M12 60V22C12 17 17 12 22 12H60" stroke="@C" stroke-opacity="0.5" stroke-width="1.5"/><path d="M4 28C12 28 18 22 18 14" stroke="@C" stroke-width="1.5" stroke-opacity="0.8"/>', None, 'All', 'Fallout: London', 'Top-left corner ornament; rotate 90/180/270 for other corners.')
add('corner_commonwealth', 64, 64, '<path d="M4 60V4H60" stroke="@C" stroke-width="2.5"/><path d="M12 60V12H60" stroke="@C" stroke-opacity="0.5" stroke-width="1.5"/><path d="M4 22h10v-10M22 4v10h-10" stroke="@C" stroke-width="1.5" stroke-opacity="0.8"/>', None, 'All', 'Fallout 4 Commonwealth', 'Top-left corner ornament; rotate for other corners.')
add('selection_highlight', 96, 32, f'<path d="{rr(2, 2, 92, 28, 4)}" fill="@C" fill-opacity="0.12" stroke="@C" stroke-width="1.5"/><path d="{corners(0, 0, 96, 32, 8, 2)}" stroke="@C" stroke-width="2.5"/>', (12, 10, 12, 10), 'All')
# ---- mechanical controls / decor ----
def dial_ticks(cx, cy, r0, r1, n):
    d = ''
    for i in range(n):
        a = 135 + 270*i/(n-1); x0, y0 = pt(cx, cy, r0, a); x1, y1 = pt(cx, cy, r1, a)
        d += f'M{fmt(x0)} {fmt(y0)}L{fmt(x1)} {fmt(y1)}'
    return d
add('knob_dial', 48, 48, f'<path d="{dial_ticks(24, 24, 18, 22, 11)}" stroke="@G" stroke-width="1.6"/><circle cx="24" cy="24" r="14.5" fill="@H" stroke="@G" stroke-width="2"/><circle cx="24" cy="24" r="10" fill="@K" fill-opacity="0.6" stroke="@C" stroke-opacity="0.5" stroke-width="1.2"/><path d="M24 24l-5.500 5.500" stroke="@C" stroke-width="2.4"/>', None, 'All')
add('switch_lever_up', 24, 48, '<rect x="5" y="30" width="14" height="14" rx="3" fill="@H" stroke="@G" stroke-width="1.8"/><path d="M12 32V10" stroke="@G" stroke-width="3.5"/><circle cx="12" cy="9" r="4.500" fill="@C" stroke="none"/>', None, 'Settings')
add('switch_lever_down', 24, 48, '<rect x="5" y="4" width="14" height="14" rx="3" fill="@H" stroke="@G" stroke-width="1.8"/><path d="M12 16V38" stroke="@G" stroke-width="3.5"/><circle cx="12" cy="39" r="4.500" fill="@G" stroke="none"/>', None, 'Settings')
add('rivet_round', 16, 16, rivet(8, 8, 5), None, 'All')
add('screw_slot', 16, 16, screw(8, 8, 5.5), None, 'All')
add('label_plate', 96, 32, f'<path d="{rr(2, 2, 92, 28, 3)}" fill="@B" fill-opacity="0.9" stroke="@K" stroke-width="1.5"/><path d="{rr(5, 5, 86, 22, 2)}" stroke="@K" stroke-opacity="0.45" stroke-width="1"/>' + screw(10, 16, 2.6) + screw(86, 16, 2.6), (12, 8, 12, 8), 'All', note='Brass label plate; add text on top.')
add('band_hazard', 64, 16, '<path d="M0 0H64V16H0z" fill="@K" stroke="none"/>' + hazard(0, 0, 64, 16, 32, '@A'), None, 'All', note='Tiles horizontally.')
add('badge_dot', 16, 16, '<circle cx="8" cy="8" r="5" fill="@A" stroke="@K" stroke-width="1.2"/>', None, 'All')
