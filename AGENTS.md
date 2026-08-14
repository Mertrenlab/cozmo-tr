# AGENTS.md

> Agent contract for Cozmo TR. Read this top-to-bottom before writing or
> modifying code. The Iron Rules are enforced.

## Project, in one paragraph

Cozmo TR lets a non-technical demo user speak Turkish through an external
microphone and receive bounded robot actions plus Turkish audio from an Anki
Cozmo without the mobile app. Its fragile assumption is that the small Turkish
Vosk model recognizes at least 80% of the fixed demo utterances.

## Hard rules (you will be held to these)

- TDD with proof in commit history; the test commit precedes implementation
- Function ≤30 LoC, Python file ≤200 LoC, complexity ≤8
- Coverage ≥85% line, ≥80% branch; 100% on critical paths
- Conventional commits; PR/diff ≤400 LoC
- No magic numbers, commented-out code, or swallowed errors
- Public APIs fully typed; unjustified `Any` is forbidden
- Every new dependency requires an ADR in `.genesis/DECISIONS.md`
- No motor call may bypass `SafetyPolicy`

## Decision log

All significant decisions live in `.genesis/DECISIONS.md`. Read it before
structural changes and cite immutable ADR IDs.

## Updating progress

Append `YYYY-MM-DD HH:MM | ADR-refs | summary` to `.genesis/PROGRESS.md` after
every meaningful action.

## When blocked

Make reversible progress inside an existing ADR. For an architectural choice,
draft an ADR and ask the user; never guess around physical safety.

---

## Architecture summary

The code is a hexagonal modular monolith. Pure parsing and safety rules emit a
`RobotAction`; external adapters implement microphone, TTS, and robot ports.
Neither STT nor a future LLM can call motors directly. See
`docs/ARCHITECTURE.md`.

## Quality standards summary

Strict typing, short functions/modules, structured errors and JSON logging are
mandatory. Quality exceptions require an ADR. See
`docs/QUALITY_STANDARDS.md`.

## Testing approach

Use unit tests for parsing and safety, integration tests with fake ports for a
full turn, and a manual ground-level smoke test for the physical robot. Tests
are authored before implementation.

## Critical paths

- Turkish text to `RobotAction`
- Movement limits and `STOP` priority
- No movement for ambiguous input
- Cozmo WAV format validation

These require 100% branch coverage and explicit failure tests.

## What this project deliberately does not do

- MVP LLM chat, wake-word, camera, face recognition, or persistent memory
- Unsupervised autonomous movement
- Mobile-app, multi-robot, or server deployment

## Tooling

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev,voice,robot]'
.venv/bin/python -m pytest --cov=cozmo_tr --cov-branch --cov-fail-under=85
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy --strict src
.venv/bin/cozmo-tr doctor
```

## Conventions

- Commits: `feat(scope): subject`, `fix(scope): subject`, etc.
- Branches: `type/short-kebab-description`
- ADR and progress files are append-only.

## See also

- `.genesis/CONSTITUTION.md` — immutable principles
- `docs/CHARTER.md` — mission
- `docs/ARCHITECTURE.md` — technical design
- `docs/QUALITY_STANDARDS.md` — full rules
- `.genesis/DECISIONS.md` — decisions
- `.genesis/RISKS.md` — risks
- `.genesis/PROGRESS.md` — journal
- `CLAUDE.md` — Claude addendum
