"""Seslendirme + müzik + efekt miksajı (müzik konuşma altında kısılır).

Kullanım: python3 mix_v1.py VO_DIR MUZIK.wav EFEKT.wav OUT.wav [--marka 03_marka.mp3]
"""
import argparse, subprocess, wave
import numpy as np

SR = 44100
ap = argparse.ArgumentParser()
ap.add_argument("vo"); ap.add_argument("muzik"); ap.add_argument("efekt"); ap.add_argument("out")

A = ap.parse_args()

# (dosya, başlangıç sn): reel_v3 sahne zamanlarına göre (gerçek saniye)
CUES = [("k01_hook.mp3", 0.1), ("k02_cevap.mp3", 3.3), ("k03_icgoru.mp3", 7.15), ("k04_urun1.mp3", 10.9),
        ("k05_urun2.mp3", 13.75), ("k06_guven.mp3", 19.3), ("k07_marka.mp3", 22.8), ("k08_cagri.mp3", 27.0)]   # kozmetik k2


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<i2").reshape(-1, 2).astype(float) / 32768


mus, sfx = load(A.muzik), load(A.efekt)
N = len(mus); vo = np.zeros((N, 2))
for f, t0 in CUES:
    x = load(f"{A.vo}/{f}"); i = int(t0 * SR); x = x[: N - i]; vo[i:i + len(x)] += x

# sidechain: konuşma varken müzik -10 dB, efekt -4 dB (atak 40 ms, bırakma 350 ms)
lvl = np.abs(vo).max(1); win = int(0.02 * SR)
lvl = np.convolve(lvl, np.ones(win) / win, "same"); gate = (lvl > 0.01).astype(float)
env = np.zeros(N); a, r = np.exp(-1 / (0.04 * SR)), np.exp(-1 / (0.35 * SR)); e = 0.0
for i in range(N):
    g = gate[i]; e = (a * e + (1 - a) * g) if g > e else (r * e + (1 - r) * g); env[i] = e
duck_m = 1 - env * (1 - 10 ** (-10 / 20)); duck_s = 1 - env * (1 - 10 ** (-4 / 20))

vo /= np.abs(vo).max() + 1e-9
mix = vo * 0.95 + mus * duck_m[:, None] * 0.55 + sfx * duck_s[:, None] * 0.6
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
with wave.open(A.out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
print("ok", A.out, len(mix) / SR, "sn")
