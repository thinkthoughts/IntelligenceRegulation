#!/bin/bash
# Independent external review (RPI-RLT-VR-007). Checks one Lean theorem and everything it depends on with nanoda,
# a kernel written in Rust, separate from Lean's own (https://github.com/ammkrn/nanoda_lib).
#
#   evidence/scripts/r7-nanoda.sh <tag> <module> <declaration> [out dir]
#   e.g. evidence/scripts/r7-nanoda.sh top-real ZK60Formal.RunStgAlgTopR \
#        ZK60.ProtocolClassify.RunShapeP.stgAlg_productionReadyL_epP_exec_real
#
# Run from the repository root after `lake build` in formal/ has compiled <module>. Needs git, elan/lake, cargo.
# What it does, in order:
#   1. builds lean4export (pinned commit) with the library's own toolchain, and nanoda_lib (pinned commit), in
#      $R7_WORK (default ~/.cache/r7-nanoda), outside the repository;
#   2. exports <declaration> and its transitive dependencies from <module> as NDJSON into $R7_WORK (not committed:
#      the files are hundreds of megabytes; their SHA-256 is recorded);
#   3. runs nanoda with exactly three permitted axioms (propext, Classical.choice, Quot.sound), any other axiom a
#      hard error;
#   4. control: runs nanoda again on the same export with Classical.choice removed from the permitted list, and
#      expects a refusal, which shows the axiom check is live.
# It writes <out dir>/<tag>.log and <tag>.result.tsv (default out dir evidence/results/R7-nanoda) and changes no
# file of the library. Home paths and the host name are replaced in what it writes.
set -u
TAG=$1; MOD=$2; DECL=$3; OUT=$(realpath -m "${4:-evidence/results/R7-nanoda}"); mkdir -p "$OUT"
WORK=${R7_WORK:-$HOME/.cache/r7-nanoda}; mkdir -p "$WORK"
L4E_COMMIT=df81913eee5519d5a88ae5b0fd701b5298cc29ab       # leanprover/lean4export, 2026-10-14, export format 3.1.0
NANODA_COMMIT=0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929    # ammkrn/nanoda_lib 0.4.32, 2026-11-07, accepts format 3.1.x
TOOLCHAIN=$(cat formal/lean-toolchain)
LOG=$OUT/$TAG.log; RES=$OUT/$TAG.result.tsv
san() { sed -e "s|$HOME|~|g" -e "s|$(hostname)|<host>|g"; }
peak() { # runs "$@" (stdout and stderr untouched), prints "exit seconds peak_rss_mb" on fd 3
  python3 -c '
import os, resource, subprocess, sys, time
t = time.time(); rc = subprocess.call(sys.argv[1:])
kb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
os.write(3, f"{rc} {time.time() - t:.0f} {kb // 1024}\n".encode())' "$@"
}
{
echo "# r7-nanoda: $TAG"; date -u +%FT%TZ; echo "module: $MOD"; echo "declaration: $DECL"; echo "library toolchain: $TOOLCHAIN"
echo "lean4export: $L4E_COMMIT"; echo "nanoda_lib: $NANODA_COMMIT"; echo "source commit: $(git rev-parse HEAD)"
[ -d "$WORK/lean4export" ] || git clone -q https://github.com/leanprover/lean4export "$WORK/lean4export"
( cd "$WORK/lean4export" && git checkout -q $L4E_COMMIT && echo "$TOOLCHAIN" > lean-toolchain && lake build 2>&1 | tail -1 )
[ -d "$WORK/nanoda_lib" ] || git clone -q https://github.com/ammkrn/nanoda_lib "$WORK/nanoda_lib"
( cd "$WORK/nanoda_lib" && git checkout -q $NANODA_COMMIT && CARGO_TARGET_DIR="$WORK/target" cargo build --release 2>&1 | tail -1 )
X=$WORK/lean4export/.lake/build/bin/lean4export; N=$WORK/target/release/nanoda_bin; E=$WORK/$TAG.ndjson
[ -x "$X" ] && [ -x "$N" ] || { echo "BLOCKER: a tool failed to build"; printf 'tag\tstep\tresult\n%s\tbuild\tblocked\n' "$TAG" > "$RES"; exit 3; }
echo "\$ lake env lean4export $MOD -- $DECL > $TAG.ndjson   (cwd: formal/)"
exec 3> "$WORK/$TAG.m1"; ( cd formal && peak lake env "$X" "$MOD" -- "$DECL" > "$E" 2> "$WORK/$TAG.export.err" ); exec 3>&-
read -r erc esec emb < "$WORK/$TAG.m1"
echo "export: exit $erc, $esec s, peak $emb MB, $(wc -l < "$E") lines, $(du -m "$E" | cut -f1) MB, sha256 $(sha256sum "$E" | cut -d' ' -f1)"
head -c 220 "$E" | head -1; tail -3 "$WORK/$TAG.export.err"
grep -q "\"${DECL##*.}\"" "$E" && echo "the export names ${DECL##*.}: yes" || echo "the export names ${DECL##*.}: NO"
cfg() { printf '{"export_file_path": "%s", "permitted_axioms": %s, "unpermitted_axiom_hard_error": true, "nat_extension": true, "string_extension": true, "print_success_message": true}\n' "$E" "$1"; }
cfg '["propext", "Classical.choice", "Quot.sound"]' > "$WORK/$TAG.json"; cfg '["propext", "Quot.sound"]' > "$WORK/$TAG.neg.json"
echo "\$ nanoda_bin <config: three permitted axioms, any other a hard error>"
exec 3> "$WORK/$TAG.m2"; peak "$N" "$WORK/$TAG.json" > "$WORK/$TAG.nanoda.out" 2>&1; exec 3>&-
read -r nrc nsec nmb < "$WORK/$TAG.m2"; tail -4 "$WORK/$TAG.nanoda.out"; echo "nanoda: exit $nrc, $nsec s, peak $nmb MB"
echo "\$ nanoda_bin <control: Classical.choice removed from the permitted axioms; a refusal is expected>"
"$N" "$WORK/$TAG.neg.json" > "$WORK/$TAG.neg.out" 2>&1; crc=$?; tail -3 "$WORK/$TAG.neg.out"; echo "control: exit $crc   (a nonzero exit is the expected refusal when the theorem depends on Classical.choice; exit 0 means the export declares no such axiom)"
date -u +%FT%TZ
printf 'tag\tdeclaration\texport_exit\texport_lines\texport_sha256\tnanoda_exit\tnanoda_seconds\tnanoda_peak_mb\tdeclarations_checked\tcontrol_exit\n' > "$RES"
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$TAG" "$DECL" "$erc" "$(wc -l < "$E")" "$(sha256sum "$E" | cut -d' ' -f1)" "$nrc" "$nsec" "$nmb" \
  "$(grep -o 'Checked [0-9]* declarations' "$WORK/$TAG.nanoda.out" | grep -o '[0-9]*' | head -1)" "$crc" >> "$RES"
} 2>&1 | san > "$LOG"
tail -12 "$LOG"
