# Rule 02 - Every skill carries all six parts

## Purpose

A skill missing a part fails in a specific, predictable way:

- No **trigger description** - it never fires, and the effort that produced it is
  wasted entirely.
- No **when-NOT-to-use** - it fires on the wrong problem, and confidently gives a
  procedure for a situation the reader is not in. This is worse than silence.
- No **preconditions** - the procedure fails at the step that assumed something.
- No **failure modes** - the reader follows the steps, hits the known
  complication, and re-derives the diagnosis that someone already paid for.
- No **definition of done** - "done" becomes a feeling, and the next agent
  inherits a half-finished procedure.

The six parts are not a formatting preference. Each one prevents a distinct
failure that has actually happened.

## Applies to

- **In scope:** every `SKILL.md` in this repository, and every skill an
  Akinator-governed session writes into a target repository.
- **Out of scope:** a target repo's pre-existing skills, on the day it is
  onboarded. Those are reported as findings and improved in batches - adopt,
  never impose. Skills *written* after onboarding follow this rule.

## Mandatory rules

1. Frontmatter contains `name` (kebab-case) and `description`.
2. The `description` is written as a **trigger** - the situation, in the words
   someone uses when they are in it - not as a summary of the skill.
3. The body contains a **When to use** section.
4. The body contains a **When NOT to use** section naming where to go instead.
5. The body contains a **Procedure** with real commands, and, for anything
   operational, an explicit statement of what is parallel-safe and what is not.
6. The body contains **Failure modes and pitfalls** describing the misleading
   symptom, not only the fix.
7. The body contains a **Definition of done** of checkable, observable
   conditions.

## Prohibited patterns

```markdown
---
name: database-migrations
description: This skill handles database migrations.
---
```

The description describes the skill instead of the situation, so it never fires.
No agent thinks "I am handling database migrations"; they think "the migration
ran but the API still says the column does not exist".

```markdown
## Procedure
Rebuild the affected services and run the migration.
```

Describes commands instead of writing them, states no ordering, and gives the
reader nothing they did not already have.

## Correct pattern

```markdown
---
name: nimbus-schema-change
description: Use when a change adds or edits a file under db/migrations/, or when a schema change has been deployed and the API is returning column-not-found errors even though the migration reportedly ran.
---
```

See `templates/skill.md` for the skeleton and `templates/examples/skill.md` for
a fully worked example with parallel-vs-sequential steps and real failure modes.

## Enforcement

- Mechanism: `skills/everything/scripts/akinator_coverage.py` - the `skill-format` check parses
  every `SKILL.md`, requires `name` and `description` in frontmatter
  (**critical** if absent) and requires the When-to-use, When-NOT-to-use,
  Procedure and Definition-of-done sections.
- Mechanism: `tests/test_plugin_structure.py::test_every_skill_has_six_parts`
  asserts it for this repository's own skills, so the plugin cannot ship a skill
  it would reject in a target repo.
- Type: script check in CI, plus a unit test.
- How it fails: the coverage report names the skill and the missing section; the
  test names the file.
- Last observed passing: 2026-08-26

**Never a git hook** - see `rules/05-no-git-hook-complication.md`.

## Exceptions

A skill may omit **Failure modes and pitfalls** only when the procedure has
genuinely never failed in a way worth recording - which is rare enough that the
section should be present and say so:

```markdown
## Failure modes and pitfalls

None observed yet. Add the first one that occurs - the misleading symptom is
what makes this section worth more than the procedure.
```

No other part is optional.

## Related

- Skills: `akinator-skillify`, `akinator-anti-gaming`
- Templates: `templates/skill.md`, `templates/examples/skill.md`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] Enforcement mechanisms exist in the tree and are named by path.
- [x] The mechanisms are not git hooks.
- [x] Prohibited and correct patterns are shown.
- [x] The exception path is named.
- [x] The rule is indexed and reflected in every router.
