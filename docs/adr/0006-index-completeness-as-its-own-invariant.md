# ADR 0006 - Index completeness is a separate invariant, and CI runs at --strict

- **Status:** accepted
- **Date:** 2026-08-26
- **Deciders:** Ihab Khaled (owner)

## Context

Running `akinator-everything` against this repository surfaced a gap between a
stated law and an enforced one.

The taxonomy's second law is *"every artifact reachable from an index; unindexed
means nonexistent."* The `reachability` check proved something weaker: that an
artifact is referenced from **some** markdown file anywhere in the tree. An
artifact linked only from a router, or only from a sibling doc, satisfied it
while remaining invisible to a reader who opens the category index and reads
down the list - which is exactly how a fresh agent looks for things.

Two decisions followed, and both had real alternatives.

## Decision 1 - a separate check, not a stronger `reachability`

### Option A - tighten `reachability` to require the category index

- **What it is:** change the existing check to demand index membership rather
  than any reference.
- **Cost:** it collapses two distinct defects into one finding. "Nothing links
  this at all" and "this is linked but not from its own index" need different
  fixes and carry different urgency. It also silently re-scopes a check that
  target repositories already run, turning a passing layer into a failing one on
  upgrade with no new information about why.
- **Why it lost:** a repository with no category index for a kind of knowledge
  would start failing for a reason the message no longer distinguishes.

### Option B - a separate `index-completeness` check (chosen)

- **What it is:** a new invariant covering twelve categories. Where a category
  has no index at all, it defers to `reachability` rather than double-counting.
- **Cost:** eleven checks instead of ten, and one more thing to keep true.
- **Why it won:** the two findings stay separable, the message names the index
  the reader would have browsed, and the deferral rule means a repo mid-onboarding
  sees one finding per defect rather than two.

## Decision 2 - CI at `--strict`, not raising the findings to HIGH

Both `reachability` and `index-completeness` emit MEDIUM. CI ran
`--fail-on high`. A review lens deleted a row from `docs/skills.md` and watched
CI stay green - so the invariant existed and protected nothing. That had been
true of `reachability` since it was written and was never noticed.

### Option A - raise both findings to HIGH

- **Cost:** it changes the severity every *target* repository sees. A repo part
  way through onboarding would face a wall of HIGH findings on day one, and the
  predictable response is to switch the check off entirely.
- **Why it lost:** severity should describe the defect, not the tier one
  repository wants to enforce at. An unindexed artifact is a real but recoverable
  problem - MEDIUM is the honest grade.

### Option B - CI runs `--strict` (chosen)

- **Cost:** this repository now fails CI on any MEDIUM, including ones a target
  repo would reasonably defer. It is a stricter bar than the tool's default, and
  a contributor has to know that the default command is not the CI command -
  which is why every router carries a "Coverage check (strict)" row.
- **Why it won:** the severity stays honest for everyone, and the repository that
  ships the checker holds itself to the full bar. Onboarding repos keep a default
  that does not drown them.

### Option C - leave it, and document that the checks are advisory in CI

- **Why it lost:** an invariant that CI does not enforce is a rule with no live
  mechanism, which `rules/03-rules-need-live-enforcement.md` exists to forbid.

## Consequences

**Good**
- The taxonomy's second law is now enforced as written rather than approximated.
- A delisted artifact fails CI. Verified by mutation, not assumed.
- Severity stays meaningful across repositories with different maturity.

**Bad**
- Two commands where there was one: the default tier and the CI tier differ, and
  someone will run the default, see green, and be surprised by CI.
- `--strict` also gates on `staleness` and `generated`, so an unrelated MEDIUM
  can now block a merge here.

**Debt taken on**
- `index-completeness` looks one level deep and compares case-insensitively on
  Windows. Both limits are stated in `skills/everything/references/akinator-coverage.md` and
  tested. Pay down if a repository grows nested category directories.

## Revisit when

- A target repository reports that MEDIUM is the wrong grade for an unindexed
  artifact in practice.
- The nesting limit produces a real miss.
- `router-sync` is extended to compare factual claims rather than links, which
  would remove the adjacent gap this batch also found.

## Related

- Code: `skills/everything/scripts/akinator_coverage.py` - `check_index_completeness`, `_indexed_paths`
- Tests: `tests/test_coverage_checker.py`
- Docs: `docs/architecture.md` - enforcement homes and the tier rationale
- Memory: `memory/2026-08-26-checkers-fail-silently-in-both-directions.md`
- Rules: `rules/03-rules-need-live-enforcement.md`

_Paths updated 2026-09-18: the host-repository tools moved into the one skill (`skills/everything/scripts/`) under ADR 0009; the decision above is unchanged._
