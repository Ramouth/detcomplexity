"""Small-case checks for the geometric tasks T-012 to T-015.

rename (Prod.map s t) sends the variable x[i][j] to x[s(i)][t(j)].
  T-012: the permanent is unchanged.
  T-013: the permanent is unchanged under x[i][j] -> x[j][i].
  T-014: the determinant is multiplied by sign(s) * sign(t).
  T-015: substituting affine forms into the generic determinant gives the
         determinant of the matrix of those forms (checked on random forms).
Run: python3 experiments/symmetry.py [max_n]
"""
import random, sys
from itertools import permutations
import sympy as sp
from sympy.combinatorics import Permutation

def run(n):
    x = [[sp.Symbol(f"x{i}{j}") for j in range(n)] for i in range(n)]
    X = sp.Matrix(n, n, lambda i, j: x[i][j])
    perm = lambda M: sp.expand(sum(sp.prod(M[i, s[i]] for i in range(n)) for s in permutations(range(n))))
    P, D = perm(X), sp.expand(X.det())
    ok12 = ok14 = True
    for s in permutations(range(n)):
        for t in permutations(range(n)):
            sub = {x[i][j]: x[s[i]][t[j]] for i in range(n) for j in range(n)}
            ok12 &= sp.expand(P.subs(sub, simultaneous=True)) == P
            sgn = Permutation(list(s)).signature() * Permutation(list(t)).signature()
            ok14 &= sp.expand(D.subs(sub, simultaneous=True) - sgn * D) == 0
    swap = {x[i][j]: x[j][i] for i in range(n) for j in range(n)}
    ok13 = sp.expand(P.subs(swap, simultaneous=True)) == P
    rng = random.Random(n)
    ys = sp.symbols("y0:3")
    F = sp.Matrix(n, n, lambda i, j: rng.randint(-2, 2) + sum(rng.randint(-2, 2) * y for y in ys))
    ok15 = sp.expand(D.subs({x[i][j]: F[i, j] for i in range(n) for j in range(n)}, simultaneous=True) - F.det()) == 0
    print(f"n={n}: T-012 {ok12} | T-013 {ok13} | T-014 {ok14} | T-015 {ok15}")
    return ok12 and ok13 and ok14 and ok15

if __name__ == "__main__":
    print("ALL OK" if all([run(n) for n in range(1, (int(sys.argv[1]) if len(sys.argv) > 1 else 3) + 1)]) else "FAILURE")
