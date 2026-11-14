#!/bin/bash
# Independent external review (RPI-RLT-VR-004), step R2: run the Rust tests and the public-fixture demo.
# These are the commands the reviewer ran. Run from the repository root at commit eee3eb57. CPU only.
# Build output goes to $CARGO_TARGET_DIR (outside the checkout). No source file is changed.
# Note: the tests write three result folders under ops/zkp-mvp/gpu-metal/results/ (r12-tied-2347,
# r12b-profile-fields, r12b-rope); they are test output and are left untracked.
# On a machine with less than about 8 GiB per job, use r2-hashline-per-test.sh for the Hashline suite instead of
# the single-process run below (the reviewer's single-process run was killed for memory after 613 passes).
set -u
OUT=$(realpath "${1:-evidence/results/R2-rust}")
mkdir -p "$OUT"
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-/tmp/ir-target-rel}
( cd ops/zkp-mvp/gpu-metal/zkp-core && cargo test --locked --release --lib ) > "$OUT/zkp-core-lib-release.log" 2>&1
echo "zkp-core: exit $?"
( cd ops/zkp-mvp/gpu-metal/hashline && cargo test --locked --release --lib -- --test-threads=2 ) > "$OUT/hashline-lib-release.log" 2>&1
echo "hashline: exit $?"
# The F12 controls alone (eight tests whose names contain "f12"):
( cd ops/zkp-mvp/gpu-metal/hashline && cargo test --locked --release --lib f12 -- --test-threads=1 --nocapture ) > "$OUT/f12-control.log" 2>&1
echo "f12 controls: exit $?"
# The one-command CPU demo with public synthetic fixtures (prove, verify in a separate process, six refusals):
python3 scripts/zk60_p1_demo.py --output "$OUT/p1-demo" > "$OUT/p1-demo.log" 2>&1
echo "p1 demo: exit $?"
