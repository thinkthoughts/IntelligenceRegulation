#!/bin/bash
# Independent external review (VR-006): positive and negative tests of r6_check.py. Needs python3 only.
# Each negative test copies the evidence it needs to a scratch folder, damages one thing, and expects the named check to fail.
set -u
HERE=$(cd "$(dirname "$0")" && pwd); S=$(dirname "$HERE"); E=$(dirname "$S"); pass=0; fail=0
fresh() { T=$(mktemp -d); mkdir -p "$T/results"; cp -r "$E/results/R5-premises" "$E/results/R6-reconciliation" "$E/results/R1-lean-vps" "$T/results/"; }
run() { # name wanted-exit wanted-text
  python3 "$S/r6_check.py" "$T" > "$T/out.txt" 2>&1; local rc=$?
  if [ $rc -eq "$2" ] && grep -q "$3" "$T/out.txt"; then echo "PASS  $1"; pass=$((pass+1)); else echo "FAIL  $1 (exit $rc)"; sed 's/^/      /' "$T/out.txt" | head -12; fail=$((fail+1)); fi
}
fresh; run "the committed evidence passes all eight checks" 0 "RESULT all checks pass"
fresh; printf ' ' >> "$T/results/R5-premises/inventory-lean.json"; run "a changed Lean inventory is caught" 1 "FAIL 1 preserved"
fresh; echo "edited" >> "$T/results/R1-lean-vps/02-lake-build.log"; run "a changed VPS log is caught" 1 "FAIL 2 vps-hashes"
fresh; python3 -c "
import json,sys; p=sys.argv[1]; j=json.load(open(p))
[b for b in j['binders'] if b['name']=='hdzero'][0]['isProp']=False
json.dump(j,open(p,'w'))" "$T/results/R5-premises/inventory-lean.json"; run "an inventory that disagrees with the VPS axiom log is caught" 1 "FAIL 3 lean-vs-log"
fresh; sed -i '/^hblk\t/d' "$T/results/R6-reconciliation/lean-key-map.tsv"; run "a Lean key missing from the map is caught" 1 "FAIL 5 map-complete"
fresh; sed -i '/^hdzero\t/d' "$T/results/R6-reconciliation/classification-normalized.tsv"; run "an unclassified key is caught" 1 "unclassified hdzero"
fresh; printf 'hGhost\topen\t\t\t\t\tnew\n' >> "$T/results/R6-reconciliation/classification-normalized.tsv"; run "a stray classification row is caught" 1 "stray hGhost"
fresh; sed -i 's/^hdzero\topen/hdzero\tproved/' "$T/results/R6-reconciliation/classification-normalized.tsv"; run "an unknown category is caught" 1 "category proved at hdzero"
fresh; sed -i 's/^hblk\topen/hblk\tdischarged/' "$T/results/R6-reconciliation/classification-normalized.tsv"; run "a hypothesis wrongly marked discharged is caught" 1 "'hblk' is marked discharged"
fresh; sed -i 's/\thW\tconjunct-of\thW\t/\thW\tconjunct-of\tnone\t/' "$T/results/R6-reconciliation/lean-key-map.tsv"; run "a VR-005 row with no trace is caught" 1 "untraced: hW"
echo "tests passed: $pass, failed: $fail"; [ "$fail" -eq 0 ]
