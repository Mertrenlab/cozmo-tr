# Risks — Cozmo TR

Yeni riskler bulundukça append edilir; ID'ler değişmez.

## Conceptual risks

### RISK-C1: Turkish recognition misses commands

- Source: Adversary, Phase 1
- Severity: high
- Description: Küçük Vosk modeli ortam gürültüsünde hedefi yanlış anlayabilir.
- Mitigation: Sabit 20 cümle seti, push-to-talk ve açık sözlük.
- Kill criterion: Vosk ve fallback adayının ikisi de 16/20 altındaysa dur.

### RISK-C2: Direct robot connection is unstable

- Source: Adversary, Phase 1
- Severity: high
- Description: Eski PyCozmo ve firmware kombinasyonu bağlantıyı bozabilir.
- Mitigation: Adaptör izolasyonu, `doctor`, sürüm kaydı ve smoke test.
- Kill criterion: Desteklenen Mac'te tekrar üretilebilir bağlantı kurulamıyorsa
  ulaşım katmanını yeniden seç.

### RISK-C3: Robot hears itself

- Source: Adversary, Phase 1
- Severity: medium
- Description: Sürekli mikrofon TTS'yi yeni komut sanabilir.
- Mitigation: MVP push-to-talk; gelecekte TTS sırasında STT kapalı.
- Kill criterion: Yok; continuous listen özelliği yayınlanmaz.

### RISK-C4: Unsafe movement causes a fall

- Source: Adversary, Phase 1
- Severity: critical
- Description: Yanlış veya sınırsız hareket masadan düşmeye yol açabilir.
- Mitigation: `SafetyPolicy`, cliff stop, kısa limitler, zemin smoke testi.
- Kill criterion: Güvenlik kapısı aşılabiliyorsa fiziksel demo yok.

### RISK-C5: Setup friction defeats the demo

- Source: Adversary, Phase 1
- Severity: medium
- Description: Model, mikrofon izni ve Wi-Fi adımları kullanıcıyı durdurabilir.
- Mitigation: `doctor`, tek quick-start ve Türkçe çözüm mesajları.
- Kill criterion: Temiz makinede yönergeyle kurulum tamamlanamıyorsa paketleme
  yeniden tasarlanır.

## Operational risks

### RISK-O1: Missing microphone permission

- Source: Operator, Phase 1
- Severity: high
- Description: macOS mikrofon akışını reddedebilir.
- Mitigation: `doctor` ve Sistem Ayarları yönlendirmesi.
- Detection: Cihaz listesi veya kayıt açma hatası.

### RISK-O2: Model unavailable on Cozmo Wi-Fi

- Source: Operator, Phase 1
- Severity: high
- Description: Cozmo AP internete çıkmaz; model sonradan indirilemez.
- Mitigation: Modeli Cozmo ağına geçmeden indir ve yerel yolu doğrula.
- Detection: Model dizini yok veya geçersiz.

### RISK-O3: TTS conversion failure

- Source: Operator, Phase 1
- Severity: medium
- Description: Sistem sesi veya `afconvert` yoksa WAV üretilemez.
- Mitigation: Araç ve WAV başlığı tanılaması; geçici dosyayı temizleme.
- Detection: Komut exit code'u veya format doğrulaması başarısız.

### RISK-O4: Robot disconnects mid-action

- Source: Operator, Phase 1
- Severity: critical
- Description: Bağlantı eylem sırasında kesilebilir.
- Mitigation: Sonlu süreli motor çağrıları, `STOP` önceliği ve kapanış denemesi.
- Detection: Adaptör hatası ve bağlantı durum olayı.

## User-experience risks

### RISK-U1: Listening state is unclear

- Source: User Advocate, Phase 1
- Severity: medium
- Description: Kullanıcı ne zaman konuşacağını bilemeyebilir.
- Mitigation: Push-to-talk öncesi ve sonrası açık Türkçe durum mesajı.

### RISK-U2: Rejection does not explain recovery

- Source: User Advocate, Phase 1
- Severity: medium
- Description: “Anlamadım” tek başına yardım etmez.
- Mitigation: Desteklenen örnek komutları ve yeniden deneme adımını göster.

### RISK-U3: Technical setup leaks into demo

- Source: User Advocate, Phase 1
- Severity: medium
- Description: Paket/model ayrıntıları ilk kullanıcıyı bunaltabilir.
- Mitigation: `doctor` sonucu tek eyleme dönük Türkçe öneriye çevirir.

## See also

- `.genesis/CONSTITUTION.md` — kill criteria
- `docs/ARCHITECTURE.md` — risklerin etkilediği bileşenler
- `docs/ROADMAP.md` — azaltım sırası
