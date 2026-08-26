# Templates

What Akinator writes into target repositories. Ten templates, each with a filled
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

All ten examples are written against **one** fictional product, so they
cross-reference each other the way real artifacts do. See
[examples/README.md](examples/README.md).

## Adopt, never impose

These are defaults, not requirements. When a target repository already has a
format for a kind of knowledge, use **its** format - its numbering, its
frontmatter, its index style - and record the mapping with
`onboarding-mapping.md`. Creating a parallel structure beside an existing one is
the most damaging thing this plugin can do to a repository.
