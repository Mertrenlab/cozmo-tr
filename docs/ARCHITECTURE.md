# Architecture — Cozmo TR

## Architectural style

Proje küçük bir hexagonal modüler monolittir. Saf domain kodu ses ve robot
donanımını portlar üzerinden görür; macOS, Vosk ve PyCozmo adaptörleri dış
kenardadır. Bu ayrım fiziksel robot olmadan güvenlik ve orkestrasyon testlerini
mümkün kılar (`ADR-002`).

## Module boundaries

| Module | Responsibility | Not responsible for |
|---|---|---|
| `actions` | Tipli eylemler ve güvenlik sınırları | Motor I/O, STT |
| `commands` | Türkçe metni deterministik eyleme çevirme | LLM, hareket yürütme |
| `orchestrator` | Bir kullanıcı turunu koordine etme | Donanım ayrıntıları |
| `tts` | Türkçe metni Cozmo WAV biçimine çevirme | Hoparlör aktarımı |
| `robot` | Robot portu ve PyCozmo adaptörü | Komut yorumlama |
| `stt` | Mikrofon sesini Türkçe metne çevirme | Eylem seçme |
| `cli` | Girdi doğrulama ve kullanıcı mesajları | Domain kararları |

## The narrow waist

`RobotAction(kind, value, text)` sistemin dar boğazıdır. Parser ve gelecekteki
LLM yalnızca bu tipi üretir; `SafetyPolicy` doğrulamadan robot portuna hiçbir
eylem geçmez. Değişiklikler ADR ve geriye uyumluluk testi gerektirir.

## Tech stack

| Layer | Choice | Rationale | ADR |
|---|---|---|---|
| Language | Python 3.11–3.12 | PyCozmo/Vosk uyumu ve hızlı prototip | ADR-003, ADR-010 |
| CLI | `argparse` | Yeni runtime bağımlılığı yok | ADR-003 |
| STT | Vosk Turkish | Küçük, çevrimdışı, komut odaklı | ADR-DEP-002 |
| TTS | macOS `say` + `afconvert` | Bu Mac'te hazır ve Türkçe Yelda sesi var | ADR-004 |
| Robot | PyCozmo | Telefonsuz doğrudan Wi-Fi ve WAV oynatma | ADR-DEP-001 |
| Persistence | None | MVP durum saklamaz | ADR-003 |

## Data model

- `ActionKind`: desteklenen hareket veya konuşma türü.
- `RobotAction`: tür, sayısal değer ve isteğe bağlı metin.
- `SafetyPolicy`: izin verilen mesafe, açı, hız ve metin uzunluğu.
- `TurnResult`: anlaşılma, uygulanan eylem ve kullanıcı mesajı.

## Logging strategy

Üretim yolları standart `logging` ile tek satırlı JSON üretir; ek bağımlılık
alınmaz. Zaman, seviye, logger, olay ve eylem türü kaydedilir. Ham mikrofon sesi
ve tam konuşma metni varsayılan olarak kaydedilmez.

- Format: structured JSON
- Levels: ERROR, WARN, INFO, DEBUG
- Required fields: `timestamp`, `level`, `logger`, `event`
- INFO: bağlantı ve güvenli eylem durumları
- ERROR: TTS, STT veya robot bağlantı başarısızlığı

## Secrets management

MVP sır kullanmaz. Gelecekteki API anahtarları yalnız ortam değişkenlerinden
alınır ve `.env` dışlanır (`ADR-005`).

## Deployment & rollback

Kaynak kod sanal ortamda editable kurulur; sürümler Git etiketiyle belirlenir
(`ADR-006`). Rollback, bilinen iyi etikete dönüp sanal ortamı yeniden kurmaktır.

## Observability

- Logs: stderr veya kullanıcı seçerse dosya
- Metrics: MVP'de yok; kabul testi sonucu rapordur
- Traces: not yet instrumented
- Alerting: not yet configured

## What this architecture deliberately does not support

- Çoklu robot, sunucu dağıtımı veya uzaktan kullanıcı
- LLM'nin doğrudan motor erişimi
- Sürekli mikrofon veya wake-word
- Kalıcı konuşma geçmişi
- Mobil Cozmo uygulaması üzerinden bağlantı

## See also

- `.genesis/DECISIONS.md` — karar kayıtları
- `docs/QUALITY_STANDARDS.md` — kod kuralları
- `.genesis/RISKS.md` — operasyonel riskler
- `.genesis/CONSTITUTION.md` — kuruluş ilkeleri
