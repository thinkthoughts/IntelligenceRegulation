# VR-007 runs on the second machine (VPS): instructions, results awaited

> **Independent external review.** Part of the review described in [../../README.md](../../README.md). Victor
> Rielly has had no part in it.

**Update, 2026-11-15 (commit `51480d81`): the results are here.** The fork owner ran steps 0 to 3 and committed the
logs with a manifest, `PUBLIC-SHA256SUMS` (32 files). VR-007 §2.2 to §2.7 read them; `evidence/scripts/r7_vps_check.py`
checks them. Two departures from the steps below, both recorded in the logs: nanoda needed `stack_size_bytes` of
268,435,456 (256 MiB) per checking worker, where its 32 MiB default and 64 MiB overflowed (`r7-nanoda.sh` now sets
256 MiB by default); and the 29 check modules were built and replayed in a pass of their own (`check-replay/`).
Step 4, the out-of-memory diagnostic, produced no committed file. The text below is the earlier note, kept as
written.

**Status on 2026-11-14, before that commit: this folder holds instructions only.** The reviewer's own machine (2 cores, about 6 GiB per
job) can compile and check the component and block modules, and VR-007 reports those results. The run-level
modules need the VPS. Everything below runs there, writes only under `evidence/`, and changes no file of the
library.

Expected time on a 4-core, 16 GB machine: per-module replay several hours (the slowest module seen so far took
399 s here); nanoda on the top theorem roughly 15 to 60 minutes (measured here: 248 s for the block theorem, whose
export is 266 MB). These are estimates.

## 0. Start from the review branch, with the build in place

```bash
cd IntelligenceRegulation
git fetch origin formalize-now/intelligenceregulation-review
git checkout formalize-now/intelligenceregulation-review
git diff --stat eee3eb57 -- formal/                 # must print nothing: formal/ is Victor's tree as published
(cd evidence/results/R1-lean-vps && sha256sum -c SHA256SUMS)   # the VR-006 evidence, unchanged
(cd formal && lake build 2>&1 | tail -1)             # should report the existing build, nothing rebuilt
D=evidence/results/R7-vps
```

## 1. Look at the replay script before running it

```bash
python3 evidence/scripts/r1_replay_modules.py --help          # states every behaviour, guard and output file
python3 evidence/scripts/r1_replay_modules.py --out $D --limit 3   # trial: three modules, then stop
cat $D/06-replay-per-module.tsv
```

The script runs one `lake env leanchecker <module>` at a time, kills a module whose process group passes
`--max-rss-mb` (default 9000) or `--timeout` seconds (default 1800), records each module once, resumes where it
stopped, skips the whole-library root module unless asked, and replaces the home path and host name in what it
writes.

## 2. Replay every module, one per process

```bash
nohup python3 evidence/scripts/r1_replay_modules.py --out $D --max-rss-mb 12000 --timeout 3600 \
      > $D/06-replay-console.log 2>&1 &
tail -f $D/06-replay-console.log          # Ctrl-C stops watching; the run continues
```

When it ends, `06-replay-summary.txt` gives the counts by status, the largest peak memory and the slowest modules.
Modules marked `memory-limit` or `timeout` can be retried alone with a larger limit:
`python3 evidence/scripts/r1_replay_modules.py --out $D-retry --modules <file with their names> --max-rss-mb 14000`.

## 3. nanoda on the top theorem (an independent kernel)

The pinned pair was established in VR-007 §2.3: lean4export `df81913` built with Lean 4.34.1 writes export format
3.1.0, and nanoda_lib `0da9f98` (0.4.32) accepts 3.1.0 up to 3.2.0. The script builds both outside the repository
(in `~/.cache/r7-nanoda`, needs `cargo`) and keeps the large export files there.

```bash
evidence/scripts/r7-nanoda.sh top-real ZK60Formal.RunStgAlgTopR \
  ZK60.ProtocolClassify.RunShapeP.stgAlg_productionReadyL_epP_exec_real $D
# optional, same pattern, for the parallel top theorems:
evidence/scripts/r7-nanoda.sh top-cb  ZK60Formal.RunCloseBTopF ZK60.ProtocolClassify.RunShapeP.cb_productionReadyL_epP_codeF $D
evidence/scripts/r7-nanoda.sh top-eb  ZK60Formal.RunEpBTopT    ZK60.ProtocolClassify.RunShapeP.eb_productionReadyL_epP_codeT $D
evidence/scripts/r7-nanoda.sh top-bnd ZK60Formal.RunBndTop     ZK60.ProtocolClassify.RunShapeP.bnd_productionReadyL_epP_args $D
```

Each writes `<tag>.log` and `<tag>.result.tsv`.

The axioms of the two top theorems the VR-006 log did not cover, through the premise tool (about a minute each):

```bash
evidence/scripts/r5-premises.sh ZK60Formal.RunEpBTopT ZK60.ProtocolClassify.RunShapeP.eb_productionReadyL_epP_codeT $D/inventory-lean-eb.json
evidence/scripts/r5-premises.sh ZK60Formal.RunBndTop  ZK60.ProtocolClassify.RunShapeP.bnd_productionReadyL_epP_args  $D/inventory-lean-bnd.json
python3 -c "import json,sys; [print(p, json.load(open(p))['axioms']) for p in sys.argv[1:]]" $D/inventory-lean-eb.json $D/inventory-lean-bnd.json
``` A pass is `nanoda_exit` 0 together with `control_exit` 1: the
control removes `Classical.choice` from the permitted axioms and must be refused.

## 4. The whole-library replay's memory failure: a sanitized diagnostic

The VR-006 log `04-leanchecker.log` is empty. If the kernel recorded the kill, the record is in its log. This step
copies that record if it exists and writes a plain statement if it does not; it creates no checker output.

```bash
{ echo "# kernel records of memory kills on this machine, sanitized (independent external review, VR-007)"
  date -u +%FT%TZ; uname -srm
  echo "## journalctl -k, lines mentioning an out-of-memory kill"
  journalctl -k --no-pager 2>/dev/null | grep -iE 'out of memory|oom-kill|oom_reaper|Killed process' || echo "(none found by journalctl)"
  echo "## dmesg, the same"
  dmesg -T 2>/dev/null | grep -iE 'out of memory|oom-kill|oom_reaper|Killed process' || echo "(none found by dmesg, or dmesg needs root)"
} | sed -e "s|$HOME|~|g" -e "s|$(hostname)|<host>|g" > $D/07-oom-diagnostic.txt
cat $D/07-oom-diagnostic.txt
```

If the kill happened before the machine's last restart, the kernel record may be gone; the file then says so.

## 5. Hashes, a privacy check, commit and push

```bash
(cd $D && sha256sum $(ls | grep -v -e '^README.md$' -e '^SHA256SUMS$') > SHA256SUMS)
grep -rIl -e "$(hostname)" -e "$HOME" $D && echo "REMOVE these before committing" || echo "no host name or home path"
git add $D
git commit -m "evidence: VR-007 VPS runs (per-module leanchecker, nanoda, OOM diagnostic)"
git push origin formalize-now/intelligenceregulation-review
```

Read the logs once for anything else private before pushing; the branch is public.
