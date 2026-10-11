"""Mie fason Reels v7 — müzik + efekt (kodla üretim), reel_v7 zaman çizelgesine kilitli (120 BPM).

Çıktılar: <out>_muzik.wav, <out>_efekt.wav, <out>_mix.wav (44.1 kHz stereo)
Kullanım: python3 music_v5.py OUT_PREFIX
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
DUR = 33.0
N = int(DUR * SR)
BEAT = 0.5                    # 120 BPM: her süreç adımı (2 sn) = 4 vuruş
rng = np.random.default_rng(3)


def buf(): return np.zeros((N, 2))
def tt(d): return np.arange(int(d * SR)) / SR
def env(d, a=0.005, r=None):
    n = int(d * SR); e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if r: e *= np.exp(-tt(d) / r)
    return e
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)
def add(b, x, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i + len(x) <= 0: return
    if i < 0: x = x[-i:]; i = 0
    x = x[: N - i]
    b[i:i + len(x), 0] += x * g * (1 - max(0, pan)); b[i:i + len(x), 1] += x * g * (1 + min(0, pan))
def note(n): return 440 * 2 ** ((n - 69) / 12)
def saw(f, d):
    t = tt(d); return 2 * ((t * f) % 1) - 1


# ---------- sesler ----------
def kick(g=1.0):
    d = 0.45; t = tt(d); f = 45 + 110 * np.exp(-t / 0.045)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16) * g
def boom():   # büyük vuruş (damga / kapı)
    d = 2.2; t = tt(d); f = 32 + 90 * np.exp(-t / 0.08)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7)
    n = lp(rng.standard_normal(len(t)), 900) * np.exp(-t / 0.25) * 0.5
    return s + n
def clap():
    d = 0.3; n = bp(rng.standard_normal(int(d * SR)), 900, 4000)
    e = np.exp(-tt(d) / 0.06); e[: int(0.012 * SR)] *= 1.6
    return n * e * 0.6
def hat(open_=False):
    d = 0.25 if open_ else 0.06; n = hp(rng.standard_normal(int(d * SR)), 7000)
    return n * np.exp(-tt(d) / (0.08 if open_ else 0.015)) * 0.35
def tick():   # kart düşme / onay
    d = 0.09; t = tt(d)
    return (np.sin(2 * np.pi * 1800 * t) * 0.5 + bp(rng.standard_normal(len(t)), 1500, 6000) * 0.4) * np.exp(-t / 0.018)
def thud():   # kart yere konma
    d = 0.18; t = tt(d); f = 140 * np.exp(-t / 0.05) + 70
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.05) * 0.7
def whoosh(d=0.5, rise=True):
    n = rng.standard_normal(int(d * SR)); out = np.zeros_like(n); seg = 512
    for i in range(0, len(n), seg):
        x = i / len(n); fc = 400 + 7000 * (x if rise else 1 - x)
        out[i:i + seg] = bp(n[i:i + seg], max(200, fc * 0.6), min(18000, fc * 1.4))
    e = np.sin(np.pi * np.linspace(0, 1, len(n))) ** 2
    return out * e * 0.6
def riser(d):
    t = tt(d); x = t / d
    n = rng.standard_normal(len(t)); out = np.zeros_like(n); seg = 1024
    for i in range(0, len(n), seg):
        fc = 300 + 9000 * (i / len(n)) ** 2; out[i:i + seg] = bp(n[i:i + seg], fc * 0.5, min(19000, fc * 1.5))
    tone = np.sin(2 * np.pi * np.cumsum(110 * 2 ** (2 * x)) / SR) * 0.25
    return (out * 0.5 + tone) * x ** 1.5
def pad(notes, d, g=0.15, cut=1800):
    t = tt(d); s = np.zeros(len(t))
    for n in notes:
        for det in (-0.08, 0.08):
            s += saw(note(n + det), d)
    s = lp(s, cut, 2); e = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)
    return s * e * g / len(notes)
def pluck(n, d=0.3, g=0.25):
    t = tt(d); s = saw(note(n), d) + 0.5 * saw(note(n + 12), d)
    return lp(s, 2500) * np.exp(-t / 0.09) * g
def sub(n, d, g=0.5):
    t = tt(d); s = np.sin(2 * np.pi * note(n) * t) + 0.3 * np.sin(4 * np.pi * note(n) * t)
    return s * np.minimum(1, t / 0.01) * np.exp(-t / (d * 0.8)) * g


def reverb(x, sec=1.6, mix=0.18):
    ir = rng.standard_normal(int(sec * SR)) * np.exp(-tt(sec) / (sec / 5))
    ir = lp(ir, 5000); ir /= np.abs(ir).sum() ** 0.5 * 30
    wet = np.stack([fftconvolve(x[:, c], ir)[: N] for c in range(2)], 1)
    return x * (1 - mix) + wet * mix * 3


# ---------- düzenleme (reel_v7 zaman çizelgesi, gerçek saniye) ----------
mus, sfx = buf(), buf()
CH = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]   # Am F C G
BASS = [45, 41, 36, 43]

def groove(t0, t1, full=True):
    nb = int(round((t1 - t0) / BEAT))
    for b in range(nb):
        t = t0 + b * BEAT; ch = (b // 4) % 4
        add(mus, kick(), t, 0.85)
        if b % 2 == 1: add(mus, clap(), t, 0.55 if full else 0.35)
        for h in range(2):
            add(mus, hat(open_=(h == 1 and b % 4 == 3)), t + h * BEAT / 2, 0.5 if full else 0.35, pan=0.25)
        add(mus, sub(BASS[ch], BEAT * 0.95, 0.42), t, 1.0)
        if b % 4 == 0: add(mus, pad(CH[ch], BEAT * 4, 0.13, 2200), t, 1.0)
        if full:
            for k in range(4):
                n = CH[ch][(b * 4 + k) % 3] + 12 + (12 if k == 3 else 0)
                add(mus, pluck(n, 0.25, 0.16), t + k * BEAT / 4, 1.0, pan=(-0.35 if k % 2 else 0.35))

# HOOK (0–4): ilk karede vuruş, ritim hemen başlar (yalın açılış yok), sonuna doğru yükselen gerilim
add(sfx, boom(), 0.0, 0.7); add(sfx, whoosh(0.35), 0.0, 0.4)
groove(0.0, 4.0, full=False)
add(mus, riser(1.6), 2.4, 0.5)
# MARKA (4–7): büyük vuruş, tam ritim
add(sfx, boom(), 4.0, 0.9); add(sfx, clap(), 4.0, 0.7); add(sfx, whoosh(0.5), 3.6, 0.5)
groove(4.0, 7.0)
# 10 SÜREÇ ADIMI (7–27): tam ritim, her adım değişiminde kaydırma + onay tıkı
groove(7.0, 27.0)
for k in range(10):
    t = 7.0 + k * 2.0
    add(sfx, whoosh(0.3), t - 0.15, 0.35, pan=0.3); add(sfx, tick(), t + 0.12, 0.5)
add(mus, riser(2.0), 25.0, 0.4)
# KAPANIŞ (27–33): büyük vuruş, çözülen akor, CTA ve iletişim kartı efektleri
add(sfx, boom(), 27.0, 0.8); add(sfx, whoosh(0.4, False), 26.7, 0.5)
groove(27.0, 29.0, full=False)
add(mus, pad((57, 60, 64, 69), DUR - 29.0, 0.16, 2600), 29.0, 1.0)
add(mus, sub(33, 3.0, 0.5), 29.0, 1.0)
add(sfx, tick(), 29.95, 0.5)             # CTA butonu
add(sfx, thud(), 30.2, 0.5)              # iletişim kartı
for t in (30.55, 30.8): add(sfx, tick(), t, 0.4)   # ikonlar

# ---------- miks ----------
mus = reverb(mus, 1.8, 0.2); sfx = reverb(sfx, 1.0, 0.12)
fade = np.ones(N); nf = int(0.3 * SR); fade[-nf:] = np.linspace(1, 0, nf)
mus *= fade[:, None]; sfx *= fade[:, None]
def norm(x, peak): return x / (np.abs(x).max() + 1e-9) * peak
mus, sfx = norm(mus, 0.7), norm(sfx, 0.8)
mix = np.tanh((mus * 0.8 + sfx * 0.75) * 1.2) * 0.9
import wave
def wav(path, x):
    x = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes())
p = sys.argv[1]
wav(p + "_muzik.wav", mus); wav(p + "_efekt.wav", sfx); wav(p + "_mix.wav", mix)
print("ok", DUR, "sn")
