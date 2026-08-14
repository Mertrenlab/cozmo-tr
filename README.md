# Cozmo TR

Harici mikrofondan Türkçe komut alan ve yanıtını Cozmo hoparlöründen Türkçe
veren, telefonsuz çalışan güvenli prototip.

## What this is

Cozmo TR klasik Anki Cozmo'yu doğrudan Wi-Fi üzerinden kontrol eder. İlk hedef
Türkçe deterministik komutlar, sınırlı hareket ve robot hoparlöründen Türkçe
sestir; telefon uygulaması ve bulut zorunlu değildir.

Şu an yazılım prototipi hazırdır. Donanım olmadan parser, güvenlik, STT
sınırları ve ses biçimi test edilir; fiziksel robot ayrı smoke testte zeminde
doğrulanır.

## Status

Software MVP ready — physical Cozmo smoke test pending.

## Quick start

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev,voice,robot]'
mkdir -p models
curl -L https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip \
  -o /tmp/vosk-model-small-tr-0.3.zip
unzip /tmp/vosk-model-small-tr-0.3.zip -d models
.venv/bin/python -m pytest --cov=cozmo_tr --cov-branch --cov-fail-under=85
.venv/bin/cozmo-tr doctor
.venv/bin/cozmo-tr parse "ileri git"
.venv/bin/cozmo-tr say "Merhaba, ben Cozmo"
```

Python 3.11 veya 3.12 kullanın. Vosk modelini Cozmo Wi-Fi'ye geçmeden indirin;
robotun ağı internete çıkmaz.

## Demo

Önce robot olmadan mikrofon ve komut zincirini deneyin:

```bash
.venv/bin/cozmo-tr run --once
```

Gerçek robot için Cozmo'yu şarj platformunda uyandırın, kaldırma kolunu bir
kez indirip kaldırarak ekranda Wi-Fi parolasını gösterin ve Mac'i `COZMO_...`
ağına bağlayın. Robotu ilk denemede masada değil, boş zeminde tutun:

```bash
.venv/bin/cozmo-tr doctor
.venv/bin/cozmo-tr run --once --robot
```

Konuşma örnekleri: `ileri 50`, `geri 30`, `sola 45`, `sağa 45`, `dur` ve
`söyle merhaba ben Cozmo`. Hareket 150 mm, dönüş 90 derece ile sınırlıdır;
firmware cliff-stop bağlantı sırasında açılır.

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
