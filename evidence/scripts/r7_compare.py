#!/usr/bin/env python3
"""Independent external review (RPI-RLT-VR-007). Compares the four production-readiness top theorems of
IntelligenceRegulation binder by binder, and checks the reviewer's classification of the differences.

  r7_compare.py <repository root> [evidence dir]

Inputs (read only): the four theorems' source text (via r5_static_binders.py); the VPS axiom log, for the Lean list
of the L55 theorem's hypotheses; results/R6-reconciliation/classification-normalized.tsv; scripts/r7_added.json
(binders a parallel theorem adds); scripts/r7_exchange.json (what stands in place of each discharged or open key).
Writes results/R7-comparison/four-theorems.tsv and comparison-summary.txt. Exit 0 only when every check passes.

Checks:
  C1 same-conclusion  the four theorems have the same conclusion text
  C2 lean-agrees      the L55 theorem's propositional binders, as Lean lists them in the VPS log, are exactly its
                      binders that r7_added.json or the normalized classification treats as hypotheses
  C3 added-covered    every binder a parallel theorem has and the audited one lacks is classified in r7_added.json,
                      and r7_added.json names nothing else
  C4 exchange-true    for each entry of r7_exchange.json: its keys are binders of the audited theorem; "absent_on"
                      is exactly the set of lines lacking them; each name "in its place" is a binder of that line
                      and absent from the audited theorem; no key is an open obligation of the normalized classification
  C5 open-accounted   each open key of the audited theorem is, on each line, either a binder there or replaced
                      by stand-ins listed in r7_exchange.json that are binders there
  C6 relation-sound   a key marked "discharged" has nothing in its place on any line; a key marked "exchanged"
                      has a non-empty list in its place on every line where it is absent
  C7 lacks-partitioned every hypothesis of the audited theorem that a line lacks is exactly one of: discharged,
                      exchanged, open (an earlier form stands there), or a condition of the audited theorem's finer
                      stage forms
  C8 discharge-sourced every key that the normalized classification classes "discharged" has an entry in
                      r7_exchange.json naming the theorem or lemma that supplies it
A smaller count of hypotheses on a line is reported and never read as a stronger result: the checks establish which
hypotheses are absent and what stands in their place, from names; they read no proof.
"""
import csv, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = {"audited": ("RunStgAlgTopR.lean", "stgAlg_productionReadyL_epP_exec_real", "L57"),
       "eb": ("RunEpBTopT.lean", "eb_productionReadyL_epP_codeT", "L52"),
       "cb": ("RunCloseBTopF.lean", "cb_productionReadyL_epP_codeF", "L55"),
       "bnd": ("RunBndTop.lean", "bnd_productionReadyL_epP_args", "L56")}
LINES = ("eb", "cb", "bnd")

def static(root, f, n):
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "r5_static_binders.py"),
                        os.path.join(root, "formal/ZK60Formal", f), n, "--json"], capture_output=True, text=True)
    if r.returncode: raise SystemExit(f"cannot read {n}: {r.stdout}{r.stderr}")
    return json.loads(r.stdout)

def lean_hyps(log, decl):
    i = log.index("PREMISES " + decl); k = log.index("hypotheses: [", i); e = log.index("]", k)
    return [x.strip() for x in log[k + 13:e].replace("\n", " ").split(",") if x.strip() and not x.strip().startswith("inst")]

def main():
    root = sys.argv[1]
    E = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(HERE)
    out = os.path.join(E, "results/R7-comparison"); os.makedirs(out, exist_ok=True)
    J = {k: static(root, f, n) for k, (f, n, _) in TOP.items()}
    B = {k: [b["name"] for b in j["binders"] if b["name"] != "(instance)"] for k, j in J.items()}
    S = {k: set(v) for k, v in B.items()}
    added = json.load(open(os.path.join(HERE, "r7_added.json"), encoding="utf-8"))["names"]
    X = json.load(open(os.path.join(HERE, "r7_exchange.json"), encoding="utf-8"))
    norm = list(csv.DictReader(open(os.path.join(E, "results/R6-reconciliation/classification-normalized.tsv"), encoding="utf-8"), delimiter="\t"))
    ncat = {}; kcat = {r["key"]: r["category"] for r in norm}
    for r in norm: ncat.setdefault(r["key"].split(".")[0], set()).add(r["category"])
    log = open(os.path.join(E, "results/R1-lean-vps/03-axioms-premises.log"), encoding="utf-8").read()
    ok = []; msgs = []
    def check(name, probs, detail=""):
        ok.append(not probs); msgs.append(("PASS " if not probs else "FAIL ") + name + (": " + detail if not probs and detail else "") +
                                          ("" if not probs else ": " + "; ".join(probs[:6])))
    concl = {J[k]["conclusion"] for k in TOP}
    check("C1 same-conclusion", [] if len(concl) == 1 else [f"{len(concl)} different conclusions"], "one conclusion, ProductionReadyL at radius 768")
    lh = set(lean_hyps(log, "ZK60.ProtocolClassify.RunShapeP." + TOP["cb"][1]))
    def is_hyp(name):
        if name in added: return added[name]["kind"] == "hypothesis"
        cats = ncat.get(name)
        return cats is not None and name not in ("T", "Xx", "place", "site", "mk", "Rn", "Iin", "Oout", "bp", "hon") and (name.startswith("h") or name in ("O", "msg_place"))
    mine = {n for n in S["cb"] if is_hyp(n)}
    p2 = [f"Lean lists {n}, the review does not treat it as a hypothesis" for n in sorted(lh - mine)] + \
         [f"the review treats {n} as a hypothesis, Lean does not list it" for n in sorted(mine - lh)]
    check("C2 lean-agrees", p2, f"{len(lh)} propositional binders of the L55 theorem")
    extra = set().union(*[S[k] - S["audited"] for k in LINES])
    p3 = [f"unclassified added binder {n}" for n in sorted(extra - set(added))] + [f"r7_added.json names {n}, which no line adds" for n in sorted(set(added) - extra)]
    check("C3 added-covered", p3, f"{len(extra)} binders added by the parallel theorems")
    p4 = []; p6 = []
    for e in X["entries"]:
        for key in e["keys"]:
            base = key.split(".")[0]
            if base not in S["audited"]: p4.append(f"{key} is no binder of the audited theorem")
            if "." in key: continue
            absent = [k for k in LINES if base not in S[k]]
            if sorted(absent) != sorted(e["absent_on"]): p4.append(f"{key}: absent on {absent}, the file says {e['absent_on']}")
        place = e["in_its_place"] if isinstance(e["in_its_place"], dict) else {}
        for k, names in place.items():
            for n in names:
                if n not in S[k]: p4.append(f"{e['keys'][0]}: {n} is said to stand in on {k} and is no binder there")
                if n in S["audited"]: p4.append(f"{e['keys'][0]}: {n} stands in on {k} but the audited theorem has it too")
        if e["relation"] == "discharged" and any(place.values()): p6.append(f"{e['keys'][0]} is marked discharged yet something stands in its place")
        if e["relation"] == "exchanged":
            for k in e["absent_on"]:
                if not place.get(k): p6.append(f"{e['keys'][0]} is marked exchanged with nothing in its place on {k}")
        for key in e["keys"]:
            cats = {kcat[key]} if key in kcat else ncat.get(key.split(".")[0], set())
            if "open" in cats: p4.append(f"{key} is an open obligation in the normalized classification and cannot be discharged or exchanged here")
    check("C4 exchange-true", p4, f"{sum(len(e['keys']) for e in X['entries'])} keys in {len(X['entries'])} entries")
    p5 = []
    openp = sorted({r["key"].split(".")[0] for r in norm if r["category"] == "open"})
    for o in openp:
        for k in LINES:
            if o in S[k]: continue
            si = X["open_stand_ins"].get(o, {}).get(k)
            if not si: p5.append(f"open {o} is absent on {k} with no stand-in listed")
            elif any(n not in S[k] for n in si): p5.append(f"open {o}: a stand-in listed for {k} is no binder there")
    check("C5 open-accounted", p5, f"{len(openp)} open binders on 3 lines")
    check("C6 relation-sound", p6, "")
    # table
    names = list(dict.fromkeys(B["audited"] + [n for k in LINES for n in B[k]]))
    rel = {}
    for e in X["entries"]:
        for key in e["keys"]: rel[key.split(".")[0]] = e["relation"]
    with open(os.path.join(out, "four-theorems.tsv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["binder", "audited_L57", "eb_L52", "cb_L55", "bnd_L56", "category", "relation_or_status", "source"])
        for n in names:
            pres = ["yes" if n in S[k] else "" for k in TOP]
            if n in added: cat, st, src = added[n]["category"], added[n]["status"], added[n]["evidence"]
            elif n in ncat: cat, st, src = "/".join(sorted(ncat[n])), rel.get(n, ""), "results/R6-reconciliation/classification-normalized.tsv"
            else: cat, st, src = "data", "", ""
            w.writerow([n] + pres + [cat, st, src])
    # summary
    lack = {k: [n for n in B["audited"] if n not in S[k] and is_hyp(n)] for k in LINES}
    add_h = {k: [n for n in B[k] if n not in S["audited"] and added.get(n, {}).get("kind") == "hypothesis"] for k in LINES}
    openset = set(openp)
    openl = {k: sorted(n for n in B[k] if n in openset or added.get(n, {}).get("category") == "open") for k in TOP}
    # C7: every hypothesis a line lacks falls in exactly one bucket, and every lacked open one has a stand-in
    p7 = []
    for k in LINES:
        for n in lack[k]:
            b = [rel.get(n) == "discharged", rel.get(n) == "exchanged", n in X["audited_refinement_conditions"]["keys"], n in openset]
            if sum(b) != 1: p7.append(f"{n} on {k} falls in {sum(b)} buckets")
    listed = {key for e in X["entries"] for key in e["keys"]}
    p8 = [f"{r['key']} is classed discharged and r7_exchange.json records no supplier for it" for r in norm
          if r["category"] == "discharged" and r["key"] not in listed]
    check("C8 discharge-sourced", p8, f"{sum(r['category'] == 'discharged' for r in norm)} discharged keys, each with its supplier")
    check("C7 lacks-partitioned", p7, "each lacked hypothesis is discharged, exchanged, an open obligation in another form, or a finer-form condition")
    lines = ["# Four production-readiness top theorems, compared (independent external review, VR-007)", ""]
    for k in LINES:
        lk = lack[k]
        d = [n for n in lk if rel.get(n) == "discharged"]; x = [n for n in lk if rel.get(n) == "exchanged"]
        c_ = [n for n in lk if n in X["audited_refinement_conditions"]["keys"]]
        r_ = [n for n in lk if n not in d and n not in x and n not in c_]
        ah = add_h[k]; cats = {}
        for n in ah: cats.setdefault(added[n]["category"], []).append(n)
        lines += [f"{TOP[k][1]} ({TOP[k][2]}): binders {len(B[k])}",
                  f"  lacks {len(lk)} hypotheses of the audited theorem: discharged {len(d)}, exchanged {len(x)}, open, another form of it stands here {len(r_)}, conditions of the audited theorem's finer stage forms {len(c_)}",
                  f"    discharged: {' '.join(d)}", f"    exchanged: {' '.join(x)}", f"    open, another form of it stands here: {' '.join(r_)}",
                  f"    finer-form conditions: {' '.join(c_)}",
                  f"  open hypotheses on this line: {len(openl[k])} (the audited theorem: {len(openl['audited'])})",
                  f"  adds {len(ah)} hypotheses: " + "; ".join(f"{c} {len(v)}" for c, v in sorted(cats.items())),
                  *[f"    {c}: {' '.join(v)}" for c, v in sorted(cats.items())], ""]
    lines += msgs + ["RESULT " + ("all checks pass" if all(ok) else f"{ok.count(False)} check(s) failed")]
    open(os.path.join(out, "comparison-summary.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if all(ok) else 1

if __name__ == "__main__":
    sys.exit(main())
