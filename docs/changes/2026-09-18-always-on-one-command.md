# Change — Always-on one-command Akinator and living wiki

- **When:** 2026-09-18
- **Actor / agent:** ChatGPT coding agent on behalf of Ihab Khaled
- **Request / source:** owner request to simplify Akinator and strengthen vibe-coding knowledge
- **Status:** implemented on feature branch

## Before

Akinator had one command file but documented mode words and treated the exhaustive
`akinator-everything` skill as deliberate/exceptional. Claude had SessionStart
activation; Codex depended on skill selection/router behavior. Change provenance
was distributed across docs, memory, ADR and ledger concepts without one minimum
record contract.

## Change

Removed user-facing mode dispatch, made `/akinator:everything` the sole explicit
command, made the master orchestrator the automatic path for repository-changing
prompts, strengthened Claude/Codex/Cursor adapters, added the living-wiki
contract and added a change-record template.

## Now

Users prompt normally. Akinator resolves the standing contract automatically.
Internal skills execute behind one master orchestrator. Meaningful changes record
before → change → now plus why, intent, provenance, consequences and verification.

## Why

Reduce command/interface complexity while increasing durable product, business,
architecture and historical context available to future coding agents.

## Technical reasoning

Platform-native activation is used where available: Claude SessionStart, Codex
portable AGENTS contract, Cursor always-apply rule. This avoids pretending the
three products have identical hook APIs.

## Compatibility / migration / rollback

Existing internal skills remain. User-facing mode words are removed. Reverting
the branch restores prior command documentation and trigger behavior.

## Knowledge delta

- ADR: `docs/adr/0008-always-on-master-contract.md` (filed as 0006, which was
  already taken; renumbered)
- Wiki: `docs/living-wiki.md`
- Template: `templates/change-record.md`
- Skills: master, everything, document-change, rule-forge
- Routers/generators: Claude, Codex, Cursor behavior sources
- README: simplified installation and usage

## Verification

Branch diff and generated-source relationships are reviewed in this change.
Repository CI must regenerate derived routers/Codex pack and run the existing
test suite before merge.

## Future

Marketplace-specific installation can be added when distribution is published.

## Stale when

Claude, Codex or Cursor changes its plugin/rules/agent-instruction contract.
