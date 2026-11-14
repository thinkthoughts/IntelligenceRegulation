#!/usr/bin/env python3
"""Independent external review (RPI-RLT-VR-006). Reconciles Lean's premise inventory with the VR-005 classification.

  r6_reconcile.py <inventory-lean.json> <classification.tsv (VR-005)> <r6_rules.json> <out dir>

Reads the three inputs and changes none of them. Writes, in <out dir>:
  lean-key-map.tsv              one row per key Lean's inventory requires (the rule of r5_check_classification.py),
                                with the normalized key it maps to, the VR-005 row it traces to and the discrepancy class
  classification-normalized.tsv one row per normalized key
Normalization rules (r6_rules.json):
  * a hypothesis whose type is a conjunction (head `And`) is one key, the binder's name; the tool had split it into
    `.left` / `.right` because `And` is a structure;
  * a hypothesis bundle (a proposition-valued structure) stays split into its fields, one key each; a field inherits
    the VR-005 category of its parent unless a rule gives it its own;
  * a data binder whose listed proof fields belong to a library type (`Fin`, `Finset`) is kept as one key and marked
    as a library invariant;
  * every other key is kept as Lean lists it.
"""
import csv, json, sys

def required(inv):
    out = []
    for b in inv["binders"]:
        pf = [f["field"] for f in b["structureFields"] if f["isProp"]]
        if b["isProp"]:
            out += [(f'{b["name"]}.{f}', "bundle-field", b) for f in pf] if pf else [(b["name"], "prop", b)]
        elif pf and b["binder"] == "explicit":
            out.append((b["name"], "data-with-proofs", b))
    return out

def main():
    inv_p, cls_p, rules_p, out = sys.argv[1:5]
    inv = json.load(open(inv_p, encoding="utf-8")); rules = json.load(open(rules_p, encoding="utf-8"))
    old = {r["key"]: r for r in csv.DictReader(open(cls_p, encoding="utf-8", newline=""), delimiter="\t")}
    maprows, norm = [], {}
    def put(nkey, cat, status, ev, note, vr005, change):
        if nkey not in norm:
            norm[nkey] = [nkey, cat, status, ev, note, vr005, change]
    for key, kind, b in required(inv):
        parent = b["name"]
        if kind == "bundle-field" and b["head"] in rules["conjunction_heads"]:
            nkey, rel, cls = parent, "conjunct-of", "conjunction split by the tool"
        elif kind == "data-with-proofs" and b["head"] in rules["library_invariant_heads"]:
            nkey, rel, cls = parent, "same", "new: library type invariant"
        elif kind == "bundle-field":
            nkey, rel = key, "same"
            cls = "matched" if key in old else "nested proof field of a bundle VR-005 classified as one row"
        else:
            nkey, rel = key, "same"
            if key in old: cls = "matched"
            elif b["binder"] == "instance": cls = "new: instance parameter"
            elif kind == "data-with-proofs": cls = "new: data binder with proof fields"
            else: cls = "new: hypothesis omitted by VR-005"
        trace = key if key in old else (parent if parent in old else "none")
        maprows.append([key, b["index"], b["binder"], kind, b["head"], nkey, rel, trace, cls])
        # classification of the normalized key
        if nkey in old:
            o = old[nkey]; put(nkey, o["category"], o["status"], o["evidence"], o["note"], o["category"], "unchanged")
        elif nkey in rules["field_overrides"]:
            c, s, e, n = rules["field_overrides"][nkey]
            oc = old[parent]["category"] if parent in old else ""
            put(nkey, c, s, e, n, oc + " (as part of " + parent + ")" if oc else "", "refined from the parent row" if oc else "new")
        elif kind == "bundle-field" and parent in old:
            o = old[parent]
            if parent in rules["parent_field_default"]:
                c, s, e, n = rules["parent_field_default"][parent]
                put(nkey, c, s, e, n, o["category"] + " (as part of " + parent + ")", "refined from the parent row")
            else:
                put(nkey, o["category"], o["status"], o["evidence"], "field of " + parent + "; " + o["note"] if o["note"] else "field of " + parent,
                    o["category"] + " (as part of " + parent + ")", "expanded from the parent row, category kept")
        elif nkey in rules["new_keys"]:
            c, s, e, n = rules["new_keys"][nkey]; put(nkey, c, s, e, n, "", "new")
        else:
            put(nkey, "UNCLASSIFIED", "", "", "", "", "new")
    with open(out + "/lean-key-map.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["lean_key", "binder_index", "binder_kind", "lean_kind", "type_head", "normalized_key", "relation", "vr005_row", "discrepancy_class"])
        w.writerows(maprows)
    with open(out + "/classification-normalized.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["key", "category", "status", "evidence", "note", "vr005_category", "change"])
        w.writerows(norm.values())
    print(f"lean keys: {len(maprows)}; normalized keys: {len(norm)}")

if __name__ == "__main__":
    main()
