# Rule 05 - Never put knowledge checks in git hooks

## Purpose

Git hooks gate **code**, and they must stay fast. A pre-commit hook that also
runs documentation checks, coverage audits, index verification or router-sync
validation produces three failures, in this order:

1. **Slow commits.** A commit that takes 40 seconds trains people to batch
   unrelated work into one commit, which destroys the reviewable history that
   was the reason to commit often.
2. **Bypassed hooks.** Once commits are slow, `--no-verify` becomes muscle
   memory - and then the *code* checks stop running too. Loading the hook with
   knowledge checks does not add enforcement; it removes it.
3. **Timeout flakiness that reads as real failure.** On a loaded machine a slow
   hook times out. The developer sees a red commit, assumes their change broke
   something, and spends twenty minutes debugging the machine.

This was learned expensively. It is the reason Akinator ships a coverage
checker that is explicitly documented as CI-and-on-demand only.

Knowledge enforcement has three correct homes, all of which are more reliable
than a git hook: **session behavior** (the librarian agent, blocking the batch),
**CI** (the coverage checker), and **unit-test invariants** (a rule's
enforcement mechanism running with the suite).

## Applies to

- **In scope:** every hook Akinator or an Akinator-governed session would add to
  a repository - `.git/hooks/*`, `.husky/*`, `.pre-commit-config.yaml`,
  `lefthook.yml`, and any equivalent - in this repository and in every repository
  Akinator onboards.
- **Out of scope:** hooks that gate code and nothing else - a fast formatter, a
  scoped linter on changed files, a commit-message format check. Those are
  legitimate. This rule is about *what* the hook runs, not about hooks existing.

## Mandatory rules

1. No Akinator skill, command, agent or onboarding procedure adds a
   documentation, knowledge, coverage, index, router-sync or memory check to any
   git hook.
2. `scripts/akinator_coverage.py` is never invoked from a git hook. Its own
   docstring says so, and the `git-hooks` check in it detects the violation.
3. Onboarding a repository never installs a git hook. If a target repo asks for
   knowledge enforcement, it gets a CI step.
4. Where a target repo *already* has knowledge checks in its hooks, Akinator
   reports it as a critical finding and proposes moving it to CI - it does not
   silently remove the repo's own configuration.

## Prohibited patterns

```bash
# WRONG - .husky/pre-commit
npm run lint-staged
python scripts/akinator_coverage.py --strict   # knowledge check in a hook
```

```yaml
# WRONG - .pre-commit-config.yaml
- repo: local
  hooks:
    - id: akinator-coverage
      name: Akinator knowledge coverage
      entry: python scripts/akinator_coverage.py
      language: system
```

## Correct pattern

```yaml
# RIGHT - .github/workflows/coverage.yml
- name: Akinator coverage
  run: python scripts/akinator_coverage.py . --fail-on high
```

```bash
# RIGHT - .husky/pre-commit (code only, fast, scoped)
npm run lint-staged
```

Plus the two non-CI homes:

- **Session behavior** - the `akinator-librarian` agent blocks a batch whose
  knowledge delta is missing. This catches the problem before a commit exists,
  which is earlier and cheaper than any hook.
- **Test invariants** - `tests/test_coverage_checker.py` and each rule's own
  enforcement mechanism run with the normal suite.

## Enforcement

- Mechanism: `scripts/akinator_coverage.py` - the `git-hooks` check scans
  `.git/hooks/`, `.husky/` and `.pre-commit-config.yaml` for knowledge-check
  markers and reports any hit as **critical**.
- Mechanism: the same script's `rule-enforcement` check reports **critical** for
  any rule whose Enforcement section names a git hook.
- Mechanism: `tests/test_coverage_checker.py::test_detects_knowledge_check_in_git_hook`
  asserts the detection works, so the enforcement cannot silently rot.
- Type: script check in CI, plus a unit test.
- How it fails: the coverage report prints the offending hook file, the matched
  markers, and this rule's path; CI exits non-zero.
- Last observed passing: 2026-08-26

**This rule's own enforcement is not, and must never be, a git hook.**

## Exceptions

None. This is one of the few rules in Akinator with no exception path, and that
is deliberate: every proposed exception in the past took the form "just this one
fast check", which is exactly how the hook stack grew the last time.

If a repository genuinely needs a knowledge check to block a merge, that is what
a **required CI status check** is for. It blocks the merge, runs off the
developer's machine, and cannot be bypassed with `--no-verify`.

## Related

- Skills: `akinator-rule-forge`, `akinator-gate-economy`, `akinator-onboard`
- Agents: `akinator-librarian` - the session-behavior enforcement home
- Docs: `docs/architecture.md` - enforcement homes
- ADR: `docs/adr/0003-enforcement-outside-git-hooks.md`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] The enforcement mechanism exists in the tree and is named by path.
- [x] The mechanism is not a git hook.
- [x] Both a prohibited and a correct pattern are shown in real code.
- [x] The absence of an exception path is deliberate and justified.
- [x] The rule is indexed and reflected in every router.
