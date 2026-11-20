#!/usr/bin/env bash
# Run a scratch Lean file against the project and print compact diagnostics.
# Usage: tools/try.sh path/to/Scratch.lean [max_lines, default 80]
# Put `exact?`, `#check`, `#print`, `simp?` in the file; this is the cheap way
# to ask Lean a question instead of guessing lemma names. Keep scratch files in
# scratch/ (ignored by git). Exit code is Lean's: nonzero if the file has errors.
set -o pipefail
[ -f "${1:-}" ] || { echo "usage: tools/try.sh <file.lean> [max_lines]"; exit 2; }
export PATH="$HOME/.elan/bin:$PATH"
f=$(realpath "$1"); cd "$(dirname "$0")/.." || exit 2
out=$(lake env lean "$f" 2>&1); rc=$?
out=$(echo "$out" | sed "s|$f|scratch|g" | grep -v "module system" | sed -E 's/^(.{600}).+$/\1 ...[line cut at 600 chars]/')
n=$(echo "$out" | wc -l); echo "$out" | head -${2:-80}
[ "$n" -gt "${2:-80}" ] && echo "... ($n lines in total; pass a larger max_lines)"
exit $rc
