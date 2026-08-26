# Rule 08 - `skills/` holds only skill directories

## Purpose

Both plugin platforms import skills by scanning `skills/` for **subdirectories
containing `SKILL.md`**. A loose file directly under `skills/` is not imported -
and Codex plugin validation rejects the plugin outright with:

> Files directly under `skills/` are not imported as skills. Move this file into
> a skill directory containing `SKILL.md`, or remove it.

The trap is that the loose file is usually a **README index**, which is the right
instinct in a normal repository and the wrong one in a plugin. It looks correct,
it reads correctly, it is linked from the routers - and it silently makes the
package invalid.

Akinator shipped exactly this defect in its first build - a good index, in a
place that made the plugin fail validation:

```
skills/
  README.md          <- linked from every router, and not imported
  akinator/
    SKILL.md
```

## Applies to

- **In scope:** the `skills/` directory of this plugin, and of any plugin
  Akinator generates or onboards.
- **Out of scope:** a target repository's own `skills/` directory when that repo
  is **not** a plugin. There, a README index inside `skills/` is perfectly good,
  and `templates/router.md` still recommends it. The constraint is about plugin
  packaging, not about knowledge layout.

## Mandatory rules

1. Every entry directly under `skills/` is a directory.
2. Every such directory contains a `SKILL.md`.
3. The skills index for a plugin lives outside `skills/` - in this repository it
   is `docs/skills.md` - and the routers link to it there.

## Prohibited patterns

```
skills/
  README.md            <- not imported; fails Codex validation
  index.md             <- same
  .DS_Store            <- same
  akinator/
    SKILL.md
```

## Correct pattern

```
skills/
  akinator/
    SKILL.md
  akinator-intake/
    SKILL.md

docs/
  skills.md            <- the index lives here, linked from every router
```

## Enforcement

- Mechanism: `tests/test_plugin_structure.py` - `test_skills_dir_holds_only_skill_directories`
  asserts nothing but directories sit under `skills/`, and that each one contains
  a `SKILL.md`.
- Type: unit test, run with the suite and in CI.
- How it fails: the test names the offending path and points here.
- Last observed passing: 2026-08-26

**Never a git hook** - see `rules/05-no-git-hook-complication.md`.

## Exceptions

None for a plugin. If a file feels like it belongs under `skills/`, it belongs in
one of two places instead:

- Index or narrative about the skills → `docs/skills.md`.
- A supporting file for one skill → inside that skill's own directory, where
  both platforms support `scripts/`, `references/` and `examples/` subdirectories.

## Related

- Rules: `rules/02-skills-carry-all-six-parts.md`
- Docs: `docs/skills.md` - where the index moved to
- Docs: `docs/compatibility.md` - the packaging contracts
- Memory: `memory/2026-08-26-codex-plugin-validation-surprises.md`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] The enforcement mechanism exists in the tree and is named by path.
- [x] The mechanism is not a git hook.
- [x] Prohibited and correct patterns are shown.
- [x] The absence of an exception path is deliberate, with the alternatives named.
- [x] The rule is indexed and reflected in every router.
