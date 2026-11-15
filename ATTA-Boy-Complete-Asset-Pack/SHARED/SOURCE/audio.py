import wave
import numpy as np
SR = 48000
def tt(d): return np.arange(int(round(d*SR)), dtype=np.float64)/SR
def sil(d): return np.zeros(int(round(d*SR)))
def place(buf, sig, start):
    i = int(round(start*SR)); j = min(len(buf), i + len(sig))
    if i < len(buf) and j > i: buf[i:j] += sig[:j-i]
    return buf
def env(n, a=0.003, d=0.1, sustain=0.0, hold=0.0):
    """attack / hold / exponential decay envelope over n samples."""
    x = np.arange(n)/SR; e = np.where(x < a, x/max(a, 1e-6), 1.0)
    dec = np.exp(-(np.maximum(x - a - hold, 0))/max(d, 1e-6)); return e*(sustain + (1 - sustain)*dec)
def sine(f, d, ph=0.0):
    f = np.asarray(f) if not np.isscalar(f) else np.full(int(round(d*SR)), float(f))
    return np.sin(2*np.pi*np.cumsum(f)/SR + ph)
def chirp(f0, f1, d, curve='lin'):
    n = int(round(d*SR)); u = np.linspace(0, 1, n)
    f = f0 + (f1 - f0)*(u if curve == 'lin' else u**2 if curve == 'sq' else 1 - (1-u)**2); return sine(f, d)
def soft_square(f, d, k=3.0):
    return np.tanh(k*sine(f, d))/np.tanh(k)
def saw(f, d):
    f = np.full(int(round(d*SR)), float(f)) if np.isscalar(f) else np.asarray(f); ph = np.cumsum(f)/SR; return 2*(ph - np.floor(ph + 0.5))
def noise(d, seed=0): return np.random.default_rng(seed).standard_normal(int(round(d*SR)))
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    m = np.clip((f - lo)/max(lo*0.2, 20), 0, 1)*np.clip((hi - f)/max(hi*0.2, 20), 0, 1); return np.fft.irfft(X*m, n=len(x))
def lp(x, fc): return bp(x, 0.0001, fc)
def hp(x, fc): return bp(x, fc, SR/2 - 100)
def bell(f, d, partials=((1, 1.0, 1.0), (2.0, 0.5, 0.6), (2.76, 0.35, 0.45), (5.4, 0.18, 0.25)), a=0.002, base=0.5):
    n = int(round(d*SR)); out = np.zeros(n)
    for r, amp, dec in partials: out += amp*sine(f*r, d)*env(n, a, base*dec)
    return out
def relay(seed=1, strength=1.0):
    n = int(0.03*SR); c = bp(noise(0.03, seed), 700, 5200)*env(n, 0.0004, 0.0045)
    th = sine(110, 0.03)*env(n, 0.0008, 0.011)*0.8; return strength*(c*1.4 + th)
def clack(f_lo=1500, f_hi=6000, d=0.02, seed=2, dec=0.003): return bp(noise(d, seed), f_lo, f_hi)*env(int(round(d*SR)), 0.0003, dec)
def hum(d, f0=60, amp=1.0):
    t = tt(d); return amp*(sine(f0, d) + 0.5*sine(2*f0, d) + 0.25*sine(3*f0, d) + 0.12*sine(5*f0, d))
def finalize(x, target_db=-19.0, peak=0.88, fade_in=0.0008, fade_out=0.008):
    x = np.asarray(x, np.float64).copy(); x -= x.mean()
    n_in = int(fade_in*SR); n_out = int(fade_out*SR)
    if n_in: x[:n_in] *= np.linspace(0, 1, n_in)
    if n_out and len(x) > n_out: x[-n_out:] *= np.linspace(1, 0, n_out)
    act = np.abs(x) > 0.05*np.abs(x).max()
    rms = np.sqrt(np.mean(x[act]**2)); x *= (10**(target_db/20))/rms
    if np.abs(x).max() > peak: x = peak*np.tanh(x/peak)
    if np.abs(x).max() > peak: x *= peak/np.abs(x).max()
    return x
def write_wav(path, x):
    pcm = np.clip(np.round(x*32767), -32767, 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

def terminal_startup():
    b = sil(2.5)
    place(b, relay(1, 1.2), 0.0); place(b, sine(70, 0.12)*env(int(0.12*SR), 0.002, 0.04)*0.9, 0.0)
    h = hum(2.3, 60, 0.18); h *= np.minimum(1, tt(2.3)/0.7)*np.exp(-np.maximum(tt(2.3)-1.6, 0)/0.5); place(b, h, 0.15)
    n = int(0.45*SR); place(b, (chirp(160, 40, 0.45)*0.9 + bp(noise(0.45, 5), 200, 2200)*0.5)*env(n, 0.004, 0.14), 0.12)
    for k, f in enumerate((600, 750, 900, 1125, 1350)):
        s = soft_square(f, 0.06, 2.0)*env(int(0.06*SR), 0.002, 0.03); place(b, s*0.35, 0.8 + 0.17*k)
    place(b, bell(880, 0.7, base=0.45)*0.5 + bell(1320, 0.7, base=0.35)*0.3, 1.75)
    return finalize(b)
def terminal_shutdown():
    b = sil(1.9); n = int(0.9*SR)
    sw = (chirp(900, 90, 0.9, 'sq')*0.7 + saw(np.linspace(450, 45, n), 0.9)*0.25)*env(n, 0.004, 0.5)
    place(b, sw, 0.0); place(b, hp(noise(0.3, 7), 2500)*env(int(0.3*SR), 0.002, 0.1)*0.35, 0.0)
    place(b, bp(noise(0.14, 8), 3000, 9500)*env(int(0.14*SR), 0.0005, 0.03)*0.9, 0.92)
    place(b, sine(60, 0.2)*env(int(0.2*SR), 0.002, 0.07)*1.0, 1.05); place(b, relay(3, 1.0), 1.05)
    h = hum(0.7, 60, 0.12)*np.linspace(1, 0, int(0.7*SR)); place(b, h, 0.9)
    return finalize(b)
def connection_established():
    b = sil(0.95); place(b, relay(4, 0.9), 0.0)
    place(b, chirp(500, 800, 0.12)*env(int(0.12*SR), 0.004, 0.09)*0.6, 0.06)
    place(b, chirp(800, 1200, 0.12)*env(int(0.12*SR), 0.004, 0.09)*0.6, 0.22)
    place(b, bell(1000, 0.6, base=0.35)*0.6, 0.4); return finalize(b)
def connection_lost():
    b = sil(1.05); place(b, chirp(900, 500, 0.16)*env(int(0.16*SR), 0.004, 0.1)*0.6, 0.0)
    place(b, chirp(500, 260, 0.22, 'sq')*env(int(0.22*SR), 0.004, 0.14)*0.6, 0.2)
    st = bp(noise(0.3, 9), 1000, 6500)*(0.6 + 0.4*np.sin(2*np.pi*40*tt(0.3)))*env(int(0.3*SR), 0.003, 0.12); place(b, st*0.5, 0.15)
    place(b, sine(55, 0.3)*env(int(0.3*SR), 0.003, 0.1)*0.9, 0.5); place(b, relay(10, 0.9), 0.5); return finalize(b)
def data_received():
    b = sil(0.13); place(b, clack(1800, 6500, 0.01, 11, 0.002)*0.8, 0.0)
    place(b, sine(1400, 0.045)*env(int(0.045*SR), 0.002, 0.02)*0.6, 0.004); place(b, sine(1850, 0.035)*env(int(0.035*SR), 0.002, 0.016)*0.5, 0.055); return finalize(b)
def notification():
    b = sil(0.75)
    for st, f in ((0.0, 988), (0.2, 1318)):
        place(b, bell(f, 0.5, base=0.28)*0.7, st); place(b, clack(2500, 7000, 0.01, 12, 0.002)*0.4, st)
    return finalize(b)
def menu_navigate():
    b = sil(0.07); place(b, clack(1500, 5000, 0.012, 13, 0.003), 0.0); place(b, sine(1100, 0.025)*env(int(0.025*SR), 0.001, 0.009)*0.6, 0.0); return finalize(b)
def button_confirm():
    b = sil(0.22); place(b, relay(14, 0.9), 0.0); place(b, chirp(500, 900, 0.09)*env(int(0.09*SR), 0.003, 0.05)*0.6, 0.02)
    place(b, sine(1200, 0.07)*env(int(0.07*SR), 0.002, 0.03)*0.5, 0.11); return finalize(b)
def button_cancel():
    b = sil(0.22); place(b, relay(15, 0.9), 0.0); place(b, chirp(700, 330, 0.1)*env(int(0.1*SR), 0.003, 0.06)*0.6, 0.02)
    place(b, sine(220, 0.07)*env(int(0.07*SR), 0.002, 0.03)*0.6, 0.12); return finalize(b)
def inventory_select():
    b = sil(0.13); place(b, clack(900, 4200, 0.02, 16, 0.004)*1.0, 0.0); place(b, sine(220, 0.03)*env(int(0.03*SR), 0.001, 0.01)*0.7, 0.0)
    place(b, clack(1800, 6500, 0.015, 17, 0.003)*0.8, 0.03); return finalize(b)
def medical_treatment():
    b = sil(1.35); n = int(1.0*SR)
    hiss = bp(noise(1.0, 18), 3000, 9500)*(np.minimum(1, tt(1.0)/0.15)*np.exp(-np.maximum(tt(1.0)-0.25, 0)/0.28)); place(b, hiss*0.8, 0.0)
    place(b, relay(19, 0.8), 0.0); place(b, sine(90, 0.12)*env(int(0.12*SR), 0.003, 0.04)*0.9, 0.42)
    for k, f in enumerate((1400, 1750, 2100)): place(b, sine(f, 0.06)*env(int(0.06*SR), 0.002, 0.03)*0.3, 0.72 + 0.14*k)
    return finalize(b)
def autodoc_start():
    b = sil(2.3); n = int(1.3*SR); f = np.linspace(70, 430, n)**1.0
    mot = (saw(f, 1.3)*0.35 + sine(f, 1.3)*0.5 + sine(f*2, 1.3)*0.15)*np.minimum(1, tt(1.3)/0.15)*(0.5 + 0.5*np.linspace(0, 1, n))
    mot += 0.04*bp(noise(1.3, 20), 300, 1200); place(b, mot*0.8, 0.1)
    place(b, relay(21, 1.0), 0.0); place(b, relay(22, 0.9), 0.38)
    m = int(0.9*SR); u = np.linspace(0, 1, m); sc = sine(400 + 1400*np.sin(np.pi*u), 0.9)*np.sin(np.pi*u)**0.5; place(b, sc*0.18, 1.25)
    place(b, sine(1320, 0.08)*env(int(0.08*SR), 0.002, 0.03)*0.4, 2.15); return finalize(b)
def autodoc_complete():
    b = sil(1.55); n = int(0.55*SR)
    place(b, (saw(np.linspace(430, 90, n), 0.55)*0.3 + sine(np.linspace(430, 90, n), 0.55)*0.5)*env(n, 0.003, 0.3)*0.8, 0.0)
    place(b, relay(23, 0.9), 0.5)
    for k, f in enumerate((784, 988, 1318)): place(b, bell(f, 0.6, base=0.3)*0.6, 0.62 + 0.24*k)
    return finalize(b)
def medical_warning():
    b = sil(1.0)
    for k in range(3):
        s = (soft_square(740, 0.17, 2.0)*0.6 + soft_square(560, 0.17, 2.0)*0.4)*(0.85 + 0.15*np.sin(2*np.pi*18*tt(0.17)))*env(int(0.17*SR), 0.004, 0.1, 0.3, 0.06)
        place(b, s*0.7, 0.04 + 0.3*k); place(b, sine(80, 0.08)*env(int(0.08*SR), 0.002, 0.03)*0.5, 0.04 + 0.3*k)
    return finalize(b)
def warning():
    b = sil(0.85)
    for k, f in enumerate((880, 660, 880, 660)): place(b, soft_square(f, 0.17, 2.2)*env(int(0.17*SR), 0.004, 0.08, 0.35, 0.05)*0.6, 0.03 + 0.2*k)
    return finalize(b)
def error():
    b = sil(0.7)
    for k in range(2):
        n = int(0.26*SR); s = np.tanh(2.5*(saw(np.linspace(175, 118, n), 0.26)*0.6 + soft_square(np.linspace(87, 59, n), 0.26)*0.5))*env(n, 0.004, 0.2, 0.5, 0.1)
        place(b, s*0.7, 0.03 + 0.31*k)
    return finalize(b)
def critical_warning():
    b = sil(2.6)
    for k in range(7):
        t0 = 0.05 + 0.34*k
        place(b, (soft_square(960, 0.16, 2.5)*0.55)*env(int(0.16*SR), 0.003, 0.1, 0.5, 0.05), t0)
        place(b, (soft_square(640, 0.16, 2.5)*0.55)*env(int(0.16*SR), 0.003, 0.1, 0.5, 0.05), t0 + 0.17)
        place(b, sine(70, 0.1)*env(int(0.1*SR), 0.002, 0.04)*0.7, t0)
    return finalize(b, fade_out=0.04)
SOUNDS = [
 ('terminal_startup', terminal_startup, 'Terminal', 'Power-on: relay clunk, degauss thump, hum swell, data blips and a bell.'),
 ('terminal_shutdown', terminal_shutdown, 'Terminal', 'Power-off: falling sweep, CRT collapse zap, thunk.'),
 ('connection_established', connection_established, 'Terminal', 'Relay click, two rising chirps, soft bell.'),
 ('connection_lost', connection_lost, 'Terminal', 'Falling chirps with static burst and thunk.'),
 ('data_received', data_received, 'Terminal', 'Tiny tick plus two blips; unobtrusive.'),
 ('notification', notification, 'Terminal', 'Two-note mechanical bell.'),
 ('menu_navigate', menu_navigate, 'Navigation', 'Very short tick; subtle.'),
 ('button_confirm', button_confirm, 'Navigation', 'Relay click with rising chirp.'),
 ('button_cancel', button_cancel, 'Navigation', 'Relay click with falling chirp.'),
 ('inventory_select', inventory_select, 'Navigation', 'Two-stage mechanical switch clack.'),
 ('medical_treatment', medical_treatment, 'Medical', 'Pneumatic hiss, pressure thump and soft confirmation tones.'),
 ('autodoc_start', autodoc_start, 'Medical', 'Servo spin-up, latch clicks, scanner sweep.'),
 ('autodoc_complete', autodoc_complete, 'Medical', 'Servo wind-down then three rising chimes.'),
 ('medical_warning', medical_warning, 'Medical', 'Three dual-tone pulses.'),
 ('warning', warning, 'System', 'Two-tone alternating beeps.'),
 ('error', error, 'System', 'Low descending double buzzer.'),
 ('critical_warning', critical_warning, 'System', 'Urgent two-tone alarm with thumps.'),
]
