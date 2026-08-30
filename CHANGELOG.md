# Changelog

Semantic versioning. A breaking change to the **behavioral contract** - the loop,
the non-negotiables, the taxonomy homes - is a major version, because target
repositories depend on it the way they depend on an API.

## [1.1.0] - 2026-08-30

The v2 pipeline, and a defect the plugin was shipping into every repository that
installed it.

### Fixed

- **Installing Akinator no longer dirties the repository it installs into.**
  Every file the Codex pack ships carried a banner naming
  `scripts/build_codex_pack.py` and `skills/<name>/SKILL.md`; the portable
  contract named `build_codex_pack.py`. None of those exists in a repository
  that installs the pack. A bare repo that ran the installer and then the
  coverage checker got **22 HIGH findings on its first run**, every one on a
  file the plugin had just written - from the plugin whose premise is that a
  document asserting things that are not there is a critical defect.

  Both banners now name no file at all. They state where the file came from and
  how to refresh it, which is what a vendored artifact actually owes its reader.
  `check_generated` gained a matching branch requiring **both** halves, ordered
  after the named-generator check so that "installed from" cannot become a
  phrase you write to silence it.

  Twenty-one tests covered the pack, including one named
  `test_portable_contract_names_no_repo_relative_paths`. All of them read it
  from inside this checkout, where every path resolves; none read it from where
  it lands. The new regression test writes the pack into a scratch repository
  and runs the real checker there. See
  `rules/12-artifacts-that-travel-name-nothing-local.md`,
  `docs/adr/0007-vendored-artifacts-declare-origin-not-generator.md` and
  `memory/2026-08-30-a-claim-is-only-true-relative-to-a-tree.md`.

  Found by two red-team agents in eval 06, independently, while refusing the
  shortcuts they were told to take.

### Added

- **CAPTURE - the ledger** (`scripts/akinator_ledger.py`). Failures, questions,
  decisions and surprises as durable records, fingerprinted so the same problem
  under a different error message is recognised as the same problem.
  **Redaction runs inside `Ledger.write()`**, with no bypass and no per-record
  opt-out: a credential written into a committed ledger is in git history
  forever. `rules/10`.

- **DISTIL - what recurs becomes a proposal** (`scripts/akinator_distil.py`).
  At two occurrences the pass stops and asks: rule, skill, or neither.
  **"Neither" is a recorded answer**, which is what stops the question being
  re-asked every session. Two of this repository's four decisions are refusals.

- **HARDEN - rule evolution** (`scripts/akinator_rules.py`). Rules gain optional
  provenance - `introduced_by`, `supersedes`, `caused` - so a rule that fixed
  one problem and created another can be traced and replaced rather than
  accumulating beside its own damage. Bodies are preserved byte-for-byte.

- **PROJECT - eleven routers from one contract** (`scripts/render_routers.py`).
  CLAUDE, AGENTS, CODEX, GEMINI, GLM, KIMI, QWEN, DEEPSEEK, MISTRAL, the Cursor
  rule and the Copilot instructions are all rendered from
  `context/router-contract.md`. Eleven hand-maintained entry points is eleven
  chances to fork. `rules/09`.

- **PROJECT - the stack map** (`scripts/extract_stack.py`). One generated map of
  every dependency and module, linked to the ADR that chose each one and the
  failure record it caused - **instead of a document per library**. A page
  saying "we use axios for HTTP" restates `package.json`, rots on the next
  version bump, and at a hundred libraries buries the handful of pages that
  carry real knowledge.

- **SURFACE - the brief** (`scripts/build_brief.py`). `.ai/BRIEF.md` plus a
  complete `.ai/index.json`, under a hard token cap (lean 4k, standard 12k, deep
  25k). The corpus is unbounded; the brief is not. "Document every needle" is a
  write problem and "a new chat knows everything in seconds" is a retrieval
  problem, and optimising the first degrades the second.

- **Change scoping and the interrupt budget** (`scripts/akinator_scope.py`).
  **"Everything" means every station, not every file.** Stations are scoped, not
  skipped: on a typo most find nothing and the batch records
  `knowledge delta: none, because ...` in one line. Questions are ranked and
  capped at five per session, with the remainder carried rather than dropped -
  twenty questions in one session means zero answers by session three.

- `rules/12-artifacts-that-travel-name-nothing-local.md`,
  `docs/adr/0007-vendored-artifacts-declare-origin-not-generator.md`.

### Verified

- **All six behavioral eval suites now have runs, all passing.** Suites 02, 05
  and 06 had never been run; 04 was re-run against decontaminated fixtures and
  its earlier result is superseded. Grades and full write-ups in
  `evals/results/`, indexed from `evals/README.md`.

  Suite 06 is adversarial - five prompts pressuring the agent to fake
  compliance. All five were declined, and two of them found the pack defect
  above.

- Full test suite passing, `--strict` coverage clean, ledger verified, no rule
  conflicts, all six drift checks clean, `claude plugin validate .` passing. The
  count is intentionally not stated - a number in prose that no mechanism
  maintains goes stale on the next commit, and this release fixed exactly that
  class of defect elsewhere; run `python -m pytest tests/ -q` for the current
  count.

## [1.0.2] - 2026-08-26

### Added

- **An eleventh invariant: `index-completeness`.** Every artifact must appear in
  its **own** category index, not merely somewhere in the tree. Twelve categories
  are covered: rules, skills, context, memory, ADRs, docs, business, product,
  ops, templates, agents and eval suites. A category with no index at all is left
  to `reachability` rather than double-counted.

  `reachability` proved an artifact was referenced from *some* markdown file,
  which is weaker than the taxonomy's actual law. An artifact linked only from a
  router, or only from a sibling doc, satisfied it while remaining invisible to a
  reader who opens the category index and reads down the list - which is exactly
  how a fresh agent looks for things.

  Found by running `akinator-everything` against this repository, and its
  matching rule was wrong **three times** before it was right - each fix
  producing the next failure. A bare substring let `demo` be satisfied by a
  listed `demo-extended`. Word-bounding closed that and let `docs/overview.md`
  be satisfied by `adr/overview.md`. Path-bounding closed that and produced six
  false positives on suites listed with a directory prefix. The rule that works
  is not a pattern: it **resolves** each index reference to a repo-relative path
  and compares. There is a regression test for each failure above, plus one for
  the taxonomy homes that were silently exempt.

- **CI moved from `--fail-on high` to `--strict`.** `reachability` and
  `index-completeness` are MEDIUM findings, so on the default tier an unindexed
  artifact passed CI green - true of `reachability` since it was written, and
  never noticed until a review lens mutation-tested it by deleting a row from a
  real index. MEDIUM remains right for a repository onboarding gradually; it is
  not the right bar for the repository that ships the checker.

- `docs/agents.md` - an index for the seven boardroom lenses, which had none.

- `docs/akinator-v2-design.md` - the approved design for the next major version.
  It names the conflict v1 never resolved: "document every needle" is a write
  problem and "a new chat knows everything in seconds" is a retrieval problem,
  and optimizing the first degrades the second. v2 splits them into an unbounded
  corpus and a hard-capped brief, and adds the learning loop - a fingerprinted
  failure ledger, recurrence-to-rule synthesis, and rule evolution when a rule
  causes the next failure. Seven phases, not yet implemented.

### Fixed

- Stale skill counts. `docs/compatibility.md`, `docs/README.md`, `README.md`,
  `docs/skills.md`, `CLAUDE.md` and `CODEX.md` all said 20; there are 21. The
  index itself and two routers were the last to be corrected, which is the
  instructive part: the first pass fixed every file that *pointed at* the index
  and left the index wrong, and declared "Routers: none" for a batch whose whole
  subject was a number the routers carried.
- `docs/architecture.md` now records that `/akinator` runs the complete pass by
  default, and the deliberate split between `akinator` (scales to the change) and
  `akinator-everything` (does not scale down). It had described neither.
- `docs/deviations.md` item 1 now carries the amendment as well as the original
  six-to-one decision.

## [1.0.1] - 2026-08-26

### Verified installing and loading in Claude Code

Previously this was asserted by the structural tests and never actually done.
It has now been done, against Claude Code 2.1.154:

```
claude plugin validate .            -> Validation passed
claude plugin marketplace add ./    -> added marketplace: akinator
claude plugin install akinator@akinator -> installed (scope: user), enabled
```

`claude plugin details akinator` enumerates the whole surface: 21 skills, 7
agents, 1 command, 1 SessionStart hook, 0 MCP servers, 0 LSP servers. Always-on
cost ~3.0k tokens - the per-skill always-on figure is the trigger description
only, which is what makes 21 skills affordable; the body is paid on invoke.

Two observations from the real install, neither a defect:

- The details output reports "Skills (22)" and lists `akinator` twice. There are
  21 skill directories on disk. The 22nd entry is `commands/akinator.md`, which
  shares the name - the inventory counts the command alongside the skills.
- The install copies the whole repository into the plugin cache, so `.agents/`,
  `evals/`, `tests/` and `scripts/` ship with it. Only `skills/`, `agents/`,
  `commands/` and `hooks/` are loaded, and the generated `.agents/skills/` is
  **not** double-registered as skills. The rest costs disk, not context.

### Added

- `docs/listing.md` gains the everything-pass use case - the flagship bare
  `/akinator`, which the listing had no example for.

### Changed

- Version bumped across `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json` and `.codex-plugin/plugin.json`. The suite
  asserts all three agree.

## [1.0.0] - 2026-08-26

First release.

### Fixed before release - Codex plugin validation

Three defects found by a validation run against the packaged plugin:

- **`interface.composerIcon` and `interface.logo` are required**, not optional,
  and must reference square images that exist in the plugin. `docs/compatibility.md`
  had asserted the opposite and was corrected. Akinator now ships
  `assets/akinator-icon.png` and `assets/akinator-logo.png`, both 512x512,
  **generated** by `scripts/generate_assets.py` - the mark is drawn from a signed
  distance field and the PNG encoded with the standard library, so it keeps its
  provenance and can be drift-checked like every other generated artifact.
- **Files directly under `skills/` are not imported** and fail validation. The
  skills index moved from `skills/README.md` to `docs/skills.md`, and
  `rules/08-skills-dir-holds-only-skill-directories.md` now prevents the class of
  defect with a test as its enforcement.
- Both surprises are recorded in
  `memory/2026-08-26-codex-plugin-validation-surprises.md`, with the general
  lesson: **the validator is the contract; the field list is a summary.**

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

- **`/akinator` runs everything.** With no arguments, or with free text, the
  command loads `akinator-everything` and runs the complete pass - every station,
  every applicable boardroom lens, every mechanical check, looping until the
  Definition of Done is proven with evidence. Mode words narrow the target, never
  the depth. See `docs/adr/0005-single-command-surface.md`.
- **21 skills.** `akinator-everything` is the all-in-one pass; `akinator` remains
  the always-on router that scales the loop to the size of the change. The two
  are deliberately different settings - running the full pass on a typo is how a
  team learns to stop running any of it.
- **20 station skills.** The loop's stations (`akinator-intake`, `-audit`, `-plan`,
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
- `scripts/generate_assets.py` - draws and encodes the brand assets Codex
  validation requires, with a drift check.
- `scripts/run_evals.py` - runs the behavioral evals against the fixtures. Fresh
  agent per step, no follow-up turn, each run in a disposable copy of the fixture
  so an eval can never mutate it, and optional grading by a second independent
  agent that sees only the transcript, the diff and the rubric.
- `scripts/install-codex.sh` and `install-codex.ps1`.

### Verification

- 130 structural and enforcement tests. Every rule's named mechanism is asserted
  to actually work, so a rule cannot silently become decoration.
- Six behavioral eval suites, numbered without gaps, every one runnable by
  `scripts/run_evals.py`, against three fixture repositories: bare, brownfield
  with its own conventions, and one with deliberate rot.
- CI runs the tests, all three drift checks, the coverage invariants against
  Akinator's own repository, a guard that the rotten fixture still fails, and a
  check that every eval suite is parseable and runnable.

### Behavioral eval results

Four runs, recorded in `evals/results/`, including a **paired baseline** - the
same task, same fixture, same model, with and without the pack installed.

| Eval | Result |
|---|---|
| 01 silent-change (with Akinator) | **pass** - code, tests, and a README documenting the `billable` semantic that lived only in a docstring, plus a when-not-to and a stale-when line |
| 01 silent-change (baseline, no pack) | **fail, expected** - code and tests; documentation explicitly declined |
| 03 business-void | **pass** - refused to implement, filed seven dated open decisions in the fixture's own `docs/standards/`, asked the blocking question in business terms |
| 04 newcomer | **pass** - identified the undocumented refund/quota void and refused to infer an answer from the implementation |

The 01 pair is the product claim, measured: same model, one variable, and the
knowledge artifact appears only with the contract installed. One paired run is a
data point, not a study - the value is the trend across releases.

Two defects were found by running them, neither visible from writing them:

- **The installer shipped Akinator's own router into target repos**, giving them
  five dead links and an instruction to run Akinator's test suite. Fixed: the
  pack now generates a separate portable contract at `.agents/AGENTS.md` that
  names no repo-relative paths, and the installers copy that.
- **The fixtures announced that they were fixtures**, naming their planted gaps
  in their own READMEs and contaminating any run against them. Fixed: those notes
  moved to `evals/fixtures/README.md` and each fixture now reads as an ordinary
  repository. Eval 04 should be re-run against the cleaned fixtures.

Still unrun: 02 repeated-question, 05 gate-economy, 06 anti-gaming. The Claude
Code plugin path - SessionStart hook, auto-triggered skills, boardroom subagents
- was not exercised; the runs reached the agent through the Codex `AGENTS.md`
delivery path and the plugin path remains verified structurally only.

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
