# Cozmo TR — Donanım smoke testi

Bu kontrol listesi gerçek robot durumunu yazılım testlerinden ayrı kaydeder.
Testleri boş zeminde, Cozmo tam şarjlıyken ve `dur` komutu hazırken yapın.

## Ön koşullar

- [ ] `.venv/bin/cozmo-tr doctor` zorunlu kontrolleri `[OK]` gösteriyor.
- [ ] Mac `COZMO_...` Wi-Fi ağına bağlı; VPN ve mobil uygulama kapalı.
- [ ] Robot masa kenarında değil; paletlerin çevresi boş.
- [ ] Küpler/platform test edilecekse pilleri çalışıyor ve robota yakın.

## A — Bağlantı ve motorsuz etkiler

Her satırı ayrı çalıştırın; sonuçtan sonra kutuyu işaretleyin.

```bash
.venv/bin/cozmo-tr execute "söyle merhaba, ben Cozmo"
.venv/bin/cozmo-tr execute "pilin ne kadar"
.venv/bin/cozmo-tr execute "ışıklarını kırmızı yap"
.venv/bin/cozmo-tr execute "kafa ışığını aç"
.venv/bin/cozmo-tr execute "mutlu ol"
.venv/bin/cozmo-tr execute "fotoğraf çek"
```

- [ ] Türkçe ses Cozmo hoparlöründen anlaşılır geliyor.
- [ ] Pil voltajı söyleniyor.
- [ ] Sırt/kafa ışığı ve OLED yüz doğru değişiyor.
- [ ] `captures/` altında tek JPEG oluşuyor.

## B — Sınırlı motorlar

```bash
.venv/bin/cozmo-tr execute "başını kaldır"
.venv/bin/cozmo-tr execute "kolunu kaldır"
.venv/bin/cozmo-tr execute "ileri 50"
.venv/bin/cozmo-tr execute "sola 45"
.venv/bin/cozmo-tr execute "dur"
.venv/bin/cozmo-tr execute "selam ver"
.venv/bin/cozmo-tr execute "dans et"
```

- [ ] Baş ve kol mekanik sınırı zorlamıyor.
- [ ] Robot yaklaşık 50 mm ilerliyor ve yaklaşık 45 derece dönüyor.
- [ ] `dur` motorları durduruyor.
- [ ] Selam/dans rutinleri sonlu biçimde tamamlanıyor.

Bir hareket yönü tersse testi bırakın; başka motorlu komut çalıştırmayın.

## C — Küpler ve şarj platformu

```bash
.venv/bin/cozmo-tr execute "kaç küp var"
.venv/bin/cozmo-tr execute "küpü mavi yak"
.venv/bin/cozmo-tr execute "küp ışıklarını kapat"
.venv/bin/cozmo-tr execute "şarj ışığını yeşil yak"
.venv/bin/cozmo-tr execute "şarj ışığını kapat"
```

- [ ] Cozmo görünen küp sayısını söylüyor.
- [ ] Bir kübün dört LED'i mavi yanıyor ve kapanıyor.
- [ ] Platformun üç LED'i yeşil yanıyor ve kapanıyor.

Bulunamayan aksesuar komutu sonlu sürede Türkçe hatayla bitmelidir; terminal
sonsuz beklememelidir.

## D — Mikrofon

```bash
.venv/bin/cozmo-tr run --once --robot
```

`başını kaldır` deyin.

- [ ] Terminal duyduğu metni gösteriyor.
- [ ] Doğru eylem yalnız bir kez uygulanıyor.
- [ ] Cozmo kendi hoparlör sesini yeni komut sanmıyor.

## E — Top (top geldiğinde)

Kırmızı, yuvarlak topu aydınlık zeminde kameranın önüne koyun:

```bash
.venv/bin/cozmo-tr execute "topu bul"
.venv/bin/cozmo-tr execute "topla oyna"
```

- [ ] Top yokken robot ileri hareket üretmiyor.
- [ ] Top varken kısa dönüş/yaklaşma adımları zemin sınırında kalıyor.
- [ ] Her oturum `dur` ile bitiyor.

Top yoksa bu bölümü başarısız saymayın; `hardware_pending` olarak bırakın.

## Kayıt

Tarih, macOS sürümü, Python sürümü, Cozmo firmware'i, geçen/kalan maddeler ve
hata mesajını bir GitHub issue'suna yazın. Fiziksel testi geçmeyen yeteneği
`ready` olarak işaretlemeyin.
