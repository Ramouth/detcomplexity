#!/usr/bin/env bash
# Print a declaration with its full statement from mathlib source.
# Usage: tools/show.sh Matrix.det_fromBlocks₁₁   (last name component is searched)
cd "$(dirname "$0")/../.lake/packages/mathlib/Mathlib" || exit 2
name="${1##*.}"
grep -rnE -A${2:-8} "^(protected |private |noncomputable )*(theorem|lemma|def|abbrev) ([A-Za-z_0-9'.]*\.)?$name( |$|\[|\{|\()" . | cut -c1-300 | head -60
