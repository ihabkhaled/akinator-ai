<!--
DO NOT EDIT BY HAND.
Installed from the Akinator plugin - a station reference of its one skill (procedure).
No generator is named by path: this file travels into repositories
that do not have one, where naming it would be a false claim.
To update: reinstall Akinator, or regenerate inside an Akinator
checkout. Local edits here are replaced either way.
-->
# The pass - step by step

> **Station reference** of [the one Akinator skill](../SKILL.md). Load when:
> running the complete pass - the phases, their exit conditions and the
> exact tool commands. The skill carries the outline; this is the detail.

`<skill>` means the directory holding `SKILL.md`; the tools are in
`<skill>/scripts/`, wherever the skill was installed.

Run the phases in order. Each names the station that owns it and the exit
condition that lets you leave it.

### Phase 1 - Establish the ground

1. **RESOLVE** (`akinator`) - read the layer: routers, rules, skills, context,
   memory, generated manifests, docs, and **the ledger**
   (`python <skill>/scripts/akinator_ledger.py list --recurring`). Cite what you
   found; a citation is the proof that this ran. The recurring failures are the
   ones most likely to bite this pass too.
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
    python <skill>/scripts/akinator_scope.py plan --against HEAD
    python <skill>/scripts/akinator_scope.py questions   # the batched ask, budget 5
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
6. **Boardroom review, at plan time** - apply every lens the work touches. On
   Claude Code these are subagents shipped with the plugin; elsewhere apply the
   same questions inline:

   | Touches | Lens |
   |---|---|
   | money, entitlements, must-never-break | business owner |
   | architecture, dependencies, boundaries, tradeoffs | CTO |
   | user-facing behavior | product owner |
   | schema, dependencies, build inputs, topology | ops |
   | numbers with business meaning | analyst |
   | scope and completion honesty | PM |

   A veto at plan time is cheap. The same veto at verify time costs the batch.

**Exit when:** every batch has a declared delta and no lens holds a veto.

### Phase 3 - Build, batch by batch

For **each** batch, in order:

7. **Check the machine** (`akinator-resource-guard`) before anything heavy.
8. **IMPLEMENT** - the code. No gates mid-batch.
9. **DOCUMENT** (`akinator-document-change`) - the why, the when-not-to, the
   business meaning, the operational consequence. Route each to its home.
10. **SKILLIFY** (`akinator-skillify`) - any procedure that will happen twice,
    written as the host repository's own skill, in its own conventions.
11. **RULE** (`akinator-rule-forge`) - any new constraint, with a mechanism that
    exists in the tree. Then check what the existing ones are doing:

    ```bash
    python <skill>/scripts/akinator_rules.py conflicts   # overlapping, opposed
    python <skill>/scripts/akinator_rules.py evolve      # a rule that caused a failure
    ```

    If this batch's failure was **caused by an existing rule's enforcement**,
    record it - `akinator_rules.py caused <rule> <fingerprint>` - and write the
    replacement that satisfies both. The superseded rule stays; deleting it
    deletes the reason the replacement is shaped as it is.
12. **CONTEXTIFY** (`akinator-contextify`) - structural facts; build the
    extractor rather than the map wherever the fact is derivable. **Do not write
    a document per library, component or module** - one generated map replaces
    N generated documents, and the prose budget goes to the decision that chose
    the dependency and the failure it caused:

    ```bash
    python <skill>/scripts/extract_stack.py --write   # dependencies and modules
    ```
13. **MEMOIZE** (`akinator-memoize`) - decisions, surprises, dead ends, with
    dates and reversal conditions. Prune while you are there.

13b. **LEDGER** - record what actually happened, not only what was decided:

    ```bash
    python <skill>/scripts/akinator_ledger.py add failure --title "..." --field ...
    python <skill>/scripts/akinator_ledger.py occurred <fingerprint> --source self-report
    python <skill>/scripts/akinator_ledger.py list --recurring
    ```

    Anything at two occurrences or more **stops the pass** and asks whether it
    should become a rule, a skill, or neither:

    ```bash
    python <skill>/scripts/akinator_distil.py detect     # what reached the threshold
    python <skill>/scripts/akinator_distil.py propose <fingerprint>
    python <skill>/scripts/akinator_distil.py decide <fingerprint> --as rule --note "..."
    ```

    Record the answer either way; **`neither` is valid** and stops it being
    re-asked. Recurrence proves the failure is real; it does not prove an
    enforceable mechanism exists.
14. **Record decisions** (`akinator-adr`) - anything chosen between real
    alternatives.
15. **Business, product, operations** (`akinator-business-map`,
    `akinator-product-map`, `akinator-ops-map`) wherever the batch touched
    money, user-visible behavior, or how the system is run.
16. **INDEX and SYNC** (`akinator-index-sync`, `akinator-router-sync`) - every
    artifact reachable; every router updated together.
17. **Librarian review** - on every batch, without exception: is the declared
    delta present, routed to its home, reachable and true? On Claude Code this is
    the librarian subagent. Do not call a batch done over a `BLOCKED`.

**Exit each batch when:** the librarian review returns `CLEAR`.

### Phase 4 - Prove it

18. **Gate once** (`akinator-gate-economy`) - at the end, scoped to what was
    touched. Fix reds, re-run only what was red, judge by exit codes.
19. **Run every mechanical check the repository has** - its own tests, linters
    and drift checks - plus the knowledge invariants:

    ```bash
    python <skill>/scripts/akinator_coverage.py . --strict
    python <skill>/scripts/akinator_ledger.py verify
    python <skill>/scripts/akinator_rules.py conflicts
    ```

20. **Coverage and the newcomer test** (`akinator-coverage`) - both halves. A
    green mechanical run measures presence and consistency, not usefulness. Say
    which one you ran.
21. **Anti-gaming sweep** (`akinator-anti-gaming`) - turned on your **own**
    output from this pass. Every doc faces the delete-the-derivable test; every
    ticked box names an artifact changed in this pass; every coverage claim is
    sampled, not asserted.
22. **Boardroom review, at verify time** - the same lenses, against what was
    actually built rather than what was planned.
23. **Clean up** (`akinator-resource-guard`) - machine as you found it. Verify by
    listing, not by assuming.

23b. **Regenerate the brief** - `python <skill>/scripts/build_brief.py --write`.
    It is what the next session reads; everything this pass learned is invisible
    until it is composed in.

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
trivial, and the librarian review still runs on every batch you do open.
