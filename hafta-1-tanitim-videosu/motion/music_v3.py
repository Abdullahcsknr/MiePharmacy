"""Mie fason Reels — müzik + efekt (kodla üretim), reel_v2 zaman çizelgesine kilitli.

Çıktılar: <out>_muzik.wav, <out>_efekt.wav, <out>_mix.wav (44.1 kHz stereo)
Kullanım: python3 music_v1.py OUT_PREFIX
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
TS = 1.3                      # reel_v2 zaman ölçeği
DUR = 21.3 * TS               # 27.7 sn (v4: ilk 9 sn çıkarıldı)
SHIFT = 6.5                   # eski zaman çizelgesinden kaydırma (gerçek sn)
N = int(DUR * SR)
BEAT = 0.5 * TS               # 0.65 sn → 92.3 BPM; tüm sahne kesmeleri bu ızgaraya düşer
rng = np.random.default_rng(3)
T = lambda a: a * TS - SHIFT  # animasyon saniyesi (eski çizelge) → yeni gerçek saniye


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


# ---------- düzenleme ----------
mus, sfx = buf(), buf()
CH = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]   # Am F C G
BASS = [45, 41, 36, 43]

# AÇILIŞ (0–5.2): kapıya yürürken sakin ped + yükselen gerilim, hook ve vaatte hafif vuruş
add(mus, pad(CH[0], 2.6, 0.12, 1000), 0, 1.0)
add(mus, pad(CH[1] + (65,), 2.8, 0.11, 1400), 2.4, 1.0)
add(sfx, kick(0.8), 0.05, 0.7); add(sfx, kick(0.7), 2.45, 0.6)
add(mus, riser(T(9.0) - 2.6), 2.6, 0.5)

# REVEAL'dan sona (11.7–32.5): 92,3 BPM ritim
start = T(9.0)
add(sfx, boom(), start, 0.9); add(sfx, whoosh(0.6), start - 0.45, 0.6)
nbeats = int((T(22.0) + 2 * BEAT - start) / BEAT)   # outro'nun ilk 2 vuruşuna kadar ritim
for b in range(nbeats):
    t0 = start + b * BEAT; bar = b // 4; ch = bar % 4
    add(mus, kick(), t0, 0.85)
    if b % 2 == 1: add(mus, clap(), t0, 0.55)
    for h in range(2):
        add(mus, hat(open_=(h == 1 and b % 4 == 3)), t0 + h * BEAT / 2, 0.5, pan=0.25)
    add(mus, sub(BASS[ch], BEAT * 0.95, 0.42), t0, 1.0)   # bas
    if b % 4 == 0: add(mus, pad(CH[ch], BEAT * 4, 0.13, 2200), t0, 1.0)
    # 16'lık arpej: "hassas üretim" hissi
    for k in range(4):
        n = CH[ch][(b * 4 + k) % 3] + 12 + (12 if k == 3 else 0)
        add(mus, pluck(n, 0.25, 0.16), t0 + k * BEAT / 4, 1.0, pan=(-0.35 if k % 2 else 0.35))
# sahne kesmelerinde vurgu
for a in (11.5, 14.0, 17.0, 19.5):
    add(sfx, whoosh(0.4), T(a) - 0.3, 0.45)
# adım onay tıkları
for i in range(4):
    add(sfx, tick(), T(14.0 + 0.55 + i * 0.7), 0.6)
for k in range(3):
    add(sfx, tick(), T(17.0 + 0.4 + k * 0.5), 0.45)

# OUTRO (28.6–32.5): çözülen akor + son vuruş, döngüye hazır kuyruk
o = T(22.0) + 2 * BEAT
add(mus, pad((57, 60, 64, 69), DUR - o, 0.16, 2600), o, 1.0)
add(mus, sub(33, 2.5, 0.5), o, 1.0)
add(sfx, boom(), o, 0.5)
add(sfx, tick(), T(22.0 + 1.5), 0.5)   # CTA butonu

# ---------- miks ----------
mus = reverb(mus, 1.8, 0.2); sfx = reverb(sfx, 1.0, 0.12)
fade = np.ones(N); nf = int(0.25 * SR); fade[-nf:] = np.linspace(1, 0, nf)
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
