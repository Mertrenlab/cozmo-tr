# Cozmo TR

Anki Cozmo'yu telefon uygulaması olmadan, macOS üzerinden Türkçe konuşturan ve
Türkçe komutlarla kontrol eden güvenli, çevrimdışı çalışma zamanı.

Robot doğrudan kendi `COZMO_...` Wi-Fi ağı üzerinden PyCozmo ile kontrol edilir.
Mac'in mikrofonu Türkçe konuşmayı Vosk ile yerelde çözer; yanıt macOS Türkçe
sesiyle WAV'a çevrilip Cozmo'nun hoparlöründen çalınır. Çalışırken internet ve
Android/iPhone gerekmez.

Günlük kullanımda terminal gerekmez: ilk kurulumdan sonra Finder'daki
`Cozmo TR.app` çift tıklanır ve kontrol paneli tarayıcıda otomatik açılır.

## Neler yapıyor?

| Grup | Türkçe örnekler | Durum |
|---|---|---|
| Hareket | `ileri 50`, `geri 30`, `sola 45`, `sağa 45`, `dur` | Yazılım testli; zemin smoke testi gerekli |
| Konuşma | `söyle merhaba`, `nasılsın`, `adın ne`, `şaka yap` | Cozmo hoparlörüne yerel Türkçe WAV |
| Baş ve kol | `başını kaldır`, `kolunu indir` | Açı/yükseklik sınırları etkin |
| Işıklar | `ışıklarını kırmızı yap`, `kafa ışığını aç` | Sırt ve kafa ışıkları |
| OLED yüz | `mutlu ol`, `üzgün ol`, `şaşır`, `kızgın ol` | Yerel üretilen ifadeler |
| Kamera | `fotoğraf çek` | `captures/` içine tek kare; sürekli kayıt yok |
| Durum/ses | `pilin ne kadar`, `sesini kıs`, `sesini aç` | Pil voltajı ve hoparlör seviyesi |
| Rutinler | `selam ver`, `dans et`, `kafanı salla`, `görüşürüz` | Sonlu, güvenli ilkel eylemler |
| Küpler | `kaç küp var`, `küpü mavi yak`, `küp ışıklarını kapat` | Üç küp tipi ve dört LED; fiziksel test gerekli |
| Şarj platformu | `şarj ışığını mavi yak`, `şarj ışığını kapat` | Üç platform LED'i; fiziksel test gerekli |
| Kırmızı top | `topu bul`, `topla oyna` | Sentetik görüntü testli; gerçek top testi gerekli |

Makinedeki güncel listeyi görmek için:

```bash
.venv/bin/cozmo-tr commands
.venv/bin/cozmo-tr capabilities
.venv/bin/cozmo-tr capabilities --json
```

`experimental`, kodun hazır fakat gerçek robot smoke testinin henüz kayıtlı
olmadığını; `hardware_pending`, ilgili aksesuarın fiziksel doğrulamasının
beklediğini belirtir. Proje doğrulanmamış bir özelliği “hazır” diye göstermez.

## 1. İnternet varken Mac'i hazırla

Python 3.11 veya 3.12 kullanın. Python 3.13, PyCozmo'nun eski `chunk`
bağımlılığı nedeniyle desteklenmez.

```bash
git clone https://github.com/Mertrenlab/cozmo-tr.git
cd cozmo-tr
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev,voice,robot]'
mkdir -p models
curl -L https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip \
  -o /tmp/vosk-model-small-tr-0.3.zip
unzip /tmp/vosk-model-small-tr-0.3.zip -d models
.venv/bin/cozmo-tr doctor
```

Kurulum testi:

```bash
.venv/bin/python -m pytest --cov=cozmo_tr --cov-branch --cov-fail-under=85
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy --strict src
```

Modeli ve Python paketlerini Cozmo ağına geçmeden indirin; Cozmo'nun Wi-Fi ağı
internete çıkmaz.

## 2. Mac'i Cozmo'ya bağla

1. Cozmo'yu şarj platformunda uyandırın.
2. Kaldırma kolunu indirip kaldırarak robot ekranındaki Wi-Fi adı ve parolayı
   gösterin.
3. Mac'in Wi-Fi menüsünden `COZMO_...` ağına bağlanın.
4. VPN'i kapatın ve resmî Cozmo uygulamasının robota bağlı olmadığından emin
   olun.
5. Hareket testleri için robotu masa yerine boş ve aydınlık zemine koyun.

Mac bu sırada “internet yok” gösterebilir; bu beklenen durumdur.

## 3. Terminal kullanmadan dashboard'u aç

Finder'da proje klasörünü açıp `Cozmo TR.app` uygulamasına çift tıklayın. İlk
açılışta macOS engellerse uygulamaya sağ tıklayıp `Aç` seçin. Uygulamayı proje
klasöründen taşımayın; isterseniz Dock'a veya masaüstüne alias ekleyin.

Panel açılınca:

1. `Cozmo'ya bağlan` düğmesine basın.
2. `Sürüş modunu aç` düğmesine basıp ok tuşları veya `W A S D` ile sürün;
   `Space` durdurur, `Esc` paneli kapatır.
3. Hazır ifade, ışık, küp ve kamera düğmelerinden birini seçin.
4. Serbest Türkçe komutu kutuya yazın veya `Bas ve konuş` düğmesini kullanın.
5. İşiniz bitince `Bağlantıyı kes` düğmesine basın.

Panel yalnız bu Mac'teki `127.0.0.1` adresinde çalışır; internete yayınlanmaz.
`src/cozmo_tr/web/index.html` dosyasını doğrudan açmayın; bu yalnız görsel
önizlemedir ve robota bağlanamaz.
Tarayıcı sekmesini yanlışlıkla kapatırsanız uygulamayı yeniden çift tıklamak
mevcut paneli açar. Geliştirici alternatifi:

```bash
.venv/bin/cozmo-tr dashboard
```

## 4. İsteğe bağlı komut satırı donanım testi

Tek bir yazılı komutu bağlanıp çalıştırır ve bağlantıyı güvenle kapatır:

```bash
.venv/bin/cozmo-tr execute "söyle merhaba, ben Cozmo"
.venv/bin/cozmo-tr execute "başını kaldır"
.venv/bin/cozmo-tr execute "mutlu ol"
.venv/bin/cozmo-tr execute "pilin ne kadar"
```

Hareketi yalnız zeminde deneyin:

```bash
.venv/bin/cozmo-tr execute "ileri 50"
.venv/bin/cozmo-tr execute "sağa 45"
.venv/bin/cozmo-tr execute "dur"
```

Küp ve platform yakındaysa:

```bash
.venv/bin/cozmo-tr execute "kaç küp var"
.venv/bin/cozmo-tr execute "küpü mavi yak"
.venv/bin/cozmo-tr execute "şarj ışığını yeşil yak"
```

Tam doğrulama sırası için [donanım smoke testi](docs/HARDWARE_SMOKE_TEST.md)
belgesini kullanın.

## 5. İsteğe bağlı komut satırı mikrofonu

Dashboard veya Terminal ilk dinlemede mikrofon izni isteyebilir. İzni
`Sistem Ayarları > Gizlilik ve Güvenlik > Mikrofon` bölümünden verin.

Tek dinleme penceresi:

```bash
.venv/bin/cozmo-tr run --once --robot
```

Birden çok push-to-talk turu:

```bash
.venv/bin/cozmo-tr run --robot
```

Her tur için Enter'a basın, ekranda `Dinliyorum` yazınca yaklaşık dört saniye
konuşun. Çıkmak için `q` yazın. Mikrofon Mac'in mikrofonudur; Cozmo'nun
mikrofonu kullanılmaz.

## Güvenlik ve mahremiyet

- Hareket en fazla 150 mm, dönüş en fazla 90 derece; baş, kol ve ses değerleri
  de sınırlandırılır.
- Bağlantıda firmware uçurum durdurması açılır; yine de ilk testler zemindedir.
- Her motor kararı `SafetyPolicy` üzerinden geçer.
- Mikrofon sesi ve transkript saklanmaz; buluta gönderilmez.
- Kamera yalnız açık `fotoğraf çek` komutuyla bir kare kaydeder.
- PyCozmo'nun güvensiz üçüncü taraf animasyon arşivi otomatik indirilmez.

## Sorun giderme

- `Cozmo bağlantısı kurulamadı`: Mac'in `COZMO_...` ağında olduğunu, robotun
  uyanık olduğunu ve başka uygulamanın bağlı olmadığını kontrol edin.
- `Türkçe Vosk modeli bulunamadı`: model klasörü
  `models/vosk-model-small-tr-0.3/` altında olmalıdır.
- Mikrofon hatası: macOS mikrofon iznini ve `.venv/bin/cozmo-tr doctor`
  çıktısını kontrol edin.
- `Küp bulunamadı`: küp pilini kontrol edin, küpü hareket ettirip robota
  yaklaştırın ve komutu yeniden verin.
- Kamera zaman aşımı: ortamı aydınlatın, robot bağlantısını yenileyin.

## Proje yapısı

```text
.genesis/          karar, risk ve ilerleme kayıtları
Cozmo TR.app/      Finder'dan çift tıklanan yerel dashboard başlatıcısı
docs/              mimari, yol haritası ve smoke test
src/cozmo_tr/      uygulama ve donanım adaptörleri
tests/             donanımsız otomatik testler
AGENTS.md          katkı ve güvenlik sözleşmesi
```

Katkıdan önce `AGENTS.md` ve `.genesis/DECISIONS.md` dosyalarını okuyun. Test
uygulamadan önce yazılır; tüm Python dosyaları 200 satırın, fonksiyonlar 30
satırın altında tutulur.

## Lisans

Proje MIT lisanslıdır. PyCozmo, Vosk ve indirilen dil modelinin kendi lisansları
ayrıca geçerlidir.
