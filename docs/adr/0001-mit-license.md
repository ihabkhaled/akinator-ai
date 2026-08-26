# ADR 0001 - MIT license

- **Status:** accepted
- **Date:** 2026-08-26
- **Deciders:** Ihab Khaled (owner)

## Context

Akinator is a behavioral plugin: prose, skills and small scripts. Its value is
adoption - a knowledge discipline that only one team uses does not bend the cost
curve the product exists to bend. The build brief specified MIT as the default
unless the owner said otherwise, and recorded as an ADR.

The plugin embeds no third-party code, so there is no inbound license
constraint to satisfy.

## Options considered

### Option A - MIT (chosen)

- **What it is:** permissive; use, modify, redistribute, sublicense, with
  attribution and no warranty.
- **Cost:** a company can fork Akinator into a closed internal product and
  contribute nothing back.
- **Why it won:** adoption is the goal, and MIT is the license that corporate
  legal review approves without a conversation. For a plugin whose content is
  prose that people will copy into their own repos anyway, a restrictive license
  would be unenforceable in practice and would deter the exact users it targets.

### Option B - Apache 2.0

- **What it is:** permissive, plus an explicit patent grant and a
  notice-preservation requirement.
- **Cost:** more ceremony - NOTICE files, per-file headers by convention - for a
  repository that is mostly markdown.
- **Why it lost:** the patent grant protects against a risk that does not exist
  here; there is nothing patentable in a documentation discipline. The added
  file-header ceremony would appear in every skill Akinator ships into a target
  repo, which is a real cost paid on every install.

### Option C - AGPL or a source-available license

- **What it is:** copyleft, requiring derivative works to be shared.
- **Cost:** many companies forbid AGPL dependencies outright by policy.
- **Why it lost:** it would block adoption inside exactly the organizations that
  most need institutional memory - large ones with many contributors. It also
  fits badly: the "derivative work" of a prose plugin is a target repository's
  documentation, and demanding that be shared is neither desirable nor
  enforceable.

## Decision

Akinator is MIT licensed. `LICENSE` at the repository root, and `license: "MIT"`
in both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`.

## Consequences

**Good**
- No legal review friction for adopters.
- Users can copy templates and skills directly into their own repositories,
  which is the intended use.
- Both plugin manifests can declare a standard SPDX identifier.

**Bad**
- No obligation for improvements to flow back.
- No patent grant, explicit or implied.

**Debt taken on**
- None. Relicensing later would require consent from every contributor, so this
  is effectively a one-way door - which is why it is recorded here rather than
  assumed.

## Revisit when

- Akinator accepts substantial outside contributions and the contributor set
  becomes large enough that relicensing would be impractical - at which point
  this is settled permanently, and the ADR should be marked as such.
- The project takes on a dependency whose license imposes stronger terms.

## Related

- `LICENSE`
- `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`
