# Requirements

What this answers: the requirements register - current, changed, missing.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## What are the current requirements, which changed recently, and which are known to be missing?

Register of the owner's stated requirements, each also recorded as a
`requirement` ledger record (`python skills/everything/scripts/akinator_ledger.py
list --type requirement`). Status values follow the ledger's fixed vocabulary:
`current`, `changed`, `missing`, `dropped`.

| Statement | Status | Source |
|---|---|---|
| Exactly one skill and one command surface on every platform - `/akinator:everything` (Claude Code), `$akinator` (Codex), `/akinator` (Cursor) | current | ADR 0009; `README.md` |
| Akinator is always on - no command normally needs to be typed | current | ADR 0008; `docs/adr/0009-one-skill-one-command-one-installer.md`; `README.md` |
| Install in one line, with no marketplace required | current | `README.md`, "One line (recommended)"; ADR 0009 Decision 4 |
| Every prompt is documented everywhere it lands - the repository is its own wiki | current | ADR 0010; `docs/wiki/` |
| Many questions per prompt, grouped and ranked, each with a recommended default | current | ADR 0010; `docs/scoping.md` |
| Facts are generated, why is curated, gaps are honest and marked | current | ADR 0010; `skills/everything/scripts/extract_libraries.py`, `akinator_wiki.py` |
| The host-repo tools travel with the skill (no path assumes this checkout) | current | ADR 0009 Decision 3; `rules/12-artifacts-that-travel-name-nothing-local.md` |
| Knowledge checks never go into git hooks | current | `rules/05-no-git-hook-complication.md` |
| Gate once, scoped, at the end of a batch - never per edit or per commit | current | `rules/06-gate-once-scoped-at-the-end.md` |
| Every router renders from one contract; none is hand-edited | current | `rules/09-routers-are-rendered-from-one-contract.md` |
| Live verification that the Codex and Cursor routes actually work as installed | missing | `CHANGELOG.md` 1.2.0, "Not verified here": the Codex plugin route "comes from Codex docs and source"; Codex and Cursor are not installed on the maintaining machine per ADR 0009's own verification table |
| A refreshed plugin-directory listing that mentions the 2.0 living-wiki work | missing | `docs/listing.md` "Review when": last verified 2026-09-18 against 1.2.0, before ADR 0010 shipped |
| A quantified figure for the AI-cost-reduction claim (tokens or dollars saved) | missing | `docs/business-case.md` states the mechanism (capped brief, generated facts) but records no measured figure |
| A stated revenue or pricing model beyond "free, MIT" | missing | `docs/wiki/business/README.md`; no paid tier is named anywhere in the repository |

Source for every `current` row above: owner, 2026-09-18/19 sessions (ADR 0009
and ADR 0010 dates), plus the repository files cited. Source for `missing` rows:
the maintainers' own gap notes in `CHANGELOG.md` and the ADR "Review when"
sections cited per row.

## What changed recently

- The question budget rose from five to fifteen per prompt
  (`docs/scoping.md`, "The interrupt budget"; ADR 0010 supersedes the five-
  question cap it names in "Supersedes, in part").
- The stack map's earlier "no document per library" stance was reversed to a
  page per library, generated (ADR 0010 Context and Decision; supersedes the
  stance in `skills/everything/scripts/extract_stack.py`).
- The command surface moved from six planned commands (ADR 0005) to one
  command via twenty station skills (ADR 0008) to one skill whose stations are
  references (ADR 0009) - see `docs/wiki/drift/README.md` for the full chain.
