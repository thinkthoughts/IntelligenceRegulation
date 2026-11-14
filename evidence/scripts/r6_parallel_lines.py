#!/usr/bin/env python3
"""Independent external review (RPI-RLT-VR-006). Compares, from source text, the binder names of the audited top
theorem with the three parallel top theorems of the repository, and lists the hypotheses of the lemmas cited as
discharging some of them. No Lean run; names only.

  r6_parallel_lines.py <repository root> <classification-normalized.tsv> <out dir>

Writes parallel-lines.json and discharge-audit.tsv. "Absent on a line" means: the name is a binder of the audited
theorem and is no binder of that line's theorem. It shows that the line's theorem needs no such hypothesis; what
that line needs instead is listed as "added".
"""
import csv, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
F = "formal/ZK60Formal/"
TOP = {"audited": ("RunStgAlgTopR.lean", "stgAlg_productionReadyL_epP_exec_real", "L57"),
       "eb": ("RunEpBTopT.lean", "eb_productionReadyL_epP_codeT", "L52"),
       "cb": ("RunCloseBTopF.lean", "cb_productionReadyL_epP_codeF", "L55"),
       "bnd": ("RunBndTop.lean", "bnd_productionReadyL_epP_args", "L56")}
LEMMAS = [("hwin", "RunEndptWin.lean", "ep_hwin_top"), ("hBal", "RunEpBTest.lean", "eb_xB_alive"),
          ("hopX (part 0)", "RunEpBInc.lean", "eb_hopX0"), ("hopX (part 0, earlier form)", "RunOpenGeoStageX.lean", "og_hopX0"),
          ("O.shapes", "RunShapeShield.lean", "shield_shapes_valid")]

def binders(root, file, name):
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "r5_static_binders.py"), os.path.join(root, F + file), name, "--json"],
                       capture_output=True, text=True)
    if r.returncode: raise SystemExit(f"cannot read {name}: {r.stderr or r.stdout}")
    return json.loads(r.stdout)["binders"]

def main():
    root, cls_p, out = sys.argv[1:4]
    names = {k: [b["name"] for b in binders(root, f, n) if b["name"] != "(instance)"] for k, (f, n, _) in TOP.items()}
    A = names["audited"]; res = {"schema": "r6-parallel-lines/1", "theorems": {k: {"file": F + f, "name": n, "lane": l, "binders": len(names[k])} for k, (f, n, l) in TOP.items()}, "lines": {}}
    for k in ("eb", "cb", "bnd"):
        s = set(names[k])
        res["lines"][k] = {"absent_here": [x for x in A if x not in s], "added_here": [x for x in names[k] if x not in set(A)]}
    rows = list(csv.DictReader(open(cls_p, encoding="utf-8", newline=""), delimiter="\t"))
    parents = lambda cat: sorted({r["key"].split(".")[0] for r in rows if r["category"] == cat})
    res["open_binders_presence"] = {p: [k for k in TOP if p in names[k]] for p in parents("open")}
    res["discharged_binders_presence"] = {p: [k for k in TOP if p in names[k]] for p in parents("discharged")}
    json.dump(res, open(out + "/parallel-lines.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(out + "/discharge-audit.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["item", "supplied_by", "file", "what_the_supplier_still_requires", "kind"])
        for k in ("eb", "cb", "bnd"):
            f_, n, l = TOP[k]; d = res["lines"][k]
            hyp = lambda xs: [x for x in xs if x.startswith("h") or x in ("O", "msg_place")]
            w.writerow(["hypotheses of the audited theorem that this theorem lacks: " + " ".join(hyp(d["absent_here"])), n, F + f_,
                        "hypotheses this theorem has and the audited one lacks: " + " ".join(hyp(d["added_here"])) + " (plus every hypothesis the two share)",
                        "parallel top theorem (lane " + l + "); conditional"])
        for item, file, n in LEMMAS:
            b = [x for x in binders(root, file, n) if x["origin"] == "theorem statement"]
            h = [x["name"] for x in b if x["name"].startswith("h")]
            w.writerow([item, n, F + file, (f"{len(h)} named hypotheses: " + " ".join(h)) if h else "no hypothesis; a closed statement about the Shieldstral export",
                        "lemma; " + ("conditional" if h else "unconditional about the concrete export, to be tied to the theorem's parameter S")])
    print(json.dumps({k: {a: len(v) for a, v in d.items()} for k, d in res["lines"].items()}))

if __name__ == "__main__":
    main()
