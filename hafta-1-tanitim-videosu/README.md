# Hafta 1 — Sabitlenecek Kurumsal Tanıtım Videosu (Fason Sayfa)

**Hedef:** Instagram profiline sabitlenecek, markayı tanıtan, emeği ve kurumsal ölçeği gösteren, Instagram'a özel tanıtım videosu.
Ardından aynı yöntemle kozmetik (B2C) sayfası için ikinci video.

**Kurallar:** Kurumsal kimliğin dışına çıkma (orijinal logo, site renkleri) · yapay değil ama profesyonel.

> **KAYNAK KURALI:** Videoda, açıklamada ve ekranda yer alan **her ifade miepharma.com'da ya da @mie.fabrika'da birebir yazıyor olmalı.** Her cümlenin kaynağı `05-metin.md` tablosunda. Kaynağı olmayan ifade kullanılmaz. Kısaltma yalnızca cümleden kelimeleri sırası bozulmadan almakla yapılır.

## Teknik çerçeve (öneri)

| Alan | Karar |
|---|---|
| Format | 9:16, 1080×1920, 25 fps · grid kapağı için 4:5 güvenli alan |
| Süre | 30–40 sn (sabitlenmiş video izlenme sonuna kadar gitsin) |
| Dil | Türkçe dış ses + ekranda Türkçe altyazı (sessiz izleme için) |
| Yapı | Marka renkli motion grafik ekranlar + bizim çizdiğimiz maskeli alanlarda arşiv/fabrika görüntüleri |
| Üretim aracı | Kodla render (HTML/Canvas veya Remotion + ffmpeg). Her sahne parametrik, yani 2. video ve sonraki haftalar şablondan çıkar |

## Aşamalar ve durum

| # | Aşama | Kim yapar | Girdi | Çıktı | Durum |
|---|---|---|---|---|---|
| 1 | Fason Instagram sayfası analizi | **Claude in Chrome** (prompt: `prompts/01-instagram-analizi.md`) → Claude sentez | IG hesabı | `01-instagram-analizi.md` | 🟡 Prompt hazır |
| 2 | Web sitesi analizi | **Claude in Chrome** (prompt: `prompts/02-web-analizi.md`) → Claude sentez | miepharma.com | `02-web-analizi.md` | 🟡 Prompt hazır (site bu ortamdan erişilemiyor) |
| 3 | Fabrika / arşiv görüntü analizi | Claude | Küçültülmüş arşiv videoları | `03-arsiv-gorunt-envanteri.md` (sahne, zaman kodu, kullanılabilirlik) | 🔴 Videolar bekleniyor |
| 4 | Storyboard | Claude taslak → sen onay | 1–3 | `04-storyboard.md` + kare çizimleri | ⚪ |
| 5 | Metin (Ogilvy) | Claude (ogilvy-copywriting) → sen onay | 1–4 | `05-metin.md` | ⚪ |
| 6 | Motion video | Claude kodla üretir (`motion/reel_v1.py`) | Storyboard v5, 1080p klipler | `cikti/mie-fason-reel-v1-sessiz.mp4` | 🟡 v1 hazır, onay bekliyor |
| 7 | Müzik | Claude (kodla müzik) — yedek: lisanslı kütüphane | Ton/tempo kararı | `cikti/muzik.wav` | ⚪ |
| 8 | Seslendirme | ElevenLabs | 5'teki metin | `cikti/ses.mp3` | ⚪ Erişim yöntemi bekleniyor |
| 9 | Teslim + feedback | Claude gönderir, sen/müşteri yorumlar | v1 | feedback notları | ⚪ |
| 10 | Kozmetik sayfası versiyonu | Aynı akış | 9'daki dersler | 2. video | ⚪ |

## Senden gerekenler (kritik yol)

1. **Örnek görsel** (maskeli alan referansı): mesajda ek görünmüyor, tekrar gönder
2. **Fason Instagram hesabının adı**
3. **Arşiv videoları küçük boyutta** (Drive bağlantısı ~5 MB üstünü indiremiyor), aşağıdaki komutla
4. **Logo vektör dosyası** (SVG/AI/PDF), kurumsal font adı, renk kodları (varsa kurumsal kimlik kılavuzu)
5. **ElevenLabs erişimi:** API anahtarı mı, yoksa metni ben hazırlayıp senin web arayüzünden mi üretelim?

### Arşiv videolarını küçültme (kendi bilgisayarında)

ffmpeg ile (her video için 480p, sessiz, ~1–3 MB):
```
ffmpeg -i "GIRDI.mp4" -vf "scale=-2:480,fps=25" -c:v libx264 -crf 30 -preset slow -an "kucuk_GIRDI.mp4"
```
Uzun videolar için önce 60 sn'lik parçalara bölmek gerekirse: `-ss 0 -t 60` ekle.
HandBrake ile: Preset "Very Fast 480p30", Audio sekmesinden sesi kaldır.

**Öncelikli videolar:** TANITIM VİDEOSU · KAPANIŞ VİDEOSU · Kozmetik Fason Üretim (2 versiyon) · İSO BELGELER · turkce_dusuk_mb · MİE 1–52 içinden fabrika/üretim içerenler
(Final render için seçilen sahnelerin **orijinal kalitede** kısa kesitlerini ayrıca isteyeceğim.)
