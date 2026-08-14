# Roadmap — Cozmo TR

Teslim küçük dikey dilimler halinde ilerler: bugün donanımsız çalışan ve sesi
üreten v0.1, ilk fiziksel oturumda robot smoke testi, sonra STT kalitesi.

## Phase 0 — Genesis (complete)

- Konsey değerlendirmesi
- Proje kiti ve Git deposu
- Mimari, risk ve karar kayıtları

## Phase 1 — MVP (target: 2026-08-15)

### Goals

- Türkçe parser ve güvenlik kapısı
- Text dry-run ve `doctor`
- macOS Türkçe WAV üretimi
- PyCozmo portu ve bağlantı smoke komutu
- Push-to-talk Vosk adaptörü

### Cut-line

Metinle verilen `dur`, `ileri`, `geri`, `sol`, `sağ` komutları güvenli sonucu
üretmeli; Türkçe ses doğru WAV biçiminde çıkmalıdır. Bunun altı demo değildir.

### Deferred

- Piper doğal ses
- faster-whisper karşılaştırması
- LLM sohbeti
- Wake-word ve web paneli

## Phase 2 — Physical validation (target: first robot session)

### Goals

- Cozmo Wi-Fi bağlantısı ve uçurum koruması
- Hoparlörden Türkçe WAV
- Beş komutluk masa değil zemin smoke testi
- 20 cümlelik STT kabul raporu

### Exit

En az 16/20 doğru STT ve beş fiziksel komuttan en az dört başarı.

## Phase 3 — Natural interaction (target: after MVP evidence)

### Goals

- Piper sesi değerlendirmek
- Gerekirse faster-whisper'a geçmek
- Yapılandırılmış araç çağrılı yerel Ollama sohbeti
- Konuşurken mikrofonu durdurmak

## Cut-list (post-MVP, ordered)

1. Piper Türkçe ses
2. faster-whisper yedeği
3. Yerel LLM
4. Wake-word
5. Web paneli ve kamera

## Non-goals

- Denetimsiz otonom hareket
- Bulut zorunluluğu veya mobil uygulama
- Çoklu robot ve üretim sunucusu
- MVP'de yüz tanıma ve kalıcı hafıza

## See also

- `docs/CHARTER.md` — bu planın teslim ettiği görev
- `.genesis/DECISIONS.md` — faz kararları
- `.genesis/PROGRESS.md` — gerçekleşen ilerleme
