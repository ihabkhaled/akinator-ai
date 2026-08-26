# Akinator

The knowledge-layer operating system for AI-maintained codebases, shipped as a
Claude Code plugin and a Codex pack. Installed into a repository, it makes it
structurally impossible to change code without growing the knowledge around it.

**This repo is maintained under its own discipline.** Every change here carries
its own docs, skills, rules, context and memory delta.

## Start here

- Rules (constraints you must not break): `rules/README.md`
- Skills (the loop's stations): `docs/skills.md`
- Context (structural facts): `context/README.md`
- Docs (architecture, decisions, compatibility): `docs/README.md`
- Memory (durable decisions and surprises): `memory/index.md`
- Templates (what Akinator ships to target repos): `templates/README.md`

## Before you change anything

- **Every batch declares a knowledge delta by path** - `rules/01-knowledge-delta-per-batch.md`
- **Never add knowledge checks to git hooks** - `rules/05-no-git-hook-complication.md`
- **The Codex pack is generated, never hand-edited** - `rules/07-codex-pack-is-generated.md`

The full creed, loop and taxonomy live in `skills/akinator/SKILL.md`.

## Running this repo

| Task | Command |
|---|---|
| Test | `python -m pytest tests/ -q` |
| Coverage check | `python scripts/akinator_coverage.py .` |
| Regenerate the Codex pack | `python scripts/build_codex_pack.py --write` |
| Check the pack for drift | `python scripts/build_codex_pack.py --check` |
| Install to Codex | `sh scripts/install-codex.sh --user` |

Gate once, at the end of the batch, scoped to what you touched. See
`rules/06-gate-once-scoped-at-the-end.md`.

## Layout

| Directory | Holds | Generated? |
|---|---|---|
| `skills/` | The 20 canonical skills - the loop's stations | no, canonical |
| `agents/` | The 7 boardroom review lenses | no |
| `commands/` | The single `/akinator` command | no |
| `templates/` | What Akinator writes into target repos, with filled examples | no |
| `scripts/` | Coverage checker, Codex pack generator, installers | no |
| `evals/` | Behavioral eval suites and fixture repos | no |
| `tests/` | Structural and enforcement tests | no |
| `.agents/skills/` | The Codex pack | **yes** - `scripts/build_codex_pack.py` |
| `AGENTS.md` | The Codex router | **yes** - `scripts/build_codex_pack.py` |

<!-- akinator:tool-specific -->
## Codex specifics

`AGENTS.md` is the file Codex actually reads at the repository root, and it is
generated. This file exists for tools and humans that look for `CODEX.md` by
name; it carries the same facts.

- Skills are read from `.agents/skills/` - repository scope, walking up from the
  working directory to the repository root, then `$HOME/.agents/skills`.
- Invoke a skill explicitly with `$akinator`, or describe the task and let Codex
  select from the skill descriptions.
- Install with `scripts/install-codex.sh` (or `scripts/install-codex.ps1`).
- The Codex plugin manifest is `.codex-plugin/plugin.json`. Codex validation
  rejects unsupported manifest fields such as `hooks`, so the SessionStart hook
  is a Claude-only surface - the same contract reaches Codex through `AGENTS.md`
  instead. See `docs/compatibility.md`.
