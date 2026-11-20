# DetComplexity: a pilot for open, agent-assisted GCT

## The idea

Geometric Complexity Theory (GCT) is the most ambitious geometric program
toward P ≠ NP. Its framework exists, but only on paper: dense, scattered and
unverified. Building frameworks earns little prestige, so the work stalls.

This pilot tests a different model:

1. **Translate before inventing.** Formalize GCT's existing foundations in
   Lean 4 / mathlib, where every step is machine-checked.
2. **Use scoreboards, not vibes.** Organize progress around numbers that can
   move, so partial progress is measurable and claimable.
3. **Make tasks claimable.** Break the program into small, independent,
   verifiable tasks that humans *and* agents can take on (the bbchallenge /
   Equational Theories Project model).

## Scoreboard #1: determinantal complexity of the permanent

`dc(p)` = smallest m such that p = det(A) for an m×m matrix A of
affine-linear polynomials.

| Bound on dc(perm_n)            | Status in math        | Status here |
|--------------------------------|-----------------------|-------------|
| every p has a representation   | Valiant 1979          | **proved** (`exists_hasDetRep`) |
| ≥ n (degree bound)             | folklore              | **proved**, unconditional (`n_le_detComplexity_perm'`) |
| ≤ 2ⁿ − 1 (Grenet 2011)         | known                 | Tier 2b: construction tested for n ≤ 4 in `experiments/grenet.py`, not yet in Lean |
| ≥ n²/2 (Mignon–Ressayre 2004)  | best known, char 0    | Tier 3 |
| superpolynomial ⇒ VP ≠ VNP     | open                  | the goal |

## Roadmap

- **Tier 0 (done):** definitions; `totalDegree p ≤ dc p`.
- **Tier 1 (done):** `totalDegree (perm n) = n`, so `dc(perm_n) ≥ n` with no `sorry`.
- **Tier 2a (done):** universality, so the `∃ m` hypothesis is gone.
- **Tier 2b:** Grenet's upper bound `dc(perm_n) ≤ 2ⁿ − 1`.
- **Tier 3:** Mignon–Ressayre via the Hessian rank argument. This is
  research-grade formalization.
- **Tier 4:** GCT proper: orbit closures, occurrence/multiplicity
  obstructions, and stating the Bürgisser–Ikenmeyer–Panova no-go theorem.
- **Side track:** an open database of computed Kronecker/plethysm
  coefficients for small cases, with reproducible code.

## Running it

See `CLAUDE.md` for the local agent. For humans:

```
lake exe cache get
lake build
```
