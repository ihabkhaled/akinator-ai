# Rules

Constraints that must not be broken in this repository. Each one names an
enforcement mechanism that exists in the tree - see
`rules/03-rules-need-live-enforcement.md`, which is the rule about rules.

Numbered, never renumbered. Written with `templates/rule.md`.

| # | Rule | Enforced by |
|---|---|---|
| 01 | [Every batch declares and delivers a knowledge delta](01-knowledge-delta-per-batch.md) - the plan names its docs, skills, rules, context, memory and ADR paths before any code exists | `agents/akinator-librarian.md`, `scripts/akinator_coverage.py`, `tests/test_plugin_structure.py` |
| 02 | [Every skill carries all six parts](02-skills-carry-all-six-parts.md) - trigger frontmatter, when-to-use, when-NOT-to-use, procedure, failure modes, definition of done | `scripts/akinator_coverage.py` (`skill-format`), `tests/test_plugin_structure.py` |
| 03 | [Every rule names an enforcement mechanism that exists](03-rules-need-live-enforcement.md) - a named-but-absent mechanism reads as enforced and is not | `scripts/akinator_coverage.py` (`rule-enforcement`), `tests/test_coverage_checker.py` |
| 04 | [Routers stay thin, and they never fork](04-routers-stay-thin-and-synced.md) - all AI entry points change together and none reproduces canonical content | `scripts/akinator_coverage.py` (`router-sync`), `tests/test_plugin_structure.py` |
| 05 | [Never put knowledge checks in git hooks](05-no-git-hook-complication.md) - hooks gate code and must stay fast; knowledge enforcement lives in CI, tests and session behavior | `scripts/akinator_coverage.py` (`git-hooks`), `tests/test_coverage_checker.py` |
| 06 | [Gate once, at the end, scoped to what was touched](06-gate-once-scoped-at-the-end.md) - no commits mid-batch, no gate storms, no re-proving a proven tree | `skills/akinator-gate-economy/SKILL.md`, `agents/akinator-pm.md` |
| 07 | [The Codex pack is generated, never hand-edited](07-codex-pack-is-generated.md) - the Claude skills are canonical; two hand-maintained copies diverge invisibly | `scripts/build_codex_pack.py --check`, `tests/test_codex_pack.py` |
| 09 | [Every router is rendered from one contract](09-routers-are-rendered-from-one-contract.md) - eleven AI entry-point files, one source, zero fork surface | `scripts/render_routers.py --check`, `tests/test_routers.py` |
| 08 | [`skills/` holds only skill directories](08-skills-dir-holds-only-skill-directories.md) - a loose file there is not imported and fails Codex validation; the index lives in `docs/` | `tests/test_plugin_structure.py` |

## Adding a rule

Use `skills/akinator-rule-forge/SKILL.md`. The mechanism must exist in the tree
**before** the rule is written, and it must not be a git hook.
