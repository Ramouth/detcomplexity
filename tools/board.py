#!/usr/bin/env python3
"""Generate the scoreboard block in README.md from the code, so it cannot drift from the proofs.

Sources of truth:
  * Lean: every constant the project adds to the environment, as listed by Lean
    itself (not parsed from source text or from compiler output), with the
    axioms it depends on. A theorem is "proved" iff it does not depend on sorryAx.
  * data/certificates/: explicit matrices, re-verified on every run.
  * data/literature.json: known results not verified here; shown as such.

Rules enforced (exit 1 on violation):
  * nothing outside DetComplexity/Open/ depends on sorry;
  * no constant is an axiom, is opaque, or uses a non-standard axiom;
  * a theorem inside DetComplexity/Open/ must still be open (if you proved it, move it out);
  * no existing statement or definition may change or disappear, compared with
    statements.lock at $STATEMENT_BASE (default HEAD), unless ALLOW_STATEMENT_CHANGE=1.
    The lock holds the readable statement and a hash of the fully elaborated
    term, so a change hidden from the pretty-printer (a local instance, an
    implicit argument, a numeral type) is still a change;
  * literature bounds must not contradict verified ones.
Usage: tools/board.py          regenerate the README block and statements.lock
       tools/board.py --check  write nothing; fail if either file is stale (CI)
"""
import hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import verify_data

STANDARD = {"propext", "Classical.choice", "Quot.sound"}
NMAX = 5

# Which Lean theorems give which bounds on dc(perm_n). A bound is registered
# here when its task is stated (a reviewed Statement PR), never by the proof PR.
LEAN_LOWER = [("n_le_detComplexity_perm'", lambda n: n),
              ("sq_le_two_mul_detComplexity_perm", lambda n: -(-n * n // 2))]
LEAN_UPPER = [("detComplexity_perm_le", lambda n: 2 ** n - 1),
              ("detComplexity_perm_two", lambda n: 2 if n == 2 else None)]

QUERY = r"""
import DetComplexity
open DetComplexity
open Lean Elab Command Meta in
run_cmd do
  let env ← getEnv
  let mut out := ""
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
    let (val, rawVal) ← match ci with
      | .defnInfo d => do pure (((← liftTermElabM (ppExpr d.value)).pretty 1000000), toString d.value)
      | _ => pure ("", "")
    let j := Json.mkObj [("name", toJson n.toString), ("kind", toJson kind), ("module", toJson mod.toString),
      ("axioms", toJson (axs.toList.map (·.toString))), ("hidden", toJson hidden),
      ("type", toJson (ty.pretty 1000000)), ("value", toJson val),
      ("raw", toJson (toString ci.levelParams ++ " " ++ toString ci.type ++ " := " ++ rawVal)), ("doc", toJson doc)]
    out := out ++ j.compress ++ "\n"
  IO.FS.writeFile "OUTPATH" out
"""

def declarations():
    """Every constant the project adds to the Lean environment, as reported by Lean."""
    env = dict(os.environ, PATH=f"{Path.home()}/.elan/bin:" + os.environ["PATH"])
    with tempfile.TemporaryDirectory() as tmp:
        outpath, qpath = Path(tmp) / "decls.jsonl", Path(tmp) / "query.lean"
        qpath.write_text(QUERY.replace("OUTPATH", str(outpath)))
        r = subprocess.run(["lake", "env", "lean", str(qpath)], cwd=ROOT, env=env, capture_output=True, text=True)
        if r.returncode != 0 or not outpath.exists():
            sys.exit(f"could not query the Lean environment\n{r.stdout[-800:]}{r.stderr[-400:]}")
        rows = [json.loads(line) for line in outpath.read_text().splitlines()]
    out, seen = [], set()
    for d in rows:
        if d["name"] in seen:
            sys.exit(f"duplicate constant {d['name']} in the environment listing")
        seen.add(d["name"])
        full = d["name"]
        d.update(full=full, name=full[len("DetComplexity."):] if full.startswith("DetComplexity.") else full,
                 file=d["module"].replace(".", "/") + ".lean", axioms=set(d["axioms"]),
                 type=" ".join(d["type"].split()), value=" ".join(d["value"].split()),
                 sha=hashlib.sha256(d["raw"].encode()).hexdigest()[:16], doc=d["doc"].strip(),
                 open=".Open." in d["module"] + ".")
        out.append(d)
    if not out:
        sys.exit("the Lean environment listing is empty")
    return sorted(out, key=lambda d: (d["file"], d["name"]))

def statement_changes(lock_now):
    """Compare statements and definitions with the lock file at the base commit. Fails closed."""
    base = os.environ.get("STATEMENT_BASE", "HEAD")
    r = subprocess.run(["git", "show", f"{base}:statements.lock"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        if os.environ.get("ALLOW_NO_BASE") == "1":
            print(f"LOCK: no statements.lock at {base}; comparison skipped (ALLOW_NO_BASE=1)")
            return []
        return [f"cannot read statements.lock at base '{base}' (set ALLOW_NO_BASE=1 only for a repository's first commit)"]
    old = dict(line.split(" :: ", 1) for line in r.stdout.splitlines() if " :: " in line)
    out = [f"statement or definition of {n} changed" for n in old if n in lock_now and lock_now[n] != old[n]]
    out += [f"{n} was removed" for n in old if n not in lock_now]
    return out

def scoreboard(proved, best_cert, lit, problems):
    rows = []
    for n in range(1, NMAX + 1):
        lo = max([f(n) for t, f in LEAN_LOWER if t in proved], default=None)
        up_l = min([f(n) for t, f in LEAN_UPPER if t in proved and f(n) is not None], default=None)
        lit_lo = max([e["value"] for e in lit.get("lower", []) if e.get("n") == n], default=None)
        cert = best_cert.get(n, (None, None))[0]
        ups = [u for u in (up_l, cert) if u is not None]
        best_up = min(ups) if ups else None
        if lit_lo is not None and best_up is not None and lit_lo > best_up:
            problems.append(f"literature lower bound {lit_lo} for n={n} exceeds the verified upper bound {best_up}")
        if lo is not None and up_l is not None and lo == up_l:
            status = f"**settled in Lean: {lo}**"
        elif lo is not None and best_up is not None and lo == best_up:
            status = f"settled: {lo} (lower bound in Lean, upper bound by certificate)"
        elif lit_lo is not None and best_up is not None and lit_lo == best_up:
            status = f"{best_up}, provided the literature bound holds"
        else:
            known_lo = max(x for x in (lo, lit_lo, 0) if x is not None)
            status = f"open: at least {known_lo}" + (f", at most {best_up}" if best_up is not None else ", no verified upper bound")
        cell = lambda x: "–" if x is None else str(x)
        rows.append(f"| {n} | {cell(lo)} | {cell(lit_lo)} | {cell(cert)} | {cell(up_l)} | {status} |")
    return rows

def main():
    args = set(sys.argv[1:])
    if args - {"--check"}:
        sys.exit(f"unknown argument(s): {sorted(args - {'--check'})}")
    check = "--check" in args
    decls = declarations()
    public = [d for d in decls if not d["hidden"] and d["kind"] in ("theorem", "def", "inductive", "axiom", "opaque")]
    lock_now = {d["name"]: d["type"] + (" := " + d["value"] if d["kind"] == "def" else "") + f"  [{d['sha']}]" for d in public}
    lock = "".join(f"{n} :: {lock_now[n]}\n" for n in sorted(lock_now))
    problems = []
    changes = statement_changes(lock_now)
    if changes and os.environ.get("ALLOW_STATEMENT_CHANGE") != "1":
        problems += [c + " (needs its own reviewed PR; set ALLOW_STATEMENT_CHANGE=1 there)" for c in changes]
    for d in decls:  # every constant, hidden or not
        a = d["axioms"]
        if d["kind"] in ("axiom", "opaque"):
            problems.append(f"{d['full']} ({d['file']}) is declared as {d['kind']}")
        if a - STANDARD - {"sorryAx"}:
            problems.append(f"{d['full']} ({d['file']}) uses non-standard axioms {sorted(a - STANDARD)}")
        if not d["open"] and "sorryAx" in a:
            problems.append(f"{d['full']} ({d['file']}) depends on sorry but is outside Open/")
    theorems = [d for d in public if d["kind"] == "theorem"]
    tasks = []
    for d in theorems:
        d["proved"] = "sorryAx" not in d["axioms"]
        if d["open"] and d["proved"]:
            problems.append(f"{d['name']} is proved: move it out of DetComplexity/Open/")
        if d["open"]:
            m = re.match(r"TASK (\S+) \| (\w+) \| (.*)", d["doc"])
            if m:
                tasks.append((m[1], m[2], m[3], d))
            else:
                problems.append(f"{d['name']} in Open/ lacks a 'TASK id | difficulty | title' docstring line")
    ids = [t[0] for t in tasks]
    problems += [f"task id {i} is used more than once" for i in sorted(set(ids)) if ids.count(i) > 1]
    proved = {d["name"] for d in theorems if d["proved"] and not d["open"]}
    certs_ok, best_cert = verify_data.main(quiet=True)
    if not certs_ok:
        problems.append("a certificate failed verification (run tools/verify_data.py)")
    lit = json.loads((ROOT / "data" / "literature.json").read_text())

    L = ["## Scoreboard", "",
         "Generated by `tools/board.py` from the Lean code and the data files. Never edit this block by hand.", "",
         "### dc(perm_n): how large a determinant must be to express the n×n permanent", "",
         "Over a field of characteristic 0. (In characteristic 2 the permanent is the determinant and dc(perm_n) = n.)", "",
         "| n | lower bound, Lean-proved | lower bound, literature only | upper bound, verified certificate | upper bound, Lean-proved | status |",
         "|---|---|---|---|---|---|"]
    L += scoreboard(proved, best_cert, lit, problems)
    L += ["", "Literature bounds are not verified here. Sources and hypotheses: `data/literature.json`.", "",
          "### Open tasks", "", "| id | difficulty | task | theorem | file |", "|---|---|---|---|---|"]
    for tid, diff, title, d in sorted(tasks, key=lambda t: t[0]):
        L.append(f"| {tid} | {diff} | {title} | `{d['name']}` | `{d['file']}` |")
    L += ["", f"### Proved ({len(proved)} theorems, standard axioms only)", "",
          "Names only: what each one says is in `statements.lock`, printed by Lean. Descriptions written by",
          "authors are deliberately not shown here, because the machine cannot check them.", ""]
    by_file = {}
    for d in theorems:
        if d["name"] in proved:
            by_file.setdefault(d["file"], []).append(d["name"])
    for f in sorted(by_file):
        L.append(f"- `{f}`: " + ", ".join(f"`{n}`" for n in sorted(by_file[f])))

    START, END = "<!-- BOARD:START -->", "<!-- BOARD:END -->"
    path, lock_path = ROOT / "README.md", ROOT / "statements.lock"
    readme = path.read_text()
    if START not in readme or END not in readme:
        sys.exit("README.md lacks the BOARD:START / BOARD:END markers")
    new = readme[:readme.index(START) + len(START)] + "\n" + "\n".join(L) + "\n" + readme[readme.index(END):]
    stale = new != readme or not lock_path.exists() or lock_path.read_text() != lock
    wrote = False
    if stale and not check and not problems:  # --check never writes; a failed state is never written
        path.write_text(new)
        lock_path.write_text(lock)
        wrote = True
    print(f"CERTIFICATES: {sum(1 for _ in (ROOT / 'data' / 'certificates').glob('*.json'))} verified" if certs_ok else "CERTIFICATES: FAILED")
    print(f"BOARD: {len(proved)} proved, {len(tasks)} open tasks, {len(decls)} constants checked" + (" (README.md / statements.lock updated)" if wrote else ""))
    for p in problems:
        print("PROBLEM:", p)
    if check and stale:
        print("PROBLEM: README scoreboard or statements.lock is stale; run tools/check.sh and commit the result")
    sys.exit(1 if problems or (check and stale) else 0)

if __name__ == "__main__":
    main()
