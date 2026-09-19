# Drift

What this answers: the business, product and scope drift log.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## Where has the product or business intent drifted from what was originally specified, and was each drift accepted?

Each row is also recorded as a `drift` ledger record (`python
skills/everything/scripts/akinator_ledger.py list --type drift`). All drifts
below were accepted - each is the resolved state of a later ADR, not an open
inconsistency.

| Area | Before | After | Why | Date |
|---|---|---|---|---|
| Command surface | Six planned commands: `/akinator:onboard`, `audit`, `status`, `sync`, `question`, `decide` (the build brief, Part 9) | One command, `/akinator:everything`, with mode dispatch by argument | The owner stated directly: "I don't want variety in plugin commands. I only want one command do everything." Six names to remember, six entries cluttering a surface used constantly, for a plugin whose default path is none of them. | 2026-08-26, ADR 0005 |
| Command surface | One command file, but twenty separate station skills still auto-triggering and listed individually | One skill (`skills/everything/`) whose twenty stations became `references/`, opened on demand; the skill is the command | A live Claude Code 2.1.154 session showed the `/` menu listing `/akinator:everything` plus 21 skill entries - the "one command" requirement was about the menu, and nobody had checked the menu. Codex cannot hide a skill from its picker at all; Cursor lists every folder in `.agents/skills`. One skill was the only design giving exactly one entry on all three platforms. | 2026-09-18, ADR 0009 |
| Question budget | Five questions per session cap (`docs/scoping.md`, "twenty questions means zero answers") | Up to fifteen per prompt, grouped and ranked in one message, each with a recommended default | The owner's corporate-scale requirement needs many answers captured, not few; the fix for interrupt fatigue is ranking, grouping and defaults ("go with recommendations" as a complete answer), not a low cap that leaves gaps unasked. | 2026-09-19, ADR 0010 |
| Library documentation | No document per library - the stack map explicitly refused a page per dependency because a page restating `package.json` rots and buries the pages that carry knowledge | A generated page per dependency under `docs/wiki/libraries/`, facts regenerated between markers, why/pitfalls/upgrade sections curated and preserved across regeneration | The owner's requirement is corporate-scale knowledge, including libraries and why they were chosen; the generated/curated split answers the original rot objection instead of accepting the gap. | 2026-09-19, ADR 0010 |
| Brand asset | A generated logo, produced by a script in the repository | Hand-designed 1254x1254 artwork, the generator script removed | The owner replaced the generated mark with commissioned artwork; a later CI test that byte-compared generated brand assets against the hand-designed file then failed on every run for seven minutes until removed. | 2026-09-18, `CHANGELOG.md` 1.2.0 "Removed" and "Fixed" (`.ai/ledger/failure/byte-compare-test-hid-a-logo-for-7-minutes-e1b6f3a09d27.md`) |

## Drifts not yet resolved

None open as of this page - every drift found in the repository's history
(ADRs, CHANGELOG, ledger) has a superseding decision recorded above. A new
drift is logged here, and as a ledger `drift` record, the moment one is
noticed.
