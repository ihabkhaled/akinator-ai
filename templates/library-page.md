# <Library name>

> Template. Copy to `<libraries-home>/<library>.md` - the libraries category of
> the repository's wiki, wherever it lives. **One page per load-bearing
> library**: anything on the request path, in money, auth or data handling, or
> that has already caused a failure. The block between the generated markers is
> rewritten by the library extractor; everything outside it is yours and is
> preserved byte for byte. A fact nobody knows is written as the exact gap
> marker line `_Unknown - ask the owner and record the answer._` - never guessed.
> Delete this line and every angle-bracket placeholder.

- **Role:** <runtime | build | test | dev tooling>
- **Load-bearing for:** <what breaks, for whom, if this library breaks>
- **Owner:** <who decides upgrades and replacements>

## Generated facts

<!-- akinator:generated:begin -->
<Written by the library extractor - the declared constraint, the resolved
version, the manifest that declares it, the licence where the manifest states
one. Never edit by hand: the next run replaces everything between the markers.>
<!-- akinator:generated:end -->

## Why this library

<The problem it solves for us, what was rejected, and why. Not the library's own
marketing - the reason this repository chose it. Link the ADR if there was a
real choice.>

## How we use it

<The pattern. Which module owns it, the convention every caller follows, the
call sites that matter. The rule that stops the next person using it the other
way.>

- Owned by: <`src/<path>`> - <what that module wraps>
- Convention: <e.g. "always through the wrapper, never imported directly">
- Where it matters most: <`src/<path>`> - <why>

## Pitfalls and incidents

<The behavior that surprised someone, and the symptom that misled them.
Append-only, dated.>

| Date | What happened | Symptom that misled | What we do now | Ledger |
|---|---|---|---|---|
| <YYYY-MM-DD> | <what broke> | <what it looked like instead> | <the fix or guard> | <record id> |

## Upgrade and security notes

- **Pinning policy:** <exact | caret | tilde - and why>
- **Breaking changes to watch:** <what the next major version changes that we
  depend on>
- **Advisories:** <how security advisories are tracked, and who acts on them>
- **Last upgrade:** <YYYY-MM-DD, from and to, what broke>

## Related

- Decision: <`docs/adr/NNNN-<slug>.md`>
- Stack map: <`context/<map>.md`>
- Requirements: <requirement ids this library serves>
- Rule: <`rules/NN-<name>.md`> - if a constraint protects how it is used

## Review when

- Last verified: <YYYY-MM-DD>
- Review when: <a new major version, a security advisory, a replacement being
  considered, the owning module being rewritten>
