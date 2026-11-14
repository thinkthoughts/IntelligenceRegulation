#!/bin/bash
# Independent external review (VR-005, R5): positive and negative tests of the premise-inventory tooling.
# Needs python3; the two Lean tests also need the toolchain named in formal/lean-toolchain (skipped when absent).
set -u
HERE=$(cd "$(dirname "$0")" && pwd); S=$(dirname "$HERE"); T=$(mktemp -d); pass=0; fail=0
ok()  { echo "PASS  $1"; pass=$((pass+1)); }
bad() { echo "FAIL  $1"; fail=$((fail+1)); }
expect() { # name expected-exit command...
  local name=$1 want=$2; shift 2; "$@" > "$T/out.txt" 2>&1; local got=$?
  [ "$got" -eq "$want" ] && ok "$name (exit $got)" || { bad "$name (exit $got, wanted $want)"; sed 's/^/      /' "$T/out.txt" | head -8; }
}
C=$S/r5_check_classification.py; F=$HERE/fixture-inventory.json
# 1 positive: a complete classification of the fixture inventory agrees
printf 'key\tcategory\tstatus\tevidence\tnote\nh1\tbookkeeping\t\t\t\nB.pos\topen\t\t\t\nB.small\tdischarged\t\t\t\nd\tbookkeeping\t\t\t\nhall.pos\topen\t\t\t\nhall.small\topen\t\t\t\n' > "$T/good.tsv"
expect "complete classification agrees" 0 python3 "$C" --lean "$F" "$T/good.tsv"
# 2 negative: one hypothesis left out
grep -v '^B.pos' "$T/good.tsv" > "$T/missing.tsv"
expect "a missing hypothesis is reported" 1 python3 "$C" --lean "$F" "$T/missing.tsv"
# 3 negative: a hypothesis the theorem lacks
{ cat "$T/good.tsv"; printf 'hGhost\topen\t\t\t\n'; } > "$T/extra.tsv"
expect "an extra hypothesis is reported" 1 python3 "$C" --lean "$F" "$T/extra.tsv"
# 4 negative: an unknown category
sed 's/^h1\tbookkeeping/h1\tproved-somehow/' "$T/good.tsv" > "$T/badcat.tsv"
expect "an unknown category is reported" 1 python3 "$C" --lean "$F" "$T/badcat.tsv"
# 5 negative: a repeated key
{ cat "$T/good.tsv"; printf 'h1\topen\t\t\t\n'; } > "$T/dup.tsv"
expect "a repeated key is reported" 1 python3 "$C" --lean "$F" "$T/dup.tsv"
# 6 positive: the static lister reads the fixture theorem's binders from text
python3 "$S/r5_static_binders.py" "$HERE/fixture.lean" r5_fixture --json > "$T/static.json" 2>"$T/err.txt"
names=$(python3 -c "import json,sys;print(' '.join(b['name'] for b in json.load(open(sys.argv[1]))['binders']))" "$T/static.json")
[ "$names" = "n m (instance) h1 B d hall" ] && ok "static lister finds the fixture's 7 binders" || bad "static lister: got '$names'"
# 7 negative: the static lister refuses an unknown theorem
expect "static lister refuses an unknown theorem" 1 python3 "$S/r5_static_binders.py" "$HERE/fixture.lean" no_such_theorem
# 8, 9: Lean
if command -v lean >/dev/null 2>&1; then
  LEAN="lean"; command -v elan >/dev/null 2>&1 && LEAN="lean +${R5_TOOLCHAIN:-leanprover/lean4:v4.34.1}"
  { echo 'import Lean'; echo 'set_option linter.unusedVariables false'; cat "$HERE/fixture.lean"; cat "$S/r5_inventory_core.lean"; echo '#premise_inventory r5_fixture'; } > "$T/q.lean"
  R5_OUT="$T/inv.json" $LEAN "$T/q.lean" > "$T/lean.txt" 2>&1
  if python3 - "$T/inv.json" "$F" <<'PY'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
strip = lambda j: [(x["name"], x["binder"], x["isProp"], [(f["field"], f["isProp"]) for f in x["structureFields"] if x["head"].startswith("R5")]) for x in j["binders"]]
sys.exit(0 if strip(a) == strip(b) and a["axioms"] == b["axioms"] == [] and a["conclusionHead"] == b["conclusionHead"] else 1)
PY
  then ok "Lean inventory of the fixture theorem equals the stored one"; else bad "Lean inventory of the fixture differs"; fi
  { echo 'import Lean'; cat "$S/r5_inventory_core.lean"; echo '#premise_inventory no_such_declaration'; } > "$T/q2.lean"
  $LEAN "$T/q2.lean" > "$T/lean2.txt" 2>&1; rc=$?
  { [ $rc -eq 1 ] && grep -qi 'unknown' "$T/lean2.txt"; } && ok "Lean refuses an unknown declaration (exit 1, 'unknown' in the message)" || bad "unknown declaration: exit $rc"
else
  echo "SKIP  two Lean tests (no lean on PATH)"
fi
echo "tests passed: $pass, failed: $fail"; [ "$fail" -eq 0 ]
