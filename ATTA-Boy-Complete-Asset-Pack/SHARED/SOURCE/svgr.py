"""Minimal SVG-subset rasteriser + helpers (no external deps beyond Pillow).
Supports: svg/g/path/circle/ellipse/rect/line/polyline/polygon, fill, stroke, stroke-width,
fill-opacity, stroke-opacity, opacity, transform (translate/scale/rotate/matrix).
All fills are even-odd. Strokes use round joins; caps round (default) or butt.
Path commands: M L H V C S Q T A Z (abs+rel). Author arc flags separated by spaces."""
import re, math
import xml.etree.ElementTree as ET
ET.register_namespace('', 'http://www.w3.org/2000/svg')
from PIL import Image, ImageDraw, ImageChops

TOK = re.compile(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')
NSP = '{http://www.w3.org/2000/svg}'

def fmt(v):
    s = f'{v:.3f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

# ---------- matrices ----------
IDENT = (1, 0, 0, 1, 0, 0)
def mmul(A, B):
    return (A[0]*B[0]+A[2]*B[1], A[1]*B[0]+A[3]*B[1], A[0]*B[2]+A[2]*B[3], A[1]*B[2]+A[3]*B[3],
            A[0]*B[4]+A[2]*B[5]+A[4], A[1]*B[4]+A[3]*B[5]+A[5])
def parse_transform(s):
    m = IDENT
    for name, args in re.findall(r'(\w+)\s*\(([^)]*)\)', s or ''):
        a = [float(x) for x in re.split(r'[\s,]+', args.strip()) if x]
        if name == 'translate': t = (1, 0, 0, 1, a[0], a[1] if len(a) > 1 else 0)
        elif name == 'scale': t = (a[0], 0, 0, a[1] if len(a) > 1 else a[0], 0, 0)
        elif name == 'rotate':
            r = math.radians(a[0]); c, s_ = math.cos(r), math.sin(r)
            t = (c, s_, -s_, c, 0, 0)
            if len(a) == 3:
                t = mmul(mmul((1, 0, 0, 1, a[1], a[2]), t), (1, 0, 0, 1, -a[1], -a[2]))
        elif name == 'matrix': t = tuple(a)
        else: raise ValueError('unsupported transform ' + name)
        m = mmul(m, t)
    return m
def apply(m, x, y): return (m[0]*x+m[2]*y+m[4], m[1]*x+m[3]*y+m[5])

# ---------- path flattening ----------
def _arc(x1, y1, rx, ry, phi, fa, fs, x2, y2, step_deg):
    if (x1, y1) == (x2, y2): return []
    rx, ry = abs(rx), abs(ry)
    if rx == 0 or ry == 0: return [(x2, y2)]
    ph = math.radians(phi); cp, sp = math.cos(ph), math.sin(ph)
    dx, dy = (x1-x2)/2, (y1-y2)/2
    x1p, y1p = cp*dx+sp*dy, -sp*dx+cp*dy
    lam = x1p**2/rx**2 + y1p**2/ry**2
    if lam > 1: rx *= math.sqrt(lam); ry *= math.sqrt(lam)
    num = rx**2*ry**2 - rx**2*y1p**2 - ry**2*x1p**2
    den = rx**2*y1p**2 + ry**2*x1p**2
    co = math.sqrt(max(0, num/den)) if den else 0
    if fa == fs: co = -co
    cxp, cyp = co*rx*y1p/ry, -co*ry*x1p/rx
    cx, cy = cp*cxp - sp*cyp + (x1+x2)/2, sp*cxp + cp*cyp + (y1+y2)/2
    def ang(ux, uy, vx, vy):
        a = math.atan2(ux*vy-uy*vx, ux*vx+uy*vy); return a
    t1 = ang(1, 0, (x1p-cxp)/rx, (y1p-cyp)/ry)
    dt = ang((x1p-cxp)/rx, (y1p-cyp)/ry, (-x1p-cxp)/rx, (-y1p-cyp)/ry)
    if not fs and dt > 0: dt -= 2*math.pi
    elif fs and dt < 0: dt += 2*math.pi
    n = max(4, int(abs(math.degrees(dt))/step_deg)+1)
    pts = []
    for i in range(1, n+1):
        t = t1 + dt*i/n
        ex, ey = rx*math.cos(t), ry*math.sin(t)
        pts.append((cp*ex - sp*ey + cx, sp*ex + cp*ey + cy))
    pts[-1] = (x2, y2)
    return pts

def _bez(p0, pts, n):
    out = []
    for i in range(1, n+1):
        t = i/n; u = 1-t
        if len(pts) == 2:   # quadratic: pts = [c, p1]
            c, p1 = pts
            out.append((u*u*p0[0]+2*u*t*c[0]+t*t*p1[0], u*u*p0[1]+2*u*t*c[1]+t*t*p1[1]))
        else:
            c1, c2, p1 = pts
            out.append((u**3*p0[0]+3*u*u*t*c1[0]+3*u*t*t*c2[0]+t**3*p1[0],
                        u**3*p0[1]+3*u*u*t*c1[1]+3*u*t*t*c2[1]+t**3*p1[1]))
    return out

def parse_path(d, scale=1.0):
    """-> list of (points, closed) in user units."""
    toks = TOK.findall(d); i = 0; cmd = None
    x = y = sx = sy = 0.0; subs = []; cur = None; lastc = None; lastq = None
    def nseg(pts):
        L = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))*scale
        return max(8, min(96, int(L/2.5)))
    def num():
        nonlocal i; v = float(toks[i]); i += 1; return v
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd in 'Zz':
                if cur: subs.append((cur, True)); cur = None
                x, y = sx, sy; lastc = lastq = None
                continue
        rel = cmd.islower(); C = cmd.upper(); ox, oy = (x, y) if rel else (0, 0)
        if C == 'M':
            if cur and len(cur) > 1: subs.append((cur, False))
            x, y = ox+num(), oy+num(); sx, sy = x, y; cur = [(x, y)]
            cmd = 'l' if rel else 'L'; lastc = lastq = None
        elif C == 'L':
            x, y = ox+num(), oy+num(); cur.append((x, y)); lastc = lastq = None
        elif C == 'H':
            x = (x if rel else 0)+num(); cur.append((x, y)); lastc = lastq = None
        elif C == 'V':
            y = (y if rel else 0)+num(); cur.append((x, y)); lastc = lastq = None
        elif C in 'CS':
            if C == 'C': c1 = (ox+num(), oy+num())
            else: c1 = (2*x-lastc[0], 2*y-lastc[1]) if lastc else (x, y)
            c2 = (ox+num(), oy+num()); p1 = (ox+num(), oy+num())
            cur += _bez((x, y), [c1, c2, p1], nseg([(x, y), c1, c2, p1])); lastc = c2; lastq = None; x, y = p1
        elif C in 'QT':
            if C == 'Q': c = (ox+num(), oy+num())
            else: c = (2*x-lastq[0], 2*y-lastq[1]) if lastq else (x, y)
            p1 = (ox+num(), oy+num())
            cur += _bez((x, y), [c, p1], nseg([(x, y), c, p1])); lastq = c; lastc = None; x, y = p1
        elif C == 'A':
            rx, ry, phi, fa, fs = num(), num(), num(), int(num()), int(num())
            p1 = (ox+num(), oy+num())
            rpx = max(abs(rx), abs(ry))*scale
            step = max(0.5, min(10.0, math.degrees(2*math.acos(max(0.0, 1-0.08/max(rpx, 1.0))))))
            cur += _arc(x, y, rx, ry, phi, fa, fs, p1[0], p1[1], step); x, y = p1; lastc = lastq = None
        else: raise ValueError('bad path cmd ' + cmd)
    if cur and len(cur) > 1: subs.append((cur, False))
    return subs

# ---------- shapes -> path d ----------
def shape_d(el):
    tag = el.tag.replace(NSP, ''); g = lambda k, dflt=0: float(el.get(k, dflt))
    if tag == 'path': return el.get('d')
    if tag == 'circle':
        cx, cy, r = g('cx'), g('cy'), g('r')
        return f'M{fmt(cx-r)} {fmt(cy)}A{fmt(r)} {fmt(r)} 0 1 0 {fmt(cx+r)} {fmt(cy)}A{fmt(r)} {fmt(r)} 0 1 0 {fmt(cx-r)} {fmt(cy)}Z'
    if tag == 'ellipse':
        cx, cy, rx, ry = g('cx'), g('cy'), g('rx'), g('ry')
        return f'M{fmt(cx-rx)} {fmt(cy)}A{fmt(rx)} {fmt(ry)} 0 1 0 {fmt(cx+rx)} {fmt(cy)}A{fmt(rx)} {fmt(ry)} 0 1 0 {fmt(cx-rx)} {fmt(cy)}Z'
    if tag == 'rect':
        x, y, w, h = g('x'), g('y'), g('width'), g('height')
        rx = g('rx', el.get('ry', 0)); ry = g('ry', rx) if el.get('ry') else rx
        rx, ry = min(rx, w/2), min(ry, h/2)
        if rx <= 0: return f'M{fmt(x)} {fmt(y)}H{fmt(x+w)}V{fmt(y+h)}H{fmt(x)}Z'
        return (f'M{fmt(x+rx)} {fmt(y)}H{fmt(x+w-rx)}A{fmt(rx)} {fmt(ry)} 0 0 1 {fmt(x+w)} {fmt(y+ry)}V{fmt(y+h-ry)}'
                f'A{fmt(rx)} {fmt(ry)} 0 0 1 {fmt(x+w-rx)} {fmt(y+h)}H{fmt(x+rx)}A{fmt(rx)} {fmt(ry)} 0 0 1 {fmt(x)} {fmt(y+h-ry)}'
                f'V{fmt(y+ry)}A{fmt(rx)} {fmt(ry)} 0 0 1 {fmt(x+rx)} {fmt(y)}Z')
    if tag == 'line': return f'M{el.get("x1")} {el.get("y1")}L{el.get("x2")} {el.get("y2")}'
    if tag in ('polyline', 'polygon'):
        n = [float(v) for v in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', el.get('points'))]
        d = 'M' + ' '.join(fmt(v) for v in n[:2]) + 'L' + ' '.join(fmt(v) for v in n[2:])
        return d + ('Z' if tag == 'polygon' else '')
    return None

def hexrgb(c):
    if c in (None, 'none'): return None
    c = c.lstrip('#')
    if len(c) == 3: c = ''.join(ch*2 for ch in c)
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))

# ---------- rasteriser ----------
def _composite(canvas, mask, origin, color, opacity):
    if opacity < 1: mask = mask.point(lambda v: int(v*opacity+0.5))
    layer = Image.new('RGBA', mask.size, color+(0,)); layer.putalpha(mask)
    box = (origin[0], origin[1], origin[0]+mask.size[0], origin[1]+mask.size[1])
    reg = Image.alpha_composite(canvas.crop(box), layer); canvas.paste(reg, box)

def _draw_shape(canvas, subs, st):
    W, H = canvas.size
    allp = [p for pts, _ in subs for p in pts]
    if not allp: return
    sw = st['stroke-width']*st['_sc'] if st['stroke'] else 0
    pad = sw/2 + 2
    x0 = max(0, int(min(p[0] for p in allp)-pad)); y0 = max(0, int(min(p[1] for p in allp)-pad))
    x1 = min(W, int(max(p[0] for p in allp)+pad)+1); y1 = min(H, int(max(p[1] for p in allp)+pad)+1)
    if x1 <= x0 or y1 <= y0: return
    bw, bh = x1-x0, y1-y0
    if st['fill']:
        mask = Image.new('L', (bw, bh), 0)
        for pts, _ in subs:
            if len(pts) < 3: continue
            tmp = Image.new('L', (bw, bh), 0)
            ImageDraw.Draw(tmp).polygon([(px-x0, py-y0) for px, py in pts], fill=255)
            mask = ImageChops.difference(mask, tmp)
        _composite(canvas, mask, (x0, y0), st['fill'], st['fill-opacity']*st['opacity'])
    if st['stroke'] and sw > 0:
        mask = Image.new('L', (bw, bh), 0); dr = ImageDraw.Draw(mask); r = sw/2
        for pts, closed in subs:
            P = [(px-x0, py-y0) for px, py in pts]
            if closed and P[0] != P[-1]: P = P + [P[0]]
            for a, b in zip(P, P[1:]):
                dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy)
                if L < 1e-6: continue
                nx, ny = -dy/L*r, dx/L*r
                dr.polygon([(a[0]+nx, a[1]+ny), (b[0]+nx, b[1]+ny), (b[0]-nx, b[1]-ny), (a[0]-nx, a[1]-ny)], fill=255)
            ends = set()
            if st['linecap'] == 'butt' and not closed: ends = {0, len(P)-1}
            for k, p in enumerate(P):
                if k in ends: continue
                dr.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=255)
        _composite(canvas, mask, (x0, y0), st['stroke'], st['stroke-opacity']*st['opacity'])

def render_svg(svg_text, width_px, ss=1):
    """Render SVG text to an RGBA image of width_px (height from aspect). ss = extra supersampling."""
    root = ET.fromstring(svg_text)
    vb = [float(v) for v in re.split(r'[\s,]+', root.get('viewBox').strip())]
    s = width_px*ss/vb[2]
    W, H = int(round(vb[2]*s)), int(round(vb[3]*s))
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    base = dict(fill='#000000', stroke=None, **{'stroke-width': 1.0, 'fill-opacity': 1.0, 'stroke-opacity': 1.0,
                'opacity': 1.0, 'linecap': 'round'})
    def walk(el, m, st):
        st = dict(st)
        for k in ('fill', 'stroke'):
            if el.get(k) is not None: st[k] = el.get(k)
        for k in ('stroke-width', 'fill-opacity', 'stroke-opacity'):
            if el.get(k) is not None: st[k] = float(el.get(k))
        if el.get('stroke-linecap'): st['linecap'] = el.get('stroke-linecap')
        if el.get('opacity') is not None: st['opacity'] = st['opacity']*float(el.get('opacity'))
        if el.get('transform'): m = mmul(m, parse_transform(el.get('transform')))
        tag = el.tag.replace(NSP, '')
        if tag in ('svg', 'g'):
            for ch in el: walk(ch, m, st)
            return
        d = shape_d(el)
        if d is None: return
        sc = math.sqrt(abs(m[0]*m[3]-m[1]*m[2]))
        subs = []
        for pts, closed in parse_path(d, sc*s):
            subs.append(([apply(m, px, py) for px, py in pts], closed))
        stp = dict(st); stp['fill'] = hexrgb(st['fill']); stp['stroke'] = hexrgb(st['stroke']); stp['_sc'] = sc
        _draw_shape(canvas, subs, stp)
    walk(root, (s, 0, 0, s, -vb[0]*s, -vb[1]*s), base)
    if ss > 1: canvas = canvas.resize((W//ss, H//ss), Image.BOX)
    return canvas

# ---------- scaling an svg body (numbers) ----------
def scale_path(d, k):
    out = []; cmd = None; idx = 0
    for t in TOK.findall(d):
        if t.isalpha(): cmd = t; idx = 0; out.append(t); continue
        v = float(t)
        if cmd in ('A', 'a'):
            j = idx % 7
            v = v*k if j in (0, 1, 5, 6) else v
        else: v = v*k
        idx += 1; out.append(fmt(v))
    # rebuild with separators
    res = ''; prev_alpha = True
    for t in out:
        if t.isalpha(): res += t; prev_alpha = True
        else: res += ('' if prev_alpha else ' ') + t; prev_alpha = False
    return res

def scale_body(body, k):
    """Scale all geometry in an SVG fragment (string of elements) by k. Stroke widths are NOT scaled."""
    root = ET.fromstring('<r xmlns="http://www.w3.org/2000/svg">' + body + '</r>')
    for el in root.iter():
        for a in ('x', 'y', 'cx', 'cy', 'r', 'rx', 'ry', 'width', 'height', 'x1', 'y1', 'x2', 'y2'):
            if el.get(a) is not None: el.set(a, fmt(float(el.get(a))*k))
        if el.get('points'):
            el.set('points', ' '.join(fmt(float(v)*k) for v in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', el.get('points'))))
        if el.get('stroke-width') is not None: el.set('stroke-width', fmt(float(el.get('stroke-width'))*k))
        if el.get('d'): el.set('d', scale_path(el.get('d'), k))
        if el.get('transform'): raise ValueError('scale_body: transforms unsupported')
    s = ''.join(ET.tostring(ch, encoding='unicode') for ch in root)
    return s.replace(' xmlns="http://www.w3.org/2000/svg"', '').replace('ns0:', '')
