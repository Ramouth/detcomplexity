#!/usr/bin/env bash
# The referee. One command, short output, exit 0 only if everything holds:
#   build passes; `sorry` appears only under DetComplexity/Open/; no `axiom`;
#   every certificate verifies; every theorem's status matches where it lives;
#   no existing statement changed; README scoreboard and statements.lock regenerated.
# Usage: tools/check.sh           before committing: regenerates the generated files
#        tools/check.sh --check   CI: additionally fails if a generated file was stale
# Env:   ALLOW_STATEMENT_CHANGE=1 for a statement-change PR; STATEMENT_BASE=<git ref> (default HEAD)
export PATH="$HOME/.elan/bin:$PATH"
cd "$(dirname "$0")/.." || exit 2
out=$(lake build 2>&1); rc=$?
if [ $rc -ne 0 ]; then echo "$out" | grep -E "error" -A8 | cut -c1-300 | head -40; echo "BUILD: FAILED"; exit 1; fi
warn=$(echo "$out" | grep -E "^warning: DetComplexity" | grep -v "module system" | grep -v "declaration uses .sorry." | cut -c1-200)
if [ -n "$warn" ]; then echo "BUILD: ok, with $(echo "$warn" | wc -l) warning(s) to clean up:"; echo "$warn" | head -10; else echo "BUILD: ok"; fi
status=0
if grep -rnE "\b(sorry|admit)\b" DetComplexity/ --include=*.lean | grep -v "^DetComplexity/Open/" | grep -vE "^[^:]+:[0-9]+:\s*(--|/-|[^:]*\`sorry\`)"; then echo "GAPS: sorry outside Open/"; status=1; else echo "GAPS: none outside Open/"; fi
if grep -rnE "^\s*axiom\b" DetComplexity/; then echo "AXIOM: declared"; status=1; fi
python3 tools/board.py "$@" | grep -v "^ok  " || status=1
[ "${PIPESTATUS[0]}" -ne 0 ] && status=1
exit $status
