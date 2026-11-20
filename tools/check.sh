#!/usr/bin/env bash
# The referee. One command, short output, exit 0 only if everything holds.
# It builds the project and then runs tools/board.py, which asks Lean for every
# constant in the project and checks axioms, open tasks, the statement lock,
# the certificates and the generated files. See the docstring of tools/board.py.
# Usage: tools/check.sh           before committing: regenerates README block and statements.lock
#        tools/check.sh --check   CI: writes nothing, fails if a generated file is stale
# Env:   ALLOW_STATEMENT_CHANGE=1 for a statement-change PR; STATEMENT_BASE=<git ref> (default HEAD)
set -o pipefail
for a in "$@"; do [ "$a" = "--check" ] || { echo "unknown argument: $a"; exit 2; }; done
export PATH="$HOME/.elan/bin:$PATH"
cd "$(dirname "$0")/.." || exit 2
command -v lake >/dev/null || { echo "BUILD: FAILED (lake not found; install elan)"; exit 1; }
out=$(lake build 2>&1); rc=$?
if [ $rc -ne 0 ]; then
  echo "$out" | grep -E "error" -A8 | cut -c1-300 | head -40
  echo "$out" | tail -5 | cut -c1-300
  echo "BUILD: FAILED"; exit 1
fi
warn=$(echo "$out" | grep -E "^warning: DetComplexity" | grep -v "module system" | grep -vE "^warning: DetComplexity/Open/.*declaration uses .sorry." | cut -c1-200)
if [ -n "$warn" ]; then echo "BUILD: ok, with $(echo "$warn" | wc -l) warning(s) to clean up:"; echo "$warn" | head -10; else echo "BUILD: ok"; fi
python3 tools/board.py "$@"
