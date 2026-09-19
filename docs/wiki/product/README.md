# Product

What this answers: goals, users and personas, journeys, features, acceptance criteria.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## Who are the primary users, and what problem does this solve for them?

Teams building software with an AI coding agent doing most of the change
work - "AI-heavy teams" - on Claude Code, Codex or Cursor, at corporate scale
where a repository outlives any one contributor's memory (`docs/business-case.md`).
The problem: code outlives its context. The why, the business rules and the
rejected alternatives live in heads and chat scrollback and evaporate; a fresh
agent session is "a new hire every single morning" that infers confidently from
code and recovers *what* the system does while losing *what it should do*
(`docs/business-case.md`, "The problem").

## What core features does the product have?

From `README.md` and `docs/listing.md`:

- **One skill, one command, on every platform** - `skills/everything/`, invoked
  as `/akinator:everything` (Claude Code), `$akinator` (Codex), `/akinator`
  (Cursor); no separate onboard/audit/status/sync/question/decide commands
  (ADR 0009).
- **Always on** - a SessionStart hook (`hooks/hooks.json`) and platform-specific
  always-on blocks inject the contract before the first prompt, so an ordinary
  prompt runs the full pass with no command typed.
- **The living wiki** (2.0, ADR 0010) - a wiki home per kind of knowledge under
  `docs/wiki/`, with generated facts (`extract_libraries.py`, a page per
  dependency between `<!-- akinator:generated:begin/end -->` markers), curated
  why/how/pitfalls/upgrade sections kept byte for byte across regeneration, and
  honest gaps marked `_Unknown - ask the owner and record the answer._`.
  `akinator_wiki.py` (`init | index | gaps | check`) keeps the index honest and
  turns every gap into a question.
- **Decision superpowers** (`skills/everything/references/akinator-decide.md`) -
  with the full wiki context loaded, decide the reversible outright and
  recommend the rest with options, trade-offs and a recommendation.
- **Many questions, one message** - up to 15 per prompt by default
  (`.ai/config.json` `interrupt_budget`, `docs/scoping.md`), ranked and grouped,
  each with a recommended default, so "go with recommendations" is a complete
  answer.
- **The knowledge-delta contract** - every batch declares, by path, the docs,
  skills, rules, context and memory it will produce, before any code exists
  (`rules/01-knowledge-delta-per-batch.md`).
- **Boardroom review lenses** - 7 review agents in `agents/` (business owner,
  CTO, product owner, ops, analyst, PM, librarian) with real vetoes, per
  `docs/listing.md`.
- **A coverage checker** - `skills/everything/scripts/akinator_coverage.py`
  verifies eleven mechanically checkable invariants (unreachable artifacts, dead
  links, rules naming enforcement that does not exist, router forks, stale
  generated files, docs describing paths that are not there).
- **Gate economy** - the whole batch is built, then gated once at the end,
  scoped to what changed (`rules/06-gate-once-scoped-at-the-end.md`).
- **Adopt, never impose** - it detects a repository's existing conventions
  (routers, rules, docs folders) and extends them rather than creating a
  competing structure beside them.
- **One installer, no clone** - `install.sh` / `install.ps1` set up every
  detected platform in one line; re-running updates; `--uninstall` restores a
  host repository byte for byte.

## What journeys does a user go through?

- **Install** - one line (`install.sh` / `install.ps1`), or the manual
  per-platform routes, documented in `README.md` under "Install". The installer
  detects installed platforms, writes the skill, the always-on block or hook,
  and removes any per-station skill folders an earlier version left behind.
- **First prompt** - the user does not call Akinator; they prompt their agent
  normally ("add rate limiting to exports", "why is this service using
  Redis?"). The always-on contract runs the full loop automatically for any
  intent that can change the repository (`skills/everything/SKILL.md`).
- **Onboarding a repository** - `/akinator:everything onboard this repository`
  (or the always-on equivalent prompt): detects existing routers, rules and
  docs; maps onto them instead of replacing them; ranks gaps by severity; closes
  them in batches; finishes with the newcomer test (`docs/listing.md`, example
  2; `docs/business-case.md`, "What 'working' means").

## What are the acceptance criteria?

The newcomer test, stated in `docs/business-case.md` ("What 'working' means -
the measure"):

> A fresh agent, given only the knowledge layer, correctly answers - in seconds -
> where to go, what to do, what not to break, and what to run afterwards, for
> each of the repository's five most common change types.

Graded pass / partial / fail per `evals/README.md` (`evals/suites/04-newcomer.md`,
fixture `evals/fixtures/brownfield`). A confident-but-inferred answer is a fail;
the most dangerous result is the layer not answering and the agent not
noticing. Structural acceptance (does the plugin satisfy its own contracts) is
the test suite in `tests/`, run in CI on every push; behavioral acceptance
(does it change what an agent actually does) is the six suites in
`evals/README.md`, run before a release.

## What is not yet answered here

Quantified adoption or usage targets (how many repositories, how many
sessions) are not stated in the repository.

_Unknown - ask the owner and record the answer._
