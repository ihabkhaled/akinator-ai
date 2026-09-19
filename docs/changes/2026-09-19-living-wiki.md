# Change - Every prompt documented: the living wiki

- **When:** 2026-09-19
- **Actor / agent:** Claude Code coding agent - Claude Sonnet 5 - on behalf of Ihab Khaled
- **Request / source:** the owner: corporate-scale knowledge - product, business,
  market, requirements, drift, architecture, libraries, stack, infra,
  testing/UAT, UX, project management, decisions - so any AI reading the repo
  knows everything and can decide or recommend, with many questions per prompt
- **Status:** implemented; released as 2.0.0

## Before

Akinator documented what the value formula ranked high, and asked at most five
questions per session. A library was a line in the stack map, not a page; a
requirement that changed silently had no record; drift between what the code
does and what the docs say had nowhere to go. The five-question cap protected
attention at the cost of the owner's actual requirement: exhaustive,
corporate-scale knowledge that a fresh AI or teammate could stand on without
asking the owner again.

## Change

Still one skill, one command, always on. Added two station references -
`akinator-wiki` (document every prompt everywhere it lands) and
`akinator-decide` (decide the reversible, recommend the rest, with the full
context loaded) - and two tools: `extract_libraries.py` (a page per dependency
under `docs/wiki/libraries`, facts generated between
`<!-- akinator:generated:begin/end -->` markers, curated why/how/pitfalls/
upgrade sections kept byte for byte across regeneration) and `akinator_wiki.py`
(`init | index | gaps | check` - a wiki home per kind of knowledge at
`docs/wiki/index.md`, adopting an existing home where the repository already
has one, turning every gap and homeless category into a question). The ledger
gained two record kinds: `requirement` (statement, status
current/changed/missing/dropped, source) and `drift` (area, before, after,
why), both surfaced in the context brief. Raised the question budget from five
to fifteen per prompt, delivered as one grouped, ranked message where every
question carries a recommended default, so "go with recommendations" is always
a complete answer. Added three templates: `library-page`, `requirement`,
`business-drift`. Ran the new tooling over Akinator's own repository, so
`docs/wiki/` now documents Akinator under its own discipline.

## Now

A fresh agent reads `docs/wiki/index.md` and reaches the product, business,
requirements (current, changed, missing, dropped), drift, architecture,
libraries, stack, infra, testing/UAT, UX, project status and decisions - each
with generated facts where they can be generated and an honest
`_Unknown - ask the owner and record the answer._` marker where they cannot.
Every prompt that touches any of it re-runs `akinator_wiki.py index` and
`extract_libraries.py --write` in the same batch, so the wiki never trails the
tree it describes.

## Why

The owner's requirement is exhaustive, structurally-guaranteed knowledge, not a
value-ranked subset of it. Generating the facts and curating only the why is
the only way to reach that volume without shipping pages that restate
`package.json` and rot on the next commit - the same failure the stack map was
built to avoid, now solved by the generated/curated split instead of by
refusing the page.

## Technical reasoning

`extract_libraries.py` reuses the stack map's per-ecosystem manifest and usage
detectors so a library page's generated block is exact, not guessed, and
re-running it is idempotent - `test_check_is_silent_when_current`. Curated
sections survive regeneration byte for byte because the writer parses the
existing page's curated headings before rewriting only the block between the
markers - `test_curated_text_survives_regeneration_byte_for_byte`.
`akinator_wiki.py` adopts an existing folder or README section as a category's
home instead of creating a duplicate, so a repository that already has
`docs/product/` keeps it - `test_an_existing_product_folder_is_linked_not_duplicated`.
Every unresolved marker and every homeless category becomes exactly one
question, so the gap detector and the question budget share one source of
truth instead of drifting apart.

## Compatibility / migration / rollback

Additive: existing routers, skills and the ledger schema are unchanged except
for the two new record kinds, which are optional fields nothing else requires.
A repository on 1.2.0 keeps working with a five-question budget until it
re-runs Akinator, which now emits fifteen by default; the budget is lowered
back in `.ai/config.json` per ADR 0010's revisit condition. Rollback: revert to
the 1.2.0 release; no destructive migration is involved because `docs/wiki/`
is new, generated content.

## Knowledge delta

- ADR: `docs/adr/0010-every-prompt-documented-living-wiki.md`
- Skill: `skills/everything/references/akinator-wiki.md`,
  `skills/everything/references/akinator-decide.md`
- Rules: `rules/13-every-prompt-is-documented.md`
- Docs: `docs/wiki/`, `docs/ledger.md`, `docs/brief.md`, `docs/scoping.md`,
  `CHANGELOG.md`
- Templates: `templates/examples/library-page.md`,
  `templates/examples/requirement.md`, `templates/examples/business-drift.md`
- Memory: `memory/2026-09-19-document-every-prompt.md`
- Tests: `tests/test_wiki.py`, `tests/test_libraries.py`

## Verification

- `python -m pytest tests/test_wiki.py tests/test_libraries.py -q` - both
  suites pass, including the mutation-shaped checks
  (`test_check_fires_on_a_stale_generated_block`,
  `test_a_broken_block_is_refused_not_guessed`).
- `python skills/everything/scripts/akinator_coverage.py . --strict` - run
  after every file in this batch's knowledge delta.

## Future

Watch whether owners routinely answer "go with recommendations" (ADR 0010's
first revisit condition) and whether curated library sections stay gaps for
months (its second); either narrows the defaults.

## Stale when

The taxonomy of knowledge kinds changes, the ledger schema changes shape, or a
platform changes how many questions fit in one message.
