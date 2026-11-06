from palette import PAL, tokens
from svgr import scale_body
from icons_a import I24
from icons_b import I48, CAT, MED, IBODY
SW = {24: 1.5, 48: 2.5, 128: 5.0}
CATEGORY_BY_PREFIX = [
 ('nav_', 'Application shell / Navigation'), ('conn_', 'Connection'), ('status_', 'Status & diagnostics'),
 ('ctl_', 'Controls'), ('sel_', 'Indicators'), ('progress_', 'Indicators'), ('loading_', 'Indicators'), ('led_', 'Indicators'),
 ('act_', 'Inventory actions'), ('inv_', 'Inventory properties'), ('cat_', 'Inventory categories'),
 ('map_', 'World & navigation'), ('radio_', 'Radio'), ('data_', 'Data & diagnostics'), ('tree_', 'Data & diagnostics'),
 ('limb_', 'Body status'), ('ind_', 'Body status'), ('marker_', 'Body status'), ('body_', 'Body status'),
 ('med_', 'Medical systems'), ('special_', 'Player statistics'), ('stat_', 'Player statistics'), ('world_', 'World identity'),
]
def category_of(i):
    for p, c in CATEGORY_BY_PREFIX:
        if i.startswith(p): return c
    return 'Other'
def world_of(i):
    return {'world_london': 'Fallout: London', 'world_commonwealth': 'Fallout 4 Commonwealth'}.get(i, 'Shared')
def make_svg(vb, body, col):
    ink = PAL[col]
    inner = tokens(body)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb} {vb}" width="{vb}" height="{vb}">'
            f'<g fill="none" stroke="{ink}" stroke-width="{SW[vb]:g}" stroke-linecap="round" stroke-linejoin="round">{inner}</g></svg>')
def all_icons():
    out = []
    def add(e, vb, scale=None):
        i, body, col, screen = e[0], e[1], e[2], e[3]
        if scale: body = scale_body(body, scale)
        multi = any(t in body for t in ('@A', '@D', '@G', '@K', '@W', '#FF')) or col != 'C'
        out.append(dict(id=i, vb=vb, svg=make_svg(vb, body, col), mono=not multi, screen=screen,
                        category=category_of(i), world=world_of(i)))
    for e in I24: add(e, 24)
    for e in I48: add(e, 48)
    for e in CAT + MED: add(e, 128, 128/48)
    for e in IBODY: add(e, 128)
    return out
