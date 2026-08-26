# Rule 04 - Routers stay thin, and they never fork

## Purpose

Every AI tool reads a different entry file. Each one that gets updated alone
becomes a separate version of the truth, and an agent reading the stale one acts
confidently and wrongly - which is the most expensive failure mode available,
because confidence suppresses checking.

The second failure is slower and just as fatal: content migrates *into* the
router. Someone pastes a rule's text in for convenience, and now the rule exists
twice. The copies diverge, and the reader has no way to know which is current.

## Applies to

- **In scope:** every AI entry-point file in this repository and in every
  repository Akinator onboards - root and per-module: `CLAUDE.md`, `AGENTS.md`,
  `CODEX.md`, `GEMINI.md`, `.cursorrules`, `.cursor/rules/*`, and any other file
  a tool reads first.
- **Out of scope:** genuinely tool-specific content - a Claude router naming
  slash commands Codex does not have. That is allowed when marked; see
  Exceptions.

## Mandatory rules

1. Every change that alters what a router says updates **all** routers in the
   same change.
2. Routers are indexes. They link to canonical content and never reproduce it.
3. The **facts** in every router agree. Tool-specific *presentation* may differ;
   tool-specific *facts* may not.
4. A per-module router links up to its parent, and the parent links down to it.
5. The router set is **discovered**, never assumed - a repo may have picked one
   up years ago that nobody remembers.

## Prohibited patterns

```markdown
<!-- CLAUDE.md -->
## Quota rules
Quota may only be mutated through applyQuota, which opens a transaction and
takes SELECT ... FOR UPDATE on the team row, then writes a ledger entry with
a reason from the QuotaReason enum...
```

The rule's text now exists in two places. One of them will be edited alone.

```markdown
<!-- CLAUDE.md says -->
Schema changes need a container rebuild, not a restart.

<!-- AGENTS.md says -->
(nothing about schema changes)
```

A fork. The Codex user restarts, loses an hour, and has no way to know the
answer was written down somewhere else.

## Correct pattern

```markdown
<!-- CLAUDE.md and AGENTS.md both -->
## Before you change anything

- **Money and entitlements:** quota is mutated only through `applyQuota` -
  `rules/07-quota-mutations.md`.
- **Schema changes need a container rebuild, not a restart** - see the
  `nimbus-schema-change` skill.
```

One sentence plus a link, identical facts, in every router.

```markdown
<!-- CODEX.md - legitimate tool-specific section -->
<!-- akinator:tool-specific -->
## Codex specifics
Skills are read from `.agents/skills/`.
```

## Enforcement

- Mechanism: `scripts/akinator_coverage.py` - the `router-sync` check compares
  the knowledge each root router references and reports **high** for any router
  omitting what the others carry, unless that router is marked
  `<!-- akinator:tool-specific -->`. The `module-routers` check reports modules
  with no local router.
- Mechanism: `tests/test_plugin_structure.py::test_routers_agree`
  asserts this repository's own routers carry the same knowledge links.
- Type: script check in CI, plus a unit test.
- How it fails: the report names the router and the links it is missing.
- Last observed passing: 2026-08-26

**Never a git hook** - see `rules/05-no-git-hook-complication.md`.

## Exceptions

A genuinely tool-specific section is marked with the HTML comment
`<!-- akinator:tool-specific -->`, which the coverage check honors. Use it only
for content that is *true of the tool* - where its skills live, which commands
exist - never for a fact about the repository that you did not get around to
copying across.

## Related

- Skills: `akinator-router-sync`, `akinator-index-sync`
- Templates: `templates/router.md`, `templates/examples/router.md`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] Enforcement mechanisms exist in the tree and are named by path.
- [x] The mechanisms are not git hooks.
- [x] Prohibited and correct patterns are shown.
- [x] The exception path is named and has a machine-readable marker.
- [x] The rule is indexed and reflected in every router.
