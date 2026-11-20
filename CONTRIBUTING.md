# Contributing

The project is built so that progress lives in code and every unit of work is
small. You do not need to understand the whole programme to help.

## The three kinds of contribution

1. **Prove an open task.** Open tasks are the theorems in `DetComplexity/Open/`.
   `BOARD.md` lists them with a difficulty.
2. **Add a certificate.** An explicit matrix whose determinant is the
   permanent, as a JSON file in `data/certificates/`. A smaller matrix than the
   current best for some n moves the scoreboard. `tools/verify_data.py`
   checks it by exact computation; nobody has to trust you.
3. **Add a task.** State a known result as a new theorem with `sorry` in
   `DetComplexity/Open/`, with a docstring whose first line is
   `TASK <id> | <easy|medium|hard> | <title>` and a source. Splitting a hard
   task into easier ones counts, and is often the most useful thing to do.

## Doing a task

1. Claim it: open an issue or draft PR titled with the task id (`T-005`), on a
   branch `task/T-005`. One task per PR.
2. Prove it. Do not change the statement. If the statement is wrong or
   awkward, stop and open a separate PR that changes only the statement.
3. Move the proved theorem out of `Open/` into the library file where it
   belongs, and import nothing from `Open/` there.
4. Run `tools/check.sh`. It rebuilds, re-verifies all data and regenerates
   `BOARD.md`. Commit the regenerated board with your proof.

## What the referee enforces

`tools/check.sh` (also run by CI) fails if: the build fails; `sorry` appears
outside `Open/`; a theorem outside `Open/` depends on `sorry` or on any axiom
other than `propext`, `Classical.choice`, `Quot.sound`; a theorem inside
`Open/` is already proved; a certificate does not verify; `BOARD.md` is stale.

Humans review two things the machine cannot: whether a new *statement* says
what the mathematics means, and whether a new *definition* is the right one.
Proofs need no review beyond the referee.

## Setup

Install [elan](https://github.com/leanprover/elan), then:

```
lake exe cache get    # download prebuilt mathlib; never build it from source
tools/check.sh
```

Python 3 with `sympy` is needed for the data checks. Agents: read `CLAUDE.md`.
