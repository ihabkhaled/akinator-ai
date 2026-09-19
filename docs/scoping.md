# Change-scoping and the interrupt budget

Stage 7 of the v2 pipeline, and the one that decides whether the other six get
used.

If a full pass costs the same on a comment typo as on a release, people stop
running it. That is how this discipline dies in every repository where it dies -
not by being rejected, but by being too expensive to be worth invoking.

Run by `skills/everything/scripts/akinator_scope.py`.

## "Everything" means every station, not every file

Scoping **never skips a station**. It reports which stations have work.

A quiet station is still run; it simply finds nothing, and the batch records
`knowledge delta: none, because ...` in one line. The distinction matters: a
scoper that silently drops stations is an exemption engine, and the design
collapses into "document when convenient". A test asserts that awake plus quiet
always equals the whole loop.

Two stations are never scoped away:

- **RESOLVE** - a pass that skips it is guessing.
- **VERIFY** - a pass that skips it has no evidence.

```bash
python skills/everything/scripts/akinator_scope.py plan --against HEAD~1
```

```
AWAKE - these stations have work:
  RESOLVE     always - a pass that skips it is guessing
  OPS         deploy, migrate, restart, rebuild, recover
  ...
QUIET - nothing matched, so they will find nothing:
  BUSINESS    akinator-business-map
  PRODUCT     akinator-product-map
```

## What wakes what

| Station | Wakes on |
|---|---|
| BUSINESS | `docs/business/`, and paths naming billing, quota, pricing, payment, entitlement, refund, subscription |
| PRODUCT | `docs/product/`, routes, pages, components, handlers, controllers |
| OPS | migrations, Dockerfiles, compose files, Terraform, k8s, CI workflows, **and lockfiles** |
| CONTEXTIFY | dependency manifests |
| RULE | `rules/` |
| SKILLIFY | scripts, shell files, Makefiles |
| INDEX+SYNC | any knowledge artifact created, moved or deleted |

**A lockfile wakes ops** because a dependency change is an operational
consequence: it needs a rebuild rather than a restart, and the layer cache will
otherwise serve the old dependency set while the failure looks like something
else entirely.

## Trivial changes

Lockfile-only, image-only and ignore-file-only changes are marked trivial. That
describes **the work found, not permission to skip looking** - every station
still runs, and the batch states the empty delta explicitly.

## The interrupt budget

```bash
python skills/everything/scripts/akinator_scope.py questions
```

Up to **15 questions per prompt** by default (ADR 0010 raised it from 5 at the
owner's request), batched into ONE grouped ask, ranked, each with a recommended
default so "go with recommendations" is a complete answer. The rest are deferred
to the next prompt, not discarded. Lower it per repository with
`interrupt_budget` in `.ai/config.json`.

The budget still matters: it is what keeps fifteen questions one message instead
of fifteen interruptions. Scattered questions get ignored; one ranked battery
with defaults gets answered.

Ranking, highest first:

1. Money, permissions, deletion and public contracts - where guessing is
   prohibited outright.
2. A failure at the recurrence threshold with no recorded decision. More
   occurrences rank higher, because a thing that happened five times will happen
   a sixth.
3. Open questions carried from earlier sessions.

A recorded decision - **including `neither`** - removes the question
permanently. That is the whole point of recording it.

Configure in `.ai/config.json`:

```json
{ "brief_tier": "standard", "interrupt_budget": 5 }
```

## Related

- Docs: `docs/brief.md` - the other budget
- Docs: `docs/distil.md` - where the recurrence questions come from
- Docs: `docs/akinator-v2-design.md` - cost control
- Rules: `rules/06-gate-once-scoped-at-the-end.md` - the same principle for gates
- Code: `skills/everything/scripts/akinator_scope.py`, `tests/test_scope.py`

## Review when

- A station's globs miss something they should have caught - that is a real
  finding, and the fix is a glob plus a test.
- The interrupt budget proves wrong in practice, in either direction.
- Last verified: 2026-08-26.
