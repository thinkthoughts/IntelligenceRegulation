#!/bin/bash
# Independent external review (RPI-RLT-VR-005, step R5). Asks Lean for the premise inventory of one declaration.
# Run from the repository root, after `lake build` in formal/ has compiled the module named below.
#   evidence/scripts/r5-premises.sh [module] [declaration] [out.json]
# Defaults: the newest top theorem of the classifier run at commit eee3eb57.
# It writes one temporary Lean file outside formal/, and changes no file of the library.
set -eu
MOD=${1:-ZK60Formal.RunStgAlgTopR}
DECL=${2:-ZK60.ProtocolClassify.RunShapeP.stgAlg_productionReadyL_epP_exec_real}
OUT=$(realpath -m "${3:-evidence/results/R5-premises/inventory-lean.json}")
HERE=$(cd "$(dirname "$0")" && pwd)
TMP=$(mktemp -d)
{ echo "import $MOD"; echo "import Lean"; cat "$HERE/r5_inventory_core.lean"; echo "#premise_inventory $DECL"; } > "$TMP/r5_query.lean"
mkdir -p "$(dirname "$OUT")"
cd formal
echo "\$ R5_OUT=$OUT lake env lean <import $MOD; r5_inventory_core.lean; #premise_inventory $DECL>   (cwd: formal/)"
date -u +%FT%TZ
TIME=""; [ -x /usr/bin/time ] && TIME="/usr/bin/time -v"
R5_OUT="$OUT" $TIME lake env lean "$TMP/r5_query.lean" 2>&1 | grep -E 'R5 inventory|error|Maximum resident|Elapsed' || true
test -s "$OUT" && { sha256sum "$OUT"; date -u +%FT%TZ; }
