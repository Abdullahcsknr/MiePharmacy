# Claude in Chrome Promptu — Aşama 8: ElevenLabs Seslendirme

> Bunu Claude in Chrome'a yapıştır. ElevenLabs hesabında oturum açık olmalı.
> İndirilen 7 MP3'ü bana gönder; videoya sahne zamanlarına göre ben yerleştireceğim.

---

elevenlabs.io'da Türkçe bir Reels videosu için 7 kısa seslendirme üreteceksin. Hesapta oturum açık. Ücretli bir işlem (abonelik yükseltme, kredi satın alma) çıkarsa **durdur ve bana sor**. Hiçbir ayarı kalıcı olarak değiştirme, ses klonlama yapma.

**1. Ses seçimi**
- Text to Speech ekranını aç. Model: **Eleven Multilingual v2** (listede "Eleven v3" varsa onu da dene, Türkçe telaffuzu daha doğal olanı seç).
- Voice Library'de şunu ara: **Turkish male narrator** (ya da "Türkçe erkek, kurumsal, reklam").
- Kriterler: erkek, 30–45 yaş tınısı, sıcak ama otoriter, net diksiyon, aksansız Türkçe. Bağırmayan, abartısız reklam sesi.
- En uygun **3 aday sesi** önce şu cümleyle dene: "Kozmetik sektörüne girmek istiyor musun?" Adlarını ve neden seçtiğini bana yaz, en iyisiyle devam et.

**2. Ayarlar**
- Stability: 0.45 · Similarity: 0.80 · Style: 0.20 · Speaker boost: açık · Speed: 1.0 (2. ve 4. cümle sığmazsa 1.05)

**3. Cümleler: her biri AYRI üretilecek ve AYRI indirilecek**
Metni harfi harfine kullan, değiştirme.

| Dosya adı | Metin | Hedef süre |
|---|---|---|
| 01_hook.mp3 | Kozmetik sektörüne girmek istiyor musun? | ≤ 2,4 sn |
| 02_vaat.mp3 | Kendi markanı oluşturmak artık çok daha kolay. | ≤ 2,3 sn |
| 03_marka.mp3 | Mie Kozmetik, fason üretim merkezi. | ≤ 2,6 sn |
| 04_kanit.mp3 | Onaylanan numune ile birebir aynı kalitede seri imalat. | ≤ 3,0 sn |
| 05_sure.mp3 | Ortalama proje süresi üç ila altı hafta. | ≤ 2,8 sn |
| 06_kapanis.mp3 | Markanı oluştur, üretimini bize bırak. | ≤ 2,8 sn |
| 07_cagri.mp3 | Teklif ve katalog için iletişime geçin. | ≤ 2,4 sn |

**4. Telaffuz kontrolü**
- "Mie" kelimesi **"Mi-e"** diye okunmalı ("May" ya da "Mi" değil). Yanlış okursa metinde "Mi-e Kozmetik" yazarak tekrar üret ve hangisinin doğru çıktığını not et.
- "imalat", "numune", "fason" kelimelerinde vurgu doğal Türkçe olmalı.
- Bir cümle hedef süreyi aşarsa önce Speed 1.05 dene, yine aşarsa bana süreyi yaz.

**5. İndirme ve rapor**
Her cümleyi MP3 olarak, tablodaki adla indir. Sonunda bana şunları yaz:
- Seçilen sesin adı ve ID'si, kullanılan model
- Her dosyanın süresi
- Telaffuz sorunları (varsa)
