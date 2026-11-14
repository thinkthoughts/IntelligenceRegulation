#!/bin/bash
# Independent external review (RPI-RLT-VR-004), step R1: rebuild the Lean tree and inspect the central theorems.
# These are the commands the reviewer ran, in order. Run from the repository root at commit eee3eb57.
# Needs: elan (https://github.com/leanprover/elan), network access to the Mathlib cache, about 8 GB of disk.
# Nothing here changes a file under formal/ZK60Formal; the build writes only formal/.lake/.
set -u
OUT=${1:-evidence/results/R1-lean}
mkdir -p "$OUT"
cd formal || exit 2
lean --version                                           > "../$OUT/environment.txt" 2>&1
lake exe cache get                                       > "../$OUT/01-cache-get.log" 2>&1; echo "cache get: exit $?"
lake build                                               > "../$OUT/02-lake-build.log" 2>&1; echo "lake build: exit $?"
lake env lean ../evidence/scripts/r1_axioms_premises.lean > "../$OUT/03-axioms-premises.log" 2>&1; echo "axioms and premises: exit $?"
# Kernel replay with the checker shipped in the toolchain (it re-checks every declaration of the named modules
# with the Lean kernel, reading the compiled .olean files).
lake env leanchecker ZK60Formal                          > "../$OUT/04-leanchecker.log" 2>&1; echo "leanchecker: exit $?"
# On the reviewer's 6 GiB machine ZK60Formal.RunExtractClassify could not compile, so the reviewer ran instead:
#   lake env lean ../evidence/scripts/r1_axioms_available.lean      (imports only modules that built)
#   lake env leanchecker <module>                                   (once per compiled module; see results/R1-lean/modules-built.txt)
