# Change - 2.1.0: traced changes, fast context, sensitive data, a 25-category wiki

- **When:** 2026-10-03
- **Who / agent:** Ihab Khaled (owner), via Claude Code (Claude Sonnet 5.5)
- **Source:** owner request 2026-10-03; ADR 0011
- **Status:** implemented; released as 2.1.0

## Before

A pass could prove its knowledge delta only by prose discipline and the
librarian lens (rule 01). Gaining context meant reading the tree or the whole
brief. Nothing knew which values were secret, and nothing scanned tracked files
for a leaked one. The wiki had 16 categories and no platform, history or
operations pages. A gap marker stayed a gap until someone edited the page by
hand, and a repeated change pattern was never offered to the owner as a skill
or a rule.

## Change

Still one skill, one command, no new station reference, no new skill. Added
deterministic tools to `skills/everything/scripts/`: `akinator_context.py`
(`pack`, `owners`, `stale`, `budget`), `akinator_trace.py` (`plan`, `check`,
`record`), `akinator_sensitive.py` (`register`, `scan`, `guard`),
`extract_platform.py`, `extract_history.py`, `extract_operations.py`. Extended
`akinator_wiki.py` with `interview` and `answer`, and `akinator_distil.py` with
`repeats`. Added two rules (14 trace, 15 sensitive data), nine wiki categories
(roadmap, history, data, services, observability, standards, security,
integrations, risks), five templates, and CI steps for `trace check` and the
sensitive register and scan. Decision record: ADR 0011.

## Now

`akinator_context.py pack --for "<task>"` returns a ranked reading list inside
a token budget (default 3000) from an incremental cache at `.ai/cache/`
(self-ignored, about 80 ms warm), so a session reads the pack instead of the
tree. Every changed path must be a knowledge artifact, named in a change record
in the same diff, or listed under `knowledge delta: none, because ...`. The
sensitive register holds names and locations, never values; `scan` finds leaked
secrets and prints a fingerprint. The wiki has 25 categories. An answered gap
becomes text on the page plus a ledger question. Co-changing file sets and
repeated commit stems are put to the owner as skill, rule or neither.

## Why

The owner asked that the AI know everything, gain context very fast and cheap,
take decisions and responsibility, stay secure, and cover what company teams do
- without a second command. Prose discipline cannot be audited; a cheap
deterministic tool can, on every platform.

## Files touched

- `skills/everything/scripts/` - akinator_context, akinator_trace, akinator_sensitive, extract_platform, extract_history, extract_operations (new); akinator_wiki, akinator_distil (extended)
- `rules/14-every-changed-path-is-traced.md`, `rules/15-sensitive-data-is-known-and-never-exposed.md`, `rules/README.md`
- `templates/` - change-record rewritten; business-decision, roadmap-item, data-store, integration, risk added, each with an example under `templates/examples/`
- `tests/` - test_context, test_trace, test_sensitive, test_platform, test_history, test_operations, test_repeats (new); test_wiki, test_plugin_structure (extended)
- `.github/workflows/ci.yml` - trace check and sensitive register and scan
- `.ai/config.json` - sensitive allow list
- `docs/wiki/` - nine new category homes, generated pages, curated sections
- `README.md`, `docs/architecture.md`, `docs/README.md`, `docs/compatibility.md`, `docs/skills.md`, `CHANGELOG.md`
- `docs/adr/0011-cheap-deterministic-tools-over-prose-or-indexing.md`, `docs/adr/README.md`
- `docs/changes/2026-10-03-trace-fast-context-sensitive.md`
- `memory/2026-10-03-read-the-pack-not-the-tree.md`, `memory/index.md`
- `.ai/ledger/` - requirement, decision and drift records

## Business meaning

Cost per session falls (a bounded pack instead of tree reads), and a change
without its explanation, or a leaked secret, becomes a failing CI step instead
of a review comment. No customer-visible behavior of a target repository
changes unless it adopts the tools.

## Operational consequence

Hosts get the tools by updating the skill. `.ai/cache/` appears locally and
ignores itself. CI gains two steps; a repository with an existing leaked secret
fails `scan` until it is rotated or allow-listed.

## Rollback

Revert the commit and the 2.1.0 version bump. The cache is disposable. Ledger
records are append-only and stay.

## Knowledge delta by path

- Rules: `rules/14-every-changed-path-is-traced.md`, `rules/15-sensitive-data-is-known-and-never-exposed.md`
- Skills: none new - the one skill `skills/everything/SKILL.md` names the tools
- ADRs: `docs/adr/0011-cheap-deterministic-tools-over-prose-or-indexing.md`
- Docs, context, memory: `docs/skills.md`, `docs/architecture.md`, `docs/wiki/`, `memory/2026-10-03-read-the-pack-not-the-tree.md`

## Verification

Run at the end of the batch: `akinator_coverage.py . --strict`,
`akinator_sensitive.py guard` over the written docs, `akinator_ledger.py
verify`. Results are reported by the batch owner, not asserted here.

## Follow-ups

Not done: semantic ranking in `pack`, a measured token-saving figure, live
Codex and Cursor verification of the new tools.

## Stale when

A tool's CLI changes, a category is added to or removed from the wiki, or the
cache format version changes.

## Follow-up (same release, found by CI)

- `.gitignore` - ignores `.env`, `.env.*` (except `.env.example`) and `.ai/cache/`; the generated security page had correctly reported that no rule covered `.env`.
- `skills/everything/scripts/extract_platform.py` - the tree walk skips `.ai/cache/`, a machine-local folder that made the generated pages differ between a clone and CI.
- `tests/test_platform.py` - a test proves the cache never reaches a page.
