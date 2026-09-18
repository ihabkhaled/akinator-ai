#!/bin/sh
# Akinator installer - Claude Code, Codex and Cursor, straight from GitHub.
#
#   curl -fsSL https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.sh | sh
#   curl -fsSL https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.sh | sh -s -- --repo .
#
# Akinator is ONE skill with ONE command on every platform:
#   Claude Code  /akinator:everything   plugin, always-on through its SessionStart hook
#   Codex        $akinator              the skill + an always-on block in AGENTS.md
#   Cursor       /akinator              the skill + an alwaysApply rule
#
# Codex and Cursor both read skills from ~/.agents/skills (or <repo>/.agents/skills),
# so one installed folder serves both.
#
# Options:
#   --claude --codex --cursor   choose platforms (default: every one detected here)
#   --repo PATH                 install into one repository instead of your user
#                               profile (Claude project scope, <repo>/.agents/skills,
#                               <repo>/AGENTS.md, <repo>/.cursor/rules)
#   --ref REF                   a branch or tag of the GitHub repository (default main)
#   --uninstall                 remove everything this installer put in place
#   -h, --help                  this text
#
# Re-running updates in place. The installer only ever removes what it can
# recognise as its own: skill folders carrying the Akinator banner, the marked
# akinator:begin/akinator:end block, and its own rule file.
#
# Environment (mostly for testing): AKINATOR_SOURCE (use this checkout instead of
# downloading), AKINATOR_USER_HOME (instead of $HOME), CODEX_HOME,
# AKINATOR_CLAUDE_BIN (the claude executable to use), AKINATOR_REPO_URL.

set -eu

REPO_URL="${AKINATOR_REPO_URL:-https://github.com/ihabkhaled/akinator-ai.git}"
USER_HOME="${AKINATOR_USER_HOME:-$HOME}"
CODEX_DIR="${CODEX_HOME:-$USER_HOME/.codex}"
REF="main"
TARGET_REPO=""
UNINSTALL=0
WANT_CLAUDE=0
WANT_CODEX=0
WANT_CURSOR=0
BEGIN_MARK="<!-- akinator:begin"
END_MARK="<!-- akinator:end -->"

usage() {
  cat <<'USAGE'
Akinator installer - one skill, one command, on Claude Code, Codex and Cursor.

  sh install.sh [--claude] [--codex] [--cursor] [--repo PATH] [--ref REF] [--uninstall]

  --claude --codex --cursor   choose platforms (default: every one detected here)
  --repo PATH                 install into one repository instead of your user profile
  --ref REF                   a branch or tag of the GitHub repository (default main)
  --uninstall                 remove everything this installer put in place

One entry point per platform: /akinator:everything (Claude Code),
$akinator (Codex), /akinator (Cursor). Re-run to update.
USAGE
}

say() { printf '%s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --claude) WANT_CLAUDE=1; shift ;;
    --codex) WANT_CODEX=1; shift ;;
    --cursor) WANT_CURSOR=1; shift ;;
    --repo) [ $# -ge 2 ] || die "--repo needs a path"; TARGET_REPO="$2"; shift 2 ;;
    --ref) [ $# -ge 2 ] || die "--ref needs a branch or tag"; REF="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
done

if [ -n "$TARGET_REPO" ]; then
  [ -d "$TARGET_REPO" ] || die "not a directory: $TARGET_REPO"
  TARGET_REPO=$(CDPATH= cd -- "$TARGET_REPO" && pwd)
fi

# --- the Claude CLI: on PATH, or the one bundled inside the VS Code extension ---

find_claude() {
  if [ -n "${AKINATOR_CLAUDE_BIN:-}" ]; then
    [ "$AKINATOR_CLAUDE_BIN" = "none" ] && return 1
    printf '%s' "$AKINATOR_CLAUDE_BIN"; return 0
  fi
  if command -v claude >/dev/null 2>&1; then command -v claude; return 0; fi
  found=""
  for candidate in "$USER_HOME"/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude \
                   "$USER_HOME"/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude.exe; do
    [ -f "$candidate" ] && found="$candidate"
  done
  [ -n "$found" ] || return 1
  printf '%s' "$found"
}

CLAUDE_BIN=$(find_claude || true)

# --- which platforms --------------------------------------------------------

if [ "$WANT_CLAUDE$WANT_CODEX$WANT_CURSOR" = "000" ]; then
  [ -n "$CLAUDE_BIN" ] && WANT_CLAUDE=1
  if command -v codex >/dev/null 2>&1 || [ -d "$CODEX_DIR" ]; then WANT_CODEX=1; fi
  if command -v cursor >/dev/null 2>&1 || [ -d "$USER_HOME/.cursor" ]; then WANT_CURSOR=1; fi
  # A repository install is for whoever opens it next, with any tool.
  if [ -n "$TARGET_REPO" ]; then WANT_CODEX=1; WANT_CURSOR=1; fi
  if [ "$WANT_CLAUDE$WANT_CODEX$WANT_CURSOR" = "000" ]; then
    die "found none of Claude Code, Codex or Cursor. Name one: --claude, --codex or --cursor."
  fi
fi

# --- the source: this checkout, or a download --------------------------------

is_checkout() { [ -f "$1/skills/everything/SKILL.md" ] && [ -f "$1/.agents/skills/akinator/SKILL.md" ]; }

LOCAL_SOURCE=0
SRC=""
if [ -n "${AKINATOR_SOURCE:-}" ]; then
  is_checkout "$AKINATOR_SOURCE" || die "AKINATOR_SOURCE is not an Akinator checkout: $AKINATOR_SOURCE"
  SRC=$(CDPATH= cd -- "$AKINATOR_SOURCE" && pwd); LOCAL_SOURCE=1
else
  case "$0" in
    *install.sh)
      here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
      if is_checkout "$here"; then SRC="$here"; LOCAL_SOURCE=1; fi ;;
  esac
fi

if [ -z "$SRC" ] && [ "$UNINSTALL" -eq 0 ] && { [ "$WANT_CODEX" -eq 1 ] || [ "$WANT_CURSOR" -eq 1 ]; }; then
  SRC="$USER_HOME/.akinator/src"
  if command -v git >/dev/null 2>&1; then
    if [ -d "$SRC/.git" ]; then
      say "updating $SRC"
      git -C "$SRC" fetch --quiet --depth 1 origin "$REF"
      git -C "$SRC" checkout --quiet --force FETCH_HEAD
    else
      say "downloading Akinator ($REF) to $SRC"
      rm -rf "$SRC"; mkdir -p "$(dirname -- "$SRC")"
      git clone --quiet --depth 1 --branch "$REF" "$REPO_URL" "$SRC"
    fi
  else
    archive="https://codeload.github.com/ihabkhaled/akinator-ai/tar.gz/$REF"
    say "downloading Akinator ($REF) to $SRC"
    rm -rf "$SRC"; mkdir -p "$SRC"
    if command -v curl >/dev/null 2>&1; then curl -fsSL "$archive" | tar -xz -C "$SRC" --strip-components=1
    elif command -v wget >/dev/null 2>&1; then wget -qO- "$archive" | tar -xz -C "$SRC" --strip-components=1
    else die "need git, curl or wget to download Akinator"; fi
  fi
  is_checkout "$SRC" || die "the download at $SRC is not a complete Akinator checkout"
fi

# --- helpers ----------------------------------------------------------------

# Only ever touch what is recognisably ours.
is_ours() { [ -f "$1/SKILL.md" ] && grep -q -e "Akinator plugin" -e "build_codex_pack.py" "$1/SKILL.md"; }

remove_our_skills() {
  root="$1"
  [ -d "$root" ] || return 0
  for dir in "$root"/akinator "$root"/akinator-*; do
    [ -d "$dir" ] || continue
    if is_ours "$dir"; then rm -rf "$dir"; say "removed $dir"; fi
  done
}

strip_block() {
  file="$1"
  [ -f "$file" ] || return 0
  grep -q "$BEGIN_MARK" "$file" || return 0
  tmp="$file.akinator.tmp"
  awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
    index($0, b) == 1 { skip = 1; next }
    skip && index($0, e) == 1 { skip = 0; next }
    !skip { print }' "$file" > "$tmp"
  mv "$tmp" "$file"
}

# A user's file keeps its own line endings. The block is edited in LF - awk on
# Git Bash drops CR on read, awk on Linux keeps it - and a CRLF file is turned
# back into CRLF afterwards. Without this, installing Akinator rewrote every
# line ending of a Windows user's AGENTS.md, and uninstall could not restore it.
has_crlf() { [ -f "$1" ] && [ "$(tr -dc '\r' < "$1" | wc -c)" -gt 0 ]; }
to_lf() { awk '{ sub(/\r$/, ""); print }' "$1" > "$1.akinator.tmp" && mv "$1.akinator.tmp" "$1"; }
to_crlf() { awk '{ sub(/\r$/, ""); printf "%s\r\n", $0 }' "$1" > "$1.akinator.tmp" && mv "$1.akinator.tmp" "$1"; }

write_block() {
  file="$1"
  mkdir -p "$(dirname -- "$file")"
  crlf=0
  if has_crlf "$file"; then crlf=1; to_lf "$file"; fi
  strip_block "$file"
  block="$file.akinator.block"
  {
    printf '%s - installed from the Akinator plugin; reinstall to update. Everything up to akinator:end is replaced on reinstall. -->\n' "$BEGIN_MARK"
    # the portable contract, minus its own banner comment
    awk 'started { print; next } /^-->$/ { started = 1 }' "$SRC/.agents/AGENTS.md"
    printf '%s\n' "$END_MARK"
  } > "$block"
  if [ -s "$file" ]; then
    # drop trailing blank lines so reinstalls do not grow the file
    awk '{ lines[NR] = $0 } END { n = NR; while (n > 0 && lines[n] == "") n--; for (i = 1; i <= n; i++) print lines[i] }' "$file" > "$file.akinator.tmp"
    mv "$file.akinator.tmp" "$file"
    printf '\n' >> "$file"
    cat "$block" >> "$file"
  else
    cat "$block" > "$file"
  fi
  rm -f "$block"
  if [ "$crlf" -eq 1 ]; then to_crlf "$file"; fi
  say "wrote the Akinator block in $file"
  # Codex reads AGENTS.override.md instead of AGENTS.md: globally when it is
  # non-empty, in a repository directory whenever it exists at all.
  override="$(dirname -- "$file")/AGENTS.override.md"
  if { [ -n "$TARGET_REPO" ] && [ -e "$override" ]; } || [ -s "$override" ]; then
    warn "$override exists; Codex reads it INSTEAD of AGENTS.md there, so merge the block into it."
  fi
}

remove_block() {
  file="$1"
  [ -f "$file" ] || return 0
  grep -q "$BEGIN_MARK" "$file" || return 0
  crlf=0
  if has_crlf "$file"; then crlf=1; to_lf "$file"; fi
  strip_block "$file"
  if [ -z "$(tr -d ' \t\r\n' < "$file")" ]; then rm -f "$file"; say "removed $file"; return 0; fi
  # Drop the blank separator line install added, so the file is byte-for-byte
  # what it was before Akinator touched it.
  awk '{ lines[NR] = $0 } END { n = NR; while (n > 0 && lines[n] == "") n--; for (i = 1; i <= n; i++) print lines[i] }' "$file" > "$file.akinator.tmp"
  mv "$file.akinator.tmp" "$file"
  if [ "$crlf" -eq 1 ]; then to_crlf "$file"; fi
  say "removed the Akinator block from $file"
}

# --- scope --------------------------------------------------------------------

if [ -n "$TARGET_REPO" ]; then
  SKILLS_ROOT="$TARGET_REPO/.agents/skills"
  CONTRACT_FILE="$TARGET_REPO/AGENTS.md"
  CURSOR_RULE="$TARGET_REPO/.cursor/rules/akinator.mdc"
  CLAUDE_SCOPE="project"
else
  SKILLS_ROOT="$USER_HOME/.agents/skills"
  CONTRACT_FILE="$CODEX_DIR/AGENTS.md"
  CURSOR_RULE="$USER_HOME/.cursor/rules/akinator.mdc"
  CLAUDE_SCOPE="user"
fi

claude_run() {
  if [ -n "$TARGET_REPO" ]; then (cd "$TARGET_REPO" && "$CLAUDE_BIN" "$@"); else "$CLAUDE_BIN" "$@"; fi
}

# --- uninstall ----------------------------------------------------------------

if [ "$UNINSTALL" -eq 1 ]; then
  if [ "$WANT_CLAUDE" -eq 1 ] && [ -n "$CLAUDE_BIN" ]; then
    claude_run plugin uninstall akinator@akinator --scope "$CLAUDE_SCOPE" || warn "claude: akinator@akinator was not installed"
    say "Claude Code: uninstalled akinator@akinator ($CLAUDE_SCOPE scope)"
  fi
  if [ "$WANT_CODEX" -eq 1 ] || [ "$WANT_CURSOR" -eq 1 ]; then remove_our_skills "$SKILLS_ROOT"; fi
  if [ "$WANT_CODEX" -eq 1 ]; then remove_block "$CONTRACT_FILE"; fi
  if [ "$WANT_CURSOR" -eq 1 ] && [ -f "$CURSOR_RULE" ] && grep -q "Akinator plugin" "$CURSOR_RULE"; then
    rm -f "$CURSOR_RULE"; say "removed $CURSOR_RULE"
  fi
  # Leave no empty directories this installer created. rmdir refuses non-empty
  # ones, so anything the user keeps there survives.
  for dir in "$SKILLS_ROOT" "$(dirname -- "$SKILLS_ROOT")" \
             "$(dirname -- "$CURSOR_RULE")" "$(dirname -- "$(dirname -- "$CURSOR_RULE")")"; do
    rmdir "$dir" 2>/dev/null || true
  done
  say "Akinator uninstalled."
  exit 0
fi

# --- install: Claude Code -----------------------------------------------------

if [ "$WANT_CLAUDE" -eq 1 ]; then
  if [ -z "$CLAUDE_BIN" ]; then
    warn "Claude Code CLI not found. In the VS Code extension: type /plugins, open Marketplaces,"
    warn "add $REPO_URL, then install Akinator."
  else
    if [ "$LOCAL_SOURCE" -eq 1 ]; then MARKET="$SRC"; else MARKET="$REPO_URL#$REF"; fi
    # Adding a marketplace whose name already exists replaces its source, so this
    # both installs and switches an older registration over.
    claude_run plugin marketplace add "$MARKET" --scope "$CLAUDE_SCOPE"
    claude_run plugin install akinator@akinator --scope "$CLAUDE_SCOPE" || true
    claude_run plugin update akinator@akinator --scope "$CLAUDE_SCOPE" >/dev/null 2>&1 || true
    say "Claude Code: akinator@akinator installed ($CLAUDE_SCOPE scope). Restart Claude, then /akinator:everything."
  fi
fi

# --- install: the one skill, for Codex and Cursor ---------------------------

if [ "$WANT_CODEX" -eq 1 ] || [ "$WANT_CURSOR" -eq 1 ]; then
  remove_our_skills "$SKILLS_ROOT"
  mkdir -p "$SKILLS_ROOT"
  cp -R "$SRC/.agents/skills/akinator" "$SKILLS_ROOT/akinator"
  find "$SKILLS_ROOT/akinator" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
  say "installed the akinator skill to $SKILLS_ROOT/akinator"
fi

if [ "$WANT_CODEX" -eq 1 ]; then
  write_block "$CONTRACT_FILE"
  say "Codex: \$akinator is the one entry point; the block makes it always on."
fi

if [ "$WANT_CURSOR" -eq 1 ]; then
  mkdir -p "$(dirname -- "$CURSOR_RULE")"
  cp "$SRC/.agents/cursor/akinator.mdc" "$CURSOR_RULE"
  say "wrote $CURSOR_RULE"
  say "Cursor: /akinator is the one entry point; the rule makes it always on."
fi

say ""
say "Done. Re-run this installer to update; add --uninstall to remove."
