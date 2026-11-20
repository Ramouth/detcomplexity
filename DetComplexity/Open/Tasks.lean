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

/-- TASK T-006 | medium | dc does not increase under affine substitution
Substitute into every matrix entry; an affine polynomial of affine polynomials
is affine. This is what makes dc a measure of *projections*. -/
theorem detComplexity_bind₁_le (f : σ → MvPolynomial τ R) (hf : ∀ i, (f i).totalDegree ≤ 1)
    (p : MvPolynomial σ R) : detComplexity (bind₁ f p) ≤ detComplexity p := by
  sorry

/-- TASK T-007 | hard | Grenet's upper bound: dc(perm_n) ≤ 2^n - 1
Construction and sign convention are executable in `experiments/grenet.py`
(verified for n ≤ 4). Source: Grenet 2011. -/
theorem detComplexity_perm_le (n : ℕ) : detComplexity (perm R n) ≤ 2 ^ n - 1 := by
  sorry

/-- TASK T-008 | hard | Mignon–Ressayre lower bound: dc(perm_n) ≥ n²/2 in characteristic 0
Hessian rank argument. Research-grade formalization; expect to split this
into sub-tasks first. Source: Mignon–Ressayre 2004. -/
theorem sq_le_two_mul_detComplexity_perm (K : Type*) [Field K] [CharZero K] (n : ℕ) :
    n ^ 2 ≤ 2 * detComplexity (perm K n) := by
  sorry

end DetComplexity
