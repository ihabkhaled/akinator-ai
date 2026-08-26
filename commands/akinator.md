---
description: Akinator - the one command. Ask everything, document everything, skillify everything, rule everything. Runs the loop, or any station of it, on whatever you name.
argument-hint: [onboard | audit | status | sync | question | decide | <describe what you want done>]
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "TodoWrite", "AskUserQuestion", "Skill", "Task"]
---

# Akinator

One command. Every skill, every station, every mode.

`$ARGUMENTS` is either a **mode word** or a **description of work**. Parse it as
follows, then execute. If `$ARGUMENTS` is empty, run **Dispatch** below.

## Modes

| First word | Do this |
|---|---|
| `onboard` | Load `akinator-onboard`. Detect brownfield vs greenfield, write the mapping document, audit, close gaps in batches, run the newcomer test. |
| `audit` | Load `akinator-coverage` and `akinator-audit`. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/akinator_coverage.py .` plus a claim-vs-code audit. Report every gap ranked by severity, and say what was **not** checked. |
| `status` | Knowledge-health dashboard - see **Status** below. |
| `sync` | Load `akinator-index-sync` and `akinator-router-sync`. Regenerate everything generable, re-index every artifact, re-sync every router, then re-run the coverage check to prove it. |
| `question` | Load `akinator-intake`. Run the intake battery on the described task, then route every answer to its taxonomy home. |
| `decide` | Load `akinator-adr`. Record a decision interactively: context, at least two real options with their costs, decision, consequences including the bad ones, revisit-when. |
| anything else | Treat `$ARGUMENTS` as the work. Run the full loop on it - **Dispatch** below. |

Everything after the mode word is that mode's argument. `akinator audit
services/api` audits that path; `akinator decide which queue to use` opens an ADR
on that question.

## Dispatch - the full loop

This is the default and the main path. Load the `akinator` skill for the creed,
the loop and the taxonomy, then run the twelve stations, routing each to its
skill:

| # | Station | Skill |
|---|---------|-------|
| 1 | ASK | `akinator-intake` |
| 2 | RESOLVE | routers, rules, skills, context, memory, `.ai`, docs - in that order |
| 3 | AUDIT | `akinator-audit` |
| 4 | PLAN | `akinator-plan` - **declare the knowledge delta by path, per batch** |
| 5 | IMPLEMENT | domain skills |
| 6 | DOCUMENT | `akinator-document-change` |
| 7 | SKILLIFY | `akinator-skillify` |
| 8 | RULE | `akinator-rule-forge` |
| 9 | CONTEXTIFY | `akinator-contextify` |
| 10 | MEMOIZE | `akinator-memoize` |
| 11 | INDEX+SYNC | `akinator-index-sync`, `akinator-router-sync` |
| 12 | VERIFY | `akinator-gate-economy`, `akinator-coverage` |

Business, product and operational knowledge route to `akinator-business-map`,
`akinator-product-map` and `akinator-ops-map` from stations 1, 4 and 6 whenever
the work touches money, user-facing behavior, or how the system is operated.

Before any heavy command, `akinator-resource-guard`. Throughout,
`akinator-anti-gaming`.

### Scale to the work

- **Trivial** (a typo, a one-line fix): run stations 2, 5 and 12. State the
  knowledge delta in one line - including "none, because ...".
- **Normal**: all twelve stations, one batch.
- **Large**: all twelve stations, several batches, each with its own declared
  delta, one scoped gate at the very end.

Do not perform ceremony on a typo. Do not skip stations on a feature.

### Boardroom review

At station 4 and again at station 12, invoke the review lenses the work
actually touches - as subagents:

| Touches | Agent |
|---|---|
| money, entitlements, must-never-break | `akinator-business-owner` |
| architecture, dependencies, boundaries, tradeoffs | `akinator-cto` |
| user-facing behavior | `akinator-product-owner` |
| schema, dependencies, build inputs, topology | `akinator-ops` |
| numbers with business meaning | `akinator-analyst` |
| **every batch, always** | `akinator-librarian` |
| completion claims | `akinator-pm` |

The **librarian runs on every batch** and blocks completion until stations 6
through 11 are satisfied. Do not call a batch done over a librarian `BLOCKED`.

## Status

Report, from the tree, without guessing:

1. **Coverage** - run
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/akinator_coverage.py . --json` and
   summarize counts by severity.
2. **Unindexed artifacts** - the `reachability` findings.
3. **Stale-doc suspects** - `doc-truth` findings, plus context maps whose
   last-verified date is oldest.
4. **Router drift** - `router-sync` findings, and which routers exist at all.
5. **Memory age** - the oldest and newest entries, and any whose reversal
   conditions now appear met.
6. **Knowledge entry points present** - which of the routers and knowledge
   directories exist.

Present it as a short table. If the repo has no knowledge layer, say so plainly
and offer `/akinator onboard` rather than reporting zeros as if they were
measurements.

## Standing rules

These hold in every mode:

- **Stations 6-11 are not deferrable.** "I'll document in a follow-up" is a
  prohibited sentence.
- **Declare the knowledge delta by path at plan time**, or state explicitly why
  none applies.
- **Gate once**, at the end, scoped to what was touched. Never per edit, never
  per commit, never all-workspace.
- **Never add knowledge checks to git hooks.**
- **Adopt, never impose** - match the repo's existing conventions before
  creating anything.
- **Never weaken a check to make it pass.** A red check is information.
- **Ask on voids, not on routine calls.** Many questions early, near zero late.
  Never guess on money, permissions, deletion or public contracts.
- **Leave the machine as you found it.**
