# UX

What this answers: design system, UX decisions, accessibility.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## Is there a design system, which UX decisions are settled, and which accessibility standard applies?

There is no visual design system - Akinator ships no UI. Its product surface
*is* the command/menu surface and the agent's own messages, so "UX" here means
those, decided in `docs/adr/0009-one-skill-one-command-one-installer.md` and
`docs/adr/0010-every-prompt-documented-living-wiki.md`.

**One entry point, one per platform, always on.**

| Platform | Entry point | Menu-visible surface |
|---|---|---|
| Claude Code | `/akinator:everything` | exactly one - `slash_commands: ['akinator:everything']`, verified live against a 2.1.154 session |
| Codex | `$akinator` | one skill in the `$` picker |
| Cursor | `/akinator` | one skill folder in `.agents/skills` |

Akinator is always-on from `SessionStart` (`hooks/hooks.json` /
`hooks/session-start.sh`) - normal prompts need no command at all; the
explicit command exists for a forced full pass. ADR 0009 rejected hiding the
twenty station references as separate skills (`user-invocable: false`) because
that only works on Claude Code; Codex and Cursor have no equivalent hide, so
the one-skill-with-references design was chosen to give exactly one entry on
all three platforms, not merely on the one that supports hiding.

**Questions are grouped, ranked, and each carries a recommended default.**
ADR 0010 raised the per-prompt question budget from the earlier five-question
interrupt cap (`docs/scoping.md`) to up to fifteen (`interrupt_budget` in
`.ai/config.json`, currently `15`), delivered as one ranked message rather than
a drip of prompts, each question carrying a recommended default so "go with
recommendations" is always a complete, single-word answer. This is the UX
decision that makes a high question count tractable instead of the
"twenty questions means zero answers" failure the five-question cap was
originally set to avoid.

**Honest gaps, not silent invention.** Every unknown fact in the wiki is the
exact line `_Unknown - ask the owner and record the answer._` - never a guess,
never left blank. `akinator_wiki.py gaps` turns every such marker, and every
category with no page, into a question for the owner. This is the UX contract
for uncertainty: visible and queryable, not smoothed over.

**Accessibility: not applicable.** Akinator has no graphical or web interface -
its surface is CLI slash/`$` commands and generated Markdown/text files read
by a human or an agent in a terminal or editor. No accessibility standard
(WCAG or otherwise) applies to a command-line and file-based surface; this is
a fact, not a gap, so it carries no marker.
