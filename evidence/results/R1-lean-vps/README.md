# R1 on a larger machine (VPS): results as reported, logs awaited

> **Independent external review.** Part of the review described in [../../README.md](../../README.md). Victor
> Rielly has had no part in it.

**Update, 2026-11-14 (commit `41f67ade`): the logs are here.** The fork owner committed them with hashes; report
VR-006 §2 reads them. The whole-library replay left an empty log (`04-leanchecker.log`, 0 bytes), so its memory
failure stays a reported result. The text below is the earlier note, kept as written.

**Status on 2026-11-14, before that commit: this folder holds no logs yet.** The figures below were reported by the fork owner, who
ran the commands on a separate Linux VPS. The author of reports VR-003 to VR-005 has seen the figures only, and
has inspected none of the VPS logs. Each figure stays labelled "reported" until its log is in this folder.

| Item | Reported result |
|---|---|
| Machine | Ubuntu Linux, 15 GiB RAM, 8 GiB swap; Lean 4.34.1 |
| `lake build` | 3,840 jobs completed, exit 0 |
| Axiom and premise inspection (`evidence/scripts/r1_axioms_premises.lean`) | exit 0 |
| Axioms of the central theorem | `propext`, `Classical.choice`, `Quot.sound` |
| `leanchecker ZK60Formal.RunStgAlgTopR` | exit 0; peak memory about 3.10 GiB |
| `leanchecker ZK60Formal` (whole library in one process) | killed for memory, exit 137 |

## Placing the logs here

On the VPS, in the clone that produced the results (commit `eee3eb57`, with this branch checked out or its
`evidence/` folder copied in):

```bash
cd IntelligenceRegulation
git fetch origin formalize-now/intelligenceregulation-review
git checkout formalize-now/intelligenceregulation-review          # formal/ is identical to eee3eb57 on this branch
D=evidence/results/R1-lean-vps
# 1. copy the logs as they were written, without editing them; suggested names:
#    01-lake-build.log   02-axioms-premises.log   03-leanchecker-RunStgAlgTopR.log   04-leanchecker-whole-library.log
cp /path/to/your/logs/*.log "$D"/
# 2. record the machine and toolchain
{ date -u +%FT%TZ; uname -srm; nproc; free -m; swapon --show; (cd formal && lake --version && lake env lean --version); git rev-parse HEAD; } > "$D/environment.txt"
# 3. the premise inventory of the top theorem, straight from Lean (about one minute once the build exists)
evidence/scripts/r5-premises.sh 2>&1 | tee evidence/results/R5-premises/inventory-lean.log
python3 evidence/scripts/r5_check_classification.py --lean evidence/results/R5-premises/inventory-lean.json \
        evidence/results/R5-premises/classification.tsv | tee evidence/results/R5-premises/classification-check-lean.log
# 4. hashes, then commit and push
(cd "$D" && sha256sum *.log environment.txt > SHA256SUMS)
git add "$D" evidence/results/R5-premises/inventory-lean.json evidence/results/R5-premises/inventory-lean.log \
        evidence/results/R5-premises/classification-check-lean.log
git commit -m "evidence: VPS logs for R1 and the Lean-generated premise inventory"
git push origin formalize-now/intelligenceregulation-review
```

Before committing, read the logs once for anything private (host names, user names, IP addresses, tokens); the
branch is public. Step 3's check is expected to report differences the first time: it lists every hypothesis that
Lean reports and the interim classification lacks. Those lines are the input for the next revision of the
classification.

If a whole-library replay is wanted on that machine, run the checker one module at a time, as VR-004 did
(`lake env leanchecker <module>` for each line of a module list); the single-process form needs more memory than
the per-module form.
