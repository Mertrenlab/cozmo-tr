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

MVP önce deterministik komutları kanıtlar. Doğal sohbet, daha doğal ses ve
görsel arayüz ancak bu fiziksel döngü güvenilir olduğunda eklenir.

## Scope

### In scope (MVP)

- Metin girdisiyle donanımsız dry-run
- Türkçe push-to-talk ve Vosk transkripsiyonu
- `ileri`, `geri`, `sol`, `sağ`, `dur` ve basit konuşma komutları
- Sınırlandırılmış `RobotAction` güvenlik kapısı
- macOS `say` ile 22.050 Hz, 16-bit, mono WAV
- PyCozmo ile telefonsuz bağlantı ve hoparlör oynatma
- `doctor` tanılama komutu ve Türkçe hatalar

### Post-MVP (ordered)

1. Piper Türkçe ses ve Vosk/faster-whisper karşılaştırması
2. Yerel Ollama sohbeti ve yapılandırılmış araç çağrıları
3. Wake-word ve konuşma sırasında yankı engelleme
4. Web paneli, kamera ve kontrollü davranışlar

### Non-goals

- MVP'de doğal LLM sohbeti
- Otonom gezinme veya denetimsiz hareket
- Yüz tanıma, kalıcı hafıza veya bulut hesabı
- Mobil uygulama, çoklu robot ve üretim servisi

## Success criteria

- 20 hedef Türkçe cümlenin en az 16'sı doğru aksiyona dönüşür.
- Güvenlik sınırı dışındaki her hareket reddedilir veya kırpılır.
- Türkçe WAV, Cozmo uyumlu biçimde üretilir.
- Donanım yokken tüm otomatik testler geçer.
- İlk fiziksel oturumda beş temel komuttan en az dördü başarıyla çalışır.

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
