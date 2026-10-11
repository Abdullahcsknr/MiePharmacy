"""Mie fason tanıtım Reels — v7 (müşteri geri bildirimi: drone açılış, 10 üretim süreci, karartma yok)

Yapı: drone + hook → MİE PHARMA / Kaliteli Üretim, Güçlü Marka → 10 süreç adımı (gerçek makine/ekip/bant)
→ kapanış (çağrı + iletişim kartı). Okunabilirlik görüntüyü karartarak değil, kartlarla sağlanır.

Kullanım: python3 reel_v7.py SEG_DIR REPO_DIR OUT.mp4 [--from S --to S] [--stills t1,t2,...]
SEG_DIR: seg7/<ad>/%04d.jpg (30 fps, kaynak çözünürlükte).
"""
import argparse, glob, math, os, subprocess, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 33.0
OR = (255, 100, 24); WH = (255, 255, 255); GR = (85, 85, 85); LG = (244, 244, 244); INK = (20, 20, 20)

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
    fs = frames(name); i = min(len(fs) - 1, max(0, int(lt * FPS)))
    return Image.open(fs[i]).convert("RGB")

def cover(src, w, h, fx=0.5, fy=0.5, zoom=1.0):
    """Kaynağı w×h alanını dolduracak şekilde kırp (fx, fy: odak noktası)."""
    s = max(w / src.width, h / src.height) * zoom; cw, ch = w / s, h / s
    x0 = clamp(fx * src.width - cw / 2, 0, src.width - cw); y0 = clamp(fy * src.height - ch / 2, 0, src.height - ch)
    return src.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def blur_bg(src, fx=0.5):
    """Arka plan: aynı görüntünün bulanık hali (karartma yok, hafif aydınlatma)."""
    small = cover(src, 108, 192, fx).filter(ImageFilter.GaussianBlur(6))
    return Image.blend(small.resize((W, H), Image.BICUBIC), Image.new("RGB", (W, H), WH), 0.12)

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

def window(fr, img, lab, x, y, w, h, alpha=1.0, scale=1.0, rad=28, bar=54):
    """Referans stil pencere kartı; img zaten (w, h-bar) boyutunda."""
    c = Image.new("RGBA", (w, h), WH + (255,)); c.paste(img, (0, bar))
    d = ImageDraw.Draw(c); r, gap, x0 = 7, 22, 24
    for j, col in enumerate([OR, (210, 210, 210), (210, 210, 210)]):
        d.ellipse([x0 + j * gap, bar // 2 - r, x0 + j * gap + 2 * r, bar // 2 + r], fill=col)
    lx = x0 + 2 * gap + 2 * r + 14; fs = 22
    while fs > 11 and PO("800", fs).getlength(lab) > w - lx - 12: fs -= 1
    d.text((lx, bar // 2), lab, font=PO("800", fs), fill=GR, anchor="lm")
    c.putalpha(rmask(w, h, rad))
    put(fr, shadow(w, h, rad), x - 80 + (w - w * scale) / 2, y - 80 + (h - h * scale) / 2, alpha, scale)
    put(fr, c, x + (w - w * scale) / 2, y + (h - h * scale) / 2, alpha, scale)

def shade(fr, y0, y1, a):
    """Yalnız yazının olduğu bantta yumuşak gölge (tam ekran karartma yok)."""
    g = Image.linear_gradient("L").resize((1, y1 - y0)).point(lambda v: int(v * a / 255))
    m = Image.new("L", (W, H), 0); m.paste(g.resize((W, y1 - y0)), (0, y0)); m.paste(a, (0, y1, W, H))
    fr.paste((0, 0, 0), (0, 0, W, H), m)

def caption(fr, words, t, start, per, y, size=70, mx=780):
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
    lines = [[]]
    for w in s.split():
        if f.getlength(" ".join(lines[-1] + [w])) > mx and lines[-1]: lines.append([w])
        else: lines[-1].append(w)
    return [" ".join(l) for l in lines]


# ---------- yerleşim ----------
WX, WY, WW, WH_ = 80, 330, 770, 820          # pencere (sağ 230 px güvenli alan boş)
CY = 1195                                     # pencerenin altındaki kart
HOOK_END, TITLE_END, STEP0, STEP_D = 4.0, 7.0, 7.0, 2.0
STEPS = [  # (kesit, müşterinin süreç listesinden birebir başlık, pencere etiketi, odak x)
    ("s01", "Müşteri Talebi ve Ürün Planlaması", "PLANLAMA", 0.45),
    ("s02", "AR-GE ve Formülasyon Geliştirme", "AR-GE", 0.42),
    ("s03", "Numune Hazırlama ve Onay Süreci", "NUMUNE", 0.45),
    ("s04", "Hammadde ve Ambalaj Tedariki", "HAMMADDE", 0.55),
    ("s05", "Üretim Planlaması ve Hazırlık", "ÜRETİM PLANLAMASI", 0.5),
    ("s06", "Kozmetik Ürün Üretimi", "ÜRETİM", 0.55),
    ("s07", "Kalite Kontrol ve Analiz Süreçleri", "KALİTE KONTROL", 0.5),
    ("s08", "Dolum, Etiketleme ve Paketleme", "DOLUM", 0.5),
    ("s09", "Nihai Ürün Kontrolü", "NİHAİ KONTROL", 0.45),
    ("s10", "Sevkiyat ve Teslimat", "SEVKİYAT", 0.5),
]


def win_img(seg, lt, fx, zoom_t):
    z = lerp(1.0, 1.08, clamp(zoom_t))   # yavaş itme (Ken Burns)
    return cover(foot(seg, lt), WW, WH_ - 54, fx, 0.5, z)


def drone_img(lt):
    # kaynak 640×360; sağ üstteki eski logo filigranı kırpma dışında kalır
    return cover(foot("drone", lt), WW, WH_ - 54, 0.47, 0.55, lerp(1.0, 1.06, lt / 7))


def s_hook(t):
    src = foot("drone", t); fr = blur_bg(src, 0.47)
    q = eo(prog(t, 0, 0.35)) if t > 0 else 0
    window(fr, drone_img(t), "MİE PHARMA", WX, WY, WW, WH_, 1.0, lerp(0.96, 1, q))
    shade(fr, 1120, 1560, 120)
    caption(fr, "Kozmetik sektörüne girmek istiyor musunuz?".split(), t, 0.05, 0.32, 1215, 76)
    return fr


def s_title(t):
    lt = t - HOOK_END; src = foot("drone", t); fr = blur_bg(src, 0.47)
    window(fr, drone_img(t), "MİE PHARMA", WX, WY, WW, WH_)
    p = eo(prog(lt, 0.0, 0.45)); bw = int(770 * p)
    if bw > 20:
        card = Image.new("RGBA", (770, 270), OR + (255,)); d = ImageDraw.Draw(card)
        card.paste(txt("MİE PHARMA", ("AN", 128), WH), (36, 22), txt("MİE PHARMA", ("AN", 128), WH))
        q = prog(lt, 0.45, 0.4)
        sub = txt("Kaliteli Üretim, Güçlü Marka", ("PO", "800", 44), WH)
        if q > 0:
            sub2 = sub.copy(); sub2.putalpha(sub.getchannel("A").point(lambda v: int(v * eo(q))))
            card.paste(sub2, (40, 190 + int((1 - eo(q)) * 20)), sub2)
        card = card.crop((0, 0, bw, 270)); card.putalpha(rmask(bw, 270, 30))
        put(fr, shadow(bw, 270, 30, 60, 24), WX - 80, CY - 80); put(fr, card, WX, CY)
    return fr


def step_card(fr, k, lt):
    """Kart: büyük numara + müşterinin süreç adı. Yeni adımda içerik aşağıdan kayar."""
    card = Image.new("RGBA", (770, 270), WH + (255,)); d = ImageDraw.Draw(card)
    q = eo(prog(lt, 0.0, 0.3)); dy = int((1 - q) * 40)
    num = txt(f"{k + 1:02d}", ("AN", 150), OR); n2 = num.copy(); n2.putalpha(num.getchannel("A").point(lambda v: int(v * q)))
    card.paste(n2, (34, 40 + dy), n2)
    f = PO("800", 46); lines = wrap(STEPS[k][1], f, 520)
    if len(lines) > 2: f = PO("800", 40); lines = wrap(STEPS[k][1], f, 520)
    y0 = 135 - len(lines) * 30
    for i, ln in enumerate(lines):
        qi = eo(prog(lt, 0.08 + i * 0.06, 0.3)); im = txt(ln, ("PO", "800", f.size), INK)
        im2 = im.copy(); im2.putalpha(im.getchannel("A").point(lambda v: int(v * qi)))
        card.paste(im2, (215, y0 + i * 62 + int((1 - qi) * 30)), im2)
    card.putalpha(rmask(770, 270, 30))
    put(fr, shadow(770, 270, 30, 60, 24), WX - 80, CY - 80); put(fr, card, WX, CY)


def top_bar(fr, k, lt):
    """Üst bant: süreç başlığı + 10 parçalı ilerleme çubuğu."""
    lab = txt("FASON KOZMETİK ÜRETİM SÜREÇLERİ", ("PO", "800", 30), WH)
    pw = lab.width + 56; pill = Image.new("RGBA", (pw, 64), OR + (255,)); pill.paste(lab, (28, 14), lab)
    pill.putalpha(rmask(pw, 64, 32)); put(fr, pill, WX, 222)
    d = ImageDraw.Draw(fr); sw = (770 - 9 * 8) / 10
    for i in range(10):
        x0 = WX + i * (sw + 8)
        d.rounded_rectangle([x0, 300, x0 + sw, 308], 4, fill=(255, 255, 255))
        if i < k: d.rounded_rectangle([x0, 300, x0 + sw, 308], 4, fill=OR)
        elif i == k:
            f = clamp(lt / STEP_D); d.rounded_rectangle([x0, 300, x0 + max(8, sw * f), 308], 4, fill=OR)


def s_steps(t):
    lt_all = t - STEP0; k = min(9, int(lt_all / STEP_D)); lt = lt_all - k * STEP_D
    seg, _, lab, fx = STEPS[k]
    fr = blur_bg(foot(seg, lt), fx)
    img = win_img(seg, lt, fx, lt / STEP_D)
    # yeni görüntü pencerede sağdan kayarak gelir
    s = eo(prog(lt, 0, 0.3))
    if k > 0 and s < 1:
        pseg, _, _, pfx = STEPS[k - 1]
        prev = win_img(pseg, STEP_D + lt, pfx, 1.0); x = int(WW * (1 - s))
        comp = prev.copy(); comp.paste(img.crop((0, 0, WW - x, img.height)), (x, 0)); img = comp
    elif k == 0 and s < 1:
        prev = drone_img(t); x = int(WW * (1 - s)); comp = prev.copy(); comp.paste(img.crop((0, 0, WW - x, img.height)), (x, 0)); img = comp
    window(fr, img, f"{k + 1:02d} · {lab}", WX, WY + 20, WW, WH_ - 20)
    top_bar(fr, k, lt)
    step_card(fr, k, lt)
    return fr


def s_outro(t):
    lt = t - 27.0; fr = Image.new("RGB", (W, H), WH)
    lg = LOGO.copy(); lg.thumbnail((440, 440))
    p = eo(prog(lt, 0.05, 0.45)); put(fr, lg, 80, 270 + (1 - p) * 40, p)
    for i, (w, c) in enumerate([("MARKANIZI OLUŞTURUN,", INK), ("ÜRETİMİNİ", INK), ("BİZE BIRAKIN.", OR)]):
        sz = 96
        while AN(sz).getlength(w) > 770: sz -= 2
        q = prog(lt, 0.3 + i * 0.3, 0.3); put(fr, txt(w, ("AN", sz), c), 80, 540 + i * 112 + (1 - eo(q)) * 40, eo(q))
    q = eback(prog(lt, 2.9, 0.35))
    if q > 0:
        pulse = 1 + 0.03 * math.sin(max(0, lt - 3.3) * 7) * (lt > 3.3)
        bw, bh = int(770 * q * pulse), int(104 * q * pulse)
        if bw > 10:
            b = Image.new("RGBA", (bw, bh), OR + (255,)); b.putalpha(rmask(bw, bh, bh // 2)); put(fr, b, 465, 960, anchor="c")
            put(fr, txt("Teklif ve Katalog İçin İletişime Geçin", ("PO", "800", 32), WH), 465, 960, clamp(q), q * pulse, "c")
    contact_card(fr, lt - 3.2)
    # adımlardan geçiş: beyaz panel aşağıdan yükselir
    s = prog(lt, 0, 0.35)
    if s < 1:
        prev = s_steps(26.99); y0 = int(H * (1 - eo(s))); prev.paste(fr.crop((0, y0, W, H)), (0, y0)); fr = prev
    return fr


def contact_card(fr, lt):
    """İletişim kartı: kart alttan kayar, ikonlar zıplar, yazılar daktilo gibi yazılır, ışık süpürmesi."""
    if lt <= 0: return
    x, y, w, h = 80, 1060, 770, 300
    p = eo(prog(lt, 0, 0.4))
    card = Image.new("RGBA", (w, h), LG + (255,)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 36, outline=OR, width=4)
    d.text((40, 52), "İLETİŞİM", font=PO("800", 26), fill=GR, anchor="lm")
    rows = [(ICON_IG, "@mie.fabrika", 0.35), (ICON_WEB, "miepharma.com", 0.6)]
    for i, (ico, label, t0) in enumerate(rows):
        ry = 120 + i * 100
        q = eback(prog(lt, t0, 0.35), 2.4)
        if q > 0:
            big = ico.resize((72, 72), Image.LANCZOS)
            put(card, big, 40 + 36 * (1 - q), ry - 36 + 36 * (1 - q), clamp(q), max(0.01, q))
        n = int(len(label) * clamp((lt - t0 - 0.15) / 0.45))
        if n > 0:
            put(card, txt(label[:n], ("PO", "800", 46), INK), 136, ry - 32)
            if n < len(label) and int(lt * 8) % 2 == 0:
                d.rectangle([136 + PO("800", 46).getlength(label[:n]) + 10, ry - 26, 142 + PO("800", 46).getlength(label[:n]) + 10, ry + 26], fill=OR)
    sh = prog(lt, 1.25, 0.6)
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
    if t < 27.0: return s_steps(t)
    return s_outro(t)


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
