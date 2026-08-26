---
name: windows-python3-alias-stub
type: constraint
date: 2026-08-26
---

# On Windows, `python3` resolves on PATH and then fails

## The fact

Windows ships an App Execution Alias for `python3` that exists on PATH even when
Python is installed only as `python`. `command -v python3` succeeds; running it
prints "Python was not found; run without arguments to install from the
Microsoft Store" and does not execute the script.

Any interpreter probe based on presence therefore picks an interpreter that does
not work. Probe by **executing**:

```sh
for candidate in python3 python py; do
  if command -v "$candidate" >/dev/null 2>&1 &&
     "$candidate" -c "import sys" >/dev/null 2>&1; then
    PY="$candidate"; break
  fi
done
```

## Why

The alias is a stub installer shim, not an interpreter. It is on PATH by default
in `%LOCALAPPDATA%\Microsoft\WindowsApps` and can only be disabled per-user in
Settings, so a cross-platform script cannot assume it is absent.

Found when `scripts/install-codex.sh` selected `python3`, failed to regenerate
the pack, and - under `set -e` - exited after printing a message that read like a
missing-Python error on a machine where Python 3.13 was installed and working.

## Date

- 2026-08-26 - recorded after the installer failed on the author's machine.

## Reversal conditions

- Microsoft removes the App Execution Alias, or stops placing it on PATH by
  default.
- The installer stops needing a Python interpreter at all - it currently needs
  one only to run the drift check before installing.

## Related

- `scripts/install-codex.sh` - the probe lives at the top
- `rules/07-codex-pack-is-generated.md` - why the installer checks for drift
