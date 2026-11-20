/-
# The permanent (Tier 1 target: contains `sorry` to be filled)
-/
import DetComplexity.Basic

open MvPolynomial Matrix

namespace DetComplexity

variable (R : Type*) [CommRing R]

/-- The `n × n` permanent as a polynomial in the `n²` variables `X (i, j)`. -/
noncomputable def perm (n : ℕ) : MvPolynomial (Fin n × Fin n) R :=
  (Matrix.of fun i j => X (i, j)).permanent

/-- TODO (Tier 1): the permanent has total degree exactly `n`.
Hint: `≤` as in `totalDegree_det_le`; `≥` because the diagonal monomial
`∏ i, X (i, i)` has coefficient 1 (only the identity permutation produces it). -/
theorem totalDegree_perm [Nontrivial R] (n : ℕ) : (perm R n).totalDegree = n := by
  sorry

/-- `dc(perm_n) ≥ n`. Once `totalDegree_perm` is proved this is sorry-free. -/
theorem n_le_detComplexity_perm [Nontrivial R] (n : ℕ)
    (h : ∃ m, HasDetRep (perm R n) m) : n ≤ detComplexity (perm R n) := by
  have := totalDegree_le_detComplexity (perm R n) h
  rwa [totalDegree_perm] at this

end DetComplexity
