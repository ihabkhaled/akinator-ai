#!/bin/sh
# Akinator Claude UserPromptSubmit hook: three loud lines on every prompt, so the
# always-on contract survives long sessions. Display-only: prints context,
# exits 0, never returns a permission decision.
printf '%s
' "AKINATOR IS NOT OPTIONAL. NO COMMAND NEEDED. STOP BEING LAZY: RUN THE FULL PASS."
printf '%s
' "BEFORE DONE: VERSION BUMP (akinator_version.py), TRACE CHECK, SENSITIVE GUARD AND SCAN."
printf '%s
' "THE OWNER SHOULD NEVER HAVE TO REPEAT THEMSELVES."
exit 0
