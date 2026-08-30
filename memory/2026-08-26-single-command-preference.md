---
name: single-command-preference
type: preference
date: 2026-08-26
---

# The owner wants exactly one command, not a command per mode

## The fact

Akinator ships a single `/akinator` command that dispatches every mode
(`onboard`, `audit`, `status`, `sync`, `question`, `decide`, or free-text work)
and routes to every skill. The build brief originally specified six separate
slash commands; the owner asked for one.

Adding a second command to this plugin is a change the owner has already
declined. Propose it explicitly rather than assuming it is an improvement.

## Why

Stated by the owner during the build: "I don't want variety in plugin commands.
I only want one command do everything, all skills everything in the plugin."

The design reason it works: the skills are auto-triggered by their descriptions,
so the command surface does not need to expose them. A mode word is cheaper to
remember than six command names, and free text falls through to the loop, which
is the default path anyway.

## Date

- 2026-08-26 - stated by the owner mid-build; the six-command design was
  replaced before any command file was written.

## Reversal conditions

- The owner asks for a second command.
- A mode needs a genuinely different tool allowlist or permission surface that
  cannot be expressed within one command's frontmatter.

## Related

- `commands/everything.md` - the single command
- `docs/adr/0005-single-command-surface.md` - the decision record
- `tests/test_plugin_structure.py::test_there_is_exactly_one_command`
