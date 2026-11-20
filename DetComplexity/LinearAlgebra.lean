/-
# General linear algebra

Facts about matrices, determinants and permanents that do not mention
determinantal complexity. Candidates for mathlib itself.
-/
import Mathlib

open Matrix

namespace DetComplexity

/-- If every nonzero entry `N i j` has `r i < r j`, then `det (1 - N) = 1`. -/
theorem det_one_sub_of_rank_lt {A : Type*} [CommRing A] {ι : Type*} [Fintype ι] [DecidableEq ι]
    (N : Matrix ι ι A) (r : ι → ℕ) (h : ∀ i j, N i j ≠ 0 → r i < r j) :
    (1 - N).det = 1 := by
  have hN : ∀ i j, r j ≤ r i → N i j = 0 := fun i j hij => by
    by_contra hne
    exact absurd (h i j hne) (not_lt.mpr hij)
  have hbt : (1 - N).BlockTriangular r := fun i j hij => by
    have hne : i ≠ j := by rintro rfl; exact lt_irrefl _ hij
    simp [hN i j hij.le, hne]
  rw [hbt.det]
  refine Finset.prod_eq_one fun a _ => ?_
  have h1 : (1 - N).toSquareBlock r a = 1 := by
    ext ⟨i, hi⟩ ⟨j, hj⟩
    simp [toSquareBlock_def, hN i j (by rw [hi, hj]), Matrix.one_apply]
  rw [h1, det_one]

end DetComplexity
