/-
# The generic determinant

`detPoly R m` is the determinant of the `m × m` matrix of independent variables.
Geometrically it is the central object: a polynomial `p` has a determinantal
representation of size `m` exactly when `p` is the image of `detPoly R m` under
an affine substitution (task T-015). Geometric Complexity Theory studies the
closure of that set of images.
-/
import DetComplexity.Basic

open MvPolynomial Matrix

namespace DetComplexity

/-- The `m × m` determinant as a polynomial in the `m²` variables `X (i, j)`. -/
noncomputable def detPoly (R : Type*) [CommRing R] (m : ℕ) : MvPolynomial (Fin m × Fin m) R :=
  (Matrix.of fun i j => X (i, j)).det

end DetComplexity
