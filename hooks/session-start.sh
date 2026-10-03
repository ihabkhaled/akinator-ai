#!/bin/sh
# Akinator Claude SessionStart hook: inject the always-on contract before prompt 1.
set -u
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
cat <<'CONTRACT'
# AKINATOR IS NOT OPTIONAL

YOU DO NOT GET TO SKIP IT BECAUSE THE PROMPT DIDN'T NAME IT.
STOP BEING LAZY. YOU ARE NOT TOO CLEVER FOR THE PROCEDURE.
SKIPPING IT IS THE ONE THING YOU ARE NOT ALLOWED TO DO.
THE OWNER SHOULD NEVER HAVE TO REPEAT THEMSELVES.
Every prompt, every repository, no slash command: run the full pass.

No slash command is required. Treat every user prompt as entering Akinator first.
For repository-changing work, load Akinator's one skill (`everything`) and run
its complete pass. Its twelve stations are reference files inside that skill,
opened as the work reaches them. `/akinator:everything` is the one explicit
command - it is the same skill.

ASK -> RESOLVE -> AUDIT -> PLAN -> IMPLEMENT -> DOCUMENT -> SKILLIFY -> RULE ->
CONTEXTIFY -> MEMOIZE -> INDEX+SYNC -> VERIFY

Every prompt is documented everywhere it lands, in the same batch: the living
wiki (product, business, market, requirements, drift, architecture, libraries,
stack, infra, testing, UX, project, decisions, changes), README and install docs,
every agent router, rules, memory, context and the ledger. Ask a grouped battery
of questions with recommended defaults; honest gaps only, never invented facts.
Gain context cheaply with akinator_context.py pack, trace every changed path
(akinator_trace.py), keep sensitive data named and never exposed
(akinator_sensitive.py), and own the reversible decisions.

Code + knowledge is the change. Preserve WHAT, WHY, WHO/agent when knowable,
WHEN, BEFORE, NOW, NEXT, business/product intent, technical reasoning, decisions,
failures, constraints and consequences. Record failures; reusable prevention
becomes an enforced rule. Repeatable procedures become skills.

Adopt existing repo conventions. One canonical home per fact. Never guess on
money, permissions, deletion, security or public contracts. Knowledge work is
same-batch, never follow-up. Gate once, late and scoped. Never put knowledge
checks in git hooks.
CONTRACT
FOUND=""
for path in CLAUDE.md AGENTS.md CODEX.md .cursor/rules rules skills context memory docs .ai; do
  if [ -e "$PROJECT_DIR/$path" ]; then FOUND="$FOUND $path"; fi
done
if [ -n "$FOUND" ]; then
  printf '\nKnowledge entry points:%s\nResolve them before planning.\n' "$FOUND"
else
  printf '\nNo knowledge layer detected. Use Akinator onboarding behavior automatically; do not require another command.\n'
fi
exit 0
