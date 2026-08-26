# Rule NN - <short imperative name>

> Template. Copy to `rules/NN-<short-name>.md`, keep the section order, delete
> this line and every angle-bracket placeholder. A rule that keeps a placeholder
> fails the coverage check.

## Purpose

<What breaks if this is violated, concretely. Not "for consistency" - name the
failure: the bug that ships, the data that corrupts, the customer who is charged
twice, the hour that is lost. If you cannot name a concrete failure, this is a
preference and belongs in `memory/`, not here.>

<If this rule exists because of a decision, link the ADR.>

## Applies to

- **In scope:** <paths, modules, situations>
- **Out of scope:** <what this deliberately does not cover, and where that is
  handled instead>

## Mandatory rules

<Testable propositions. Each one must be something a machine could, in
principle, decide about the tree.>

1. <e.g. "Quota fields are written only inside `src/quota/apply.ts`.">
2. <...>

## Prohibited patterns

<Real code, not a description of code. Show what someone actually writes when
they get this wrong.>

```<language>
// WRONG - <why>
<code>
```

## Correct pattern

```<language>
// RIGHT - <why>
<code>
```

## Enforcement

<The exact mechanism, by path, in backticks. It must exist in the tree before
this rule is written. The coverage check opens what you name here.>

- Mechanism: `<path/to/test-or-lint-rule-or-ci-step>`
- Type: <type system | linter | custom AST check | unit test | architecture
  test | CI step>
- How it fails: <what the developer sees when they violate this>
- Last observed passing: <YYYY-MM-DD>

**Never a git hook.** Git hooks gate code and must stay fast; knowledge and
constraint checks live in the type system, the test suite, CI and session
behavior. See `rules/05-no-git-hook-complication.md`.

## Exceptions

<When this rule legitimately does not apply, and how an exception is recorded -
an annotation, a suppression comment with a required reason, an entry in an
allowlist. A rule with no exception path gets violated silently instead of
deliberately.>

## Related

- Skills: <`skill-name`>
- Context: <`context/<map>.md`>
- Docs: <`docs/<page>.md`>
- ADR: <`docs/adr/NNNN-<slug>.md`>

## Definition of done

- [ ] The constraint is stated as a testable proposition.
- [ ] The enforcement mechanism exists in the tree and is named by path.
- [ ] The mechanism is not a git hook.
- [ ] Both a prohibited and a correct pattern are shown in real code.
- [ ] An exception path is named.
- [ ] The rule is indexed and reflected in every router.
