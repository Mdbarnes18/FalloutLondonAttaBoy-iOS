import os, sys, json, csv, pickle, time, zipfile, wave, hashlib, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
from core import ROOT, P, reg, REG, save_png, save_text, px
from build_assets import IOS, AND, DESK, T, A
def font(sz, bold=False):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
BG = (11, 13, 10); GR = (76, 255, 127); DIM = (47, 158, 88)
def load(rel): return Image.open(os.path.join(ROOT, rel)).convert('RGBA')
def nine(img, ins, size):
    l, t, r, b = ins; w, h = img.size; W, H = size; out = Image.new('RGBA', size, (0, 0, 0, 0))
    xs = [(0, l, 0, l), (l, w-r, l, W-r), (w-r, w, W-r, W)]; ys = [(0, t, 0, t), (t, h-b, t, H-b), (h-b, h, H-b, H)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if sx1 <= sx0 or sy1 <= sy0 or dx1 <= dx0 or dy1 <= dy0: continue
            out.alpha_composite(img.crop((sx0, sy0, sx1, sy1)).resize((dx1-dx0, dy1-dy0), Image.LANCZOS), (dx0, dy0))
    return out
def icon_file(a, target):
    """Pick an exported Windows PNG for asset a at ~target px width."""
    best = None
    for s, f, d in DESK:
        wp = px(a['w'], f)
        if best is None or abs(wp - target) < abs(best[0] - target): best = (wp, f'Windows/{d}/{a["group"]}/{a["id"]}.png')
    im = load(best[1]);
    if im.width != target: im = im.resize((target, int(round(im.height*target/im.width))), Image.LANCZOS)
    return im
def sheet(items, cell, cols, title=None, label=True, bg=BG):
    pad = 16 if label else 4; head = 34 if title else 0; rows = (len(items)+cols-1)//cols
    im = Image.new('RGB', (cols*(cell+12)+12, head + rows*(cell+pad+12)+12), bg); d = ImageDraw.Draw(im)
    if title: d.text((12, 8), title, fill=GR, font=font(15, True))
    for n, (name, ic) in enumerate(items):
        x = 12 + (n % cols)*(cell+12); y = head + 12 + (n//cols)*(cell+pad+12)
        d.rectangle([x-1, y-1, x+cell, y+cell], outline=(30, 38, 28))
        if ic.width > cell or ic.height > cell: s = min(cell/ic.width, cell/ic.height); ic = ic.resize((max(1, int(ic.width*s)), max(1, int(ic.height*s))), Image.LANCZOS)
        im.paste(ic, (x + (cell-ic.width)//2, y + (cell-ic.height)//2), ic)
        if label: d.text((x, y+cell+2), name[:max(6, int(cell/6.2))], fill=(110, 135, 100), font=font(9))
    return im
def previews(assets, log):
    by = {a['id']: a for a in assets}; icons = [a for a in assets if a['kind'] == 'icon']; ui = [a for a in assets if a['kind'] == 'ui']
    meta = lambda i, d: dict(id=i, category='Preview', screen='n/a', world='Shared', platform='Shared', logical='n/a', scale='n/a', source='Generated from exported platform files', notes=d)
    # 1 overview
    groups = []; 
    for g in dict.fromkeys(a['group'] for a in icons): groups.append((g, [a for a in icons if a['group'] == g]))
    parts = [sheet([(a['id'], icon_file(a, 64)) for a in lst], 64, 18, title=f'{g}  ({len(lst)})') for g, lst in groups]
    uis = sheet([(a['id'], load(f'Windows/PNG-1x/UI/{a["id"]}.png')) for a in ui], 96, 12, title=f'UI components ({len(ui)})')
    W = max(p.width for p in parts + [uis]); H = sum(p.height for p in parts + [uis]); ov = Image.new('RGB', (W, H), BG); y = 0
    for p in parts + [uis]: ov.paste(p, (0, y)); y += p.height
    save_png(ov, 'PREVIEW/asset-overview.png', **meta('asset-overview', 'Every icon and UI component, from exported PNGs.')); log('  preview overview')
    # 2 medical
    med = [(a['id'], icon_file(a, 128)) for a in icons if a['id'].startswith('med_')]
    body = [(f'body_full_{s}', icon_file(by[f'body_full_{s}'], 128)) for s in ('healthy', 'wounded', 'damaged', 'critical', 'crippled')]
    limbs = [(a['id'], icon_file(a, 72)) for a in icons if a['id'].startswith(('limb_', 'ind_', 'marker_', 'progress_ring'))]
    parts_ = [sheet(med, 128, 6, 'Medical systems'), sheet(body, 128, 5, 'Body status - full silhouette, five states'),
              sheet([(f'{p}_{s}'.replace('body_', ''), icon_file(by[f'body_{p}_{s}'], 96)) for p in ('head', 'torso', 'arm_left', 'leg_right') for s in ('healthy', 'wounded', 'damaged', 'critical', 'crippled')], 96, 10, 'Individual parts (stack on a 128x128 canvas)', label=False),
              sheet(limbs, 72, 12, 'Condition glyphs, indicators, progress rings')]
    W = max(p.width for p in parts_); im = Image.new('RGB', (W, sum(p.height for p in parts_)), BG); y = 0
    for p in parts_: im.paste(p, (0, y)); y += p.height
    save_png(im, 'PREVIEW/medical-preview.png', **meta('medical-preview', 'Medical, body-status and indicator assets.'))
    # 3 inventory
    cats = [(a['id'], icon_file(a, 128)) for a in icons if a['id'].startswith('cat_')]
    acts = [(a['id'], icon_file(a, 72)) for a in icons if a['id'].startswith(('act_', 'inv_', 'special_', 'stat_'))]
    parts_ = [sheet(cats, 128, 6, 'Inventory categories (128 grid)'), sheet(acts, 72, 12, 'Inventory actions / properties / SPECIAL / statistics')]
    W = max(p.width for p in parts_); im = Image.new('RGB', (W, sum(p.height for p in parts_)), BG); y = 0
    for p in parts_: im.paste(p, (0, y)); y += p.height
    save_png(im, 'PREVIEW/inventory-preview.png', **meta('inventory-preview', 'Inventory category icons, actions and statistics.'))
    # 4 interface composition (built only from exported assets)
    Wd, Hd = 1280, 800; base = load('Windows/TEXTURES/Backgrounds/bg_terminal_clean_1920x1080.png').resize((Wd, Hd), Image.LANCZOS)
    canvas = base.copy(); d = ImageDraw.Draw(canvas); fb = font(14, True); fs = font(11)
    sl = lambda i: json.load(open(os.path.join(ROOT, 'Windows/nine_slice.json')))['assets'][i]['insets']
    def put9(i, x, y, w, h, scale=2):
        ins = sl(i); img = load(f'Windows/PNG-2x/UI/{i}.png'); n = nine(img, tuple(int(ins[k]*scale) for k in ('left', 'top', 'right', 'bottom')), (w*2, h*2)).resize((w, h), Image.LANCZOS)
        canvas.alpha_composite(n, (x, y))
    put9('frame_screen_worn', 20, 20, 1240, 760)
    tabs = [('STAT', 'nav_stat'), ('INV', 'nav_inventory'), ('DATA', 'nav_data'), ('MAP', 'nav_map'), ('RADIO', 'nav_radio')]
    for k, (t, ic) in enumerate(tabs):
        x = 90 + k*150; put9('tab_active' if k == 0 else 'tab_inactive', x, 70, 140, 44)
        canvas.alpha_composite(icon_file(by[ic], 24), (x+14, 80)); d.text((x+48, 83), t, fill=GR if k == 0 else DIM, font=fb)
    put9('panel_clean', 90, 130, 330, 560)
    d.text((112, 148), 'CONDITION', fill=GR, font=fb); canvas.alpha_composite(icon_file(by['body_full_wounded'], 190), (150, 175))
    for k, i in enumerate(['limb_ok', 'limb_wounded', 'limb_damaged', 'limb_critical', 'limb_crippled']): canvas.alpha_composite(icon_file(by[i], 48), (112+k*58, 380))
    for k, (i, v) in enumerate([('stat_health', 0.82), ('stat_action_points', 0.6), ('stat_radiation', 0.15)]):
        y = 460 + k*60; canvas.alpha_composite(icon_file(by[i], 36), (112, y)); put9('progress_bar_track', 160, y+8, 240, 20)
        put9('progress_bar_fill', 160, y+8, int(240*v), 20)
    put9('panel_worn', 440, 130, 380, 560); d.text((462, 148), 'STATISTICS', fill=GR, font=fb)
    for k, i in enumerate(['special_strength', 'special_perception', 'special_endurance', 'special_charisma', 'special_intelligence', 'special_agility', 'special_luck']):
        y = 182 + k*64
        if k == 2: put9('selection_highlight', 456, y-6, 350, 56)
        canvas.alpha_composite(icon_file(by[i], 48), (466, y)); d.text((536, y+14), i.replace('special_', '').upper(), fill=GR, font=fb)
        d.text((740, y+14), str(5 + (k*3) % 6), fill=GR, font=fb)
    put9('panel_inset', 840, 130, 380, 270); d.text((862, 146), 'INVENTORY', fill=GR, font=fb)
    for k, i in enumerate(['cat_weapons', 'cat_apparel', 'cat_armor', 'cat_aid', 'cat_food', 'cat_drink', 'cat_misc', 'cat_ammo']):
        canvas.alpha_composite(icon_file(by[i], 72), (856 + (k % 4)*88, 176 + (k//4)*96))
    put9('panel_warning', 840, 420, 380, 140); d.text((862, 452), 'WARNING PANEL', fill=(227, 161, 47), font=fb)
    canvas.alpha_composite(icon_file(by['status_warning'], 36), (1160, 440)); canvas.alpha_composite(icon_file(by['med_quick_aid'], 64), (862, 478))
    for k, b in enumerate(['button_normal', 'button_pressed', 'button_selected', 'button_disabled']): put9(b, 850+(k % 2)*180, 580+(k//2)*50, 170, 44)
    put9('panel_notification', 90, 706, 330, 64); canvas.alpha_composite(icon_file(by['conn_connected'], 36), (130, 720)); d.text((176, 728), 'CONNECTED', fill=GR, font=fb)
    for k, i in enumerate(['led_green', 'led_amber', 'led_off', 'led_alert']): canvas.alpha_composite(icon_file(by[i], 36), (440+k*44, 716))
    canvas.alpha_composite(icon_file(by['toggle_on'] if 'toggle_on' in by else by['led_green'], 48), (640, 720))
    for ov in ('overlay_scanlines_fine', 'overlay_vignette', 'overlay_glass_reflection'):
        o = load(f'Windows/TEXTURES/Overlays/{ov}.png').resize((Wd, Hd), Image.LANCZOS); canvas.alpha_composite(o)
    save_png(canvas.convert('RGB'), 'PREVIEW/interface-preview.png', **meta('interface-preview', 'Composite built only from exported assets (nine-sliced panels, tabs, bars) with CRT overlays.'))
    # 5 platform previews (actual exported files)
    samples = [('nav_stat', 24), ('special_luck', 48), ('med_stimpak', 128), ('button_normal', None), ('panel_clean', None)]
    spec = {'iOS': [(s, d) for s, f, d in IOS], 'Android': [(s, d) for s, f, d in AND], 'Windows': [(s, d) for s, f, d in DESK], 'Linux': [(s, d) for s, f, d in DESK]}
    for plat, scales in spec.items():
        colw = 150 if plat != 'Android' else 130; rows = []; H = 40; W = 20 + colw*len(scales)*0 + 640
        canvas = Image.new('RGB', (1500 if plat == 'Android' else 1300, 760), BG); dd = ImageDraw.Draw(canvas); dd.text((14, 10), f'{plat} export check: real files from {plat}/ at each scale', fill=GR, font=font(15, True)); y = 44
        for i, _ in samples:
            a = by[i]; x = 14; dd.text((x, y), i, fill=GR, font=font(11, True)); x0 = x; y2 = y + 18; rowh = 0
            for s, d in scales:
                if plat == 'Android': fn = f'Android/{d}/{i}.{"9." if a["slice"] else ""}png'
                elif plat == 'iOS': fn = f'iOS/{d}/{a["group"]}/{i}{"" if s == "1x" else "@" + s}.png'
                else: fn = f'{plat}/{d}/{a["group"]}/{i}.png'
                im = load(fn)
                if plat == 'Android' and a['slice']: im = im.crop((1, 1, im.width-1, im.height-1))
                if im.width > 260 or im.height > 140: s2 = min(260/im.width, 140/im.height); shown = im.resize((int(im.width*s2), int(im.height*s2)), Image.LANCZOS)
                else: shown = im
                cw = max(shown.width, 110) + 14
                if x0 + cw > canvas.width - 10: break
                dd.rectangle([x0-1, y2-1, x0+shown.width, y2+shown.height], outline=(30, 38, 28)); canvas.paste(shown, (x0, y2), shown)
                dd.text((x0, y2+shown.height+3), f'{s} {im.width}x{im.height}', fill=(110, 135, 100), font=font(9)); x0 += cw; rowh = max(rowh, shown.height)
            y = y2 + rowh + 26
        save_png(canvas.crop((0, 0, canvas.width, min(canvas.height, y+10))), f'PREVIEW/platform-previews/{plat.lower()}.png', **meta(f'{plat.lower()}-preview', f'{plat} exports at every scale (native pixel size, large assets shrunk to fit).'))
    log('  previews done')
