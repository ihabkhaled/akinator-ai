---
name: codex-plugin-validation-surprises
type: surprise
date: 2026-08-26
---

# Codex plugin validation requires interface assets, and rejects loose files under skills/

## The fact

Three things Codex plugin validation enforces that the written spec does not make
obvious:

1. **`interface.composerIcon` is required**, and must reference a square image.
2. **`interface.logo` is required**, and must reference a square image.
3. **Files directly under `skills/` are not imported**, and fail validation:
   *"Files directly under `skills/` are not imported as skills. Move this file
   into a skill directory containing `SKILL.md`, or remove it."*

The spec lists `composerIcon` and `logo` among the *optional* interface fields.
They are not optional. Reading the field list and believing it produces a plugin
that looks correct, passes every local test, and is rejected on submission.

## Why

The first two were misread rather than undocumented: the spec's "Optional
Fields" section lists them, but the validator treats the interface block as a
storefront listing, and a listing without an icon cannot be rendered. The lesson
generalizes - **the validator is the contract, the field list is a summary.**

The third is a genuine trap, and Akinator walked straight into it. `skills/` had
a `README.md` index: linked from every router, correct by the taxonomy's own
"every artifact reachable from an index" law, and reasonable in any normal
repository. In a *plugin* it silently makes the package invalid, because both
platforms import skills by scanning for subdirectories containing `SKILL.md`.

The index now lives at `docs/skills.md`.

## Date

- 2026-08-26 - recorded when the owner reported all three from a validation run.
  `docs/compatibility.md` had asserted the opposite about the assets and was
  corrected in the same batch.

## Reversal conditions

- Codex changes the interface requirements, or begins importing loose files under
  `skills/`.
- Akinator stops shipping a Codex plugin manifest, at which point only the
  `skills/` constraint still applies (Claude Code also ignores loose files there,
  it just does not reject the plugin for them).

## Related

- `rules/08-skills-dir-holds-only-skill-directories.md` - the constraint, with a
  test as its enforcement
- `docs/compatibility.md` - the corrected contract table
- `docs/deviations.md` - item 4, kept and corrected rather than rewritten
- `assets/akinator-icon.png`, `assets/akinator-logo.png` - the required assets;
  hand-designed since 2026-09-18, when the drawing script was retired
- [[verify-contracts-from-installed-plugins]] - the same lesson from the Claude
  side: the artifact beats the documentation
