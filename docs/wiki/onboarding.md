# Onboarding

What this answers: how a newcomer, or a fresh agent, gets productive.

Part of the [project wiki](index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## How does a newcomer, or a fresh agent, get from clone to a verified first change?

**For a fresh agent:** read `.ai/BRIEF.md` first - it is what a new session is
meant to read before anything else, and it is capped to a token budget
(`.ai/config.json`'s `brief_tier`, currently `standard`) precisely so it stays
readable in one pass.

**For a human newcomer:**

1. **Clone** the repository.
2. **Run the tests** - `python -m pytest tests/ -q`. A clean run confirms the
   checkout is sound before anything else is trusted.
3. **Read `CLAUDE.md`** at the repo root - the router: where the rules,
   skills, agents, context, docs and memory live, and the command table for
   every generator and checker.
4. **Read `docs/wiki/index.md`** - the wiki home: every category of knowledge
   (product, business, market, requirements, drift, architecture, libraries,
   stack, infra, testing, UX, project, decisions, changes, glossary,
   onboarding), its canonical home, and its open-gap count.
5. **Make a change through the loop** - the one skill is
   `skills/everything/SKILL.md` (`/akinator:everything` on Claude Code,
   `$akinator` on Codex, `/akinator` on Cursor, and normally invoked by
   nothing at all, because it is always on from `SessionStart`). The full
   step-by-step pass is `skills/everything/references/procedure.md`; every
   batch declares a knowledge delta by path
   (`rules/01-knowledge-delta-per-batch.md`).
6. **Gates** - run the checks once, at the end of the batch, scoped to what
   was touched (`rules/06-gate-once-scoped-at-the-end.md`), never mid-batch
   and never in a git hook (`rules/05-no-git-hook-complication.md`):
   - `python skills/everything/scripts/akinator_coverage.py . --strict` - the
     tier CI runs
   - `python skills/everything/scripts/akinator_scope.py plan` - to scope the
     pass to the change first
   - the generators relevant to what changed: `akinator_ledger.py verify`,
     `build_brief.py --check`, `akinator_wiki.py check`,
     `extract_libraries.py --check`, `extract_stack.py --check`,
     `render_routers.py --check`, `build_codex_pack.py --check`

A first change is verified, not merely made, when the scoped coverage gate is
green and the knowledge delta for that batch is filed - not before.
