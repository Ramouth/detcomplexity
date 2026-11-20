#!/usr/bin/env python3
"""Verify every certificate in data/certificates/ by exact computation.

A certificate claims dc(perm_n) <= size by giving the matrix explicitly:
  {"poly": "perm", "n": 2, "size": 2, "source": "...",
   "matrix": [[{"x00": 1}, {"x01": -1}], [{"x10": 1}, {"x11": 1}]]}
Each entry is a map  variable -> integer coefficient  ("1" is the constant term),
so entries are affine by construction and no expression is ever evaluated.

Limits, so that a small file cannot stall the referee: 1 <= n <= MAX_N,
size <= MAX_SIZE, coefficients below 10^6 in absolute value, TIMEOUT seconds per
file. The determinant is first compared with the permanent at random integer
points (cheap, rejects almost every wrong matrix), then expanded exactly.
Prints one line per certificate; exit 0 only if all verify.
"""
import json, random, re, signal, sys
from itertools import permutations
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parent.parent
VAR = re.compile(r"^x(\d)(\d)$")
NAME = re.compile(r"^[A-Za-z0-9_.-]+\.json$")
MAX_N, MAX_SIZE, MAX_COEFF, TIMEOUT = 6, 64, 10 ** 6, 300

def strict_int(v, what):
    if type(v) is not int:
        raise ValueError(f"{what} must be an integer, got {v!r}")
    return v

def entry(d, n):
    if type(d) is not dict:
        raise ValueError("matrix entry must be an object")
    e = sp.Integer(0)
    for k, c in d.items():
        if abs(strict_int(c, "coefficient")) >= MAX_COEFF:
            raise ValueError("coefficient too large")
        if k == "1":
            e += c
        else:
            m = VAR.match(k)
            if not m or int(m[1]) >= n or int(m[2]) >= n:
                raise ValueError(f"bad variable {k!r}")
            e += c * sp.Symbol(k)
    return e

def perm_value(n, val):
    return sum(sp.prod(val[i][s[i]] for i in range(n)) for s in permutations(range(n)))

def verify(path):
    if not NAME.match(path.name) or path.is_symlink():
        raise ValueError("file name must match [A-Za-z0-9_.-]+.json and not be a link")
    c = json.loads(path.read_text())
    if type(c) is not dict or c.get("poly") != "perm":
        raise ValueError("malformed certificate")
    n, size, rows = strict_int(c.get("n"), "n"), strict_int(c.get("size"), "size"), c.get("matrix")
    if not 1 <= n <= MAX_N or not 0 <= size <= MAX_SIZE:
        raise ValueError(f"n must be 1..{MAX_N} and size 0..{MAX_SIZE}")
    if type(rows) is not list or len(rows) != size or any(type(r) is not list or len(r) != size for r in rows):
        raise ValueError("matrix must be size x size")
    A = sp.Matrix(size, size, lambda i, j: entry(rows[i][j], n))
    xs = [[sp.Symbol(f"x{i}{j}") for j in range(n)] for i in range(n)]
    rng = random.Random(0)
    for _ in range(3):  # cheap pretest at integer points
        val = [[rng.randint(-9, 9) for _ in range(n)] for _ in range(n)]
        sub = {xs[i][j]: val[i][j] for i in range(n) for j in range(n)}
        if A.subs(sub).det() != perm_value(n, val):
            raise ValueError("determinant is not the permanent (differs at an integer point)")
    if sp.expand(A.det(method="berkowitz") - perm_value(n, xs)) != 0:
        raise ValueError("determinant is not the permanent")
    return n, size

def _alarm(signum, frame):
    raise TimeoutError(f"exceeded {TIMEOUT} s")

def main(quiet=False):
    ok, best = True, {}
    signal.signal(signal.SIGALRM, _alarm)
    for path in sorted((ROOT / "data" / "certificates").iterdir()):
        if path.suffix != ".json":
            ok = False
            print(f"FAIL {path.name!r}: only .json files belong in data/certificates/")
            continue
        try:
            signal.alarm(TIMEOUT)
            n, size = verify(path)
            signal.alarm(0)
            if not quiet:
                print(f"ok   {path.name}: dc(perm_{n}) <= {size}", flush=True)
            if size < best.get(n, (10 ** 9, ""))[0]:
                best[n] = (size, path.name)
        except Exception as e:  # report and fail
            signal.alarm(0)
            ok = False
            print(f"FAIL {path.name!r}: {type(e).__name__}: {e}", flush=True)
    return ok, best

if __name__ == "__main__":
    sys.exit(0 if main()[0] else 1)
