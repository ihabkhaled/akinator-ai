<!--
Akinator behavioral contract - GENERATED, DO NOT EDIT BY HAND.

Inside an Akinator checkout: regenerate with `build_codex_pack.py`.
Installed in another repository: reinstall to update. Local edits here
are replaced - keep this repository's own content in its own router.
-->

# Akinator

Ask everything. Document everything. Skillify everything. Rule everything.

A change is never the code alone. A change is the code plus the knowledge that lets
the next agent act on it in seconds. Half a change is no change.

## The loop

Run every codebase touch through twelve stations:

```
ASK -> RESOLVE -> AUDIT -> PLAN -> IMPLEMENT -> DOCUMENT ->
SKILLIFY -> RULE -> CONTEXTIFY -> MEMOIZE -> INDEX+SYNC -> VERIFY
```

Non-negotiable:

- Stations 6-11 happen in the same batch as station 5. "I'll document in a
  follow-up" is a prohibited sentence.
- The knowledge delta is declared at PLAN time, **by path**, per batch. A batch
  with no knowledge delta states why, explicitly.
- Gate once, at the end, scoped to what was touched. Never per edit, never per
  commit, never all-workspace.
- Never add knowledge or documentation checks to git hooks. Hooks gate code.
- **Adopt, never impose.** Match this repository's existing conventions before
  creating anything. A parallel structure beside an existing one is worse than
  no structure - the agent picks the wrong one half the time.
- Never guess on money, permissions, deletion or public contracts. Stop, ask,
  and write the answer down before coding past it.

## Station 2 - RESOLVE, before anything

Discover what this repository actually has, then read it in this order,
stopping when your question is answered:

```
routers   CLAUDE.md, AGENTS.md, CODEX.md, and any per-module ones
rules     constraints you may not break
skills    runbooks - follow one rather than improvising
context   structural facts: ownership, routes, events, permissions
memory    durable decisions, preferences, surprises
docs      architecture, business, product, ops, decision records
```

Those are the conventional homes, not a promise about this repo. Look first;
this repository may use different names, and if it does, **its** names win.

If none of them exist, say so rather than inventing a structure, and offer to
onboard the repository properly.

## Skills

Installed under `.agents/skills/`. Invoke one explicitly with `$<name>`, or
describe the task and let the skill be selected by its trigger.

| Skill | Use when |
|---|---|
| `akinator` | Use when touching a codebase in any way - planning, exploring, auditing, refactoring, implementing, fixing, upgrading, deleting or documenting. |
| `akinator-adr` | Use when a decision was made between real alternatives that will be questioned later - a library or vendor choice, an architectural boundary, a data model, a protocol, a build-versus-buy call, a deliberate tradeoff. Records context, the options considered, the decision, its consequences and when to revisit it. |
| `akinator-anti-gaming` | Use when reviewing whether documentation work is real, when a checklist is about to be ticked, when tempted to weaken a failing check, or when a batch's knowledge delta looks complete but thin. Catches fake compliance - vacuous docs, copy-paste skills, rules with no enforcement, claimed coverage - which is worse than absence because it is trusted. |
| `akinator-audit` | Use before planning work on anything claimed to already exist, when a doc or ticket says a feature is done, when inheriting unfamiliar code, or when a request assumes a capability is wired up. Compares claim against code and returns done, partial or missing per item, catching the present-is-not-wired failure. |
| `akinator-business-map` | Use when work touches money, plans, pricing, quotas, entitlements, limits, trials, refunds, proration, discounts, taxes or anything a customer is charged or granted. |
| `akinator-contextify` | Use when a change alters a structural fact about the system - ownership, module boundaries, routes, ports, events, permissions, environment variables, dependencies or data flow. Updates the structural map and, wherever the fact is extractable from the tree, builds the extractor so the map regenerates instead of drifting. |
| `akinator-coverage` | Use to audit whether a repository's knowledge layer is complete, reachable and true - before claiming onboarding is done, when docs are suspected of being stale, periodically as a health check, or when a fresh agent gets lost in a repo that is supposedly documented. |
| `akinator-document-change` | Use in the same batch as any code change, before the batch is called done. |
| `akinator-everything` | Use when the user explicitly asks for everything - "run the full akinator", "do all of it", "maximum depth", "leave nothing out", "the complete pass" - or before a release, an audit, a handover, or any change too expensive to get wrong. Loads and applies every station, every boardroom lens and every mechanical check, and does not stop until the Definition of Done is proven rather than asserted. |
| `akinator-gate-economy` | Use before running any lint, typecheck, test or build, and before any commit or push during multi-step work. Enforces batch-first gate-last discipline - gates run once at the end, scoped to what was touched - and prevents paying twice for the same proof. |
| `akinator-index-sync` | Use whenever a knowledge artifact is created, renamed, moved or deleted - a rule, skill, doc, context map, ADR or memory entry. Makes every artifact reachable from an index and removes index entries pointing at things that no longer exist. |
| `akinator-intake` | Use before planning any substantive work, and whenever a request has two readings that lead to materially different work, or when implementation forces a product decision no document answers. |
| `akinator-memoize` | Use when a session produces a durable fact worth carrying forward - a decision made without an ADR, an owner preference, a surprise, a dead end, a non-obvious constraint discovered the hard way. |
| `akinator-onboard` | Use when installing Akinator's standing behavior into a repository for the first time, when a repo has no knowledge layer and an agent keeps re-deriving the same context, or when asked to onboard, bootstrap or set up documentation structure for a codebase. Detects what already exists, maps onto it rather than replacing it, ranks the gaps and closes them in batches. |
| `akinator-ops-map` | Use when a change alters how the system is deployed, migrated, restarted, rebuilt, recovered or rolled back - schema changes, dependency changes, config changes, service topology changes. |
| `akinator-plan` | Use before implementing anything that touches more than one file or takes more than one step. |
| `akinator-product-map` | Use when building, changing or removing a user-facing feature. Captures the feature's intent, its users, its acceptance criteria, its edge-case decision log, its non-goals and its open questions, so the reason a feature behaves the way it does survives the ticket that created it. |
| `akinator-resource-guard` | Use before starting anything heavy - a build, a test suite, a container rebuild, a long-running process - and at the end of every task. Checks CPU and memory pressure, reduces your own load rather than the developer's, and leaves the machine as you found it. |
| `akinator-router-sync` | Use whenever a change alters what an AI entry-point file should say - CLAUDE.md, AGENTS.md, CODEX.md, GEMINI.md, cursor rules, or any per-module router. Updates every router in the same change so no tool reads a different version of the truth, and keeps routers thin indexes rather than mirrors. |
| `akinator-rule-forge` | Use when a change establishes a constraint others must not break - an invariant, a forbidden pattern, a required call path, a boundary. |
| `akinator-skillify` | Use when a procedure was worked out during a task - a debugging path, a deployment sequence, a migration recipe, a setup dance, a diagnostic order. |

Start with `$akinator` - it carries the full creed, the loop and the
knowledge taxonomy, and routes to the rest.
