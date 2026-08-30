# Rule 09 - Every router is rendered from one contract

## Purpose

Every AI tool reads a different entry file. This repository ships eleven of them
- Claude, Codex, Gemini, GLM, Kimi, Qwen, DeepSeek, Mistral, Cursor, Copilot and
the common `AGENTS.md` fallback.

Maintained by hand, that is **eleven times the fork surface**. One router
updated alone becomes a separate version of the truth, and an agent reading the
stale one acts confidently and wrongly - the most expensive failure available,
because confidence suppresses checking.

Akinator shipped a small instance of exactly this: `CLAUDE.md` carried a
"Coverage check (strict)" row that `AGENTS.md` and `CODEX.md` did not, so a
Codex agent following its own router ran the tier the architecture doc had just
declared insufficient, reported green, and CI blocked. Three routers, one fact,
one fork. Eleven routers make that inevitable rather than possible.

They are only safe because they are generated.

## Applies to

- **In scope:** every file listed in `ADAPTERS` in `scripts/render_routers.py`,
  and `context/router-contract.md` as their single source.
- **Out of scope:** `.agents/AGENTS.md`, the **portable** contract the installer
  copies into other repositories. It is generated too, by
  `scripts/build_codex_pack.py`, and governed by
  `rules/07-codex-pack-is-generated.md` - deliberately a different document,
  because it must name no repo-relative paths. Also out of scope: a target
  repository's own routers, which Akinator syncs but does not own.

## Mandatory rules

1. Router files are written only by `scripts/render_routers.py`.
2. Facts shared by all routers live in `context/router-contract.md` and nowhere
   else.
3. Per-tool content lives in that tool's adapter in the renderer, and is emitted
   under an `<!-- akinator:tool-specific -->` marker.
4. Rendering is **deterministic**: the same contract produces byte-identical
   output. No clock, no absolute paths, no unordered iteration.
5. A change to the contract re-renders every router in the **same batch**.
6. Adding a new AI tool means adding an adapter, never a hand-written file.

## Prohibited patterns

```bash
# WRONG - editing a rendered router
vim CLAUDE.md
```

The next render silently discards the edit, and until then that one tool reads
something the others do not.

```markdown
<!-- WRONG - a fact stated in one adapter's tool-specific block -->
<!-- akinator:tool-specific -->
## Claude Code
- Schema changes need a container rebuild, not a restart.
```

That is a fact about the repository, not about Claude Code. Marking it
tool-specific exempts it from the sync check and hides the fork from the very
mechanism built to catch it. The marker is for **where a tool reads its skills
from**, not for anything true of the system.

## Correct pattern

```bash
# RIGHT - edit the contract, re-render everything, in one batch
vim context/router-contract.md
python scripts/render_routers.py --write
```

```python
# RIGHT - a new tool is an adapter, not a file
Adapter("NEWTOOL.md", "New Tool", GENERIC_SPECIFICS),
```

## Enforcement

- Mechanism: `scripts/render_routers.py` - `--check` re-renders every router in
  memory and diffs against the tree, exiting non-zero on any difference. This
  catches a hand-edit and a stale render identically, because both produce the
  same symptom.
- Mechanism: `tests/test_routers.py` - asserts the rendered set is not drifted,
  that rendering is deterministic, that every adapter carries the shared
  sections, and that no tool-specific block contains a repository fact.
- Mechanism: `.github/workflows/ci.yml` runs the drift check on every push.
- Type: script check in CI, plus unit tests.
- How it fails: the check names each drifted router and the command that fixes
  it.
- Last observed passing: 2026-08-26

**Never a git hook** - see `rules/05-no-git-hook-complication.md`.

## Exceptions

None for the eleven rendered routers.

If a tool needs content the contract cannot express, it goes into that tool's
**adapter** as a documented transformation - not into the output file. An
adapter is reviewable as a diff and reproducible; a hand-edit is neither.

## Related

- Rules: `rules/04-routers-stay-thin-and-synced.md` - the sync law this
  mechanizes
- Rules: `rules/07-codex-pack-is-generated.md` - the same pattern, applied to
  the skills pack
- Context: `context/router-contract.md` - the source
- Docs: `docs/akinator-v2-design.md` - stage 4, PROJECT
- Memory: `memory/2026-08-26-fix-the-index-not-only-its-pointers.md` - the
  router fact fork that motivated this

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] The enforcement mechanism exists in the tree and is named by path.
- [x] The mechanism is not a git hook.
- [x] Prohibited and correct patterns are shown.
- [x] The absence of an exception path is deliberate, with the alternative named.
- [x] The rule is indexed and reflected in every router.
