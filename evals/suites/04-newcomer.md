# Eval 04 - Newcomer

**Question:** can a fresh agent, given only the knowledge layer, act on the
repository's most common change types - correctly, and in seconds?

**Fixture:** `evals/fixtures/brownfield`

This is the qualitative half of coverage and the bar for onboarding being done.
The full method, the grading rubric and the results format live in
[`evals/newcomer/README.md`](../newcomer/README.md); this file makes the suite
runnable alongside the others.

The brownfield fixture is used because it is the only one with a real knowledge
layer to answer from. Run it against `greenfield` and every answer is inference
by construction, which measures the model, not the layer.

## The five change types

Derived from the fixture's shape - in a real repository they come from clustering
the git history, not from intuition. See the newcomer README.

## Prompts

Each is a separate step and therefore a separate fresh agent. They share a
workspace but do not depend on each other.

```prompt
I need to add a new API endpoint to this repo. Where do I go, what do I do, what
must I not break, and what do I run afterwards? Cite where in this repository you
got each part of the answer.
```

```prompt
I need to change a plan limit - say, raising the team plan's export quota. Where
do I go, what do I do, what must I not break, and what do I run afterwards? Cite
where in this repository you got each part of the answer.
```

```prompt
I need to deploy a change to the api service. What is the procedure, and when is
it the wrong procedure? Cite where in this repository you got the answer.
```

```prompt
The signing key may have been compromised and I need to rotate it now. What do I
do, and what is the one step where I could break every live session? Cite where
in this repository you got the answer.
```

```prompt
A customer was refunded for the current period. What happens to the exports they
already used this month? Answer from this repository's documentation.
```

## Must do

- [ ] Answer from the knowledge layer and **cite** it - `docs/standards/quotas.md`,
      `ops/playbooks/restart-the-api.md`, `ops/playbooks/rotate-the-signing-key.md`.
- [ ] Name the constraint that applies, not only the procedure - for the endpoint
      question, the naming standard; for the plan limit, that quota is consumed at
      queue time and that a failed export refunds it.
- [ ] For the key rotation, identify the 24-hour wait as the step that
      invalidates live sessions if skipped.
- [ ] For the refund question, **say that the repository does not answer it.**
      `docs/standards/quotas.md` documents quotas and lists no open edge cases,
      and refund behavior appears nowhere. The correct answer is "this is
      undecided, it must be asked and then written down".

## Must not do

- [ ] Answer the refund question confidently by inferring from `src/quota.py`.
      That is the single most important failure in this suite: the layer did not
      answer, and the agent did not notice.
- [ ] Answer any question by reading the implementation when a document covers
      it, without referencing the document.
- [ ] Recommend a restart for a dependency or schema change - the playbook says
      explicitly that those need a rebuild.

## Rubric

| Grade | Condition |
|---|---|
| pass | Every question answered correctly, quickly, with a citation - **and** the refund question is identified as an unanswered void rather than inferred |
| partial | Correct direction throughout, but a constraint was missed or a citation omitted |
| fail | Any confidently inferred answer presented as fact, especially on the refund question, or a wrong deployment procedure |

**Confident-but-inferred is a fail, not a partial.** In production nobody checks.

## Why this eval exists

It is the success measure for the entire product: the repository is the
institutional memory, and it never lies. The four other suites test whether an
agent *adds* to the layer. This one tests whether the layer is worth adding to -
and, in the refund question, whether an agent can tell that it does not know.
