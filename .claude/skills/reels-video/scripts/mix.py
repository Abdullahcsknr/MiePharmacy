"""Seslendirme + müzik + efekt miksajı. Müzik konuşma altında -10 dB, efekt -4 dB kısılır (sidechain).

Kullanım:
  python3 mix.py VO_DIR MUZIK.wav EFEKT.wav OUT.wav --cues "01_hook.mp3:0.05,02_vaat.mp3:2.55,..." [--tempo 1.25]
  --tempo: seslendirmeyi perdeyi bozmadan hızlandırır (ffmpeg atempo). Başlangıç zamanları değişmez;
           render tarafında altyazı kelime hızını da aynı orana böl (VO_SPEED).
Sonra videoya:
  ffmpeg -i sessiz.mp4 -i OUT.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k -ar 44100 -shortest final.mp4
"""
import argparse, subprocess, wave
import numpy as np

SR = 44100
ap = argparse.ArgumentParser()
ap.add_argument("vo"); ap.add_argument("muzik"); ap.add_argument("efekt"); ap.add_argument("out")
ap.add_argument("--cues", required=True); ap.add_argument("--tempo", type=float, default=1.0)
A = ap.parse_args()
CUES = [(c.rsplit(":", 1)[0], float(c.rsplit(":", 1)[1])) for c in A.cues.split(",")]


def load(path, tempo=1.0):
    af = ["-af", f"atempo={tempo}"] if tempo != 1.0 else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, *af, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<i2").reshape(-1, 2).astype(float) / 32768


mus, sfx = load(A.muzik), load(A.efekt)
n = min(len(mus), len(sfx)); mus, sfx = mus[:n], sfx[:n]   # stem uzunlukları birkaç örnek farklı olabilir
N = n; vo = np.zeros((N, 2))
for f, t0 in CUES:
    x = load(f"{A.vo}/{f}", A.tempo); i = int(t0 * SR); x = x[: N - i]; vo[i:i + len(x)] += x
    print(f"{f:28s} {t0:6.2f} → {t0 + len(x) / SR:6.2f} sn")

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
print("ok", A.out, round(N / SR, 2), "sn")
