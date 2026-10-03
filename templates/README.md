# Templates

What Akinator writes into target repositories. Nineteen templates, each with a filled
example in `examples/`.

A template is a skeleton with placeholders. The example is the same document
filled in properly - particularly the sections that are usually left thin.

| Template | For | Example |
|---|---|---|
| [rule.md](rule.md) | A constraint others must not break, with a real enforcement mechanism | [example](examples/rule.md) |
| [skill.md](skill.md) | A repeatable procedure, with all six required parts | [example](examples/skill.md) |
| [context-map.md](context-map.md) | Structural facts, generated where possible | [example](examples/context-map.md) |
| [memory.md](memory.md) | One durable fact, with its why and reversal conditions | [example](examples/memory.md) |
| [adr.md](adr.md) | A decision, with its rejected options and their costs | [example](examples/adr.md) |
| [business-logic.md](business-logic.md) | Money and entitlement rules, in business language | [example](examples/business-logic.md) |
| [product-feature.md](product-feature.md) | Feature intent and the edge-case decision log | [example](examples/product-feature.md) |
| [ops-runbook.md](ops-runbook.md) | An operational procedure, with its point of no return | [example](examples/ops-runbook.md) |
| [router.md](router.md) | Thin CLAUDE.md / AGENTS.md / CODEX.md index skeletons | [example](examples/router.md) |
| [onboarding-mapping.md](onboarding-mapping.md) | Adopt-never-impose, recorded as a contract | [example](examples/onboarding-mapping.md) |
| [change-record.md](change-record.md) | One change: before, change, now, why, files, business meaning, operational consequence, rollback and knowledge delta | [example](examples/change-record.md) |
| [library-page.md](library-page.md) | One load-bearing dependency: generated facts, plus why we use it, how, what bit us and how to upgrade | [example](examples/library-page.md) |
| [requirement.md](requirement.md) | One requirements-register entry - current, changed, missing or dropped - with its source and append-only history | [example](examples/requirement.md) |
| [business-drift.md](business-drift.md) | One change of direction: before, after, why, who decided, impact, and every page it made untrue | [example](examples/business-drift.md) |
| [business-decision.md](business-decision.md) | One business decision: options with cost, the choice, its owner, money and entitlement impact, and when to revisit | [example](examples/business-decision.md) |
| [roadmap-item.md](roadmap-item.md) | One roadmap item: status, outcome wanted, why now, dependencies, requirement ids, risks and evidence of done | [example](examples/roadmap-item.md) |
| [data-store.md](data-store.md) | One database, cache or queue: purpose, schema home, retention, backup and restore, failure modes, readers, writers and cost | [example](examples/data-store.md) |
| [integration.md](integration.md) | One external service: what for, auth handling without secrets, limits, failure behaviour, cost, SLA and exit plan | [example](examples/integration.md) |
| [risk.md](risk.md) | One risk: statement, likelihood, impact even when tiny, signal, mitigation, owner and status | [example](examples/risk.md) |

All nineteen examples are written against **one** fictional product, so they
cross-reference each other the way real artifacts do. See
[examples/README.md](examples/README.md).

## Adopt, never impose

These are defaults, not requirements. When a target repository already has a
format for a kind of knowledge, use **its** format - its numbering, its
frontmatter, its index style - and record the mapping with
`onboarding-mapping.md`. Creating a parallel structure beside an existing one is
the most damaging thing this plugin can do to a repository.
