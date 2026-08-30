---
name: akinator-everything
description: Use when the user explicitly asks for everything - "run the full akinator", "do all of it", "maximum depth", "leave nothing out", "the complete pass" - or before a release, an audit, a handover, or any change too expensive to get wrong. Loads and applies every station, every boardroom lens and every mechanical check, and does not stop until the Definition of Done is proven rather than asserted.
---

# Akinator Everything - the all-in-one pass

One skill that runs all of it.

The `akinator` master skill scales the loop to the work. Every station still
runs - stations 6-11 are never deferrable - but on trivial work most of them
produce nothing, and the batch records `knowledge delta: none, because ...`
in a line. That is correct as a default, because ceremony applied to trivia
gets the whole discipline abandoned.

This skill is the other setting. It is **deliberately invoked**, it assumes the
work is worth maximum thoroughness, and it does not scale down. Every station
runs. Every applicable lens reviews. Every check executes. Nothing is deferred,
nothing is sampled, and completion is proven with evidence rather than claimed.

## When to use

- The user asks for it explicitly: "run everything", "the full akinator", "all
  of it", "maximum depth", "leave nothing out", "don't stop until it's done".
- Before a release, a handover, or an external audit.
- After a long or interrupted session, when you cannot account for what was
  skipped.
- On a change too expensive to get wrong - money, permissions, deletion, a
  public contract, a migration.
- When onboarding a repository that matters.

## When NOT to use

- **Ordinary work.** Use `akinator`, which scales the loop to the change. Running
  the full pass on a typo is the fastest way to make the team stop running any of
  it.
- When the user wants one specific station - use that station's skill.
- Inside a subagent dispatched to execute one narrow step. The dispatching
  session owns the pass.
- As a substitute for thinking. This skill is exhaustive, not clairvoyant: it
  guarantees nothing is skipped, not that every judgment is right.

## Procedure

Run these in order. Do not skip forward. Each phase names the skill that owns it,
and the exit condition that lets you leave it.

### Phase 1 - Establish the ground

1. **RESOLVE** (`akinator`) - read the layer: routers, rules, skills, context,
   memory, generated manifests, docs, and **the ledger**
   (`python scripts/akinator_ledger.py list --recurring`). Cite what you found;
   a citation is the proof that this ran. The recurring failures are the ones
   most likely to bite this pass too.
2. **Detect the conventions** (`akinator-onboard`, section A1) - even outside
   onboarding. What does this repo call things? Adopt those names for everything
   that follows. Getting this wrong poisons every artifact the pass produces.
3. **ASK** (`akinator-intake`) - run the intake battery, minus what the layer
   already answered. Group the questions; ask once. Never guess on money,
   permissions, deletion or public contracts.
4. **AUDIT** (`akinator-audit`) - claim versus code for everything the work
   touches. Anything marked done names its live call path; anything marked
   missing names the search that failed.

4b. **SCOPE the pass** - which stations this change actually wakes:

    ```bash
    python scripts/akinator_scope.py plan --against HEAD
    python scripts/akinator_scope.py questions      # the batched ask, budget 5
    ```

    This **never skips a station**. It reports which have work, so a quiet one
    is run and finds nothing rather than being silently dropped. Ask the
    budgeted questions in **one grouped message**; twenty questions in a session
    means zero answers by the third.

**Exit when:** the layer has been read, the conventions are named, the open
questions are asked or explicitly assumed, and every claim has a status.

### Phase 2 - Plan, and commit to the delta

5. **PLAN** (`akinator-plan`) - batches cut on real seams, blast radius per
   batch, and the **knowledge delta declared by path**. Empty categories are
   stated with their reason.
6. **Boardroom review, at plan time** - dispatch every lens the work touches:

   | Touches | Lens |
   |---|---|
   | money, entitlements, must-never-break | `akinator-business-owner` |
   | architecture, dependencies, boundaries, tradeoffs | `akinator-cto` |
   | user-facing behavior | `akinator-product-owner` |
   | schema, dependencies, build inputs, topology | `akinator-ops` |
   | numbers with business meaning | `akinator-analyst` |
   | scope and completion honesty | `akinator-pm` |

   A veto at plan time is cheap. The same veto at verify time costs the batch.

**Exit when:** every batch has a declared delta and no lens holds a veto.

### Phase 3 - Build, batch by batch

For **each** batch, in order:

7. **Check the machine** (`akinator-resource-guard`) before anything heavy.
8. **IMPLEMENT** - the code. No gates mid-batch.
9. **DOCUMENT** (`akinator-document-change`) - the why, the when-not-to, the
   business meaning, the operational consequence. Route each to its home.
10. **SKILLIFY** (`akinator-skillify`) - any procedure that will happen twice.
11. **RULE** (`akinator-rule-forge`) - any new constraint, with a mechanism that
    exists in the tree. Then check what the existing ones are doing:

    ```bash
    python scripts/akinator_rules.py conflicts   # overlapping, opposed
    python scripts/akinator_rules.py evolve      # a rule that caused a failure
    ```

    If this batch's failure was **caused by an existing rule's enforcement**,
    record it - `akinator_rules.py caused <rule> <fingerprint>` - and write the
    replacement that satisfies both. The superseded rule stays; deleting it
    deletes the reason the replacement is shaped as it is. See
    Akinator's rule-evolution guide.
12. **CONTEXTIFY** (`akinator-contextify`) - structural facts; build the
    extractor rather than the map wherever the fact is derivable. **Do not write
    a document per library, component or module** - one generated map replaces
    N generated documents, and the prose budget goes to the decision that chose
    the dependency and the failure it caused:

    ```bash
    python scripts/extract_stack.py --write        # dependencies and modules
    python scripts/extract_components.py --write   # the plugin's own surface
    ```
13. **MEMOIZE** (`akinator-memoize`) - decisions, surprises, dead ends, with
    dates and reversal conditions. Prune while you are there.
13b. **LEDGER** - record what actually happened, not only what was decided:

    ```bash
    python scripts/akinator_ledger.py add failure --title "..." --field ...
    python scripts/akinator_ledger.py occurred <fingerprint> --source self-report
    python scripts/akinator_ledger.py list --recurring
    ```

    Anything at two occurrences or more **stops the pass** and asks whether it
    should become a rule, a skill, or neither:

    ```bash
    python scripts/akinator_distil.py detect     # what reached the threshold
    python scripts/akinator_distil.py propose <fingerprint>
    python scripts/akinator_distil.py decide <fingerprint> --as rule --note "..."
    ```

    The proposal arrives pre-drafted - the rule, its mechanism and the test that
    would have caught it - so you approve rather than author. Record the answer
    either way; **`neither` is valid** and stops it being re-asked. Recurrence
    proves the failure is real; it does not prove an enforceable mechanism
    exists. Akinator's ledger and distil guides cover the mechanics.
14. **Record decisions** (`akinator-adr`) - anything chosen between real
    alternatives.
15. **Business, product, operations** - `akinator-business-map`,
    `akinator-product-map`, `akinator-ops-map` wherever the batch touched money,
    user-visible behavior, or how the system is run.
16. **INDEX and SYNC** (`akinator-index-sync`, `akinator-router-sync`) - every
    artifact reachable; every router updated together.
17. **Librarian** (`akinator-librarian`) - **on every batch, without exception.**
    Do not call a batch done over a `BLOCKED`.

**Exit each batch when:** the librarian returns `CLEAR`.

### Phase 4 - Prove it

18. **Gate once** (`akinator-gate-economy`) - at the end, scoped to what was
    touched. Fix reds, re-run only what was red, judge by exit codes.
19. **Run every mechanical check the repo has** - whatever tests, linters and
    drift checks it already runs, plus `akinator-coverage`. For example, in the
    Akinator repository itself:

    ```bash
    python -m pytest tests/ -q
    python scripts/akinator_coverage.py . --strict
    python scripts/build_codex_pack.py --check
    python scripts/render_routers.py --check
    python scripts/extract_components.py --check
    python scripts/generate_assets.py --check
    python scripts/akinator_ledger.py verify
    python scripts/build_brief.py --check
    python scripts/extract_stack.py --check
    python scripts/akinator_rules.py conflicts
    ```

20. **Coverage and the newcomer test** (`akinator-coverage`) - both halves. A
    green mechanical run measures presence and consistency, not usefulness. Say
    which one you ran.
21. **Anti-gaming sweep** (`akinator-anti-gaming`) - turn it on your **own**
    output from this pass. Every doc faces the delete-the-derivable test; every
    ticked box names an artifact changed in this pass; every coverage claim is
    sampled, not asserted.
22. **Boardroom review, at verify time** - the same lenses, now against what was
    actually built rather than what was planned.
23. **Clean up** (`akinator-resource-guard`) - machine as you found it. Verify by
    listing, not by assuming.

23b. **Regenerate the brief** - `python scripts/build_brief.py --write`. It is
    what the next session reads; everything this pass learned is invisible until
    it is composed in.

**Exit when:** every check has been run and its exit code observed, the brief is
current, and no lens holds a veto.

### Phase 5 - Loop until proven, then stop

24. Re-read the Definition of Done below. For every unmet line, the fix is a new
    batch: return to phase 3 for that batch only.
25. Repeat until every line is met **with evidence**, or until a line is blocked
    by something outside your control - in which case say so explicitly, name
    what is blocked and by whom, and stop.
26. **Then stop.** Exhaustive does not mean endless. Once the DoD is proven,
    further polishing is scope you were not asked for.

## The one exception

If the work is genuinely trivial - a typo in a comment, a formatting-only change
- say so **in one line, out loud**, do it, record `knowledge delta: none,
because ...`, and stop. Performing the full pass on a typo is how a team learns
to stop running any of it.

That judgment is made once, explicitly, and it is not a licence to scale down by
default. Everything above still applies the moment the change is more than
trivial. Note that this is the *only* thing that scales here: the librarian still
runs on every batch you do open, without exception.

## Failure modes and pitfalls

- **Running this on ordinary work.** The fastest route to the whole discipline
  being abandoned. Default to `akinator`.
- **Treating the phase list as a checklist to tick.** Every phase produces an
  artifact or an observed exit code. A tick with neither is the fake compliance
  this pass is supposed to catch.
- **Skipping the librarian on a "small" batch.** Small batches are where the
  delta gets dropped, because it feels disproportionate.
- **Gate storms.** Phase 4 is one gate, at the end. The temptation to verify
  after each batch is strong and wrong.
- **Auditing everyone but yourself.** Phase 21 turns anti-gaming on this pass's
  own output. Your artifacts from two hours ago get the same scrutiny.
- **Looping forever.** Phase 5 has a stop condition. An agent that cannot stop
  after the DoD is proven has substituted thoroughness for judgment.
- **Sampling in a pass that promised not to.** If you check three of twenty, say
  three of twenty. A pass called "everything" that quietly sampled is worse than
  one that admitted its scope.

## Definition of done

Every line needs evidence, not assertion.

- [ ] The layer was read and cited; the repo's own conventions were adopted.
- [ ] Every open question was asked, or the assumption made instead is written
      down.
- [ ] Every claim carries a status and its evidence.
- [ ] Every batch declared a knowledge delta **by path**, and delivered it.
- [ ] Every artifact is true against the tree, reachable from an index, and
      reflected in every router.
- [ ] Every new rule names an enforcement mechanism that exists and was run.
- [ ] Every structural fact that could be generated is generated.
- [ ] The librarian returned `CLEAR` on every batch.
- [ ] Every applicable boardroom lens reviewed at plan **and** verify, and none
      holds a veto.
- [ ] Gates ran once, scoped, and their exit codes were observed.
- [ ] Every mechanical check the repo has was run and reported, including the
      ones that failed.
- [ ] The newcomer test was run, or its absence was stated explicitly.
- [ ] Anti-gaming was applied to this pass's own output.
- [ ] The machine was left as it was found.
- [ ] Anything left undone is named, with why and who is blocked.
