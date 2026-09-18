# Rule 03 - Every rule names an enforcement mechanism that exists

## Purpose

A constraint written as prose and enforced by nothing is not a rule. It is a
hope, and it will be broken within a quarter by a well-meaning contributor whose
review is done by someone who was not in the original conversation.

Worse is the rule that *names* a mechanism which does not exist - a test file
never written, a lint rule since removed, a CI step that was renamed. That rule
reads as enforced. Everyone downstream believes the constraint is held
mechanically, and nobody checks. It is fake compliance with a paper trail.

## Applies to

- **In scope:** every file in `rules/` in this repository, and every rule an
  Akinator-governed session writes into a target repository.
- **Out of scope:** a target repo's pre-existing rules on the day it is
  onboarded - those become findings, not failures. Also out of scope: constraints
  the platform already makes impossible (the type system, the compiler), which
  do not need a separate mechanism, only a note pointing at the one that exists.

## Mandatory rules

1. Every rule has an **Enforcement** section.
2. That section names at least one mechanism **by path, in backticks**, and that
   path exists in the tree.
3. The mechanism was run at least once and observed to pass, and the rule records
   the date it was last observed passing.
4. The mechanism is not a git hook - see `rules/05-no-git-hook-complication.md`.
5. The rule states what the developer sees when they violate it.
6. The rule names an exception path, or states explicitly that having none is
   deliberate.

## Prohibited patterns

```markdown
## Enforcement

Reviewers should check this during code review.
```

Review-only enforcement decays. It is acceptable as a *supplement*, never as the
whole mechanism.

```markdown
## Enforcement

- Mechanism: `tests/architecture/quota-single-writer.test.ts`
```

...when that file does not exist. This is the failure the coverage checker
treats as **critical**, because it is indistinguishable from real enforcement
until someone violates the rule and nothing happens.

## Correct pattern

```markdown
## Enforcement

- Mechanism: `skills/everything/scripts/akinator_coverage.py` - the `rule-enforcement` check
  opens every path named in an Enforcement section and fails if it is absent.
- Type: script check in CI.
- How it fails: the report prints the rule path and the missing mechanism.
- Last observed passing: 2026-08-26
```

The mechanism exists, the failure mode is described, and the date makes staleness
visible.

## Enforcement

- Mechanism: `skills/everything/scripts/akinator_coverage.py` - the `rule-enforcement` check
  reports **high** for a rule with no Enforcement section, **critical** for one
  naming only paths that do not exist, and **critical** for one naming a git
  hook.
- Mechanism: `tests/test_coverage_checker.py::test_flags_rule_naming_absent_mechanism`
  asserts the detection works on a fixture, so this rule's own enforcement
  cannot silently rot.
- Type: script check in CI, plus a unit test.
- How it fails: the coverage report names the rule, the absent mechanism, and
  the skill that fixes it.
- Last observed passing: 2026-08-26

## Exceptions

A rule may name a **CODEOWNERS entry plus review** as its sole mechanism when the
constraint is genuinely not machine-checkable - a judgment call about tone,
naming quality or API ergonomics. Such a rule must say so explicitly:

```markdown
- Type: human review (not machine-checkable - the constraint is a judgment call
  about X, and an automated approximation would produce false failures that
  train people to ignore it).
```

The exception is for constraints that *cannot* be checked, never for ones that
have not been.

## Related

- Skills: `akinator-rule-forge`, `akinator-anti-gaming`
- Templates: `templates/rule.md`, `templates/examples/rule.md`
- Rules: `rules/05-no-git-hook-complication.md`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] Enforcement mechanisms exist in the tree and are named by path.
- [x] The mechanisms are not git hooks.
- [x] Prohibited and correct patterns are shown.
- [x] The exception path is named and narrowly scoped.
- [x] The rule is indexed and reflected in every router.
