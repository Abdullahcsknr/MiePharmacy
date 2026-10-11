# Mie · Brif videosu (animasyon + altyazı + kapanış taslağı)

Hyperframes ile hazırlanmış 9:16, 31 sn kompozisyon. Avatar klipleri (HeyGen) henüz yok, yer tutucu.
Render: `render/brif-taslak.mp4` (taslak kalite). Yeniden üretmek için: `npm run check` ve `npm run render`.

## Yer tutucular
- `av1` (0–3 sn), `av2` (7–12 sn), `av3` (22–27 sn): HeyGen avatar klipleri bu katmanların yerine `<video>` olarak konur.
- `mc` (12–17 sn): makro doku klibi (Mie arşivi) bu katmanın yerine konur.
- Logo: metin olarak yazılmış yer tutucu. Gerçek logo dosyası (SVG/PNG) `.logo` ve `.end .wm` yerine konur.
- Renkler (pembe vurgu, lacivert) ve yazı tipi (Inter) örnek videodan tahmin edildi, kurumsal kimlikle doğrulanmadı.
- Kapanış kartındaki telefon "+90 850 303 65 77 / +90 0552 668 42 55" örnek videodan aynen alındı, biçimi kontrol edilmeli.

## Standart öğeler (mie-avatar-serisi.md)
Alt şerit "MİE BİLGİ SERİSİ", sol altta "Yapay zekâ sunucu" yazısı (videonun tamamında), kinetik altyazı (kelime kelime, vurgulu kelime pembe), kapanış kartı ve "Adres" (Türkçe).
