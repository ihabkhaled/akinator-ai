# ADR 0003 - Knowledge enforcement lives outside git hooks

- **Status:** accepted
- **Date:** 2026-08-26
- **Deciders:** Ihab Khaled (owner)

## Context

Akinator enforces things: that a batch carries its knowledge delta, that rules
name live mechanisms, that routers do not fork, that artifacts are reachable.
Enforcement needs a home, and git hooks are the reflexive choice - they run
automatically and they block.

The owner's mandate was explicit and came from experience: *do not complicate
pre-commit and pre-push with non-code checks. Hooks gate code.*

The failure chain behind that mandate:

1. A hook that runs documentation checks makes commits slow.
2. Slow commits train people to batch unrelated work into one commit, destroying
   the reviewable history that was the reason to commit often.
3. Slow commits also train `--no-verify` as muscle memory - and once that is
   habitual, the *code* checks stop running too. Loading the hook with knowledge
   checks does not add enforcement; it removes it.
4. On a loaded machine a slow hook times out, and the developer reads a red
   commit as their change breaking something.

## Options considered

### Option A - Pre-commit hook

- **What it is:** run the coverage checker in `.husky/pre-commit` or equivalent.
- **Cost:** the full failure chain above. Also wrong in scope: the coverage
  checker is a whole-tree check, so it would run against a tree that includes
  unstaged work, producing findings unrelated to the commit.
- **Why it lost:** it is self-defeating. Hooks that people bypass enforce
  nothing, and it takes down the code checks with it.

### Option B - Pre-push hook

- **What it is:** the same checks, moved later, where slowness is less painful.
- **Cost:** milder but the same shape - and it fires at the worst moment, when
  someone is trying to land finished work, which maximizes the incentive to
  bypass.
- **Why it lost:** it delays discovery to the point of least willingness to act
  on it, and it still burns the developer's machine rather than CI's.

### Option C - Session behavior, CI and test invariants (chosen)

Three homes, each catching the problem at the right moment:

- **Session behavior** - `akinator-librarian` blocks a batch whose knowledge
  delta is missing. This fires *before a commit exists*, which is earlier and
  cheaper than any hook, and it can explain what is missing and which skill
  produces it.
- **CI** - `skills/everything/scripts/akinator_coverage.py` runs on every push, off the
  developer's machine, and can be made a required status check that genuinely
  cannot be bypassed.
- **Test invariants** - each rule's own mechanism runs with the normal suite.

- **Cost:** none of the three is as reflexive as a hook. A developer working
  without an Akinator-governed session and pushing to a branch with no CI would
  be unenforced until the pull request.
- **Why it won:** it catches the problem earlier (the librarian), enforces it
  more strongly where it matters (a required CI check cannot be `--no-verify`'d),
  and never makes the developer's commit slow.

## Decision

Akinator never adds knowledge, documentation, coverage, index, router-sync or
memory checks to any git hook, in this repository or in any repository it
onboards. Enforcement lives in session behavior, CI, and test invariants.

Where a target repository already has knowledge checks in its hooks, Akinator
reports it as a critical finding and proposes moving it - it does not silently
remove the repo's own configuration.

## Consequences

**Good**
- Commits stay fast, so hooks keep their credibility for the code checks that
  belong in them.
- The librarian catches missing knowledge before a commit exists, with an
  explanation rather than an exit code.
- CI enforcement cannot be bypassed locally.

**Bad**
- A contributor who never runs an Akinator-governed session and pushes to a
  branch without CI is unenforced until review.
- Feedback arrives later than a hook would give it, for that contributor.

**Debt taken on**
- None. The rule has no exception path, deliberately: every past proposal took
  the form "just this one fast check", which is how the hook stack grew last
  time.

## Revisit when

- A pre-commit mechanism appears that is genuinely instant and cannot be
  bypassed - which would change the cost side of the analysis, though not the
  scope argument about whole-tree checks.
- Never for "just one fast check". That is the failure mode, not an exception.

## Related

- Rules: `rules/05-no-git-hook-complication.md`
- Agents: `agents/akinator-librarian.md`
- Code: `skills/everything/scripts/akinator_coverage.py` - the `git-hooks` check
- Docs: `docs/architecture.md` - the three enforcement homes

_Paths updated 2026-09-18: the host-repository tools moved into the one skill (`skills/everything/scripts/`) under ADR 0009; the decision above is unchanged._
