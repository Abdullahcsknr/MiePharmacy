#!/usr/bin/env python3
"""Outlier sıralaması: izlenme / hesabın medyanı. Kanca türünü anahtar kelimeyle tahmin eder.

Kullanım: python3 swipe.py kayit.tsv --out swipe.md
Sütunlar (başlık satırı zorunlu): platform hesap takipci medyan izlenme url tarih sure_sn kanca ekran_metni cta sayfa
Medyanı olmayan satır sıralamaya girmez, ayrıca listelenir.
"""
import argparse, csv, re, statistics
from collections import Counter

KANCA = [  # sıra önemli: ilk eşleşen kazanır
    ("B2B problem", r"kendi marka|fason|private label|girişimci|fabrikaya ihtiyac|marka kur"),
    ("Perde arkası", r"nasıl (üretil|dol|yapıl)|fabrika|üretim hattı|perde arkası|laboratuvar|how it'?s made|factory"),
    ("Mit çürütme", r"\bmit\b|yanlış bilinen|herkes .* sanıyor|aslında|doğru sanılan|myth"),
    ("Merak boşluğu", r"bilmiyordun|kimse söylemiyor|kimsenin söylemediği|sır\b|gizli|içinde ne var|en pahalı|nobody tells"),
    ("Doku/ASMR", r"asmr|doku\b|damla|texture|satisfying"),
    ("Ölçek", r"günde \d|\d+\s*(bin|milyon)\b|\d+\s*(k|m)\b"),
    ("Sayı/liste", r"^\s*\d+\s|\b\d+\s*(etken|adım|ipucu|hata|şey|yol|madde|dakika|saniye|sn|dk)\b"),
    ("Soru", r"\?\s*$|^(neden|nasıl|ne zaman|hangisi|hangi|kim|ne)\b"),
]

def num(x):
    x = (x or "").strip().replace(".", "").replace(",", "")
    return int(x) if x.isdigit() else None

def kanca_tur(metin):
    t = (metin or "").lower()
    for ad, rx in KANCA:
        if re.search(rx, t):
            return ad
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv"); ap.add_argument("--out", default="swipe.md")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.tsv, encoding="utf-8"), delimiter="\t"))
    ok, eksik = [], []
    for r in rows:
        v, m = num(r.get("izlenme")), num(r.get("medyan"))
        if not v or not m:
            eksik.append(r); continue
        r["_v"], r["_m"], r["_x"] = v, m, v / m
        r["_tur"] = kanca_tur((r.get("kanca") or "") + " " + (r.get("ekran_metni") or ""))
        ok.append(r)
    ok.sort(key=lambda r: -r["_x"])
    n, hesaplar = len(ok), len({r["hesap"] for r in ok})
    out = [f"# SWIPE · {n} video · {hesaplar} hesap · taban: hesabın kendi medyanı\n"]
    if n < 12:
        out.append(f"> ⚠️ Örneklem küçük ({n} video). Bulgular iddia değil, ipucudur.\n")
    out.append("## Outlier'lar (≥3x)\n\n| Çarpan | Tür | Hesap | İzlenme (medyan) | Kanca | URL |\n|---|---|---|---|---|---|")
    for r in ok:
        if r["_x"] >= 3:
            out.append(f"| {r['_x']:.1f}x | {r['_tur'] or '—'} | {r['hesap']} | {r['_v']:,} ({r['_m']:,}) | {r['kanca']} | {r['url']} |")
    if not any(r["_x"] >= 3 for r in ok):
        out.append("| — | — | — | — | Hiç video 3x'e ulaşmadı | — |")
    k = max(1, n // 3)
    ust, alt = ok[:k], ok[-k:]
    cu = Counter(r["_tur"] or "sınıflanamadı" for r in ust)
    ca = Counter(r["_tur"] or "sınıflanamadı" for r in alt)
    out.append(f"\n## Neyin payı yüksek (üst {len(ust)} / alt {len(alt)})\n\n| Tür | Üstte | Altta |\n|---|---|---|")
    for t in sorted(set(cu) | set(ca), key=lambda t: -cu[t]):
        out.append(f"| {t} | {cu[t]} | {ca[t]} |")
    ort = lambda g: statistics.mean(len((r.get('kanca') or '').split()) for r in g) if g else 0
    out.append(f"\nKanca uzunluğu (ort. kelime): üst {ort(ust):.0f} · alt {ort(alt):.0f}")
    sn = [r for r in ok if not r["_tur"]]
    out.append(f"\n## Sınıflandırılamayan kancalar ({len(sn)}) — elle oku\n")
    out += [f"- {r['_x']:.1f}x · {r['hesap']} · “{r['kanca']}” · {r['url']}" for r in sn] or ["- Yok"]
    if eksik:
        out.append(f"\n## Medyanı/izlenmesi olmayan, sıralanamayan ({len(eksik)})\n")
        out += [f"- {r['hesap']} · {r.get('url','')}" for r in eksik]
    out.append("\n> Kanca türü kaba anahtar kelime tahminidir. Yanlış sınıflananları düzelt. Regülasyon filtresini (SKILL.md bölüm 3) uygulamadan hiçbir fikir üretme.")
    open(a.out, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"{a.out}: {n} video, {sum(r['_x']>=3 for r in ok)} outlier, {len(eksik)} sıralanamadı")

if __name__ == "__main__":
    main()
