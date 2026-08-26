# Deviations from the build brief

The build brief (Prompt Pack v1.0) said: where it conflicts with the platform's
actual contract, the platform wins and the deviation is stated explicitly - never
applied silently. This is that statement.

Every deviation below is either an owner instruction that superseded the brief,
or a place where the real platform contract differed from what the brief
described.

## 1. One command instead of six

- **Brief, Part 9:** six commands - `/akinator:onboard`, `:audit`, `:status`,
  `:sync`, `:question`, `:decide`.
- **Shipped:** one command, `/akinator`, dispatching all six modes plus
  free-text work.
- **Why:** the owner instructed it directly during the build: *"I don't want
  variety in plugin commands. I only want one command do everything, all skills
  everything in the plugin."*
- **Recorded in:** `docs/adr/0005-single-command-surface.md`,
  `memory/2026-08-26-single-command-preference.md`.

## 2. The Codex pack is real Codex skills, not "prompt files"

- **Brief, Part 3.2:** "the skills as Codex-consumable prompt files".
- **Shipped:** `.agents/skills/<name>/SKILL.md` - the actual Codex skills
  contract, which turned out to be the same shape as Claude's (`SKILL.md` with
  `name` and `description` frontmatter).
- **Why:** the brief predated verification. Codex has a first-class skills
  system reading `.agents/skills/`; shipping loose prompt files would have been
  strictly worse - not auto-selected, not invocable with `$name`, not discovered.
- **Consequence:** generation is a banner-only transformation rather than a
  format conversion, which is why the two platforms cannot diverge.
- **Recorded in:** `docs/adr/0002-codex-pack-generated-from-claude-skills.md`,
  `docs/compatibility.md`.

## 3. No Codex hook surface

- **Brief, Part 10:** a SessionStart hook injecting the contract.
- **Shipped:** the hook exists for Claude Code only.
- **Why:** Codex plugin manifest validation **rejects** unsupported fields such
  as `hooks`. There is no equivalent surface to ship it on.
- **How the contract still reaches Codex:** the generated `AGENTS.md` carries
  the same creed, loop and non-negotiables, and Codex reads it at session start
  by its own convention. `tests/test_codex_pack.py::test_agents_md_carries_the_non_negotiables`
  asserts the content is actually there rather than assumed.
- **Recorded in:** `docs/compatibility.md`.

## 4. No image assets in the Codex manifest

- **Brief, Appendix / Part 18:** implies a distributable, listable plugin.
- **Shipped:** `.codex-plugin/plugin.json` omits `composerIcon`, `logo`,
  `privacyPolicyURL` and `termsOfServiceURL`.
- **Why:** Codex validation requires asset paths to point at real files inside
  the plugin archive, and URLs to be absolute `https://`. Akinator ships no image
  assets and has no privacy or terms documents. Naming files that do not exist
  would fail validation - and would be precisely the fake compliance the plugin
  forbids (`skills/akinator-anti-gaming/SKILL.md`).
- **To close:** add real assets, then add the fields. Asserted by
  `tests/test_plugin_structure.py::test_codex_manifest_assets_exist`, which will
  start checking them the moment they are declared.

## 5. Templates directory holds 10 templates in 10 files, with a shared examples set

- **Brief, Appendix:** ten templates, "each with a filled example".
- **Shipped:** ten templates in `templates/`, and ten filled examples in
  `templates/examples/`, all written against **one** fictional product (Nimbus).
- **Why:** the brief did not specify whether examples should be independent. One
  coherent product makes the examples cross-reference each other the way real
  artifacts do - the rule cites the ADR, the business doc names the code the rule
  protects, the runbook fires from the skill. Ten disconnected samples would not
  have shown that, and the cross-referencing is a large part of what the
  taxonomy is for.
- **Note:** item 9 of the Appendix ("Router templates - thin CLAUDE.md /
  CODEX.md / AGENTS.md index skeletons") is one file holding three skeletons, as
  the brief describes it.

## 6. Fenced code blocks are exempt from truth checking

- **Brief, Part 14.1:** "No doc describes deleted behavior (sampled: docs' named
  files/symbols exist)."
- **Shipped:** the coverage checker strips fenced code blocks before extracting
  links and path mentions.
- **Why:** without the exemption, every illustrative example in a skill produces
  a false HIGH finding - and a checker with false findings trains people to
  ignore it, which is worse than not having it. The first run against Akinator's
  own skills produced five such findings, all illustrations.
- **The rule it creates:** an illustrative path must live inside a fence; prose
  outside a fence is treated as a claim and is checked.
- **Recorded in:** `memory/2026-08-26-fenced-examples-avoid-false-findings.md`.

## 7. Gate receipts are specified, not shipped

- **Brief, Part 12.2:** "Implement a tree-bound gate receipt".
- **Shipped:** the mechanism is specified in
  `rules/06-gate-once-scoped-at-the-end.md` and
  `skills/akinator-gate-economy/SKILL.md`; no reference implementation ships.
- **Why:** hook stacks differ too much between repositories for one
  implementation to be correct, and a wrong one would be trusted. This is
  recorded as debt with a payoff condition rather than left implicit.
- **To close:** build the first one in a real target repository, then extract it
  into `templates/`.
- **Recorded in:** `docs/adr/0004-gate-receipts-over-hook-bypass.md`, under Debt
  taken on.

## Review when

- The brief is revised.
- A platform contract changes such that a deviation is no longer necessary -
  particularly items 3 and 4, which exist only because of current Codex
  validation behavior.
- Last verified: 2026-08-26.
