# Charter — Cozmo TR

## One-line description

Harici mikrofondan Türkçe komut alan ve yanıtını Cozmo hoparlöründen Türkçe
veren, telefonsuz çalışan güvenli bir müşteri demosu.

## Primary user

Tarık, çalışan sonucu görmek isteyen ve robotik yazılım ayrıntılarını bilmesi
gerekmeyen ilk demo kullanıcısıdır. Başlatma, bas-konuş ve durdurma akışı kısa;
hatalar Türkçe ve çözüme yönlendirici olmalıdır.

## Mission

Başarı, kullanıcının Cozmo'nun ağına bağlanıp tek komutla tanılama yapması,
konuşması ve robotun güvenli biçimde tepki verdiğini görmesidir. İnternet veya
telefon uygulaması bu temel akışın parçası değildir.

Deterministik komutlar ve doğrudan robot etkileri önce kanıtlanır. Doğal sohbet
ve daha ağır görüntü işleme ancak bu fiziksel döngü güvenilir olduğunda eklenir.

## Scope

### In scope

- Metin girdisiyle donanımsız dry-run
- Türkçe push-to-talk ve Vosk transkripsiyonu
- Hareket, konuşma, baş/kol, ışık, OLED yüz, kamera, pil/ses ve sonlu rutinler
- Kırmızı top için güven skorlu, kısa ve güvenlik kapılı hareket planı
- Üç ışıklı küp ve şarj platformu için sonlu keşif/LED kontrolü
- Mikrofondan bağımsız `execute` donanım smoke yolu
- Sınırlandırılmış `RobotAction` güvenlik kapısı
- macOS `say` ile 22.050 Hz, 16-bit, mono WAV
- PyCozmo ile telefonsuz bağlantı ve hoparlör oynatma
- `doctor` tanılama komutu ve Türkçe hatalar

### Sonraki doğrulamalar (ordered)

1. Robot, küp, platform ve top fiziksel smoke matrisi
2. 20 cümlelik Vosk kabul ölçümü; gerekirse faster-whisper karşılaştırması
3. Yerel sohbet ve yalnız tipli `RobotAction` araç çağrıları
4. Kanıtlanırsa daha doğal TTS ve kontrollü yüz/işaret algılama

### Non-goals

- Otonom gezinme veya denetimsiz hareket
- Doğrulanmamış yüz tanıma, kalıcı hafıza veya bulut zorunluluğu
- Mobil uygulama, çoklu robot ve üretim servisi
- Resmî mobil oyun/animasyon motoruyla birebir özellik eşitliği

## Success criteria

- 20 hedef Türkçe cümlenin en az 16'sı doğru aksiyona dönüşür.
- Güvenlik sınırı dışındaki her hareket reddedilir veya kırpılır.
- Türkçe WAV, Cozmo uyumlu biçimde üretilir.
- Donanım yokken tüm otomatik testler geçer.
- Donanım smoke belgesindeki her test ayrı sonuç ve durumla kaydedilir.

İlk haftada ölçülebilir sinyal: 20 cümlelik kabul setinde en az 16 doğru sonuç.

## First user

> Tarık, 2026-08-14 sonrası ilk uygun fiziksel Cozmo oturumunda `doctor`
> komutunu çalıştırır, beş komutu dener ve duyduğu Türkçe sesi değerlendirir.

## Most-fragile assumption

> Küçük Türkçe Vosk modeli, demo ortamındaki hedef komutların en az yüzde
> 80'ini güvenilir biçimde tanıyabilir.

## Timeline

- MVP target: 2026-08-15
- Post-MVP phasing: see `docs/ROADMAP.md`

## See also

- `.genesis/CONSTITUTION.md` — kuruluş ilkeleri
- `docs/ROADMAP.md` — teslim planı
- `.genesis/RISKS.md` — bilinen riskler
- `docs/DEFINITION_OF_DONE.md` — tamamlanma ölçütleri
