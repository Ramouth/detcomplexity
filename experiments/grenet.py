"""Executable spec for Tier 2b (Grenet 2011): dc(perm_n) <= 2^n - 1.

Vertices: subsets S of {0..n-1}, with the empty set and the full set identified.
Edge S -> S + {j} (j not in S) has weight x[|S|][j].  Every other vertex gets a
loop of weight 1.  The matrix is the weighted adjacency matrix; cycle covers are
one cycle through the merged vertex (a path empty -> full, i.e. a permutation)
plus loops, so det = (-1)^(n-1) * perm.  The sign is fixed by negating the
row of the merged vertex when n is even.
Run: python3 experiments/grenet.py [max_n]
"""
import sys
from itertools import combinations, permutations
import sympy as sp

def grenet(n):
    x = [[sp.Symbol(f"x{i}{j}") for j in range(n)] for i in range(n)]
    full = frozenset(range(n))
    subsets = [frozenset(c) for k in range(n) for c in combinations(range(n), k)]  # proper subsets, empty first
    idx = {S: i for i, S in enumerate(subsets)}
    idx[full] = 0  # identify full set with empty set
    N = len(subsets)
    A = sp.zeros(N, N)
    for S in subsets:
        for j in range(n):
            if j not in S:
                A[idx[S], idx[S | {j}]] += x[len(S)][j]
    for i in range(1, N):
        A[i, i] += 1
    if n % 2 == 0:
        A[0, :] = -A[0, :]
    perm = sum(sp.prod(x[i][s[i]] for i in range(n)) for s in permutations(range(n)))
    return A, sp.expand(perm), x

if __name__ == "__main__":
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    for n in range(1, max_n + 1):
        A, perm, x = grenet(n)
        flat = [v for row in x for v in row]
        affine = all(sp.Poly(e, *flat).total_degree() <= 1 for e in A)
        ok = sp.expand(A.det(method='berkowitz') - perm) == 0
        print(f"n={n} size={A.rows} (2^n-1={2**n-1}) affine={affine} det==perm: {ok}")
