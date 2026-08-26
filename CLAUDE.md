# Akinator

The knowledge-layer operating system for AI-maintained codebases, shipped as a
Claude Code plugin and a Codex pack. Installed into a repository, it makes it
structurally impossible to change code without growing the knowledge around it.

**This repo is maintained under its own discipline.** Every change here carries
its own docs, skills, rules, context and memory delta. If this is not the
best-documented repo you have seen, the plugin has failed its first test.

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

The full creed, loop and taxonomy live in `skills/akinator/SKILL.md`. Read that
before working here; this file is an index, not a contract.

## Running this repo

| Task | Command |
|---|---|
| Test | `python -m pytest tests/ -q` |
| Coverage check | `python scripts/akinator_coverage.py .` |
| Coverage check (strict) | `python scripts/akinator_coverage.py . --strict` - the tier CI uses |
| Regenerate the Codex pack | `python scripts/build_codex_pack.py --write` |
| Check the pack for drift | `python scripts/build_codex_pack.py --check` |
| Install to Codex | `sh scripts/install-codex.sh --user` |

Gate once, at the end of the batch, scoped to what you touched. The whole suite
here runs in under two seconds, so "scoped" mostly means: do not run it after
every edit. See `rules/06-gate-once-scoped-at-the-end.md`.

## Layout

| Directory | Holds | Generated? |
|---|---|---|
| `skills/` | The 21 canonical skills - the loop's stations | no, canonical |
| `agents/` | The 7 boardroom review lenses | no |
| `commands/` | The single `/akinator` command | no |
| `hooks/` | SessionStart contract injection | no |
| `templates/` | What Akinator writes into target repos, with filled examples | no |
| `scripts/` | Coverage checker, Codex pack generator, installers | no |
| `evals/` | Behavioral eval suites and fixture repos | no |
| `tests/` | Structural and enforcement tests | no |
| `.agents/skills/` | The Codex pack | **yes** - `scripts/build_codex_pack.py` |
| `AGENTS.md` | The Codex router | **yes** - `scripts/build_codex_pack.py` |

## Changing a skill

Skills in `skills/` are canonical. A change to one must regenerate the Codex
pack **in the same batch**, or CI fails on drift:

```bash
python scripts/build_codex_pack.py --write
```
