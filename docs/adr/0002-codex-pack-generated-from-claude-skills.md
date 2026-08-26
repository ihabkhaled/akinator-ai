# ADR 0002 - The Codex pack is generated from the Claude skills

- **Status:** accepted
- **Date:** 2026-08-26
- **Deciders:** Ihab Khaled (owner)

## Context

Akinator ships the same behavioral contract to two platforms with different
extension systems:

- **Claude Code** reads `skills/<name>/SKILL.md` from a plugin whose manifest is
  `.claude-plugin/plugin.json`, plus `commands/`, `agents/` and `hooks/`.
- **Codex** reads skills from `.agents/skills/` (repository scope, walking up to
  the repository root, then `$HOME/.agents/skills`), takes its root context from
  `AGENTS.md`, and has a plugin manifest at `.codex-plugin/plugin.json` whose
  validation **rejects** unsupported fields such as `hooks`.

The formats turned out to be nearly identical - both are `SKILL.md` with `name`
and `description` frontmatter - which was not a given when the build started.

The forcing question: two platforms, one contract, and Akinator's entire premise
is that forked truth is how repositories rot. Shipping a plugin that itself
maintains two divergent copies of its own behavioral contract would be
disqualifying.

## Options considered

### Option A - Maintain both by hand

- **What it is:** author `skills/` and `.agents/skills/` independently.
- **Cost:** every skill edit must be made twice, forever, with nothing detecting
  a missed one.
- **Why it lost:** it is precisely the failure the plugin exists to prevent, and
  the divergence would be *invisible* - a Claude user and a Codex user would each
  believe they were running the same plugin while getting different instructions.
  Failing our own `router-sync` invariant inside our own repository is not a
  defensible ship.

### Option B - A shared directory, symlinked

- **What it is:** make `.agents/skills` a symlink to `skills/`. Codex documents
  that symlinked folders are supported.
- **Cost:** symlinks do not survive a plain `git clone` on Windows without
  developer mode or `core.symlinks=true`, and the primary development machine
  for this project is Windows. It also forbids any per-platform transformation
  forever, since the bytes are literally the same file.
- **Why it lost:** the portability failure is silent - the pack simply appears
  empty on an affected checkout - and the zero-transformation constraint is too
  rigid to bet on when the two platform contracts are separately versioned.

### Option C - Generate the pack from the canonical skills (chosen)

- **What it is:** `skills/` is canonical; `scripts/build_codex_pack.py` projects
  it into `.agents/skills/` and generates `AGENTS.md`. `--check` regenerates in
  memory and diffs, so drift is detectable; CI runs it.
- **Cost:** one script to maintain, a regeneration step in any batch that touches
  a skill, and a hard determinism requirement - a generator that emitted a
  timestamp would make every run a diff, the drift check would become noise, and
  it would be disabled.
- **Why it won:** it makes divergence *mechanically impossible to ship* rather
  than merely discouraged, it survives Windows checkouts, and it leaves a place
  to express genuine per-platform differences as reviewable transformations
  rather than as hand-edits.

## Decision

`skills/` is canonical. `.agents/skills/**` and `AGENTS.md` are build outputs of
`scripts/build_codex_pack.py`, carry a generated-file banner, and are never
hand-edited. Generation is deterministic. CI fails on drift.

Per-platform differences, if any are ever needed, go into the **generator** as a
documented transformation - never into the output.

## Consequences

**Good**
- The two platforms cannot ship different behavioral contracts.
- A stale pack and a hand-edit produce the same detectable symptom, so one check
  catches both.
- `AGENTS.md` gets the same knowledge links as the other routers by construction,
  which is what keeps `router-sync` green.

**Bad**
- A skill edit is not complete until the pack is regenerated. This is a real
  step that a contributor will forget, which is why CI fails on it rather than
  relying on discipline.
- The generator is a second place to look when the Codex output is wrong.

**Debt taken on**
- `CLAUDE_ONLY` in the generator is currently empty. If a Claude-only skill is
  ever added, the exclusion path exists but has never been exercised - the first
  use should add a test.

## Revisit when

- Codex's skills contract diverges from Claude's beyond a banner - for example,
  if it requires different frontmatter keys, at which point the transformation
  stops being cosmetic and deserves its own design.
- Codex gains a plugin surface that can consume `skills/` directly, making the
  projection unnecessary.
- A platform ships a first-party sync mechanism.

## Related

- Rules: `rules/07-codex-pack-is-generated.md`
- Docs: `docs/compatibility.md`
- Code: `scripts/build_codex_pack.py`, `tests/test_codex_pack.py`
