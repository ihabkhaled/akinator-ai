# Docs

Narrative knowledge about Akinator: how it works, why it exists, what it depends
on, and every decision made building it.

Facts that can be extracted from the tree live in `context/`, not here.

## Understanding Akinator

| Doc | Answers |
|---|---|
| [Architecture](architecture.md) | What each component is, when it runs, and how the five surfaces compose into a behavior that persists across sessions |
| [Business case](business-case.md) | Why this exists, what it is worth, how to tell whether it is working, and what would make it fail |
| [Compatibility](compatibility.md) | The Claude Code and Codex contracts relied on, how they were verified, and what breaks when they move |
| [Listing](listing.md) | The directory-submission copy - name, description, example use cases - kept in the repo so it cannot drift from what ships |
| [The brief](brief.md) | The budget-capped context bundle a new session reads first, and how items compete for a place in it |
| [Scoping](scoping.md) | How a pass scales to the change without skipping a station, and the interrupt budget on questions |
| [Rule evolution](rule-evolution.md) | When a rule's enforcement causes the next failure - and why a superseded rule is never deleted |
| [Distil](distil.md) | How a recurring failure becomes a rule proposal - and why `neither` is a real answer |
| [The ledger](ledger.md) | What happened - failures, questions, decisions and surprises - fingerprinted so recurrence becomes a rule |
| [Akinator v2 design](akinator-v2-design.md) | The capture/distil/harden/project/surface pipeline, its budgets, and the seven implementation phases - all shipped in 1.1.0. Kept as the reasoning behind the pipeline, not as a plan |
| [Deviations](deviations.md) | Where the implementation departs from the build brief, and why |

## Decisions

Every non-obvious choice, with its rejected alternatives and their costs.

| ADR | Decision |
|---|---|
| [0001](adr/0001-mit-license.md) | MIT license - adoption is the goal, and MIT is what passes corporate legal review without a conversation |
| [0002](adr/0002-codex-pack-generated-from-claude-skills.md) | The Codex pack is generated from the Claude skills, not maintained by hand or symlinked |
| [0003](adr/0003-enforcement-outside-git-hooks.md) | Knowledge enforcement lives in session behavior, CI and tests - never in a git hook |
| [0004](adr/0004-gate-receipts-over-hook-bypass.md) | Tree-bound gate receipts rather than hook bypass, because a receipt is auditable |
| [0005](adr/0005-single-command-surface.md) | One command dispatching every mode, not one command per mode |
| [0006](adr/0006-index-completeness-as-its-own-invariant.md) | Index completeness is its own invariant, and CI runs at `--strict` |

See [the ADR index](adr/README.md) for the full list and the conventions.

## Related

- `rules/README.md` - the constraints this repository holds itself to
- [Skills index](skills.md) - the 21 skills and what triggers each
- [Agents index](agents.md) - the seven boardroom lenses and what each vetoes
- `context/README.md` - generated structural maps
- `memory/index.md` - durable decisions and surprises
- `evals/README.md` - the behavioral eval suites


## Living product knowledge

- [Living wiki contract](living-wiki.md) — use when an agent needs to resolve or maintain product/business intent, change provenance, current truth, historical truth, future intent, failures, decisions, constraints and staleness conditions above the codebase.
