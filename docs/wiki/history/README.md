# History

<!-- akinator:generated:begin -->
<!-- Facts read from manifests, CHANGELOG.md, docs/changes, docs/adr and
     .ai/ledger. Rewritten on every run; write outside this block. -->

## Versions

| Manifest | Version |
|---|---|
| `.claude-plugin/plugin.json` | `2.1.0` |
| `.codex-plugin/plugin.json` | `2.1.0` |

## Releases

| Version | Date | Summary |
|---|---|---|
| `2.1.0` | 2026-10-03 | Traced changes, cheap context, sensitive data known and never exposed, and a |
| `2.0.0` | 2026-09-19 | Every prompt documented: the repository becomes its own living wiki. Still one |
| `1.2.0` | 2026-09-18 | One skill, one command, one installer - and the always-on work from PR #1, which |
| `1.1.0` | 2026-08-30 | The v2 pipeline, and a defect the plugin was shipping into every repository that |
| `1.0.2` | 2026-08-26 | **An eleventh invariant: `index-completeness`.** Every artifact must appear in |
| `1.0.1` | 2026-08-26 | Previously this was asserted by the structural tests and never actually done. |
| `1.0.0` | 2026-08-26 | First release. |

## Change records

| Date | Change | Path |
|---|---|---|
| 2026-10-03 | Change - 2.1.0: traced changes, fast context, sensitive data, a 25-category wiki | `docs/changes/2026-10-03-trace-fast-context-sensitive.md` |
| 2026-09-19 | Change - Every prompt documented: the living wiki | `docs/changes/2026-09-19-living-wiki.md` |
| 2026-09-18 | Change - One skill, one command, one installer | `docs/changes/2026-09-18-one-skill-one-installer.md` |
| 2026-09-18 | Change — Always-on one-command Akinator and living wiki | `docs/changes/2026-09-18-always-on-one-command.md` |

## Decisions

| Decision | Status | Path |
|---|---|---|
| ADR 0001 - MIT license | accepted | `docs/adr/0001-mit-license.md` |
| ADR 0002 - The Codex pack is generated from the Claude skills | accepted | `docs/adr/0002-codex-pack-generated-from-claude-skills.md` |
| ADR 0003 - Knowledge enforcement lives outside git hooks | accepted | `docs/adr/0003-enforcement-outside-git-hooks.md` |
| ADR 0004 - Tree-bound gate receipts, not hook bypass | accepted | `docs/adr/0004-gate-receipts-over-hook-bypass.md` |
| ADR 0005 - One command, not one per mode | accepted; mechanism superseded by ADR 0009 (2026-09-18) | `docs/adr/0005-single-command-surface.md` |
| ADR 0006 - Index completeness is a separate invariant, and CI runs at --strict | accepted | `docs/adr/0006-index-completeness-as-its-own-invariant.md` |
| ADR 0007 - A vendored artifact declares its origin, not a generator | accepted | `docs/adr/0007-vendored-artifacts-declare-origin-not-generator.md` |
| ADR 0008 — Always-on master contract and living wiki | accepted | `docs/adr/0008-always-on-master-contract.md` |
| ADR 0009 - One skill, one command, one installer | accepted | `docs/adr/0009-one-skill-one-command-one-installer.md` |
| ADR 0010 - Every prompt documented: the repository is its own wiki | accepted | `docs/adr/0010-every-prompt-documented-living-wiki.md` |
| ADR 0011 - Cheap deterministic tools, with an enforced trace and guard | accepted | `docs/adr/0011-cheap-deterministic-tools-over-prose-or-indexing.md` |

## Ledger

| Record type | Records |
|---|---|
| decision | 7 |
| drift | 7 |
| failure | 11 |
| question | 2 |
| requirement | 18 |
| surprise | 2 |

### Requirement records

| Title | Status | Path |
|---|---|---|
| A 25-category wiki with generated platform, history and operations pages | current | `.ai/ledger/requirement/a-25-category-wiki-with-generated-platform-history-and-opera.md` |
| Always on, no command normally typed | current | `.ai/ledger/requirement/always-on-no-command-normally-typed.md` |
| Context gained from a ranked pack within a token budget | current | `.ai/ledger/requirement/context-gained-from-a-ranked-pack-within-a-token-budget.md` |
| Every changed path is traced to its knowledge | current | `.ai/ledger/requirement/every-changed-path-is-traced-to-its-knowledge.md` |
| Every prompt documented everywhere it lands | current | `.ai/ledger/requirement/every-prompt-documented-everywhere-it-lands.md` |
| Gaps become recorded answers through an interview | current | `.ai/ledger/requirement/gaps-become-recorded-answers-through-an-interview.md` |
| Generated facts, curated why, honest gaps | current | `.ai/ledger/requirement/generated-facts-curated-why-honest-gaps.md` |
| Listing refreshed for the living-wiki release | missing | `.ai/ledger/requirement/listing-refreshed-for-the-living-wiki-release.md` |
| Live verification of Codex and Cursor routes | missing | `.ai/ledger/requirement/live-verification-of-codex-and-cursor-routes.md` |
| Many questions with recommended defaults | current | `.ai/ledger/requirement/many-questions-with-recommended-defaults.md` |
| One-line install with no marketplace | current | `.ai/ledger/requirement/one-line-install-with-no-marketplace.md` |
| One skill, one command on every platform | current | `.ai/ledger/requirement/one-skill-one-command-on-every-platform.md` |
| Quantified AI-cost-reduction figure | missing | `.ai/ledger/requirement/quantified-ai-cost-reduction-figure.md` |
| Repetition prompts a skill or rule decision | current | `.ai/ledger/requirement/repetition-prompts-a-skill-or-rule-decision.md` |
| Same tools on Claude Code, Codex and Cursor with one skill and one command | current | `.ai/ledger/requirement/same-tools-on-claude-code-codex-and-cursor-with-one-skill-an.md` |
| Sensitive data is known and never exposed | current | `.ai/ledger/requirement/sensitive-data-is-known-and-never-exposed.md` |
| Stated revenue or pricing model | missing | `.ai/ledger/requirement/stated-revenue-or-pricing-model.md` |
| Tools travel with the skill | current | `.ai/ledger/requirement/tools-travel-with-the-skill.md` |

### Drift records

| Title | Status | Path |
|---|---|---|
| Command file replaced by one skill as the command | unknown | `.ai/ledger/drift/command-file-replaced-by-one-skill-as-the-command.md` |
| Generated logo replaced by hand-designed artwork | unknown | `.ai/ledger/drift/generated-logo-replaced-by-hand-designed-artwork.md` |
| Knowledge delta by prose becomes a traced diff | unknown | `.ai/ledger/drift/knowledge-delta-by-prose-becomes-a-traced-diff.md` |
| No document per library becomes a generated page per library | unknown | `.ai/ledger/drift/no-document-per-library-becomes-a-generated-page-per-library.md` |
| Question budget raised from five to fifteen | unknown | `.ai/ledger/drift/question-budget-raised-from-five-to-fifteen.md` |
| Six commands collapsed to one command | unknown | `.ai/ledger/drift/six-commands-collapsed-to-one-command.md` |
| Wiki grew from 16 to 25 categories | unknown | `.ai/ledger/drift/wiki-grew-from-16-to-25-categories.md` |

Regenerate with: `python <skill>/scripts/extract_history.py --write`
<!-- akinator:generated:end -->

What this answers: every version and revision, what shipped when.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## Which versions and revisions exist, and what shipped in each?

The generated block above is the version and release log. The story in short:

- **1.0.0 - 1.0.2 (2026-08-26):** first release, the knowledge invariants, and
  `index-completeness` as its own check.
- **1.1.0 (2026-08-30):** the v2 pipeline - ledger, distil, harden, project,
  surface - and a fix for a defect shipped into every target repository.
- **1.2.0 (2026-09-18):** one skill, one command, one installer, always on.
- **2.0.0 (2026-09-19):** every prompt documented; the living wiki
  (ADR 0010).
- **2.1.0 (2026-10-03):** traced changes, cheap context, sensitive data, a
  25-category wiki (ADR 0011).

Why each moved is in its change record under `docs/changes/` and its ADR under
`docs/adr/`; this page links, it does not copy.
