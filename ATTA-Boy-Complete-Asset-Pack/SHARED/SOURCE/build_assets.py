import os, sys, json, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from core import *
from assemble import all_icons
from ui_def import UI
from palette import tokens, PAL
import textures as T, audio as A

GROUP_PREFIX = [('nav_', 'Navigation'), ('conn_', 'Connection'), ('status_', 'Status'), ('ctl_', 'Controls'), ('sel_', 'Indicators'),
    ('progress_ring', 'Indicators'), ('loading_', 'Indicators'), ('led_', 'Indicators'), ('act_', 'Inventory'), ('inv_', 'Inventory'),
    ('cat_', 'Categories'), ('map_', 'World'), ('radio_', 'Radio'), ('data_', 'Data'), ('tree_', 'Data'), ('limb_', 'Body'), ('ind_', 'Body'),
    ('marker_', 'Body'), ('body_', 'Body'), ('med_', 'Medical'), ('special_', 'Stats'), ('stat_', 'Stats'), ('world_', 'Identity')]
UI_CAT = [('panel_', 'Panels, frames & dividers'), ('frame_', 'Panels, frames & dividers'), ('divider_', 'Panels, frames & dividers'), ('corner_', 'Panels, frames & dividers'),
    ('band_', 'Panels, frames & dividers'), ('label_', 'Panels, frames & dividers'), ('button_', 'Buttons & tabs'), ('tab_', 'Buttons & tabs'),
    ('selection_', 'Buttons & tabs'), ('toggle_', 'Toggles & mechanical controls'), ('checkbox_', 'Toggles & mechanical controls'), ('radio_', 'Toggles & mechanical controls'),
    ('switch_', 'Toggles & mechanical controls'), ('knob_', 'Toggles & mechanical controls'), ('progress_bar', 'Progress & scrollbars'), ('scrollbar_', 'Progress & scrollbars'),
    ('rivet_', 'Decor'), ('screw_', 'Decor'), ('badge_', 'Decor')]
def group_of(i, kind):
    if kind == 'ui': return 'UI'
    for p, g in GROUP_PREFIX:
        if i.startswith(p): return g
    return 'Misc'
def ui_category(i):
    for p, c in UI_CAT:
        if i.startswith(p): return c
    return 'UI'
def build_asset_list():
    out = []
    for ic in all_icons():
        ic = dict(ic); ic['kind'] = 'icon'; ic['w'] = ic['h'] = ic['vb']; ic['slice'] = None; ic['group'] = group_of(ic['id'], 'icon'); out.append(ic)
    for u in UI:
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {u["w"]} {u["h"]}" width="{u["w"]}" height="{u["h"]}">'
               f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{tokens(u["body"])}</g></svg>')
        out.append(dict(id=u['id'], kind='ui', w=u['w'], h=u['h'], svg=svg, mono=False, screen=u['screen'], world=u['world'], category=ui_category(u['id']),
                        slice=u['slice'], group='UI', note=u['note']))
    return out
IOS = [('1x', 1, 'PNG-1x'), ('2x', 2, 'PNG-2x'), ('3x', 3, 'PNG-3x')]
AND = [('mdpi', 1, 'drawable-mdpi'), ('hdpi', 1.5, 'drawable-hdpi'), ('xhdpi', 2, 'drawable-xhdpi'), ('xxhdpi', 3, 'drawable-xxhdpi'), ('xxxhdpi', 4, 'drawable-xxxhdpi')]
DESK = [('1x', 1, 'PNG-1x'), ('1.5x', 1.5, 'PNG-1.5x'), ('2x', 2, 'PNG-2x'), ('3x', 3, 'PNG-3x')]
def common(a): return dict(id=a['id'], category=a['category'], screen=a['screen'], world=a['world'])

def export_asset(a):
    g, i, w, h = a['group'], a['id'], a['w'], a['h']
    svg_rel = f'SHARED/SVG/{g}/{i}.svg'
    save_text(svg_rel, a['svg'] + '\n', platform='Shared', logical=f'{w}x{h}', scale='vector', source='(master)', notes=a.get('note', ''), **common(a))
    for plat in ('iOS', 'Android', 'Windows', 'Linux'):
        save_text(f'{plat}/SVG/{g}/{i}.svg', a['svg'] + '\n', platform=plat, logical=f'{w}x{h}', scale='vector', source=svg_rel, notes='Copy of shared master', **common(a))
    sl = a['slice']
    # ---- iOS ----
    ims = {}; slc = {}
    for s, f, d in IOS:
        wp, hp = px(w, f), px(h, f); im = render_px(a, wp, hp); fn = f'{i}.png' if s == '1x' else f'{i}@{s}.png'
        ims[s] = im
        meta = dict(platform='iOS', logical=f'{w}x{h} pt', scale=s, source=svg_rel, notes=a.get('note', ''), **common(a))
        save_png(im, f'iOS/{d}/{g}/{fn}', **meta); save_png(im, f'iOS/Assets.xcassets/{g}/{i}.imageset/{fn}', **meta)
        if sl: slc[s] = (px(sl[0], f), px(sl[1], f), px(sl[2], f), px(sl[3], f), wp, hp)
    template = a['kind'] == 'icon' and a['mono']
    save_text(f'iOS/Assets.xcassets/{g}/{i}.imageset/Contents.json', imageset_json(i, template, slc if sl else None), platform='iOS', scale='n/a', source=svg_rel,
              notes='Template rendering (tint in app)' if template else 'Original rendering' + (' + slicing' if sl else ''), **common(a))
    # ---- Android ----
    for dn, f, d in AND:
        wp, hp = px(w, f), px(h, f); im = render_px(a, wp, hp)
        meta = dict(platform='Android', logical=f'{w}x{h} dp', scale=dn, source=svg_rel, notes=a.get('note', ''), **common(a))
        if sl:
            n = nine_patch(im, px(sl[0], f), px(sl[1], f), px(sl[2], f), px(sl[3], f)); save_png(n, f'Android/{d}/{i}.9.png', **{**meta, 'notes': '9-patch (stretch region in 1px border)'})
        else: save_png(im, f'Android/{d}/{i}.png', **meta)
    save_text(f'Android/vector-drawable/{i}.xml', svg_to_vector(a['svg']), platform='Android', logical=f'{w}x{h} dp', scale='vector', source=svg_rel, notes='VectorDrawable (alternative to PNG)', **common(a))
    # ---- Windows / Linux ----
    for plat in ('Windows', 'Linux'):
        for s, f, d in DESK:
            wp, hp = px(w, f), px(h, f); im = render_px(a, wp, hp)
            save_png(im, f'{plat}/{d}/{g}/{i}.png', platform=plat, logical=f'{w}x{h} px', scale=s, source=svg_rel, notes=a.get('note', ''), **common(a))
def write_nine_slice(assets):
    d = {}
    for a in assets:
        if a['slice']:
            l, t, r, b = a['slice']; d[a['id']] = {'logicalSize': [a['w'], a['h']], 'insets': {'left': l, 'top': t, 'right': r, 'bottom': b}, 'mode': ('horizontal-3-part' if not (t or b) else 'vertical-3-part' if not (l or r) else '9-part')}
    txt = json.dumps({'note': 'Insets are in logical units (pt / dp / px). Multiply by the export scale for pixel insets.', 'assets': d}, indent=2) + '\n'
    for rel in ('SHARED/SOURCE/nine_slice.json', 'Windows/nine_slice.json', 'Linux/nine_slice.json'):
        save_text(rel, txt, platform='Shared' if rel.startswith('SHARED') else rel.split('/')[0], scale='n/a', category='Nine-slice data', screen='All', world='Shared', id='nine_slice', source='ui_def.py', notes='Nine-slice guidance')
def wrap_resize(im, size):
    w, h = im.size; big = Image.new(im.mode, (w*3, h*3))
    for ox in range(3):
        for oy in range(3): big.paste(im, (ox*w, oy*h))
    big = big.resize((size*3, size*3), Image.LANCZOS); return big.crop((size, size, size*2, size*2))
def tex_meta(i, d): return dict(id=i, category='Textures', screen='All', world='Shared', source='SOURCE/textures.py (procedural)', notes=d)
def stage_tex(log):
    for i, f, d in T.SEAMLESS:
        t2 = f(512)
        save_png(t2, f'SHARED/TEXTURES/Seamless/{i}.png', platform='Shared', logical='512x512 px', scale='1x', **tex_meta(i, d))
        for plat in ('Windows', 'Linux'): save_png(t2, f'{plat}/TEXTURES/Seamless/{i}.png', platform=plat, logical='512x512 px', scale='1x', **tex_meta(i, d))
        save_png(t2, f'Android/drawable-nodpi/{i}.png', platform='Android', logical='512x512 px', scale='nodpi', **tex_meta(i, d + ' Tile with the matching tile_* XML.'))
        t1 = wrap_resize(t2, 256); t3 = wrap_resize(t2, 768)
        for s_, im, fn in (('1x', t1, f'{i}.png'), ('2x', t2, f'{i}@2x.png'), ('3x', t3, f'{i}@3x.png')):
            save_png(im, f'iOS/Assets.xcassets/Textures/{i}.imageset/{fn}', platform='iOS', logical='256x256 pt', scale=s_, **tex_meta(i, d))
        save_text(f'iOS/Assets.xcassets/Textures/{i}.imageset/Contents.json', imageset_json(i, False), platform='iOS', scale='n/a', **tex_meta(i, 'Seamless tile; draw as pattern'))
        log(f'  seamless {i}')
    for i, f, d, a in T.OVERLAYS:
        im = f(); meta = lambda p, lg, sc: dict(platform=p, logical=lg, scale=sc, **tex_meta(i, d))
        save_png(im, f'SHARED/TEXTURES/Overlays/{i}.png', **meta('Shared', '1024x1024 px', '1x'))
        for plat in ('Windows', 'Linux'): save_png(im, f'{plat}/TEXTURES/Overlays/{i}.png', **meta(plat, '1024x1024 px', '1x'))
        save_png(im, f'Android/drawable-nodpi/{i}.png', **meta('Android', '1024x1024 px', 'nodpi'))
        save_png(im, f'iOS/Assets.xcassets/Textures/{i}.imageset/{i}@2x.png', **meta('iOS', '512x512 pt', '2x'))
        c = json.loads(imageset_json(i, False, scales=('2x',))); save_text(f'iOS/Assets.xcassets/Textures/{i}.imageset/Contents.json', json.dumps(c, indent=2) + '\n', platform='iOS', scale='n/a', **tex_meta(i, 'Overlay, 2x only'))
        log(f'  overlay {i}')
def stage_bg(k, log):
    i, f, d = T.BACKGROUNDS[k]
    for (w, h, tag) in ((1920, 1080, 'standard'), (2560, 1440, 'highres')):
        im = f(w, h); name = f'{i}_{w}x{h}'
        for plat in ('Shared', 'Windows', 'Linux'):
            rel = f'{"SHARED" if plat == "Shared" else plat}/TEXTURES/Backgrounds/{name}.png'
            im.save(P(rel), 'PNG', optimize=True, compress_level=9); reg(rel, platform=plat, logical=f'{w}x{h} px', scale='1x', **tex_meta(name, d + f' ({tag}).'))
        del im; log(f'  background {name}')
MOBILE = (('bg_terminal_mobile', lambda w, h: T.bg_terminal(w, h, False), 'Portrait phone background, clean CRT.'), ('bg_industrial_mobile', T.bg_industrial, 'Portrait phone background, olive riveted panels.'))
def stage_mobile(k, log):
    i, fn, d = MOBILE[k]; big = fn(1440, 3200); sizes = {'xxxhdpi': (1440, 3200), 'xxhdpi': (1080, 2400), 'xhdpi': (720, 1600), 'hdpi': (540, 1200), 'mdpi': (360, 800)}
    for dn, (w, h) in sizes.items():
        im = big if dn == 'xxxhdpi' else big.resize((w, h), Image.LANCZOS)
        rel = f'Android/drawable-{dn}/{i}.png'; im.save(P(rel), 'PNG', optimize=True, compress_level=9); reg(rel, platform='Android', logical='360x800 dp', scale=dn, **tex_meta(i, d))
    for s_, f, (w, h) in (('1x', 1, (390, 844)), ('2x', 2, (780, 1688)), ('3x', 3, (1170, 2532))):
        im = big.resize((w, h), Image.LANCZOS); fnm = f'{i}.png' if s_ == '1x' else f'{i}@{s_}.png'
        rel = f'iOS/Assets.xcassets/Textures/{i}.imageset/{fnm}'; im.save(P(rel), 'PNG', optimize=True, compress_level=9); reg(rel, platform='iOS', logical='390x844 pt', scale=s_, **tex_meta(i, d))
    save_text(f'iOS/Assets.xcassets/Textures/{i}.imageset/Contents.json', imageset_json(i, False), platform='iOS', scale='n/a', **tex_meta(i, d))
    log(f'  mobile {i}')
def write_audio(log):
    for n, f, cat, d in A.SOUNDS:
        x = f(); tmp = f'/tmp/_snd_{n}.wav'; A.write_wav(tmp, x)
        meta = dict(id=n, category=f'Audio / {cat}', screen='All', world='Shared', logical=f'{len(x)/A.SR:.2f} s', scale='n/a', source='SOURCE/audio.py (synthesized)', notes=d)
        copy_to(tmp, f'SHARED/AUDIO/{n}.wav', platform='Shared', **meta)
        for plat, rel in (('iOS', f'iOS/Sounds/{n}.wav'), ('Android', f'Android/raw/{n}.wav'), ('Windows', f'Windows/AUDIO/{n}.wav'), ('Linux', f'Linux/AUDIO/{n}.wav')):
            copy_to(tmp, rel, platform=plat, **meta)
    log('  audio done')
def write_android_xml(assets):
    sel = lambda items, default: ('<?xml version="1.0" encoding="utf-8"?>\n<selector xmlns:android="http://schemas.android.com/apk/res/android">\n' + ''.join(f'    <item {a} android:drawable="@drawable/{d}"/>\n' for a, d in items) + f'    <item android:drawable="@drawable/{default}"/>\n</selector>\n')
    files = {'selector_button': sel([('android:state_enabled="false"', 'button_disabled'), ('android:state_pressed="true"', 'button_pressed'), ('android:state_selected="true"', 'button_selected')], 'button_normal'),
             'selector_toggle': sel([('android:state_checked="true"', 'toggle_on')], 'toggle_off'),
             'selector_checkbox': sel([('android:state_checked="true"', 'checkbox_on')], 'checkbox_off'),
             'selector_radio': sel([('android:state_checked="true"', 'radio_on')], 'radio_off'),
             'selector_tab': sel([('android:state_selected="true"', 'tab_active')], 'tab_inactive')}
    for n, i, _d in [(t[0], t[0], t[2]) for t in T.SEAMLESS]:
        files['tile_' + n.replace('tex_', '')] = ('<?xml version="1.0" encoding="utf-8"?>\n<bitmap xmlns:android="http://schemas.android.com/apk/res/android"\n'
            f'    android:src="@drawable/{n}"\n    android:tileMode="repeat"\n    android:dither="true" />\n')
    for n, x in files.items():
        save_text(f'Android/drawable/{n}.xml', x, platform='Android', id=n, category='Android resource XML', screen='All', world='Shared', logical='n/a', scale='n/a', source='build_assets.py', notes='State-list / tiled-bitmap drawable referencing exported PNGs')
TRAY = [('tray_connected', 'conn_connected'), ('tray_disconnected', 'conn_disconnected'), ('tray_connecting', 'conn_connecting'), ('tray_warning', 'status_warning'), ('tray_error', 'status_error'), ('tray_ok', 'status_ok')]
def write_desktop_extras(assets):
    by = {a['id']: a for a in assets}
    for n, src in TRAY:
        a = by[src]; frames = [render_px(a, s, s) for s in (16, 24, 32, 48)]
        rel = f'Windows/TrayIcons/{n}.ico'
        with open(P(rel), 'wb') as f: f.write(make_ico(frames))
        reg(rel, id=n, category='Tray icons', screen='System tray', world='Shared', platform='Windows', logical='16/24/32/48 px', scale='multi', source=f'SHARED/SVG/{a["group"]}/{src}.svg', notes='ICO with PNG frames')
    for n, src in TRAY:
        a = by[src]; svg = re.sub(r'#(?:[0-9A-Fa-f]{6})', '#BEBEBE', a['svg']); name = n.replace('tray_', 'atta-boy-') + '-symbolic'
        save_text(f'Linux/DesktopResources/icons/hicolor/symbolic/status/{name}.svg', svg + '\n', id=name, category='Tray icons', screen='System tray', world='Shared', platform='Linux', logical=f'{a["w"]}x{a["h"]}', scale='vector', source=f'SHARED/SVG/{a["group"]}/{src}.svg', notes='Symbolic status icon (GTK/KDE recolours it)')
        for s in (16, 22, 24, 32, 48):
            im = render_svg(svg, s, ss=4); save_png(im, f'Linux/DesktopResources/icons/hicolor/{s}x{s}/status/{name}.png', id=name, category='Tray icons', screen='System tray', world='Shared', platform='Linux', logical=f'{s}x{s} px', scale='1x', source=f'SHARED/SVG/{a["group"]}/{src}.svg', notes='Freedesktop hicolor size')
def stage_icons(log=print):
    t0 = time.time(); assets = build_asset_list(); log(f'{len(assets)} assets')
    if os.path.exists(ROOT): shutil.rmtree(ROOT)
    os.makedirs(ROOT)
    for n, a in enumerate(assets):
        export_asset(a)
        if n % 25 == 0: log(f'  exported {n}/{len(assets)}  t={time.time()-t0:.0f}s'); clear_cache()
    clear_cache(); write_nine_slice(assets); write_android_xml(assets); write_desktop_extras(assets)
    save_text('iOS/Assets.xcassets/Contents.json', XC_INFO, id='xcassets', category='Catalog', screen='n/a', world='Shared', platform='iOS', scale='n/a', source='build_assets.py', notes='Catalog root')
    for g in sorted({a['group'] for a in assets} | {'Textures'}):
        save_text(f'iOS/Assets.xcassets/{g}/Contents.json', XC_INFO, id=f'xcassets_{g}', category='Catalog', screen='n/a', world='Shared', platform='iOS', scale='n/a', source='build_assets.py', notes='Group folder')
    import pickle; pickle.dump(assets, open('/tmp/assets.pkl', 'wb'))
if __name__ == '__main__':
    st = sys.argv[1]; arg = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    {'icons': lambda: stage_icons(print), 'tex': lambda: stage_tex(print), 'bg': lambda: stage_bg(arg, print), 'mobile': lambda: stage_mobile(arg, print), 'audio': lambda: write_audio(print)}[st]()
    json.dump(REG, open(f'/tmp/reg_{st}{arg}.json', 'w')); print('stage', st, arg, 'ok', len(REG), 'files')
