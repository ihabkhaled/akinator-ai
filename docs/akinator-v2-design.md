# Akinator v2 - design

- **Status:** approved, not implemented
- **Date:** 2026-08-26
- **Approved by:** Ihab Khaled
- **Supersedes:** nothing. Extends v1; every v1 artifact keeps working.

> Spec location note: the brainstorming skill's default is
> `docs/superpowers/specs/`. This repository keeps narrative docs flat under
> `docs/` with `docs/README.md` as the index, and the `index-completeness`
> invariant only looks one level deep - a nested spec would be an unindexed
> artifact in the repo that ships the checker. Adopt, never impose: it lives
> here, indexed, per this repo's own convention.

## The problem v2 solves

v1 makes a change carry its knowledge. It does not make that knowledge
**findable at scale**, and it does not **learn**.

Two goals in the owner's brief are in direct conflict, and naming that conflict
is what this design is organized around:

- *"Document every single needle to the rocket"* is a **write** problem.
- *"A new chat knows everything in seconds"* is a **retrieval** problem.

Optimizing the first makes the second worse. Generating a document per library,
component, controller, service, hook and module produces a corpus no session can
read. v1 has no concept of a bounded, ranked context bundle, so more documents
would actively degrade the outcome the owner wants.

v2 separates the two: an unbounded **corpus**, and a hard-capped **brief** that
is what a session actually reads.

## Artifacts this design specifies

None of these exist yet. They are the output of the phases below, listed here
once so the rest of the document can refer to them without asserting that the
tree already contains them:

```
.ai/BRIEF.md                       the budget-capped context bundle
.ai/index.json                     the retrieval index
.ai/config.json                    tier and budget configuration
.ai/ledger/<type>/<id>.md          the event records
.cursor/rules/akinator.mdc         Cursor router
.github/copilot-instructions.md    Copilot router
```

## Goals

1. One command. `/akinator:everything` is the whole surface.
2. A new session reaches working context in seconds, from a generated brief.
3. Failures that recur become rules, automatically proposed and human-approved.
4. A rule that causes a new failure evolves into one that satisfies both.
5. Every AI entry-point file is generated from one contract; none can fork.
6. Questions asked and answers given become permanent, so nothing is asked twice.
7. Documentation effort is value-weighted, not uniform.

## Non-goals

Explicitly not built, and why:

- **A document per library.** It restates `package.json` and fails the
  delete-the-derivable test in `skills/akinator-anti-gaming/SKILL.md`. Replaced
  by one generated dependency map plus prose only where a choice or a scar
  exists.
- **A vector store or embedding index.** At this corpus size the brief plus grep
  is sufficient, and a stale index is worse than none.
- **A background daemon or watcher.** Everything runs inside the command.
- **Automatic resolution of rule conflicts.** Detected and reported; silently
  picking a winner between two constraints produces a system nobody trusts.
- **Per-component docs for components with no non-obvious behavior.**

## The pipeline

Five stages, one direction. Each has one purpose and a defined handoff.

```
/akinator:everything          the only command, change-scoped
        |
        v
 (1) CAPTURE -> (2) DISTIL -> (3) HARDEN -> (4) PROJECT -> (5) SURFACE
  what happened   what recurs   what binds   where it goes   what is read
  ledger events   rule/skill    evolution    11 routers      .ai/BRIEF.md
  failures, Q&A   proposals     + conflicts  + value docs    budget-capped
```

The ordering principle: **capture is cheap, surfacing is scarce.** Stages 1-4
may produce unlimited volume. Stage 5 has a hard token cap and everything
competes for a place in it.

---

## Stage 1 - CAPTURE

### Location

`.ai/ledger/<type>/<id>.md` - **committed to the repository.** A gitignored
local cache would defeat the entire purpose: a new clone, a new teammate or a
fresh CI agent would get nothing.

### Event types

| Type | Fields | Why it is not derivable from the tree |
|---|---|---|
| `failure` | `fingerprint`, `symptom`, `trigger`, `root_cause`, `fix`, `occurrences[]`, `sources[]` | The symptom and the cause are different facts; only whoever debugged it holds both |
| `question` | `asked`, `answer`, `answered_by`, `date`, `routed_to` | The answer exists only in a conversation that is about to be discarded |
| `decision` | `what`, `alternatives[]`, `why`, `cost_accepted`, `adr` | Rejected options never appear in a diff |
| `surprise` | `behavior`, `misleading_symptom`, `why` | The thing that cost three hours and looks obvious afterwards |

### symptom-as-first-observed

A `failure` record stores the symptom **as first seen**, not as understood
afterwards. A future agent arrives holding the symptom and needs to find the
record by it. A record indexed only by its root cause is unfindable by the
person who needs it.

### Failure signal sources - all three, cross-referenced

`sources[]` records where each occurrence came from:

- **`self-report`** - the agent noticed and recorded it during the session.
  Richest signal: it is the only source that carries the trigger and the
  misleading symptom. Depends on the agent being honest and attentive.
- **`git`** - revert commits, `fix:`-prefixed commits, repeated churn on one
  file within a window. Objective, shallow, after the fact.
- **`ci`** - test and check failure history. Objective and structured; blind to
  everything that never reached CI.

Cross-referencing is the point. Self-report is the rich signal; git and CI are
the **honesty check** on it. A `fix:` commit with no corresponding self-reported
failure is itself a finding: something broke and the session did not record it.

### Secret redaction - designed in, not bolted on

Failure records contain error text, and error text contains tokens, connection
strings and customer identifiers. Every record passes a redaction pass **before
write**:

- Known secret shapes (JWTs, AWS keys, connection strings, bearer tokens,
  private-key blocks, long high-entropy strings) are replaced with
  `[redacted:<kind>]`.
- Values matching anything in the repo's `.env*` files are replaced.
- The redaction pass is itself tested with a fixture of known secret shapes.

A ledger that leaks a credential into git history is worse than no ledger. This
is the one part of the design that cannot be added later.

---

## Stage 2 - DISTIL

### Fingerprinting

```
fingerprint = hash(error_class, touched_module, operation_kind)
```

Normalized, not raw text. Raw error text never matches twice - paths, line
numbers, ids and timings all differ. Too coarse and everything collides.

Tuning strategy: **start coarse, ask on collision.** When a new failure lands on
an existing fingerprint but the human says it is a different problem, the
fingerprint is split and the discriminator is recorded. The system learns its
own matching rule from real data rather than from a guess made up front.

This is the highest-risk component in v2 (see Risks).

### The threshold is 2

Once is an incident. Twice is a pattern. At the second occurrence, the pass
**stops** and asks:

> This has now happened twice - 2026-08-14 and 2026-08-26. Should it become a
> rule, a skill, or neither?

The proposal arrives **pre-drafted**: the rule text, an enforcement mechanism
that exists or can be written, and the test that would have caught it. The human
approves or edits; they do not author from blank.

**"Neither" is a valid answer** and is recorded, so it is never re-asked.

---

## Stage 3 - HARDEN

### Rule frontmatter

```yaml
id: 07
introduced_by: failure/quota-lost-update
supersedes: [04]
caused: [failure/migration-blocked-by-lint]
scope: "src/billing/**"
```

### Rule evolution - the mechanism the owner asked for

When rule A's **enforcement** is implicated in a new failure B, the system holds
both records: the constraint A protects, and the failure A caused. It synthesizes
**A'** satisfying both, marks A `superseded`, and links the chain forward.

The chain is the value. It is how the third agent understands why a rule is
shaped strangely - because the strange shape is the scar tissue from B.

A rule is never deleted. Superseded rules stay, marked, with a forward link.

### Conflict detection

Two rules conflict when their `scope` globs overlap **and** their mandates
disagree. Conflicts are **reported, never auto-resolved.** The resolution is a
human decision, recorded as an ADR, producing either a narrowed scope or a
synthesized replacement.

### Retirement

A rule whose `revisit_when` condition is met is surfaced in the brief as a
question, not silently dropped. Rules that accumulate without retirement become
noise, and noise gets suppressed wholesale.

---

## Stage 4 - PROJECT

### Routers - one contract, eleven adapters

| Target | Notes |
|---|---|
| `CLAUDE.md` | Claude Code |
| `AGENTS.md` | Codex, and the common fallback |
| `CODEX.md` | named-file convention |
| `GEMINI.md` | |
| `GLM.md`, `KIMI.md`, `QWEN.md`, `DEEPSEEK.md`, `MISTRAL.md` | |
| .cursor/rules/akinator.mdc | Cursor's own format |
| .github/copilot-instructions.md | |

All generated from one canonical contract by per-tool adapters that differ only
in path conventions and invocation syntax. All drift-checked.

The coverage checker already **detects** ten of these names; the generator
currently emits two. v2 closes generation to match detection.

Eleven hand-maintained routers would be eleven times the fork surface. They are
only safe because they are generated - this is `rules/07-codex-pack-is-generated.md`
applied at scale.

### Documents - value-weighted

```
value  ~=  rediscovery_cost  x  recurrence_probability  x  blast_radius
```

| Artifact | Value | Treatment |
|---|---|---|
| A library in `package.json` | ~0 - the library has docs | Row in the generated dependency map |
| Why that library over the alternative | high | ADR |
| What that library did to us at 3am | high | `failure` record, surfaced in the brief |
| A CRUD controller | low | Row in the generated component map |
| The controller with the non-obvious ordering constraint | high | Prose doc plus a rule |
| A business rule with a number in it | very high | `docs/business/`, per v1 |

**One generated map replaces N generated documents.** Facts about the tree are
extracted; prose is spent only where a choice or a scar exists.

---

## Stage 5 - SURFACE

### The brief

.ai/BRIEF.md - **generated, never hand-written, hard-capped.**

| Tier | Budget | For |
|---|---|---|
| `lean` | 4,000 | small repos, or per-token-sensitive teams |
| **`standard`** | **12,000 (default)** | carries the constraint set and the failure catalogue as content, not pointers |
| `deep` | 25,000 | large multi-service repos where boundaries alone are expensive |

Configured in .ai/config.json; `standard` unless set.

12k is roughly 1% of a 1M context window and 6% of 200k - cheap enough to load
every session, large enough that recurring failures appear as content rather
than as one-line pointers, which is what made a smaller budget feel thin.

### Composition, standard tier

| Section | Budget | Content |
|---|---|---|
| What this system is | 600 | Two paragraphs. Never more |
| Constraints that must not break | 2,500 | Active rules by scope, highest value first |
| Recurring failures and their fixes | 3,000 | `occurrences >= 2`, symptom-first |
| Business rules with numbers | 2,000 | Money, quotas, entitlements |
| Open questions blocking work | 1,000 | With what each blocks |
| Where to look for what | 1,400 | The retrieval map |
| Pointers into the corpus | 1,500 | Everything that did not fit |

Items compete on value score. Anything that does not fit becomes a one-line
pointer - it is not dropped, it is demoted.

### The retrieval index

.ai/index.json - generated. Per artifact: `kind`, `tags`, `token_cost`,
`last_verified`, `value_score`, `path`. This is what ranks the brief and what a
session greps when the brief points at something.

---

## Cost control

Two budgets, both enforced, because both have a hard human limit.

### Token budget

The brief's cap, above. Enforced at generation: if the composed brief exceeds
the tier, the lowest-value items demote to pointers until it fits. The
generator fails rather than emitting an over-budget brief.

### Interrupt budget

**Maximum 5 questions per session**, batched into one grouped ask, ranked by
value. The remainder go to `open-questions` and are asked next session.

Twenty questions in one session means zero answers by session three. The
interrupt budget is as real a constraint as the token budget, and v1 has no
concept of it.

### Change-scoping

`/akinator:everything` reads the diff and the ledger to decide which stations
have work. **"Everything" means every station, not every file.**

If a full pass costs the same on a typo as on a release, people stop running it.
That is how this discipline dies in every repository where it dies.

---

## Compatibility with v1

- Every v1 artifact keeps working. `rules/`, `skills/`, `docs/`, `memory/`,
  `context/` are unchanged in meaning.
- New rule frontmatter fields are **optional**. A rule without them behaves as
  today.
- `.ai/` is new and additive.
- The eleven-router fan-out replaces the two-router generation; `CLAUDE.md` and
  `CODEX.md` move from hand-maintained to generated, which is a behavior change
  for contributors and needs an ADR.
- Target repositories that have adopted v1 gain v2 by upgrading the plugin and
  running the command once; the ledger starts empty and fills.

---

## Testing strategy

Each stage gets mechanically verifiable invariants, because a stage that only
has prose enforcement is a stage that decays:

| Stage | Invariant |
|---|---|
| Capture | Redaction fixture: known secret shapes never reach a written record |
| Capture | Every ledger record parses and carries its required fields |
| Distil | Fingerprint stability: the same failure twice produces one record with `occurrences == 2` |
| Distil | Fingerprint discrimination: two different failures do not collide |
| Harden | A rule marked `caused` by a failure surfaces an evolution proposal |
| Harden | Overlapping scopes with disagreeing mandates are reported |
| Project | All eleven routers are generated and drift-checked |
| Project | Generated maps are deterministic |
| Surface | The brief never exceeds its tier budget |
| Surface | Every brief item resolves to a real artifact |

Mutation testing is mandatory for the new checks. This repository learned on
2026-08-26 that a checker validated only by running it on a healthy tree reports
green when it is broken - see
`memory/2026-08-26-checkers-fail-silently-in-both-directions.md`.

---

## Risks

| Risk | Mitigation | Residual |
|---|---|---|
| **Fingerprints never match twice, so nothing ever reaches the threshold** | Start coarse, ask on collision, learn the discriminator from real data | **High - the hardest part of v2** |
| Ledger leaks a secret into git history | Redaction before write, tested with a secret-shape fixture | Low if built in; catastrophic if deferred |
| Rule corpus becomes noise | Scope globs, supersession, retirement surfaced as questions | Medium |
| Corpus rot at N=1000 | Value score gates creation; only briefed items carry staleness checks | Medium |
| Brief goes stale | Regenerated every pass, drift-checked like the Codex pack | Low |
| Auto-proposed rules overfit to one incident | Threshold of 2, human approval, `scope` required on every synthesized rule | Medium |
| Eleven routers multiply the fork surface | All generated from one contract, none hand-edited | Low |
| The pass becomes too expensive to run | Change-scoping; interrupt budget; token budget | Medium |

---

## Implementation phases

Ordered by dependency, not by size. Each phase lands complete, gated once, with
its own knowledge delta.

| Phase | Delivers | Depends on |
|---|---|---|
| **1** | Router fan-out to eleven targets, all generated and drift-checked | nothing - independent, lowest risk, ships value immediately |
| **2** | The ledger: schema, redaction, write path, indexes | nothing |
| **3** | The brief: composition, budget enforcement, retrieval index | 2 (needs something to surface) |
| **4** | Distil: fingerprinting, recurrence counting, the stop-and-ask | 2 |
| **5** | Harden: rule frontmatter, evolution, conflict detection | 4 |
| **6** | Value-weighted docs: dependency and component maps, value scoring | 3 |
| **7** | Change-scoping and the interrupt budget | 1-6 |

Phase 1 first is deliberate: it is independent, mechanical, and proves the
generation pattern that phases 3 and 6 reuse.

The command rename to `/akinator:everything` rides along with phase 1.

## Related

- `docs/architecture.md` - v1, which v2 extends
- `docs/adr/0002-codex-pack-generated-from-claude-skills.md` - the generation
  pattern the router fan-out scales up
- `docs/adr/0006-index-completeness-as-its-own-invariant.md` - the checker
  discipline v2's new invariants must meet
- `memory/2026-08-26-checkers-fail-silently-in-both-directions.md` - why
  mutation testing is mandatory here
- `skills/akinator-anti-gaming/SKILL.md` - the test that rules out per-library
  docs

## Review when

- Any phase lands, to confirm the interfaces held.
- Fingerprint matching produces real data, which should change the tuning
  strategy from guess to evidence.
- Last verified: 2026-08-26.
