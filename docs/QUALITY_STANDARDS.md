# Quality Standards — Cozmo TR

Bu standartlar uygulanır; istisna yeni bir ADR gerektirir.

## Code shape

- Fonksiyonlar docstring ve boşluklar hariç en çok 30 satırdır. Bu sınır tek
  sorumluluğu ve donanım olmadan test edilebilirliği korur.
- Python dosyaları en çok 200 satırdır. Büyük dosya modül sınırının kaybolduğu
  sinyali sayılır.
- Cyclomatic complexity en çok 8, nesting en çok 3'tür. Robot güvenliğinde
  gizli dallar bırakmamak için `ruff C901` uygulanır.
- Her modül başlığı sorumluluğunu ve bilerek yapmadığı işi söyler.

## Type safety

Tüm public API'ler tam tiplidir ve `mypy --strict` geçer. `Any` yalnız gerekçe
yorumuyla kullanılabilir; çünkü adaptör sınırındaki belirsizlik domain'e
sızmamalıdır.

## Testing

Test piramidi yaklaşık yüzde 80 unit, yüzde 15 integration ve yüzde 5 manuel
hardware smoke testtir. TDD commit geçmişinde `test:` kırmızı adımı, ardından
`feat:`/`fix:` yeşil adımıyla görünür.

- Line coverage en az yüzde 85, branch coverage en az yüzde 80.
- Her public API'nin en az bir hata yolu testi vardır.
- Her hata düzeltmesi önce regresyon testi alır.
- Fiziksel robot CI koşulu değildir; portlar sahte adaptörlerle sınanır.

### Critical paths

Aşağıdakiler yüzde 100 branch coverage gerektirir; yanlış bir dal fiziksel
hasar veya beklenmedik hareket doğurabilir.

- Türkçe komuttan `RobotAction` üretimi
- Hareket güvenlik sınırları ve `STOP` önceliği
- Belirsiz girdinin hareketsiz reddedilmesi
- TTS WAV biçimi doğrulaması

## Version control hygiene

- Conventional commits zorunludur; tarih makine ve insan tarafından okunur.
- Bir commit tek mantıksal değişiklik taşır; geri alma güvenli kalır.
- Diff en çok 400 LoC'dir; belgeler ve salt silmeler hariçtir.
- Yorum satırına alınmış kod yoktur; Git geçmişi saklama işini yapar.
- Anlamlı sayılar isimlendirilmiş sabittir; güvenlik değerlerinin kaynağı
  görünür kalır.

## Dependency discipline

Runtime bütçesi üç Python bağımlılığıdır: `pycozmo`, `vosk`, `sounddevice`.
macOS `say` ve `afconvert` sistem araçlarıdır. Her bağımlılık ayrı `ADR-DEP`
kaydına sahiptir; bütçeyi aşmak yeni ADR gerektirir.

Sürümler `requirements.lock` içinde sabitlenir. Tek satırlık problem için yeni
paket alınmaz; bakım ve güvenlik yüzeyi küçük tutulur.

## Operability

- Üretim yolları `print` değil yapılandırılmış JSON log kullanır.
- Hatalar yakalanır, bağlamla yeniden yükseltilir veya kullanıcıya uygulanabilir
  mesajla çevrilir; bare `except` ve sessiz yutma yoktur.
- `doctor` bağımlılıkları ve bağlantı önkoşullarını hareketten önce denetler.
- Robot kapanışında önce `STOP`, sonra bağlantı kapatma denenir.

## Security baseline

- Secret commit edilmez; gelecekteki anahtarlar ortam değişkenidir.
- CLI, STT ve dosya yolları sınırda doğrulanır.
- Ham ses ve konuşma metni varsayılan olarak kalıcılaştırılmaz.
- CI bağımlılık güvenlik taraması çalıştırır.

## Documentation requirements

Her public fonksiyon amaç, girdi, çıktı, yan etki ve hata durumlarını belgeleyen
docstring taşır. README yeni kullanıcıyı sıfırdan geçen teste ulaştırır. Yapısal
kararlar append-only ADR olarak kaydedilir.

## AI-readability

Kuralların gerekçesi yanında bulunur; ADR referansları sabittir. Anlamlı her
değişiklik `.genesis/PROGRESS.md` günlüğüne eklenir. Tekrarlanan proje terimleri
`.genesis/GLOSSARY.md` içine yazılır.

## CI/CD enforcement

Yerel ve CI komutları:

```bash
python -m ruff check src tests
python -m mypy --strict src
python -m pytest --cov=cozmo_tr --cov-branch --cov-fail-under=85
```

Pre-commit aynı kontrolleri çalıştırır. Ana dala birleşme için yeşil CI gerekir;
prototip tek geliştirici olsa bile aynı tekrar üretilebilir yol korunur.

## Rationale notes

Genesis varsayılanları gevşetilmedi. Donanım E2E testi CI dışında tutuldu;
çünkü robot çevresel bir cihazdır, fakat aynı port sözleşmesi integration
testleri ve manuel smoke test ile doğrulanır (`ADR-007`).

## See also

- `.genesis/CONSTITUTION.md` — standing principles
- `docs/DEFINITION_OF_DONE.md` — tamamlanma kontrol listeleri
- `.genesis/DECISIONS.md` — istisna ve bağımlılık kararları
