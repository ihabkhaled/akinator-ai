# Market

What this answers: market, competitors, positioning, marketing.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## Who is this sold to, and who are the main competitors?

**Sold to:** AI-heavy teams and corporates using Claude Code, Codex or Cursor
who need a codebase to remain navigable and truthful across many fresh-context
agent sessions - stated directly as the target in `docs/business-case.md`
("Every codebase decays... On an AI-heavy team that tax is paid per session")
and in this repository's own `CLAUDE.md` ("Akinator - the knowledge-layer
operating system for AI-maintained codebases").

**Positioning, from `docs/listing.md`:** against doing nothing, or against a
hand-maintained `CLAUDE.md`/`AGENTS.md` that a team writes once and lets rot.
The listing's own framing: "Akinator makes it structurally impossible to change
code without growing the knowledge around it" - the differentiator is
enforcement (a twelve-station loop, a declared knowledge delta, a coverage
checker with eleven mechanically verifiable invariants, review-lens vetoes)
rather than a convention a team is trusted to follow.

**Named competitors or comparable products:** none are named anywhere in the
repository. The closest stated comparison is the category of practice it
replaces - "a plain `CLAUDE.md`/`AGENTS.md` file a team writes once and forgets"
- rather than a competing named tool or vendor.

_Unknown - ask the owner and record the answer._

## How is it positioned against a plain CLAUDE.md/AGENTS.md file?

A hand-written router file states intent once and is not verified: it can
silently diverge from the code (docs describing a deleted service), from
itself across platforms (a `CLAUDE.md` and `AGENTS.md` that say different
things), and it does not grow with the codebase because nothing forces it to.
Akinator's contract (`docs/business-case.md`, "Why a plugin, not a prompt";
`docs/listing.md` example 5, "Find out whether your documentation is actually
true") is that the router files are **generated and checked**, not hand-written
and trusted: every router renders from one contract
(`context/router-contract.md`, `rules/09-routers-are-rendered-from-one-contract.md`),
and the coverage checker fails CI when a router forks from that contract, a
doc names a path that does not exist, or a rule names enforcement that is not
wired.

## What channels does it use to reach users?

- **GitHub** - the canonical source, `github.com/ihabkhaled/akinator-ai`
  (`README.md` install commands, `docs/listing.md`).
- **Plugin marketplaces** - Claude Code (`claude plugin marketplace add` +
  `claude plugin install akinator@akinator`, `.claude-plugin/marketplace.json`,
  `.claude-plugin/plugin.json`) and a Codex plugin route documented but "not
  verified here" per `CHANGELOG.md` ("Not verified here", 1.2.0) - taken from
  Codex docs and source, not run on the maintaining machine. `docs/listing.md`
  itself is written as submission copy for "the plugin directory", implying at
  least one plugin marketplace listing is the intended discovery channel.
- **Direct one-line install** - `curl | sh` / `irm | iex` from the raw GitHub
  URL, requiring no marketplace at all (`README.md`, "One line (recommended)").

No paid marketing, ads, or content channel is named in the repository.

_Unknown - ask the owner and record the answer._

## What marketing copy exists, and is it current?

`docs/listing.md` is the canonical marketing/submission text, explicitly kept
so "the listing and the repository cannot drift, and so a change to one is a
change to both." Its own "Review when" note: last verified 2026-09-18 against
plugin version 1.2.0. As of this page (2026-09-19, version 2.0.0) that listing
predates the living-wiki release (ADR 0010) and should be refreshed to mention
the wiki, the 15-question budget, and the `akinator-decide`/`akinator-wiki`
station references before the next marketplace submission.
