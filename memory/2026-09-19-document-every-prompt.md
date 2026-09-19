---
name: document-every-prompt
type: preference
date: 2026-09-19
---

# The owner wants exhaustive, corporate-scale documentation and many questions

## The fact

The owner's stated requirement for Akinator at corporate scale: every prompt
and every change is documented - product, business, market, requirements
(current, changed, missing, dropped), drift, architecture, libraries, stack,
infra, testing/UAT, UX, project management, decisions - so that any AI reading
the repository knows it completely and can decide or recommend with evidence.
The owner also wants many questions asked per prompt, not few.

This reverses two earlier decisions made in this same repository:
[[single-command-preference]]'s neighbor, the five-question interrupt budget in
`docs/scoping.md`, and the stack map's refusal to give each library its own
page. Both were optimizing for the maintainer's effort; the owner is optimizing
for a reader who was never in the room.

## Why

Stated by the owner while scoping ADR 0010: documentation at scale for
corporate use, covering everything a new AI or teammate would need to decide or
recommend without asking again. A five-question cap and a no-page-per-library
stance both trade completeness for cheapness - the opposite of what was asked
for.

The design answer is not "write more by hand" (Option B in ADR 0010, rejected:
volume without truth is worse than absence). It is generate the facts, curate
only the why, and mark every unknown as a question. That is what keeps
"exhaustive" from becoming "stale."

## Date

- 2026-09-19 - recorded while writing ADR 0010 and the `akinator-wiki` /
  `akinator-decide` stations.

## Reversal conditions

- The owner routinely answers "go with recommendations" to most of the fifteen
  questions - then the default budget is too high for the value it returns
  (ADR 0010's first revisit condition), and the budget should come back down.
- The owner asks for fewer documents, or narrower scope, explicitly.

## Related

- `docs/adr/0010-every-prompt-documented-living-wiki.md` - the decision record
- `skills/everything/references/akinator-wiki.md`,
  `skills/everything/references/akinator-decide.md`
- `docs/scoping.md` - the question budget, now 15, was 5
- `rules/13-every-prompt-is-documented.md`
- [[single-command-preference]] - the same owner, the opposite instinct: one
  surface, but no limit on what that surface must produce
