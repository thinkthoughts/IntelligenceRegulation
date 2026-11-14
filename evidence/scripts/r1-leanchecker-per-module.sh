#!/bin/bash
# Independent external review (VR-006, closing step R1). Replays every compiled module of the library through
# `leanchecker`, one module per process, so that memory stays near the 3 GiB the run-level module needed.
# Run from the repository root after `lake build` in formal/ has completed.
#   evidence/scripts/r1-leanchecker-per-module.sh [out dir]      (resumable: modules already in the result file are skipped)
set -u
OUT=$(realpath -m "${1:-evidence/results/R1-lean-vps}"); mkdir -p "$OUT"
RES=$OUT/06-leanchecker-per-module.tsv
cd formal || exit 2
[ -f "$RES" ] || printf 'module\texit\tseconds\n' > "$RES"
find ZK60Formal -name '*.lean' | sed 's|/|.|g; s|\.lean$||' | sort > "$OUT/06-modules.txt"; echo ZK60Formal >> "$OUT/06-modules.txt"
while read -r m; do
  grep -q "^$m	" "$RES" && continue
  [ -f ".lake/build/lib/lean/$(echo "$m" | tr . /).olean" ] || { printf '%s\tnot-compiled\t0\n' "$m" >> "$RES"; continue; }
  s=$(date +%s); timeout "${PER_MODULE_TIMEOUT:-1800}" lake env leanchecker "$m" > "$OUT/06-last-output.txt" 2>&1; rc=$?; e=$(date +%s)
  printf '%s\t%s\t%s\n' "$m" "$rc" "$((e-s))" >> "$RES"
  [ $rc -ne 0 ] && { echo "=== $m (exit $rc)"; tail -5 "$OUT/06-last-output.txt"; } >> "$OUT/06-leanchecker-failures.log"
done < "$OUT/06-modules.txt"
rm -f "$OUT/06-last-output.txt"
echo "modules: $(($(wc -l < "$RES") - 1)); exit 0: $(awk -F'\t' '$2=="0"' "$RES" | wc -l); other: $(awk -F'\t' 'NR>1 && $2!="0"' "$RES" | wc -l)"
date -u +%FT%TZ
