# Claude in Chrome Promptu — Aşama 1: Fason Instagram Sayfası Analizi

> Bunu Claude in Chrome'a olduğu gibi yapıştır. `[HESAP]` yerine hesap adını yaz. Hesabı bilmiyorsan ilk adım onu bulur.
> Çıktıyı bana geri yapıştır.

---

Bir sosyal medya içerik analizi yapıyorsun. Yalnızca gözlemlediğini yaz, tahmin ettiğin her şeyi "(tahmin)" diye işaretle. Hiçbir şeyi paylaşma, beğenme, takip etme veya mesaj gönderme. Sadece oku.

**Adım 0:** instagram.com/[HESAP] adresini aç. Hesap adı yoksa miepharma.com sitesinin altındaki Instagram bağlantılarını ve "Mie Pharma fason" aramasını kullanarak Mie'nin fason/private label üretim hesabını bul. @miekozmetik ana marka hesabıdır. Ayrı bir fason hesabı yoksa bunu açıkça belirt ve @miekozmetik ile devam et.

**Adım 1: Profil**
- Kullanıcı adı, görünen ad, bio metni (birebir), bağlantı, kategori, takipçi / takip / gönderi sayısı
- Öne çıkan hikâyeler (highlights): adları ve kapak stilleri
- Profil fotoğrafı: hangi logo versiyonu, hangi renkler
- Sabitlenmiş gönderiler varsa: ne, ne zaman

**Adım 2: Son 30 gönderi.** Her biri için tek satır:
`tarih | format (Reels/Carousel/Tekil) | konu | ilk 1 sn'de ne görünüyor | ekrandaki ana metin | caption'ın ilk cümlesi | beğeni | yorum | (Reels ise) izlenme`

**Adım 3: Görsel kimlik**
- En sık kullanılan renkler (mümkünse HEX tahmini), fontlar (serif/sans, kalın/ince), logo kullanımı tutarlı mı?
- Fotoğraf türleri: gerçek fabrika/çalışan mı, stok fotoğraf mı, ürün çekimi mi? Örnek gönderi tarihleriyle.

**Adım 4: Performans**
- En çok etkileşim alan 5 gönderi (neden öne çıkmış olabilir?)
- En az etkileşim alan 5 gönderi
- Paylaşım sıklığı (son 3 ay, haftada kaç)

**Adım 5: Yorumlar ve DM sinyalleri**
- Yorumlarda tekrar eden sorular (fiyat, minimum adet, numune, süre vb.)

**Adım 6: Rakip kıyas (3 hesap)**
Instagram'da "fason kozmetik" ve "private label kozmetik Türkiye" araması yap, en aktif 3 fason üretici hesabını seç. Her biri için: takipçi, sabitlenmiş videosu var mı ve ne anlatıyor, en çok izlenen 2 Reels'in konusu ve ilk 3 saniyesi.

**Çıktı formatı:** Markdown, başlıklar yukarıdaki adımlar. Sonunda "Tanıtım videosu için çıkarımlar" başlığıyla 5 madde: kaçınılacaklar ve fırsatlar.
