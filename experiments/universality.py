"""Executable spec for `exists_hasDetRep` (every polynomial is a determinant), checked before formalizing.

Invariant W(p): there are T (k x k), S with T*S = I, det T = 1, vectors v, w and
a scalar c, all of T, v, w, c affine-linear, with  p = c - w . (S v).
Then p = det [[T, v], [w, c]], an affine matrix of size k+1.

Closure rules (exactly the three cases of MvPolynomial.induction_on):
  const a : k = 0, c = a
  p + q   : T = diag(T1,T2), S = diag(S1,S2), v = v1++v2, w = w1++w2, c = c1+c2
  p * x   : T' = [[T, v],[0, 1]], S' = [[S, -S v],[0, 1]], v' = (0, -x), w' = (w, c), c' = 0
Run: python3 experiments/universality.py
"""
import random
import sympy as sp

def const(a):
    return dict(T=sp.zeros(0, 0), S=sp.zeros(0, 0), v=sp.zeros(0, 1), w=sp.zeros(1, 0), c=sp.Integer(a))

def add(P, Q):
    return dict(T=sp.diag(P['T'], Q['T']), S=sp.diag(P['S'], Q['S']),
                v=P['v'].col_join(Q['v']), w=P['w'].row_join(Q['w']), c=P['c'] + Q['c'])

def mulx(P, x):
    k = P['T'].rows
    T = P['T'].row_join(P['v']).col_join(sp.zeros(1, k).row_join(sp.ones(1, 1)))
    S = P['S'].row_join(-P['S'] * P['v']).col_join(sp.zeros(1, k).row_join(sp.ones(1, 1)))
    v = sp.zeros(k, 1).col_join(sp.Matrix([[-x]]))
    w = P['w'].row_join(sp.Matrix([[P['c']]]))
    return dict(T=T, S=S, v=v, w=w, c=sp.Integer(0))

def build(p, xs):
    """Follow induction_on: p = sum over monomials of coeff * x^e."""
    acc = const(0)
    for exps, coeff in sp.Poly(p, *xs).terms():
        m = const(coeff)
        for x, e in zip(xs, exps):
            for _ in range(e):
                m = mulx(m, x)
        acc = add(acc, m)
    return acc

def check(P, p, xs):
    k = P['T'].rows
    M = P['T'].row_join(P['v']).col_join(P['w'].row_join(sp.Matrix([[P['c']]])))
    affine = all(sp.Poly(e, *xs).total_degree() <= 1 for e in M)
    ok_inv = sp.simplify(P['T'] * P['S'] - sp.eye(k)) == sp.zeros(k, k)
    ok_detT = sp.expand(P['T'].det()) == 1
    ok_det = sp.expand(M.det() - p) == 0
    return affine and ok_inv and ok_detT and ok_det, k + 1

if __name__ == "__main__":
    random.seed(0)
    xs = sp.symbols('x0:3')
    allok = True
    for trial in range(12):
        p = sum(random.randint(-3, 3) * sp.prod([x ** random.randint(0, 2) for x in xs]) for _ in range(random.randint(0, 4)))
        p = sp.expand(p)
        ok, size = check(build(p, xs), p, xs)
        allok &= ok
        print(f"{'ok ' if ok else 'BAD'} size={size:2d} deg={sp.Poly(p, *xs).total_degree() if p != 0 else 0}  p={p}")
    print("ALL OK" if allok else "FAILURE")
