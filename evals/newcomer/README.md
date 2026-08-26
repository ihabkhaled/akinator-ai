# The newcomer test

The qualitative half of coverage, and the bar for onboarding being done.

The mechanical checker measures presence and consistency. It cannot measure
whether a document is *useful*. A repository can pass every invariant - perfectly
indexed, no dead links, every rule enforced - and still fail this completely,
because the documents answer no question anyone actually has.

## The bar

> A fresh agent, given only the knowledge layer, correctly answers - **in
> seconds** - where to go, what to do, what not to break, and what to run
> afterwards, for each of the repository's five most common change types.

"In seconds" is part of the bar, not a nicety. An answer that takes fifteen
minutes of searching is a fail even when it is correct, because in practice
nobody spends those fifteen minutes. They guess.

## Setup

1. **Identify the five most common change types** from the git history, not from
   intuition. Cluster the last few hundred commits by what they did. Typical
   results: add an endpoint, add a background job, change a plan limit, add a
   migration, debug a failing job.

2. **Write the question a newcomer would actually ask** for each - in their
   words, not the maintainer's:

   > I need to add an API endpoint. Where do I go, what do I do, what must I not
   > break, and what do I run afterwards?

3. **Record the five questions** in `questions.md` in the repo being tested, so
   later runs are comparable. Changing the questions between runs makes the
   trend meaningless.

## Run

- Use a **fresh-context** agent. One that watched the layer being built knows
  things the layer does not contain, and will pass a test the layer fails.
- Give it the repository and the question. Nothing else.
- **Do not help.** No hints, no clarification, no follow-up. Every hint is
  exactly the thing that will not be there next time.
- Time it, from question to answer.
- Record the full transcript.

## Grade

| Grade | Meaning |
|---|---|
| **pass** | Correct, quick, and **cites the layer** - names the rule, skill or doc it came from |
| **partial** | Right direction, but missed a constraint, a required step, or the operational consequence |
| **fail** | Wrong, could not answer, or answered confidently from inference rather than from the layer |

**Confident-but-inferred is a fail**, and it is the most dangerous result: the
layer did not answer, the agent did not notice, and in production nobody checks.

A correct answer with no citation grades **partial** at best. Without a citation
you cannot tell whether the layer worked or the model already knew.

## Use the failures

Every failure names a missing artifact. That list is the next improvement batch,
and it is better specified than anything written from imagination - it comes
from an agent that actually needed the thing and could not find it.

Record results in `results/` as `YYYY-MM-DD-<repo>.md`:

```markdown
# Newcomer test - <repo> - 2026-08-26

Plugin version: 1.0.0
Agent: fresh context, no hints

| Change type | Grade | Time | What was missing |
|---|---|---|---|
| Add an API endpoint | pass | 12s | - |
| Add a migration | fail | 90s | Answered "restart the services" from inference. Nothing documents the drop-and-rebuild requirement |

## Next batch

- Write the schema-change runbook and a skill so it fires (akinator-ops-map)
```

## Frequency

- At the end of onboarding - this is what makes onboarding done.
- Quarterly, or after any large feature.
- After any batch that touches the routers.

## Related

- `skills/akinator-coverage/SKILL.md` - both halves of coverage
- `skills/akinator-onboard/SKILL.md` - where this is the completion bar
- `docs/business-case.md` - why this is the success measure
