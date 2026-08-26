#!/bin/sh
# Install the Akinator Codex pack.
#
# Codex reads skills from, in order of scope:
#   $CWD/.agents/skills  (and every directory up to the repository root)
#   $HOME/.agents/skills
#   /etc/codex/skills
#
# This script copies the generated pack into one of those locations. It never
# writes to /etc.
#
# Usage:
#   ./scripts/install-codex.sh [--user | --repo <path>] [--force]
#
#   --user          install to $HOME/.agents/skills (default)
#   --repo <path>   install to <path>/.agents/skills, and copy AGENTS.md if the
#                   target has none
#   --force         overwrite an existing akinator* skill directory
#
# The pack is generated from the canonical Claude skills. If it is missing or
# drifted, this script regenerates it first - see rules/07-codex-pack-is-generated.md.

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PACK_ROOT=$(dirname -- "$SCRIPT_DIR")

MODE="user"
TARGET_REPO=""
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --user) MODE="user"; shift ;;
    --repo)
      MODE="repo"
      [ $# -ge 2 ] || { echo "--repo needs a path" >&2; exit 2; }
      TARGET_REPO="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

# --- ensure the pack is current -------------------------------------------

# Probe by executing, not by presence. On Windows, `python3` is often an App
# Execution Alias stub that resolves on PATH and then fails when run - so
# `command -v` finds an interpreter that does not exist.
PY=""
for candidate in python3 python py; do
  if command -v "$candidate" >/dev/null 2>&1 &&
     "$candidate" -c "import sys" >/dev/null 2>&1; then
    PY="$candidate"
    break
  fi
done

if [ -n "$PY" ]; then
  if ! "$PY" "$PACK_ROOT/scripts/build_codex_pack.py" "$PACK_ROOT" --check >/dev/null 2>&1; then
    echo "Codex pack is missing or drifted - regenerating from the canonical skills."
    "$PY" "$PACK_ROOT/scripts/build_codex_pack.py" "$PACK_ROOT" --write
  fi
else
  echo "Warning: python not found; installing the pack as-is without a drift check." >&2
fi

SOURCE="$PACK_ROOT/.agents/skills"
if [ ! -d "$SOURCE" ]; then
  echo "No generated pack at $SOURCE, and python was unavailable to build it." >&2
  exit 1
fi

# --- resolve the destination ----------------------------------------------

if [ "$MODE" = "repo" ]; then
  [ -d "$TARGET_REPO" ] || { echo "not a directory: $TARGET_REPO" >&2; exit 1; }
  DEST="$TARGET_REPO/.agents/skills"
else
  DEST="$HOME/.agents/skills"
fi

mkdir -p "$DEST"

# --- copy ------------------------------------------------------------------

INSTALLED=0
for skill_dir in "$SOURCE"/*/; do
  [ -d "$skill_dir" ] || continue
  name=$(basename "$skill_dir")
  target="$DEST/$name"

  if [ -e "$target" ] && [ "$FORCE" -eq 0 ]; then
    echo "skip    $name (already present - use --force to overwrite)"
    continue
  fi

  rm -rf "$target"
  mkdir -p "$target"
  cp "$skill_dir/SKILL.md" "$target/SKILL.md"
  echo "install $name"
  INSTALLED=$((INSTALLED + 1))
done

# --- AGENTS.md for repo installs ------------------------------------------

if [ "$MODE" = "repo" ]; then
  if [ -e "$TARGET_REPO/AGENTS.md" ]; then
    echo
    echo "$TARGET_REPO/AGENTS.md already exists - not overwritten."
    echo "Merge Akinator's contract into it by hand:"
    echo "  $PACK_ROOT/.agents/AGENTS.md"
    echo "Adopt, never impose: keep the repo's own content and add the loop."
  else
    # The portable contract - NOT Akinator's own router, which names paths
    # that exist only in Akinator's repository.
    cp "$PACK_ROOT/.agents/AGENTS.md" "$TARGET_REPO/AGENTS.md"
    echo "install AGENTS.md"
  fi
fi

echo
echo "Installed $INSTALLED skill(s) to $DEST"
echo
echo "Codex will discover them automatically. Invoke one explicitly with"
echo "\$akinator, or describe your task and let Codex select from the"
echo "skill descriptions."
