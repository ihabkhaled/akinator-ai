# Architecture decision records

One record per decision that was made between real alternatives and will be
questioned later. Written with `templates/adr.md`; see
`templates/examples/adr.md` for a fully worked example.

The value of an ADR is almost entirely in the **rejected options**. A record that
says only what was chosen is a description; one that says what was not chosen,
and on what grounds, is knowledge.

## Conventions

- Numbered `NNNN-slug.md`, sequential, **never renumbered**.
- A superseded ADR is never deleted - it is marked superseded with a link
  forward, because the chain is the point.
- At least two options, each with what it would have cost and why it lost.
- Consequences include the bad ones. An ADR listing only benefits is advocacy.
- Every record names a **revisit-when** condition, which turns it from a museum
  piece into a live tripwire.

## The records

| # | Decision | Status | Revisit when |
|---|---|---|---|
| [0001](0001-mit-license.md) | MIT license | accepted | the contributor set grows large enough that relicensing becomes impractical |
| [0002](0002-codex-pack-generated-from-claude-skills.md) | The Codex pack is generated from the canonical Claude skills | accepted | the Codex skills contract diverges from Claude's beyond a banner |
| [0003](0003-enforcement-outside-git-hooks.md) | Knowledge enforcement lives outside git hooks | accepted | a pre-commit mechanism appears that is instant and unbypassable - never for "just one fast check" |
| [0004](0004-gate-receipts-over-hook-bypass.md) | Tree-bound gate receipts, not hook bypass | accepted | git gains native content-addressed check results |
| [0005](0005-single-command-surface.md) | One command, not one per mode | accepted | the owner asks for a second, or a mode needs a different tool allowlist |
| [0006](0006-index-completeness-as-its-own-invariant.md) | Index completeness is a separate invariant, and CI runs at `--strict` | accepted | MEDIUM proves the wrong grade in practice, or the one-level nesting limit produces a real miss |
| [0007](0007-vendored-artifacts-declare-origin-not-generator.md) | A vendored artifact declares its origin, not a generator | accepted | the pack stops being copied and starts being referenced in place, or a second artifact needs to travel |

## Adding one

Use `skills/akinator-adr/SKILL.md`, or `/akinator decide <the question>`.
