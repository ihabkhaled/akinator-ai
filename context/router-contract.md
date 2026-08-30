# Router contract

The single canonical source for every AI entry-point file. Eleven routers are
rendered from this one document by `scripts/render_routers.py`.

## Scope

- **Covers:** the facts every AI router in this repository states - what the repo
  is, where the knowledge lives, the constraints to see before any work, how to
  run it, and the layout.
- **Does not cover:** tool-specific content - where a given tool reads skills
  from, or how it invokes them. That lives in the adapters, in the renderer, and
  is emitted under an `akinator:tool-specific` marker so the coverage check can
  tell an intentional difference from rot.

## Why this file exists

Eleven hand-maintained routers would be eleven times the fork surface. One
router updated alone becomes a separate version of the truth, and an agent
reading the stale one acts confidently and wrongly.

They are only safe because they are generated. This is
`rules/07-codex-pack-is-generated.md` applied at scale, and
`rules/04-routers-stay-thin-and-synced.md` made mechanical rather than
remembered.

**Edit this file, then regenerate.** Never edit a router directly.

## Identity

Akinator - the knowledge-layer operating system for AI-maintained codebases,
shipped as a Claude Code plugin and a Codex pack. Installed into a repository,
it makes it structurally impossible to change code without growing the knowledge
around it.

**This repo is maintained under its own discipline.** Every change here carries
its own docs, skills, rules, context and memory delta.

## Start here

- Rules (constraints you must not break): `rules/README.md`
- Skills (the loop's stations): `docs/skills.md`
- Agents (the boardroom lenses): `docs/agents.md`
- Context (structural facts): `context/README.md`
- Docs (architecture, decisions, compatibility): `docs/README.md`
- Memory (durable decisions and surprises): `memory/index.md`
- The brief (what a new session reads first): `.ai/BRIEF.md`
- The ledger (what happened, and what recurs): `docs/ledger.md`
- Templates (what Akinator ships to target repos): `templates/README.md`

## Before you change anything

- **Every batch declares a knowledge delta by path** - `rules/01-knowledge-delta-per-batch.md`
- **Never add knowledge checks to git hooks** - `rules/05-no-git-hook-complication.md`
- **The Codex pack and every router are generated** - `rules/07-codex-pack-is-generated.md`
- **Routers are rendered from this contract** - `rules/09-routers-are-rendered-from-one-contract.md`
- **Ledger records are redacted before write** - `rules/10-ledger-records-are-redacted-before-write.md`
- **Every invariant ships with a test that proves it fires** - `rules/11-invariants-ship-with-a-mutation-test.md`
- **Anything installed elsewhere names no local file** - `rules/12-artifacts-that-travel-name-nothing-local.md`

The full creed, loop and taxonomy live in `skills/akinator/SKILL.md`.

## Running this repo

| Task | Command |
|---|---|
| Test | `python -m pytest tests/ -q` |
| Coverage check | `python scripts/akinator_coverage.py .` |
| Coverage check (strict) | `python scripts/akinator_coverage.py . --strict` - the tier CI uses |
| Regenerate the Codex pack | `python scripts/build_codex_pack.py --write` |
| Regenerate every router | `python scripts/render_routers.py --write` |
| Regenerate the context brief | `python scripts/build_brief.py --write` |
| Verify the ledger | `python scripts/akinator_ledger.py verify` |
| Scope a pass to the change | `python scripts/akinator_scope.py plan` |
| What recurs and needs a decision | `python scripts/akinator_distil.py detect` |
| Regenerate the component map | `python scripts/extract_components.py --write` |
| Regenerate the stack map | `python scripts/extract_stack.py --write` |
| Regenerate the brand assets | `python scripts/generate_assets.py --write` |
| Install to Codex | `sh scripts/install-codex.sh --user` |

Gate once, at the end of the batch, scoped to what you touched. See
`rules/06-gate-once-scoped-at-the-end.md`.

## Layout

| Directory | Holds | Generated? |
|---|---|---|
| `skills/` | The canonical skills - the loop's stations | no, canonical |
| `agents/` | The boardroom review lenses | no |
| `commands/` | The single `/akinator` command | no |
| `hooks/` | SessionStart contract injection | no |
| `templates/` | What Akinator writes into target repos, with filled examples | no |
| `scripts/` | Coverage checker, generators, installers | no |
| `evals/` | Behavioral eval suites and fixture repos | no |
| `tests/` | Structural and enforcement tests | no |
| `context/router-contract.md` | This file - the canonical router source | no, canonical |
| `.agents/skills/` | The Codex pack | **yes** - `scripts/build_codex_pack.py` |
| Every router file | CLAUDE, AGENTS, CODEX, GEMINI and the rest | **yes** - `scripts/render_routers.py` |

## Regenerate when

- Extractor: `scripts/render_routers.py`
- Regenerate with: `python scripts/render_routers.py --write`
- Drift check: `python scripts/render_routers.py --check` in CI - re-renders in
  memory and diffs every router; exits non-zero if any differs.
- Regenerate when: any section above changes, a rule is added that belongs in
  "Before you change anything", or a new AI tool needs a router.

## Related

- Rules: `rules/09-routers-are-rendered-from-one-contract.md`
- Rules: `rules/04-routers-stay-thin-and-synced.md`
- Docs: `docs/akinator-v2-design.md` - stage 4, PROJECT
