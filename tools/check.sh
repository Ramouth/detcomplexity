#!/usr/bin/env bash
# The referee. One command, short output, exit 0 only if everything holds:
#   build passes; `sorry` appears only under DetComplexity/Open/; no `axiom`;
#   every certificate verifies; every theorem's status matches where it lives;
#   BOARD.md is regenerated from the code.
# Usage: tools/check.sh [--check]   (--check also fails on a stale BOARD.md; used by CI)
export PATH="$HOME/.elan/bin:$PATH"
cd "$(dirname "$0")/.." || exit 2
out=$(lake build 2>&1); rc=$?
if [ $rc -ne 0 ]; then echo "$out" | grep -E "error" -A8 | cut -c1-300 | head -40; echo "BUILD: FAILED"; exit 1; fi
echo "BUILD: ok"
status=0
if grep -rnE "\b(sorry|admit)\b" DetComplexity/ --include=*.lean | grep -v "^DetComplexity/Open/" | grep -vE "^[^:]+:[0-9]+:\s*(--|/-|[^:]*\`sorry\`)"; then echo "GAPS: sorry outside Open/"; status=1; else echo "GAPS: none outside Open/"; fi
if grep -rnE "^\s*axiom\b" DetComplexity/; then echo "AXIOM: declared"; status=1; fi
python3 tools/board.py "$@" || status=1
exit $status
