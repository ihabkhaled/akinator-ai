# Rule 13 - Every prompt is documented everywhere it lands

## Purpose

A repository that is "exhaustively documented" as of the last audit and silent
about the last ten prompts is not exhaustively documented - it is a snapshot
with a caption that lied the moment work resumed. The owner's requirement is
corporate-scale knowledge that a fresh AI or teammate can stand on without
asking again: product, business, market, requirements, drift, architecture,
libraries, stack, infra, testing/UAT, UX, project management, decisions. That
only holds if every prompt that touches any of it updates the wiki in the same
batch as the change, not in a later cleanup pass that never gets scheduled.

Decided in `docs/adr/0010-every-prompt-documented-living-wiki.md`.

## Applies to

- **In scope:** any prompt that changes a dependency, a requirement, an
  architectural decision, business or product behavior, infra, testing/UAT, UX,
  or project status - the wiki categories under `docs/wiki/`, the ledger's
  `requirement` and `drift` record kinds, and the context brief sections that
  surface them.
- **Out of scope:** a prompt scoped to nothing the wiki taxonomy covers - see
  `docs/scoping.md`, which reports a quiet station rather than skipping it, so
  "out of scope" is a recorded finding, not a silent skip.

## Mandatory rules

1. A batch that touches any wiki category updates its home in the same batch,
   not later - same-batch updates to the wiki page, its index, the routers, the
   relevant rule or memory entry, context, and the ledger.
2. A library page's facts are generated between
   `<!-- akinator:generated:begin -->` / `<!-- akinator:generated:end -->`
   markers; the curated why/how/pitfalls/upgrade sections are hand-written and
   survive regeneration byte for byte.
3. An unknown fact is recorded as the exact marker
   `_Unknown - ask the owner and record the answer._`, never guessed and never
   left blank. A blank field and a guessed field are both false claims of
   completeness; the marker is the only honest gap.
4. A requirement that changes, goes missing, or is dropped is recorded as a
   ledger `requirement` record (statement, status
   current/changed/missing/dropped, source) - not silently overwritten in
   place.
5. Behavior that diverges from what the docs say is recorded as a ledger
   `drift` record (area, before, after, why) - not left for the next reader to
   discover by running the code.
6. `docs/wiki/index.md` is regenerated whenever a category is added, adopted,
   or gains a page, so the index never trails the tree it indexes.

## Prohibited patterns

```
docs/wiki/libraries/react.md
```
```markdown
# react

18.3.1. Used everywhere.
```

No generated markers, no curated sections, no source - a hand-typed fact that
rots on the next `package.json` bump and nobody will notice.

```markdown
## Why this library

TODO
```

A blank placeholder reads as "answered and there is nothing to say." It is not
the honest-gap marker, and `akinator_wiki.py gaps` will not turn it into a
question.

## Correct pattern

```markdown
<!-- akinator:generated:begin -->
- **Version:** 18.3.1
- **Kind:** runtime dependency
- **Manifests:** `package.json`
- **Used in:** `src/App.tsx`, `src/components/*.tsx` (41 files)
<!-- akinator:generated:end -->

## Why this library

_Unknown - ask the owner and record the answer._

## Pitfalls

_Unknown - ask the owner and record the answer._
```

Generated facts that cannot rot because they are regenerated; curated sections
that are either answered or honestly marked as a gap `akinator_wiki.py gaps`
will surface as a question.

## Enforcement

- Mechanism: `tests/test_wiki.py` - covers `akinator_wiki.py init | index |
  gaps`: every homeless category and every unresolved marker becomes one
  question, an existing home is adopted rather than duplicated, and the index
  is current on a fresh repo.
- Mechanism: `tests/test_libraries.py` - covers `extract_libraries.py`:
  generated facts are exact per ecosystem, curated text survives regeneration
  byte for byte (`test_curated_text_survives_regeneration_byte_for_byte`), and
  a broken generated block is refused rather than guessed
  (`test_a_broken_block_is_refused_not_guessed`).
- Mechanism: `skills/everything/scripts/akinator_wiki.py check` - exits nonzero
  when the wiki index is stale against the tree it indexes; run in CI.
- Mechanism: `skills/everything/scripts/extract_libraries.py --check` - exits
  nonzero when a library page's generated block has drifted from the manifests
  and usage it describes; run in CI.
- Mechanism: `agents/akinator-librarian.md` - the boardroom review that vetoes
  a batch whose declared knowledge delta, wiki included, was not delivered.
- Type: unit tests, CI step, review agent.
- How it fails: `check` names the stale page or the missing home; the review
  blocks completion and names what is missing.
- Last observed passing: 2026-09-19

**Never a git hook** - see `rules/05-no-git-hook-complication.md`.

## Exceptions

A prompt that is genuinely out of every wiki category's scope needs no wiki
update - recorded as a quiet station in `akinator_scope.py plan`, not a silent
skip. There is no exception for a prompt that is in scope but inconvenient to
document; volume without truth is the rejected option in ADR 0010, and skipping
this rule under time pressure produces exactly that.

## Related

- ADR: `docs/adr/0010-every-prompt-documented-living-wiki.md`
- Skill: `skills/everything/references/akinator-wiki.md`,
  `skills/everything/references/akinator-decide.md`
- Docs: `docs/wiki/`, `docs/ledger.md`, `docs/brief.md`, `docs/scoping.md`
- Memory: `memory/2026-09-19-document-every-prompt.md`
- Rules: `rules/01-knowledge-delta-per-batch.md` - the same discipline, one
  level up: the delta is declared before code exists; this rule is what the
  wiki categories owe that delta
- Rules: `rules/12-artifacts-that-travel-name-nothing-local.md` - a library
  page's generated block names its source the same way a travelling artifact
  must: by description and refresh path, never by an unverifiable claim

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] The enforcement mechanism exists in the tree and is named by path.
- [x] The mechanism is not a git hook.
- [x] Prohibited and correct patterns are shown, including the near-miss form.
- [x] The exception path is named.
- [x] The rule is indexed and reflected in every router.
