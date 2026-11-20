/-
# Open tasks: first geometric restatements

Known, routine facts about the determinant and the permanent, stated in the
form the geometric programme uses: symmetries, invariance under change of
variables, and "being a projection of the determinant". None of this is new
mathematics. The point is the form: each fact says how a polynomial sits under
a group action or inside a set of images, which is the vocabulary that orbits
and orbit closures will need.
-/
import DetComplexity.Permanent
import DetComplexity.Determinant

open MvPolynomial Matrix

namespace DetComplexity

variable {R : Type*} [CommRing R] {σ : Type*}

/-- TASK T-012 | easy | The permanent is invariant under permuting rows and columns
Symmetry of `perm` under `S_n × S_n` acting on the variables. See
`Matrix.permanent_permute_rows` and `Matrix.permanent_permute_cols`. -/
theorem rename_prodMap_perm (n : ℕ) (s t : Equiv.Perm (Fin n)) :
    rename (Prod.map s t) (perm R n) = perm R n := by
  sorry

/-- TASK T-013 | easy | The permanent is invariant under transposition
See `Matrix.permanent_transpose`. Together with T-012 this is the whole
symmetry group of the permanent that acts by permuting variables. -/
theorem rename_swap_perm (n : ℕ) : rename Prod.swap (perm R n) = perm R n := by
  sorry

/-- TASK T-014 | easy | The determinant under permuting rows and columns
The same group acts on the determinant through the sign character. The
difference between this and T-012 is the difference between the two polynomials
that the whole problem is about. See `Matrix.det_permute`. -/
theorem rename_prodMap_detPoly (n : ℕ) (s t : Equiv.Perm (Fin n)) :
    rename (Prod.map s t) (detPoly R n) =
      ((Equiv.Perm.sign s * Equiv.Perm.sign t : ℤˣ) : ℤ) • detPoly R n := by
  sorry

/-- TASK T-015 | medium | A determinantal representation is a projection of the determinant
`p` has a representation of size `m` iff `p` is the image of `detPoly R m` under
an affine substitution. This restates the definition geometrically: the set of
such `p` is the image of one polynomial under a family of maps, and
Geometric Complexity Theory studies its closure. Use `AlgHom.map_det`. -/
theorem hasDetRep_iff_projection (p : MvPolynomial σ R) (m : ℕ) :
    HasDetRep p m ↔
      ∃ f : Fin m × Fin m → MvPolynomial σ R,
        (∀ ij, (f ij).totalDegree ≤ 1) ∧ aeval f (detPoly R m) = p := by
  sorry

/-- TASK T-016 | easy | Upper bounds on dc are witnesses
`dc p ≤ m` iff a representation of size `m` exists. So every upper bound has
the shape of a missing piece: exhibit the matrix. Needs T-004 (padding) and
`hasDetRep_detComplexity`. -/
theorem detComplexity_le_iff (p : MvPolynomial σ R) (m : ℕ) :
    detComplexity p ≤ m ↔ HasDetRep p m := by
  sorry

set_option linter.deprecated false in
/-- TASK T-017 | easy | dc is constant along invertible affine changes of variables
If the substitution `f` has an affine inverse `g`, then `dc` does not change.
So `dc` is a function on orbits of the group of invertible affine substitutions:
the first statement here that is about orbits. Apply `detComplexity_bind₁_le`
in both directions. -/
theorem detComplexity_bind₁_eq (f g : σ → MvPolynomial σ R)
    (hf : ∀ i, (f i).totalDegree ≤ 1) (hg : ∀ i, (g i).totalDegree ≤ 1)
    (hgf : ∀ q : MvPolynomial σ R, bind₁ g (bind₁ f q) = q) (p : MvPolynomial σ R) :
    detComplexity (bind₁ f p) = detComplexity p := by
  sorry

end DetComplexity
