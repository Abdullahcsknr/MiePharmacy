# Teknik tuzaklar ve çözümleri (Mie fason v1 → v15 sürecinden)

## Kaynak görüntü
- **Drive MCP indirme** pratikte ~5 MB'a kadar çalışır, 10 MB üstü kesin başarısız. Sonuç dosyaya JSON olarak kaydedilir (`content` alanı base64). Çözmek için: `python3 -c "import json,base64;d=json.load(open(F));open(OUT,'wb').write(base64.b64decode(d['content']))"`.
- Drive'daki dosyalar çoğu zaman **analiz için küçültülmüş** (270p–360p). Final için kullanıcıdan **orijinal/HD** iste, sohbete yükletebilirsin (yüklemelerin boyut sınırı Drive'dan geniş).
- Müşterinin tanıtım videolarında **alt yazı bantları** (lower third) ve **eski logo filigranı** (sağ üst) olur. Kırpma kutusunu bunları dışarıda bırakacak şekilde seç ve `segsheet` ile kontrol et.
- WhatsApp ile gelen tanıtım videolarındaki hat görüntüleri **stok** olabilir. Arşivde karşılığı yoksa kullanma ("gerçek görüntü" kuralı).

## Kesim ve zaman
- Temas tabakasından (`fps=1/2,tile`) saniye tahmini **kayar**. Kesim noktasını `tools.py times` ile tek tek kareler çekerek doğrula.
- `while read` döngüsünde ffmpeg'e **`-nostdin`** ver, yoksa stdin'i yer ve sonraki satırlar bozulur.
- `concat` filtresinde SAR uyuşmazlığı hatası: her dala `setsar=1` ekle.
- Ağır çekim: `setpts=PTS/0.6`. 0,5'in altına inme (takılma görünür).

## Netlik (kullanıcı "kalite düşük sahne olmasın" der)
- 9:16 tam ekran için 1080p kaynak 1,78 kat, 720p kaynak 2,67 kat büyür ve bulanıklaşır. **Önce ölç:** `tools.py sharp seg/*`.
- **Yatay bant + bulanık arka plan çözümü kullanıcıya garip geldi.** Açılış tam ekran olmalı.
- Çözüm: **Real-ESRGAN** (`scripts/esr.py`, model `realesr-general-x4v3`, ~4–9 sn/kare, CPU). Kaynak kırpmayı **doğal çözünürlükte** çıkar (ör. 607×1080 veya 405×720), 4 kat büyüt, sonra 1080×1920'ye lanczos ile indir.
  - Kurulum: `pip install torch` (PyPI. download.pytorch.org proxy'de engelli). Ağırlıklar GitHub releases:
    `https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth`
  - x4plus modeli 10 kat yavaş (~46 sn/kare), fark az. compact yeterli.
  - Uzun işi arka planda zincirle (`nohup bash chain.sh &`), bitişi `until grep -q BITTI log; do sleep 30; done` ile `run_in_background` olarak bekle.
- Küçük pencere/karolarda (≤ 300 px) düşük çözünürlük sorun değil.
- Kodlama: `-crf 14 -preset slow` (Instagram yeniden sıkıştırır, yüksek başla).

## Ses
- Ortamda ses dinlenemez (Whisper/HF engelli). VO yerleşimi süre + zaman damgası ile yapılır, kullanıcıya bunu söyle.
- Hızlandırma: `mix.py --tempo 1.25` (perde korunur) **ve** render'da `VO_SPEED` aynı değer. Kullanıcı 1,15'i yavaş buldu, 1,25 kabul edildi.
- Müzik ve efekt stem'lerinin uzunluğu birkaç örnek farklı olabilir. mix.py kırpar.
- Açılış "yalın" kalmasın: ilk karede vuruş + ritim hemen başlasın.

## Ortam
- `rm -rf $VAR/*` gibi silmeler güvenlik kontrolüne takılır. Yeni klasör adı kullan, silme.
- miepharma.com bu ortamdan erişilemez (DNS). Web ve IG araştırması **Claude in Chrome** promptuyla yapılır.
- Stop hook her turda commit + push ister. Büyük ara dosyalar scratchpad'de, scriptler ve finaller repoda.
- `**/cikti/ses/*.wav` gitignore'da. mp4'ler commit edilir.
