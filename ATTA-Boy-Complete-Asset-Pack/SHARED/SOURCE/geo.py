import math
from svgr import fmt
def pt(cx, cy, r, deg):
    a = math.radians(deg); return cx + r*math.cos(a), cy + r*math.sin(a)
def arc_d(cx, cy, r, a0, a1, move=True):
    """clockwise arc (screen coords) from angle a0 to a1 degrees (0=east, -90=north)."""
    x0, y0 = pt(cx, cy, r, a0); x1, y1 = pt(cx, cy, r, a1)
    sweep = (a1 - a0) % 360 or 360
    large = 1 if sweep > 180 else 0
    return (f'M{fmt(x0)} {fmt(y0)}' if move else '') + f'A{fmt(r)} {fmt(r)} 0 {large} 1 {fmt(x1)} {fmt(y1)}'
def ring_d(cx, cy, r, frac):
    if frac >= 0.999:
        return f'M{fmt(cx-r)} {fmt(cy)}A{fmt(r)} {fmt(r)} 0 1 1 {fmt(cx+r)} {fmt(cy)}A{fmt(r)} {fmt(r)} 0 1 1 {fmt(cx-r)} {fmt(cy)}'
    return arc_d(cx, cy, r, -90, -90 + 360*frac)
def dashed_circle(cx, cy, r, n=8, duty=0.55):
    seg = 360/n; d = ''
    for i in range(n):
        a0 = -90 + i*seg + seg*(1-duty)/2; a1 = a0 + seg*duty
        d += arc_d(cx, cy, r, a0, a1)
    return d
def star_d(cx, cy, ro, ri, n=5, rot=-90):
    pts = []
    for i in range(2*n):
        r = ro if i % 2 == 0 else ri
        pts.append(pt(cx, cy, r, rot + i*180/n))
    return 'M' + 'L'.join(f'{fmt(x)} {fmt(y)}' for x, y in pts) + 'Z'
def gear_d(cx, cy, ro, ri, n=8, tooth=0.5):
    pts = []; step = 360/n
    for i in range(n):
        a = -90 + i*step
        w = step*tooth/2; wi = step*(1-tooth)/2
        for aa, rr in [(a - step/2 + wi*0.0 - 0 + (step/2 - w) , ri), (a - w, ri), (a - w*0.7, ro), (a + w*0.7, ro), (a + w, ri)]:
            pts.append(pt(cx, cy, rr, aa))
    return 'M' + 'L'.join(f'{fmt(x)} {fmt(y)}' for x, y in pts) + 'Z'
def wedge_d(cx, cy, ri, ro, a0, a1):
    x0, y0 = pt(cx, cy, ro, a0); x1, y1 = pt(cx, cy, ro, a1)
    x2, y2 = pt(cx, cy, ri, a1); x3, y3 = pt(cx, cy, ri, a0)
    return (f'M{fmt(x0)} {fmt(y0)}A{fmt(ro)} {fmt(ro)} 0 0 1 {fmt(x1)} {fmt(y1)}L{fmt(x2)} {fmt(y2)}'
            f'A{fmt(ri)} {fmt(ri)} 0 0 0 {fmt(x3)} {fmt(y3)}Z')
def trefoil_d(cx, cy, ri, ro, gap=8):
    return ''.join(wedge_d(cx, cy, ri, ro, c - 30 + gap/2, c + 30 - gap/2) for c in (-90, 30, 150))
def rot_rect_d(cx, cy, w, h, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    pts = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
    return 'M' + 'L'.join(f'{fmt(cx+x*c-y*s)} {fmt(cy+x*s+y*c)}' for x, y in pts) + 'Z'
def poly_dashed(pts, dash=6, gap=4, closed=True):
    """Dashed outline of a polygon as separate M/L segments (no stroke-dasharray needed)."""
    P = pts + ([pts[0]] if closed else []); d = ''; carry = 0.0; on = True; budget = dash
    for a, b in zip(P, P[1:]):
        L = math.dist(a, b); pos = 0.0
        while pos < L - 1e-9:
            take = min(budget, L - pos)
            if on:
                p0 = (a[0] + (b[0]-a[0])*pos/L, a[1] + (b[1]-a[1])*pos/L)
                p1 = (a[0] + (b[0]-a[0])*(pos+take)/L, a[1] + (b[1]-a[1])*(pos+take)/L)
                d += f'M{fmt(p0[0])} {fmt(p0[1])}L{fmt(p1[0])} {fmt(p1[1])}'
            pos += take; budget -= take
            if budget <= 1e-9: on = not on; budget = dash if on else gap
    return d
HEART24 = 'M12 20.5C5 15.5 3.5 12 3.5 8.8A4.6 4.6 0 0 1 12 6.6A4.6 4.6 0 0 1 20.5 8.8C20.5 12 19 15.5 12 20.5Z'
STAR24 = star_d(12, 12, 9, 4.2)

def rr(x, y, w, h, r):
    r = min(r, w/2, h/2)
    return (f'M{fmt(x+r)} {fmt(y)}H{fmt(x+w-r)}A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x+w)} {fmt(y+r)}V{fmt(y+h-r)}'
            f'A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x+w-r)} {fmt(y+h)}H{fmt(x+r)}A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x)} {fmt(y+h-r)}'
            f'V{fmt(y+r)}A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x+r)} {fmt(y)}Z')
def corners(x, y, w, h, s, inset=0):
    x0, y0, x1, y1 = x+inset, y+inset, x+w-inset, y+h-inset
    return (f'M{fmt(x0)} {fmt(y0+s)}V{fmt(y0)}H{fmt(x0+s)}M{fmt(x1-s)} {fmt(y0)}H{fmt(x1)}V{fmt(y0+s)}'
            f'M{fmt(x1)} {fmt(y1-s)}V{fmt(y1)}H{fmt(x1-s)}M{fmt(x0+s)} {fmt(y1)}H{fmt(x0)}V{fmt(y1-s)}')
def clip_x(poly, lo, hi):
    def clip(poly, inside, inter):
        out = []
        for i in range(len(poly)):
            a, b = poly[i-1], poly[i]
            if inside(b):
                if not inside(a): out.append(inter(a, b))
                out.append(b)
            elif inside(a): out.append(inter(a, b))
        return out
    def ix(v):
        return lambda a, b: (v, a[1] + (b[1]-a[1])*(v-a[0])/(b[0]-a[0]))
    p = clip(poly, lambda q: q[0] >= lo, ix(lo))
    if p: p = clip(p, lambda q: q[0] <= hi, ix(hi))
    return p
def hazard(x0, y0, w, h, period, color):
    d = ''
    n = int(w/period) + int(h/period) + 4
    for i in range(-int(h/period)-2, n):
        sx = x0 + i*period
        poly = [(sx, y0+h), (sx+period/2, y0+h), (sx+period/2+h, y0), (sx+h, y0)]
        p = clip_x(poly, x0, x0+w)
        if len(p) >= 3: d += 'M' + 'L'.join(f'{fmt(a)} {fmt(b)}' for a, b in p) + 'Z'
    return f'<path d="{d}" fill="{color}" stroke="none"/>'
