"""Reels üretimi yardımcı araçları (ffmpeg + Pillow). Her komut kendi başına çalışır.

  probe    VIDEO                                   süre, çözünürlük, fps
  sheet    VIDEO OUT.jpg [--every 2] [--cols 8]    temas tabakası (her N sn bir kare)
  times    VIDEO OUT.jpg t1,t2,...                 belirli saniyelerden kareler yan yana (kesim noktası bulmak için)
  seg      VIDEO OUTDIR --ss S --t D --w W --h H [--fx 0.5] [--fy 0.5] [--speed 1.0] [--box x,y,w,h]
                                                   30 fps kare çıkarır, W×H'ye doldurur (cover), fx/fy odak
  sharp    DIR [DIR ...]                           keskinlik ölçümü (kenar varyansı; düşük = bulanık)
  segsheet SEGROOT OUT.jpg                         seg klasörlerinin ilk/orta/son karesi (insan/kapı/filigran kontrolü)

Notlar:
- Her ffmpeg çağrısı -nostdin ile: while-read döngüsünde stdin'i yutmasın.
- -ss girişten önce: hızlı ve kare doğru. Sheet karelerinden zaman tahmini YAPMA; 'times' ile doğrula.
"""
import argparse, glob, json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def sh(cmd): return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def probe(v):
    j = json.loads(sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", v]))
    vs = [s for s in j["streams"] if s["codec_type"] == "video"][0]
    return float(j["format"]["duration"]), vs["width"], vs["height"], vs.get("r_frame_rate")


def cmd_probe(a): print(*probe(a.video))


def cmd_sheet(a):
    d, w, h, _ = probe(a.video)
    sh(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", a.video, "-vf",
        f"fps=1/{a.every},scale=240:-1,tile={a.cols}x{int(d / a.every / a.cols) + 1}", "-frames:v", "1", a.out])
    print(a.out, f"(satır başına {a.cols} kare, kare arası {a.every} sn)")


def cmd_times(a):
    ims = []
    for t in a.times.split(","):
        tmp = f"/tmp/_t_{t}.jpg"
        sh(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", t, "-i", a.video, "-frames:v", "1", "-vf", "scale=200:-1", tmp])
        ims.append((t, Image.open(tmp)))
    W = sum(i.width for _, i in ims); H = max(i.height for _, i in ims) + 16
    out = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(out); x = 0
    for t, i in ims: out.paste(i, (x, 16)); d.text((x + 2, 1), t, fill="red"); x += i.width
    out.save(a.out); print(a.out)


def cmd_seg(a):
    os.makedirs(a.outdir, exist_ok=True)
    vf = []
    if a.box: x, y, w, h = a.box.split(","); vf.append(f"crop={w}:{h}:{x}:{y}")
    if a.speed != 1.0: vf.append(f"setpts=PTS/{a.speed}")
    vf += ["fps=30", f"scale={a.w}:{a.h}:force_original_aspect_ratio=increase:flags=lanczos",
           f"crop={a.w}:{a.h}:(iw-{a.w})*{a.fx}:(ih-{a.h})*{a.fy}", "setsar=1"]
    sh(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(a.ss), "-t", str(a.t * a.speed), "-i", a.video,
        "-vf", ",".join(vf), "-q:v", "2", os.path.join(a.outdir, "%04d.jpg")])
    print(a.outdir, len(glob.glob(os.path.join(a.outdir, "*.jpg"))), "kare")


def sharp(path):
    im = Image.open(path).convert("L"); return np.asarray(im.filter(ImageFilter.FIND_EDGES), float).var()


def cmd_sharp(a):
    for d in a.dirs:
        fs = sorted(glob.glob(os.path.join(d, "*.jpg")))
        if fs: print(f"{os.path.basename(d.rstrip('/')):14s} {Image.open(fs[0]).size}  keskinlik={sharp(fs[len(fs) // 2]):8.1f}")


def cmd_segsheet(a):
    ds = sorted(d for d in glob.glob(os.path.join(a.root, "*")) if os.path.isdir(d))
    out = Image.new("RGB", (680, 130 * len(ds)), "white"); dr = ImageDraw.Draw(out)
    for r, d in enumerate(ds):
        fs = sorted(glob.glob(os.path.join(d, "*.jpg")))
        for c, i in enumerate([0, len(fs) // 2, len(fs) - 1] if fs else []):
            t = Image.open(fs[i]); t.thumbnail((200, 120)); out.paste(t, (80 + c * 200, r * 130))
        dr.text((2, r * 130 + 50), os.path.basename(d), fill="red")
    out.save(a.out); print(a.out)


ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
p = sp.add_parser("probe"); p.add_argument("video"); p.set_defaults(f=cmd_probe)
p = sp.add_parser("sheet"); p.add_argument("video"); p.add_argument("out"); p.add_argument("--every", type=float, default=2); p.add_argument("--cols", type=int, default=8); p.set_defaults(f=cmd_sheet)
p = sp.add_parser("times"); p.add_argument("video"); p.add_argument("out"); p.add_argument("times"); p.set_defaults(f=cmd_times)
p = sp.add_parser("seg"); p.add_argument("video"); p.add_argument("outdir")
for k, t, dv in [("--ss", float, 0), ("--t", float, 3), ("--w", int, 1080), ("--h", int, 1920), ("--fx", float, 0.5), ("--fy", float, 0.5), ("--speed", float, 1.0)]:
    p.add_argument(k, type=t, default=dv)
p.add_argument("--box", default=""); p.set_defaults(f=cmd_seg)
p = sp.add_parser("sharp"); p.add_argument("dirs", nargs="+"); p.set_defaults(f=cmd_sharp)
p = sp.add_parser("segsheet"); p.add_argument("root"); p.add_argument("out"); p.set_defaults(f=cmd_segsheet)
A = ap.parse_args(); A.f(A)
