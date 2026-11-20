/-
# Determinantal complexity: definition and the degree lower bound

The *permanent versus determinant* problem (Valiant) asks how large a matrix of
affine-linear polynomials must be so that its determinant equals the n×n
permanent. That minimal size is the *determinantal complexity* `dc(p)`.

This file proves the most basic lower bound: `totalDegree p ≤ dc p`.
For the permanent that gives `dc(perm_n) ≥ n`. The best known general bound is
about n²/2, in characteristic 0 (Mignon–Ressayre 2004). Away from
characteristic 2, a superpolynomial lower bound on `dc(perm_n)` would separate
VNP from the class of polynomials with small formulas (VP_e); separating VNP
from VP itself needs slightly more, a bound beyond n^(c log n). In
characteristic 2 the permanent equals the determinant and `dc(perm_n) = n`.

Geometric Complexity Theory (Mulmuley–Sohoni) studies the limiting ("border")
version of `dc`, which is a different quantity from the one defined here.
-/
import Mathlib

open MvPolynomial Matrix

namespace DetComplexity

variable {R : Type*} [CommRing R] {σ : Type*}

/-- A square matrix whose entries are affine-linear polynomials
(total degree at most 1). -/
def IsAffineMatrix {n : Type*} (A : Matrix n n (MvPolynomial σ R)) : Prop :=
  ∀ i j, (A i j).totalDegree ≤ 1

/-- `p` has a determinantal representation of size `m`: it is the determinant
of some `m × m` matrix of affine-linear polynomials. -/
def HasDetRep (p : MvPolynomial σ R) (m : ℕ) : Prop :=
  ∃ A : Matrix (Fin m) (Fin m) (MvPolynomial σ R), IsAffineMatrix A ∧ A.det = p

/-- Determinantal complexity: the smallest size of a determinantal
representation. One always exists (`exists_hasDetRep`). Size 0 is allowed, and
the empty determinant is 1, so `dc 1 = 0`; the literature usually starts at
size 1. -/
noncomputable def detComplexity (p : MvPolynomial σ R) : ℕ :=
  sInf {m | HasDetRep p m}

/-- Key lemma: the determinant of an `n × n` affine matrix has total degree
at most `n`. Each of the `n!` terms of the Leibniz expansion is a product of
`n` entries of degree ≤ 1, up to a sign. -/
theorem totalDegree_det_le {n : Type*} [Fintype n] [DecidableEq n]
    (A : Matrix n n (MvPolynomial σ R)) (hA : IsAffineMatrix A) :
    A.det.totalDegree ≤ Fintype.card n := by
  rw [det_apply]
  refine (totalDegree_finsetSum _ _).trans (Finset.sup_le fun τ _ => ?_)
  have hprod : (∏ i, A (τ i) i).totalDegree ≤ Fintype.card n := by
    refine (totalDegree_finsetProd _ _).trans ?_
    calc ∑ i, (A (τ i) i).totalDegree
        ≤ ∑ _i : n, 1 := Finset.sum_le_sum fun i _ => hA _ _
      _ = Fintype.card n := by simp
  rcases Int.units_eq_one_or (Equiv.Perm.sign τ) with h | h
  · rw [h, one_smul]
    exact hprod
  · rw [h, Units.neg_smul, one_smul, totalDegree_neg]
    exact hprod

/-- Any determinantal representation is at least as large as the degree. -/
theorem totalDegree_le_of_hasDetRep {p : MvPolynomial σ R} {m : ℕ}
    (h : HasDetRep p m) : p.totalDegree ≤ m := by
  obtain ⟨A, hA, rfl⟩ := h
  simpa using totalDegree_det_le A hA

/-- **Degree lower bound.** If `p` has any determinantal representation,
then `totalDegree p ≤ dc p`. -/
theorem totalDegree_le_detComplexity (p : MvPolynomial σ R)
    (hp : ∃ m, HasDetRep p m) : p.totalDegree ≤ detComplexity p :=
  totalDegree_le_of_hasDetRep (Nat.sInf_mem (s := {m | HasDetRep p m}) hp)

/-- Any determinantal representation bounds `dc` from above. This is how every
upper bound on the scoreboard is proved. -/
theorem detComplexity_le_of_hasDetRep {p : MvPolynomial σ R} {m : ℕ}
    (h : HasDetRep p m) : detComplexity p ≤ m :=
  Nat.sInf_le h

end DetComplexity
