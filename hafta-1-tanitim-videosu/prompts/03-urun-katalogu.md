# Claude in Chrome Promptu — Ürün Kataloğu Çıkarma (görsel üretimi için)

> Claude in Chrome'a olduğu gibi yapıştır. Çıktıyı bana (ya da GPT görsel ajanına) geri ver.

---

Mie Kozmetik ürün kataloğu çıkarıyorsun. Sadece oku; form doldurma, sepete ekleme, takip etme yok. Yalnızca gözlemlediğini yaz, tahminleri "(tahmin)" diye işaretle. Metinleri birebir alıntıla, okunamayanı uydurma ("okunamadı" yaz).

**Kaynaklar (sırayla):** miepharma.com ürün/kategori sayfaları → instagram.com/miekozmetik (profil + son 30 gönderi + highlights) → varsa resmi e-ticaret/eczane sayfaları.

**Her ürün için bir satır/kart:**
- Ürün adı (birebir) · kategori (cilt / saç / takviye / diğer) · hacim (ml/adet)
- Ambalaj tipi (şişe, damlalık, pompa, sprey, tüp, kutu) ve ana renkler (HEX tahmini)
- Etiket özelliği (holografik, metalik, mat, vb.)
- Etken maddeler (ambalaj/sayfada yazan, birebir)
- Sitedeki kısa açıklama (birebir) ve kaynak URL
- Ürün fotoğrafı URL'leri (ön, yan, kutu; sadece URL yaz)
- Kayıt türü: kozmetik mi, takviye edici gıda mı? (kaynakta yazıyorsa; yoksa "belirsiz")

**Önceliklendirme sinyalleri (varsa, rakamıyla):**
- Instagram'da ürün başına geçen gönderi sayısı, ortalama beğeni/yorum/izlenme
- Sitede "çok satan / yeni / öne çıkan" etiketi olan ürünler
- Yorumlarda ürün hakkında tekrar eden sorular

**Çıktı:** Markdown tablo (yukarıdaki sütunlarla), ardından:
1. "Görsel üretimi için önerilen ilk 5 ürün" — her biri için tek cümle gerekçe (sinyale dayalı)
2. "Eksik/belirsiz bilgiler" listesi
3. Aynı ürün için birden fazla ambalaj versiyonu görürsen ayrıca belirt
