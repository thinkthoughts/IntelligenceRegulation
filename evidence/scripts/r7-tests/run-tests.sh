#!/bin/bash
# Independent external review (VR-007): positive and adversarial tests of r7_compare.py and r1_replay_modules.py.
#   evidence/scripts/r7-tests/run-tests.sh <path to a clone of IntelligenceRegulation at eee3eb57>
# The comparison tests need python3 only. Each adversarial test edits a scratch copy of the evidence and scripts.
set -u
REPO=${1:?give the path of a clone at eee3eb57}; HERE=$(cd "$(dirname "$0")" && pwd); S=$(dirname "$HERE"); E=$(dirname "$S")
pass=0; fail=0
fresh() { T=$(mktemp -d); mkdir -p "$T/ev/results" "$T/ev/scripts"; cp -r "$E/results/R6-reconciliation" "$E/results/R1-lean-vps" "$T/ev/results/"
          cp "$S"/r5_static_binders.py "$S"/r7_compare.py "$S"/r7_added.json "$S"/r7_exchange.json "$T/ev/scripts/"; }
run() { # name wanted-exit wanted-text
  python3 "$T/ev/scripts/r7_compare.py" "$REPO" "$T/ev" > "$T/out.txt" 2>&1; local rc=$?
  if [ $rc -eq "$2" ] && grep -q -- "$3" "$T/out.txt"; then echo "PASS  $1"; pass=$((pass+1)); else echo "FAIL  $1 (exit $rc)"; grep -E 'FAIL|RESULT' "$T/out.txt" | head -6 | sed 's/^/      /'; fail=$((fail+1)); fi
}
J() { python3 - "$@" <<'PY'
import json, sys
p, code = sys.argv[1], sys.argv[2]; d = json.load(open(p)); exec(code); json.dump(d, open(p, "w"), ensure_ascii=False)
PY
}
fresh; run "the committed classification passes all eight checks" 0 "RESULT all checks pass"
fresh; J "$T/ev/scripts/r7_added.json" "del d['names']['hchk']"; run "an added hypothesis left unclassified is caught" 1 "unclassified added binder hchk"
fresh; J "$T/ev/scripts/r7_added.json" "d['names']['hGhost']={'kind':'hypothesis','category':'open','status':'','evidence':'','note':''}"; run "a classified name that no theorem adds is caught" 1 "names hGhost, which no line adds"
fresh; J "$T/ev/scripts/r7_added.json" "d['names']['hchk']['kind']='data'"; run "a hypothesis mislabelled as data disagrees with Lean" 1 "FAIL C2 lean-agrees"
fresh; J "$T/ev/scripts/r7_added.json" "d['names']['hw']['kind']='hypothesis'"; run "data mislabelled as a hypothesis disagrees with Lean" 1 "Lean does not list it"
fresh; J "$T/ev/scripts/r7_exchange.json" "[e for e in d['entries'] if e['keys']==['hW']][0]['relation']='discharged'"; run "an exchange recorded as a discharge is caught" 1 "is marked discharged yet something stands in its place"
fresh; J "$T/ev/scripts/r7_exchange.json" "[e for e in d['entries'] if e['keys']==['hopX']][0]['in_its_place']['eb'].append('hchk')"; run "a stand-in that the line lacks is caught" 1 "hchk is said to stand in on eb"
fresh; J "$T/ev/scripts/r7_exchange.json" "[e for e in d['entries'] if e['keys']==['hW']][0]['absent_on']=['cb','eb']"; run "a wrong absent-on list is caught" 1 "FAIL C4 exchange-true"
fresh; J "$T/ev/scripts/r7_exchange.json" "del d['open_stand_ins']['hdinS']"; run "an open obligation dropped on a line without a stand-in is caught" 1 "open hdinS is absent on"
fresh; sed -i 's/^hblk\topen/hblk\tdischarged/' "$T/ev/results/R6-reconciliation/classification-normalized.tsv"; run "an open obligation relabelled discharged is caught" 1 "hblk is classed discharged and r7_exchange.json records no supplier"
fresh; J "$T/ev/scripts/r7_exchange.json" "d['audited_refinement_conditions']['keys'].append('hdinS')"; run "a hypothesis placed in two buckets is caught" 1 "hdinS on eb falls in 2 buckets"
# replay script: argument handling only (its guards are exercised on a real module in VR-007 §2.1)
T=$(mktemp -d); python3 "$S/r1_replay_modules.py" --out "$T" > "$T/o.txt" 2>&1; rc=$?
{ [ $rc -ne 0 ] && grep -q 'run from the repository root' "$T/o.txt"; } && { echo "PASS  the replay script refuses to run outside the repository root"; pass=$((pass+1)); } || { echo "FAIL  replay script outside the root (exit $rc)"; fail=$((fail+1)); }
echo "tests passed: $pass, failed: $fail"; [ "$fail" -eq 0 ]
