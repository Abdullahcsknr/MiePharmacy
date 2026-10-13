# Mie fason v15'i yeniden üretme tarifi (referans çıktı)

Final: `hafta-1-tanitim-videosu/cikti/mie-fason-reel-v15.mp4` (27,7 sn, 1080×1920, 30 fps)

## Sahne → kaynak (hepsi insansız makine ya da drone)
| Seg | Kaynak | Aralık | Kırpma/İşlem |
|---|---|---|---|
| open | Mie_Cosmetics.mp4 (720p, kullanıcı yükledi) | 0,2–2,2 (0,6x) + 4,95–5,95 (0,57x) | 405×720 @x=481 / x=542 → ESRGAN → 1080×1920 |
| walk (marka) | hd/MIE_38.mp4 | 6,0–9,5 | 607×1080 @x=656 → ESRGAN |
| line (kanıt) | hd/MIE_30.mp4 | 2,3–5,7 | 607×1080 @x=656 → ESRGAN → 1242×2208 |
| tank (seri üretim zemini) | hd/MIE_3.mp4 | 30,0–33,5 | 607×1080 @x=1024 → ESRGAN |
| s1 (adım 1 penceresi) | hd/MIE_3.mp4 | 21,3 | 770×546 |
| s2 (adım 2) | Mie_Cosmetics.mp4 | 35,6 | crop 705×500 @300,20 → 770×546 |
| s3 (adım 3) | MIE_45 raf (v6'dan) | | 770×546 |
| s4 (adım 4) | Mie_Cosmetics.mp4 | 113,8 | crop 960×680 @60,40 → 770×546 |
| w9/w28/w38 | MIE_3 27,3 / MIE_28 / MIE_38 | | 240×260 |
| g_* karolar | MIE_28/30/38/3, MIE_29, MIE_3 33 sn | | 270×270 |

## Komutlar
```
python3 reel_v8.py SEG13 .. sessiz.mp4                       # motion/reel_v8.py (= skill reel_template.py)
python3 mix_v3b.py ../cikti/ses/vo v4_muzik.wav v4_efekt.wav v13_mix.wav --tempo 1.25
ffmpeg -i sessiz.mp4 -i v13_mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k -ar 44100 -shortest v15.mp4
```
VO cue'ları (gerçek sn): 01_hook 0,05 · 02_vaat 2,55 · 03_marka 5,65 · 04_kanit 8,5 · 05_sure 19,1 · 06_kapanis 22,5 · 07_cagri 24,85

## Metin (v6'dan beri sabit, müşteri içeriğe itiraz etmedi)
Hook: "Kozmetik sektörüne girmek istiyor musun?" → "Kendi markanı oluşturmak artık çok daha kolay."
MİE KOZMETİK · FASON ÜRETİM MERKEZİ → "Onaylanan numune ile birebir aynı kalitede seri imalat."
Adımlar: STRATEJİK PLANLAMA · FORMÜLASYON GELİŞTİRME · TASARIM VE AMBALAJ SEÇİMİ · YASAL KAYITLAR
05 SERİ ÜRETİM VE KALİTE KONTROL → ORTALAMA PROJE SÜRESİ 3-6 HAFTA* (*Proje bazlı yeni ürünler için ek süre gerekebilir.)
MARKANI OLUŞTUR, ÜRETİMİNİ BİZE BIRAK. · Teklif ve Katalog İçin İletişime Geçin · İLETİŞİM: @mie.fabrika · miepharma.com
