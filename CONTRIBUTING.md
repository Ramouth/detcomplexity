# Contributing

Progress here lives in code, and every unit of work is small. You do not need
to understand the whole programme to help. Humans and agents follow the same
rules; agents should also read `CLAUDE.md`.

## Scope: only PRs that advance the framework

A PR is welcome if, after it merges, the machine can tell that something moved.
That means exactly one of:

| Kind | What it does | Who decides |
|---|---|---|
| **Proof** | Proves a task from `DetComplexity/Open/` and moves it into the library | the referee alone |
| **Certificate** | Adds a data file that the verifier accepts | the referee alone |
| **Statement** | Adds, splits, corrects or relabels a task or a definition | the referee plus a human reviewer |
| **Rules and tools** | Improves the referee, the scripts or these instructions | a human reviewer |

Not welcome, and closed without discussion:

- claimed solutions to P vs NP, VP vs VNP or any open bound that do not come as
  one of the four kinds above;
- prose-only arguments, essays and ideas with nothing for the referee to check
  (open an issue instead);
- proofs of results that are not on the board. Add the statement first, as its
  own PR, then prove it;
- anything that makes the scoreboard say more without the machine checking more.

A big result arrives here the same way a small one does: as a chain of small
merged tasks. If a task is too big, the useful contribution is a Statement PR
that splits it.

## Proof PRs

1. Claim the task: open an issue or draft PR titled with the task id (`T-009`),
   on a branch `task/T-009`. One task per PR.
2. Prove it. **Do not change the statement**, including whether an argument is
   explicit or implicit. The referee compares every statement with
   `statements.lock` and fails on any difference. If a statement is wrong or
   awkward, stop and open a Statement PR.
3. Move the theorem out of `Open/` into the library:
   - `Basic.lean`: definitions and facts that need nothing else;
   - `Universality.lean`: existence of representations and general closure
     properties of dc (products, substitution, padding);
   - `Permanent.lean`: anything about the permanent;
   - a new file if none fits. Library files never import from `Open/`.
   Mind the `variable` lines: they differ between files, and a cut-and-paste can
   silently change binders. The lock check will tell you.
4. Replace the `TASK ...` docstring with a one-line description of the result.
5. Helper lemmas are fine. Make them `private` unless they are useful on their
   own; public ones appear on the board.
6. If the theorem is a new bound on `dc(perm_n)`, register it in the
   `LEAN_LOWER` / `LEAN_UPPER` table at the top of `tools/board.py`, or the
   scoreboard will not move.
7. Run `tools/check.sh` and commit everything it regenerated (`README.md`,
   `statements.lock`) together with the proof.

## Certificate PRs

Add a JSON file to `data/certificates/` in the format documented in
`tools/verify_data.py`: an explicit matrix whose determinant is the permanent.
A smaller matrix than the current best for some n moves the scoreboard.

## Statement PRs

Add a theorem with `sorry` to `DetComplexity/Open/`. The docstring's first line
is `TASK <id> | <easy|medium|hard> | <title>`, followed by a hint and a source.
Before stating a construction (an explicit object claimed to have a property),
test it on small cases in `experiments/`; a false statement wastes everyone's
time. To change or remove an existing statement, run the referee with
`ALLOW_STATEMENT_CHANGE=1` and say why in the PR. Label the PR
`statement-change`.

A human reviews these because the machine cannot judge whether a statement says
what the mathematics means, or whether a definition is the right one.

## What the referee enforces

`tools/check.sh` regenerates the scoreboard and the lock file and exits 0 only
if: the build passes; `sorry` appears only in `Open/`; no theorem outside
`Open/` depends on `sorry` or on axioms other than `propext`,
`Classical.choice`, `Quot.sound`; no theorem inside `Open/` is already proved;
no existing statement changed; every certificate verifies. CI runs
`tools/check.sh --check`, which also fails if the committed generated files
were stale. It prints build warnings; clean up the ones in your own code.

## Repository settings (for maintainers)

- Protect `main`: require the `referee` check, forbid direct pushes.
- Proof and Certificate PRs may merge on a green referee alone.
- Require one approving review on PRs labelled `statement-change` and on any
  PR touching `tools/`, `.github/`, `CONTRIBUTING.md` or `CLAUDE.md`.
- After merging, run `tools/credit.py` on `main` and commit `CREDITS.md`.
- When the instructions change, rerun the cold-start test: give a fresh agent
  only the repository and two tasks, and ask it to report every point of
  friction. Fix what it finds.

## Setup

Install [elan](https://github.com/leanprover/elan), then:

```
lake exe cache get    # download prebuilt mathlib; never build it from source
tools/check.sh
```

Do not run `lake update` unless the PR is specifically a mathlib bump.
Python 3 with `sympy` is needed for the data checks.
