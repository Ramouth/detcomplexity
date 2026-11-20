# Instructions for agents

This is a Lean 4 + mathlib project on determinantal complexity: how large a
determinant must be to express a given polynomial, the quantity behind the
permanent-versus-determinant problem. `README.md` explains the aim.
`CONTRIBUTING.md` is the procedure and applies to you in full; this file adds
only what is specific to agents.

## Setup

If `.lake/` exists and `tools/check.sh` passes, do nothing. Otherwise follow
"Setup" in `CONTRIBUTING.md`. Never run `lake update`. Never build mathlib from
source; if the cache download fails, stop and say so.

## What to work on

The scoreboard at the top of `README.md` is the state of the project. Open
tasks are the theorems in `DetComplexity/Open/`. Take one task at a time, the
one you were given, or the easiest open one. Do not start a task marked
`hard`: say that it needs splitting, and stop.

Stay inside the four kinds of PR in `CONTRIBUTING.md`. Never produce prose
arguments or claimed solutions that the referee cannot check.

## What kind of contribution is wanted

Read "The hypothesis" in `README.md`. In short: do not attempt long open-ended
derivations. The project wants hard questions turned into gaps with a shape.
When you propose tasks (a Statement PR), prefer, in this order:

1. statements whose proof is a witness that can be checked (an explicit
   matrix, a solution of a linear system, an object with stated properties);
2. geometric restatements of facts already proved here: symmetry, invariance
   under a group action, membership in an orbit or an image;
3. structure that later statements need (definitions, with the smallest facts
   that show they are the right ones).

A split of a hard task is good when each piece is a gap of this kind, not
merely when each piece is short.

## Rules

- `sorry` only in `DetComplexity/Open/`. No `admit`, no `axiom`, no
  `native_decide`.
- Never change or weaken a statement or a definition to make a proof go
  through. If one is wrong, stop and explain. If the referee says a statement
  changed and you are sure it did not, that is a referee bug: stop and report
  it. Never set `ALLOW_STATEMENT_CHANGE` yourself.
- **Always validate that the README is up to date before you finish.** Bring
  your branch up to date with `main`, run `tools/check.sh`, commit what it
  regenerated, then confirm `tools/check.sh --check` exits 0. Do this again if
  `main` moved while you worked. Never edit the scoreboard block or
  `statements.lock` by hand, and never resolve a conflict in them by hand.
- Verify, do not trust: your own belief that something works counts for
  nothing until `tools/check.sh --check` exits 0. Never report "done" from memory.
- One task per commit, with a message naming the theorem and the task id.
- If you cannot open a PR yourself, leave the work on a branch `task/<id>` and
  put your report where the PR description would go (see below).

## Your report

Fill in `.github/pull_request_template.md`. Under "Notes" add: what you had to
look up, where you got stuck, and anything in this repository's instructions
or tools that was unclear, wrong or slowed you down. That last part is wanted;
the instructions are tested the same way the proofs are.

## Working method: compute first, reason second

Keep reasoning out of prose wherever a cheap command can answer instead.

- `tools/check.sh` is the referee. Its output is a few lines; read all of them.
- `tools/find.sh <regex> [subdir]` and `tools/show.sh <name>` look lemmas up in
  the mathlib source. Do not guess lemma names.
- `tools/try.sh scratch/<file>.lean` asks Lean directly (`exact?`, `simp?`,
  `#check`). Scratch files live in `scratch/`, which git ignores. Start one
  with `import DetComplexity`, then copy the `open`, `namespace` and `variable`
  lines of the file you are working towards, or the statement will not be the
  same one.
- Before stating or formalizing a construction (an explicit object claimed to
  have a property, such as a matrix with a given determinant), write it as an
  executable spec in `experiments/` and test small cases. Routine lemmas do
  not need one. Current specs: `experiments/universality.py`,
  `experiments/grenet.py`, `experiments/grenet_split.py` (tasks T-007, T-009
  to T-011).
