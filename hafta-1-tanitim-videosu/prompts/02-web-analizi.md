# Claude in Chrome Promptu — Aşama 2: Web Sitesi Analizi

> Bunu Claude in Chrome'a yapıştır, çıktıyı bana geri yapıştır.
> Not: miepharma.com bu çalışma ortamından erişilemiyor, bu yüzden Chrome üzerinden yapıyoruz.

---

miepharma.com sitesini incele. Sadece oku, hiçbir form doldurma. **Metinleri birebir alıntıla** (videoda yalnızca sitede yazan bilgileri kullanacağız, yeni iddia uydurmayacağız). Tahminlerini "(tahmin)" diye işaretle.

Ziyaret edilecek sayfalar (en azından): ana sayfa, /fason-uretimimiz/, /ne-uretiyoruz/, /fason-kozmetik-uretimi/, hakkımızda/kurumsal, sertifikalar/kalite, iletişim. Menüde başka kurumsal sayfa varsa onları da aç.

**1. Kurumsal bilgiler** (her biri için kaynak URL)
- Kuruluş yılı, tesis yeri ve büyüklüğü (m²), üretim kapasitesi, çalışan sayısı, ihracat yapılan ülkeler
- Sertifikalar (ISO 9001, ISO 22716, ISO 22000, GMP, Helal vb.): sitede belge görseli var mı?
- Laboratuvar/AR-GE ile ilgili tüm ifadeler
- Rakam içeren her ifade (ör. "X yıllık tecrübe", "Y ürün") birebir

**2. Fason / private label anlatımı**
- Süreç adımları (formül, test, ambalaj, tasarım, seri üretim…): sitedeki sırayla ve birebir
- Üretilen kategori listesi
- Minimum sipariş, süre, gizlilik gibi ticari ifadeler

**3. Dil ve ton**
- Sitedeki slogan(lar) ve başlıklar birebir
- Ton: resmi/samimi, "siz" mi "sen" mi, sık geçen kelimeler (ör. güven, kalite, yerli…)

**4. Kurumsal kimlik**
- Logonun sitedeki versiyonu ve renkleri (mümkünse sayfa kaynağından/CSS'ten HEX kodları)
- Kullanılan font adları (CSS'ten font-family)
- Sitedeki fotoğraflar: gerçek tesis mi, stok mu?
- Logo dosyasının URL'si (SVG/PNG): sadece URL'yi yaz

**5. Videoda kullanılabilecek "kanıtlar" listesi**
Sitede açıkça yazan, tanıtım videosunda güvenle söylenebilecek 8–10 ifadeyi kaynak URL'leriyle listele. Sitede olmayan hiçbir şeyi ekleme.
