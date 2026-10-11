"""Mie fason tanıtım Reels — v3 render (seslendirmeye senkron, sesli çağrı için uzatılmış outro).

Kullanım: python3 reel_v1.py SEG_DIR REPO_DIR OUT.mp4 [--from S --to S] [--stills t1,t2,...]
SEG_DIR: sahne başına çıkarılmış görüntü kareleri (seg/<ad>/%04d.jpg, 30 fps).
"""
import argparse, glob, math, os, random, subprocess, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 26.3   # outro +1,3 sn: sesli çağrı (07_cagri) için
TS = 1.3  # zaman ölçeği: tüm hareketler 1,3 kat yavaş (toplam 32,5 sn)
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
    for j, col in enumerate([OR, (210, 210, 210), (210, 210, 210)]):
        d.ellipse([24 + j * 22, bar // 2 - 7, 38 + j * 22, bar // 2 + 7], fill=col)
    d.text((104, bar // 2), lab, font=PO("800", 22 if bar > 45 else 18), fill=GR, anchor="lm")
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
                if k == act or (k == len(words) - 1 and act >= k):
                    d.rounded_rectangle([x - 12, y - 4, x + bw + 12, y + size + 16], 14, fill=OR)
                else:
                    put(fr, txt(w, ("PO", "900", size), (0, 0, 0)), x - 1, y + 1 + (1 - eo(p)) * 30, eo(p) * 0.65)
                put(fr, txt(w, ("PO", "900", size), WH), x - 4, y - 4 + (1 - eo(p)) * 30, eo(p))
                x += bw + f.getlength(" ")
            k += 1
        y += size + 30


# ---------- sahneler ----------
ITEMS = ["FORMÜLASYON", "STABİLİTE", "MİKROBİYOLOJİK", "CHALLENGE TEST", "MSDS", "PIF", "CPSR",
         "ÜTS BİLDİRİMİ", "AMBALAJ", "ETİKET", "GRAFİK TASARIM", "SERİ ÜRETİM"]
random.seed(7)
POS = [(70, 420), (420, 450), (120, 550), (460, 590), (60, 680), (400, 720), (150, 820), (470, 860),
       (80, 950), (380, 1000), (120, 1100), (430, 1140)]
ROT = [random.uniform(-14, 14) for _ in ITEMS]
JIT = [(random.randint(-30, 30), random.randint(-20, 20)) for _ in ITEMS]
DROP = [2.15 + 2.7 * (1 - (1 - i / 12) ** 1.7) for i in range(12)]   # giderek hızlanan yağış
HOOK = [("KOZMETİK", WH), ("SEKTÖRÜNE", WH), ("GİRMEK", WH), ("İSTİYOR", INK), ("MUSUN?", INK)]


def s_hook(t):
    fr = Image.new("RGB", (W, H), OR)
    sh = 0
    if 1.35 < t < 1.6: sh = int(10 * math.sin((t - 1.35) * 90) * (1.6 - t) / 0.25)
    for i, (w, c) in enumerate(HOOK):
        p = prog(t, -0.12 + i * 0.27, 0.3)
        put(fr, txt(w, ("AN", 158), c), 80 + sh, 330 + i * 178 + (1 - eo(p)) * 120, eo(p), lerp(1.25, 1, eback(p)))
    return fr


def chips_pile(fr, t, pull=0.0, center=(500, 900)):
    for i, it in enumerate(ITEMS):
        p = prog(t, DROP[i], 0.32)
        if p <= 0: continue
        x, y = POS[i][0] + JIT[i][0], POS[i][1] + JIT[i][1]
        y = lerp(-250, y, eback(p, 1.2))
        if pull > 0:
            q = eo(clamp(pull * 1.6 - i * 0.05))
            x, y = lerp(x, center[0] - 150, q), lerp(y, center[1] - 40, q)
            if q > 0.95: continue
            put(fr, chip_rot(it, round(ROT[i])), x, y, 1 - q * 0.6, 1 - q * 0.7)
        else:
            put(fr, chip_rot(it, round(ROT[i])), x, y)


def s_stake(t):
    fr = Image.new("RGB", (W, H), LG)
    chips_pile(fr, t)
    n = sum(1 for d in DROP if t > d + 0.15)
    if n: put(fr, txt(str(n), ("AN", 150), OR), 80, 250)
    # hook panelinin yukarı kayarak çıkışı
    p = prog(t, 2.0, 0.28)
    if p < 1:
        top = Image.new("RGB", (W, H), OR); fr.paste(top.crop((0, 0, W, int(H * (1 - eo(p))))), (0, 0))
    return fr


def s_turn(t):
    fr = Image.new("RGB", (W, H), LG)
    chips_pile(fr, t, pull=prog(t, 5.5, 0.6))
    b = eback(prog(t, 5.5, 0.32))
    if b > 0:
        bw, bh = int(780 * b), int(360 * b)
        if bw > 4 and bh > 4:
            box = Image.new("RGBA", (bw, bh), OR + (255,)); box.putalpha(rmask(bw, bh, 36))
            put(fr, box, 500, 900, anchor="c")
    s = prog(t, 5.85, 0.2)
    if s > 0:
        sh = int(8 * math.sin(t * 120) * (1 - prog(t, 6.05, 0.15)))
        lab = txt("ANAHTAR", ("AN", 150), WH); lab2 = txt("TESLİM", ("AN", 150), WH)
        sc = lerp(1.6, 1, eo(s))
        put(fr, lab, 500 + sh, 830, s, sc, "c"); put(fr, lab2, 500 + sh, 985, s, sc, "c")
    return fr


def s_promise(t):
    # turuncu kutu ekranı doldurur, içinde kapı görüntüsü (kutu = kapı)
    lt = t - 7.0; e = eo(prog(lt, 0, 0.4))
    fr = Image.new("RGB", (W, H), LG)
    bw, bh = int(lerp(780, W, e)), int(lerp(360, H, e))
    ft = foot("door", lt).resize((W, H))
    ft = Image.blend(ft, Image.new("RGB", (W, H)), 0.42)
    x0, y0 = int(lerp(110, 0, e)), int(lerp(720, 0, e))
    crop = ft.crop((x0, y0, x0 + bw, y0 + bh))
    if e < 1:
        tint = Image.new("RGB", crop.size, OR); crop = Image.blend(tint, crop, e)
    fr.paste(crop, (x0, y0), rmask(bw, bh, int(lerp(36, 0, e))))
    if lt > 0.35:
        caption(fr, "Kendi markanı oluşturmak artık çok daha kolay.".split(), t, 7.35, 0.241, 900, 76)   # 02_vaat.mp3 ile senkron
    return fr


def s_reveal(t):
    lt = t - 9.0
    fr = foot("walk", lt)
    fr = Image.blend(fr, Image.new("RGB", (W, H)), 0.12); shade(fr, 650, 1150, 190)
    p1 = eo(prog(lt, 0.25, 0.35)); p2 = prog(lt, 0.55, 0.35)
    put(fr, txt("MİE KOZMETİK", ("AN", 128), WH), 80 + (1 - p1) * -120, 1010, p1)
    if p2 > 0:
        w = int(700 * eo(p2)); d = ImageDraw.Draw(fr); d.rounded_rectangle([80, 1180, 80 + max(w, 40), 1290], 18, fill=OR)
        lab = txt("FASON ÜRETİM MERKEZİ", ("AN", 72), WH)
        fr.paste(lab.crop((0, 0, min(lab.width, max(0, w - 30)), lab.height)), (110, 1195), lab.crop((0, 0, min(lab.width, max(0, w - 30)), lab.height)))
    return fr


def s_scale(t):
    lt = t - 11.5; z = lerp(1.0, 1 / 1.15, eo(prog(lt, 0, 2.5)))
    src = foot("line", lt); cw, ch = int(W * 1.15 * z), int(H * 1.15 * z)
    x0, y0 = (src.width - cw) // 2, (src.height - ch) // 2
    fr = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    shade(fr, 850, 1350, 190)
    caption(fr, "Onaylanan numune ile birebir aynı kalitede seri imalat.".split(), t, 11.56, 0.316, 1040, 64)   # 04_kanit.mp3 ile senkron
    return fr


STEPS = [("s1", "01 · STRATEJİK PLANLAMA", "STRATEJİK PLANLAMA"), ("s2", "02 · FORMÜLASYON GELİŞTİRME", "FORMÜLASYON GELİŞTİRME"),
         ("s3", "03 · TASARIM VE AMBALAJ SEÇİMİ", "TASARIM VE AMBALAJ SEÇİMİ"), ("s4", "04 · YASAL KAYITLAR", "YASAL KAYITLAR")]


def s_steps(t):
    lt = t - 14.0; fr = Image.new("RGB", (W, H), LG); d = ImageDraw.Draw(fr)
    k = min(3, int(max(0, lt - 0.2) / 0.7))
    for i in range(6):
        fill = OR if (i < k + 1 and lt > 0.2) else (215, 215, 215)
        d.rounded_rectangle([80 + i * 125, 250, 190 + i * 125, 262], 6, fill=fill)
    pw = eback(prog(lt, 0.05, 0.35))
    seg, lab, _ = STEPS[k]
    window(fr, foot(seg, (lt - 0.2 - k * 0.7)), lab, 80, 310, 770, 600, alpha=clamp(pw), scale=lerp(0.85, 1, pw))
    for i, (_, _, name) in enumerate(STEPS):
        p = prog(lt, 0.35 + i * 0.7, 0.25)
        if p > 0: put(fr, chip_img(name, 1 if lt > 0.55 + i * 0.7 else 0), 80 + (1 - eo(p)) * -60, 960 + i * 112, eo(p))
    # giriş: soldan açık gri panel kayar
    p = prog(lt, 0, 0.25)
    if p < 1:
        prev = s_scale(13.99); x = int(W * eo(p))
        prev.paste(fr.crop((0, 0, x, H)), (0, 0)); fr = prev
    return fr


def s_series(t):
    lt = t - 17.0; fr = foot("tank", lt); shade(fr, 900, 1300, 170); d = ImageDraw.Draw(fr)
    p = eo(prog(lt, 0.1, 0.3))
    if p > 0:
        w = int(760 * p); d.rounded_rectangle([80, 250, 80 + max(40, w), 330], 40, fill=OR)
        lab = txt("05 · SERİ ÜRETİM VE KALİTE KONTROL", ("PO", "800", 30), WH)
        c = lab.crop((0, 0, min(lab.width, max(0, w - 40)), lab.height)); fr.paste(c, (110, 272), c)
    for k, (seg, lab) in enumerate([("w9", "ÜRETİM"), ("w28", "ÜRÜN DOLUMLARI"), ("w38", "KALİTE KONTROL")]):
        q = eback(prog(lt, 0.4 + k * 0.5, 0.3))
        if q > 0: window(fr, foot(seg, lt - 0.4 - k * 0.5), lab, 80 + k * 258, 1110, 240, 300, clamp(q), lerp(0.7, 1, q), 20, 40, False)
    return fr


def s_fact(t):
    lt = t - 19.5; fr = Image.new("RGB", (W, H), WH); d = ImageDraw.Draw(fr)
    for k, n in enumerate(["MIE_30", "MIE_28", "MIE_38", "MIE_9", "MIE_7", "MIE_3"]):
        q = eo(prog(lt, 0.1 + k * 0.08, 0.35))
        if q > 0:
            im = foot("g_" + n, lt); im = Image.blend(im, Image.new("RGB", im.size, WH), 0.3).convert("RGBA"); im.putalpha(rmask(270, 270, 22))
            put(fr, im, 80 + (k % 3) * 285, 880 + (k // 3) * 285 + (1 - q) * 60, q)
    put(fr, txt("ORTALAMA PROJE SÜRESİ", ("PO", "800", 40), GR), 80, 290, eo(prog(lt, 0, 0.3)))
    big = txt("3-6 HAFTA*", ("AN", 180), OR); w = int(big.width * eo(prog(lt, 0.25, 0.5)))
    if w > 0: c = big.crop((0, 0, w, big.height)); fr.paste(c, (70, 370), c)
    put(fr, txt("*Proje bazlı yeni ürünler için ek süre gerekebilir.", ("PO", "600", 26), GR), 80, 1395, eo(prog(lt, 0.7, 0.3)))
    return fr


def s_outro(t):
    lt = t - 22.0; fr = Image.new("RGB", (W, H), WH); d = ImageDraw.Draw(fr)
    lg = LOGO.copy(); lg.thumbnail((560, 560))
    p = eo(prog(lt, 0.05, 0.45)); put(fr, lg, 80, 330 + (1 - p) * 40, p)
    for i, (w, c) in enumerate([("MARKANI OLUŞTUR,", INK), ("ÜRETİMİNİ", INK), ("BİZE BIRAK.", OR)]):
        q = prog(lt, 0.4 + i * 0.3, 0.3); put(fr, txt(w, ("AN", 100), c), 80, 700 + i * 118 + (1 - eo(q)) * 40, eo(q))
    q = eback(prog(lt, 1.5, 0.35))
    if q > 0:
        pulse = 1 + 0.03 * math.sin(max(0, lt - 1.9) * 7) * (lt > 1.9)
        bw, bh = int(770 * q * pulse), int(110 * q * pulse)
        if bw > 10:
            b = Image.new("RGBA", (bw, bh), OR + (255,)); b.putalpha(rmask(bw, bh, bh // 2)); put(fr, b, 465, 1215, anchor="c")
            put(fr, txt("Teklif ve Katalog İçin İletişime Geçin", ("PO", "800", 32), WH), 465, 1215, clamp(q), q * pulse, "c")
    put(fr, txt("miepharma.com", ("PO", "600", 34), GR), 80, 1320, eo(prog(lt, 1.8, 0.3)))
    if t >= DUR - 1 / (FPS * TS): fr = Image.new("RGB", (W, H), OR)   # döngü: son kare hook zeminine
    return fr


SCENES = [(0, 2.0, s_hook), (2.0, 5.5, s_stake), (5.5, 7.0, s_turn), (7.0, 9.0, s_promise), (9.0, 11.5, s_reveal),
          (11.5, 14.0, s_scale), (14.0, 17.0, s_steps), (17.0, 19.5, s_series), (19.5, 22.0, s_fact), (22.0, DUR, s_outro)]


def frame_at(t):
    for a, b, f in SCENES:
        if a <= t < b or (f is s_outro and t >= a): return f(t)


if A.stills:
    for s in A.stills.split(","):
        frame_at(float(s) / TS).save(f"{A.out}_{float(s):05.2f}.jpg", quality=90)
    raise SystemExit

n0, n1 = int(A.t0 * FPS), int(A.t1 * FPS)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                      "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", A.out],
                     stdin=subprocess.PIPE)
for i in range(n0, n1):
    p.stdin.write(frame_at(i / FPS / TS).tobytes())
p.stdin.close(); p.wait(); print("ok", A.out)
