"""Seslendirme + müzik + efekt miksajı (müzik konuşma altında kısılır).

v10+: seslendirme hızlandırılabilir (--tempo, perde korunur; başlangıç zamanları aynı kalır).

Kullanım: python3 mix_v3b.py VO_DIR MUZIK.wav EFEKT.wav OUT.wav [--marka 03_marka.mp3] [--tempo 1.15]
"""
import argparse, subprocess, wave
import numpy as np

SR = 44100
ap = argparse.ArgumentParser()
ap.add_argument("vo"); ap.add_argument("muzik"); ap.add_argument("efekt"); ap.add_argument("out")
ap.add_argument("--marka", default="03_marka.mp3")
ap.add_argument("--tempo", type=float, default=1.0)
A = ap.parse_args()

# (dosya, başlangıç sn): reel_v3 sahne zamanlarına göre (gerçek saniye)
CUES = [("01_hook.mp3", 0.05), ("02_vaat.mp3", 2.55), (A.marka, 5.65), ("04_kanit.mp3", 8.5),
        ("05_sure.mp3", 19.1), ("06_kapanis.mp3", 22.5), ("07_cagri.mp3", 24.85)]   # v4 (ilk 9 sn çıkarıldı)


def load(path, tempo=1.0):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af", f"atempo={tempo}", "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<i2").reshape(-1, 2).astype(float) / 32768


mus, sfx = load(A.muzik), load(A.efekt)
n = min(len(mus), len(sfx)); mus, sfx = mus[:n], sfx[:n]
N = len(mus); vo = np.zeros((N, 2))
for f, t0 in CUES:
    x = load(f"{A.vo}/{f}", A.tempo); i = int(t0 * SR); x = x[: N - i]; vo[i:i + len(x)] += x

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
