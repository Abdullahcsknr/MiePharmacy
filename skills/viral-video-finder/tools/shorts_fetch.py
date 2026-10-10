#!/usr/bin/env python3
"""YouTube Shorts izlenmelerini çeker (herkese açık, giriş gerekmez) ve swipe.tsv satırı üretir.

Kullanım (kendi bilgisayarında; pip install yt-dlp):
  python3 shorts_fetch.py @gumuskozmetik @baskahesap --n 12 --out kayit.tsv
(Windows'ta '>' yönlendirmesi yerine --out kullan: Türkçe karakterler UTF-8 yazılır.)
Küçük partilerle çalış (birkaç kanal), arka planda döngüye sokma.
Kanca sütunu video BAŞLIĞIDIR; söylenen ilk cümle için videoyu aç ya da otomatik altyazıya bak (ilk 3 sn).
"""
import argparse, json, statistics, subprocess, sys

COLS = "platform hesap takipci medyan izlenme url tarih sure_sn kanca ekran_metni cta sayfa".split()

def fetch(handle, n):
    url = f"https://www.youtube.com/{handle}/shorts"
    p = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "--playlist-end", str(n), "-J", url],
                       capture_output=True, text=True)
    if p.returncode:
        sys.stderr.write(f"{handle}: {p.stderr.strip()[:200]}\n"); return None
    return json.loads(p.stdout)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("handles", nargs="+"); ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.out:
        sys.stdout = open(a.out, "w", encoding="utf-8", newline="\n")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
    print("\t".join(COLS))
    for h in a.handles:
        d = fetch(h if h.startswith("@") else "@" + h, a.n)
        if not d: continue
        es = [e for e in d.get("entries", []) if e.get("view_count") is not None]
        if len(es) < 6:
            sys.stderr.write(f"{h}: yalnızca {len(es)} izlenme okundu, medyan güvenilmez, atlandı\n"); continue
        med = int(statistics.median(e["view_count"] for e in es))
        fol = d.get("channel_follower_count") or ""
        for e in es:
            print("\t".join(str(x) for x in ["youtube", h, fol, med, e["view_count"], e.get("url", ""), "",
                                              int(e.get("duration") or 0), (e.get("title") or "").replace("\t", " "), "", "", ""]))

if __name__ == "__main__":
    main()
