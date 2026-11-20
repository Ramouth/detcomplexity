# Instructions for the agent

This is a Lean 4 + mathlib project formalizing determinantal complexity, the
first scoreboard of Geometric Complexity Theory. Read README.md for context.

## Setup (do first)

1. Make sure `elan` is installed (https://github.com/leanprover/elan).
2. Run `lake update`, then make `lean-toolchain` identical to
   `.lake/packages/mathlib/lean-toolchain` (copy it over if they differ,
   then run `lake update` again).
3. Run `lake exe cache get`. Never build mathlib from source; if the cache
   fails, stop and report.
4. Run `lake build`.

## Task order

1. **Make `DetComplexity/Basic.lean` compile with no `sorry`.** It was
   drafted without access to a compiler, so lemma names (for example
   `Units.neg_smul`, `totalDegree_finsetSum`, `Nat.sInf_mem`) may need fixing.
   Keep the theorem *statements* unchanged; only change proofs. If a
   statement is genuinely wrong, stop and explain before changing it.
2. **Tier 1:** prove `totalDegree_perm` in `DetComplexity/Permanent.lean`.
3. Then stop and report. Do not start Tier 2 or later without the user's go-ahead.

## Rules

- Never leave `sorry`, `admit` or new `axiom`s in finished work. Check with
  `grep -rn "sorry\|admit\|axiom" DetComplexity/`.
- Before calling something done, run `#print axioms` on the main theorems.
  Only `propext`, `Classical.choice` and `Quot.sound` are acceptable.
- Don't weaken statements to make proofs go through.
- Commit after each theorem that compiles, with a message naming the theorem.
- At the end, report: what compiled, what you had to change, how long it
  took, and where you got stuck. That report is the actual experiment result.

## Working method: compute first, reason second

Keep reasoning out of prose wherever a cheap command can answer instead.

- `tools/check.sh` is the referee: build, gap scan, axiom check, in a few lines.
  Run it before every commit; never report "done" from memory.
- `tools/find.sh <regex> [subdir]` and `tools/show.sh <name>` look lemmas up in
  the mathlib source. Do not guess lemma names.
- `tools/try.sh <scratch.lean>` asks Lean directly (`exact?`, `simp?`, `#check`).
  Keep scratch files outside `DetComplexity/`.
- Before formalizing any construction, write it as an executable spec in
  `experiments/` (sympy) and test it on small cases. The Lean proof then
  follows a construction already known to be right, and the invariant in the
  script's docstring is the proof plan. Current specs:
  `experiments/universality.py` (Tier 2a), `experiments/grenet.py` (Tier 2b).
