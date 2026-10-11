# Aşama 4 — Storyboard v5

![storyboard v5](04-storyboard-v5.jpg)

Mavi taralı alanlar = Instagram arayüzünün kapattığı bölge (ig-reel kuralı: y<230, y>1440, sağ 230 px). Yazıların hepsi temiz alanda.

## v5'te değişenler
- **Renk:** site paleti. Zemin turuncu `#ff6418` / açık gri `#F4F4F4` / beyaz. Siyah yalnızca logoda ve 2 hook kelimesinde
- **Font:** Reels tipografisi. Başlık **Anton** (yoğun, dar, büyük), altyazı **Poppins Black** + aktif kelime turuncu kutu
- **Görüntü:** 6 klip 1080p (MIE_3, MIE_7, MIE_9, MIE_28, MIE_30, MIE_38). Tam ekran sahneler artık net
- **Logo:** HD siyah "Mie" (`kimlik/logo-mie-siyah-hd.png`)

## ig-reel yapısı (25 sn)
| Bölüm | Süre | Sahne |
|---|---|---|
| HOOK | 0–2 | 01 turuncu zemin, soru (kare 1'de hareket) |
| STAKE | 2–5,5 | 02 12 süreç kartı yağar |
| BODY | 5,5–22 | 03 ANAHTAR TESLİM · 04 vaat · 05 kapıdan giriş (MIE_3 tek plan) · 06 dev dolum hattı · 07 adımlar 01–04 · 08 adım 05 · 09 3-6 hafta |
| PAYOFF + ASK | 22–25 | 10 logo + kapanış cümlesi + tek çağrı |
| LOOP | son kare | Turuncuya kesme; tekrar oynatınca hook'a dikişsiz bağlanır |

Her sahne ≤ 3,5 sn (kare her vuruşta değişir). Ekran kartları ≤ 6 kelime (hook hariç: 5 kelime).

## Hook seçenekleri (ig-reel adım 1–2)
`hookscore.py` / `hooks.json` dosyaları gelmediği için puanlama elle yapıldı.
| # | Formül | Sözlü | Ekranda | Değerlendirme |
|---|---|---|---|---|
| 1 | Kitleyi işaretleyen soru | Kozmetik sektörüne girmek istiyor musun? | KOZMETİK SEKTÖRÜNE GİRMEK İSTİYOR MUSUN? | **Seçildi.** Hesapta aynı soru 100 B izlendi; izleyiciyi ilk kelimede seçiyor |
| 2 | Kolaylık vaadi | Kendi markanı oluşturmak artık çok daha kolay. | ARTIK ÇOK DAHA KOLAY | Güçlü vaat ama kime olduğu belli değil. Vaat olarak 04'te kullanıldı |
| 3 | Rakam | Ortalama proje süresi 3-6 hafta. | 3-6 HAFTA | Somut ama bağlamsız açılışta zayıf. Kanıt olarak 09'da kullanıldı |

## Kaynak tablosu (her ifade birebir)
| İfade | Kaynak |
|---|---|
| KOZMETİK SEKTÖRÜNE GİRMEK İSTİYOR MUSUN? | @mie.fabrika sabit Reels, 11.07.2025 ekran yazısı ("İSTİYOSUN ?"), yazımı düzeltildi |
| FORMÜLASYON, STABİLİTE, MİKROBİYOLOJİK, CHALLENGE TEST, MSDS, PIF, CPSR | @mie.fabrika 28.04.2026 "FASON KOZMETİK ÜRETİM SÜREÇLERİMİZ" + site "Formülasyon Geliştirme" |
| ÜTS BİLDİRİMİ | @mie.fabrika 24.04.2026 "ÜTS BİLDİRİMİ VE SAĞLIK BAKANLIĞI SÜREÇ YÖNETİMİ" |
| AMBALAJ, ETİKET, GRAFİK TASARIM | site /fason-uretimimiz/ "grafik tasarımından ambalaj ve etiket seçimlerinize kadar" |
| SERİ ÜRETİM | site adım 5 "Seri Üretim ve Kalite Kontrol" |
| ANAHTAR TESLİM | @mie.fabrika 05.12.2025 "ANAHTAR TESLİM FASON ÜRETİM HİZMETİ" |
| Kendi markanı oluşturmak artık çok daha kolay. | @mie.fabrika 4 gönderi (29.04, 27.04, 17.04, 09.04.2026) |
| Mie Kozmetik \| Fason Üretim Merkezi | @mie.fabrika bio |
| Onaylanan numune ile birebir aynı kalitede seri imalat | site adım 5 cümlesinden kesit |
| Ortalama proje süresi 3-6 hafta / *Proje bazlı yeni ürünler için ek süre gerekebilir. | site /fason-proje-hazirliklari/ |
| 6 adım adları | site /fason-kozmetik-uretimi/ |
| Markanı oluştur, üretimini bize bırak. | @mie.fabrika 09.04.2026 (hesabın en çok etkileşim alan görseli) |
| Teklif ve Katalog İçin İletişime Geçin | @mie.fabrika bio |
| miepharma.com | IG bio |

Sayaç "12": ekrandaki kart sayısı (iddia değil, ekranda sayılan kartlar).

Metin gerekçesi ve dış ses: `05-metin.md`

## Görüntü kaynağı (önemli)
Videodaki **görüntüler** site ya da Instagram'dan değil, **müşterinin arşivinden** (Drive › MiePharm: OneDrive_2, OneDrive_3, Downloads klasörleri) geliyor. Müşteriye cevap: "Sizin paylaştığınız tesis arşivinden." Metinler: site + @mie.fabrika.
Görüntüde yüzü görünen çalışanlar ve yöneticiler için müşteriden yazılı onay alınmalı.

## Logo
- Kullanılacak: `kimlik/logo-guncel-siyah.webp` (siyah serif "Mie": site, IG profil, kapanış videosu)
- Kullanılmayacak: `kimlik/logo-eski-yesil.webp` (eski logo; tesis tabelalarında ve formalarda görünmesi sorun değil)
- Eldeki siyah logo 280×280 px. Videoda ~600 px genişlikte kullanılacağı için **en az 1200 px PNG ya da SVG** gerekli

---

## v7 — Müşteri geri bildirimi (11.10.2026)

Geri bildirim: kapı girişleri az, makine, eleman ve seri üretim bandı çok; drone kullanılabilir; gerçek görüntü şart; ifadeler profesyonel; karartma filtresi çok koyu; ses daha canlı olmalı.

| Sn | Sahne | Görüntü (kaynak) | Metin |
|---|---|---|---|
| 0–4 | Hook | Drone: bina havadan (Drive "turkce_dusuk_mb_PART_000", 2–9 sn) | Kozmetik sektörüne girmek istiyor musunuz? |
| 4–7 | Marka | Drone devam | MİE PHARMA · Kaliteli Üretim, Güçlü Marka |
| 7–27 | 10 süreç adımı (2 sn/adım) | 01 MIE_43 toplantı · 02 MIE_6. lab · 03 YENI_21 numune dolum · 04 MIE_42 varil deposu · 05 MIE_8 üretim ekibi · 06 MIE_7 kazan · 07 MIE_5 kalite kontrol · 08 MIE_28 dolum hattı · 09 MIE_38 etiketli şişeler · 10 YENI_18 transpalet | Müşterinin "Fason Kozmetik Üretim Süreçleri" listesi birebir |
| 27–33 | Kapanış | Logo | MARKANIZI OLUŞTURUN, ÜRETİMİNİ BİZE BIRAKIN. · Teklif ve Katalog İçin İletişime Geçin · İletişim kartı |

Tasarım: görüntü karartılmıyor. Arka plan aynı görüntünün bulanık hali; okunabilirlik beyaz ve turuncu kartlarla. Üstte "FASON KOZMETİK ÜRETİM SÜREÇLERİ" bandı ve 10 parçalı ilerleme çubuğu.
WhatsApp tanıtım videosu (51 sn) kullanılmadı: drone yok, hat görüntülerinin çoğu arşivde yok (stok olabilir), "Sağlık Bakanlığı GMP" ifadesi onay gerektirir.

## v8 — v7 geri alındı; v6 içeriği aynen, yalnız sahneler değişti (11.10.2026)

Kullanıcı: "içeriğe laf etmedim, sadece sahneleri değiştirecektin; insan gösterme, makine kullan." v7 (yeni metin/yapı) iptal; reel_v7.py arşivde.
v6 metni, sesi, müziği, zamanlaması birebir korundu. Değişen görüntüler (hepsi insansız, HD makine):
- Açılış (kapı MIE_3 başı) → MIE_3 16–21 sn dolum makinesi salonu
- Marka açılışı (koridor) → MIE_38 etiketli Mie şişeleri hatta
- Adımlar: toplantı → dolum makinesi (MIE_3) · lab → kazan içi karıştırma (YENI_13) · ofis → kapak makinesi (MIE_29); raf (ürünler) aynen
- Seri üretim zemini (insanlı kazan) → insansız kazan (MIE_3 30 sn); küçük pencere "ÜRETİM" → kazan
- 3-6 hafta ızgarası: insanlı karolar → makine/kazan karoları
- Karartma: tam ekran karartma kaldırıldı; yalnız yazı bandında yumuşak gölge
Drone (Drive "turkce_dusuk_mb", 360p) denendi: bloklu ve eski logo filigranlı, kullanılmadı. Orijinal HD drone dosyası gelirse açılışa eklenir.

## v8: v6 içeriği aynen korundu, yalnızca sahneler değişti (11.10.2026)

v6 metni, sesi, müziği ve zamanlaması birebir korundu. İnsan ve kapı görüntüleri HD, insansız makine görüntüleriyle değiştirildi:
- Açılış: MIE_3 16–21 sn, dolum makinesi salonu.
- Marka açılışı: MIE_38, etiketli Mie şişeleri hatta.
- Adımlar:
  - Toplantı yerine dolum makinesi (MIE_3).
  - Laboratuvar yerine kazan içi karıştırma (YENI_13).
  - Ofis yerine kapak makinesi (MIE_29).
- Seri üretim zemini: insansız kazan (MIE_3 30 sn).
- Izgara karoları: makine görüntüleri.

Karartma: tam ekran karartma kaldırıldı; yalnızca yazı bandında yumuşak gölge var.

Drone (Drive "turkce_dusuk_mb", 360p) kalite yetersiz olduğu için kullanılmadı. HD orijinal bekleniyor.

## v9: v8 + drone açılışı (11.10.2026)

Açılış (ilk 5,2 sn): kullanıcının yüklediği "Mie_Cosmetics.mp4" (720p) videosunun 0,4–5,75 sn arası drone çekimi. 9:16 kırpma yapıldı; sağ üstteki eski logo filigranı kırpma dışında kaldı. 6. saniyeden sonra alt yazı bandı girdiği için o kısım kullanılmadı. Diğer her şey v8 ile aynı (v6 içeriği, sesi ve müziği).
Not: Mie_Cosmetics.mp4 160 sn, 720p; içinde makine sahnelerinin daha kaliteli halleri de var.

## v10: v9 + düşük çözünürlüklü pencereler 720p ile değişti

- Adım 02 penceresi (kazan içi karıştırma): YENI_13 (270p) yerine Mie_Cosmetics.mp4 35,6 sn (720p). Alt yazı bandı ve filigran kırpma dışında.
- Adım 04 penceresi (kapak makinesi): MIE_29 (480p) yerine Mie_Cosmetics.mp4 113,8 sn (720p).

## v11: v10 + seslendirme 1,15 kat hızlı

Seslendirme 1,15 kat hızlandırıldı (perde korunuyor, ffmpeg atempo). Cümlelerin başlangıç zamanları aynı. Altyazı kelime hızı da 1,15 kat artırıldı. Kullanılan araçlar: mix_v3b.py --tempo 1.15, reel_v8.py VO_SPEED.
