# Changelog

Semantic versioning. A breaking change to the **behavioral contract** - the loop,
the non-negotiables, the taxonomy homes - is a major version, because target
repositories depend on it the way they depend on an API.

## [1.0.0] - 2026-08-26

First release.

### The contract

- The **creed** and the twelve-station **loop**, carried in the master
  `akinator` skill: ASK, RESOLVE, AUDIT, PLAN, IMPLEMENT, DOCUMENT, SKILLIFY,
  RULE, CONTEXTIFY, MEMOIZE, INDEX+SYNC, VERIFY.
- Stations 6-11 are not deferrable, and the knowledge delta is declared **by
  path** at plan time - the structural choice that makes skipped documentation
  visible instead of silent.
- The knowledge **taxonomy**: one canonical home per kind of knowledge, one home
  per fact, every artifact reachable from an index, generated beats written, and
  every doc states what would make it stale.

### Components

- **20 skills.** The loop's stations (`akinator-intake`, `-audit`, `-plan`,
  `-document-change`, `-skillify`, `-rule-forge`, `-contextify`, `-memoize`,
  `-adr`, `-index-sync`, `-router-sync`); business, product and operational
  mapping (`-business-map`, `-product-map`, `-ops-map`); discipline
  (`-gate-economy`, `-resource-guard`, `-anti-gaming`); installation and audit
  (`-onboard`, `-coverage`).
- **7 boardroom agents** with real vetoes. `akinator-librarian` runs on every
  batch and blocks completion until stations 6-11 are satisfied.
- **1 command**, `/akinator`, dispatching `onboard`, `audit`, `status`, `sync`,
  `question`, `decide`, and free-text work.
- **1 SessionStart hook** injecting the behavioral contract and reporting which
  knowledge entry points the current repo actually has.
- **10 templates**, each with a filled example written against one coherent
  fictional product so they cross-reference the way real artifacts do.

### Tooling

- `scripts/akinator_coverage.py` - ten mechanically verifiable invariants:
  reachability, dead links, rule enforcement, router sync, module routers,
  generated artifacts, doc truth, skill format, staleness, and git hooks.
  Exit-code driven, JSON output, `.akinatorignore` support. **Never for a git
  hook**, and it says so in its own docstring.
- `scripts/build_codex_pack.py` - deterministic generation of `.agents/skills/`
  and `AGENTS.md` from the canonical Claude skills, with a drift check.
- `scripts/extract_components.py` - generates `context/components.md` from the
  tree; fails if a skill has no declared loop station.
- `scripts/install-codex.sh` and `install-codex.ps1`.

### Verification

- 109 structural and enforcement tests. Every rule's named mechanism is asserted
  to actually work, so a rule cannot silently become decoration.
- Six behavioral eval suites and three fixture repositories: bare, brownfield
  with its own conventions, and one with deliberate rot.
- CI runs the tests, both drift checks, the coverage invariants against
  Akinator's own repository, and a guard that the rotten fixture still fails.

### Platform contracts

Verified 2026-08-26 against Claude Code 2.1.154 and the Codex skills and plugin
manifest specs. See `docs/compatibility.md`.

### Deviations from the build brief

Recorded in full in `docs/deviations.md`. The notable ones:

- **One command instead of six**, at the owner's instruction
  (`docs/adr/0005-single-command-surface.md`).
- **The Codex pack ships real Codex skills**, not loose prompt files - Codex has
  a first-class skills system reading `.agents/skills/`.
- **No Codex hook surface**: Codex plugin validation rejects a `hooks` field, so
  the contract reaches Codex through the generated `AGENTS.md`.
- **Gate receipts are specified, not shipped** - hook stacks differ too much
  between repositories for one implementation to be correct. Recorded as debt
  with a payoff condition.
