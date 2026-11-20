/-
# Open tasks

Every theorem in `DetComplexity/Open/` is a claimable task: a statement that is
believed true (known mathematics) but not yet proved here. This is the only
place where `sorry` is allowed. To complete a task, prove it, move the theorem
into the main library (outside `Open/`), and run `tools/check.sh`.

Docstring format, first line:  `TASK <id> | <difficulty> | <title>`
Do not change a statement while proving it; statement changes are their own PR.
-/
import DetComplexity.Permanent

open MvPolynomial Matrix

namespace DetComplexity

variable {R : Type*} [CommRing R] {σ τ : Type*}

/-- TASK T-001 | easy | Constants have dc at most 1
A `1 × 1` matrix with entry `C a`. -/
theorem detComplexity_C_le (a : R) : detComplexity (C a : MvPolynomial σ R) ≤ 1 := by
  sorry

/-- TASK T-002 | easy | A variable has dc exactly 1
Upper bound: a `1 × 1` matrix. Lower bound: `totalDegree_le_detComplexity'`. -/
theorem detComplexity_X [Nontrivial R] (i : σ) :
    detComplexity (X i : MvPolynomial σ R) = 1 := by
  sorry

/-- TASK T-003 | easy | dc is subadditive under products
Block-diagonal matrix; see `det_fromBlocks_zero₂₁` and `hasDetRep_of_matrix`. -/
theorem detComplexity_mul_le (p q : MvPolynomial σ R) :
    detComplexity (p * q) ≤ detComplexity p + detComplexity q := by
  sorry

/-- TASK T-004 | easy | Representations can be padded
Add a row and column with a single `1` on the diagonal. -/
theorem HasDetRep.succ {p : MvPolynomial σ R} {m : ℕ} (h : HasDetRep p m) :
    HasDetRep p (m + 1) := by
  sorry

/-- TASK T-007 | hard | Grenet's upper bound: dc(perm_n) ≤ 2^n - 1 (assembly)
Needs one more split before it is medium. Plan, following
`experiments/grenet_split.py`: index set = nonempty proper subsets, `u S = g S`,
check `u ᵥ* T = w` and `c - u ⬝ᵥ v = perm`, using T-009, T-010, T-011. Missing
pieces: (a) `n = 0` is a separate case (`perm R 0 = 1`, size 0); (b) T-011 is
stated for `Fin (n + 1)`, while `g S` is a permanent over a column subset
`S ⊆ Fin n`, so a bridging lemma is needed. Holds over any commutative ring.
Source: Grenet, manuscript 2011 (stated there for characteristic ≠ 2). -/
theorem detComplexity_perm_le (n : ℕ) : detComplexity (perm R n) ≤ 2 ^ n - 1 := by
  sorry

/-- TASK T-009 | medium | A bordered matrix with a solved linear system is a representation
If `det T = 1` and `u ᵥ* T = w` then `det [[T, v], [w, c]] = c - u ⬝ᵥ v`.
The proof of `exists_hasDetRep` already does this with an explicit inverse;
here `u = w T⁻¹` is given instead, so no inverse has to be exhibited
(`det T = 1` makes `T` invertible; then `Matrix.det_fromBlocks₁₁`). -/
theorem hasDetRep_of_solve {ι : Type*} [Fintype ι] [DecidableEq ι]
    (T : Matrix ι ι (MvPolynomial σ R)) (u v w : ι → MvPolynomial σ R) (c : MvPolynomial σ R)
    (hT : ∀ i j, (T i j).totalDegree ≤ 1) (hv : ∀ i, (v i).totalDegree ≤ 1)
    (hw : ∀ i, (w i).totalDegree ≤ 1) (hc : c.totalDegree ≤ 1)
    (hdet : T.det = 1) (hu : u ᵥ* T = w) :
    HasDetRep (c - u ⬝ᵥ v) (Fintype.card ι + 1) := by
  sorry

/-- TASK T-011 | medium | Expansion of the permanent along the last row
The permanent analogue of Laplace expansion, without signs. Indexing is
checked in `experiments/grenet_split.py`. A candidate for mathlib itself. -/
theorem permanent_expand_last_row {A : Type*} [CommRing A] {n : ℕ}
    (M : Matrix (Fin (n + 1)) (Fin (n + 1)) A) :
    M.permanent = ∑ j, M (Fin.last n) j * (M.submatrix Fin.castSucc j.succAbove).permanent := by
  sorry

/-- TASK T-008 | hard | Mignon–Ressayre lower bound: dc(perm_n) ≥ n²/2 in characteristic 0
Hessian rank argument. Research-grade formalization; expect to split this
into sub-tasks first. Source: Mignon–Ressayre 2004. -/
theorem sq_le_two_mul_detComplexity_perm (K : Type*) [Field K] [CharZero K] (n : ℕ) :
    n ^ 2 ≤ 2 * detComplexity (perm K n) := by
  sorry

end DetComplexity
