# ADR 0010 - Every prompt documented: the repository is its own wiki

- **Status:** accepted
- **Date:** 2026-09-19
- **Deciders:** Ihab Khaled (owner)
- **Supersedes, in part:** the five-question interrupt budget of `docs/scoping.md`
  and the "no document per library" stance of the stack map
  (`skills/everything/scripts/extract_stack.py`).

## Context

The owner's requirement, for corporate use at scale: every prompt and every
change is documented - product goals, business rules and drift, requirements
(current, changed, missing), libraries and stack, architecture, infra, testing
and UAT, UX and design, project status, decisions, market - so that any AI
reading the repository knows it "from the needle to the rocket" and can decide
or recommend with evidence. Every prompt should also ask the owner many
questions. All of it inside the one skill and the one command.

Two earlier decisions pointed the other way. The interrupt budget capped
questions at five per session ("twenty questions means zero answers"), and the
stack map refused a page per library because a page restating `package.json`
rots and buries the pages that carry knowledge.

## Options

### Option A - keep both caps; document only what the value formula ranks high

- **Cost:** the owner's requirement is refused. A repository that documents only
  "high-value" facts leaves exactly the gaps a fresh agent falls into.
- **Why it lost:** it optimises the writer's effort against the owner's explicit
  goal.

### Option B - document everything, as prose, by hand

- **Cost:** hundreds of hand-written pages that restate the tree and rot on the
  next commit - the stale-doc failure this plugin exists to prevent.
- **Why it lost:** volume without truth is worse than absence, because it is
  trusted.

### Option C - document everything; generate the facts, curate the why, mark the gaps (chosen)

- **What it is:** a living wiki with one home per kind of knowledge, adopted from
  the repository's existing structure where one exists:
  - **Facts are generated.** `extract_libraries.py` writes a page per dependency
    - version, kind, manifests, the files that use it - between generated
    markers; `akinator_wiki.py index` rebuilds the wiki home. Generated facts
    cannot rot, because they are regenerated.
  - **Why is curated.** Every page carries the sections only a person knows -
    why this library, pitfalls, business meaning - kept byte for byte across
    regeneration.
  - **Gaps are honest.** An unknown is the exact marker
    `_Unknown - ask the owner and record the answer._`; `akinator_wiki.py gaps`
    turns every marker and every missing category into a question.
  - **Requirements and drift are records.** The ledger gains `requirement`
    (current / changed / missing / dropped) and `drift` (before / after / why),
    and the context brief ranks them first.
  - **Questions are many, and cheap to answer.** Up to fifteen per prompt, in
    one ranked message, each with a recommended default, so "go with
    recommendations" is always a complete answer.
- **Cost:** more files in every repository, and a longer pass per prompt. The
  generated/curated split and the gap markers are what keep that volume true.

## Decision

Option C, inside the one skill: a new station reference, `akinator-wiki`
(document every prompt everywhere it lands), and `akinator-decide` (with the
full context loaded, decide the reversible and recommend the rest with options,
trade-offs and a recommendation).

## Consequences

**Good.** A fresh agent, or a new teammate, reads one wiki and knows the
product, the business, the requirements that changed and the ones still
missing, the libraries and why they were chosen, and every decision and its
reason. Questions become answers the same prompt, and answers become documents.

**Bad.** Fifteen questions is a lot. The ranking, the grouping and the
recommended defaults are what make it answerable; a repository can lower the
budget in `.ai/config.json`.

**Bad.** Library pages multiply with dependencies. Their facts are generated, so
they do not rot; their curated sections start as gaps, which is honest but can
look unfinished until the owner answers.

## Revisit when

- Owners routinely answer "go with recommendations" to most questions - then the
  default budget is too high for the value it returns.
- Curated library sections stay gaps for months - then the page-per-library
  default should be narrowed to runtime dependencies.

## Related

- Skill: `skills/everything/references/akinator-wiki.md`,
  `skills/everything/references/akinator-decide.md`
- Tools: `skills/everything/scripts/extract_libraries.py`,
  `skills/everything/scripts/akinator_wiki.py`
- Docs: `docs/ledger.md`, `docs/brief.md`, `docs/scoping.md`
