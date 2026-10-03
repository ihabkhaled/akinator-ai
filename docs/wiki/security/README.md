# Security

<!-- akinator:generated:begin -->
<!-- Facts detected from the tree. This block is rewritten on every run;
     write outside it. Nothing here is guessed: every row names its file. -->

### Secret handling

| Detected | Where |
|---|---|
| `.env` is gitignored | `.gitignore` |

### Environment variable names

Nothing detected.

### Dependency and vulnerability scanning

Nothing detected.

### Authentication libraries

Nothing detected.

### Ownership and policy

Nothing detected.

Regenerate with: `python <skill>/scripts/extract_platform.py --write`
<!-- akinator:generated:end -->

What this answers: secret handling, auth, threat model.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## How are secrets handled, how do users and services authenticate, and what is the threat model?

- **Secrets:** the repository holds no runtime secrets and declares no
  environment variables. Sensitive data is governed by rule 15: the register at
  [sensitive-data](sensitive-data.md) holds names and locations, never values;
  `akinator_sensitive.py scan` runs in CI and prints a fingerprint, not the
  value; `guard` pre-checks text bound for docs, ledger and memory. Ledger
  records are redacted before write (rule 10).
- **Authentication:** none - Akinator is a plugin and a set of local scripts,
  with no service and no users to authenticate. The installer fetches from the
  project's GitHub repository.
- **Network:** the context, trace and sensitive tools make no network calls.
- **Trust boundary:** the tools read the host repository and write only under
  `docs/`, `.ai/` and the paths the owner names.

_Unknown - ask the owner and record the answer._
