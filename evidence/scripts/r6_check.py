#!/usr/bin/env python3
"""Independent external review (RPI-RLT-VR-006). Consistency checks of the reconciled premise inventory.

  r6_check.py [evidence dir]        (default: the evidence/ folder this script lives in)

Checks, each printed as PASS or FAIL; exit 0 only when all pass:
  1 preserved     inventory-lean.json has the SHA-256 that its generation log recorded on the VPS
  2 vps-hashes    every file named in R1-lean-vps/SHA256SUMS has the recorded hash
  3 lean-vs-log   Lean's inventory agrees with the VPS axiom log: 196 binders, 88 propositional, the same three axioms
  4 lean-vs-text  Lean's binder names, in order, equal the names read from the source text
  5 map-complete  lean-key-map.tsv holds exactly the keys Lean's inventory requires, each once
  6 classified    every normalized key has exactly one row with a known category; no stray rows
  7 traced        every row of the VR-005 classification is the trace of at least one Lean key
  8 discharges    every binder classified "discharged" is absent from at least one parallel top theorem, or is
                  covered by a cited lemma; every binder classified "open" is a binder of the audited theorem
"""
import csv, hashlib, json, os, re, sys
CATS = {"discharged", "open", "modelling", "instance-data", "bookkeeping", "ruling"}
STD = ["Classical.choice", "Quot.sound", "propext"]
DECL = "ZK60.ProtocolClassify.RunShapeP.stgAlg_productionReadyL_epP_exec_real"

def tsv(p): return list(csv.DictReader(open(p, encoding="utf-8", newline=""), delimiter="\t"))
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def required(inv):
    out = []
    for b in inv["binders"]:
        pf = [f["field"] for f in b["structureFields"] if f["isProp"]]
        if b["isProp"]: out += [f'{b["name"]}.{f}' for f in pf] if pf else [b["name"]]
        elif pf and b["binder"] == "explicit": out.append(b["name"])
    return out

def main():
    E = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    R5, R6, V = E + "/results/R5-premises/", E + "/results/R6-reconciliation/", E + "/results/R1-lean-vps/"
    res = []
    def check(name, ok, detail=""): res.append(ok); print(("PASS " if ok else "FAIL ") + name + (": " + detail if detail else ""))
    inv = json.load(open(R5 + "inventory-lean.json", encoding="utf-8"))
    log = open(R5 + "inventory-lean.log", encoding="utf-8").read()
    m = re.search(r"^([0-9a-f]{64})\s+\S*inventory-lean\.json", log, re.M)
    check("1 preserved", bool(m) and m.group(1) == sha(R5 + "inventory-lean.json"), "sha256 " + sha(R5 + "inventory-lean.json")[:16] + "…")
    bad = [l.split()[1] for l in open(V + "SHA256SUMS") if l.strip() and sha(V + l.split()[1].lstrip("*")) != l.split()[0]]
    check("2 vps-hashes", not bad, "differs: " + " ".join(bad) if bad else "6 files" if True else "")
    ax = open(V + "03-axioms-premises.log", encoding="utf-8").read()
    pm = re.search(re.escape("PREMISES " + DECL) + r": (\d+) binders = (\d+) data \+ (\d+) instance \+ (\d+) propositional", ax)
    am = re.search(re.escape("'" + DECL + "' depends on axioms: [") + r"([^\]]*)\]", ax)
    logax = sorted(x.strip() for x in am.group(1).replace("\n", " ").split(",")) if am else None
    nprop = sum(b["isProp"] for b in inv["binders"])
    ok3 = (inv["declaration"] == DECL and pm is not None and int(pm.group(1)) == inv["binderCount"] == len(inv["binders"])
           and int(pm.group(4)) == nprop and sorted(inv["axioms"]) == STD == logax)
    check("3 lean-vs-log", ok3, f"{inv['binderCount']} binders, {nprop} propositional, axioms {sorted(inv['axioms'])}")
    st = json.load(open(R5 + "inventory-static.json", encoding="utf-8"))
    ln = [b["name"] for b in inv["binders"] if b["binder"] != "instance"]; sn = [b["name"] for b in st["binders"] if b["name"] != "(instance)"]
    check("4 lean-vs-text", ln == sn and len(inv["binders"]) == len(st["binders"]), f"{len(ln)} named binders in the same order")
    mp = tsv(R6 + "lean-key-map.tsv"); req = required(inv); mk = [r["lean_key"] for r in mp]
    check("5 map-complete", sorted(mk) == sorted(req) and len(set(mk)) == len(mk), f"{len(mk)} keys in the map, {len(req)} required")
    nc = tsv(R6 + "classification-normalized.tsv"); nk = [r["key"] for r in nc]; want = {r["normalized_key"] for r in mp}
    probs = ([f"unclassified {k}" for k in sorted(want - set(nk))] + [f"stray {k}" for k in nk if k not in want]
             + [f"repeated {k}" for k in set(nk) if nk.count(k) > 1] + [f"category {r['category']} at {r['key']}" for r in nc if r["category"] not in CATS])
    check("6 classified", not probs, "; ".join(probs[:6]) if probs else f"{len(nk)} normalized keys")
    old = [r["key"] for r in tsv(R5 + "classification.tsv")]; tr = {r["vr005_row"] for r in mp}
    lost = [k for k in old if k not in tr]
    check("7 traced", not lost, "untraced: " + " ".join(lost) if lost else f"{len(old)} VR-005 rows")
    pl = json.load(open(R6 + "parallel-lines.json", encoding="utf-8"))
    lemma_items = {r["item"].split(" ")[0] for r in tsv(R6 + "discharge-audit.tsv") if r["kind"].startswith("lemma")}
    absent = set().union(*[set(d["absent_here"]) for d in pl["lines"].values()])
    inv_names = {b["name"] for b in inv["binders"]}
    p8 = [f"'{r['key']}' is marked discharged and every parallel theorem still has it" for r in nc
          if r["category"] == "discharged" and r["key"].split(".")[0] not in absent and r["key"] not in lemma_items]
    p8 += [f"'{r['key']}' is marked open and is no binder of the audited theorem" for r in nc if r["category"] == "open" and r["key"].split(".")[0] not in inv_names]
    check("8 discharges", not p8, "; ".join(p8[:4]) if p8 else "")
    from collections import Counter
    c = Counter(r["category"] for r in nc)
    print("normalized keys by category: " + ", ".join(f"{k}={c.get(k, 0)}" for k in sorted(CATS)))
    print("RESULT " + ("all checks pass" if all(res) else f"{res.count(False)} check(s) failed"))
    return 0 if all(res) else 1

if __name__ == "__main__":
    sys.exit(main())
