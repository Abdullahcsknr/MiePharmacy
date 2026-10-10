"""Mie tanıtım videosu — sahne şablonu (prototip).

Referans stil: koyu zemin, yüzen toz partikülleri, serif başlıkta kelime kelime
bulanıklıktan netleşme, ortada pencere çerçeveli kart içinde arşiv görüntüsü.

Kullanım:
  python3 render.py --foot DIR_PNG --out out.mp4 --fonts FONT_DIR \
      --title "Formülden|rafa." --label "DOLUM" --seconds 6
"""
import argparse, glob, math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 25

# Renkler — kurumsal kimlik netleşince buradan değişecek
BG = (16, 17, 17)
CARD_BAR = (28, 30, 30)
DOT = (88, 90, 90)
LABEL = (205, 207, 207)
TITLE = (232, 230, 225)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def background(seed=7):
    """Büyük, bulanık, düşük kontrastlı lekeler — bir kez hesaplanır, kaydırılarak kullanılır."""
    random.seed(seed)
    s = 4
    small = Image.new("RGB", (W * 2 // s, H * 2 // s), BG)
    d = ImageDraw.Draw(small)
    for _ in range(9):
        x, y = random.randint(0, small.width), random.randint(0, small.height)
        r = random.randint(60, 160)
        c = random.choice([(34, 36, 36), (8, 8, 8), (40, 42, 41), (4, 4, 4)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    small = small.filter(ImageFilter.GaussianBlur(45))
    return small.resize((W * 2, H * 2), Image.BICUBIC)


def vignette():
    v = Image.new("L", (W // 4, H // 4), 0)
    d = ImageDraw.Draw(v)
    for i in range(60):
        a = int(150 * (1 - i / 60) ** 2)
        d.rectangle([i, i, v.width - i, v.height - i], outline=a)
    return v.filter(ImageFilter.GaussianBlur(20)).resize((W, H), Image.BICUBIC)


def particles(n=70, seed=3):
    random.seed(seed)
    return [(random.uniform(0, W), random.uniform(0, H), random.uniform(1.2, 3.2),
             random.uniform(-6, 6), random.uniform(-14, -4), random.uniform(0, 6.28)) for _ in range(n)]


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255)
    return m


def cover(img, size, zoom=1.0):
    tw, th = size
    sc = max(tw / img.width, th / img.height) * zoom
    im = img.resize((int(img.width * sc + 1), int(img.height * sc + 1)), Image.LANCZOS)
    x, y = (im.width - tw) // 2, (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--foot", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--title", default="Formülden|rafa.")
    ap.add_argument("--label", default="DOLUM")
    ap.add_argument("--seconds", type=float, default=6)
    a = ap.parse_args()

    f_title = ImageFont.truetype(os.path.join(a.fonts, "cormorant-garamond-400.ttf"), 112)
    f_label = ImageFont.truetype(os.path.join(a.fonts, "jetbrains-mono-500.ttf"), 22)
    feet = sorted(glob.glob(os.path.join(a.foot, "*.png")))
    bg_big, vig, parts = background(), vignette(), particles()

    cw, ch, bar, rad = 640, 840, 56, 30
    cx, cy = (W - cw) // 2, 690
    mask = rounded_mask((cw, ch), rad)
    words = a.title.split("|")

    frames_dir = a.out + "_frames"
    os.makedirs(frames_dir, exist_ok=True)
    n = int(a.seconds * FPS)
    for i in range(n):
        t = i / FPS
        # zemin: yavaş kayan lekeler + vinyet
        ox = int(W / 2 + 60 * math.sin(t * 0.25))
        oy = int(H / 2 + 80 * math.cos(t * 0.18))
        frame = bg_big.crop((ox, oy, ox + W, oy + H))
        frame = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), frame, vig)

        # partiküller
        pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pl)
        for x, y, r, vx, vy, ph in parts:
            px, py = (x + vx * t) % W, (y + vy * t) % H
            al = int(70 + 60 * math.sin(t * 1.3 + ph))
            pd.ellipse([px - r, py - r, px + r, py + r], fill=(220, 220, 215, al))
        frame.paste(pl, (0, 0), pl)

        # kart: gölge + çerçeve + görüntü
        k = ease_out((t - 0.3) / 1.0)
        if k > 0:
            off = int(90 * (1 - k))
            sh = Image.new("RGBA", (cw + 200, ch + 200), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle([100, 130, 100 + cw, 130 + ch], rad, fill=(0, 0, 0, int(190 * k)))
            sh = sh.filter(ImageFilter.GaussianBlur(40))
            frame.paste(sh, (cx - 100, cy - 100 + off), sh)

            card = Image.new("RGB", (cw, ch), CARD_BAR)
            src = Image.open(feet[min(i, len(feet) - 1)]).convert("RGB")
            card.paste(cover(src, (cw, ch - bar), zoom=1.10 - 0.08 * (t / a.seconds)), (0, bar))
            cd = ImageDraw.Draw(card)
            for j in range(3):
                x0 = 28 + j * 22
                cd.ellipse([x0, bar // 2 - 6, x0 + 12, bar // 2 + 6], fill=DOT)
            lx = 110
            for ch_ in a.label:  # harf aralığı açık mono etiket
                cd.text((lx, bar // 2), ch_, font=f_label, fill=LABEL, anchor="lm")
                lx += f_label.getlength(ch_) + 5
            al = Image.new("L", (cw, ch), 0)
            al.paste(mask.point(lambda v: int(v * k)), (0, 0))
            frame.paste(card, (cx, cy + off), al)

        # başlık: kelime kelime bulanıktan netleşme
        tl = Image.new("RGBA", (W, 400), (0, 0, 0, 0))
        x = 96
        for wi, w in enumerate(words):
            p = ease_out((t - 0.2 - wi * 0.55) / 0.9)
            if p > 0:
                wl = Image.new("RGBA", (W, 400), (0, 0, 0, 0))
                ImageDraw.Draw(wl).text((x + int(24 * (1 - p)), 200), w, font=f_title,
                                        fill=TITLE + (int(255 * p),), anchor="ls")
                if p < 1:
                    wl = wl.filter(ImageFilter.GaussianBlur(16 * (1 - p)))
                tl = Image.alpha_composite(tl, wl)
            x += f_title.getlength(w + " ")
        frame.paste(tl, (0, 230), tl)

        frame.save(os.path.join(frames_dir, f"{i:04d}.png"))

    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i",
                    os.path.join(frames_dir, "%04d.png"), "-c:v", "libx264", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], check=True)
    print("ok", a.out)


if __name__ == "__main__":
    main()
