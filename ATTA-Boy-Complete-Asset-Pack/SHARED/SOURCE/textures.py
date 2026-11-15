import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from palette import PAL
OLIVE = np.array([0.31, 0.34, 0.20], dtype=np.float32)
def col(k): h = PAL[k].lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], dtype=np.float32)/255.0
def fnoise(h, w, beta, seed, ax=1.0, ay=1.0):
    """Periodic 1/f^beta noise (tileable by construction), roughly zero-mean/unit-std."""
    rng = np.random.default_rng(seed); F = np.fft.rfft2(rng.standard_normal((h, w)))
    fy = np.fft.fftfreq(h)[:, None]*ay; fx = np.fft.rfftfreq(w)[None, :]*ax
    f = np.sqrt(fx**2 + fy**2); f[0, 0] = 1.0
    F = F/(f**beta); F[0, 0] = 0
    x = np.fft.irfft2(F, s=(h, w)); return (x - x.mean())/(x.std() + 1e-9)
def n01(x, k=2.6): return np.clip(x/(2*k) + 0.5, 0, 1)
def smooth(a, lo, hi): t = np.clip((a-lo)/(hi-lo), 0, 1); return t*t*(3-2*t)
def tint(base, lum): return np.clip(base[None, None, :]*lum[..., None], 0, 1)
def to_img(a, alpha=None):
    rgb = (np.clip(a, 0, 1)*255 + 0.5).astype(np.uint8)
    if alpha is None: return Image.fromarray(rgb, 'RGB')
    return Image.fromarray(np.dstack([rgb, (np.clip(alpha, 0, 1)*255 + 0.5).astype(np.uint8)]), 'RGBA')
def grid(h, w):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32); return y, x

# ------------------------- seamless textures (opaque unless *_alpha) -------------------------
def tex_metal_brushed_clean(n=512):
    streak = fnoise(n, n, 0.35, 1, ax=0.02); fine = fnoise(n, n, 0.2, 2); big = fnoise(n, n, 2.4, 3)
    lum = 0.74 + 0.07*n01(streak) * 2 - 0.07 + 0.025*fine + 0.05*big
    return to_img(tint(col('G'), lum*1.05))
def tex_olive_paint_clean(n=512):
    lum = 0.92 + 0.08*fnoise(n, n, 2.2, 11) + 0.025*fnoise(n, n, 0.5, 12) + 0.012*fnoise(n, n, 1.0, 13)
    return to_img(tint(OLIVE, lum))
def tex_olive_paint_worn(n=512):
    paint = tint(OLIVE, 0.92 + 0.09*fnoise(n, n, 2.2, 21) + 0.03*fnoise(n, n, 0.6, 22))
    mid = 0.55*fnoise(n, n, 1.1, 23) + 0.9*fnoise(n, n, 0.45, 24)
    chip = smooth(n01(mid), 0.70, 0.74)                         # exposed metal where paint chipped
    edge = smooth(n01(mid), 0.64, 0.70)*(1-chip)                # dark rim around chips
    metal = tint(np.array([0.36, 0.31, 0.25], np.float32), 0.8 + 0.25*n01(fnoise(n, n, 0.5, 25)))
    metal = metal*(1 - 0.45*n01(fnoise(n, n, 2.0, 26))[..., None]*0.5)
    out = paint*(1 - chip[..., None]) + metal*chip[..., None]
    out *= (1 - 0.35*edge[..., None])
    grime = n01(fnoise(n, n, 2.6, 27)); out *= (0.82 + 0.18*grime)[..., None]
    return to_img(out)
def tex_charcoal_plate(n=512):
    lum = 0.9 + 0.08*fnoise(n, n, 1.4, 31) + 0.03*fnoise(n, n, 0.4, 32) + 0.03*n01(fnoise(n, n, 0.3, 33, ax=0.05))
    img = to_img(tint(col('H')*1.1, lum*1.0))
    d = ImageDraw.Draw(img, 'RGBA'); rng = np.random.default_rng(34)
    for _ in range(70):
        x, y = rng.uniform(0, n), rng.uniform(0, n); a = rng.uniform(-0.3, 0.3); L = rng.uniform(6, 40); c = int(rng.uniform(60, 110))
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                d.line([(x+ox, y+oy), (x+ox+L*math.cos(a), y+oy+L*math.sin(a))], fill=(c, c, c-6, int(rng.uniform(20, 70))), width=1)
    return img
def tex_perforated_steel(n=512):
    base = tint(col('G')*0.9, 0.84 + 0.06*fnoise(n, n, 2.0, 41) + 0.02*fnoise(n, n, 0.4, 42))
    y, x = grid(n, n); sp = 32.0; out = base.copy()
    for ox, row in ((0.0, 0), (sp/2, 1)):
        pass
    yy = (y + sp/2) % sp - sp/2; row = np.floor((y + sp/2)/sp).astype(int)
    xx = np.where(row % 2 == 0, (x + sp/2) % sp - sp/2, x % sp - sp/2)
    r = np.sqrt(xx**2 + yy**2); hole = 1 - smooth(r, 7.0, 8.2); rim = smooth(r, 7.5, 8.2)*(1 - smooth(r, 8.2, 10.5))
    shade = 0.8 + 0.4*(-(xx + yy)/ (20.0))*rim            # bevel highlight toward top-left
    out = out*np.clip(1 + (shade - 0.8)*0.9, 0.5, 1.35)[..., None]
    out = out*(1 - hole[..., None]) + col('K')[None, None, :]*1.6*hole[..., None]*(0.6 + 0.4*(r/8.0))[..., None]
    return to_img(out)
def tex_crt_phosphor(n=512):
    glow = n01(fnoise(n, n, 2.6, 51)); band = n01(fnoise(n, n, 0.4, 52, ax=0.02)); grain = fnoise(n, n, 0.1, 53)
    lum = 0.55 + 0.35*glow + 0.12*band + 0.05*grain
    base = np.array([0.03, 0.17, 0.07], np.float32)*1.25
    return to_img(tint(base, lum))
def tex_hazard_stripes(n=512):
    y, x = grid(n, n); per = 64.0; t = ((x + y) % per)/per
    amber = (t < 0.5).astype(np.float32); soft = smooth(np.abs(((t*2) % 1) - 0.5), 0.46, 0.5)*0
    a = col('A')[None, None, :]; k = col('K')[None, None, :]*1.6
    wear = n01(fnoise(n, n, 1.3, 61)) + 0.3*fnoise(n, n, 0.6, 62)
    out = a*amber[..., None] + k*(1 - amber[..., None])
    worn = smooth(wear, 0.62, 0.78)[..., None]; out = out*(1 - 0.55*worn) + np.array([0.3, 0.27, 0.22], np.float32)*0.55*worn
    out *= (0.9 + 0.1*n01(fnoise(n, n, 2.0, 63)))[..., None]
    return to_img(out)
def tex_rust_grime_alpha(n=512):
    m = n01(fnoise(n, n, 2.0, 71)) + 0.25*fnoise(n, n, 0.8, 72)
    a = smooth(m, 0.55, 0.9)*0.62
    c = np.array([0.22, 0.14, 0.08], np.float32)[None, None, :]*(0.7 + 0.5*n01(fnoise(n, n, 1.0, 73)))[..., None]
    return to_img(c, a)
def tex_scratches_alpha(n=512):
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(img); rng = np.random.default_rng(81)
    for _ in range(220):
        x, y = rng.uniform(0, n), rng.uniform(0, n); a = rng.uniform(-math.pi, math.pi); L = rng.uniform(5, 60); c = int(rng.uniform(150, 230)); al = int(rng.uniform(30, 110))
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                d.line([(x+ox, y+oy), (x+ox+L*math.cos(a), y+oy+L*math.sin(a))], fill=(c, c, c, al), width=1)
    return img
SEAMLESS = [
 ('tex_metal_brushed_clean', tex_metal_brushed_clean, 'Clean brushed industrial grey metal.'),
 ('tex_olive_paint_clean', tex_olive_paint_clean, 'Clean olive-drab painted metal.'),
 ('tex_olive_paint_worn', tex_olive_paint_worn, 'Olive paint with chips exposing bare metal and grime.'),
 ('tex_charcoal_plate', tex_charcoal_plate, 'Scuffed charcoal plate.'),
 ('tex_perforated_steel', tex_perforated_steel, 'Perforated steel sheet (speaker / vent grille).'),
 ('tex_crt_phosphor', tex_crt_phosphor, 'Dark phosphor-green CRT glass base with banding and grain.'),
 ('tex_hazard_stripes', tex_hazard_stripes, 'Worn amber/black hazard stripes (diagonal).'),
 ('tex_rust_grime_alpha', tex_rust_grime_alpha, 'Transparent rust/grime layer to blend over any surface.'),
 ('tex_scratches_alpha', tex_scratches_alpha, 'Transparent fine-scratch layer.'),
]
# ------------------------- overlays 1024x1024 (RGBA) -------------------------
N = 1024
def _rgba(color, alpha): 
    c = np.broadcast_to(np.array(color, np.float32)/255.0, alpha.shape + (3,)); return to_img(c, alpha)
def ov_scanlines_fine():
    y = np.arange(N)[:, None].astype(np.float32); a = (0.5 + 0.5*np.cos(2*np.pi*y/4)); a = np.repeat(a, N, 1)
    return _rgba((0, 0, 0), a*0.42)
def ov_scanlines_coarse():
    y = np.arange(N)[:, None].astype(np.float32); a = np.clip(np.cos(2*np.pi*y/8)*1.3, 0, 1)**1.5; a = np.repeat(a, N, 1)
    return _rgba((0, 0, 0), a*0.5)
def _r():
    y, x = grid(N, N); u, v = (x - N/2 + 0.5)/(N/2), (y - N/2 + 0.5)/(N/2); return u, v, np.sqrt(u*u + v*v)
def ov_screen_glow():
    u, v, r = _r(); a = 0.46*np.exp(-(r/0.62)**2) + 0.1*np.exp(-((v+0.1)/0.18)**2)*np.exp(-(u/0.9)**2)
    return _rgba((76, 255, 127), np.clip(a - 0.012, 0, 0.6))
def ov_vignette():
    u, v, r = _r(); a = smooth(r, 0.45, 1.25)**1.5*0.9; return _rgba((0, 0, 0), a)
def ov_glass_reflection():
    u, v, r = _r(); d = (u + v)/2
    band = np.exp(-((d + 0.55)/0.1)**2)*0.5 + np.exp(-((d + 0.32)/0.035)**2)*0.35
    mask = smooth(1 - np.sqrt(((u + 0.35)/1.05)**2 + ((v + 0.35)/1.05)**2), 0.0, 0.5)
    return _rgba((235, 255, 240), np.clip(band*mask*0.5, 0, 0.2))
def ov_scratches():
    img = Image.new('RGBA', (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(img); rng = np.random.default_rng(91)
    for i in range(260):
        x, y = rng.uniform(0, N), rng.uniform(0, N); a = rng.normal(0.4, 0.9); L = rng.uniform(10, 140)
        c = (230, 245, 230) if i % 5 else (10, 12, 10); al = int(rng.uniform(25, 120))
        d.line([(x, y), (x+L*math.cos(a), y+L*math.sin(a))], fill=c+(al,), width=1 if rng.random() < 0.85 else 2)
    return img
def ov_grime_edges():
    u, v, r = _r(); e = np.maximum(np.abs(u), np.abs(v)); n = n01(fnoise(N, N, 1.6, 95)) + 0.3*fnoise(N, N, 0.7, 96)
    a = smooth(e + (n - 0.5)*0.55, 0.62, 1.05)*0.8
    return _rgba((24, 18, 10), np.clip(a, 0, 0.85))
def ov_noise_grain():
    rng = np.random.default_rng(97); a = rng.random((N, N)).astype(np.float32); a = np.where(a > 0.55, (a - 0.55)/0.45, 0)**2*0.35
    c = np.where(rng.random((N, N, 1)) > 0.5, 255, 0).astype(np.float32)/255
    return to_img(np.broadcast_to(c, (N, N, 3)), a)
def ov_crt_distortion_map():
    u, v, r = _r(); k = 0.12; dx, dy = -k*u*r*r, -k*v*r*r; m = k
    R = 0.5 + dx/(2*m)*0.9; G = 0.5 + dy/(2*m)*0.9
    return to_img(np.dstack([R, G, np.full_like(R, 0.5)]))
def ov_reticle_grid():
    S = 2; im = Image.new('RGBA', (N*S, N*S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (76, 255, 127)
    for k in range(1, 8):
        p = int(k*N/8*S); a = 150 if k == 4 else 60
        d.line([(p, 24*S), (p, (N-24)*S)], fill=c+(a,), width=(3 if k == 4 else 2)); d.line([(24*S, p), ((N-24)*S, p)], fill=c+(a,), width=(3 if k == 4 else 2))
    for k in range(0, 65):
        p = int((24 + k*(N-48)/64)*S); L = (14 if k % 8 == 0 else 7)*S
        for (a, b, e, f) in ((p, N*S//2 - L, p, N*S//2 + L), (N*S//2 - L, p, N*S//2 + L, p)): d.line([(a, b), (e, f)], fill=c+(190,), width=2)
    d.rectangle([24*S, 24*S, (N-24)*S, (N-24)*S], outline=c+(200,), width=4)
    return im.resize((N, N), Image.LANCZOS)
def ov_compass_ring():
    S = 2; M = N*S; im = Image.new('RGBA', (M, M), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (76, 255, 127); cx = cy = M/2; R = 460*S
    d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=c+(220,), width=5); d.ellipse([cx-R+60*S, cy-R+60*S, cx+R-60*S, cy+R-60*S], outline=c+(90,), width=3)
    for deg in range(0, 360, 5):
        L = 56*S if deg % 45 == 0 else (34*S if deg % 15 == 0 else 18*S); w = 6 if deg % 45 == 0 else (4 if deg % 15 == 0 else 2)
        a = math.radians(deg - 90); d.line([(cx+math.cos(a)*R, cy+math.sin(a)*R), (cx+math.cos(a)*(R-L), cy+math.sin(a)*(R-L))], fill=c+(230,), width=w)
    d.polygon([(cx, cy-R-34*S), (cx-22*S, cy-R-2*S), (cx+22*S, cy-R-2*S)], fill=c+(255,))
    return im.resize((N, N), Image.LANCZOS)
OVERLAYS = [
 ('overlay_scanlines_fine', ov_scanlines_fine, 'Fine 4px scanline pattern (stretch or tile vertically).', True),
 ('overlay_scanlines_coarse', ov_scanlines_coarse, 'Coarse 8px scanline pattern.', True),
 ('overlay_screen_glow', ov_screen_glow, 'Phosphor glow bloom centred on the screen.', True),
 ('overlay_vignette', ov_vignette, 'Dark CRT edge falloff.', True),
 ('overlay_glass_reflection', ov_glass_reflection, 'Soft glass highlight, top-left.', True),
 ('overlay_scratches', ov_scratches, 'Random fine scratches (light and dark).', True),
 ('overlay_grime_edges', ov_grime_edges, 'Dirty edges / corner build-up.', True),
 ('overlay_noise_grain', ov_noise_grain, 'Sparse static grain.', True),
 ('overlay_crt_distortion_map', ov_crt_distortion_map, 'RG displacement map for barrel distortion in a shader (128 = no shift). Opaque data texture.', False),
 ('overlay_reticle_grid', ov_reticle_grid, 'Generic reticle/graticule grid with centre ticks. Interface element only; contains no map data.', True),
 ('overlay_compass_ring', ov_compass_ring, 'Compass bezel ring with degree ticks and a north pointer (no letters).', True),
]
# ------------------------- backgrounds -------------------------
def _scan(h, w, period, strength):
    y = np.arange(h)[:, None].astype(np.float32); return 1 - strength*(0.5 + 0.5*np.cos(2*np.pi*y/period))*np.ones((1, w), np.float32)
def _vig(h, w, k=0.55):
    y, x = grid(h, w); u, v = (x/w - 0.5)*2, (y/h - 0.5)*2; r = np.sqrt((u*0.85)**2 + (v*0.85)**2); return 1 - k*smooth(r, 0.35, 1.2)
def bg_terminal(w, h, worn):
    s = h/1080.0; y, x = grid(h, w); u, v = (x/w - 0.5)*2, (y/h - 0.5)*2
    glow = np.exp(-((u/0.95)**2 + (v/0.9)**2)*1.2)
    base = np.array([0.016, 0.06, 0.028], np.float32); ph = np.array([0.10, 0.55, 0.22], np.float32)
    lum = 0.55 + 0.5*glow; out = base[None, None, :] + ph[None, None, :]*(0.55*glow)[..., None]
    out *= (0.9 + 0.1*n01(fnoise(h, w, 2.4, 101)))[..., None]
    out *= _scan(h, w, max(3.0, 4*s), 0.28)[..., None]*_vig(h, w)[..., None]
    out += (fnoise(h, w, 0.05, 102)*0.006)[..., None]
    if worn:
        e = np.maximum(np.abs(u), np.abs(v)); n = n01(fnoise(h, w, 1.6, 103)) + 0.3*fnoise(h, w, 0.7, 104)
        gr = smooth(e + (n - 0.5)*0.5, 0.7, 1.1)*0.7; out = out*(1 - gr[..., None]) + np.array([0.05, 0.04, 0.02], np.float32)*gr[..., None]
        band = n01(fnoise(h, w, 0.5, 105, ax=0.01)); out *= (0.94 + 0.08*band)[..., None]
    return to_img(out)
def bg_industrial(w, h):
    s = h/1080.0
    paint = tint(OLIVE*0.95, 0.9 + 0.08*fnoise(h, w, 2.3, 111) + 0.025*fnoise(h, w, 0.5, 112))
    mid = 0.55*fnoise(h, w, 1.1, 113) + 0.9*fnoise(h, w, 0.45, 114); chip = smooth(n01(mid), 0.74, 0.78)[..., None]
    metal = np.array([0.30, 0.26, 0.21], np.float32)*(0.85 + 0.2*n01(fnoise(h, w, 0.6, 115)))[..., None]
    out = paint*(1 - chip) + metal*chip
    out *= (0.8 + 0.2*n01(fnoise(h, w, 2.7, 116)))[..., None]*_vig(h, w, 0.35)[..., None]
    img = to_img(out); d = ImageDraw.Draw(img, 'RGBA')
    cols, rows = 4, 2 if w > h else 6
    for i in range(1, cols):
        x0 = int(w*i/cols); d.line([(x0, 0), (x0, h)], fill=(8, 10, 6, 210), width=max(2, int(3*s))); d.line([(x0+max(2, int(3*s)), 0), (x0+max(2, int(3*s)), h)], fill=(190, 200, 160, 40), width=1)
    for j in range(1, rows):
        y0 = int(h*j/rows); d.line([(0, y0), (w, y0)], fill=(8, 10, 6, 210), width=max(2, int(3*s))); d.line([(0, y0+max(2, int(3*s))), (w, y0+max(2, int(3*s)))], fill=(190, 200, 160, 40), width=1)
    rv = max(3, int(5*s)); step = int(70*s)
    for i in range(0, cols+1):
        x0 = min(max(int(w*i/cols), rv*2), w - rv*2)
        for y0 in range(step//2, h, step):
            for xx in (x0 - int(14*s), x0 + int(14*s)):
                d.ellipse([xx-rv, y0-rv, xx+rv, y0+rv], fill=(98, 102, 90, 255), outline=(8, 10, 6, 255)); d.ellipse([xx-rv//2-1, y0-rv//2-1, xx-1, y0-1], fill=(220, 230, 205, 120))
    return img
BACKGROUNDS = [
 ('bg_terminal_clean', lambda w, h: bg_terminal(w, h, False), 'Clean dark CRT screen with faint phosphor glow, scanlines and vignette.'),
 ('bg_terminal_worn', lambda w, h: bg_terminal(w, h, True), 'Aged CRT screen with grime at the edges and uneven brightness.'),
 ('bg_industrial_olive', bg_industrial, 'Riveted olive-drab panel wall with chipped paint.'),
]
