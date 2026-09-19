# Project

What this answers: roadmap, milestones, status, risks.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## What is on the roadmap, which milestone is next, and what are the top delivery risks?

### Milestones, from `CHANGELOG.md`

| Version | Date | Theme |
|---|---|---|
| 1.0.0 | 2026-08-26 | First release: the loop, non-negotiables, taxonomy, Codex plugin validation fixes |
| 1.0.1 | 2026-08-26 | Verified installing and loading in Claude Code |
| 1.0.2 | 2026-08-26 | Additions and fixes following first-install verification |
| 1.1.0 | 2026-08-30 | (see `CHANGELOG.md` "## [1.1.0]" for the fixed/added/verified detail) |
| 1.2.0 | 2026-09-18 | One skill, one command, one installer; always-on work from PR #1 shipped together with what it got wrong (ADR 0009) |
| 2.0.0 | 2026-09-19 | The living wiki: every prompt documented everywhere it lands, decision superpowers, a 15-question budget, generated library pages, requirement and drift ledger records (ADR 0010) |

### Current status

Version 2.0.0, dated 2026-09-19 (this page). The one-skill, one-command,
always-on contract from 1.2.0 is unchanged in 2.0 - 2.0 adds the living-wiki
mandate on top of it (`docs/adr/0010-every-prompt-documented-living-wiki.md`,
Decision). The wiki structure (`docs/wiki/`) and its two new tools
(`extract_libraries.py`, `akinator_wiki.py`) are new in this release; the
requirements register and drift log on this page are their first population.

### Top delivery risks

- **Codex and Cursor routes are not verified live.** ADR 0009's own
  verification table marks the Codex row "from its docs and source" and the
  Cursor row "from its docs" - "neither run because neither is installed on
  the verifying machine." `CHANGELOG.md` 1.2.0 repeats this under "Not verified
  here" for the Codex plugin route specifically. Only the Claude Code row has
  live confirmation (2.1.154 and 2.1.276). This risk carries forward unchanged
  into 2.0 - nothing in ADR 0010 or this session's evidence closes it.
- **The plugin-directory listing is stale against the current release.**
  `docs/listing.md` "Review when" records last verification as 2026-09-18
  against 1.2.0, one release behind this page's 2.0.0 and predating the
  living-wiki work it should now describe.
- **Fifteen questions per prompt is unproven at scale.** ADR 0010's own
  "Consequences" names this directly: "Fifteen questions is a lot... a
  repository can lower the budget in `.ai/config.json`" if the ranking and
  defaults do not make it answerable in practice; "Revisit when" names owners
  routinely answering "go with recommendations" as the signal the budget is
  too high.
- **Curated library-page sections can look unfinished.** ADR 0010
  "Consequences": generated facts do not rot, but a curated why/pitfalls
  section starts as a gap marker and "can look unfinished until the owner
  answers." "Revisit when" names curated sections staying gaps for months as
  the signal to narrow the page-per-library default to runtime dependencies
  only.
- **The value-curve claim (second repo costs a tenth of the first) is
  unmeasured.** `docs/business-case.md` "Review when": "The newcomer test is
  run against a real target repository and produces data that contradicts or
  confirms the cost-curve claim" - not yet done as of the business case's own
  last-verified date (2026-08-26).

## What is not yet answered here

A dated roadmap beyond the shipped versions above (a public 2.1/3.0 plan, or a
target date for closing the Codex/Cursor verification risk) is not stated in
the repository.

_Unknown - ask the owner and record the answer._
