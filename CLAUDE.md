# CLAUDE.md

This file extends `AGENTS.md` with Claude-specific guidance. Read `AGENTS.md`
first.

## Posture

Prefer small, test-first changes and expose safety consequences before code.
Treat physical movement as a critical path, not an ordinary side effect.

The user's Phase 0 self-assessment is **I trust the agent**: act decisively
inside accepted ADRs, log new decisions, and summarize them for awareness.

## Tool preferences

- Plan tasks touching more than three files.
- Prefer small patches over rewrites; keep diffs below 400 LoC.
- Draft an ADR before structural changes or dependencies.
- Append meaningful work to `.genesis/PROGRESS.md`.

## What to ask vs. what to assume

Ask before constitutional change, new dependency, critical-path relaxation, or
new module coupling. Assume routine implementation and test choices already
allowed by the architecture.

## Project-specific anti-patterns

- Calling PyCozmo directly from CLI, STT, parser, or future LLM code
- Treating an unrecognized utterance as the nearest movement
- Enabling continuous listening before TTS echo suppression exists
- Downloading models after switching the Mac to Cozmo's offline Wi-Fi
- Copying code from a repository without a compatible license

## Project-specific opportunities

- Improve Turkish command normalization with regression fixtures.
- Keep adapters small enough to replace Vosk or macOS TTS independently.
- Turn each physical failure into a fake-adapter regression test.

## When the kit is out of sync with the code

Surface the drift, decide whether kit or code is wrong, then log the resolution.
Do not silently normalize contradictions.

## See also

- `AGENTS.md` — platform-independent contract
- `docs/QUALITY_STANDARDS.md` — rules
- `.genesis/DECISIONS.md` — decision log
