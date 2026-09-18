# Rule 11 - Every invariant ships with a test that proves it fires

## Purpose

A checker cannot be validated by running it on a healthy tree and seeing zero
findings. **Zero findings is exactly what a broken checker produces.**

This failed three times in one session, each fix producing the next failure:

```
bare substring   `demo` satisfied by a listed `demo-extended`; the master
                 skill unflaggable because its name is inside every sibling
word-bounded     `docs/overview.md` satisfied by a link to `adr/overview.md`
path-bounded     six false positives on suites listed with a directory prefix
```

A fourth instance followed in the same session and is the clearest of all: a
regex lost its trailing word boundary to a shell escape and compiled to a
literal backspace. The check ran, reported a clean tree, and matched nothing at
all. Every test written alongside it passed throughout.

The asymmetry is what makes this rule necessary. A **false positive is loud** -
someone sees a wrong finding and either fixes the check or stops trusting it,
and either way it is discovered. A **false negative is silent** - the check
reports green, everyone believes it, and the invariant has quietly stopped
existing.

## Applies to

- **In scope:** every check registered in `CHECKS` in
  `skills/everything/scripts/akinator_coverage.py`, and every drift check shipped by a generator
  in `scripts/`.
- **Out of scope:** tests of ordinary behavior, where a passing test on correct
  input is meaningful evidence. This rule is specifically about **detectors**,
  whose whole job is to notice something wrong.

## Mandatory rules

1. Every registered check has at least one test that **constructs a violating
   tree and asserts the check fires on it**.
2. Every registered check has at least one test that asserts it stays **silent**
   on a healthy tree. A detector that fires on everything protects nothing, and
   it is the failure mode that gets checkers disabled.
3. A check whose matching rule changes gets a **new** regression test for the
   case that broke, not an edit to the old one. The old case must keep passing.
4. Before a new invariant is called done, it is mutation-tested against the real
   repository: break the invariant on purpose, confirm the finding, restore.

## Prohibited patterns

```python
# WRONG - the only evidence is a clean run on a healthy tree
def test_new_invariant() -> None:
    assert not by_check(healthy_repo, "new-invariant")
```

This passes identically whether the check works or does nothing at all.

```python
# WRONG - asserting the check ran, not that it detected
def test_new_invariant(repo) -> None:
    findings = run_checks(repo, [], [], 40)
    assert isinstance(findings, list)
```

## Correct pattern

```python
# RIGHT - a violating tree, and a specific expected finding
def test_flags_artifact_missing_from_its_category_index(tmp_path) -> None:
    root = build_repo_where_a_rule_is_linked_but_not_indexed(tmp_path)

    # precondition: the neighbouring check stays quiet, so this test cannot
    # pass for the wrong reason
    assert not [f for f in by_check(root, "reachability") if "hidden" in f.path]

    hits = by_check(root, "index-completeness")
    assert [f.path for f in hits] == ["rules/02-hidden.md"]
```

## Enforcement

- Mechanism: `tests/test_coverage_checker.py::test_every_invariant_has_a_test_that_proves_it_fires`
  - a meta-test that walks `CHECKS` and requires each check id to appear in a
  test asserting a non-empty result. A check registered without one fails the
  suite.
- Mechanism: `tests/test_coverage_checker.py` - the per-check firing tests
  themselves, one per registered invariant.
- Type: unit tests, run with the suite and in CI.
- How it fails: the meta-test names the check id that has no firing test.
- Last observed passing: 2026-08-26

**Never a git hook** - see `rules/05-no-git-hook-complication.md`.

## Exceptions

None for a registered check.

If an invariant is genuinely impossible to violate in a fixture - which has not
happened yet - say so in the check's docstring with the reason, and the
meta-test's allowlist gets an entry with that reason. An allowlist entry is a
reviewable claim; a missing test is an invisible one.

## Related

- Ledger: `.ai/ledger/failure/checker-silent-false-negative-a1b2c3d4e5f6.md` -
  the three occurrences that produced this rule
- Memory: `memory/2026-08-26-checkers-fail-silently-in-both-directions.md`
- Skills: `akinator-anti-gaming` - "never weaken a check to make it pass"; this
  is the adjacent failure, where a check is weak by accident
- Rules: `rules/03-rules-need-live-enforcement.md`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] The enforcement mechanism exists in the tree and is named by path.
- [x] The mechanism is not a git hook.
- [x] Prohibited and correct patterns are shown.
- [x] The exception path is named and requires a reviewable claim.
- [x] The rule is indexed and reflected in every router.
