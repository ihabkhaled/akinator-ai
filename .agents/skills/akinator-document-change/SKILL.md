---
name: akinator-document-change
description: Use in the same batch as any code change, before the batch is called done. Routes the change's why, its when-not-to, its business meaning and its operational consequence to their canonical homes in the knowledge taxonomy, and verifies each doc against the tree it describes.
---
<!--
DO NOT EDIT BY HAND.
Installed from the Akinator plugin - the canonical akinator-document-change skill.
No generator is named by path: this file travels into repositories
that do not have one, where naming it would be a false claim.
To update: reinstall Akinator, or regenerate inside an Akinator
checkout. Local edits here are replaced either way.
-->

# Akinator Document Change - station 6

Station 6 is where most documentation mandates die, because the code works now
and the docs feel like paperwork. They are not paperwork. They are the difference
between the next agent spending four seconds and four hours.

The rule that makes this station cheap: **document what the code cannot say
about itself.**

## When to use

In the same batch as station 5, every time, before the batch is called done. Also
when deleting behavior - deletion is a documentation event.

## When NOT to use

- To restate what the code plainly says. A doc that paraphrases an
  implementation is a liability: it costs bytes, earns trust, and rots on the
  next refactor.
- To create a new home for a fact that already has one. Link instead.

## Procedure

### 1. Ask the four questions the code cannot answer

For the change you just made:

1. **Why is it this way?** What forced this shape - a constraint, a bug, a
   business rule, a platform limit, a rejected alternative?
2. **When should someone NOT do this?** The conditions under which this pattern
   is wrong. This is the highest-value sentence in most documents, and it is
   almost never written.
3. **What does it mean to the business?** In business language. What breaks for
   whom, and what is it worth?
4. **What is the operational consequence?** Does this change how the system is
   deployed, migrated, restarted, recovered or rolled back?

If all four answers are genuinely "nothing beyond what the code says" - a typo
fix, a rename with no semantic change - say so explicitly in the batch. That is a
justified empty delta, not a skipped station.

### 2. Route each answer to its canonical home

| Answer | Home | Skill |
|---|---|---|
| Why this shape, with alternatives rejected | `docs/adr/` | `akinator-adr` |
| Why this shape, no real alternatives | inline in the relevant `docs/` page | this skill |
| When not to do this | the rule, if it is a constraint; otherwise the doc | `akinator-rule-forge` |
| Business meaning, numbers, money semantics | `docs/business/` | `akinator-business-map` |
| Feature intent, acceptance criteria, edge cases | `docs/product/` | `akinator-product-map` |
| Deployment, migration, restart, recovery, rollback | `docs/ops/` | `akinator-ops-map` |
| A structural fact that changed | `context/` | `akinator-contextify` |
| A surprise, a preference, a decision worth remembering | `memory/` | `akinator-memoize` |

Never write the same fact into two homes. The second one is a link.

### 3. Write it so it earns its bytes

Each doc change states:

- **The fact**, in the fewest words that are still true.
- **The why**, including what was rejected and on what grounds.
- **The when-not-to.**
- **What would make this stale** - "regenerate when the route table changes",
  "review when a second payment provider is added". Every doc carries this line;
  it is what makes staleness detectable instead of discovered.
- **Links to the code** it describes, by path.

### 4. Handle deletion

When behavior is removed:

1. Find every doc that described it - grep the removed symbols, routes, flags and
   feature names across `docs/`, `rules/`, `context/`, `memory/` and the routers.
2. Delete or correct each one **in this batch**.
3. If the behavior was removed for a reason worth knowing, that reason is an ADR
   or a memory entry - the knowledge outlives the code.

A doc describing deleted behavior is a **critical** finding in
`akinator-coverage`. Leaving one behind is worse than never having written it.

### 5. Verify against the tree

Before the batch is done, for each doc you touched:

- Every file path named in it exists.
- Every symbol, route, flag, command and env var named in it exists.
- Every code snippet reflects current code, not the version you started from.

This verification is what separates documentation from fiction.

## Failure modes and pitfalls

- **The what-restating doc.** "The `applyQuota` function applies the quota."
  Delete it; write why quota is applied there and nowhere else.
- **Documenting the plan instead of the change.** Docs describe what is true now,
  not what you intended.
- **Writing the doc from the diff.** The diff shows the change; the doc needs the
  resulting state. Read the final file.
- **Deferring to a follow-up.** Prohibited. The batch is not done.
- **New home creation.** Before creating a doc, check whether the fact already
  has a home. Two homes means two versions means one of them is wrong.
- **Missing the staleness line.** A doc without it cannot be audited and will rot
  silently.

## Definition of done

- [ ] The four questions were asked for this change, and answered or explicitly
      dismissed.
- [ ] Every answer is written into exactly one canonical home.
- [ ] Every doc touched states what would make it stale.
- [ ] Every path, symbol and command named in a touched doc exists in the tree.
- [ ] If behavior was deleted, every doc describing it was found and corrected in
      this batch.
- [ ] Every new doc is reachable from an index (`akinator-index-sync`).
