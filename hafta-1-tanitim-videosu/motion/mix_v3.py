"""Fason v7 miksajı: seslendirme + müzik + efekt (müzik konuşma altında kısılır).

Kullanım: python3 mix_v3.py VO_DIR MUZIK.wav EFEKT.wav OUT.wav
"""
import argparse, subprocess, wave
import numpy as np

SR = 44100
ap = argparse.ArgumentParser()
ap.add_argument("vo"); ap.add_argument("muzik"); ap.add_argument("efekt"); ap.add_argument("out")
A = ap.parse_args()

# (dosya, başlangıç sn): reel_v7 sahne zamanları
CUES = [("v7_01_hook.mp3", 0.1), ("v7_02_marka.mp3", 4.2), ("v7_03_surec1.mp3", 7.2), ("v7_04_surec2.mp3", 13.2),
        ("v7_05_surec3.mp3", 19.2), ("v7_06_surec4.mp3", 23.2), ("v7_07_kapanis.mp3", 27.3), ("v7_08_cagri.mp3", 30.2)]


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
