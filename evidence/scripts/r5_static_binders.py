#!/usr/bin/env python3
"""Independent external review (RPI-RLT-VR-005, step R5). Reads a Lean source file as text and lists the binders
written in one theorem's statement. It runs no Lean: it sees the binders as written (section variables that Lean
adds to the theorem are listed separately, from the file's `variable` lines, as candidates only). The list Lean
itself reports (r5_premise_inventory.lean) is the authority; this script exists so the two can be compared and
so a reader without a 16 GB machine can see the statement's shape.

usage: r5_static_binders.py <file.lean> <theorem name> [--json]
"""
import json, re, sys

OPEN, CLOSE = "([{⦃", ")]}⦄"

def statement(src, name):
    m = re.search(r"^theorem\s+" + re.escape(name) + r"\b", src, re.M)
    if not m:
        raise SystemExit(f"theorem {name} not found")
    i = m.end(); depth = 0; j = i
    while j < len(src):
        c = src[j]
        if c in OPEN: depth += 1
        elif c in CLOSE: depth -= 1
        elif depth == 0 and src.startswith(":=", j):
            return src[i:j]
        j += 1
    raise SystemExit("no ':=' found at depth 0")

def groups(text):
    out = []; depth = 0; start = None
    for k, c in enumerate(text):
        if c in OPEN:
            if depth == 0: start = k
            depth += 1
        elif c in CLOSE:
            depth -= 1
            if depth == 0: out.append((text[start], text[start + 1:k], k + 1))
    return out

def binders(text, origin):
    rows = []
    for br, body, _ in groups(text):
        body = " ".join(body.split())
        if br == "[":
            rows.append({"names": [], "bracket": "[]", "type": body, "origin": origin}); continue
        if ":" not in body: continue
        names, ty = body.split(":", 1)
        rows.append({"names": names.split(), "bracket": {"(": "()", "{": "{}", "⦃": "⦃⦄"}[br],
                     "type": ty.strip(), "origin": origin})
    return rows

def main():
    path, name = sys.argv[1], sys.argv[2]
    src = open(path, encoding="utf-8").read()
    st = statement(src, name)
    depth = 0; cut = len(st)
    for k, c in enumerate(st):          # the first ':' outside every bracket separates binders from conclusion
        if c in OPEN: depth += 1
        elif c in CLOSE: depth -= 1
        elif c == ":" and depth == 0: cut = k; break
    concl = " ".join(st[cut + 1:].split())
    st = st[:cut]
    head = src[:src.index("theorem " + name)]
    var = [b for m in re.finditer(r"^variable\s+(.*?)(?=^\S)", head, re.M | re.S) for b in binders(m.group(1), "section variable (candidate)")]
    rows = var + binders(st, "theorem statement")
    flat = []
    for r in rows:
        for n in (r["names"] or ["(instance)"]):
            flat.append({"name": n, "bracket": r["bracket"], "origin": r["origin"], "type": r["type"]})
    if "--json" in sys.argv:
        json.dump({"schema": "r5-static-binders/1", "file": path, "theorem": name, "conclusion": concl, "binders": flat},
                  sys.stdout, ensure_ascii=False, indent=1)
    else:
        for f in flat:
            print(f"{f['name']}\t{f['bracket']}\t{f['origin']}\t{f['type'][:150]}")
        print("CONCLUSION\t" + concl[:300])

if __name__ == "__main__":
    main()
