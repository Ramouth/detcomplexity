/-
# Universality: every polynomial has a determinantal representation

This removes the `∃ m, HasDetRep p m` hypothesis from the degree bound.
The construction is the executable spec in `experiments/universality.py`.

Invariant (`HasSchurRep`): `p = c - w ⬝ᵥ (S *ᵥ v)` where `T * S = 1`, `det T = 1`
and `T`, `v`, `w`, `c` are affine. Then `p = det [[T, v], [w, c]]`.
The invariant is closed under constants, sums and multiplication by a variable,
which are exactly the cases of `MvPolynomial.induction_on`.
-/
import DetComplexity.Basic

open MvPolynomial Matrix

namespace DetComplexity

variable {R : Type*} [CommRing R] {σ : Type*}

/-- A determinantal representation indexed by any finite type gives one of
size `Fintype.card`. -/
theorem hasDetRep_of_matrix {ι : Type*} [Fintype ι] [DecidableEq ι]
    (A : Matrix ι ι (MvPolynomial σ R)) (hA : IsAffineMatrix A) :
    HasDetRep A.det (Fintype.card ι) :=
  ⟨A.submatrix (Fintype.equivFin ι).symm (Fintype.equivFin ι).symm, fun _ _ => hA _ _,
    det_submatrix_equiv_self _ _⟩

/-- The bordered ("Schur complement") normal form used for the induction. -/
def HasSchurRep (p : MvPolynomial σ R) : Prop :=
  ∃ (ι : Type) (_ : Fintype ι) (_ : DecidableEq ι)
    (T S : Matrix ι ι (MvPolynomial σ R)) (v w : ι → MvPolynomial σ R) (c : MvPolynomial σ R),
    T * S = 1 ∧ T.det = 1 ∧ (∀ i j, (T i j).totalDegree ≤ 1) ∧ (∀ i, (v i).totalDegree ≤ 1) ∧
    (∀ i, (w i).totalDegree ≤ 1) ∧ c.totalDegree ≤ 1 ∧ p = c - w ⬝ᵥ (S *ᵥ v)

theorem hasSchurRep_C (a : R) : HasSchurRep (C a : MvPolynomial σ R) :=
  ⟨Empty, inferInstance, inferInstance, 1, 1, 0, 0, C a, by simp, by simp,
    fun i => i.elim, fun i => i.elim, fun i => i.elim, by simp, by simp⟩

theorem HasSchurRep.add {p q : MvPolynomial σ R} (hp : HasSchurRep p) (hq : HasSchurRep q) :
    HasSchurRep (p + q) := by
  obtain ⟨ι₁, _, _, T₁, S₁, v₁, w₁, c₁, hTS₁, hdet₁, hT₁, hv₁, hw₁, hc₁, rfl⟩ := hp
  obtain ⟨ι₂, _, _, T₂, S₂, v₂, w₂, c₂, hTS₂, hdet₂, hT₂, hv₂, hw₂, hc₂, rfl⟩ := hq
  refine ⟨ι₁ ⊕ ι₂, inferInstance, inferInstance, fromBlocks T₁ 0 0 T₂, fromBlocks S₁ 0 0 S₂,
    Sum.elim v₁ v₂, Sum.elim w₁ w₂, c₁ + c₂, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · simp [fromBlocks_multiply, hTS₁, hTS₂]
  · simp [hdet₁, hdet₂]
  · rintro (i | i) (j | j) <;> simp [hT₁, hT₂]
  · rintro (i | i) <;> simp [hv₁, hv₂]
  · rintro (i | i) <;> simp [hw₁, hw₂]
  · exact (totalDegree_add _ _).trans (max_le hc₁ hc₂)
  · simp [fromBlocks_mulVec, dotProduct, Fintype.sum_sum_type]
    ring

theorem HasSchurRep.mul_X {p : MvPolynomial σ R} (hp : HasSchurRep p) (x : σ) :
    HasSchurRep (p * X x) := by
  obtain ⟨ι, _, _, T, S, v, w, c, hTS, hdet, hT, hv, hw, hc, rfl⟩ := hp
  have hTSv : T *ᵥ (S *ᵥ v) = v := by rw [mulVec_mulVec, hTS, one_mulVec]
  refine ⟨ι ⊕ Unit, inferInstance, inferInstance,
    fromBlocks T (replicateCol Unit v) 0 1,
    fromBlocks S (replicateCol Unit (-(S *ᵥ v))) 0 1,
    Sum.elim 0 (fun _ => -X x), Sum.elim w (fun _ => c), 0, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · rw [fromBlocks_multiply, hTS]
    have h0 : T * replicateCol Unit (-(S *ᵥ v)) + replicateCol Unit v = 0 := by
      apply Matrix.ext
      intro i j
      have hi := congrFun hTSv i
      simp only [mulVec, dotProduct] at hi
      simp [Matrix.mul_apply, mulVec, dotProduct, hi]
    simp [h0, fromBlocks_one]
  · simp [hdet]
  · rintro (i | i) (j | j) <;> simp [hT, hv]
  · rintro (i | i)
    · simp
    · simpa using (isHomogeneous_X R x).totalDegree_le
  · rintro (i | i) <;> simp [hw, hc]
  · simp
  · simp [dotProduct, Fintype.sum_sum_type, mulVec]
    simp only [← mul_assoc, ← Finset.sum_mul]
    ring

theorem hasSchurRep (p : MvPolynomial σ R) : HasSchurRep p := by
  induction p using MvPolynomial.induction_on with
  | C a => exact hasSchurRep_C a
  | add p q hp hq => exact hp.add hq
  | mul_X p x hp => exact hp.mul_X x

/-- **Universality.** Every polynomial is the determinant of a square matrix of
affine-linear polynomials. -/
theorem exists_hasDetRep (p : MvPolynomial σ R) : ∃ m, HasDetRep p m := by
  obtain ⟨ι, _, _, T, S, v, w, c, hTS, hdet, hT, hv, hw, hc, rfl⟩ := hasSchurRep p
  let M : Matrix (ι ⊕ Unit) (ι ⊕ Unit) (MvPolynomial σ R) :=
    fromBlocks T (replicateCol Unit v) (replicateRow Unit w) (of fun _ _ => c)
  have hM : IsAffineMatrix M := by
    rintro (i | i) (j | j) <;> simp [M, hT, hv, hw, hc]
  have hdetM : M.det = c - w ⬝ᵥ (S *ᵥ v) := by
    let _ := invertibleOfRightInverse T S hTS
    have hinv : ⅟T = S := invOf_eq_right_inv hTS
    simp only [M]
    rw [det_fromBlocks₁₁, hdet, one_mul, det_unique, hinv]
    simp [Matrix.mul_apply, dotProduct, mulVec, Finset.mul_sum]
    simp only [Finset.sum_mul, mul_assoc]
    exact Finset.sum_comm
  exact ⟨_, hdetM ▸ hasDetRep_of_matrix M hM⟩

/-- `dc p` is attained: `p` has a determinantal representation of size `dc p`. -/
theorem hasDetRep_detComplexity (p : MvPolynomial σ R) : HasDetRep p (detComplexity p) :=
  Nat.sInf_mem (s := {m | HasDetRep p m}) (exists_hasDetRep p)

/-- **Degree lower bound, unconditional.** -/
theorem totalDegree_le_detComplexity' (p : MvPolynomial σ R) :
    p.totalDegree ≤ detComplexity p :=
  totalDegree_le_detComplexity p (exists_hasDetRep p)

/-- dc is subadditive under products: `dc (p * q) ≤ dc p + dc q`, by a block-diagonal matrix. -/
theorem detComplexity_mul_le (p q : MvPolynomial σ R) :
    detComplexity (p * q) ≤ detComplexity p + detComplexity q := by
  obtain ⟨A, hA, hdA⟩ := hasDetRep_detComplexity p
  obtain ⟨B, hB, hdB⟩ := hasDetRep_detComplexity q
  have hA' : ∀ i j, (A i j).totalDegree ≤ 1 := hA
  have hB' : ∀ i j, (B i j).totalDegree ≤ 1 := hB
  have h := hasDetRep_of_matrix (fromBlocks A 0 0 B)
    (by rintro (i | i) (j | j) <;> simp [hA', hB'])
  rw [det_fromBlocks_zero₂₁, hdA, hdB] at h
  simpa using detComplexity_le_of_hasDetRep h

-- The statements below are about `bind₁`, which mathlib now deprecates in favour of `aeval`.
set_option linter.deprecated false in
/-- Substituting affine polynomials into an affine polynomial gives an affine polynomial. -/
theorem totalDegree_bind₁_le_one {τ : Type*} (f : σ → MvPolynomial τ R)
    (hf : ∀ i, (f i).totalDegree ≤ 1) (q : MvPolynomial σ R) (hq : q.totalDegree ≤ 1) :
    (bind₁ f q).totalDegree ≤ 1 := by
  rw [bind₁, aeval_def, eval₂_eq]
  refine totalDegree_finsetSum_le fun d hd => ?_
  refine (totalDegree_mul _ _).trans ?_
  rw [algebraMap_eq, totalDegree_C, zero_add]
  refine (totalDegree_finsetProd _ _).trans ?_
  refine le_trans (Finset.sum_le_sum fun i _ => (totalDegree_pow _ _).trans
    (Nat.mul_le_mul_left _ (hf i))) ?_
  simpa [Finsupp.sum] using (le_totalDegree hd).trans hq

set_option linter.deprecated false in
/-- **dc does not increase under affine substitution.** Substitute into every
matrix entry; an affine polynomial of affine polynomials is affine. This is
what makes dc a measure of *projections*. -/
theorem detComplexity_bind₁_le {τ : Type*} (f : σ → MvPolynomial τ R)
    (hf : ∀ i, (f i).totalDegree ≤ 1) (p : MvPolynomial σ R) :
    detComplexity (bind₁ f p) ≤ detComplexity p := by
  obtain ⟨A, hA, hdet⟩ := hasDetRep_detComplexity p
  refine detComplexity_le_of_hasDetRep ⟨A.map (bind₁ f), fun i j => ?_, ?_⟩
  · exact totalDegree_bind₁_le_one f hf _ (hA i j)
  · exact (AlgHom.map_det _ _).symm.trans (congrArg _ hdet)

end DetComplexity
