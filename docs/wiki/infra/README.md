# Infra

What this answers: how the system is built, run, configured and installed.

Part of the [project wiki](../index.md). One canonical home per fact - link to
it, never copy it. Generated pages are rewritten by
`skills/everything/scripts/extract_operations.py --write`; write outside their
generated blocks.

| Page | Holds |
|---|---|
| [Tools and commands](tools-and-commands.md) | every runnable command, script and CI job, and what it does |
| [Environment variables](environment-variables.md) | variable names only, never values |
| [Repositories](repositories.md) | remotes and provider, credentials stripped |
| [Installation](installation.md) | install, run and test commands, runtime versions |

Akinator deploys nothing and runs no service; its "infrastructure" is the
installer (`install.sh`, `install.ps1`) and the CI workflow
`.github/workflows/ci.yml`.
