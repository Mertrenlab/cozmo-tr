# Roadmap — Cozmo TR

Teslimler yazılım kanıtı ile fiziksel kanıtı ayırır. Bir özellik fake-adapter ve
sentetik testleri geçebilir; ilgili donanımla smoke edilmeden `ready` olmaz.

## Phase 0 — Genesis (complete)

- Proje sözleşmesi, mimari, risk ve karar kayıtları
- TDD, boyut, tip ve coverage kapıları

## Phase 1 — Türkçe güvenli çekirdek (complete)

- Deterministik Türkçe parser ve `RobotAction` dar boğazı
- Tüm hareketlerde `SafetyPolicy`, cliff-stop ve güvenli shutdown
- macOS Türkçe WAV, Vosk push-to-talk ve doğrudan PyCozmo bağlantısı
- `doctor`, dry-run, yetenek kataloğu ve tek-komut `execute`

## Phase 2 — Doğrudan Cozmo yetenekleri (software complete)

- Paletler, baş, kaldırma kolu, sırt/kafa ışıkları ve hoparlör seviyesi
- Yerel OLED ifadeleri, pil yanıtı, tek kare kamera ve sonlu rutinler
- Sentetik testli kırmızı top algılama ve güvenli hareket planı
- Üç küp türü ile şarj platformu için sonlu keşif, BLE bağlantısı ve LED'ler
- Yazı, push-to-talk ve hazır kontroller içeren loopback-only dashboard
- Terminal göstermeyen çift tıklanabilir macOS uygulama paketi

## Phase 3 — Fiziksel doğrulama (current)

- `docs/HARDWARE_SMOKE_TEST.md` listesini boş zeminde yürüt
- Robot/küp/platform/top sonuçlarını ayrı ayrı kaydet
- Geçen yetenekleri `experimental` / `hardware_pending` durumundan `ready`ye al
- 20 hedef Türkçe cümlede en az 16 doğru eylemi doğrula

## Phase 4 — Doğal ve görsel etkileşim (gated)

- STT kabulü başarısızsa faster-whisper değerlendirmesi
- Yerel sohbet; yalnız tipli ve güvenlik kapılı araç çağrıları
- Konuşurken mikrofonu kapatma ve isteğe bağlı wake-word
- Yanlış pozitif testleri geçerse yüz/işaret algılama ve şarj yönlendirmesi

## Sürekli non-goals

- Denetimsiz otonom hareket veya masada hareket testi
- Telefon uygulamasına, internete ya da buluta çalışma zamanı bağımlılığı
- Kaynağı/lisansı doğrulanmamış animasyon arşivini otomatik indirme
- PyCozmo'nun uygulamadığı mobil oyun motoru özelliklerini hazır gösterme

## See also

- `docs/CHARTER.md` — ürün görevi
- `docs/HARDWARE_SMOKE_TEST.md` — fiziksel kabul sırası
- `.genesis/DECISIONS.md` — faz kararları
- `.genesis/PROGRESS.md` — gerçekleşen ilerleme
