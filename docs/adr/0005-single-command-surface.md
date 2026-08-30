# ADR 0005 - One command, not one per mode

- **Status:** accepted
- **Date:** 2026-08-26
- **Deciders:** Ihab Khaled (owner)

## Context

The build brief (Part 9) specified six slash commands: `/akinator:onboard`,
`/akinator:audit`, `/akinator:status`, `/akinator:sync`, `/akinator:question`
and `/akinator:decide`.

During the build the owner stated a different requirement directly: *"I don't
want variety in plugin commands. I only want one command do everything, all
skills everything in the plugin."*

This is a deviation from the brief. The brief itself says the platform contract
and the owner's mandate win over the pack, and that deviations must be stated
explicitly rather than applied silently - hence this record.

Relevant context for evaluating it later: Akinator's skills are
**auto-triggered** by their descriptions. The command surface is not how skills
get invoked; it is how a user asks for a specific mode deliberately.

## Options considered

### Option A - Six commands, as specified in the brief

- **What it is:** one command per mode, each with its own frontmatter and
  argument hint.
- **Cost:** six names to remember and six entries in the user's slash-command
  list, for a plugin whose default path - run the loop on some work - is none of
  them. Six files to keep consistent as the loop evolves.
- **Why it lost:** the owner declined it. Independently, it optimizes for
  discoverability of modes that are used rarely, at the cost of cluttering a
  surface the user sees constantly.

### Option B - One command with mode dispatch (chosen)

- **What it is:** `/akinator [mode] [args]`. The first word selects a mode if it
  matches one; otherwise the whole argument string is treated as the work to run
  through the loop.
- **Cost:** the modes are less discoverable - a user must read
  `argument-hint` or the command body to learn that `status` exists. Argument
  parsing lives in prose rather than in the platform's command routing.
- **Why it won:** it matches the owner's stated preference, it keeps the surface
  to one memorable name, and free-text fallthrough means the most common use -
  "run the loop on this" - needs no mode word at all. The modes remain
  documented in the command's own body, which is where a user who types
  `/akinator` with no arguments will end up.

### Option C - No command, skills only

- **What it is:** rely entirely on skill auto-triggering.
- **Cost:** no way to deliberately ask for `status` or `sync`, which are audit
  operations a user wants on demand rather than by inference.
- **Why it lost:** the modes are genuinely user-initiated. Auto-triggering is
  right for "I am about to change code"; it is wrong for "show me the knowledge
  health of this repo".

## Decision

Akinator ships exactly one command: `commands/everything.md`.

**It runs everything by default.** With no arguments, or with free text, it loads
`akinator-everything` and runs the complete pass - every station, every
applicable boardroom lens, every mechanical check, looping until the Definition
of Done is proven with evidence. The mode words `onboard`, `audit`, `status`,
`sync`, `question` and `decide` narrow the *target*, never the depth.

A second command is not added without the owner asking for one.

**Renamed 2026-08-26.** The command file moved to `commands/everything.md` from
its original name, so it is invoked as `/akinator:everything` - the plugin
namespace supplies the `akinator` half, and the file name supplies the rest.
Still exactly one command; the name now says what it does.

**Amended 2026-08-26.** The original decision had the command run the loop
*scaled to the work*. The owner asked for the root command to "run literally
everything", so the default is now the exhaustive pass, and scaling down is a
judgment the agent must make out loud and only for genuinely trivial work. The
scaled behavior remains available through the auto-triggered `akinator` skill,
which is the right default when no one typed a command at all.

## Consequences

**Good**
- One name to remember; one entry in the slash-command list.
- The default path - free text - needs no mode word.
- One file to keep consistent with the loop, instead of six.

**Bad**
- Mode discoverability depends on the `argument-hint` and the command body
  rather than on the platform's command list.
- Argument parsing is prose the model interprets, not platform routing, so a
  mode word that collides with a plausible free-text opening ("audit the
  refund flow") is interpreted as the mode. This is usually the right reading,
  but it is an ambiguity the six-command design would not have had.

**Debt taken on**
- If a mode ever needs a narrower `allowed-tools` list than the others - a
  read-only `status`, say - one command's frontmatter cannot express that. Pay
  this down by splitting only that mode out, and update this ADR.

## Revisit when

- The owner asks for a second command.
- A mode needs a genuinely different tool allowlist or permission surface.
- Mode collision with free text causes a real misfire in practice.

## Related

- Code: `commands/everything.md`
- Memory: `memory/2026-08-26-single-command-preference.md`
- Test: `tests/test_plugin_structure.py::test_there_is_exactly_one_command`
- Docs: `docs/deviations.md` - every deviation from the build brief
