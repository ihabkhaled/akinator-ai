# Sensitive data

<!-- akinator:generated:begin -->

## Sensitive data register

Names and locations only - this page never holds a value.

### Secret-bearing environment variables

- none declared.

### Secret-bearing files

- none present.

### PII-ish and credential fields in schemas

- `.agents/skills/akinator/scripts/akinator_sensitive.py:356` `secret_files` - credential
- `skills/everything/scripts/akinator_sensitive.py:353` `secret_files` - credential
- `.agents/skills/akinator/scripts/akinator_coverage.py:336` `token` - credential
- `.agents/skills/akinator/scripts/akinator_scope.py:20` `token` - credential
- `.agents/skills/akinator/scripts/akinator_wiki.py:239` `secret` - credential
- `skills/everything/scripts/akinator_coverage.py:333` `token` - credential
- `skills/everything/scripts/akinator_scope.py:17` `token` - credential
- `skills/everything/scripts/akinator_wiki.py:236` `secret` - credential

### Logging that mentions those fields

- `.agents/skills/akinator/scripts/akinator_sensitive.py:268`
- `skills/everything/scripts/akinator_sensitive.py:265`
- `tests/test_sensitive.py:155`

### Handling rules

| Class | Default handling |
|---|---|
| credential | never log, never commit, encrypt at rest, redact in ledger, rotate on exposure |
| PII | never log in clear, never commit real values, encrypt at rest, redact in ledger, delete on request |
| financial | never log, never commit, encrypt at rest, redact in ledger, tokenise where possible |
| health | never log, never commit, encrypt at rest, redact in ledger, restrict access |

Regenerate with: `python <skill>/scripts/akinator_sensitive.py register --write`.
<!-- akinator:generated:end -->

## Who rotates each secret and how

Who rotates each secret and how: _Unknown - ask the owner and record the answer._

## Where secrets live in production

Where secrets live in production: _Unknown - ask the owner and record the answer._

## Who to tell after an exposure

Who to tell after an exposure: _Unknown - ask the owner and record the answer._
