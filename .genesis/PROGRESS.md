# Progress — Cozmo TR

Projenin append-only çalışma günlüğü. Her anlamlı işlem şu biçimde eklenir:

```text
YYYY-MM-DD HH:MM | ADR-refs | summary
```

## Log

2026-08-14 20:20 | ADR-001 | Genesis Protocol kit generated; 13 initial ADRs logged
2026-08-14 20:25 | ADR-002, ADR-004 | Implements safe parser core and macOS Turkish Cozmo WAV; 15 tests pass
2026-08-14 21:05 | ADR-002, ADR-007 | Adds CLI, Vosk and PyCozmo adapters; 43 tests pass at 96.25% coverage
2026-08-14 21:07 | ADR-010, RISK-O5 | Pins Python 3.11–3.12 and Vosk 0.3.44 for Apple Silicon compatibility
2026-08-14 21:15 | ADR-007, RISK-O4 | Cleans up the PyCozmo client after any partial connection failure
2026-08-14 21:32 | ADR-006, ADR-007 | Publishes private GitHub repo; branch and tag CI pass
2026-08-14 22:10 | ADR-CON-001, RISK-O6, RISK-O7 | Expands macOS-only direct capability scope; excludes ball games
2026-08-15 00:05 | ADR-CON-002, RISK-C6 | Restores ball play and full phased Cozmo vision with explicit capability states

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

2026-08-15 00:24 | ADR-CON-002, ADR-011 | Adds bounded ball, cube, charger and full direct Cozmo capability paths
2026-08-15 00:24 | ADR-007 | Publishes typed hardware execute flow and runbook; 94 tests pass at 96.00% coverage
2026-08-15 00:49 | ADR-CON-003, RISK-O9 | Ships local dashboard and Finder app; 115 tests pass at 95.83%
2026-08-15 00:59 | ADR-002, ADR-CON-003 | Adds styled file preview and bounded keyboard drive modal; 117 tests pass
