/-
# The permanent: `totalDegree (perm n) = n`, hence `dc(perm_n) ≥ n`
-/
import DetComplexity.Basic

open MvPolynomial Matrix

namespace DetComplexity

variable (R : Type*) [CommRing R]

/-- The `n × n` permanent as a polynomial in the `n²` variables `X (i, j)`. -/
noncomputable def perm (n : ℕ) : MvPolynomial (Fin n × Fin n) R :=
  (Matrix.of fun i j => X (i, j)).permanent

/-- The permanent has total degree exactly `n`: it is homogeneous of degree `n`
and nonzero (it evaluates to `1` at the identity matrix). -/
theorem totalDegree_perm [Nontrivial R] (n : ℕ) : (perm R n).totalDegree = n := by
  -- `perm` is homogeneous of degree `n`: a sum of products of `n` variables.
  have hhom : (perm R n).IsHomogeneous n := by
    unfold perm Matrix.permanent
    refine IsHomogeneous.sum _ _ _ fun τ _ => ?_
    have h := IsHomogeneous.prod (Finset.univ : Finset (Fin n))
      (fun i => (X (τ i, i) : MvPolynomial (Fin n × Fin n) R)) (fun _ => 1)
      (fun i _ => isHomogeneous_X R (τ i, i))
    simpa using h
  -- `perm` is nonzero: evaluated at the identity matrix it gives `1`.
  have hne : perm R n ≠ 0 := by
    intro h0
    have h1 : eval (fun ij : Fin n × Fin n => (1 : Matrix (Fin n) (Fin n) R) ij.1 ij.2)
        (perm R n) = 1 := by
      have : eval (fun ij : Fin n × Fin n => (1 : Matrix (Fin n) (Fin n) R) ij.1 ij.2)
          (perm R n) = (1 : Matrix (Fin n) (Fin n) R).permanent := by
        simp [perm, Matrix.permanent]
      rw [this, Matrix.permanent_one]
    rw [h0, map_zero] at h1
    exact zero_ne_one h1
  exact hhom.totalDegree hne

/-- `dc(perm_n) ≥ n`. -/
theorem n_le_detComplexity_perm [Nontrivial R] (n : ℕ)
    (h : ∃ m, HasDetRep (perm R n) m) : n ≤ detComplexity (perm R n) := by
  have := totalDegree_le_detComplexity (perm R n) h
  rwa [totalDegree_perm] at this

end DetComplexity
