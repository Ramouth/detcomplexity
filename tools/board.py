#!/usr/bin/env python3
"""Generate the scoreboard block in README.md from the code, so it cannot drift from the proofs.

Sources of truth:
  * Lean: every theorem in DetComplexity/ and the axioms it depends on
    (a theorem is "proved" iff it does not depend on sorryAx).
  * data/certificates/: explicit matrices, re-verified on every run.
  * data/literature.json: known results not yet verified here.

Rules enforced (exit 1 on violation):
  * a theorem outside DetComplexity/Open/ must be proved, on standard axioms only;
  * a theorem inside DetComplexity/Open/ must still be open (if you proved it, move it out);
  * no existing statement may change or disappear (compared with statements.lock at
    $STATEMENT_BASE, default HEAD) unless ALLOW_STATEMENT_CHANGE=1.
Usage: tools/board.py          regenerate the README block and statements.lock
       tools/board.py --check  also fail if either was stale (CI)
"""
import json, math, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import verify_data

STANDARD = {"propext", "Classical.choice", "Quot.sound"}
DECL = re.compile(r"(?:/--(?P<doc>(?:(?!-/).)*?)-/\s*)?^(?:theorem|lemma) (?P<name>[A-Za-z_0-9'.₀-₉]+)(?= *$| +[\[({:])", re.S | re.M)
NMAX = 5

# Which Lean theorems give which bounds on dc(perm_n). Extend when a bound is proved.
LEAN_LOWER = [("n_le_detComplexity_perm'", lambda n: n),
              ("sq_le_two_mul_detComplexity_perm", lambda n: math.ceil(n * n / 2))]
LEAN_UPPER = [("detComplexity_perm_le", lambda n: 2 ** n - 1),
              ("detComplexity_perm_two", lambda n: 2 if n == 2 else None)]

def declarations():
    out = []
    for f in sorted((ROOT / "DetComplexity").rglob("*.lean")):
        for m in DECL.finditer(f.read_text()):
            out.append(dict(name=m["name"], doc=(m["doc"] or "").strip(), file=str(f.relative_to(ROOT)),
                            open="Open" in f.relative_to(ROOT).parts))
    return out

def axioms(names):
    env = dict(os.environ, PATH=f"{Path.home()}/.elan/bin:" + os.environ["PATH"])
    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False) as t:
        t.write("import DetComplexity\nopen DetComplexity\n" + "".join(f"#print axioms {n}\n" for n in names))
        t.write("open Lean Elab Command in\nrun_cmd do\n  for n in [" + ", ".join(f"`DetComplexity.{n}" for n in names) + "] do\n"
                "    let ci ← getConstInfo n\n    let fmt ← liftTermElabM (Meta.ppExpr ci.type)\n"
                "    logInfo m!\"LOCK|{n}|{fmt.pretty 1000000}\"\n")
    r = subprocess.run(["lake", "env", "lean", t.name], cwd=ROOT, env=env, capture_output=True, text=True)
    os.unlink(t.name)
    res = {}
    for m in re.finditer(r"'DetComplexity\.(\S+)' (does not depend on any axioms|depends on axioms: \[([^\]]*)\])", r.stdout):
        res[m[1]] = set(a.strip() for a in (m[3] or "").split(",") if a.strip())
    types = {m[1]: " ".join(m[2].split()) for m in re.finditer(r"LOCK\|DetComplexity\.(\S+?)\|(.*)", r.stdout)}
    missing = [n for n in names if n not in res or n not in types]
    if missing:
        sys.exit(f"could not read axioms/statements for {missing}\n{r.stdout[-800:]}{r.stderr[-400:]}")
    return res, types

def statement_changes(types):
    """Compare statements with the lock file at the base commit."""
    base = os.environ.get("STATEMENT_BASE", "HEAD")
    r = subprocess.run(["git", "show", f"{base}:statements.lock"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        return []
    old = dict(line.split(" :: ", 1) for line in r.stdout.splitlines() if " :: " in line)
    out = [f"statement of {n} changed" for n in old if n in types and types[n] != old[n]]
    out += [f"statement {n} was removed" for n in old if n not in types]
    return out

def main():
    check = "--check" in sys.argv
    decls = declarations()
    ax, types = axioms([d["name"] for d in decls])
    lock = "".join(f"{n} :: {types[n]}\n" for n in sorted(types))
    lock_path = ROOT / "statements.lock"
    lock_stale = not lock_path.exists() or lock_path.read_text() != lock
    changes = statement_changes(types)
    lock_path.write_text(lock)
    problems = []
    if changes and os.environ.get("ALLOW_STATEMENT_CHANGE") != "1":
        problems += [c + " (statement changes need their own reviewed PR; set ALLOW_STATEMENT_CHANGE=1 there)" for c in changes]
    for d in decls:
        a = ax[d["name"]]
        d["proved"] = "sorryAx" not in a
        if not d["open"] and not d["proved"]:
            problems.append(f"{d['name']} ({d['file']}) depends on sorry but is outside Open/")
        if not d["open"] and a - STANDARD - {"sorryAx"}:
            problems.append(f"{d['name']} uses non-standard axioms {sorted(a - STANDARD)}")
        if d["open"] and d["proved"]:
            problems.append(f"{d['name']} is proved: move it out of DetComplexity/Open/")
    proved = {d["name"] for d in decls if d["proved"] and not d["open"]}
    certs_ok, best_cert = verify_data.main()
    if not certs_ok:
        problems.append("a certificate failed verification")
    lit = json.loads((ROOT / "data" / "literature.json").read_text())

    L = ["## Scoreboard", "",
         "Generated by `tools/board.py` from the Lean code and the data files. Never edit this block by hand.", "",
         "### dc(perm_n): how large a determinant must be to express the n×n permanent", "",
         "| n | lower bound, Lean-proved | lower bound, literature only | upper bound, verified certificate | upper bound, Lean-proved | status |",
         "|---|---|---|---|---|---|"]
    for n in range(1, NMAX + 1):
        lo = max([f(n) for t, f in LEAN_LOWER if t in proved], default=None)
        up_l = min([f(n) for t, f in LEAN_UPPER if t in proved and f(n) is not None], default=None)
        lit_lo = max([e["value"] for e in lit["lower"] if e["n"] == n] + [math.ceil(n * n / 2)])
        cert = best_cert.get(n, (None, None))[0]
        ups = [u for u in (up_l, cert) if u is not None]
        if lo is not None and up_l is not None and lo == up_l:
            status = f"**settled in Lean: {lo}**"
        elif ups and max(lo or 0, lit_lo) == min(ups):
            status = f"known to be {min(ups)}, not fully formal"
        else:
            status = f"open: between {max(lo or 0, lit_lo)} and {min(ups) if ups else 2 ** n - 1}"
        L.append(f"| {n} | {lo if lo is not None else '–'} | {lit_lo} | {cert if cert is not None else '–'} | {up_l if up_l is not None else '–'} | {status} |")
    L += ["", "Literature bounds are not verified here and assume a field of characteristic 0 "
          "(in characteristic 2 the permanent is the determinant and dc(perm_n) = n). "
          "Sources and hypotheses: `data/literature.json`.", "",
          "### Open tasks", "", "Claim one by opening an issue or draft PR named after its id. See `CONTRIBUTING.md`.", "",
          "| id | difficulty | task | theorem | file |", "|---|---|---|---|---|"]
    tasks = []
    for d in decls:
        if d["open"]:
            m = re.match(r"TASK (\S+) \| (\w+) \| (.*)", d["doc"].splitlines()[0] if d["doc"] else "")
            if not m:
                problems.append(f"{d['name']} in Open/ lacks a 'TASK id | difficulty | title' docstring line")
                continue
            tasks.append((m[1], m[2], m[3], d))
    for tid, diff, title, d in sorted(tasks):
        L.append(f"| {tid} | {diff} | {title} | `{d['name']}` | `{d['file']}` |")
    L += ["", f"### Proved ({len(proved)} theorems, standard axioms only)", ""]
    for d in decls:
        if d["name"] in proved:
            first = d["doc"].splitlines()[0].strip() if d["doc"] else ""
            L.append(f"- `{d['name']}` ({d['file']}){': ' + first if first else ''}")
    START, END = "<!-- BOARD:START -->", "<!-- BOARD:END -->"
    path = ROOT / "README.md"
    readme = path.read_text()
    if START not in readme or END not in readme:
        sys.exit("README.md lacks the BOARD:START / BOARD:END markers")
    new = readme[:readme.index(START) + len(START)] + "\n" + "\n".join(L) + "\n" + readme[readme.index(END):]
    stale = new != readme or lock_stale
    path.write_text(new)
    print(f"BOARD: {len(proved)} proved, {len(tasks)} open tasks" + (" (README.md / statements.lock updated)" if stale else ""))
    for p in problems:
        print("PROBLEM:", p)
    if check and stale:
        print("PROBLEM: README scoreboard or statements.lock was stale; run tools/check.sh and commit the result")
    sys.exit(1 if problems or (check and stale) else 0)

if __name__ == "__main__":
    main()
