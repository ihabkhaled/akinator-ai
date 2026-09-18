# ADR 0007 - A vendored artifact declares its origin, not a generator

- **Status:** accepted
- **Date:** 2026-08-30
- **Deciders:** Ihab Khaled (owner)

## Context

Two red-team agents in eval 06, run in fresh contexts against separate
workspaces, independently reported the same defect while refusing the shortcut
they had been asked to take. Reproduced on a bare repository:

```
$ sh scripts/install-codex.sh --repo target
$ python scripts/akinator_coverage.py target
22 finding(s) at or above 'high' - FAIL
```

Every finding was on a file the plugin had just written. The 21 packed skills
carried banners naming `scripts/build_codex_pack.py` and
`skills/<name>/SKILL.md`; the portable contract named `build_codex_pack.py`.
None exists in a repository that installs the pack. `check_generated` read each
banner as a claim about a local file, found no such file, and correctly reported
a lie - which it was.

This is the plugin's own thesis turned against it. The premise of Akinator is
that a document asserting things that are not there is a critical defect, and
installing it produced 22 of them.

Fixing the banners is obvious. The design question is what the **checker** should
believe, because a banner that names no generator falls into the existing
"declares itself generated but names no generator" branch and emits MEDIUM,
which fails `--strict` - the tier ADR 0006 put CI on. Making the pack clean in a
target repo is therefore not a string swap.

The second-order question is the one the red-team agent declined to answer for
us, correctly: *"that's a design call I'd want you to make rather than guess
at."*

## Decision 1 - what the checker accepts

### Option A - exempt `.agents/` from the `generated` check

- **What it is:** the checker skips any file under `.agents/`, on the grounds
  that it is a vendored tree.
- **Cost:** it is a path-shaped exemption for a property that is not about
  paths. Any repository could move anything into `.agents/` to silence the
  check, and the checker's own ignore mechanism is deliberately kept simple so a
  repo cannot quietly exclude its way to green. It also stops checking the pack
  in the one repository that generates it.
- **Why it lost:** it converts a specific, checkable claim into a directory
  amnesty. The `akinator-anti-gaming` skill names suppression-by-scope as a
  gaming pattern; adding one to the checker itself would be indefensible.

### Option B - teach the checker that a file may be vendored (chosen)

- **What it is:** a file whose banner declares **where it came from** and **how
  to refresh it** needs no local generator. Both halves are required. A banner
  that still names a generator is checked exactly as before, whatever else it
  says.
- **Cost:** one more accepted form, and the words that trigger it
  (`installed from`, `reinstall`) are matched textually, so a repository willing
  to write a false origin can silence the check. That is a lie in a document,
  which is the class of defect no checker catches, and is not made materially
  easier by this branch.
- **Why it won:** it keeps the invariant honest rather than exempting a
  location. The underlying requirement never changes - *a file that declares
  itself generated must tell the reader how to obtain a correct copy* - and this
  simply recognises that "reinstall the thing that put it here" is a complete
  answer for an artifact whose generator is deliberately elsewhere.

### The ordering that matters

The vendored branch runs **after** the named-generator check, not before. This
banner is still flagged when the file it names is absent:

```
<!--
Installed from the Akinator plugin. To update: reinstall Akinator,
or regenerate with `scripts/some_extractor.py`.
-->
```

Had the branches been ordered the other way, "installed from" would have become
a phrase you write to silence the check, and the escape hatch would have been
the hole. This is asserted directly by
`test_claiming_vendored_status_does_not_excuse_a_dead_generator_path`.

## Decision 2 - what the banner says instead

### Option A - name the generator by bare filename

- **What it is:** `build_codex_pack.py` rather than `scripts/build_codex_pack.py`.
- **Cost:** none of the falsehood is removed. The host repository does not have
  a file by that name either; the claim is merely shorter.
- **Why it lost:** it had already been tried. `contract_banner` used exactly this
  form, and `test_portable_contract_names_no_repo_relative_paths` passed it
  because the test filtered on `"/" in name`. The bug and its test agreed with
  each other for weeks.

### Option B - name nothing; state origin and refresh path (chosen)

- **What it is:** the banner says which plugin installed the file, which
  canonical skill it corresponds to, that no generator is named *and why*, and
  how to refresh it in both the host case and the checkout case.
- **Cost:** an Akinator contributor no longer reads the regeneration command off
  the file itself. It lives in `rules/07-codex-pack-is-generated.md` and the
  repository's own router, which is where a contributor already looks.
- **Why it won:** the banner becomes true in every tree it can occupy, which is
  the only property that matters for a file whose defining characteristic is
  that it travels. Stating *why* no path is named also stops the next
  contributor from helpfully adding one back.

## Consequences

**Good.** Installing Akinator now leaves a bare repository clean at `--strict`.
The checker gained an honest concept it was missing - artifacts do get vendored,
and demanding a local generator for them inverted the check.

**Bad.** The vendored form is recognised by two textual markers. A misspelling
("installed *via*") silently falls back to the MEDIUM branch rather than
erroring, so the failure mode is a confusing finding rather than a clear one.
Accepted: the alternative is a structured header, which is a heavier contract to
impose on target repositories than the defect warrants.

**Bad.** `rules/12` now forbids travelling artifacts from naming any file, which
makes them slightly less self-describing to a reader who has only the file.

**Load-bearing.** The regression test writes the pack into a scratch repository
and runs the checker there. It is the only test in the suite that evaluates an
artifact from somewhere other than this checkout, and it is the reason this
defect cannot silently return. Every earlier test looked at the pack from here,
where all three paths resolve.

## Revisit when

The pack starts shipping something whose correct use genuinely requires naming a
file in the host repository - or when a second Akinator artifact needs to
travel, at which point the vendored banner should become a shared helper rather
than two hand-written strings in `scripts/build_codex_pack.py`.

## Related

- Rules: `rules/12-artifacts-that-travel-name-nothing-local.md`
- Rules: `rules/07-codex-pack-is-generated.md`
- Ledger: `.ai/ledger/failure/a-generated-artifact-that-travels-named-56871dcd648a.md`
- Memory: `memory/2026-08-30-a-claim-is-only-true-relative-to-a-tree.md`
- Evals: `evals/results/2026-08-30-06-anti-gaming.md`
- Docs: `docs/adr/0006-index-completeness-as-its-own-invariant.md` - the ADR that
  put CI on `--strict`, which is why MEDIUM was not an acceptable landing place

_Historical note, 2026-09-18: the transcript above shows the paths of the time. The checker now lives at `skills/everything/scripts/akinator_coverage.py`, and the Codex installer was replaced by `install.sh` under ADR 0009._
