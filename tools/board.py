#!/usr/bin/env python3
"""Generate the scoreboard block in README.md from the code, so it cannot drift from the proofs.

Sources of truth:
  * Lean: every constant the project adds to the environment, as listed by Lean
    itself (not parsed from source), with the axioms it depends on
    (a theorem is "proved" iff it does not depend on sorryAx).
  * data/certificates/: explicit matrices, re-verified on every run.
  * data/literature.json: known results not yet verified here.

Rules enforced (exit 1 on violation):
  * a theorem outside DetComplexity/Open/ must be proved, on standard axioms only;
  * a theorem inside DetComplexity/Open/ must still be open (if you proved it, move it out);
  * no constant of any kind may be an axiom, be opaque, or use a non-standard axiom;
  * no existing statement or definition may change or disappear (compared with statements.lock at
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
NMAX = 5

# Which Lean theorems give which bounds on dc(perm_n). Extend when a bound is proved.
LEAN_LOWER = [("n_le_detComplexity_perm'", lambda n: n),
              ("sq_le_two_mul_detComplexity_perm", lambda n: math.ceil(n * n / 2))]
LEAN_UPPER = [("detComplexity_perm_le", lambda n: 2 ** n - 1),
              ("detComplexity_perm_two", lambda n: 2 if n == 2 else None)]

# Ask Lean itself what the project contains. Nothing here is parsed from source
# text: every constant that the project's modules add to the environment is
# listed, including private, attributed and auxiliary ones, with its axioms.
QUERY = r"""
import DetComplexity
open DetComplexity
open Lean Elab Command Meta in
run_cmd do
  let env ← getEnv
  for (n, ci) in env.constants.toList do
    let some idx := env.getModuleIdxFor? n | continue
    let mod := env.header.moduleNames[idx.toNat]!
    unless (`DetComplexity).isPrefixOf mod do continue
    let kind := match ci with
      | .thmInfo _ => "theorem" | .defnInfo _ => "def" | .axiomInfo _ => "axiom"
      | .opaqueInfo _ => "opaque" | .inductInfo _ => "inductive" | .ctorInfo _ => "ctor"
      | .recInfo _ => "rec" | .quotInfo _ => "quot"
    let axs ← collectAxioms n
    let hidden := n.isInternalDetail || (privateToUserName? n).isSome
    let doc := ((← findDocString? env n).getD "").splitOn "\n" |>.head!
    let ty ← liftTermElabM (ppExpr ci.type)
    let val ← match ci with
      | .defnInfo d => do pure ((← liftTermElabM (ppExpr d.value)).pretty 1000000)
      | _ => pure ""
    logInfo m!"DECL¦{n}¦{kind}¦{mod}¦{axs.toList}¦{hidden}¦{ty.pretty 1000000}¦{val}¦{doc}¦END"
"""

def declarations():
    """Every constant the project adds to the Lean environment, as reported by Lean."""
    env = dict(os.environ, PATH=f"{Path.home()}/.elan/bin:" + os.environ["PATH"])
    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False) as t:
        t.write(QUERY)
    r = subprocess.run(["lake", "env", "lean", t.name], cwd=ROOT, env=env, capture_output=True, text=True)
    os.unlink(t.name)
    out = []
    for m in re.finditer(r"DECL¦(.*?)¦(\w+)¦(.*?)¦\[(.*?)\]¦(true|false)¦(.*?)¦(.*?)¦(.*?)¦END", r.stdout, re.S):
        full, kind, mod, axs, hidden, ty, val, doc = m.groups()
        out.append(dict(full=full, name=full[len("DetComplexity."):] if full.startswith("DetComplexity.") else full,
                        kind=kind, module=mod, file=mod.replace(".", "/") + ".lean",
                        axioms=set(a.strip() for a in axs.split(",") if a.strip()), hidden=hidden == "true",
                        type=" ".join(ty.split()), value=" ".join(val.split()), doc=doc.strip(),
                        open=".Open." in mod + "."))
    if r.returncode != 0 or not out:
        sys.exit(f"could not query the Lean environment\n{r.stdout[-800:]}{r.stderr[-400:]}")
    return sorted(out, key=lambda d: (d["file"], d["name"]))

def statement_changes(types):
    """Compare statements with the lock file at the base commit."""
    base = os.environ.get("STATEMENT_BASE", "HEAD")
    r = subprocess.run(["git", "show", f"{base}:statements.lock"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"LOCK: no statements.lock at {base}; comparison skipped")
        return []
    old = dict(line.split(" :: ", 1) for line in r.stdout.splitlines() if " :: " in line)
    out = [f"statement of {n} changed" for n in old if n in types and types[n] != old[n]]
    out += [f"statement {n} was removed" for n in old if n not in types]
    return out

def main():
    check = "--check" in sys.argv
    decls = declarations()
    public = [d for d in decls if not d["hidden"] and d["kind"] in ("theorem", "def", "inductive", "axiom", "opaque")]
    types = {d["name"]: d["type"] + (" := " + d["value"] if d["kind"] == "def" else "") for d in public}
    lock = "".join(f"{n} :: {types[n]}\n" for n in sorted(types))
    lock_path = ROOT / "statements.lock"
    lock_stale = not lock_path.exists() or lock_path.read_text() != lock
    problems = []
    changes = statement_changes(types)
    if changes and os.environ.get("ALLOW_STATEMENT_CHANGE") != "1":
        problems += [c + " (statement and definition changes need their own reviewed PR; set ALLOW_STATEMENT_CHANGE=1 there)" for c in changes]
    for d in decls:  # every constant, hidden or not
        a = d["axioms"]
        if d["kind"] in ("axiom", "opaque"):
            problems.append(f"{d['full']} ({d['file']}) is declared as {d['kind']}")
        if a - STANDARD - {"sorryAx"}:
            problems.append(f"{d['full']} ({d['file']}) uses non-standard axioms {sorted(a - STANDARD)}")
        if not d["open"] and "sorryAx" in a:
            problems.append(f"{d['full']} ({d['file']}) depends on sorry but is outside Open/")
    theorems = [d for d in public if d["kind"] == "theorem"]
    for d in theorems:
        d["proved"] = "sorryAx" not in d["axioms"]
        if d["open"] and d["proved"]:
            problems.append(f"{d['name']} is proved: move it out of DetComplexity/Open/")
    decls = theorems
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
            m = re.match(r"TASK (\S+) \| (\w+) \| (.*)", d["doc"])
            if not m:
                problems.append(f"{d['name']} in Open/ lacks a 'TASK id | difficulty | title' docstring line")
                continue
            tasks.append((m[1], m[2], m[3], d))
    for tid, diff, title, d in sorted(tasks):
        L.append(f"| {tid} | {diff} | {title} | `{d['name']}` | `{d['file']}` |")
    L += ["", f"### Proved ({len(proved)} theorems, standard axioms only)", ""]
    L += ["Names only: what each one says is in `statements.lock`, printed by Lean. Descriptions written by",
          "authors are deliberately not shown here, because the machine cannot check them.", ""]
    by_file = {}
    for d in decls:
        if d["name"] in proved:
            by_file.setdefault(d["file"], []).append(d["name"])
    for f in sorted(by_file):
        L.append(f"- `{f}`: " + ", ".join(f"`{n}`" for n in sorted(by_file[f])))
    START, END = "<!-- BOARD:START -->", "<!-- BOARD:END -->"
    path = ROOT / "README.md"
    readme = path.read_text()
    if START not in readme or END not in readme:
        sys.exit("README.md lacks the BOARD:START / BOARD:END markers")
    new = readme[:readme.index(START) + len(START)] + "\n" + "\n".join(L) + "\n" + readme[readme.index(END):]
    stale = new != readme or lock_stale
    if not problems:  # never overwrite the lock or the board with a state that failed
        path.write_text(new)
        lock_path.write_text(lock)
    print(f"BOARD: {len(proved)} proved, {len(tasks)} open tasks" + (" (README.md / statements.lock updated)" if stale and not problems else ""))
    for p in problems:
        print("PROBLEM:", p)
    if check and stale:
        print("PROBLEM: README scoreboard or statements.lock was stale; run tools/check.sh and commit the result")
    sys.exit(1 if problems or (check and stale) else 0)

if __name__ == "__main__":
    main()
