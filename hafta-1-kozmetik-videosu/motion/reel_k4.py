"""Mie kozmetik sayfası Reels — k4: müşterinin 10 fason üretim süreci (reels-video skill, v15 motoru).

Kullanım: python3 reel_k4.py SEG_DIR PROJE_DIR OUT.mp4 [--stills t1,t2,...]
  SEG_DIR: hook, title, k01..k10 (1080×1920, 30 fps). PROJE_DIR: motion/fonts + kimlik/logo-mie-siyah-hd.png
Zaman gerçek saniye (TS=1). Seslendirme yokken de okunur: her adım ekranda numara + ad kartıyla.
"""
import argparse, glob, math, os, subprocess, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 30.5
TS = 1.0
VO_SPEED = 1.10
HANDLE = "@mie_cosmeticss"
OR = (255, 100, 24); WH = (255, 255, 255); GR = (85, 85, 85); LG = (244, 244, 244); INK = (20, 20, 20)
HOOK_END, TITLE_END, STEP0, STEP_D, OUTRO = 3.0, 5.5, 5.5, 2.0, 25.5
STEPS = ["Müşteri Talebi ve Ürün Planlaması", "AR-GE ve Formülasyon Geliştirme", "Numune Hazırlama ve Onay Süreci",
         "Hammadde ve Ambalaj Tedariki", "Üretim Planlaması ve Hazırlık", "Kozmetik Ürün Üretimi",
         "Kalite Kontrol ve Analiz Süreçleri", "Dolum, Etiketleme ve Paketleme", "Nihai Ürün Kontrolü", "Sevkiyat ve Teslimat"]

ap = argparse.ArgumentParser()
ap.add_argument("seg"); ap.add_argument("repo"); ap.add_argument("out")
ap.add_argument("--from", dest="t0", type=float, default=0); ap.add_argument("--to", dest="t1", type=float, default=DUR)
ap.add_argument("--stills", default="")
A = ap.parse_args()
FD = os.path.join(A.repo, "motion/fonts")
AN = functools.lru_cache(None)(lambda s: ImageFont.truetype(f"{FD}/anton-400.ttf", s))
PO = functools.lru_cache(None)(lambda w, s: ImageFont.truetype(f"{FD}/poppins-{w}.ttf", s))
LOGO = Image.open(os.path.join(A.repo, "kimlik/logo-mie-siyah-hd.png")).convert("RGBA")


def _icon_ig():
    s = 4; n = 46 * s; im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([2 * s, 2 * s, n - 2 * s, n - 2 * s], 13 * s, outline=OR, width=4 * s)
    d.ellipse([13 * s, 13 * s, n - 13 * s, n - 13 * s], outline=OR, width=4 * s)
    d.ellipse([32 * s, 8 * s, 37 * s, 13 * s], fill=OR)
    return im.resize((46, 46), Image.LANCZOS)


def _icon_web():
    s = 4; n = 46 * s; im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = 4 * s
    d.ellipse([2 * s, 2 * s, n - 2 * s, n - 2 * s], outline=OR, width=w)
    d.ellipse([14 * s, 2 * s, n - 14 * s, n - 2 * s], outline=OR, width=w)
    d.line([(2 * s, n // 2), (n - 2 * s, n // 2)], fill=OR, width=w)
    d.line([(6 * s, 14 * s), (n - 6 * s, 14 * s)], fill=OR, width=w // 2 * 2)
    d.line([(6 * s, n - 14 * s), (n - 6 * s, n - 14 * s)], fill=OR, width=w // 2 * 2)
    return im.resize((46, 46), Image.LANCZOS)


ICON_IG, ICON_WEB = _icon_ig(), _icon_web()


# ---------- yardımcılar ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, s, d): return clamp((t - s) / d)
def eo(x): return 1 - (1 - x) ** 3
def eback(x, k=1.70158):
    x = clamp(x) - 1; return 1 + (k + 1) * x ** 3 + k * x ** 2
def lerp(a, b, x): return a + (b - a) * x

@functools.lru_cache(None)
def frames(name):
    return sorted(glob.glob(os.path.join(A.seg, name, "*.jpg")))

def foot(name, lt):
    fs = frames(name); i = min(len(fs) - 1, max(0, int(lt * TS * FPS)))
    return Image.open(fs[i]).convert("RGB")

@functools.lru_cache(None)
def txt(s, font_key, color):
    kind, *a = font_key
    f = AN(*a) if kind == "AN" else PO(*a)
    b = f.getbbox(s); im = Image.new("RGBA", (b[2] - b[0] + 8, b[3] - b[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - b[0], 4 - b[1]), s, font=f, fill=color); return im

def put(fr, im, x, y, alpha=1.0, scale=1.0, anchor="lt"):
    if alpha <= 0.01 or scale <= 0.01: return
    if abs(scale - 1) > 0.005:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if alpha < 0.999:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    if anchor == "c": x, y = x - im.width // 2, y - im.height // 2
    fr.paste(im, (int(x), int(y)), im)

@functools.lru_cache(None)
def rmask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); return m

@functools.lru_cache(None)
def shadow(w, h, r, a=70, blur=28):
    s = Image.new("RGBA", (w + 160, h + 160), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([80, 100, 80 + w, 100 + h], r, fill=(0, 0, 0, a)); return s.filter(ImageFilter.GaussianBlur(blur))

def window(fr, src, lab, x, y, w, h, alpha=1.0, scale=1.0, rad=28, bar=54, shad=True):
    c = Image.new("RGBA", (w, h), WH + (255,)); c.paste(src.resize((w, h - bar)) if src.size != (w, h - bar) else src, (0, bar))
    d = ImageDraw.Draw(c)
    big = bar > 45; r, gap, x0 = (7, 22, 24) if big else (5, 15, 16)
    for j, col in enumerate([OR, (210, 210, 210), (210, 210, 210)]):
        d.ellipse([x0 + j * gap, bar // 2 - r, x0 + j * gap + 2 * r, bar // 2 + r], fill=col)
    lx = x0 + 2 * gap + 2 * r + (14 if big else 10); fs = 22 if big else 17
    while fs > 11 and PO("800", fs).getlength(lab) > w - lx - 12: fs -= 1   # başlık pencereye sığana kadar küçült
    d.text((lx, bar // 2), lab, font=PO("800", fs), fill=GR, anchor="lm")
    c.putalpha(rmask(w, h, rad))
    if shad: put(fr, shadow(w, h, rad), x - 80 + (w - w * scale) / 2, y - 80 + (h - h * scale) / 2, alpha, scale)
    put(fr, c, x + (w - w * scale) / 2, y + (h - h * scale) / 2, alpha, scale)

@functools.lru_cache(None)
def chip_img(t, state):
    f = PO("800", 36); tw = f.getlength(t); w, h = int(tw + (118 if state else 64)), 88
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 20, fill=WH, outline=OR if not state else (230, 230, 230), width=4)
    tx = 32
    if state:
        d.ellipse([24, 22, 68, 66], fill=OR); d.line([(35, 44), (44, 54), (58, 34)], fill=WH, width=7); tx = 84
    d.text((tx, h // 2), t, font=f, fill=INK, anchor="lm"); return c

@functools.lru_cache(None)
def chip_rot(t, rot): return chip_img(t, 0).rotate(rot, expand=True, resample=Image.BICUBIC)

def shade(fr, y0, y1, a=200):
    g = Image.linear_gradient("L").resize((1, y1 - y0)).point(lambda v: int(v * a / 255))
    m = Image.new("L", (W, H), 0); m.paste(g.resize((W, y1 - y0)), (0, y0)); m.paste(a, (0, y1, W, H))
    fr.paste((0, 0, 0), (0, 0, W, H), m)

def band(fr, y0, y1, a):
    """Yalnız yazının olduğu bantta yumuşak gölge: üstte ve altta sıfıra iner (tam ekran karartma yok)."""
    import math as _m
    col = Image.new("L", (1, y1 - y0))
    for i in range(y1 - y0): col.putpixel((0, i), int(a * _m.sin(_m.pi * i / (y1 - y0)) ** 0.8))
    m = Image.new("L", (W, H), 0); m.paste(col.resize((W, y1 - y0)), (0, y0))
    fr.paste((0, 0, 0), (0, 0, W, H), m)


def caption(fr, words, t, start, per, y, size=70, mx=820):
    """Reels altyazısı: kelime kelime belirir, okunan kelime turuncu kutuda."""
    f = PO("900", size); lines = [[]]
    for w in words:
        if f.getlength(" ".join(lines[-1] + [w])) > mx and lines[-1]: lines.append([w])
        else: lines[-1].append(w)
    k = 0; d = ImageDraw.Draw(fr); act = int((t - start) / per)
    for ln in lines:
        x = 80
        for w in ln:
            p = prog(t, start + k * per, 0.18)
            if p > 0:
                bw = f.getlength(w)
                if p > 0.6 and (k == act or (k == len(words) - 1 and act >= k)):
                    d.rounded_rectangle([x - 12, y - 4, x + bw + 12, y + size + 16], 14, fill=OR)
                else:
                    put(fr, txt(w, ("PO", "900", size), (0, 0, 0)), x - 1, y + 1 + (1 - eo(p)) * 30, eo(p) * 0.65)
                put(fr, txt(w, ("PO", "900", size), WH), x - 4, y - 4 + (1 - eo(p)) * 30, eo(p))
                x += bw + f.getlength(" ")
            k += 1
        y += size + 30



def wrap(s, f, mx):
    L = [[]]
    for w in s.split():
        if f.getlength(" ".join(L[-1] + [w])) > mx and L[-1]: L.append([w])
        else: L[-1].append(w)
    return [" ".join(l) for l in L]


def pill(fr, text, x, y, size, p, fg=WH, bg=OR, font="AN"):
    """Soldan açılan turuncu kutu içinde yazı (p: 0–1)."""
    if p <= 0: return
    im = txt(text, (font, size) if font == "AN" else ("PO", "800", size), fg)
    w, h = im.width + 52, im.height + 26; ww = max(30, int(w * eo(p)))
    d = ImageDraw.Draw(fr); d.rounded_rectangle([x, y, x + ww, y + h], 18, fill=bg)
    c = im.crop((0, 0, max(0, min(im.width, ww - 26)), im.height)); fr.paste(c, (x + 26, y + 13), c)


def s_hook(t):
    fr = foot("hook", t); band(fr, 600, 1320, 170)
    caption(fr, "Kendi kozmetik markanızı kurmak mı istiyorsunuz?".split(), t, 0.1, 0.33, 820, 80)   # k4_01 (1,10x) ile senkron
    return fr


def s_title(t):
    lt = t - HOOK_END; fr = foot("title", lt); band(fr, 700, 1400, 170)
    q = eo(prog(lt, 0.1, 0.45)); put(fr, txt("MİE PHARMA", ("AN", 150), WH), 80 - (1 - q) * 120, 820, q)
    for i, ln in enumerate(["FASON KOZMETİK", "ÜRETİM SÜREÇLERİ"]):
        pill(fr, ln, 80, 1020 + i * 120, 76, prog(lt, 0.5 + i * 0.25, 0.4))
    s = prog(lt, 0, 0.3)   # hook'tan geçiş: alttan yukarı kayar
    if s < 1:
        prev = s_hook(HOOK_END - 0.01); y0 = int(H * (1 - eo(s))); prev.paste(fr.crop((0, y0, W, H)), (0, y0)); fr = prev
    return fr


def top_bar(fr, k, lt):
    lab = txt("FASON KOZMETİK ÜRETİM SÜREÇLERİ", ("PO", "800", 28), WH)
    pw = lab.width + 52; pl = Image.new("RGBA", (pw, 60), OR + (255,)); pl.paste(lab, (26, 13), lab)
    pl.putalpha(rmask(pw, 60, 30)); put(fr, pl, 80, 240)
    d = ImageDraw.Draw(fr); sw = (770 - 9 * 8) / 10
    for i in range(10):
        x0 = 80 + i * (sw + 8)
        d.rounded_rectangle([x0, 318, x0 + sw, 328], 5, fill=WH)
        f = 1 if i < k else (clamp(lt / STEP_D) if i == k else 0)
        if f > 0: d.rounded_rectangle([x0, 318, x0 + max(10, sw * f), 328], 5, fill=OR)


def step_card(fr, k, lt):
    q = eo(prog(lt, 0.05, 0.35)); w, h = 770, 250
    card = Image.new("RGBA", (w, h), WH + (255,)); d = ImageDraw.Draw(card)
    num = txt(f"{k + 1:02d}", ("AN", 150), OR); card.paste(num, (30, 34), num)
    f = PO("800", 44); lines = wrap(STEPS[k], f, 500)
    y0 = h // 2 - len(lines) * 30
    for i, ln in enumerate(lines):
        qi = eo(prog(lt, 0.15 + i * 0.08, 0.35)); im = txt(ln, ("PO", "800", 44), INK)
        im2 = im.copy(); im2.putalpha(im.getchannel("A").point(lambda v: int(v * qi)))
        card.paste(im2, (225, y0 + i * 60 + int((1 - qi) * 24)), im2)
    card.putalpha(rmask(w, h, 32))
    put(fr, shadow(w, h, 32, 60, 24), 80 - 80, 1150 - 80 + (1 - q) * 80, q)
    put(fr, card, 80, 1150 + (1 - q) * 80, q)


def step_frame(k, lt):
    z = 1 + 0.05 * clamp(lt / STEP_D)   # yavaş itme
    im = foot(f"k{k + 1:02d}", lt)
    if z > 1.001:
        cw, ch = int(W / z), int(H / z); im = im.resize((W, H), Image.BICUBIC, box=((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2))
    return im


def s_steps(t):
    a = t - STEP0; k = min(9, int(a / STEP_D)); lt = a - k * STEP_D
    fr = step_frame(k, lt)
    s = eo(prog(lt, 0, 0.3))   # yeni adım sağdan kayarak gelir
    if s < 1:
        prev = step_frame(k - 1, STEP_D + lt) if k > 0 else s_title(STEP0 - 0.01)
        x = int(W * (1 - s)); prev.paste(fr.crop((0, 0, W - x, H)), (x, 0)); fr = prev
    top_bar(fr, k, lt); step_card(fr, k, lt)
    return fr


def s_outro(t):
    lt = t - OUTRO; fr = Image.new("RGB", (W, H), WH)
    lg = LOGO.copy(); lg.thumbnail((440, 440)); p = eo(prog(lt, 0.05, 0.45)); put(fr, lg, 80, 270 + (1 - p) * 40, p)
    for i, (w, c, sz) in enumerate([("MİE PHARMA", INK, 110), ("KALİTELİ ÜRETİM,", INK, 96), ("GÜÇLÜ MARKALAR.", OR, 96)]):
        q = prog(lt, 0.3 + i * 0.3, 0.3); put(fr, txt(w, ("AN", sz), c), 80, [520, 660, 776][i] + (1 - eo(q)) * 40, eo(q))
    q = eback(prog(lt, 1.6, 0.35))
    if q > 0:
        pulse = 1 + 0.03 * math.sin(max(0, lt - 2.0) * 7) * (lt > 2.0)
        bw, bh = int(770 * q * pulse), int(104 * q * pulse)
        if bw > 10:
            b = Image.new("RGBA", (bw, bh), OR + (255,)); b.putalpha(rmask(bw, bh, bh // 2)); put(fr, b, 465, 960, anchor="c")
            put(fr, txt("Teklif ve Katalog İçin İletişime Geçin", ("PO", "800", 32), WH), 465, 960, clamp(q), q * pulse, "c")
    contact_card(fr, lt - 1.9)
    s = prog(lt, 0, 0.35)
    if s < 1:
        prev = s_steps(OUTRO - 0.01); y0 = int(H * (1 - eo(s))); prev.paste(fr.crop((0, y0, W, H)), (0, y0)); fr = prev
    return fr


def contact_card(fr, lt):
    """İletişim kartı: kart alttan kayar, ikonlar zıplayarak gelir, yazılar daktilo gibi yazılır, kartın üstünden ışık geçer."""
    if lt <= 0: return
    x, y, w, h = 80, 1060, 770, 300
    p = eo(prog(lt, 0, 0.4))
    card = Image.new("RGBA", (w, h), LG + (255,)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 36, outline=OR, width=4)
    d.text((40, 52), "İLETİŞİM", font=PO("800", 26), fill=GR, anchor="lm")
    rows = [(ICON_IG, HANDLE, 0.35), (ICON_WEB, "miepharma.com", 0.6)]
    for i, (ico, label, t0) in enumerate(rows):
        ry = 120 + i * 100
        q = eback(prog(lt, t0, 0.35), 2.4)
        if q > 0:
            big = ico.resize((72, 72), Image.LANCZOS)
            put(card, big, 40 + 36 * (1 - q), ry - 36 + 36 * (1 - q), clamp(q), max(0.01, q))
        n = int(len(label) * clamp((lt - t0 - 0.15) / 0.45))   # daktilo
        if n > 0:
            put(card, txt(label[:n], ("PO", "800", 46), INK), 136, ry - 32)
            if n < len(label) and int(lt * 8) % 2 == 0:
                d.rectangle([136 + PO("800", 46).getlength(label[:n]) + 10, ry - 26, 142 + PO("800", 46).getlength(label[:n]) + 10, ry + 26], fill=OR)
    sh = prog(lt, 1.25, 0.6)   # ışık süpürmesi
    if 0 < sh < 1:
        g = Image.new("L", (w, h), 0); gd = ImageDraw.Draw(g); cx = int(-200 + (w + 400) * sh)
        gd.polygon([(cx, 0), (cx + 90, 0), (cx - 60, h), (cx - 150, h)], fill=110)
        card.paste(Image.new("RGBA", (w, h), (255, 255, 255, 255)), (0, 0), g.filter(ImageFilter.GaussianBlur(18)))
    card.putalpha(Image.composite(card.getchannel("A"), Image.new("L", (w, h), 0), rmask(w, h, 36)))
    put(fr, shadow(w, h, 36, 60, 26), x - 80, y - 80 + (1 - p) * 120, p)
    put(fr, card, x, y + (1 - p) * 120, p)




def frame_at(t):
    if t < HOOK_END: return s_hook(t)
    if t < TITLE_END: return s_title(t)
    if t < OUTRO: return s_steps(t)
    return s_outro(t)


if A.stills:
    for s in A.stills.split(","):
        frame_at(float(s)).save(f"{A.out}_{float(s):05.2f}.jpg", quality=90)
    raise SystemExit

n0, n1 = int(A.t0 * FPS), int(A.t1 * FPS)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                      "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", A.out],
                     stdin=subprocess.PIPE)
for i in range(n0, n1):
    p.stdin.write(frame_at(i / FPS).tobytes())
p.stdin.close(); p.wait(); print("ok", A.out)
