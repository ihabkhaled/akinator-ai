# Rule 06 - Gate once, at the end, scoped to what was touched

## Purpose

Running the full lint, typecheck, test and build loop after every change is the
most expensive habit available. It proves the same thing repeatedly while the
tree keeps changing underneath it, and on a loaded machine it produces timeout
flakiness that reads as real failure - so time is then spent debugging the
machine instead of the code.

The second cost is subtler: a developer who has watched twelve gate runs stops
reading the output. The gate that finally goes red gets skimmed.

## Applies to

- **In scope:** every lint, typecheck, test-suite and build invocation during
  multi-step work, in this repository and in every repository an
  Akinator-governed session touches.
- **Out of scope:** a tight scoped loop while debugging one specific failure -
  running the single failing test repeatedly *is* the work. Also out of scope: a
  gate the user explicitly asks for right now. Their instruction wins.

## Mandatory rules

1. No commits and no pushes mid-batch. Build the coherent batch first.
2. Gates run **once**, at the end of the batch.
3. The gate is scoped to the workspaces actually touched, determined from the
   diff - never all-workspace when two workspaces changed.
4. When a gate fails, fix it and re-run **only** the failed check in the failed
   scope.
5. Results are judged by **real exit codes**, never by a notification summary or
   the last lines of output.
6. Once a tree is proven green, nothing re-proves that same tree. Record a
   tree-bound receipt; a single changed byte voids it.
7. No check is ever weakened, deleted, loosened or suppressed to obtain green.

## Prohibited patterns

```bash
# WRONG - after every file
edit src/a.ts && npm run lint && npm run typecheck && npm test && npm run build
edit src/b.ts && npm run lint && npm run typecheck && npm test && npm run build
```

```bash
# WRONG - all-workspace for a two-file change
npm test                    # every package in the monorepo
```

```bash
# WRONG - green obtained by weakening
- expect(result.quota).toBe(9);
+ expect(result.quota).toBeDefined();
```

```bash
# WRONG - judged by summary
npm test > out.log 2>&1; echo "tests finished"    # exit code discarded
```

## Correct pattern

```bash
# RIGHT - one scoped gate at the end of the batch
npm run typecheck -w packages/billing -w services/api
npm test -w packages/billing -w services/api
echo "exit=$?"

# fix the one red test, then re-run only it
npm test -w packages/billing -- -t "restores quota on partial refund"
```

```bash
# RIGHT - a tree-bound receipt, so nothing re-proves this tree
git stash create > .ai/local/gate-receipt-tree
# receipt records: tree hash, gates run, scope, exit codes, timestamp
```

## Enforcement

- Mechanism: `skills/everything/references/akinator-gate-economy.md` - session behavior. This is
  the primary enforcement: the skill fires before any gate command and before any
  commit during multi-step work.
- Mechanism: `agents/akinator-pm.md` - reviews completion claims and rejects any
  backed by a summary rather than an exit code.
- Mechanism: `skills/everything/scripts/akinator_coverage.py` - the `git-hooks` check catches the
  related failure of loading hooks with slow checks, which is what makes
  per-commit gating painful enough to be bypassed.
- Type: session behavior and review lens. **Not machine-checkable** - whether a
  gate ran mid-batch is a fact about the session, not about the tree, and an
  automated approximation (counting CI runs, inspecting reflog) would produce
  false failures that train people to ignore it.
- How it fails: the gate-economy skill states the rule before the command runs;
  the PM agent rejects the completion claim.
- Last observed passing: 2026-08-26

**Never a git hook** - see `rules/05-no-git-hook-complication.md`. Putting this
rule in a hook would be self-defeating: slow hooks are the thing that makes
per-commit gating expensive in the first place.

## Exceptions

- **Debugging a specific failure.** Run the failing test as often as needed,
  scoped to that test. This is not a gate; it is the work.
- **The user asks for a gate now.** Run it. A direct instruction outranks this
  rule, and saying so is not a violation.
- **A pre-landing verification the repo's policy requires.** Honor the repo's
  policy; use the receipt to avoid the duplicate pass where the policy permits
  it, and never to hide a failure.

## Related

- Skills: `akinator-gate-economy`, `akinator-resource-guard`, `akinator-plan`
- Agents: `akinator-pm`
- ADR: `docs/adr/0004-gate-receipts-over-hook-bypass.md`

## Definition of done

- [x] The constraint is stated as a set of testable propositions.
- [x] Enforcement mechanisms exist in the tree and are named by path.
- [x] The mechanisms are not git hooks.
- [x] Prohibited and correct patterns are shown.
- [x] The exception path is named.
- [x] The non-machine-checkable classification is stated and justified, per
      `rules/03-rules-need-live-enforcement.md`.
- [x] The rule is indexed and reflected in every router.
