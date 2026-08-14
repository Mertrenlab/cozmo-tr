# Cozmo TR

Harici mikrofondan Türkçe komut alan ve yanıtını Cozmo hoparlöründen Türkçe
veren, telefonsuz çalışan güvenli prototip.

## What this is

Cozmo TR klasik Anki Cozmo'yu doğrudan Wi-Fi üzerinden kontrol eder. İlk hedef
Türkçe deterministik komutlar, sınırlı hareket ve robot hoparlöründen Türkçe
sestir; telefon uygulaması ve bulut zorunlu değildir.

Şu an MVP geliştirilmektedir. Donanım olmadan parser, güvenlik ve ses biçimi
test edilir; fiziksel robot ayrı smoke testte zeminde doğrulanır.

## Status

MVP in progress — Genesis kit complete, implementation follows TDD.

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev,voice,robot]'
.venv/bin/python -m pytest --cov=cozmo_tr --cov-branch --cov-fail-under=85
.venv/bin/cozmo-tr doctor
.venv/bin/cozmo-tr parse "ileri git"
.venv/bin/cozmo-tr say "Merhaba, ben Cozmo"
```

Vosk Türkçe modeli Cozmo Wi-Fi'ye bağlanmadan önce indirilecektir. Fiziksel
bağlantı adımları MVP smoke testi tamamlanınca bu bölüme eklenecektir.

## Project structure

```text
.genesis/          karar, risk ve ilerleme durumu
docs/              kapsam, mimari ve kalite sözleşmesi
src/cozmo_tr/      uygulama modülleri
tests/             donanımsız otomatik testler
AGENTS.md          ajan çalışma sözleşmesi
```

## How to contribute

Önce `AGENTS.md` ve `.genesis/DECISIONS.md` dosyalarını okuyun. Testi uygulamadan
önce yazın ve anlamlı her işten sonra ilerleme günlüğünü append edin.

## Documentation map

- `.genesis/CONSTITUTION.md` — değişmez kuruluş ilkeleri
- `docs/CHARTER.md` — görev ve kapsam
- `docs/ARCHITECTURE.md` — teknik tasarım
- `docs/QUALITY_STANDARDS.md` — uygulanan kod kuralları
- `docs/ROADMAP.md` — fazlar
- `docs/DEFINITION_OF_DONE.md` — DoD kontrol listeleri
- `.genesis/DECISIONS.md` — append-only karar kaydı
- `.genesis/RISKS.md` — bilinen riskler
- `.genesis/PROGRESS.md` — çalışma günlüğü
- `AGENTS.md` — ajan sözleşmesi

## License

MIT. Bağımlılıkların ve indirilen ses/STT modellerinin kendi lisansları geçerlidir.

## See also

- `docs/CHARTER.md` — neden ve kim için
- `docs/ROADMAP.md` — sıradaki teslimler
- `.genesis/DECISIONS.md` — neden bu teknoloji
