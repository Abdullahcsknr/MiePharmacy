"""Mie kozmetik Reels — müzik + efekt (kodla), reel_k1 zaman çizelgesine kilitli. 120 BPM."""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
TS = 1.3                      # reel_v2 zaman ölçeği
DUR = 28.0
SHIFT = 6.5                   # eski zaman çizelgesinden kaydırma (gerçek sn)
N = int(DUR * SR)
BEAT = 0.5                    # 120 BPM; tüm sahne kesmeleri (3, 7, 10.5 …) bu ızgaraya düşer
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


# ---------- düzenleme (kozmetik: daha yumuşak, ferah) ----------
mus, sfx = buf(), buf()
CH = [(52, 56, 59, 64), (49, 52, 56, 61), (45, 49, 52, 57), (47, 51, 54, 59)]   # E C#m A B (sıcak, aydınlık)
BASS = [40, 37, 33, 35]
# HOOK 0–3: ped + damla parıltıları
add(mus, pad(CH[0], 3.2, 0.12, 1600), 0, 1.0)
for k in range(6): add(mus, pluck(CH[0][k % 4] + 24, 0.4, 0.12), 0.25 + k * 0.45, 0.8, pan=(-0.4 if k % 2 else 0.4))
# CEVAP 3–7: hafif ritim girer, pencere açılışlarında tık
for b in range(8):
    t0 = 3.0 + b * BEAT
    add(mus, hat(), t0 + BEAT / 2, 0.3, pan=0.25)
    if b % 2 == 0: add(mus, kick(0.5), t0, 0.35)
add(mus, pad(CH[1], 4.0, 0.11, 1800), 3.0, 1.0)
for k in range(6): add(sfx, tick(), 3.1 + k * 0.18 + 0.2, 0.35)
add(sfx, whoosh(0.5, False), 5.75, 0.4)       # "değildir": pencereler kapanır
add(mus, riser(1.0) * 0.6, 6.0, 0.5)
# 7–24: ana bölüm
start = 7.0
for b in range(int((24.0 - start) / BEAT)):
    t0 = start + b * BEAT; ch = (b // 8) % 4
    add(mus, kick(0.75), t0, 0.6 if b % 2 == 0 else 0.0)
    if b % 4 == 2: add(mus, clap(), t0, 0.35)
    add(mus, hat(open_=(b % 4 == 3)), t0 + BEAT / 2, 0.35, pan=0.25)
    add(mus, sub(BASS[ch], BEAT * 0.9, 0.35), t0, 0.9)
    if b % 8 == 0: add(mus, pad(CH[ch], BEAT * 8, 0.12, 2400), t0, 1.0)
    for k in range(2):
        n = CH[ch][(b * 2 + k) % 4] + 12
        add(mus, pluck(n, 0.35, 0.13), t0 + k * BEAT / 2, 1.0, pan=(-0.3 if k else 0.3))
add(sfx, boom() * 0.5, 7.0, 0.5)
for a in (10.5, 13.5, 16.5, 20.0, 24.0): add(sfx, whoosh(0.4), a - 0.3, 0.35)
add(sfx, tick(), 10.95, 0.5); add(sfx, tick(), 13.95, 0.5)
for k in range(3): add(sfx, tick(), 21.8 + k * 0.2, 0.4)      # etiketler
for k in range(2): add(sfx, tick(), 25.15 + k * 0.25, 0.45)   # iletişim ikonları
# ÇAĞRI 24–28: çözülen akor
add(mus, pad((52, 56, 59, 64, 68), DUR - 24.0, 0.15, 2800), 24.0, 1.0)
add(mus, sub(40, 3.5, 0.4), 24.0, 1.0)

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
