# Definition of Done — Cozmo TR

Bir iş ancak aşağıdaki koşullar sağlandığında tamamlanmıştır.

## For a function or class

- [ ] Test uygulamadan önce yazıldı; Git geçmişi red → green gösteriyor.
- [ ] Line ≥85%, branch ≥80%; kritik yolda branch %100.
- [ ] Public API tipli ve `mypy --strict` geçiyor.
- [ ] Fonksiyon ≤30 LoC, Python dosyası ≤200 LoC, complexity ≤8.
- [ ] Docstring amaç, girdi, çıktı, yan etki ve hata durumunu söylüyor.
- [ ] Magic number ve yorum satırına alınmış kod yok.

## For a feature

- [ ] Tüm birimler function-level DoD'u geçiyor.
- [ ] Ana akış ve en az bir hata yolu integration testinde.
- [ ] Kullanıcı hatası ne olduğunu ve sonraki adımı Türkçe söylüyor.
- [ ] INFO ve ERROR olayları doğru yapılandırılmış log üretiyor.
- [ ] Yeni bağımlılığın ADR'si var.
- [ ] `.genesis/PROGRESS.md` güncellendi.

## For a hardware feature

- [ ] Donanımsız fake-adapter testleri geçiyor.
- [ ] Hareket `SafetyPolicy` üzerinden geçiyor.
- [ ] Fiziksel test zeminde ve acil durdurma hazırken yapıldı.
- [ ] Smoke test sonucu tarih ve donanım bilgisiyle kaydedildi.

## For a release

- [ ] Scope içindeki özellikler feature-level DoD'u geçiyor.
- [ ] CI yeşil ve güvenlik taraması temiz.
- [ ] Changelog conventional commitlerden üretildi.
- [ ] `doctor` desteklenen temiz ortamda doğrulandı.
- [ ] Bilinen iyi Git etiketi ve rollback adımları doğrulandı.

## See also

- `docs/QUALITY_STANDARDS.md` — bu kontrollerin kuralları
- `.genesis/PROGRESS.md` — tamamlanan iş günlüğü
- `.genesis/RISKS.md` — donanım ve kullanıcı riskleri
