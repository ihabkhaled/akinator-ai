# Agents - the boardroom

Seven review lenses, invoked at station 4 (PLAN) and again at station 12
(VERIFY). They are lenses with defined powers, not roleplay: each reviews one
dimension and each holds an explicit veto.

Dispatch every lens the work touches. A veto at plan time is cheap; the same
veto at verify time costs the batch.

## The enforcement heart

| Agent | Runs | Vetoes |
|---|---|---|
| [akinator-librarian](../agents/akinator-librarian.md) - checks the knowledge delta against the tree: routing, index reachability, router sync, staleness, anti-gaming | **every batch, without exception** | any batch whose declared knowledge delta is missing, misplaced or untrue |

The librarian fires before a commit exists, which is earlier and cheaper than
any hook, and it reports which skill produces the missing artifact rather than
just an exit code. Never call a batch done over a `BLOCKED`.

## The dimension lenses

Invoked when the work touches their dimension.

| Agent | Reviews for | Vetoes |
|---|---|---|
| [akinator-business-owner](../agents/akinator-business-owner.md) - money, revenue, entitlements, what must never break | business value and risk to the money | changes altering money or entitlement semantics with no business document |
| [akinator-cto](../agents/akinator-cto.md) - architecture fit, boundaries, dependencies, rejected alternatives, the debt ledger | whether the shape is recorded, not just chosen | undocumented architectural decisions and unrecorded debt |
| [akinator-product-owner](../agents/akinator-product-owner.md) - feature intent, acceptance criteria, the edge-case decision log | whether "is this a bug or on purpose?" will be answerable | features shipping with unrecorded product decisions |
| [akinator-ops](../agents/akinator-ops.md) - restart versus rebuild, migration ordering, parallelism, rollback, the point of no return | the runbook delta | operationally consequential changes with no written procedure |
| [akinator-analyst](../agents/akinator-analyst.md) - quotas, limits, prices, thresholds, retention, anything numeric with commercial meaning | whether the numbers are written in business language | numeric business rules living only in code |
| [akinator-pm](../agents/akinator-pm.md) - batch discipline, scope creep, done-versus-claimed-done | completion honesty, in the four-part form: implemented / wired / verified / documented | done claims without evidence |

## How they are used

Claude Code loads them from `agents/` as subagents. Codex has no equivalent
subagent surface, so the same lenses are applied inline there - the review
questions are the same, only the dispatch differs.

`skills/akinator-everything/SKILL.md` names which lens applies to which kind of
work - phase 2 for the plan-time review, step 22 inside phase 4 for verify.

## Adding a lens

A new agent is warranted only when a dimension is genuinely unreviewed and has a
veto worth holding. Seven is already a lot to dispatch; an eighth that overlaps
an existing lens makes both weaker, because the work gets split and neither
reviews it fully.
