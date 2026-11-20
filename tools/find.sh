#!/usr/bin/env bash
# Search mathlib declarations by regex on the declaration line (name + start of statement).
# Usage: tools/find.sh 'det_fromBlocks'   [subdir under Mathlib/, optional]
cd "$(dirname "$0")/../.lake/packages/mathlib/Mathlib/${2:-}" || exit 2
[ -n "${1:-}" ] || { echo "usage: tools/find.sh <regex> [subdir] [max]"; exit 2; }
out=$(grep -rnE "^(protected |private |noncomputable )*(theorem|lemma|def|abbrev|instance|structure|class) [^:]*$1" .) || { echo "no match (or bad regex)"; exit 1; }
echo "$out" | cut -c1-260 | head -${3:-40}
