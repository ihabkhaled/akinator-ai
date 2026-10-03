# Rule 14 - Every changed path is traced

## Purpose

A diff that changes a source file and nothing that explains it leaves the
next reader to reverse-engineer the change. Rule 01 declares a knowledge delta
per batch; this rule makes the declaration checkable per path. Every changed
path must be traceable to a place where the change is written down, or
explicitly declared to need none, with a reason.

## Applies to

- **In scope:** every path in a diff - the working tree, or `REF...HEAD`.
- **Out of scope:** paths that are themselves knowledge artifacts or generated
  files (docs, rules, memory, context, `.ai/`, templates, routers, README,
  CHANGELOG, the generated pack), and paths exempted in `.ai/config.json`
  under `trace.ignore`.

## Mandatory rules

1. Every changed path is accounted for: it is a knowledge artifact, or it is
   named (exact path, parent directory with trailing slash, or glob) in a
   change record that is itself part of the same diff.
2. A change record that was not changed in the diff explains nothing about it.
3. An exemption is the exact line `knowledge delta: none, because <reason>`
   with a reason of at least 10 characters, and it covers only the paths listed
   as `- path` bullets under it.
4. The check fails closed: no git repository or a bad ref is exit 2, never a
   silent pass.

## Prohibited patterns

```
knowledge delta: none, because ok
- <changed-path>
```

A reason too short to be a reason covers nothing.

## Correct pattern

```
knowledge delta: none, because pure rename with no behavior change
- <changed-path>
```

## Enforcement

- Mechanism: `skills/everything/scripts/akinator_trace.py check` - exits 1
  naming every unaccounted path and the knowledge homes it implicates.
- Mechanism: `tests/test_trace.py` - a positive and a mutation case for every
  invariant: an unaccounted file fails, a mention in a record outside the diff
  fails, a too-short reason fails, a covered path passes, a docs-only diff
  passes, a bad ref exits 2.
- Type: unit and integration tests on temporary git repositories.
- How it fails: `check` lists each path with its implicated homes.
- Last observed passing: 2026-10-03

**Never a git hook** - see `rules/05-no-git-hook-complication.md`.

## Exceptions

The `knowledge delta: none, because` line, with a stated reason, per path.

## Related

- Rules: `rules/01-knowledge-delta-per-batch.md` - declares the delta; this
  rule checks it path by path
- Rules: `rules/11-invariants-ship-with-a-mutation-test.md`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] The enforcement mechanism exists in the tree and is named by path.
- [x] The mechanism is not a git hook.
- [x] Prohibited and correct patterns are shown.
- [x] The exception path is named.
- [x] The rule is indexed.
