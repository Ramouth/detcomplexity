#!/usr/bin/env python3
"""Verify every certificate in data/certificates/ by exact computation.

A certificate claims dc(perm_n) <= size by giving the matrix explicitly:
  {"poly": "perm", "n": 2, "size": 2, "source": "...",
   "matrix": [[{"x00": 1}, {"x01": -1}], [{"x10": 1}, {"x11": 1}]]}
Each entry is a map  variable -> integer coefficient  ("1" is the constant term),
so entries are affine by construction and no expression is ever evaluated.
Prints one line per certificate; exit 0 only if all verify.
"""
import json, re, sys
from itertools import permutations
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parent.parent
VAR = re.compile(r"^x(\d)(\d)$")

def entry(d, n):
    e = sp.Integer(0)
    for k, c in d.items():
        if not isinstance(c, int):
            raise ValueError(f"non-integer coefficient {c!r}")
        if k == "1":
            e += c
        else:
            m = VAR.match(k)
            if not m or int(m[1]) >= n or int(m[2]) >= n:
                raise ValueError(f"bad variable {k!r}")
            e += c * sp.Symbol(k)
    return e

def perm(n):
    return sum(sp.prod(sp.Symbol(f"x{i}{s[i]}") for i in range(n)) for s in permutations(range(n)))

def verify(path):
    c = json.loads(path.read_text())
    n, size, rows = c["n"], c["size"], c["matrix"]
    if c["poly"] != "perm" or len(rows) != size or any(len(r) != size for r in rows):
        raise ValueError("malformed certificate")
    A = sp.Matrix(size, size, lambda i, j: entry(rows[i][j], n))
    if sp.expand(A.det(method="berkowitz") - perm(n)) != 0:
        raise ValueError("determinant is not the permanent")
    return n, size

def main():
    ok, best = True, {}
    for path in sorted((ROOT / "data" / "certificates").glob("*.json")):
        try:
            n, size = verify(path)
            print(f"ok   {path.name}: dc(perm_{n}) <= {size}")
            if size < best.get(n, (10**9, ""))[0]:
                best[n] = (size, path.name)
        except Exception as e:  # report and fail
            ok = False
            print(f"FAIL {path.name}: {e}")
    return ok, best

if __name__ == "__main__":
    sys.exit(0 if main()[0] else 1)
