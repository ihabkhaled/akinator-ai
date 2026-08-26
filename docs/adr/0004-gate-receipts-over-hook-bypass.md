# ADR 0004 - Tree-bound gate receipts, not hook bypass

- **Status:** accepted
- **Date:** 2026-08-26
- **Deciders:** Ihab Khaled (owner)

## Context

Gate economy says: build the whole batch, gate once at the end, scoped to what
was touched, then land. That leaves a specific problem at the landing step.

The scoped gates have just proven the exact tree green. If the repository has
commit or push hooks that run the same checks, landing re-runs them over a tree
that has not changed - paying twice for the same proof, on the developer's
machine, at the moment they are trying to finish.

The obvious shortcut is `--no-verify`. But some repositories detect and reject
bypass recommendations as a policy violation, and a blanket habit of bypassing
is indistinguishable - from the outside, and eventually from the inside - from
hiding a failure.

## Options considered

### Option A - Always re-run the hooks

- **What it is:** accept the duplicate pass.
- **Cost:** minutes per landing, every landing, on the developer's machine,
  proving something already proven. On a loaded machine it also introduces
  timeout flakiness at the worst moment.
- **Why it lost:** it is pure waste, and the waste is what drives people to
  bypass habitually - the behavior this decision is trying to avoid.

### Option B - Bypass hooks after a green gate

- **What it is:** `--no-verify` when the batch's gates just passed.
- **Cost:** unauditable. Nothing distinguishes "I proved this tree green two
  minutes ago" from "the tests were failing and I wanted to land". Some repos
  forbid it by policy and detect the recommendation.
- **Why it lost:** the absence of evidence is the whole problem. A bypass leaves
  no trace of *why* it was safe, so it cannot be reviewed and it degrades into a
  habit.

### Option C - A tree-bound gate receipt (chosen)

- **What it is:** when the scoped gates pass, record a receipt: the hash of the
  proven tree, which gates ran, at which scope, their exit codes, and the
  timestamp. Hooks honor the receipt **for that exact tree only** and skip the
  duplicate pass. A single changed byte voids it - there is no partial credit.
- **Cost:** a mechanism to build and maintain in each target repo that wants it,
  and a discipline to record honestly. It is more work than typing
  `--no-verify`.
- **Why it won:** it is **auditable**. The receipt states exactly what was proven
  over exactly which tree, so skipping is a verifiable claim rather than an
  assertion of good intent. Tree-binding makes the dangerous case - a tree that
  changed since the proof - impossible rather than merely discouraged.

## Decision

Where a just-proven-green tree must be landed through a hook stack that would
re-prove it, Akinator uses a **tree-bound gate receipt**. The receipt is always
the preferred, auditable form.

Outright hook-skipping is permitted **only** where the target repository's own
policy explicitly allows it, and only for a tree whose gates have just passed -
never to get past a red gate, and never where the repo's policy forbids bypass.
Akinator detects that policy before recommending anything.

## Consequences

**Good**
- No duplicate proof over an unchanged tree.
- The skip is auditable: the receipt says what was proven and over what.
- Tree-binding makes the unsafe case structurally impossible, not just
  discouraged.
- Repos that forbid bypass are respected without losing the economy.

**Bad**
- The receipt mechanism must be built per target repository; Akinator specifies
  it rather than shipping it, because hook stacks differ too much for one
  implementation.
- A receipt recorded dishonestly is worse than no receipt, because it looks like
  evidence. This is a session-behavior risk, mitigated by `akinator-anti-gaming`
  and by `akinator-pm` demanding exit codes rather than claims.

**Debt taken on**
- Akinator does not currently ship a reference receipt implementation. The
  mechanism is specified in `rules/06-gate-once-scoped-at-the-end.md` and
  `skills/akinator-gate-economy/SKILL.md`. Pay this down the first time a target
  repo needs one, by extracting that implementation into `templates/`.

## Revisit when

- A target repository's hook stack makes receipts impractical.
- Git or a hook manager gains native support for content-addressed check
  results, which would make this a platform feature rather than a convention.
- The first reference implementation exists and can be generalized.

## Related

- Rules: `rules/06-gate-once-scoped-at-the-end.md`
- Skills: `skills/akinator-gate-economy/SKILL.md`
- ADR: `docs/adr/0003-enforcement-outside-git-hooks.md`
