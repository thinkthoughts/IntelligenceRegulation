#!/bin/bash
# Independent external review (RPI-RLT-VR-004), step R2, second form: run every Hashline library test in its own
# process, so that one test killed for memory (the reviewer's machine allows about 6 GiB per job) leaves the rest
# of the suite counted. Run from the repository root at commit eee3eb57 after r2-rust.sh has built the test binary.
# HL_R13_LOADER_FIXTURES is the override the test source itself names for the R13 loader fixtures; the path is
# the in-repository copy. No source file is changed.
set -u
OUT=$(realpath "${1:-evidence/results/R2-rust}")
ROOT=$(pwd)
BIN=$(ls ${CARGO_TARGET_DIR:-/tmp/ir-target-rel}/release/deps/hashline-* | grep -v '\.d$' | head -1)
export HL_R13_LOADER_FIXTURES=$ROOT/results/zk60_1b_native_20261017/r13/loader-fixtures
cd ops/zkp-mvp/gpu-metal/hashline || exit 2
TSV=$OUT/hashline-per-test.tsv
"$BIN" --list 2>/dev/null | sed -n 's/: test$//p' > "$OUT/hashline-test-names.txt"
[ -f "$TSV" ] || printf 'test\tstatus\tseconds\n' > "$TSV"
while read -r t; do
  grep -q "^$t	" "$TSV" && continue
  s=$(date +%s)
  timeout ${PER_TEST_TIMEOUT:-900} "$BIN" "$t" --exact --test-threads=1 > /tmp/r2-one.out 2>&1; rc=$?
  e=$(date +%s)
  if   grep -q '1 passed' /tmp/r2-one.out;  then st=passed
  elif grep -q '1 ignored' /tmp/r2-one.out; then st=ignored
  elif [ $rc -eq 124 ]; then st=timeout
  elif [ $rc -ge 128 ]; then st="killed(signal $((rc-128)))"
  else st=failed; { echo "=== $t"; grep -A3 'panicked at' /tmp/r2-one.out | head -6; } >> "$OUT/hashline-per-test-failures.log"
  fi
  printf '%s\t%s\t%s\n' "$t" "$st" "$((e-s))" >> "$TSV"
done < "$OUT/hashline-test-names.txt"
date -u +%FT%TZ > "$OUT/hashline-per-test.done"
