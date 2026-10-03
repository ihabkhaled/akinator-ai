# Standards

<!-- akinator:generated:begin -->
<!-- Facts detected from the tree. This block is rewritten on every run;
     write outside it. Nothing here is guessed: every row names its file. -->

### Languages

| Detected | Where |
|---|---|
| Python (59 files) | `.agents/skills/akinator/scripts/akinator_context.py`, `.agents/skills/akinator/scripts/akinator_coverage.py`, `.agents/skills/akinator/scripts/akinator_distil.py` (+56 more) |
| Shell (3 files) | `hooks/prompt-reminder.sh`, `hooks/session-start.sh`, `install.sh` |
| PowerShell (1 file) | `install.ps1` |

### Linters, formatters and type checkers

Nothing detected.

### Pre-commit and git hooks

Nothing detected.

### Test frameworks

| Detected | Where |
|---|---|
| pytest config | `tests/conftest.py` |

### CI

| Detected | Where |
|---|---|
| GitHub Actions workflows | `.github/workflows/ci.yml` |

### Ownership

Nothing detected.

### Import conventions

Nothing detected.

Regenerate with: `python <skill>/scripts/extract_platform.py --write`
<!-- akinator:generated:end -->

What this answers: languages, code standards, lint, hooks, imports, QA gates.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## Which code standards, lint rules, hooks, import rules and QA gates apply, and which are enforced by a tool?

Curated from reading the tree; the generated block above is the detected fact.

- **Language and dependencies:** Python on the standard library for every tool
  in `skills/everything/scripts/`; `pytest` is the only test dependency. CI runs
  Python 3.13.
- **Tests:** `python -m pytest tests/ -q`; every invariant ships with a test
  that proves it fires (rule 11).
- **QA gates:** `akinator_coverage.py . --strict`, the drift checks listed in
  `.github/workflows/ci.yml`, gated once at the end of a batch (rule 06).
- **Git hooks:** none, by decision (rule 05, ADR 0003).
- **Generated files** (`.agents/`, routers, `context/components.md`,
  `context/stack.md`, `.ai/BRIEF.md`) are never hand-edited (rules 07, 09).
- **Size cap:** `SKILL.md` stays under 8,000 bytes (Codex truncates there).
- **Every batch declares its knowledge delta** (rule 01) and every changed path
  is traced (rule 14).

_Unknown - ask the owner and record the answer._
