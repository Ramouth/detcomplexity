#!/usr/bin/env bash
# Search mathlib declarations by regex on the declaration line (name + start of statement).
# Usage: tools/find.sh 'det_fromBlocks'   [subdir under Mathlib/, optional]
cd "$(dirname "$0")/../.lake/packages/mathlib/Mathlib/${2:-}" || exit 2
grep -rnE "^(protected |private |noncomputable )*(theorem|lemma|def|abbrev|instance|structure|class) [^:]*$1" . | cut -c1-260 | head -${3:-40}
