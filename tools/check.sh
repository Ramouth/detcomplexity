#!/usr/bin/env bash
# One-shot referee: build, show only errors/warnings that matter, scan for
# sorry/admit/axiom, and print the axioms behind every theorem in DetComplexity/.
# Usage: tools/check.sh            (exit 0 = clean)
export PATH="$HOME/.elan/bin:$PATH"
cd "$(dirname "$0")/.." || exit 2
status=0
out=$(lake build 2>&1); rc=$?
echo "$out" | grep -E "^(error|warning):|error:|sorry" | grep -v "module system" | head -40
if [ $rc -ne 0 ]; then echo "BUILD: FAILED"; exit 1; fi
echo "BUILD: ok"
if grep -rnE "\b(sorry|admit)\b|^\s*axiom\b" DetComplexity/; then echo "GAPS: found"; status=1; else echo "GAPS: none"; fi
tmp=$(mktemp --suffix=.lean)
{ echo "import DetComplexity"; echo "open DetComplexity"
  grep -rhoE "^(theorem|lemma) [A-Za-z_0-9'.]+( *$| +[[({:])" DetComplexity/ | awk '{print "#print axioms " $2}'; } > "$tmp"
ax=$(lake env lean "$tmp" 2>&1); rm -f "$tmp"
bad=$(echo "$ax" | grep -v "depends on axioms: \[propext, Classical.choice, Quot.sound\]" | grep -v "does not depend on any axioms" | grep -vE "depends on axioms: \[(propext|Classical.choice|Quot.sound)(, (propext|Classical.choice|Quot.sound))*\]")
n=$(echo "$ax" | grep -c "axioms")
if [ -n "$bad" ]; then echo "AXIOMS: problem"; echo "$bad" | head -20; status=1; else echo "AXIOMS: $n theorems, standard only"; fi
exit $status
