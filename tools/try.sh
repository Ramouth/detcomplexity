#!/usr/bin/env bash
# Run a scratch Lean file against the project and print compact diagnostics.
# Usage: tools/try.sh path/to/Scratch.lean [max_lines, default 80]
# Put `exact?`, `#check`, `#print`, `simp?` in the file; this is the cheap way
# to ask Lean a question instead of guessing lemma names. Deprecation and
# module-system notices are filtered out so real errors are not truncated.
export PATH="$HOME/.elan/bin:$PATH"
f=$(realpath "$1"); cd "$(dirname "$0")/.." || exit 2
lake env lean "$f" 2>&1 | sed "s|$f|scratch|g" | grep -v "module system" | cut -c1-600 | head -${2:-80}
