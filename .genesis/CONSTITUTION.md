# Constitution — Cozmo TR

Adopted: 2026-08-14
Amendments: see `ADR-CON-*` entries in `.genesis/DECISIONS.md`

Bu anayasa projenin değişmez kuruluş sözleşmesidir. Sonraki kararlar bu
çerçevede alınır; değişiklik için Genesis Konseyi yeniden çalıştırılır.

## Article I — Purpose

Cozmo TR, teknik kurulumla uğraşmak istemeyen bir demo kullanıcısının harici
mikrofondan Türkçe komut verip Anki Cozmo'dan güvenli hareket ve Türkçe sesli
yanıt almasını sağlar.

## Article II — Non-purposes

- MVP doğal ve sınırsız sohbet asistanı değildir.
- Web paneli, kamera, yüz tanıma, hafıza ve otonom gezinme sunmaz.
- Mobil Cozmo uygulamasına veya sürekli bulut bağlantısına dayanmaz.
- Belirsiz bir girdiyi hareket komutu olarak tahmin etmez.

## Article III — Founding constraints

- İlk çalışan hedef macOS ve gerçek Anki Cozmo donanımıdır.
- Robotun mikrofonu yoktur; bilgisayar veya USB mikrofon kullanılır.
- Cozmo'ya telefon olmadan doğrudan Wi-Fi ve PyCozmo ile bağlanılır.
- İlk demo mümkün olan en kısa sürede, çevrimdışı bileşenlerle çıkarılır.
- Kaynak repolar mimari referanstır; lisanssız kod kopyalanmaz.

## Article IV — Standing principles

- Motor komutları bağımsız güvenlik kapısından geçer.
- Uçurum koruması gerçek robotta varsayılan olarak açıktır.
- Belirsiz komut hareket üretmez; güvenli biçimde reddedilir.
- TDD geçmişte kırmızı, yeşil ve düzenleme adımlarıyla kanıtlanır.
- Sessiz hata yoktur; kullanıcı Türkçe ve eyleme dönük hata görür.
- Fonksiyonlar 30, Python dosyaları 200 satırı geçmez.
- Donanım sınırları portlarla ayrılır ve test çiftleriyle doğrulanır.
- Yeni bağımlılık önce ADR ile gerekçelendirilir.
- Basit çalışan kesit, spekülatif özellikten önce gelir.

## Article V — Most-fragile assumption

> Küçük Türkçe Vosk modeli, demo ortamındaki hedef komutların en az yüzde
> 80'ini güvenilir biçimde tanıyabilir.

## Article VI — Kill criteria

- Sabit 20 cümlelik kabul setinde iki STT motoru da 16/20 altındaysa sesli
  komut yaklaşımı durdurulur veya kapsam yeniden belirlenir.
- Güvenlik kapısı aşılabiliyor ya da uçurum koruması doğrulanamıyorsa fiziksel
  demo yayınlanmaz.
- Desteklenen macOS kurulumunda tekrarlanabilir robot bağlantısı sağlanamazsa
  doğrudan Wi-Fi yaklaşımı yeniden değerlendirilir.

## Amendment procedure

Bu anayasa yalnızca önerilen değişikliğe odaklı Genesis Konseyi yeniden
çalıştırılarak ve kullanıcı açıkça onay vererek değişir. Değişiklikler
`.genesis/DECISIONS.md` içinde `ADR-CON-N` olarak kaydedilir.

## See also

- `docs/CHARTER.md` — operasyonel kapsam
- `docs/QUALITY_STANDARDS.md` — Article IV kurallarının uygulanması
- `.genesis/DECISIONS.md` — anayasa çerçevesindeki kararlar
