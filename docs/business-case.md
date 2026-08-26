# Business case

Why Akinator exists, what it is worth, and how to tell whether it is working.
This is a living document, not a pitch archive - it is updated when the reasoning
changes, and it is where the success measure is recorded.

## The problem

Every codebase decays the same way: **the code outlives its context.**

The why, the business rules, the product intent, the operational procedures, the
rejected alternatives - all of it lives in people's heads and chat scrollback,
and it evaporates. Every new contributor pays a re-derivation tax: hours or days
spent rediscovering what someone already knew.

On an AI-heavy team that tax is paid **per session**. An agent with a fresh
context window is a new hire every single morning - competent, fast, and
completely without institutional memory. It re-derives the same architecture,
re-asks the same product questions, and re-discovers the same operational trap
that cost three hours last month.

The tax compounds in a specific way that makes it easy to underestimate: the
agent does not know what it does not know. It infers confidently from the code,
and inference from code recovers *what* the system does while losing *what it
should* do. That gap is where the expensive failures live - the refund that
restores quota it should not, the restart that should have been a rebuild.

## The insight

The teams that win are not the teams with the best code. They are the teams
where **any agent can gain complete, accurate, trustworthy context in seconds** -
where the repository itself is the institutional memory, and it never lies.

Three words in that sentence carry the weight:

- **Complete** - the business rule is written, not only the implementation.
- **Accurate** - a stale doc is worse than no doc, because it is trusted.
- **Seconds** - an answer that takes fifteen minutes of searching is not used;
  people guess instead.

## Why a plugin, not a prompt

A prompt asking an agent to document things decays within one session. It gets
compacted away, deprioritized under time pressure, or simply not repeated in the
next session.

A plugin makes the behavior the **default operating mode**:

- loaded at session start, before the first tool call;
- reinforced by skills that trigger on every kind of codebase touch, without
  anyone remembering to invoke them;
- blocked by a review lens when it is skipped;
- verified by a check that fails in CI;
- portable across every repository the team owns.

The difference is between asking for a behavior and installing one.

## What it produces

Installed, the repository accumulates the knowledge a full team would hold:

| Persona | What the repo records because Akinator made it |
|---|---|
| Business owner | Why the product exists, who pays, what each feature is worth, what must never break |
| CEO | Strategy, priorities, what gets cut when things conflict |
| CTO | Architecture, technology choices and their rejected alternatives, the debt ledger |
| Product owner | Every feature's intent, acceptance criteria, edge-case decisions |
| Business analyst | The numbers behind pricing, quotas and entitlements, in business language |
| Decision maker | Recorded decision criteria, so an agent can decide on the owner's behalf and be right |
| Operations | Runbooks: restart versus rebuild, ordering, parallelism, rollback, what to check first |
| Project manager | Scope, batches, done versus claimed done, what blocks what |

The goal state is an AI that can take decisions on the owner's behalf, because
the repository has made it fully aware of the context - and every decision it
takes makes the repository more aware for the next one.

## The value, quantified

The measurable claim is a **curve**, not a level:

> The second repository Akinator onboards should cost roughly a tenth of the
> first.

That bend is the entire product. The first onboarding pays for the mapping, the
extractors, the first rules and the first runbooks. The second reuses the
templates, the skills, the checker and the discipline - and the third is close
to free.

Per-repository, the value shows up as:

| Cost today | After |
|---|---|
| Re-derivation per fresh session: minutes to hours, every session | Seconds, from the layer |
| The same product question asked twice | A defect, caught by the eval |
| An operational trap rediscovered per incident | A runbook that fires from a skill |
| A business rule that lives only in code | Written in business language, next to its code, asserted by a test |
| A decision reversed because nobody recorded why | An ADR with the rejected options and their costs |

## What "working" means - the measure

Not "the files exist". The bar is the **newcomer test**:

> A fresh agent, given only the knowledge layer, correctly answers - in seconds -
> where to go, what to do, what not to break, and what to run afterwards, for
> each of the repository's five most common change types.

It is tested literally: a fresh-context agent, unaided, graded pass / partial /
fail. A confident-but-inferred answer is a **fail**, and the most dangerous
result - the layer did not answer, and the agent did not notice.

Failures are not a disappointment; they are the specification for the next
improvement batch, and better specified than anything written from imagination.

See `skills/akinator-coverage/SKILL.md` and `evals/newcomer/README.md`.

## What would make this fail

Stated plainly, because a business case that names no failure mode is advocacy:

- **Fake compliance.** Vacuous docs, copy-paste skills, rules with no
  enforcement, ticked checklists. Worse than absence, because they are trusted.
  Countered by `skills/akinator-anti-gaming/SKILL.md`, and by making the
  coverage checker verify rather than accept claims.
- **Ceremony cost exceeding value.** If the discipline is applied at full weight
  to typo fixes, it becomes overhead and gets abandoned. Countered by scaling
  the loop to the work, explicitly, in the command.
- **A checker with false findings.** People stop reading it, and then it enforces
  nothing. This is why the fenced-code exemption exists, and why a red finding is
  treated as information rather than an obstacle to route around.
- **Imposing on a repo that had its own conventions.** Two competing taxonomies
  is worse than one imperfect one. Countered by adopt-never-impose and the
  mapping document.

## Related

- `README.md` - what it is and how to install it
- `docs/architecture.md` - how it works
- `skills/akinator/SKILL.md` - the creed and the loop
- `docs/adr/` - the decisions made building it

## Review when

- The newcomer test is run against a real target repository and produces data
  that contradicts or confirms the cost-curve claim.
- Last verified: 2026-08-26.
