# The brief

`.ai/BRIEF.md` is what a new session reads first. It is **generated, never
written by hand, and hard-capped.**

## The conflict it resolves

v1 never named this, and it is the reason more documentation was making things
worse rather than better:

- *"Document every needle to the rocket"* is a **write** problem.
- *"A new chat knows everything in seconds"* is a **retrieval** problem.

Optimizing the first degrades the second. A corpus large enough to hold
everything is a corpus no session can read. So v2 splits them: the **corpus is
unbounded**, and the **brief is capped**. Items compete for a place in it.

```
corpus (unbounded)  ->  value ranking  ->  .ai/BRIEF.md (capped)
                                       ->  .ai/index.json (complete)
```

## Budget tiers

| Tier | Tokens | For |
|---|---|---|
| `lean` | 4,000 | small repos, or teams paying per token every session |
| **`standard`** | **12,000** | the default - carries constraints and recurring failures as content, not as pointers |
| `deep` | 25,000 | large multi-service repos where the boundaries alone are expensive |

Set in `.ai/config.json`:

```json
{ "brief_tier": "standard" }
```

12,000 tokens is roughly 1% of a 1M context window and 6% of 200k - cheap enough
to load every session, large enough that recurring failures appear as content
rather than as one-line pointers.

## The contract

**The brief is capped. The index is complete.**

Items that do not fit their section's allowance are **demoted to pointers**, not
dropped. Pointers are budgeted too - an unbudgeted pointer list blew the very cap
it existed to protect, which a test caught by forcing 40 rules through a
900-token budget. When even the pointer list overflows, the tail is summarized
into a count and `.ai/index.json` carries every ranked item with its score,
token cost and path.

**The generator refuses to emit an over-budget brief.** A cap that is allowed to
slip is not a cap, and every other claim in this design rests on it.

## Value ranking

```
value  ~=  rediscovery_cost  x  recurrence_probability  x  blast_radius
```

Multiplicative, so any factor at zero zeroes the item. Two consequences that
shape the whole corpus:

- **A per-library doc scores near zero.** The library has documentation and ours
  would restate it. The *reason we chose it*, and *what it did to us at 3am*,
  score high.
- **Recurrence is the multiplier that matters.** A failure seen three times will
  happen a fourth, so it outranks every rule in the brief - which is exactly
  what a session needs warning about before it starts.

## Sections

| Section | Share | Content |
|---|---|---|
| What this system is | 5% | Two paragraphs, from the router contract. Never more |
| Constraints that must not break | 19% | Rules, enforced ones ranked above prose-only ones |
| Recurring failures and their fixes | 21% | From the ledger, symptom-first |
| Business rules with numbers | 14% | Money, quotas, entitlements |
| Requirements - current, changed and missing | 10% | `requirement` records from the ledger: **missing first, then changed, then current**, then dropped |
| Business and product drift | 7% | `drift` records from the ledger: before, after, why, and impact when recorded |
| Open questions blocking work | 7% | Asked and answered, so neither is asked again |
| Where to look for what | 8% | The retrieval hops |
| Everything else, by pointer | 9% | Demoted items, then a summarized count |

The shares sum to 1.0, and a test asserts it - a section table that quietly does
not add up is a cap that silently slips. Requirements and drift were carved out
of the other sections rather than added on top: the tier did not grow, so every
token they carry is one something else no longer does.

### Requirements and drift

A requirement's rank is set by its status alone, strictly decreasing, so the
section always reads in the order a session needs: what is **missing** blocks
work, what **changed** invalidates work already done, what is **current** is the
contract, and what was **dropped** is listed so it is not rebuilt. A record with
a status the ledger rejects still reaches the index - demoted, never dropped -
ranked below every valid one, and `akinator_ledger.py verify` flags it.

Drift is ranked by area: `business` and `pricing` carry the widest blast radius,
because building on an old money fact is the most expensive mistake, then
`product`, `requirement` and `scope`, then `architecture`, then anything else.

An empty section says `_nothing recorded yet_`. The brief never invents a
requirement to fill one.

## Using it

```bash
python skills/everything/scripts/build_brief.py --write     # regenerate
python skills/everything/scripts/build_brief.py --check     # exit 1 if drifted (CI runs this)
python skills/everything/scripts/build_brief.py --explain   # the ranking, and what fit
```

`--explain` is the one to reach for when something you expected is missing: it
prints every candidate with its score, token cost and whether it made the cut.

## Related

- Docs: `docs/ledger.md` - where the recurring failures, requirements and drift come from
- Docs: `docs/akinator-v2-design.md` - stage 5, SURFACE
- Code: `skills/everything/scripts/build_brief.py`, `tests/test_brief.py`

## Review when

- A section share changes, or a new section is added.
- The requirement statuses or the drift area weights change.
- The token estimate proves badly calibrated against a real tokenizer.
- Last verified: 2026-09-19.
