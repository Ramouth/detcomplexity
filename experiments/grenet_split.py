"""Test a proof route for Grenet's bound that needs no cycle covers and no matrix inverse.

Index set I = nonempty proper subsets of {0..n-1}.  For a subset S let
  g(S) = sum_{j in S} g(S - {j}) * x[|S|-1][j],   g(empty) = 1
(the permanent of the first |S| rows restricted to the columns in S), so
g(full) = perm_n is Laplace expansion along the last row.
Bordered matrix [[T, v], [w, c]] of size |I| + 1 = 2^n - 1 with
  T = 1 - N,  N[S, S+{j}] = x[|S|][j]        (strictly raises |S|, so det T = 1)
  w[S] = x[0][j] if S = {j} else 0           (edges out of the empty set)
  v[S] = -x[n-1][j] if S = full - {j} else 0 (edges into the full set, negated)
  c    = x[0][0] if n == 1 else 0
Claim A: the row vector u[S] = g(S) solves  u T = w.
Claim B: c - u.v = perm_n.
A and B give det = perm_n via the Schur complement, since u = w T^{-1}.
"""
import sys
from itertools import combinations, permutations
import sympy as sp

def run(n):
    x = [[sp.Symbol(f"x{i}{j}") for j in range(n)] for i in range(n)]
    full = frozenset(range(n))
    I = [frozenset(c) for k in range(1, n) for c in combinations(range(n), k)]
    pos = {S: i for i, S in enumerate(I)}
    g = {frozenset(): sp.Integer(1)}
    for k in range(1, n + 1):
        for c in combinations(range(n), k):
            S = frozenset(c)
            g[S] = sp.expand(sum(g[S - {j}] * x[k - 1][j] for j in S))
    perm = sp.expand(sum(sp.prod(x[i][s[i]] for i in range(n)) for s in permutations(range(n))))
    m = len(I)
    N = sp.zeros(m, m)
    for S in I:
        for j in full - S:
            if S | {j} != full:
                N[pos[S], pos[S | {j}]] = x[len(S)][j]
    T = sp.eye(m) - N
    w = sp.Matrix([[x[0][next(iter(S))] if len(S) == 1 else 0 for S in I]]) if m else sp.zeros(1, 0)
    v = sp.Matrix([-x[n - 1][next(iter(full - S))] if len(S) == n - 1 else 0 for S in I]) if m else sp.zeros(0, 1)
    c = x[0][0] if n == 1 else sp.Integer(0)
    u = sp.Matrix([[g[S] for S in I]]) if m else sp.zeros(1, 0)
    A = (u * T - w).applyfunc(sp.expand) == sp.zeros(1, m)
    B = sp.expand(c - (u * v)[0, 0] if m else c) == perm
    laplace = g[full] == perm
    M = T.row_join(v).col_join(w.row_join(sp.Matrix([[c]])))
    D = sp.expand(M.det(method="berkowitz")) == perm
    print(f"n={n} size={m+1}: uT=w {A} | c-u.v=perm {B} | g(full)=perm {laplace} | det=perm {D}")
    return A and B and laplace and D

def laplace_statement(m):
    """Exact indexing of task T-011: perm M = sum_j M[last][j] * perm(M without last row and column j)."""
    M = sp.Matrix(m, m, lambda i, j: sp.Symbol(f"m{i}{j}"))
    P = lambda A: sp.expand(sum(sp.prod(A[i, s[i]] for i in range(A.rows)) for s in permutations(range(A.rows)))) if A.rows else sp.Integer(1)
    rhs = sum(M[m - 1, j] * P(M.extract(list(range(m - 1)), [k for k in range(m) if k != j])) for j in range(m))
    ok = sp.expand(P(M) - rhs) == 0
    print(f"T-011 statement, size {m}: {ok}")
    return ok

if __name__ == "__main__":
    assert all(laplace_statement(m) for m in (1, 2, 3, 4))
    print("ALL OK" if all([run(n) for n in range(1, int(sys.argv[1]) + 1 if len(sys.argv) > 1 else 5)]) else "FAILURE")
