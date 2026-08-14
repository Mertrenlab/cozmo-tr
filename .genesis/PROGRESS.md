# Progress — Cozmo TR

Projenin append-only çalışma günlüğü. Her anlamlı işlem şu biçimde eklenir:

```text
YYYY-MM-DD HH:MM | ADR-refs | summary
```

## Log

2026-08-14 20:20 | ADR-001 | Genesis Protocol kit generated; 13 initial ADRs logged
2026-08-14 20:25 | ADR-002, ADR-004 | Implements safe parser core and macOS Turkish Cozmo WAV; 15 tests pass

## Append protocol for agents

1. İlgili ADR veya risk ID'lerini seç; yoksa `—` kullan.
2. Şimdiki zamanlı, 120 karakteri aşmayan tek satır yaz.
3. Bu dosyanın sonuna ekle; önceki kayıtları düzenleme.

Özellik, karar, risk, iki dosyayı aşan refactor, bağımlılık ve release anlamlı
iştir. Tek yazım veya biçim düzeltmesi kayıt gerektirmez.

## See also

- `.genesis/DECISIONS.md` — ADR kayıtları
- `.genesis/RISKS.md` — risk kayıtları
- `docs/DEFINITION_OF_DONE.md` — ne zaman ilerleme yazılır
