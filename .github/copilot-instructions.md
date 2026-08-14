# Copilot Instructions for Cozmo TR

When suggesting code in this repository:

- Follow TDD; implementation follows a failing test.
- Keep functions ≤30 lines, Python files ≤200 lines, complexity ≤8.
- Public APIs are fully typed; do not use unjustified `Any`.
- Do not use magic numbers; name every safety constant.
- Do not swallow errors or use bare `except`.
- Never bypass `SafetyPolicy` for a robot action.
- Use conventional commit messages.

For architectural changes, draft an ADR in `.genesis/DECISIONS.md` before code
and reference existing ADRs by ID. Update `.genesis/PROGRESS.md` after meaningful
work.

## See also

- `AGENTS.md` — full agent contract
- `docs/ARCHITECTURE.md` — module boundaries
- `docs/QUALITY_STANDARDS.md` — enforced rules
