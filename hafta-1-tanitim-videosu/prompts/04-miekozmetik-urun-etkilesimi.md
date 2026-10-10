# Claude in Chrome Promptu — @miekozmetik Ürün Etkileşim Analizi

> Claude in Chrome'a olduğu gibi yapıştır, çıktıyı bana getir. Amaç: görsel üretimine hangi ürünle başlanacağını veriyle seçmek.

---

instagram.com/miekozmetik hesabını incele. Sadece oku; beğenme, takip etme, yorum yazma, mesaj gönderme yok. Yalnızca gözlemlediğini yaz, tahminleri "(tahmin)" diye işaretle.

**1. Profil:** kullanıcı adı, bio (birebir), takipçi / gönderi sayısı, son paylaşım tarihi, öne çıkan hikâyeler (adları).

**2. Son 40 gönderi — her biri tek satır:**
`tarih | format (Reels/Carousel/Tekil) | görünen ÜRÜN ADI (yoksa "ürün yok") | beğeni | yorum | izlenme (Reels) | görsel türü (ürün çekimi / lifestyle / motion / AI / stok / insan)`

**3. Ürün bazlı özet:** Yukarıdaki tablodan ürün başına: kaç gönderi, ortalama beğeni/yorum/izlenme. En çok etkileşim alan 5 ürünü sırala.

**4. En iyi 5 ve en kötü 5 gönderi:** konusu, formatı ve neden öyle olduğuna dair tek cümle (tahmin ise işaretle).

**5. Yorumlar:** ürünlerle ilgili tekrar eden sorular (fiyat, nereden alınır, kullanım, içerik vb.) ve ilgili ürün.

**6. Görsel dil:** ürün fotoğraflarının tarzı (arka plan, ışık, dekor), logo/renk tutarlılığı, AI ile üretilmiş görsel var mı (etiketli ya da belli olan).

**7. Paylaşım sıklığı:** son 3 ay, haftada kaç gönderi.

**Çıktı:** Markdown. Sonunda "Görsel üretimi için ilk 5 ürün" başlığı: her ürün için etkileşim verisine dayalı tek cümle gerekçe.
