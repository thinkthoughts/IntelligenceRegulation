#!/usr/bin/env python3
"""Independent external review (RPI-RLT-VR-005, step R5). Checks a premise classification against an inventory.

  r5_check_classification.py --lean  inventory-lean.json   classification.tsv
  r5_check_classification.py --static static-binders.json  classification.tsv

--lean (the authority): the keys the classification must cover are computed from Lean's own answer:
  * every binder whose type is a proposition and is not a structure with proposition fields: its name;
  * every proposition-typed binder that is a structure with proposition fields (a bundle): one key
    `<binder>.<field>` per proposition field;
  * every explicit data binder whose structure type has proposition fields: its name (the bundle is classified whole).
  The check fails on a missing key, an extra key, a repeated key or an unknown category.
--static (interim, from source text): fails on a repeated key, an unknown category, a key whose binder name is absent
  from the statement, or a binder named h… that has no classification. It cannot see inside structures.
Exit 0 on agreement, 1 on any difference, 2 on bad input.
"""
import csv, json, sys
from collections import Counter

CATEGORIES = {"discharged", "open", "modelling", "instance-data", "bookkeeping", "ruling"}

def required_lean(inv):
    req = []
    for b in inv["binders"]:
        pf = [f["field"] for f in b["structureFields"] if f["isProp"]]
        if b["isProp"]:
            req += [f'{b["name"]}.{f}' for f in pf] if pf else [b["name"]]
        elif pf and b["binder"] == "explicit":
            req.append(b["name"])
    return req

def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("--lean", "--static"):
        print(__doc__); return 2
    mode, inv_path, cls_path = sys.argv[1:]
    inv = json.load(open(inv_path, encoding="utf-8"))
    rows = list(csv.DictReader(open(cls_path, encoding="utf-8", newline=""), delimiter="\t"))
    keys = [r["key"] for r in rows]
    problems = []
    problems += [f"repeated key: {k}" for k, c in Counter(keys).items() if c > 1]
    problems += [f"unknown category for {r['key']}: {r['category']}" for r in rows if r["category"] not in CATEGORIES]
    if mode == "--lean":
        if inv.get("schema") != "r5-premise-inventory/1": print("not a Lean inventory"); return 2
        req = required_lean(inv)
        problems += [f"missing classification: {k}" for k in req if k not in keys]
        problems += [f"extra classification (absent from Lean's list): {k}" for k in keys if k not in req]
    else:
        if inv.get("schema") != "r5-static-binders/1": print("not a static binder list"); return 2
        names = {b["name"] for b in inv["binders"]}
        problems += [f"key names no binder of the statement: {k}" for k in keys if k.split(".")[0] not in names]
        problems += [f"missing classification: {n}" for n in sorted(names) if n.startswith("h") and n not in keys]
        req = keys
    counts = Counter(r["category"] for r in rows)
    print(f"declaration: {inv.get('declaration', inv.get('theorem'))}")
    print(f"mode: {mode[2:]}; keys required: {len(req)}; keys classified: {len(keys)}")
    print("by category: " + ", ".join(f"{c}={counts.get(c, 0)}" for c in sorted(CATEGORIES)))
    for p in problems: print("PROBLEM " + p)
    print("RESULT " + ("agree" if not problems else f"{len(problems)} difference(s)"))
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
