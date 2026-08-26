#!/bin/sh
# Akinator SessionStart hook.
#
# Injects the behavioral contract - not a payload. The full creed, loop and
# taxonomy live in the `akinator` skill; this hook exists so the contract is the
# session's default operating mode before the first tool call, and so the agent
# knows which knowledge entry points this particular repo actually has.
#
# Contract: stdout of a SessionStart hook is added to the session context.
# Keep it short. Every line here costs context in every session forever.

set -u

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

cat <<'CONTRACT'
# Akinator is active

Ask everything. Document everything. Skillify everything. Rule everything.

A change is never the code alone. A change is the code plus the knowledge that
lets the next agent act on it in seconds. Half a change is no change.

Run every codebase touch through the twelve-station loop:
ASK -> RESOLVE -> AUDIT -> PLAN -> IMPLEMENT -> DOCUMENT -> SKILLIFY -> RULE ->
CONTEXTIFY -> MEMOIZE -> INDEX+SYNC -> VERIFY

Non-negotiable:
- Stations 6-11 happen in the same batch as station 5. "I'll document in a
  follow-up" is a prohibited sentence.
- The knowledge delta is declared at PLAN time, per batch. A batch with no
  knowledge delta must state why, explicitly.
- Gate once, at the end, scoped to what was touched. Never per edit, never
  per commit, never all-workspace.
- Never add knowledge or documentation checks to git hooks. Hooks gate code.
- Adopt, never impose: match this repo's existing conventions before creating
  anything new.

Load the `akinator` skill for the full creed, loop and knowledge taxonomy.
CONTRACT

# Report which knowledge entry points this repo actually has, so RESOLVE
# (station 2) starts from facts instead of guesses.
FOUND=""
for path in CLAUDE.md AGENTS.md CODEX.md GEMINI.md .cursorrules rules skills context memory docs .ai; do
  if [ -e "$PROJECT_DIR/$path" ]; then
    FOUND="$FOUND $path"
  fi
done

if [ -n "$FOUND" ]; then
  printf '\nKnowledge entry points present in this repo:%s\n' "$FOUND"
  printf 'RESOLVE from these before planning. Follow their indexes; do not re-derive.\n'
else
  printf '\nNo knowledge layer detected in this repo.\n'
  printf 'Offer /akinator:onboard before inventing a structure.\n'
fi

exit 0
