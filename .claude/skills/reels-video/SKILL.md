---
name: reels-video
description: Bir marka için müşterinin gerçek arşiv görüntülerinden, motion grafikli, seslendirmeli ve müzikli Instagram Reels videosu üretir (Mie fason v15 yöntemi). Araştırma (IG + web, Claude in Chrome), arşiv analizi, storyboard, Ogilvy metin, Python/Pillow motion render, kodla müzik, ElevenLabs seslendirme, yapay zekâ ile netleştirme ve geri bildirim döngüsünü kapsar. Kullanıcı "reels videosu yap", "tanıtım videosu", "fason/kozmetik videosu", "yeni video", "videoyu revize et", "sahneleri değiştir", "sesi hızlandır", "görüntü net değil" dediğinde ya da bu repoda bir video işine başladığında kullan.
---

# Reels Video Üretimi

Bu skill, Mie fason videosunun v1'den v15'e gelirken öğrenilen her şeyi içerir. Amaç, aynı hataları tekrarlamadan ilk turda v15 kalitesine ulaşmak.

**Başlamadan önce oku:**
- `references/dersler-mie.md`: kullanıcının kalıcı kuralları
- `references/teknik-tuzaklar.md`: yaşanan teknik sorunlar ve çözümleri

Referans çıktı ve birebir tarif: `references/v15-tarifi.md`.

## Çalışma tarzı (kullanıcı tercihleri, kesin)
- **Kısa yaz.** Türkçe, sade. Ne yaptın, ne gerekiyor, tek öneri.
- **Aşamaları sırayla takip et.** Atlama, birden fazla şeyi aynı anda değiştirme.
- **İstenmeyeni değiştirme.** Kullanıcı "sahneleri değiştir" dediyse metin, ses, yapı ve zamanlama aynen kalır. v7'de içerik baştan yazıldı, kullanıcı kızdı: "içeriğe laf etmedim neden değiştirdin". Geri bildirimi harfi harfine uygula, gerisine dokunma.
- **Prompt istenirse düz metin ver** (md tablo değil). Kod bloğu içinde kopyalanabilir olsun.
- Her teslimde: render → `SendUserFile` → commit + push (dal kuralına uy, PR açma).

## 10 aşama
| # | Aşama | Nasıl |
|---|---|---|
| 1 | Instagram analizi | `templates/chrome-01-instagram-analizi.md`'yi markaya uyarlayıp Claude in Chrome promptu olarak ver (sadece okuma; beğeni, takip, yorum, mesaj yok) |
| 2 | Web analizi | `templates/chrome-02-web-analizi.md` (aynı güvenlik kısıtları). Site bu ortamdan erişilemeyebilir |
| 3 | Arşiv analizi | `tools.py sheet` ile her videonun temas tabakası. Envanter tablosu: süreç adımı → klip (sn), insan/kapı var mı, çözünürlük |
| 4 | Storyboard | Hook → problem/vaat → kanıt → süreç → sayı → kapanış/çağrı. Kare kare stills ile göster, **onay al** |
| 5 | Metin | `ogilvy-copywriting` skill'i. **Her ifade site/IG'de birebir geçmeli ya da müşteriden gelmeli**; kaynak tablosu tut |
| 6 | Motion | `scripts/reel_template.py` (v15 motoru). Önce `--stills` ile önizle, sonra tam render |
| 7 | Müzik | `scripts/music_template.py`: kodla sentez, sahne kesmeleri vuruş ızgarasında, açılış yalın değil |
| 8 | Seslendirme | `templates/elevenlabs.txt`'yi metne uyarla, kullanıcı Chrome ile üretir, MP3'leri yükler. `scripts/mix.py` ile yerleştir |
| 9 | Teslim + geri bildirim | Geri bildirimi DERSLER'e satır olarak ekle |
| 10 | İkinci sayfa | Aynı akış, kendi IG/web analizi ile |

## Görüntü kuralları (v15'e kadar kullanıcının istedikleri)
1. **Gerçek görüntü.** Müşterinin arşivi. Stok yok, uydurma yok.
2. **Makine öncelikli; insan gösterme.** Dolum hattı, kazan, etiketli şişeler, kapak makinesi, panel. Kapı, koridor, ofis ve toplantı sahnesi kullanma. Seçtiğin her seg'i `tools.py segsheet` ile ilk, orta ve son karesinden kontrol et: insan, kapı, filigran ya da alt yazı bandı varsa değiştir.
3. **Drone varsa açılışta, tam ekran.** Boş arsa ya da şantiye görünen çekimi çıkar. Bina tabelasında başka marka adı varsa kullanıcıya söyle.
4. **Net görüntü.** Tam ekran sahneleri `tools.py sharp` ile ölç. 9:16'da 1,5 kattan fazla büyüyen her tam ekran sahneyi `scripts/esr.py` ile netleştir (bkz. teknik-tuzaklar). Bulanık klip kullanma; yatay bant + bulanık arka plan çözümü "garip" bulundu.
5. **Karartma yok.** Tam ekran blend/dim yapma. Yazı arkasına yalnız `band()` (yumuşak, yazı bandına sınırlı) ya da kart/pill koy.
6. **Hareket sakin** (TS = 1,3).

## Tasarım kuralları
- Renk: marka sitesinin paleti. Mie: turuncu `#ff6418`, beyaz, açık gri `#f4f4f4`, `#555`. Siyah zemin yok.
- Font: **Anton** (başlık) + **Poppins 800/900** (altyazı, aktif kelime turuncu kutuda). Dosyalar: `assets/fonts/` (Türkçe glifli).
- Logo: markanın **güncel orijinal** logosu (Mie: siyah serif, `kimlik/logo-mie-siyah-hd.png`). Eski logo grafikte kullanılmaz.
- Güvenli alan: y 230–1440, sağdaki 230 px boş.
- Açılış: **ilk kare gerçek görüntü + hook altyazısı.** Soyut animasyon ya da kutu yok.
- Kapanış: logo + slogan + turuncu CTA butonu + animasyonlu iletişim kartı (IG ve web ikonları, daktilo efekti, ışık süpürmesi).

## Metin kuralları
- Yazmadan önce sor: IG'de ya da sitede birebir var mı? Yasal açık var mı? Şirket onayı gerekir mi? Biri bile "evet" ise yazma.
- Sertifika, GMP, Helal, Sağlık Bakanlığı, sağlık iddiası ve fiyat: belge teyidi olmadan yazma.
- Ogilvy: kitleyi işaretle (hook soru), tek vaat, sıfat yerine bilgi, çağrı sesli de söylenir, müzik konuşmanın altında.
- Altyazı: kart başına ≤ 6 kelime. Yazım hatası yok (İSTİYOR MUSUN?).

## Ses kuralları
- Ses canlı ve enerjik olmalı. Hız sese göre: sakin ses (fason) **1,25x** kabul edildi; zaten heyecanlı ses (kozmetik k4) 1,25'te "çok hızlı" bulundu, **1,10x** istendi. Heyecanlı seste 1,10 ile başla. `mix.py --tempo` ve render'daki `VO_SPEED` aynı olmalı; hook altyazı kelime hızını VO süresine göre ayarla.
- Müzik konuşma altında -10 dB. Loudness -14 LUFS, TP -1,5.
- Ses dinlenemiyor: yerleşimi süre ve zaman damgasıyla yap, kullanıcıya bunu söyle.

## Hızlı akış (yeni video)
```
K=.claude/skills/reels-video/scripts
python3 $K/tools.py probe KAYNAK.mp4
python3 $K/tools.py sheet KAYNAK.mp4 sheet.jpg --every 2           # bak, aday aralıkları seç
python3 $K/tools.py times KAYNAK.mp4 t.jpg 34,35,36,37,38          # kesim noktasını doğrula
python3 $K/tools.py seg KAYNAK.mp4 seg/open --ss 0.2 --t 5.4 --fx 0.55   # 1080×1920 tam ekran
python3 $K/tools.py seg KAYNAK.mp4 seg/s1 --ss 21.3 --t 1.3 --w 770 --h 546
python3 $K/tools.py segsheet seg kontrol.jpg                      # insan/kapı/filigran kontrolü
python3 $K/tools.py sharp seg/*                                   # bulanık olanları ESRGAN'a gönder
python3 $K/esr.py realesr-general-x4v3.pth GIRIS_KARELERI CIKIS_KARELERI
python3 $K/reel_template.py seg PROJE out --stills 0.5,3,6,10,15,20,25
python3 $K/reel_template.py seg PROJE sessiz.mp4
python3 $K/music_template.py ses/m                                # zaman çizelgesini sahnelere göre düzenle
python3 $K/mix.py vo ses/m_muzik.wav ses/m_efekt.wav mix.wav --cues "01.mp3:0.05,02.mp3:2.55" --tempo 1.25
ffmpeg -i sessiz.mp4 -i mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k -ar 44100 -shortest final.mp4
```
Ara kareler ve ESRGAN çıktıları scratchpad'de kalır. Scriptler, dokümanlar ve final mp4 repoya girer.

## Geri bildirim geldiğinde
1. Tam olarak neyi istediğini ayır (sahne mi, metin mi, ses mi). Kapsam dışına çıkma.
2. Kullanıcı bir kaynak (drone vb.) önerdiyse, kalitesini ölçmeden "kullandım" deme. 360p ise HD'sini iste.
3. Değişikliği yap, `--stills` ile kontrol et, render et, gönder, `04-storyboard.md`'ye "vN: ne değişti" ekle, yeni kuralı DERSLER'e yaz.
