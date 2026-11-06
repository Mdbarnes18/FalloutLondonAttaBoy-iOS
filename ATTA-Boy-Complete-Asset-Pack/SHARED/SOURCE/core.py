import os, io, json, struct, math, re, shutil, wave
import xml.etree.ElementTree as ET
from PIL import Image
from svgr import render_svg, shape_d, NSP, hexrgb, fmt, parse_transform
ROOT = '/home/claude/pack/out/ATTA-Boy-Complete-Asset-Pack'
REG = {}
def P(rel):
    p = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p
def reg(rel, **meta): REG[rel] = meta
def save_png(img, rel, **meta):
    img.save(P(rel), 'PNG', optimize=True); reg(rel, **meta)
def save_text(rel, text, **meta):
    with open(P(rel), 'w', encoding='utf-8', newline='\n') as f: f.write(text)
    reg(rel, **meta)
def copy_to(src, rel, **meta):
    shutil.copyfile(src, P(rel)); reg(rel, **meta)
def px(v, f): return max(1, int(v*f + 0.5))
_cache = {}
def render_px(asset, wpx, hpx):
    key = (asset['id'], wpx, hpx)
    if key not in _cache:
        ss = 4 if wpx <= 100 else 3 if wpx <= 300 else 2
        im = render_svg(asset['svg'], wpx, ss=ss)
        if im.size != (wpx, hpx): im = im.resize((wpx, hpx), Image.BOX if im.width > wpx else Image.BICUBIC)
        _cache[key] = im
    return _cache[key]
def clear_cache(): _cache.clear()
# --------- ICO (PNG-compressed frames) ---------
def make_ico(frames):
    """frames: list of RGBA images (square). Returns bytes."""
    blobs = []
    for im in frames:
        b = io.BytesIO(); im.save(b, 'PNG', optimize=True); blobs.append(b.getvalue())
    out = struct.pack('<HHH', 0, 1, len(frames)); off = 6 + 16*len(frames); ent = b''
    for im, data in zip(frames, blobs):
        w = im.width; ent += struct.pack('<BBBBHHII', 0 if w >= 256 else w, 0 if w >= 256 else w, 0, 0, 1, 32, len(data), off); off += len(data)
    return out + ent + b''.join(blobs)
# --------- Android 9-patch ---------
def nine_patch(img, l, t, r, b):
    w, h = img.size; out = Image.new('RGBA', (w+2, h+2), (0, 0, 0, 0)); out.paste(img, (1, 1))
    px_ = out.load()
    x0, x1 = (1 + l, 1 + w - r) if (l or r) else (1, 1 + w)
    y0, y1 = (1 + t, 1 + h - b) if (t or b) else (1, 1 + h)
    for x in range(x0, max(x1, x0+1)): px_[x, 0] = (0, 0, 0, 255)
    for y in range(y0, max(y1, y0+1)): px_[0, y] = (0, 0, 0, 255)
    return out
# --------- Android VectorDrawable ---------
def svg_to_vector(svg_text):
    root = ET.fromstring(svg_text); vb = [float(v) for v in re.split(r'[\s,]+', root.get('viewBox').strip())]
    paths = []
    base = dict(fill='#000000', stroke=None, sw=1.0, fo=1.0, so=1.0, op=1.0, cap='round', join='round')
    def argb(c): return '#FF' + c.lstrip('#').upper()
    def walk(el, st):
        st = dict(st)
        for k, key in (('fill', 'fill'), ('stroke', 'stroke')):
            if el.get(k) is not None: st[key] = el.get(k)
        for k, key in (('stroke-width', 'sw'), ('fill-opacity', 'fo'), ('stroke-opacity', 'so')):
            if el.get(k) is not None: st[key] = float(el.get(k))
        if el.get('opacity') is not None: st['op'] *= float(el.get('opacity'))
        if el.get('stroke-linecap'): st['cap'] = el.get('stroke-linecap')
        if el.get('stroke-linejoin'): st['join'] = el.get('stroke-linejoin')
        if el.get('transform'): raise ValueError('transform not supported in vector conversion')
        tag = el.tag.replace(NSP, '')
        if tag in ('svg', 'g'):
            for ch in el: walk(ch, st)
            return
        d = shape_d(el)
        if d is None: return
        a = [f'android:pathData="{d}"']
        if st['fill'] not in (None, 'none'):
            a.append(f'android:fillColor="{argb(st["fill"])}"')
            if st['fo']*st['op'] < 1: a.append(f'android:fillAlpha="{fmt(st["fo"]*st["op"])}"')
            a.append('android:fillType="evenOdd"')
        if st['stroke'] not in (None, 'none'):
            a.append(f'android:strokeColor="{argb(st["stroke"])}"'); a.append(f'android:strokeWidth="{fmt(st["sw"])}"')
            a.append(f'android:strokeLineCap="{st["cap"]}"'); a.append(f'android:strokeLineJoin="{st["join"]}"')
            if st['so']*st['op'] < 1: a.append(f'android:strokeAlpha="{fmt(st["so"]*st["op"])}"')
        paths.append('    <path\n        ' + '\n        '.join(a) + '/>')
    walk(root, base)
    return ('<?xml version="1.0" encoding="utf-8"?>\n<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
            f'    android:width="{fmt(vb[2])}dp"\n    android:height="{fmt(vb[3])}dp"\n    android:viewportWidth="{fmt(vb[2])}"\n    android:viewportHeight="{fmt(vb[3])}">\n'
            + '\n'.join(paths) + '\n</vector>\n')
# --------- iOS Contents.json ---------
def imageset_json(name, template, sliced=None, scales=('1x', '2x', '3x'), sizes=None):
    imgs = []
    for s in scales:
        fn = f'{name}.png' if s == '1x' else f'{name}@{s}.png'
        e = {'idiom': 'universal', 'filename': fn, 'scale': s}
        if sliced:
            l, t, r, b, w, h = sliced[s]
            mode = '3-part-horizontal' if (t == 0 and b == 0) else '3-part-vertical' if (l == 0 and r == 0) else '9-part'
            e['resizing'] = {'mode': mode, 'center': {'mode': 'stretch', 'width': max(1, w - l - r), 'height': max(1, h - t - b)},
                             'cap-insets': {'top': t, 'left': l, 'bottom': b, 'right': r}}
        imgs.append(e)
    d = {'images': imgs, 'info': {'author': 'xcode', 'version': 1}}
    if template: d['properties'] = {'template-rendering-intent': 'template'}
    return json.dumps(d, indent=2) + '\n'
XC_INFO = json.dumps({'info': {'author': 'xcode', 'version': 1}}, indent=2) + '\n'
