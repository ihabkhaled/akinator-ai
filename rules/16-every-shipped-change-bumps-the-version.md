# Rule 16 - Every shipped change bumps the version

## Purpose

A plugin that changes without changing its version cannot be updated, rolled
back or reasoned about: installs cache by version, so a fix that keeps the old
number never reaches anyone, and a changelog with no matching heading hides what
moved. Version drift between manifests is the quieter form of the same failure -
one manifest says 2.1.0, another 2.2.0, and each tool reads a different truth.

## Applies to

- **In scope:** every change to a shipped path - `skills/`, `agents/`, `hooks/`,
  `install.sh`, `install.ps1`, `templates/`, the plugin manifests and the
  generated `.agents/` pack. The list is overridable in `.ai/config.json` under
  `version.shipped`.
- **Out of scope:** docs, rules, memory, context, tests and CI changes that touch
  no shipped path.

## Mandatory rules

1. Every version manifest that exists declares the same version.
2. A change to a shipped path is accompanied, in the same diff, by a version
   strictly greater (semantic-version order, not text order) than at the base.
3. The current version has a `## [<version>]` heading in `CHANGELOG.md`.
4. The bump is made with the tool, never by hand-editing one manifest:
   `akinator_version.py next` suggests the level, `bump` rewrites every manifest
   and seeds the heading, `check` proves it.
5. The tool reads no clock: the date is given with `--date`.

## Prohibited patterns

- Editing one manifest's version string by hand.
- Shipping a fix under the old number "because it is tiny".
- A changelog heading with no change behind it, or a change with no heading.

## Correct pattern

```
python skills/everything/scripts/akinator_version.py next --base HEAD
python skills/everything/scripts/akinator_version.py bump minor --date 2026-10-03
python skills/everything/scripts/akinator_version.py check --base HEAD
```

## Enforcement

- Mechanism: `skills/everything/scripts/akinator_version.py check` - exits 1 when
  manifests disagree, when a shipped path changed since the base without a
  greater version, or when the changelog heading is missing; exits 2 on a bad ref.
- Mechanism: `tests/test_version.py` - a passing and a mutation case per
  invariant, on temporary git repositories: each manifest disagreeing in turn,
  a shipped change with no bump, a lower version, a missing heading, a bad ref.
- Mechanism: `.github/workflows/ci.yml` - runs `check` always, and
  `check --base HEAD~1` on push.
- Type: unit and integration tests, plus CI.
- How it fails: `check` prints each finding with the first offending path.
- Last observed passing: 2026-10-03

**Never a git hook** - see `rules/05-no-git-hook-complication.md`.

## Exceptions

None for a shipped path. A change that touches only unshipped paths needs no bump.

## Related

- Rules: `rules/14-every-changed-path-is-traced.md` - the same per-diff idea for
  knowledge; `rules/11-invariants-ship-with-a-mutation-test.md`
- ADR: `docs/adr/0012-always-followed-and-version-discipline.md`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] The enforcement mechanism exists in the tree and is named by path.
- [x] The mechanism is not a git hook.
- [x] Prohibited and correct patterns are shown.
- [x] The exception path is named.
- [x] The rule is indexed.
