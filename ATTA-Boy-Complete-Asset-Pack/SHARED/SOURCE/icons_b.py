from geo import *
from svgr import scale_path, fmt
HEART48 = scale_path(HEART24, 2)
PISTOL = 'M6 14H41V24H30V37a2 2 0 0 1-2 2H24a2 2 0 0 1-2-2V31H18a3 3 0 0 1-3-3V24H6Z'
def bullet(x): return f'<path d="M{x} 40V19c0-5 2-9 5-12 3 3 5 7 5 12v21z"/><path d="M{x} 34h10"/>'
# ---------- 48-grid detailed icons (stroke 2.5) : (id, body, color, screen, world) ----------
I48 = [
 ('special_strength', '<rect x="7" y="16" width="6" height="16" rx="1.5"/><rect x="35" y="16" width="6" height="16" rx="1.5"/><path d="M13 24h22M3 21v6M45 21v6"/>', 'C', 'STAT'),
 ('special_perception', '<path d="M3.5 24C9 14 16 10 24 10s15 4 20.5 14C39 34 32 38 24 38S9 34 3.5 24z"/><circle cx="24" cy="24" r="6"/><circle cx="24" cy="24" r="2" fill="@C"/>', 'C', 'STAT'),
 ('special_endurance', '<path d="M24 4.5l16 6v13c0 9-7 15.5-16 19.5C15 39 8 32.5 8 23.5v-13z"/><path d="M13 24h6l3-7 4 14 3-7h6"/>', 'C', 'STAT'),
 ('special_charisma', '<path d="M9 8h30a3 3 0 0 1 3 3v18a3 3 0 0 1-3 3H23l-9 8v-8H9a3 3 0 0 1-3-3V11a3 3 0 0 1 3-3z"/><path d="M17 21c2 4 12 4 14 0"/><circle cx="18" cy="16" r="1.4" fill="@C"/><circle cx="30" cy="16" r="1.4" fill="@C"/>', 'C', 'STAT'),
 ('special_intelligence', '<path d="M24 5a13 13 0 0 0-8 23c1.2 1 2 2.8 2 4.6V35h12v-2.4c0-1.8.8-3.6 2-4.6A13 13 0 0 0 24 5z"/><path d="M19 40h10M21.5 44h5M20 22l4 5 4-5"/>', 'C', 'STAT'),
 ('special_agility', '<path d="M18 11l13 13-13 13M30 11l13 13-13 13"/><path d="M4 18h7M4 30h7M7 24h4"/>', 'C', 'STAT'),
 ('special_luck', '<rect x="7" y="7" width="34" height="34" rx="7"/><g fill="@C" stroke="none"><circle cx="17" cy="17" r="2.6"/><circle cx="31" cy="17" r="2.6"/><circle cx="24" cy="24" r="2.6"/><circle cx="17" cy="31" r="2.6"/><circle cx="31" cy="31" r="2.6"/></g>', 'C', 'STAT'),
 ('stat_experience', '<path d="M24 5l4.6 14.4L43 24l-14.4 4.6L24 43l-4.6-14.4L5 24l14.4-4.6z"/><circle cx="24" cy="24" r="3"/>', 'C', 'STAT'),
 ('stat_level', '<path d="M24 4l17 10v20L24 44 7 34V14z"/><path d="M24 33V17M17 24l7-7 7 7"/>', 'C', 'STAT'),
 ('stat_health', f'<path d="{HEART48}"/>', 'C', 'STAT'),
 ('stat_action_points', '<circle cx="24" cy="24" r="19"/><path d="M27 9L15 26h9l-3 13 12-18h-9z"/>', 'C', 'STAT'),
 ('stat_radiation', f'<circle cx="24" cy="24" r="20"/><path d="{trefoil_d(24, 24, 4.5, 15)}" fill="@C" stroke="none"/><circle cx="24" cy="24" r="3" fill="@C" stroke="none"/>', 'C', 'STAT'),
 ('stat_carry_weight', '<circle cx="24" cy="11" r="5.500"/><path d="M10 43l4.500-23h19L38 43z"/>', 'C', 'STAT, INV'),
 ('stat_active_effects', '<circle cx="9" cy="14" r="2" fill="@C"/><circle cx="9" cy="24" r="2" fill="@C"/><circle cx="9" cy="34" r="2" fill="@C"/><path d="M17 14h24M17 24h24M17 34h16"/>', 'C', 'STAT'),
 ('stat_game_stats', '<rect x="8" y="26" width="8" height="14" rx="1"/><rect x="20" y="14" width="8" height="26" rx="1"/><rect x="32" y="20" width="8" height="20" rx="1"/><path d="M5 43h38"/>', 'C', 'STAT'),
 ('stat_ammo_count', '<path d="M7 40V21c0-4 2-7 4.500-9.500C13.500 14 16 17 16 21v19z"/><path d="M7 34h9M26 16h15M26 26h15M26 36h9"/>', 'C', 'STAT, INV'),
 ('stat_equipped_weapons', f'<path d="{scale_path(PISTOL, 0.8)}"/><circle cx="35" cy="34" r="8"/><path d="M31 34l3 3 5-6"/>', 'C', 'STAT, INV'),
 ('map_compass', '<circle cx="24" cy="24" r="19"/><path d="M24 7l5.500 17L24 41l-5.500-17z"/><path d="M24 8l5 16H19z" fill="@C"/><path d="M24 2v4M24 42v4M2 24h4M42 24h4"/>', 'C', 'MAP'),
 ('world_london', '<path d="M18 40V20h12v20"/><path d="M17 20l7-13 7 13"/><circle cx="24" cy="28" r="3.5"/><path d="M24 26.2V28l1.300 1M10 40h28"/><path d="M4 45c3-2.500 6-2.500 9 0s6 2.500 9 0 6-2.500 9 0 6 2.500 9 0"/>', 'C', 'Identity'),
 ('world_commonwealth', '<path d="M8 40h32M10 40V26M18 40V26M30 40V26M38 40V26M7 26h34"/><path d="M12 26a12 10 0 0 1 24 0"/><path d="M24 16V9M22 9h4"/>', 'C', 'Identity'),
]
# ---------- authored on 48 grid, EXPORTED at 128 (scaled x128/48) ----------
CAT = [
 ('cat_weapons', f'<path d="{PISTOL}"/><path d="M33 18v3M36.500 18v3M9 11h3M35 11h3"/>', 'C', 'INV'),
 ('cat_apparel', '<path d="M17 7L7 12l3 7 4-2v22h20V17l4 2 3-7-10-5c-1 3-4 4-7 4s-6-1-7-4z"/>', 'C', 'INV'),
 ('cat_armor', '<path d="M13 7h22l6 7v8l-5 2v16H12V24l-5-2v-8z"/><path d="M18 7c1 4 3 6 6 6s5-2 6-6M17 27h14M24 18v6"/>', 'C', 'INV'),
 ('cat_aid', '<rect x="6" y="14" width="36" height="26" rx="3"/><path d="M17 14v-3a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v3M24 21v12M18 27h12"/>', 'C', 'INV'),
 ('cat_food', '<path d="M10 14a14 5 0 1 0 28 0a14 5 0 1 0-28 0"/><path d="M10 14v22M38 14v22M10 36a14 5 0 0 0 28 0M10 23a14 5 0 0 0 28 0M10 29a14 5 0 0 0 28 0"/>', 'C', 'INV'),
 ('cat_drink', '<path d="M20 5h8v9c0 3 6 5 6 11v14a2 2 0 0 1-2 2H16a2 2 0 0 1-2-2V25c0-6 6-8 6-11z"/><path d="M14 28h20M14 35h20"/>', 'C', 'INV'),
 ('cat_misc', '<path d="M24 5l17 9v18L24 43 7 32V14z"/><path d="M7 14l17 9 17-9M24 23v20"/>', 'C', 'INV'),
 ('cat_ammo', bullet(6) + bullet(19) + bullet(32), 'C', 'INV'),
 ('cat_grenades', '<circle cx="24" cy="29" r="12.500"/><path d="M20 17h8v-4h-8zM28 14c5-2 8 0 9 3"/><circle cx="37" cy="10" r="3"/><path d="M11.500 29h25M24 16.500v25"/>', 'C', 'INV'),
 ('cat_favorites', f'<path d="{star_d(24, 24, 19, 8.5)}"/>', 'C', 'INV'),
 ('cat_equipped', '<circle cx="24" cy="24" r="18"/><path d="M15 24.500l6 6 12-13"/>', 'C', 'INV'),
]
def _rr(): return rot_rect_d(24, 24, 38, 15, -45)
MED = [
 ('med_cross', '<path d="M19 6h10v13h13v10H29v13H19V29H6V19h13z"/>', 'C', 'STAT, Medical'),
 ('med_stimpak', '<path d="M24 4v8"/><rect x="17" y="12" width="14" height="22" rx="2"/><path d="M12 34h24M24 34v8M17 44h14M17 20h6M17 26h6"/>', 'C', 'STAT, INV, Medical'),
 ('med_radaway', '<path d="M14 7h20a2 2 0 0 1 2 2v21c0 6-6 9-12 13-6-4-12-7-12-13V9a2 2 0 0 1 2-2z"/><circle cx="24" cy="11" r="1.600"/><path d="M24 18c3.500 4.500 5.500 7.500 5.500 10.500a5.500 5.500 0 0 1-11 0c0-3 2-6 5.500-10.500z"/><path d="M24 43v4"/>', 'C', 'STAT, INV, Medical'),
 ('med_autodoc', '<rect x="3" y="33" width="42" height="5" rx="1.500"/><path d="M8 38v6M40 38v6"/><path d="M13 33V19a11 11 0 0 1 22 0v14"/><path d="M13 26h22" stroke-opacity="0.45"/><path d="M24 11v8M20 15h8"/>', 'C', 'Medical'),
 ('med_doctors_bag', '<path d="M13 19h22l9 6v15a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V25z"/><path d="M16 19v-2a8 8 0 0 1 16 0v2"/><path d="M4 28h40"/><rect x="21" y="25" width="6" height="7" rx="1.500"/>', 'C', 'Medical'),
 ('med_quick_aid', '<path d="M26 3L12 26h10l-3 19 17-25H25z"/><path d="M38 6v8M34 10h8"/>', 'C', 'Medical'),
 ('med_scanner', '<circle cx="24" cy="24" r="18"/><path d="M10 25h7l3.500-8 5 15 3.500-7H38"/><path d="M4 12V4h8M36 4h8v8M44 36v8h-8M12 44H4v-8"/>', 'C', 'Medical'),
 ('med_treatment', f'<path d="{_rr()}"/><path d="{rot_rect_d(24, 24, 14, 15, -45)}"/>', 'C', 'Medical'),
 ('med_healing', f'<path d="{HEART48}"/><path d="M24 19.500v11M18.500 25h11"/>', 'C', 'Medical'),
 ('med_treatment_progress', '<rect x="5" y="17" width="38" height="14" rx="2.500"/><path d="M11 22v4M17 22v4M23 22v4M29 22v4" stroke-width="3"/><path d="M35 22v4" stroke-width="3" stroke-opacity="0.3"/><path d="M24 8v5M24 35v5"/>', 'C', 'Medical'),
 ('med_warning', '<path d="M24 5L44 40H4z"/><path d="M24 17v11M18.500 22.500h11"/>', 'A', 'Medical'),
 ('med_critical_alert', f'<path d="{HEART48}"/><path d="M24 19v8M24 32v.1"/><path d="M5 7l4 4M43 7l-4 4M24 2v4"/>', 'A', 'Medical'),
]
# ---------- body status, native 128 grid ----------
import math
PARTS = {
 'head':      ('circle', (64, 17, 11)),
 'torso':     ('poly', [(45, 34), (83, 34), (79, 84), (49, 84)]),
 'arm_left':  ('poly', [(87, 35), (101, 41), (110, 88), (98, 91)]),
 'arm_right': ('poly', [(41, 35), (27, 41), (18, 88), (30, 91)]),
 'leg_left':  ('poly', [(66, 89), (84, 89), (87, 124), (70, 124)]),
 'leg_right': ('poly', [(62, 89), (44, 89), (41, 124), (58, 124)]),
}
STATES = ['healthy', 'wounded', 'damaged', 'critical', 'crippled']
def _circle_pts(cx, cy, r, n=28): return [pt(cx, cy, r, 360*i/n) for i in range(n)]
def _centroid(part):
    kind, g = PARTS[part]
    if kind == 'circle': return g[0], g[1]
    return sum(p[0] for p in g)/len(g), sum(p[1] for p in g)/len(g)
def _shape(part, attrs):
    kind, g = PARTS[part]
    if kind == 'circle': return f'<circle cx="{g[0]}" cy="{g[1]}" r="{g[2]}" {attrs}/>'
    return f'<polygon points="{" ".join(f"{x} {y}" for x, y in g)}" {attrs}/>'
def body_part(part, state):
    cx, cy = _centroid(part); k = 0.6 if part == 'head' else 1.0
    def line(x0, y0, x1, y1, col='@K'): return f'<path d="M{fmt(cx+x0*k)} {fmt(cy+y0*k)}L{fmt(cx+x1*k)} {fmt(cy+y1*k)}" stroke="{col}" stroke-width="4"/>'
    if state == 'healthy': return _shape(part, 'fill="@C" stroke="@C"')
    if state == 'wounded': return _shape(part, 'fill="@D" stroke="@D"') + line(-8, 8, 8, -8)
    if state == 'damaged': return _shape(part, 'fill="@A" stroke="@A"') + line(-11, 4, 4, -11) + line(-4, 11, 11, -4)
    if state == 'critical':
        z = f'<path d="M{fmt(cx-6*k)} {fmt(cy-13*k)}L{fmt(cx+3*k)} {fmt(cy-5*k)}L{fmt(cx-5*k)} {fmt(cy+2*k)}L{fmt(cx+5*k)} {fmt(cy+13*k)}" stroke="@K" stroke-width="4"/>'
        return _shape(part, 'fill="@A" stroke="@A"') + z
    if state == 'crippled':
        kind, g = PARTS[part]; pts = _circle_pts(*g) if kind == 'circle' else g
        d = poly_dashed(pts, 7, 5)
        x = f'<path d="M{fmt(cx-6*k)} {fmt(cy-6*k)}L{fmt(cx+6*k)} {fmt(cy+6*k)}M{fmt(cx+6*k)} {fmt(cy-6*k)}L{fmt(cx-6*k)} {fmt(cy+6*k)}" stroke="@G" stroke-width="4"/>'
        return f'<path d="{d}" stroke="@G" stroke-width="4"/>' + x
def body_full(state): return ''.join(body_part(p, state) for p in PARTS)
IBODY = [(f'body_{p}_{s}', body_part(p, s), {'healthy': 'C', 'wounded': 'D', 'damaged': 'A', 'critical': 'A', 'crippled': 'G'}[s], 'STAT') for p in PARTS for s in STATES] + \
        [(f'body_full_{s}', body_full(s), 'C', 'STAT') for s in STATES]
