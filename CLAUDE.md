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

## What to work on

`BOARD.md` is the state of the project, generated from the code. Open tasks are
the theorems in `DetComplexity/Open/`. `CONTRIBUTING.md` has the procedure;
follow it exactly, including moving a proved theorem out of `Open/`.

Take one task at a time. Do not start a task marked `hard` without the user's
go-ahead; propose a split into smaller tasks instead.

## Rules

- `sorry` is allowed only in `DetComplexity/Open/`. No `admit`, no new `axiom`.
- `tools/check.sh` must pass before every commit. It checks axioms for you.
- Never change or weaken a statement to make a proof go through. If a
  statement is wrong, stop and explain.
- Commit after each theorem that compiles, with a message naming the theorem.
- End with a report: what was proved, what had to change, how long it took,
  where you got stuck, and anything in the repo that slowed you down.

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
