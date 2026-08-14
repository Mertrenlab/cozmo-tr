# Decision Log — Cozmo TR

Bu kayıt append-only'dir. Bir kararı değiştirmek, öncekini düzenlemek yerine
onu supersede eden yeni ADR yazmayı gerektirir.

## Index

| ID | Date | Title | Status |
|---|---|---|---|
| ADR-001 | 2026-08-14 | Adopt Genesis Protocol kit | accepted |
| ADR-002 | 2026-08-14 | Hexagonal safety boundary | accepted |
| ADR-003 | 2026-08-14 | Minimal Python CLI MVP | accepted |
| ADR-004 | 2026-08-14 | macOS system TTS first | accepted |
| ADR-005 | 2026-08-14 | No stored transcripts or secrets | accepted |
| ADR-006 | 2026-08-14 | Local package deployment and Git rollback | accepted |
| ADR-007 | 2026-08-14 | Fake CI and manual hardware smoke test | accepted |
| ADR-008 | 2026-08-14 | Clean-room MIT implementation | accepted |
| ADR-009 | 2026-08-14 | STT acceptance and fallback rule | accepted |
| ADR-DEP-001 | 2026-08-14 | Adopt PyCozmo | accepted |
| ADR-DEP-002 | 2026-08-14 | Adopt Vosk Turkish | accepted |
| ADR-DEP-003 | 2026-08-14 | Adopt sounddevice | accepted |
| ADR-DEP-004 | 2026-08-14 | Adopt Python quality toolchain | accepted |

---

## ADR-001: Adopt Genesis Protocol kit

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** Proje fiziksel hareket, eski donanım ve ses I/O içerdiği için ajan
devralmalarında güvenlik ve karar bilgisinin korunması gerekir.

**Decision.** Genesis kit yapısı, Iron Rules ve append-only durum kayıtları
projenin çalışma sözleşmesidir.

**Consequences.** TDD, kalite eşikleri, ADR ve ilerleme günlüğü zorunludur.

**Considered alternatives.** Yalnız README ile başlamak hızlı görünse de
güvenlik gerekçelerini ve devralma bağlamını kaybettireceği için reddedildi.

## ADR-002: Hexagonal safety boundary

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** STT ve gelecekteki LLM yanlış veya sınırsız değer üretebilir.

**Decision.** Tüm girdiler tipli `RobotAction` üretir ve robot portundan önce
`SafetyPolicy` tarafından doğrulanır.

**Consequences.** Domain donanımdan bağımsız test edilir; hiçbir adaptör
güvenlik kapısını atlayamaz.

**Considered alternatives.** Parserdan doğrudan motor çağrısı kısa ama fiziksel
riskli olduğundan reddedildi.

## ADR-003: Minimal Python CLI MVP

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** Kullanıcı hızlı prototip istedi; web, LLM ve kamera temel varsayımı
kanıtlamaz.

**Decision.** Python 3.11+, stdlib `argparse`, stateless CLI ve dört public CLI
komutuyla başlanır: `doctor`, `parse`, `say`, `run`.

**Consequences.** Veritabanı ve web framework yoktur; özellik yüzeyi küçüktür.

**Considered alternatives.** FastAPI tabanlı `cozmo-companion` fork'u lisans ve
yüzey alanı nedeniyle MVP için reddedildi.

## ADR-004: macOS system TTS first

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** Hedef Mac'te Türkçe Yelda sesi, `say` ve `afconvert` hazırdır;
eSpeak kurulu değildir.

**Decision.** İlk TTS adaptörü bu sistem araçlarıyla 22.050 Hz, 16-bit mono WAV
üretir. Linux eSpeak ve Piper post-MVP'dir.

**Consequences.** İlk ses ek indirme istemez; MVP TTS adaptörü macOS'a özeldir.

**Considered alternatives.** eSpeak daha taşınabilir, Piper daha doğal olsa da
ilk çalışan sesi geciktirdikleri için ertelendi.

## ADR-005: No stored transcripts or secrets

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** Mikrofon verisi kişiseldir; MVP bulut API'si kullanmaz.

**Decision.** Ham ses ve transcript kalıcılaştırılmaz. Gelecek sırlar yalnız
ortam değişkenleriyle alınır ve loglanmaz.

**Consequences.** Debug için açık kullanıcı tercihi gerekir; `.env` dışlanır.

**Considered alternatives.** Varsayılan transcript logu mahremiyet riski
yarattığı için reddedildi.

## ADR-006: Local package deployment and Git rollback

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** MVP tek bir demo bilgisayarında çalışır.

**Decision.** Sanal ortamda editable paket kurulur; bilinen iyi Git etiketi
rollback noktasıdır.

**Consequences.** Sunucu veya daemon yoktur; rollback ortamı yeniden kurar.

**Considered alternatives.** Docker mikrofon ve Wi-Fi erişimini zorlaştırdığı
için reddedildi.

## ADR-007: Fake CI and manual hardware smoke test

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** CI fiziksel Cozmo'ya erişemez.

**Decision.** Portlar fake adaptörlerle otomatik test edilir; gerçek robot testi
zeminde, ayrı smoke komutuyla ve kayıtlı sonuçla yapılır.

**Consequences.** Donanım davranışı otomatik test iddiasına girmez; domain yine
tam test edilir.

**Considered alternatives.** Robot gerektiren CI tekrar üretilemez olduğundan
reddedildi.

## ADR-008: Clean-room MIT implementation

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** En yakın örneklerin bazıları GPL veya lisanssızdır.

**Decision.** Kod sıfırdan MIT lisanslı yazılır; repolar yalnız davranış ve
mimari referanstır.

**Consequences.** Kaynak kod kopyalanmaz; bağımlılıkların kendi lisansları ayrıca
korunur.

**Considered alternatives.** GPL fork hızlı olsa da gelecekteki dağıtım
esnekliğini azalttığı için reddedildi.

## ADR-009: STT acceptance and fallback rule

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** Vosk Türkçe modelinin yayımlanmış hata oranı TBD'dir.

**Decision.** Sabit 20 cümlenin 16'sı doğru aksiyon üretmezse faster-whisper
değerlendirmesi tetiklenir.

**Consequences.** STT tercihi ölçüme bağlıdır; zevke göre değiştirilmez.

**Considered alternatives.** Doğrudan Whisper daha ağır kurulum nedeniyle ilk
dilimden çıkarıldı.

## ADR-DEP-001: Adopt PyCozmo

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** Telefonsuz Wi-Fi kontrolü ve WAV oynatma gerekir.

**Decision.** MIT lisanslı `pycozmo` robot adaptörünün tek bağımlılığıdır.

**Consequences.** Eski UDP kütüphanesi adaptör arkasında izole edilir.

**Considered alternatives.** Resmî SDK telefon uygulaması istediği için
reddedildi.

## ADR-DEP-002: Adopt Vosk Turkish

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** Çevrimdışı ve küçük Türkçe STT gerekir.

**Decision.** Apache-2.0 Türkçe Vosk modeli push-to-talk adaptöründe kullanılır.

**Consequences.** Model ayrıca indirilir; doğruluk `ADR-009` ile ölçülür.

**Considered alternatives.** Google STT bulut ister; faster-whisper daha ağırdır.

## ADR-DEP-003: Adopt sounddevice

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** PortAudio mikrofon verisini Python'a taşımak gerekir.

**Decision.** `sounddevice` yalnız voice extra içinde kullanılır.

**Consequences.** Mikrofon izni ve PortAudio durumu `doctor` tarafından görülür.

**Considered alternatives.** PyAudio kurulumu macOS'ta daha sürtünmeli bulundu.

## ADR-DEP-004: Adopt Python quality toolchain

- **Status:** accepted
- **Date:** 2026-08-14

**Context.** Iron Rules otomatik uygulanmalıdır.

**Decision.** Dev grubunda pytest, pytest-cov, ruff, mypy, pre-commit ve
pip-audit kullanılır.

**Consequences.** Dev kurulumu runtime'dan ayrıdır; CI aynı komutları çalıştırır.

**Considered alternatives.** Yalnız stdlib unittest coverage, type ve güvenlik
kapılarını tek başına sağlayamadığı için reddedildi.

## How to add a new ADR

1. Sonraki kalıcı ID'yi seç.
2. İndekse `proposed` satırı ekle.
3. Context, Decision, Consequences ve Considered alternatives bölümlerini yaz.
4. Kabul edilince iki durumu da güncelle.
5. `.genesis/PROGRESS.md` içine tek satır ekle.

## See also

- `.genesis/CONSTITUTION.md` — karar sınırları
- `docs/ARCHITECTURE.md` — kararların teknik sonucu
- `.genesis/PROGRESS.md` — karar ve uygulama günlüğü
