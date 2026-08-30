---
name: akinator-intake
description: Use before planning any substantive work, and whenever a request has two readings that lead to materially different work, or when implementation forces a product decision no document answers. Runs the intake question battery, then converts every answer into a permanent artifact so the same question is never asked twice.
---
<!--
DO NOT EDIT BY HAND.
Installed from the Akinator plugin - the canonical akinator-intake skill.
No generator is named by path: this file travels into repositories
that do not have one, where naming it would be a false claim.
To update: reinstall Akinator, or regenerate inside an Akinator
checkout. Local edits here are replaced either way.
-->

# Akinator Intake - the question engine

An unasked question becomes an unrecorded assumption becomes a production bug.
An asked-and-unrecorded question becomes the same bug one session later.

The engine is calibrated: **many questions early, near zero questions late.** An
agent that interrupts mid-flow for something the knowledge layer already answers
has failed just as badly as one that guesses on a genuine void.

## When to use

- **Intake** - before planning any substantive work.
- **Ambiguity gates** - whenever two readings of the request lead to materially
  different work. Never guess on money, permissions, data deletion, or
  user-visible contracts.
- **Business-rule voids** - when implementation forces a product decision no doc
  answers ("what happens to quota on refund?"). Stop, ask, file the answer as
  business documentation, then code past it.

## When NOT to use

- Routine judgment calls a careful senior colleague would make alone. Make them,
  record them as decisions, move on.
- Anything the knowledge layer already answers. Answer from the layer and **cite
  where** - the citation is the proof that station 2 ran.
- Mid-implementation, for questions that were answerable at intake. That is an
  intake failure, not diligence; note it and improve the battery.

## Procedure

### 1. Resolve before asking

Read the layer first (routers, rules, skills, context, memory, `.ai`, docs).
Every question the layer answers is struck from the battery, and its answer is
cited in your intake summary. A battery that shrinks over time is the product
working.

### 2. Run the battery

Ask only what survived step 1. Group the questions so the owner answers in one
pass rather than in a drip.

**Goal and scope**
- What outcome are we buying? What changes for a user when this ships?
- What is explicitly a non-goal for this piece of work?
- What is the appetite - a fix, a feature, or a rebuild?

**Value and priority**
- Who pays for this, directly or indirectly? What is it worth?
- What gets cut first if this conflicts with something else in flight?

**Users and blast radius**
- Which users or tenants are affected? Which are explicitly not?
- What existing behavior must not change?

**Rules and edges the owner cares about**
- What must never break, even at the cost of shipping late?
- Which edge cases have a business answer already, and which are undecided?
- Anything touching money, permissions, deletion, or a public contract?

**Definition of done, in their words**
- How will you know this worked? What would you check first?
- What would make you say "that shipped but it is wrong"?

**Operational consequence**
- Does this change how the system is deployed, migrated, restarted, or recovered?
- Is there an ordering constraint - what must rebuild, in what order, what can
  run in parallel?

### 3. Route every answer to a permanent home

This is the station that makes the engine pay for itself. Each answer goes to its
taxonomy home **in this batch**, not later:

| Answer type | Home | Skill |
|---|---|---|
| A business rule, a number, a money or entitlement semantic | `docs/business/` | `akinator-business-map` |
| Feature intent, acceptance criteria, an edge-case decision | `docs/product/` | `akinator-product-map` |
| A hard constraint others must not break | `rules/NN-*.md` | `akinator-rule-forge` |
| A repeatable procedure the owner described | `skills/*/SKILL.md` | `akinator-skillify` |
| An operational consequence or ordering constraint | `docs/ops/` | `akinator-ops-map` |
| A decision between real alternatives | `docs/adr/` | `akinator-adr` |
| A durable preference or surprise | `memory/` | `akinator-memoize` |
| A structural fact | `context/` | `akinator-contextify` |

### 4. Record the unanswered

Questions the owner deferred are not dropped. Write them into the relevant
product or business doc under an explicit **Open questions** heading, with the
date and what is blocked by each. An open question that is written down is
knowledge; one that is only remembered is a bug waiting for a deadline.

## Failure modes and pitfalls

- **Asking what the layer answers.** Every such question tells the owner the
  documentation is not being read. Resolve first, always.
- **Asking everything at once with no shape.** A wall of twenty questions gets a
  three-word answer. Group them, lead with the ones that change the work most,
  and say what you will assume if they do not answer.
- **Blocking on questions you could proceed past.** Do everything that does not
  depend on the answer first. Reserve a hard stop for cases where proceeding
  under any assumption would be unsafe or would make the work useless if wrong -
  money, permissions, deletion, public contracts.
- **Answering your own question and not writing it down.** If you decided, that
  is a decision: it goes to `memory/` or an ADR with its why.
- **The same question in two sessions.** This is a defect. Find where the first
  answer should have been filed, and file it now.

## Definition of done

- [ ] The layer was read; questions it answered were struck and cited.
- [ ] Surviving questions were asked in one grouped pass.
- [ ] Every answer is written into its taxonomy home in this batch.
- [ ] Deferred questions are recorded as Open questions with a date and what they
      block.
- [ ] Assumptions made in the absence of an answer are stated explicitly in the
      plan.
