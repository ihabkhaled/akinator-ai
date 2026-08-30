---
name: a-claim-is-only-true-relative-to-a-tree
type: surprise
date: 2026-08-30
---

# A claim is only true relative to a tree, and every test checked the same tree

## The fact

Twenty-one tests covered the Codex pack. One of them was literally named
`test_portable_contract_names_no_repo_relative_paths`. Every one of them read
the pack from inside this checkout.

From inside this checkout, `scripts/build_codex_pack.py` exists, so a banner
naming it is true. Install the same file into another repository - which is the
file's entire purpose - and the same sentence becomes a lie. A bare repo running
`install-codex.sh` and then the coverage checker got **22 HIGH findings on its
first run**, every one on a file the plugin had just written.

The near-miss makes the point better than the miss. The portable contract *had*
been given the portability treatment, deliberately, with a docstring explaining
why it named no repo-relative paths. It named `build_codex_pack.py` instead -
no slash, so not a path - and the test filtered on `"/" in name`. The bug and
the test that was supposed to catch it were written in the same hour, by the
same reasoning, and agreed with each other.

## Why

A path is not a fact. It is a claim *about a tree*, and it carries an unstated
argument: the tree the author happened to be standing in.

Tests inherit that argument silently. `repo` in this suite is always
`d:/Freelance/akinator-ai`, so every assertion about the pack was really an
assertion about the pack *here* - and for an artifact defined by travelling
elsewhere, that is the one place where its correctness does not matter.

This is the same asymmetry as
[[checkers-fail-silently-in-both-directions]], one level up. There, a check
could pass by never firing. Here, a test could pass by never changing the
premise it was quietly assuming. Both fail green.

The habit that falls out: **for any artifact that leaves this repository, at
least one test must construct the destination.** Not mock it, not reason about
it - build a scratch tree, put the artifact in it, and run the real check there.
`test_the_installed_pack_leaves_a_target_repo_clean` does exactly that in about
fifteen lines, and it is the only test in the suite that evaluates something
from anywhere but here.

Worth noting how it was found: two red-team agents in eval 06, in fresh
contexts, both under explicit pressure to take a shortcut ("just add a docs
file", "just loosen the check"). Both refused, went looking for the real
problem, and landed on this. It could not have been found by asking someone to
look for it, because the search would have started from the same tree.

## Date

- 2026-08-30 - recorded after reproducing 22 HIGH findings on a bare repository.

## Reversal conditions

- The pack stops being copied and starts being referenced in place - a symlink,
  a package dependency, anything that keeps one canonical copy. Then a path in
  the banner is true again, and the rule becomes noise.
- The coverage checker gains a notion of artifact provenance strong enough that
  banner prose stops being the carrier of this information.

## Related

- `rules/12-artifacts-that-travel-name-nothing-local.md` - the rule this
  produced
- `docs/adr/0007-vendored-artifacts-declare-origin-not-generator.md` - why the
  checker learned "vendored" instead of exempting `.agents/`
- `.ai/ledger/failure/a-generated-artifact-that-travels-named-56871dcd648a.md`
- `evals/results/2026-08-30-06-anti-gaming.md` - the run that found it
- [[checkers-fail-silently-in-both-directions]] - the same green-failure
  asymmetry, applied to detectors rather than to premises
- [[verify-contracts-from-installed-plugins]] - the earlier instance of the same
  root habit: check the thing where it actually runs, not where it was authored
