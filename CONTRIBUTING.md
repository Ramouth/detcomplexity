# Contributing

Progress here lives in code, and every unit of work is small. You do not need
to understand the whole programme to help. Humans and agents follow the same
rules; agents should also read `CLAUDE.md`.

## Scope: only PRs that advance the framework

A PR is welcome if, after it merges, the machine can tell that something moved.
That means exactly one of:

| Kind | What it does | What the maintainer checks before merging |
|---|---|---|
| **Proof** | Proves a task from `DetComplexity/Open/` and moves it into the library | referee green; only allowed files touched |
| **Certificate** | Adds a file to `data/certificates/` that the verifier accepts | referee green; only allowed files touched |
| **Statement** | Adds, splits, corrects or relabels a task; adds or changes a definition; edits `data/literature.json` | the content, by someone who can judge the mathematics |
| **Rules and tools** | Changes the referee, scripts, CI, dependencies or these instructions | the content |

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

## How merging works (stage one)

A maintainer merges every PR. Nothing merges automatically.

For Proof and Certificate PRs the maintainer does not read the mathematics.
They check two mechanical things: the `referee` check is green, and the PR
touches only the allowed files, which are `DetComplexity/**/*.lean`,
`data/certificates/*.json`, the import list `DetComplexity.lean`, the generated
block in `README.md` and `statements.lock`. A PR that touches anything else is a Statement or Rules PR,
whatever it calls itself.

Stage two (not built): an independent proof checker in a separate CI job, a
gate that classifies PRs by changed paths, and automatic merging. Until then,
do not describe a merged proof as verified without a human in the loop.

## Keep the scoreboard current: your job, every time

The README scoreboard and `statements.lock` are generated. Two PRs that are
each correct can still leave them wrong once both merge. So:

1. Before you open a PR, and again whenever `main` has moved, bring your branch
   up to date with upstream: `git fetch origin`, then `git rebase origin/main`
   if the PR is not open yet, or `git merge origin/main` once it is. Do not
   rewrite commits a maintainer may already have seen.
2. Run `tools/check.sh`. It regenerates both files from the code.
3. Commit what it changed: into the proof commit before the PR is open, as a
   follow-up commit `Regenerate scoreboard` afterwards. Maintainers squash on
   merge, so `main` gets one commit per task either way. Keep commit messages
   true after an update.
4. Run `tools/check.sh --check`; it must exit 0.

A merge that git reports as clean can still leave the block wrong: two PRs
that each raise a count from 18 to 19 merge without conflict, and the true
count is 20. Always regenerate after updating, conflict or not.

Never resolve a conflict in the scoreboard block or in `statements.lock` by
hand. Take either side (the same side for both files), finish the merge, run
`tools/check.sh`, commit the result. The merge commit itself may fail the
check; that is fine, because PRs are squashed. If you find
`main` itself stale, fix that first with a PR that contains only the
regenerated files.

## Proof PRs

1. Pick a task from the scoreboard. Tasks marked easy or medium are not
   claimed: the first green PR is merged and duplicates are closed. Use a
   branch named `task/T-009`. One task per PR.
2. Prove it. **Do not change the statement**, including whether an argument is
   explicit or implicit. The referee compares every statement and definition
   with `statements.lock` and fails on any difference. If a statement is wrong
   or awkward, stop and open a Statement PR.
3. Move the theorem out of `Open/` into the library:
   - `Basic.lean`: definitions and facts that need nothing else;
   - `Universality.lean`: existence of representations and general closure
     properties of dc (products, substitution, padding);
   - `Permanent.lean`: anything about the permanent;
   - `LinearAlgebra.lean` (create it if absent): general facts about matrices,
     determinants and permanents that do not mention dc;
   - a new file if none fits, imported from `DetComplexity.lean`. Library files
     never import from `Open/`.
   Mind the `variable` lines: they differ between files, and a cut-and-paste can
   silently change binders. Moving a theorem unchanged does not alter its lock
   entry; if the referee reports a change it prints the old and new lines.
   **If you are sure nothing changed and the referee still says so, stop and
   report it as a referee bug. Never use `ALLOW_STATEMENT_CHANGE` to get past it.**
4. Replace the `TASK ...` docstring with a one-line description of the result.
5. Make helper lemmas `private` unless they are useful on their own. The
   number that matters is tasks closed, not theorems added.
6. Update the scoreboard as described above.

If you have no access to GitHub (many agents do not): do the same on a local
branch, commit, and hand back the branch name together with the filled-in text
of `.github/pull_request_template.md`. A person opens the PR.

## Certificate PRs

Add a JSON file to `data/certificates/` in the format documented in
`tools/verify_data.py`: an explicit matrix whose determinant is the permanent.
Only a matrix smaller than the current best for its n is worth a PR.

## Statement PRs

These need a reviewer because the machine cannot judge whether a statement says
what the mathematics means, whether a definition is the right one, or whether a
cited bound is real.

- **New task:** a theorem with `sorry` in `DetComplexity/Open/`. The docstring's
  first line is `TASK <id> | <easy|medium|hard> | <title>`, then a hint and a
  source. State the hypotheses the source states (field, characteristic).
- **New bound on dc(perm_n):** also add its theorem name to `LEAN_LOWER` or
  `LEAN_UPPER` in `tools/board.py` in this PR, so that the later Proof PR needs
  no change to the tools.
- **Constructions:** before stating that an explicit object has a property,
  test it on small cases in `experiments/`. A false statement wastes everyone's
  time.
- **Changing or removing a statement or definition:** run the referee with
  `ALLOW_STATEMENT_CHANGE=1` and explain why in the PR.
- **Literature:** every entry in `data/literature.json` names the paper, the
  exact result and its hypotheses, and says whether the source was read.
- **Hard tasks:** claim by opening an issue that states an expiry date. Prefer
  splitting to proving.

Every statement and definition in the repository is currently unreviewed by a
mathematician. That is the project's main open risk; reviews are welcome as
issues.

## Rules and tools PRs

Any change under `tools/`, `.github/`, the Lake files (`lakefile.toml`,
`lake-manifest.json`, `lean-toolchain`), `CONTRIBUTING.md`, `CLAUDE.md` or
`README.md` outside the generated block. A mathlib or toolchain bump is one of
these, on its own, with nothing else in the PR. When the instructions change,
rerun the cold-start test: give a fresh agent only the repository and two
tasks, and ask it to report every point of friction.

## What the referee enforces

`tools/check.sh` builds the project, asks Lean for every constant the project
defines (including private and auxiliary ones) and exits 0 only if:

- nothing outside `Open/` depends on `sorry`;
- nothing is declared as an axiom or uses an axiom other than `propext`,
  `Classical.choice`, `Quot.sound`;
- no theorem inside `Open/` is already proved, and every one has a `TASK` line
  with a unique id;
- no existing statement or definition changed or disappeared, judged by a hash
  of the full term and not only by how it prints;
- every certificate verifies, and no literature bound contradicts a verified one.

Without arguments it then regenerates the scoreboard and the lock; if it
found problems it writes nothing. With `--check` (used by CI) it never writes
and also fails if either file is stale. Statements are compared with the lock
at the point where your branch left `origin/main`, the same comparison CI
makes. A run takes one to three minutes (longer after a change to
`Basic.lean`, which rebuilds everything); set command timeouts accordingly.

## What it does not enforce

Be honest about these; a reviewer may ask.

- One task per PR, branch names, and replacing the `TASK` docstring.
- That a new public theorem was a task first.
- Proof quality. Build warnings are printed, not fatal; clean up your own.
- **Lean code runs programs while it compiles.** A deliberately malicious PR
  can change what the referee sees. The referee protects against mistakes and
  against the shortcuts found in the audit of 2026-11-20, not against that.
  This is why a maintainer merges and why stage two needs an independent checker.

## Repository settings (for maintainers)

- Protect `main`: require the `referee` check, forbid direct and force pushes,
  require branches to be up to date before merging. Squash-merge PRs.
- For Proof PRs, also look at where the theorem was put (step 3); the referee
  does not check placement.
- Create the label `statement-change`. CI allows statement changes only on PRs
  carrying it; only people with triage rights can set it, and it must be set
  again after new commits are pushed.
- First-time contributors' workflow runs need approval; keep that default.

## Setup

Install [elan](https://github.com/leanprover/elan), then:

```
lake exe cache get    # download prebuilt mathlib; never build it from source
tools/check.sh
```

Never run `lake update` in a Proof, Certificate or Statement PR. Python 3 with
`sympy` is needed for the data checks. Keep scratch files in `scratch/`, which
git ignores.
