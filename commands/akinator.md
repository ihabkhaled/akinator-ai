---
description: Akinator - the one command, and it runs everything. Ask everything, document everything, skillify everything, rule everything. Every station, every lens, every check, until the Definition of Done is proven.
argument-hint: [what you want done] | [onboard | audit | status | sync | question | decide]
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "TodoWrite", "AskUserQuestion", "Skill", "Task"]
---

# Akinator

**One command. It runs everything.**

Load the `akinator-everything` skill and follow it. That is the default and the
main path - not a mode, not an opt-in. `/akinator` means *the complete pass*:
every station of the loop, every applicable boardroom lens, every mechanical
check, looping until the Definition of Done is **proven with evidence** rather
than asserted.

Also load `akinator` for the creed, the loop and the knowledge taxonomy.

## What `$ARGUMENTS` means

**Empty** - run the complete pass over this repository. Resolve the layer, audit
it, find what is missing or untrue, plan the batches, close them, and prove it.

**Anything that is not a mode word** - that is the work. Run the complete pass on
it.

**A mode word as the first token** - run that mode, at full depth. Everything
after the mode word is its argument.

| Mode | Do this |
|---|---|
| `onboard` | `akinator-onboard`. Detect brownfield vs greenfield, write the mapping document, audit, close gaps in batches, run the newcomer test. |
| `audit` | `akinator-coverage` + `akinator-audit`. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/akinator_coverage.py .` plus a claim-vs-code audit. Rank every gap by severity, and say what was **not** checked. |
| `status` | The knowledge-health dashboard - see below. |
| `sync` | `akinator-index-sync` + `akinator-router-sync`. Regenerate everything generable, re-index every artifact, re-sync every router, then re-run the coverage check to prove it. |
| `question` | `akinator-intake`. Run the intake battery, then route every answer to its taxonomy home. |
| `decide` | `akinator-adr`. Record a decision: context, at least two real options with their costs, the decision, consequences including the bad ones, revisit-when. |

A mode is a **narrower target**, never a shallower pass. `/akinator audit
services/api` audits that path exhaustively.

## The complete pass

`akinator-everything` owns the procedure in full. In outline:

| Phase | What happens |
|---|---|
| 1 Ground | RESOLVE the layer, detect this repo's conventions, ASK, AUDIT |
| 2 Plan | Batches, blast radius, **knowledge delta declared by path**, boardroom review at plan time |
| 3 Build | Per batch: implement, document, skillify, rule, contextify, memoize, ADR, business/product/ops, index, sync - then the **librarian**, which must return `CLEAR` |
| 4 Prove | Gate once scoped, run every mechanical check, coverage + newcomer test, anti-gaming on your own output, boardroom review at verify time, clean up |
| 5 Close | Loop unmet lines back into phase 3. When the DoD is proven, **stop** |

Stations 6-11 happen in the same batch as station 5. "I'll document in a
follow-up" is a prohibited sentence.

### The boardroom

Dispatch every lens the work touches, at plan time and again at verify time:

| Touches | Lens |
|---|---|
| money, entitlements, must-never-break | `akinator-business-owner` |
| architecture, dependencies, boundaries, tradeoffs | `akinator-cto` |
| user-facing behavior | `akinator-product-owner` |
| schema, dependencies, build inputs, topology | `akinator-ops` |
| numbers with business meaning | `akinator-analyst` |
| scope and completion honesty | `akinator-pm` |
| **every batch, always** | `akinator-librarian` |

Never call a batch done over a librarian `BLOCKED`.

## Status

Report from the tree, without guessing:

1. **Coverage** - run
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/akinator_coverage.py . --json` and
   summarize counts by severity.
2. **Unindexed artifacts** - the `reachability` and `index-completeness`
   findings. The second is the more precise one: it names artifacts missing
   from their own category index even when something else links them.
3. **Stale-doc suspects** - `doc-truth` findings, plus the context maps with the
   oldest last-verified dates.
4. **Router drift** - `router-sync` findings, and which routers exist at all.
5. **Memory age** - oldest and newest entries, and any whose reversal conditions
   now appear met.
6. **Knowledge entry points present** - which routers and knowledge directories
   exist.

Present it as a short table. If the repo has no knowledge layer, say so plainly
and offer `/akinator onboard` rather than reporting zeros as measurements.

## The one exception to running everything

If the work is genuinely trivial - a typo in a comment, a formatting-only change
- say so in one line, do it, state the knowledge delta as `none, because ...`,
and stop. Performing the full pass on a typo is how a team learns to stop running
any of it.

That judgment is yours to make once, out loud. It is not a licence to scale down
by default.

## Standing rules

- **Stations 6-11 are not deferrable.**
- **Declare the knowledge delta by path** at plan time, or state why none applies.
- **Gate once**, at the end, scoped to what was touched. Never per edit, never
  per commit, never all-workspace.
- **Never add knowledge checks to git hooks.**
- **Adopt, never impose** - match this repo's conventions before creating
  anything.
- **Never weaken a check to make it pass.** A red check is information.
- **Ask on voids, not on routine calls.** Never guess on money, permissions,
  deletion or public contracts.
- **Report honestly.** Failures with their output, skipped steps named, coverage
  claims sampled rather than asserted.
- **Leave the machine as you found it.**
