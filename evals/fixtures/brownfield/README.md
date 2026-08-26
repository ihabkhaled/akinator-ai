# workly

A workspace API. Teams have members and items; plans set limits.

## Where things are

- Standards (constraints this codebase holds to): `docs/standards/README.md`
- Playbooks (operational procedures): `ops/playbooks/README.md`
- Source: `src/`

## Conventions

Standards are referenced from code comments by filename, so their names are
stable - do not rename or renumber them. Playbooks have imperative titles and
are run top to bottom.

## Development

```bash
python -m pytest
```
