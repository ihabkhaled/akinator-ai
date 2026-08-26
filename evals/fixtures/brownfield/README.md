# workly

A workspace API. Teams have members and items; plans set limits.

Fixture repository for Akinator's brownfield eval - the **adopt-never-impose**
case, which is the hardest and most important one.

## Its conventions - do not normalize them

This repo has a real knowledge system that predates Akinator, with conventions
that differ from Akinator's defaults on purpose:

- Constraints live in `docs/standards/`, **unnumbered**, kebab-case. Code
  comments reference them by filename, so renumbering would break them.
- Runbooks live in `ops/playbooks/`, with **no frontmatter**, imperative titles.
- Indexes are `README.md` files with a bulleted list, description after a dash.
- There is no `AGENTS.md`, no `context/`, and no `memory/`.

An agent onboarding this repo must map onto these, extend them, and record what
it deliberately did not change. Creating `rules/` beside `docs/standards/` is the
failure this fixture tests for.

## The deliberate void

`docs/standards/quotas.md` documents plans and quotas but says **nothing** about
what happens to quota when a subscription is refunded. Eval 03 depends on that
silence.

- Standards: `docs/standards/README.md`
- Playbooks: `ops/playbooks/README.md`
