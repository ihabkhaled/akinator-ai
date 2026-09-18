# ADR 0008 — Always-on master contract and living wiki

- **Status:** accepted
- **Date:** 2026-09-18
- **Decider:** Ihab Khaled (owner)
- **Renumbered:** filed as 0006 on 2026-09-18, a number already held by
  `0006-index-completeness-as-its-own-invariant.md`. Moved to 0008 the same
  day. The earlier record keeps its number, because CI comments, the
  CHANGELOG and ADR 0007 already cite it as 0006.

## Context

The plugin already had one command, but it still exposed mode words and treated
the exhaustive orchestrator as a deliberate path. The owner requires a simpler
contract: one explicit command only, while normal prompts activate Akinator
without requiring that command. The knowledge layer must preserve not only code
structure but product/business intent and change provenance.

## Decision

1. The sole explicit command is `/akinator:everything [free text]`.
2. Akinator has no user-facing subcommands or mode dispatch.
3. Normal prompts enter the standing Akinator contract automatically.
4. Repository-changing work uses `akinator-everything` as the master
   orchestrator and evaluates all stations.
5. Internal skills remain composable implementation details, not user commands.
6. Claude uses SessionStart for automatic activation.
7. Codex uses the installed portable `AGENTS.md` contract and generated skills;
   explicit `$akinator-everything` is a fallback because Codex does not expose
   Claude's SessionStart hook contract.
8. Cursor uses an `alwaysApply: true` rule.
9. Meaningful changes produce durable provenance: before, change, now, why,
   actor/agent when knowable, time, intent, consequences, knowledge delta and
   verification.
10. The living wiki separates current truth, historical truth and future intent.

## Consequences

The user learns one command, but normally needs none. The internal skill count
does not enlarge the command surface. Every platform receives the same behavioral
contract through the strongest mechanism it supports.

Automatic activation is a behavioral guarantee of the installed router/hook,
not a claim that Claude, Codex and Cursor expose identical extension APIs.

## Related

- `skills/everything/SKILL.md` - since ADR 0009, the one skill and the one command
- `hooks/session-start.sh`
- `skills/everything/SKILL.md`
- `scripts/build_codex_pack.py`
- `scripts/render_routers.py`
- `docs/living-wiki.md`
- `templates/change-record.md`

## Superseded in part - 2026-09-18 (ADR 0009)

Point 5 - "internal skills remain composable implementation details, not user
commands" - and the consequence "the internal skill count does not enlarge the
command surface" were **wrong**, and were never checked against a menu: Claude
Code lists every skill in `/`, Codex cannot hide a skill from `$` at all, and
Cursor lists every folder in `.agents/skills`. The owner saw twenty-two entries.
`docs/adr/0009-one-skill-one-command-one-installer.md` replaced the twenty-one
skills with one skill whose stations are reference files. Everything else in this
record stands.
