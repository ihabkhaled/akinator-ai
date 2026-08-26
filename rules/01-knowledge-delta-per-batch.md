# Rule 01 - Every batch declares and delivers a knowledge delta

## Purpose

Documentation does not get skipped by decision. It gets skipped because it never
became a line item, so nobody ever noticed its absence. The fix is structural:
the knowledge delta is **named at plan time, by path**, before any code exists.
Then omitting it is a visible edit to the plan rather than a silence.

Without this rule the whole plugin is advice. With it, a missing doc is a
missing deliverable.

## Applies to

- **In scope:** every batch of work in this repository, and in every repository
  an Akinator-governed session touches.
- **Out of scope:** nothing. A batch with genuinely no knowledge consequence
  still states that, and why - see Exceptions.

## Mandatory rules

1. Every batch plan names, **by path**, the docs, skills, rules, context maps,
   memory entries, ADRs and routers it will create or change.
2. Empty categories are stated with a reason. A missing line is a violation; an
   explicitly empty line is not.
3. Stations 6 through 11 of the loop happen in the **same batch** as station 5.
   "I'll document in a follow-up" is a prohibited sentence.
4. A batch whose entire delta is empty states why, in the plan and again in the
   commit message.
5. Deletion batches always have a non-empty delta - removing behavior removes or
   updates every doc that described it.

## Prohibited patterns

```markdown
Batch 2 - refund handling
  Code:  src/billing/refund.ts
  Docs:  will update after review     <- deferred: prohibited
                                      <- rules/skills/context/memory: silent
```

```
commit: "add refund quota restore"     <- no delta, no justification
```

## Correct pattern

```markdown
Batch 2 - refund handling
  Code:     src/billing/refund.ts, src/quota/apply.ts
  Docs:     docs/business/quotas.md (refund behavior section)
  Rules:    rules/07-quota-mutations.md (new)
  Skills:   (none - no repeatable procedure introduced)
  Context:  context/entitlements.md (regenerate)
  Memory:   memory/2026-08-26-refund-quota-decision.md
  ADR:      docs/adr/0012-refund-restores-quota.md
  Routers:  CLAUDE.md, AGENTS.md, CODEX.md
  Ops:      (none - no migration, no restart-ordering change)
```

## Enforcement

- Mechanism: `agents/akinator-librarian.md` - runs at the end of every batch,
  compares the declared delta against the tree, and blocks completion. This is
  the primary enforcement and it fires before a commit exists.
- Mechanism: `scripts/akinator_coverage.py` - the `reachability`, `doc-truth`
  and `staleness` checks catch delivered-but-unindexed and
  delivered-but-untrue artifacts in CI.
- Mechanism: `tests/test_plugin_structure.py::test_every_loop_station_has_a_skill`
  asserts the loop's stations each have a skill that can be routed to, so the
  delta always has somewhere to go.
- Type: session behavior (blocking agent), plus CI checks, plus a unit test.
- How it fails: the librarian reports `BLOCKED` with the specific missing path
  and the skill that produces it.
- Last observed passing: 2026-08-26

**Never a git hook** - see `rules/05-no-git-hook-complication.md`.

## Exceptions

A batch may have a fully empty delta when the change genuinely carries no
knowledge: a typo fix in a comment, a formatting-only change, a dependency bump
with no behavioral or operational consequence.

To take the exception, state it explicitly in the plan and the commit message:

```
Knowledge delta: none - formatting only, no behavior, contract or operational
consequence changed.
```

Silence is never the exception. The sentence is.

## Related

- Skills: `akinator-plan`, `akinator-document-change`, `akinator-anti-gaming`
- Agents: `akinator-librarian`
- Rules: `rules/03-rules-need-live-enforcement.md`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] Enforcement mechanisms exist in the tree and are named by path.
- [x] The mechanisms are not git hooks.
- [x] Prohibited and correct patterns are shown.
- [x] The exception path is named and requires an explicit sentence.
- [x] The rule is indexed and reflected in every router.
