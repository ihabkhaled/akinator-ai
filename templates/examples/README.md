# Filled template examples

Every template in `templates/` has a filled example here. They are all written
against **one** fictional product, so they cross-reference each other the way
real artifacts do - the rule cites the ADR, the business doc names the code the
rule protects, the runbook fires from the skill.

## The fictional product

**Nimbus** - a team workspace SaaS.

- Plans: Free, Starter, Pro.
- Teams have **seats** (members) and a monthly **export quota**.
- Billing runs through a payment provider; refunds are possible mid-period.
- Deployed as containers: `api`, `worker`, `exports`, `postgres`.

That is enough shared context for the examples to be concrete. None of it exists
in this repository - these are illustrations of shape and depth, not claims
about Akinator itself.

## The examples

| Example | Template | Shows |
|---|---|---|
| [rule.md](rule.md) | `templates/rule.md` | A constraint with a real, existing enforcement mechanism |
| [skill.md](skill.md) | `templates/skill.md` | A runbook-firing skill with parallel-vs-sequential steps |
| [context-map.md](context-map.md) | `templates/context-map.md` | A generated map with an extractor and a drift check |
| [memory.md](memory.md) | `templates/memory.md` | A single durable fact with reversal conditions |
| [adr.md](adr.md) | `templates/adr.md` | A decision with two real options and its costs |
| [business-logic.md](business-logic.md) | `templates/business-logic.md` | Money rules in business language, with open edge cases |
| [product-feature.md](product-feature.md) | `templates/product-feature.md` | Feature intent with a populated edge-case decision log |
| [ops-runbook.md](ops-runbook.md) | `templates/ops-runbook.md` | Migration procedure with a point of no return |
| [router.md](router.md) | `templates/router.md` | A thin root router that indexes rather than mirrors |
| [onboarding-mapping.md](onboarding-mapping.md) | `templates/onboarding-mapping.md` | Adopt-never-impose recorded as a contract |
| [change-record.md](change-record.md) | `templates/change-record.md` | Before, change and now for one fix, with intent and verification |
| [library-page.md](library-page.md) | `templates/library-page.md` | A library's generated facts beside its curated why, pitfalls and an honest gap |
| [requirement.md](requirement.md) | `templates/requirement.md` | A changed requirement with its source, append-only history and a missing sibling |
| [business-drift.md](business-drift.md) | `templates/business-drift.md` | A change of direction, the requirements it moved and the pages it corrected |

## How to read them

Read the example next to its template. The template says what each section is
for; the example shows what "good" looks like when the section is actually
filled - particularly the sections that are usually left thin:

- **Enforcement** in a rule - a path that exists, not a promise.
- **Failure modes** in a skill - the misleading symptom, not just the fix.
- **Edge cases OPEN** in a business doc - written down while still undecided.
- **The decision log** in a product doc - dated rows, appended, never edited.
- **Point of no return** in a runbook - the sentence that matters at 3am.
- **Reversal conditions** in a memory entry - what makes it prunable.
- **The gap marker** in a library page - an unknown written as one, never guessed.
- **The change history** in a requirement - the old wording kept, not overwritten.
- **Decided by** in a drift entry - the field that matters most a year later.
