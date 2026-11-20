# Instructions for the agent

This is a Lean 4 + mathlib project formalizing determinantal complexity, the
first scoreboard of Geometric Complexity Theory. Read README.md for context.

## Setup

Follow "Setup" in `CONTRIBUTING.md`. If `.lake/` already exists and
`tools/check.sh` passes, do nothing. Never run `lake update` and never build
mathlib from source; if the cache download fails, stop and report.

## What to work on

The scoreboard at the top of `README.md` is the state of the project, generated from the code. Open tasks are
the theorems in `DetComplexity/Open/`. `CONTRIBUTING.md` has the procedure;
follow it exactly, including moving a proved theorem out of `Open/`.

Take one task at a time. Do not start a task marked `hard`; propose a split
into smaller tasks (a Statement PR) instead. Only PRs of the four kinds in
`CONTRIBUTING.md` are in scope: never submit prose arguments or claimed
solutions that the referee cannot check.

## Rules

- `sorry` is allowed only in `DetComplexity/Open/`. No `admit`, no new `axiom`.
- `tools/check.sh` must pass before every commit. It checks axioms for you.
- Never change or weaken a statement to make a proof go through. If a
  statement is wrong, stop and explain.
- Verify, do not trust: your own claim that something works counts for
  nothing until `tools/check.sh` exits 0.
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
- Before stating or formalizing a construction (an explicit object claimed to
  have a property, such as a matrix with a given determinant), write it as an
  executable spec in `experiments/` and test small cases. Routine lemmas do
  not need one. Current specs: `experiments/universality.py`,
  `experiments/grenet.py`, `experiments/grenet_split.py` (tasks T-007, T-009
  to T-011).
