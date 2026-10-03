# Integrations

<!-- akinator:generated:begin -->
<!-- Facts detected from the tree. This block is rewritten on every run;
     write outside it. Nothing here is guessed: every row names its file. -->

### SDKs and clients

Nothing detected.

### Environment variables naming an external service

Nothing detected.

Regenerate with: `python <skill>/scripts/extract_platform.py --write`
<!-- akinator:generated:end -->

What this answers: external systems and vendors.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## Which external systems and vendors does this depend on, and what happens when each is down?

- **Claude Code, Codex and Cursor** - the three platforms Akinator installs
  into; their contracts and what breaks when they move are in
  `docs/compatibility.md`.
- **GitHub** - hosts the repository, the one-line installer source, and CI. If
  GitHub is down, installs and CI stop; a local checkout still works.
- No payment, identity, email or analytics vendor.

_Unknown - ask the owner and record the answer._
