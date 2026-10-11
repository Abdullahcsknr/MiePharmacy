"""Mie kozmetik Reels — v2 render: seslendirmeye senkron (k01–k08).

Motor: fason reel_v6 ile aynı yardımcılar. Kullanım: python3 reel_k1.py SEG_DIR FASON_REPO_DIR OUT.mp4 [--stills t1,t2]
"""
import argparse, glob, math, os, random, subprocess, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 30.5   # k2: ürün 2 sahnesi +2,5 sn (k05 seslendirmesi 4,9 sn)
D2 = 2.5
TS = 1.0  # sahneler doğrudan gerçek saniyeyle yazıldı, hareket süreleri sakin tutuldu
OR = (255, 100, 24); WH = (255, 255, 255); GR = (85, 85, 85); LG = (244, 244, 244); INK = (20, 20, 20)

ap = argparse.ArgumentParser()
ap.add_argument("seg"); ap.add_argument("repo"); ap.add_argument("out")
ap.add_argument("--from", dest="t0", type=float, default=0); ap.add_argument("--to", dest="t1", type=float, default=DUR * TS)
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


def contact_card(fr, lt):
    """İletişim kartı: kart alttan kayar, ikonlar zıplayarak gelir, yazılar daktilo gibi yazılır, kartın üstünden ışık geçer."""
    if lt <= 0: return
    x, y, w, h = 80, 1110, 770, 300
    p = eo(prog(lt, 0, 0.4))
    card = Image.new("RGBA", (w, h), LG + (255,)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 36, outline=OR, width=4)
    d.text((40, 52), "İLETİŞİM", font=PO("800", 26), fill=GR, anchor="lm")
    rows = [(ICON_IG, "@mie_cosmeticss", 0.35), (ICON_WEB, "miepharma.com", 0.6)]
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



# ---------- sahneler (gerçek saniye) ----------
ANS = [("a02", 80, 300), ("a04", 342, 300), ("a05", 604, 300), ("a06", 80, 700), ("a08", 342, 700), ("a09", 604, 700)]
KEEP = 4   # "değildir"de kalan tek pencere


def s_hook(t):
    fr = foot("hook", t); fr = Image.blend(fr, Image.new("RGB", (W, H)), 0.3)
    caption(fr, "Hassas ciltlerde nasıl işlem yapılmalıdır?".split(), t, 0.1, 0.5, 800, 82)
    return fr


def s_answer(t):
    lt = t - 3.0; fr = Image.new("RGB", (W, H), OR)
    col = prog(lt, 3.15, 0.4)   # "değildir": pencereler kapanır
    for k, (seg, x, y) in enumerate(ANS):
        q = eback(prog(lt, 0.1 + k * 0.18, 0.45))
        if q <= 0: continue
        a, sc = clamp(q), lerp(0.7, 1, q)
        if k != KEEP: a *= 1 - eo(col); sc *= 1 - 0.3 * eo(col)
        if a > 0.01: window(fr, foot(seg, lt), "", x, y, 240, 370, a, sc, 20, 36, True)
    caption(fr, "Hassas ciltlerde çözüm daha fazla ürün kullanmak değildir.".split(), t, 3.3, 0.365, 1110, 62)
    # kalan pencere ekranı kaplar ve içgörü görüntüsüne dönüşür
    g = eo(prog(lt, 3.5, 0.5))
    if g > 0:
        x0, y0 = lerp(342, 0, g), lerp(700, 0, g); w, h = int(lerp(240, W, g)), int(lerp(370, H, g))
        im = foot("ins", 0).resize((W, H)).crop((int(x0), int(y0), int(x0) + w, int(y0) + h))
        fr.paste(im, (int(x0), int(y0)), rmask(w, h, int(lerp(20, 0, g))))
    return fr


def s_insight(t):
    lt = t - 7.0; fr = foot("ins", lt); fr = Image.blend(fr, Image.new("RGB", (W, H)), 0.3)
    caption(fr, "Doğru içeriklerle cildi sakinleştirmek ve bariyeri korumaktır.".split(), t, 7.15, 0.42, 900, 68)
    return fr


def product(fr, lt, seg, lab, line, first):
    q = eback(prog(lt, 0.0, 0.5)) if first else 1.0
    window(fr, foot(seg, lt), lab, 80, 300, 770, 820, clamp(q), lerp(0.85, 1, q))
    c = prog(lt, 0.45, 0.45)
    if c > 0:
        size = 36; f = PO("800", size)
        while f.getlength(line) + 56 > 770 and size > 24: size -= 1; f = PO("800", size)
        w, h = int(f.getlength(line) + 56), 82
        chip_ = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(chip_)
        d.rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=OR); d.text((28, h // 2), line, font=f, fill=WH, anchor="lm")
        put(fr, chip_, 80 - (1 - eo(c)) * 80, 1180, eo(c))


def s_prod1(t):
    lt = t - 10.5; fr = Image.new("RGB", (W, H), LG)
    product(fr, lt, "p1", "MİE YÜZ TEMİZLEME SÜTÜ", "Her cilt tipine uygundur.", True)
    p = prog(lt, 0, 0.35)   # içgörüden geçiş: soldan açık gri panel
    if p < 1:
        prev = s_insight(10.49); x = int(W * eo(p)); prev.paste(fr.crop((0, 0, x, H)), (0, 0)); fr = prev
    return fr


def s_prod2(t):
    lt = t - 13.5; fr = Image.new("RGB", (W, H), LG)
    product(fr, lt, "p2", "MİE C VİTAMİNLİ YÜZ TEMİZLEME JELİ", "tahriş etmeyen güçlü cilt temizliği", False)
    p = prog(lt, 0, 0.3)
    if p < 1: fr = Image.blend(s_prod1(13.49), fr, eo(p))
    return fr


def s_factory(t):
    lt = t - 16.5 - D2; fr = foot("fab", lt); fr = Image.blend(fr, Image.new("RGB", (W, H)), 0.12); shade(fr, 800, 1300, 200)
    for i, (w, c) in enumerate([("YERLİ ÜRETİM,", WH), ("ÖZEL FORMÜL", OR)]):
        q = eo(prog(lt, 0.35 + i * 0.35, 0.45)); put(fr, txt(w, ("AN", 128), c), 80 - (1 - q) * 120, 1040 + i * 140, q)
    q = eback(prog(lt, 0.9, 0.45))
    if q > 0: window(fr, foot("lab", lt), "FORMÜLASYON", 80, 330, 420, 330, clamp(q), lerp(0.8, 1, q), 22, 44)
    p = prog(lt, 0, 0.3)
    if p < 1: fr = Image.blend(s_prod2(16.49 + D2), fr, eo(p))
    return fr


def s_brand(t):
    lt = t - 20.0 - D2; fr = Image.new("RGB", (W, H), WH)
    lg = LOGO.copy(); lg.thumbnail((520, 520)); p = eo(prog(lt, 0.05, 0.5)); put(fr, lg, 80, 320 + (1 - p) * 40, p)
    put(fr, txt("DERMATOLOGICAL SKINCARE", ("PO", "800", 40), GR), 80, 600, eo(prog(lt, 0.35, 0.4)))
    for i, (w, c) in enumerate([("PROFESYONEL", INK), ("DERMOKOZMETİK", INK), ("ÇÖZÜMLER", OR)]):
        q = prog(lt, 0.7 + i * 0.3, 0.4); put(fr, txt(w, ("AN", 118), c), 80, 690 + i * 130 + (1 - eo(q)) * 40, eo(q))
    x, y = 80, 1150
    for i, tag in enumerate(["#Klinik", "#Güzellik merkezleri", "#Uzmanlar"]):
        f = PO("800", 30); w = int(f.getlength(tag) + 56)
        if x + w > 850: x, y = 80, y + 86
        q = eback(prog(lt, 1.8 + i * 0.2, 0.4), 2.2)
        if q > 0.01:
            c = Image.new("RGBA", (w, 70), (0, 0, 0, 0)); d = ImageDraw.Draw(c); d.rounded_rectangle([0, 0, w - 1, 69], 35, fill=LG)
            d.text((28, 35), tag, font=f, fill=INK, anchor="lm"); put(fr, c, x + w / 2, y + 35, clamp(q), q, "c")
        x += w + 14
    p = prog(lt, 0, 0.35)   # fabrikadan geçiş: aşağıdan beyaz panel
    if p < 1:
        prev = s_factory(19.99 + D2); y0 = int(H * (1 - eo(p))); prev.paste(fr.crop((0, y0, W, H)), (0, y0)); fr = prev
    return fr


def s_contact(t):
    lt = t - 24.0 - D2; fr = Image.new("RGB", (W, H), WH)
    lg = LOGO.copy(); lg.thumbnail((420, 420)); put(fr, lg, 80, 300, eo(prog(lt, 0.0, 0.4)))
    for i, (w, c) in enumerate([("BİZİMLE", INK), ("İLETİŞİME GEÇİN", OR)]):
        q = prog(lt, 0.2 + i * 0.3, 0.4); put(fr, txt(w, ("AN", 120), c), 80, 580 + i * 135 + (1 - eo(q)) * 40, eo(q))
    contact_card(fr, lt - 0.8)
    p = prog(lt, 0, 0.3)
    if p < 1: fr = Image.blend(s_brand(23.99 + D2), fr, eo(p))
    if t >= DUR - 1 / FPS: fr = Image.new("RGB", (W, H), OR)   # döngü
    return fr


SCENES = [(0, 3.0, s_hook), (3.0, 7.0, s_answer), (7.0, 10.5, s_insight), (10.5, 13.5, s_prod1), (13.5, 16.5 + D2, s_prod2),
          (16.5 + D2, 20.0 + D2, s_factory), (20.0 + D2, 24.0 + D2, s_brand), (24.0 + D2, DUR, s_contact)]


def frame_at(t):
    for a, b, f in SCENES:
        if a <= t < b or (f is s_contact and t >= a): return f(t)


if A.stills:
    for s in A.stills.split(","):
        frame_at(float(s)).save(f"{A.out}_{float(s):05.2f}.jpg", quality=90)
    raise SystemExit

n0, n1 = int(A.t0 * FPS), int(A.t1 * FPS)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                      "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", A.out],
                     stdin=subprocess.PIPE)
for i in range(n0, n1):
    p.stdin.write(frame_at(i / FPS).tobytes())
p.stdin.close(); p.wait(); print("ok", A.out)
