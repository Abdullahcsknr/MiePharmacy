# Devam Notu (son durum)

## Biten
- Aşama 1–3: araştırma ve arşiv envanteri (`01-02-arastirma-ozeti.md`, `03-arsiv-envanteri.md`)
- Metin v4 (Ogilvy + kaynak kuralı): `05-metin.md`. Hook yazımı düzeltildi: "İSTİYOR MUSUN?"
- Logo HD: `kimlik/logo-mie-siyah-hd.png`, `kimlik/logo-mie-beyaz-hd.png` (280 px kaynaktan 2334 px, kenarlar yumuşatıldı)

## Storyboard: ONAYLANMADI → v5 hazırlanacak
Kullanıcı geri bildirimi:
1. Renkler **siteyle uyumlu** olmalı: siyah zemin YOK. Beyaz baskın, vurgu/zemin turuncu `#ff6418`, gri `#555555`; siyah yalnızca logo
2. Font **viral Reels fontu** olmalı (site fontu değil): başlık **Anton**, altyazı **Poppins Black/ExtraBold** (Hormozi/Submagic stili, aktif kelime turuncu kutu)
3. Hook, problem–çözüm, motion grafik şart; katalog gibi olmamalı

v5 planı: kavram (12 süreç yağması > ANAHTAR TESLİM > fabrikaya giriş > 6 adım > ölçek > kapanış) korunur; zeminler turuncu/beyaz, tipografi Anton + Poppins.
Script: `motion/storyboard/sb4.py` (v4) temel alınacak. Fontlar `motion/fonts/` içinde.

## Bekleyenler
- Kullanıcı 1080p kesitleri gönderecek (MIE_3, MIE_30, MIE_7, MIE_28, MIE_38, MIE_9)
- Dış ses: kadın/erkek, ElevenLabs web (Chrome)
- Müzik: kodla deneme, olmazsa lisanslı
- Kişi izinleri (müşteri)

## Cevaplananlar
- Görüntü kaynağı: müşterinin arşivi. Metinler: site + @mie.fabrika. "Paylaşılanlar dışında bir şey yok" denebilir
- Arşiv videoları yeniden indirme: Drive klasörü (küçültülmüş sürümler, 10.10.2026), `motion/storyboard/dec2.py` ile çözülür
