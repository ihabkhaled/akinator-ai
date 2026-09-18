# Living wiki contract

Akinator maintains a repository as **code plus an executable body of knowledge**.
The wiki exists so a fresh agent can understand intended behavior without
reverse-engineering product truth from implementation.

## Questions the wiki must answer

For every important capability, a newcomer should be able to resolve:

- **WHAT** exists, and what is deliberately absent?
- **WHY** does it exist, and what problem/business outcome does it serve?
- **WHO** uses it, owns it, decides it, and is affected by it?
- **WHEN** was it introduced/changed, and when does it run or apply?
- **WHERE** does it live: components, routes, data, events and integrations?
- **HOW** does it work and how is it operated, tested, recovered and rolled back?
- **BEFORE** — what was true before the latest meaningful change?
- **NOW** — what is true in the current tree?
- **NEXT** — what is intended but not yet implemented?
- **WHY NEXT** — what evidence or requirement motivates that future intent?
- **CONSTRAINTS** — what must never break and how is it enforced?
- **DECISIONS** — what alternatives were rejected and why?
- **FAILURES** — what went wrong before and how recurrence is prevented?
- **PROVENANCE** — where did each important claim come from?
- **STALE WHEN** — what event requires this knowledge to be reverified?

## Wiki domains

Akinator maps these domains onto the repository's existing structure:

1. Product vision, actors/personas, jobs-to-be-done, journeys and stories.
2. Feature intent, acceptance criteria, edge cases and non-goals.
3. Business model, policies, pricing, quotas, entitlements and invariants.
4. Architecture, boundaries, components, dependencies, data and event flows.
5. API/contracts, schemas, permissions, security and integration assumptions.
6. Operational runbooks: deploy, migrate, rollback, recover, diagnose.
7. Decisions/ADRs and their consequences/revisit conditions.
8. Change history/provenance: before → change → now → why.
9. Failures/incidents/lessons and recurrence prevention.
10. Rules with mechanical enforcement.
11. Skills/runbooks for repeatable procedures.
12. Context maps and ownership.
13. Durable memory: preferences, surprises and facts that survive sessions.
14. Future intent/roadmap, explicitly separated from implemented truth.
15. Verification evidence and staleness conditions.

## Truth model

**Current truth**, **historical truth** and **future intent** must never be mixed.

- Current docs describe the tree as it exists now.
- Change records explain how and why it became that way.
- ADRs explain decisions and alternatives.
- Future docs describe intended work and must be labeled not implemented.
- Code is evidence of implementation, not evidence of product intent.
- Unknown means unknown. Akinator asks; it does not fabricate business truth.

## Change provenance minimum

For a meaningful change record: when; actor/agent when knowable; request/source;
affected paths/components; before; change; now; why; business intent; product
intent; technical reasoning; alternatives/trade-offs; compatibility/migration/
rollback; related rules/skills/failures/ADRs; verification; future implications;
staleness condition.

## Compaction laws

A useful wiki is not a transcript.

- One canonical home per fact; other pages link.
- Prefer decisions and invariants over narration.
- Do not paraphrase obvious code.
- Preserve reasons that code cannot express.
- Record exact paths/contracts when they improve navigation.
- Every important page has an owner/source or provenance and a staleness trigger.
- Repeated procedures become skills.
- Reusable failure prevention becomes an enforced rule.
- Index every artifact so a new agent can discover it from the router.
