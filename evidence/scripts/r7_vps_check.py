#!/usr/bin/env python3
"""Independent external review (RPI-RLT-VR-007). Checks the second machine's VR-007 evidence as committed.

  r7_vps_check.py [evidence dir] [repository root with formal/]

Checks, each printed as PASS or FAIL; exit 0 only when all pass:
  V1 manifest       every file named in results/R7-vps/PUBLIC-SHA256SUMS has its recorded SHA-256
  V2 coverage       the first replay pass lists every .lean module under formal/ZK60Formal (when a repository root
                    is given), once each
  V3 reconciled     every module ends `ok`: its first-pass status is ok, or it failed there and the retry pass
                    (memory-limit) or the check-module pass (not-compiled) records it ok; the retry and check lists
                    are exactly the first pass's failures of those kinds
  V4 nanoda         for each of the four top theorems: the 256 MiB run reports "Checked N declarations with no
                    typechecker errors", the control run refuses Classical.choice, and the first run with the
                    default stack recorded export exit 0
  V5 verdicts-only  each successful nanoda run reports exactly one pretty-printer diagnostic, "Unable to print axioms"
Prints the declaration counts and the replay figures used in the report.
"""
import csv, hashlib, os, re, sys
TOPS = ("real", "cb", "eb", "bnd")

def tsv(p): return {r["module"]: r for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t")}

def main():
    E = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root = sys.argv[2] if len(sys.argv) > 2 else None
    V = os.path.join(E, "results/R7-vps")
    ok = []
    def check(name, probs, detail=""):
        ok.append(not probs); print(("PASS " if not probs else "FAIL ") + name + (": " + (detail if not probs else "; ".join(probs[:5]))))
    bad = []; n = 0
    for line in open(os.path.join(V, "PUBLIC-SHA256SUMS"), encoding="utf-8"):
        if not line.strip(): continue
        h, f = line.split(None, 1); f = f.strip().lstrip("*"); n += 1
        p = os.path.join(V, f)
        if not os.path.exists(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != h: bad.append(f)
    check("V1 manifest", bad, f"{n} files")
    a = tsv(os.path.join(V, "06-replay-per-module.tsv"))
    p2 = []
    if root:
        F = os.path.join(root, "formal")
        tree = {os.path.join(r, x)[len(F) + 1:-5].replace(os.sep, ".") for r, _, fs in os.walk(os.path.join(F, "ZK60Formal")) for x in fs if x.endswith(".lean")}
        p2 += [f"absent from the replay: {m}" for m in sorted(tree - set(a))] + [f"not in the tree: {m}" for m in sorted(set(a) - tree)]
    check("V2 coverage", p2, f"{len(a)} modules" + ("" if root else " (tree not compared: no repository root given)"))
    b = tsv(os.path.join(V, "retry/06-replay-per-module.tsv")); c = tsv(os.path.join(V, "check-replay/06-replay-per-module.tsv"))
    ml = {m for m, r in a.items() if r["status"] == "memory-limit"}; nc = {m for m, r in a.items() if r["status"] == "not-compiled"}
    p3 = []
    if set(b) != ml: p3.append(f"retry list {sorted(b)} differs from the memory-limit modules {sorted(ml)}")
    if set(c) != nc: p3.append(f"check-module pass ({len(c)}) differs from the not-compiled modules ({len(nc)})")
    final = {m: (b.get(m) or c.get(m) or r)["status"] for m, r in a.items()}
    p3 += [f"{m} ends {s}" for m, s in final.items() if s != "ok"]
    check("V3 reconciled", p3, f"{sum(r['status'] == 'ok' for r in a.values())} first pass + {len(b)} retry + {len(c)} check modules = {sum(s == 'ok' for s in final.values())} ok")
    p4 = []; p5 = []; counts = {}
    for t in TOPS:
        s = open(os.path.join(V, f"top-{t}-stack256.log"), encoding="utf-8").read()
        m = re.search(r"Checked (\d+) declarations with no typechecker errors", s)
        if not m: p4.append(f"top-{t}: no success line"); continue
        counts[t] = int(m.group(1))
        neg = open(os.path.join(V, f"top-{t}-stack256.neg.log"), encoding="utf-8").read()
        if 'unpermitted axiom "Classical.choice"' not in neg: p4.append(f"top-{t}: control did not refuse Classical.choice")
        res = list(csv.DictReader(open(os.path.join(V, f"top-{t}.result.tsv"), encoding="utf-8"), delimiter="\t"))[0]
        if res["export_exit"] != "0": p4.append(f"top-{t}: export exit {res['export_exit']}")
        diag = re.search(r"(\d+) pretty printer errors: \[\s*(.*?)\s*\]", s, re.S)
        items = [x.strip().strip(",").strip('"') for x in diag.group(2).splitlines() if x.strip()] if diag else []
        if not diag or diag.group(1) != "1" or items != ["Unable to print axioms"]: p5.append(f"top-{t}: diagnostics {items}")
    check("V4 nanoda", p4, ", ".join(f"top-{t} {counts[t]:,}" for t in TOPS if t in counts) + " declarations; four controls refused")
    check("V5 verdicts-only", p5, "one pretty-printer diagnostic per run, 'Unable to print axioms'")
    okr = [r for r in a.values() if r["status"] == "ok"]
    pk = sorted(okr, key=lambda r: -int(r["peak_rss_mb"]))[:2]
    print("first pass: " + ", ".join(f"{r['module']} {r['peak_rss_mb']} MB" for r in pk) + f"; total {sum(int(r['seconds']) for r in okr)} s")
    for m, r in b.items(): print(f"retry: {m} {r['status']}, {r['seconds']} s, {r['peak_rss_mb']} MB (first pass {a[m]['status']} at {a[m]['peak_rss_mb']} MB)")
    print("RESULT " + ("all checks pass" if all(ok) else f"{ok.count(False)} check(s) failed"))
    return 0 if all(ok) else 1

if __name__ == "__main__":
    sys.exit(main())
