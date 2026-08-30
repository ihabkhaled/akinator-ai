---
name: ci-checkouts-are-shallow-by-default
type: surprise
date: 2026-08-30
---

# A test that reads git history can pass locally and fail only in CI

## The fact

`test_mining_this_repo_finds_its_own_repairs` (`tests/test_distil.py`) asserts
that `mine_git()` finds `fix:` commits in this repository's last year of
history. It passed on every local run and every prior CI run, then failed on
CI right after 1.1.0 shipped:

```
assert sightings, "this repository has fix: commits in the last year"
AssertionError: this repository has fix: commits in the last year
assert []
```

`repo = PosixPath('/home/runner/work/akinator-ai/akinator-ai')` - a GitHub
Actions runner. `actions/checkout@v4` defaults to `fetch-depth: 1`: one commit,
no history. `mine_git()` runs `git log --since=365.days` against that single
commit and, correctly, finds nothing - the miner was never broken, the checkout
was just missing the thing it mines.

## Why

The test constructs its evidence from the live repository rather than a
fixture, on the theory that a checker validated only against fixtures might not
work against reality (the same reasoning behind rule 11's mutation-test
mandate). That is the right idea, but it imported a hidden dependency: the test
now assumes "history exists," and nothing in the test or the CI config states
that assumption, so nobody thought to check it when the workflow was written.

The general lesson: **any test that reads git history needs a checkout deep
enough to have that history**, and the default GitHub Actions checkout does
not provide one. This class of bug is invisible locally by construction - a
local clone always has full history - so it can only ever be caught in CI,
which makes it easy to introduce and easy to leave unnoticed for a while if CI
runs are not watched.

## Date

- 2026-08-30 - recorded after `python scripts/akinator_distil.py detect` (also
  a git-log reader) was added to CI in the same release, alongside the
  pre-existing `mine_git` test, and the shallow-clone gap surfaced.

## Reversal conditions

- GitHub Actions changes its default checkout depth to full history.
- The test switches to a fixture-based check instead of reading this
  repository's live log, which would trade the "proven against reality"
  property for immunity to this class of bug - a real tradeoff, not a strict
  improvement.

## Related

- `.github/workflows/ci.yml` - `actions/checkout@v4` now passes
  `fetch-depth: 0`
- `tests/test_distil.py::test_mining_this_repo_finds_its_own_repairs`
- `rules/11-invariants-ship-with-a-mutation-test.md` - the same instinct
  (validate against something real, not just a fixture) that introduced this
  dependency in the first place
