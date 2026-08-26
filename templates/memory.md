---
name: <kebab-case-slug>
type: <decision | preference | surprise | dead-end | constraint>
date: <YYYY-MM-DD>
---

# <One-line statement of the fact>

> Template. Copy to `memory/<YYYY-MM-DD>-<slug>.md`. **One fact per file.**
> Delete this line and every angle-bracket placeholder.

## The fact

<One or two sentences, plainly. What is true, or what was decided.>

## Why

<Why it is true, or why the decision was made. A fact without its why cannot be
re-evaluated later - it just becomes cargo cult, obeyed by people who do not
know what it is for.>

## Date

<YYYY-MM-DD - absolute, always. "Recently", "last sprint" and "currently" all
become lies. If the fact has been updated, keep the history:>

- <YYYY-MM-DD> - recorded.
- <YYYY-MM-DD> - updated: <what changed>.

## Reversal conditions

<What would make this no longer true, or no longer the right choice. This is
what makes memory prunable instead of accumulative - without it, the entry
survives forever past its usefulness.>

- <condition>
- <condition>

## Related

<Link the rules, skills, docs, ADRs and code this relates to. Use `[[slug]]` for
other memory entries if the repo uses that convention.>

- <`rules/NN-<name>.md`>
- <`docs/<page>.md`>
- <`src/<path>`>
