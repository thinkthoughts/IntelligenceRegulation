# RPI-RLT-VR-007 — Independent replay and author-facing review

> **Independent external review.** Written for the fork `thinkthoughts/IntelligenceRegulation` by an outside
> reviewer working with Claude (Anthropic). Victor Rielly, the author of IntelligenceRegulation, has had no part
> in it and has neither reviewed nor endorsed it. Index: [../README.md](../README.md).

2026-11-14, final version 2026-11-15 · thinkthoughts · reviewed commit `eee3eb5717dea88d0fc48dc00f6aef389d52af3a`
· built on review commit `5a7c536b107123303fa2fb854bace9bedb4c7525` · second-machine evidence from commit
`51480d81d8ac99f1152b3544af18f7283c6bf8ab`

> **Revision note.** The first version of this report (commit `886387f`) prepared the second-machine runs and marked
> their rows "awaited". This final version reads the logs the fork owner committed in `51480d8` and replaces those
> rows. Sections 2.2 to 2.6, 4, 5, 7 and 8 changed; the comparison of section 3 is unchanged. The first version stays
> in the branch history.

## 1. Summary

1. **Every module of Victor's Lean library passes Lean's kernel replay, one module at a time.** On the second
   machine, `leanchecker` accepted all 496 modules: 466 on the first pass, one more on a retry with a higher memory
   limit, and the 29 check modules once they were built (section 2.2).
2. **An independent kernel accepts all four production-readiness top theorems.** nanoda, a Lean kernel written
   separately in Rust, checks each top theorem with everything it depends on: 36,463 to 37,344 declarations per
   theorem, most of them shared Mathlib declarations. It refuses each one when `Classical.choice` is withheld, so
   all four depend on `propext`, `Classical.choice` and `Quot.sound` and on no other axiom. nanoda needed a
   256 MiB stack per checking worker; its 32 MiB default overflowed (section 2.3). Here it also accepted the
   block-level knowledge-soundness theorem and the F12 fix.
3. **Two of Victor's Rust exporters regenerated committed Lean fixtures,** and a check module that had needed
   fixtures from outside the public tree compiled with them and passed: 54 functional checks, 0 failed (section 2.6).
4. **The four top theorems prove the same conclusion under different hypothesis sets.** Each parallel theorem
   discharges the same 15 endpoint hypotheses, exchanges one or two others for conditions on the verifier's
   parameters, and carries the older, coarser form of eight stage obligations. Counted as open obligations: 24 on
   the audited theorem and on the L55 theorem, 25 on the L52 and L56 theorems (section 3). Fewer hypotheses on a line
   are a different statement, and none of the four is stronger than another by count alone.
5. **The L55 theorem's additions are classified.** It adds 33 hypotheses (VR-006 said 34, counting the data binder
   `hw`): 20 bookkeeping, 5 public instance data, and 8 open, the 8 being the coarse stage obligations (section 3.2).
6. **The author-facing summary is updated** ([`../SUMMARY-FOR-VICTOR.md`](../SUMMARY-FOR-VICTOR.md)). It leads
   with Victor's objectives and results, and keeps the chronology and attribution reading in its own section.

**What the kernel checks establish, and what they leave open.** Two independent kernels now confirm that each top
theorem's proof is a valid proof of its statement, under the three standard axioms. Each statement is an
implication: if its hypotheses hold, `ProductionReadyL` holds for a verifier given as parameters. The 31 open
obligations of the audited theorem, and a concrete Shieldstral instance, are outside what any kernel check can
supply. The repository's rule D63 keeps every profile out of production until its statements are proved, and these
findings are consistent with that rule being in force.

## 2. Verification

### 2.1 The replay script, inspected before use

[`../scripts/r1_replay_modules.py`](../scripts/r1_replay_modules.py) replaces VR-006's shell script, which ran
the root module last (the whole-library form that ran out of memory), had no memory guard and wrote paths as they
were. Its behaviour, listed in the script's help text:

| Property | Behaviour |
|---|---|
| Concurrency | one `lake env leanchecker <module>` at a time |
| Memory guard | sums the resident memory of the checker's process group once a second; kills the group above `--max-rss-mb` (default 9,000) and records `memory-limit` |
| Time guard | kills after `--timeout` seconds (default 1,800) and records `timeout` |
| Root module | skipped unless `--include-root` |
| Resumption | a module already recorded is skipped |
| Output | only under `--out`; home path and host name replaced by `~` and `<host>` |

Trial on this machine ([`../results/R7-local-trial/`](../results/R7-local-trial/README.md)):

| Run | Result |
|---|---|
| `ZK60Formal.Statements` | ok, 399 s, peak 3,455 MB |
| `ZK60Formal.SoundMProduct` | ok, 7 s, peak 3,280 MB |
| an uncompiled module, an unknown name | both recorded `not-compiled` |
| memory guard at 200 MB | killed at 914 MB, recorded `memory-limit` |
| time guard at 1 s | killed, recorded `timeout` |
| a checker that fails (`false`) | recorded `failed`, failure log written |
| a second invocation | nothing re-run |

### 2.2 Per-module replay on the VPS

Files: [`../results/R7-vps/`](../results/R7-vps/). Machine: the 4-core, 16 GB Linux server of VR-006, Lean 4.34.1.
Checked by [`../scripts/r7_vps_check.py`](../scripts/r7_vps_check.py) (section 2.7).

| Pass | Modules | Limits | Result | File |
|---|---|---|---|---|
| First | all 496 `.lean` files under `formal/ZK60Formal` | 12,000 MB, 3,600 s per module | 466 ok; 1 `memory-limit`; 29 `not-compiled` | `06-replay-per-module.tsv`, `06-replay-summary.txt` |
| Retry | `ZK60Formal.ProtocolClassifyUEp` | 14,000 MB | ok, 116 s, peak 12,239 MB | `retry/` |
| Check modules | the 29 modules outside the library's default target, after building them | 14,000 MB | 29 ok; largest peak 3,983 MB, longest 13 s | `check-replay/`, `check-modules.txt` |
| **All** | **496** | | **496 ok** | |

Reconciliation, module by module:

- **The memory-limit module.** On the first pass the guard killed `ProtocolClassifyUEp` after 277 s at 12,025 MB,
  just above its 12,000 MB limit (`06-replay-failures.log`). Under a 14,000 MB limit it finished with exit 0 at a
  peak of 12,239 MB. The guard did what it was built to do; the module needs about 12 GB to replay.
- **The 29 check modules.** These import modules that define `main` and are kept out of the library's root, so
  `lake build` leaves them unbuilt and the first pass recorded them `not-compiled`. They are the same 29 that VR-004
  counted outside the default target. Once built, all 29 passed. Of their builds, the log of
  `ZK60Formal.CoverW16MCheck` is committed (section 2.6); the other 28 builds are recorded only by their passing
  replay.
- **The largest modules.** `RunExtractClassify`, which ran out of memory on the reviewer's 6 GiB machine in VR-004,
  replays at a peak of 10,567 MB. The run-level module `RunStgAlgTopR` passes on this pass too, as it did singly in
  VR-006. The median peak of the 466 first-pass modules is 3,813 MB, mostly the loading of the imported files.

With VR-004 (358 modules accepted on the reviewer's machine), this is the second complete replay of the compiled
modules that the reviewer's machine could reach, and the first of the whole library.

### 2.3 nanoda

| Question | Finding | Source |
|---|---|---|
| What nanoda reads | export files produced by lean4export; it is configured by a JSON file naming the export, the permitted axioms and whether an unpermitted axiom is a hard error | nanoda_lib README |
| Which format version | nanoda_lib at `0da9f98` (0.4.32, 2026-11-07) accepts export format 3.1.0 and refuses anything outside 3.1.0 to 3.2.0 | `src/parser.rs`, `check_semver` |
| Which exporter | lean4export at `df81913` (2026-10-14) writes format 3.1.0; its own toolchain pin is a later Lean (4.36.0-rc1) | `Export.lean`, `lean-toolchain` |
| Compatible with Lean 4.34.1 | yes: lean4export built with Lean 4.34.1 (6 jobs, exit 0); its exports carry `"lean":{"version":"4.34.1"}` and are accepted by nanoda | this review, `results/R7-nanoda/*.log` |
| Others doing the same | an external checker project reports producing its inputs with lean4export master built with Lean 4.34.1, the way the Lean Kernel Arena makes them; the Arena lists nanoda at commit `0da9f98` | the Pestka README; the Arena's nanoda page |

The Lean Kernel Arena reports nanoda at that commit as rejecting all 84 of its soundness tests and accepting a
full Mathlib export in about 15 minutes at 6.0 GB. The Arena also notes that its nanoda integration reports
every failure as a rejection.

Results here ([`../results/R7-nanoda/`](../results/R7-nanoda/)), each run with exactly `propext`,
`Classical.choice` and `Quot.sound` permitted and any other axiom a hard error:

| Theorem | Export | nanoda | Control (without `Classical.choice`) |
|---|---|---|---|
| `ZK60.Exec.Block.Join.R13H.block_knowledge_r13_shield` | 5,211,138 lines, SHA-256 `b9828534…` | exit 0, 38,128 declarations, 248 s, peak 1,047 MB | refused, exit 1 |
| `ZK60.Sound.mproduct_sound_shift` (the F12 fix) | 1,423,236 lines, `52ec54af…` | exit 0, 17,840 declarations, 5 s, 146 MB | refused, exit 1 |
| `ZK60.trivialArith_circuitIff` | 664 lines | exit 0, 36 declarations | accepted: the theorem depends on no axiom |

The control shows the axiom check is live: the same export is refused once `Classical.choice` is withheld. Each
run also prints "Unable to print axioms", a pretty-printer message; the type-checking verdict is separate from it.
The export files are hundreds of megabytes and are kept outside the repository; their hashes are in the result
files.

What this establishes for these three: a kernel implemented separately from Lean's accepts every declaration
they depend on, including Mathlib's, under the three standard axioms.

**The four top theorems, on the second machine** (`results/R7-vps/top-*.log`, `top-*-stack256*.log`):

| Top theorem | Lane | Export (lines) | First run, nanoda's default stack | Run with a 256 MiB worker stack | Control |
|---|---|---|---|---|---|
| `stgAlg_productionReadyL_epP_exec_real` | L57 | 4,751,633 | stack overflow, exit -6 | 36,764 declarations, zero typechecker errors | `Classical.choice` refused |
| `cb_productionReadyL_epP_codeF` | L55 | 4,814,746 | stack overflow, exit -6 | 36,535 declarations, zero typechecker errors | refused |
| `eb_productionReadyL_epP_codeT` | L52 | 4,657,454 | stack overflow, exit -6 | 36,463 declarations, zero typechecker errors | refused |
| `bnd_productionReadyL_epP_args` | L56 | 4,783,448 | stack overflow, exit -6 | 37,344 declarations, zero typechecker errors | refused |

- **Stack size.** nanoda's configuration field `stack_size_bytes` sets the stack of each checking worker and
  defaults to 32 MiB (nanoda_lib README; `src/util.rs`). The first runs overflowed it. A trial at 64 MiB on the top
  theorem overflowed as well (`top-real-stack64.log`). At 268,435,456 bytes (256 MiB) all four passed. A stack
  overflow is a resource limit of the checker process: nanoda aborts before giving a verdict. The successful runs
  are the verdicts. `r7-nanoda.sh` now sets 256 MiB by default and logs the value (`R7_STACK_BYTES`).
- **The declaration counts overlap.** Each count is the theorem plus its transitive dependencies, and most of them
  (Mathlib, Lean core, the shared library modules) are common to all four. The counts measure export size; they are
  no measure of how much each theorem proves.
- **Axioms.** Every run permitted exactly `propext`, `Classical.choice` and `Quot.sound` and treated any other
  axiom as a hard error, and every control was refused at `Classical.choice`. This settles, by a second route, the
  axioms of the L52 and L56 top theorems, which the VR-006 `#print axioms` log did not cover.
- **Diagnostics.** Each successful run reports zero typechecker errors and one pretty-printer diagnostic, "Unable to
  print axioms". The pretty-printer formats the axiom list for display; the type-checking verdict is separate from
  it.
- **The export files** (about 240 MB each) stay outside the repository. Their SHA-256 values are in the result
  files of the first runs. The 256 MiB logs hold nanoda's output only; `top-real-stack256-summary.txt` records the
  pins and the stack setting, and the logs do not restate which export each run read.

### 2.4 The whole-library memory failure

The VR-006 log of the whole-library `leanchecker ZK60Formal` run is empty, and the second-machine commit adds no
kernel record of the kill (step 4 of the instructions produced no committed file). The memory failure therefore
stays the fork owner's report, with no log behind it. It matters less now: the per-module replay of section 2.2
covers every module the whole-library run would have covered, within 12.3 GB per module.

### 2.5 Earlier evidence intact

`r6_check.py` passes all eight checks, including the SHA-256 of all six VR-006 VPS files and of the Lean inventory.
The 32 files of the new manifest `results/R7-vps/PUBLIC-SHA256SUMS` all verify (re-run by this review). No file
under `results/R1-lean`, `R1-lean-vps`, `R2-rust`, `R5-premises`, `R6-reconciliation` or `R7-vps` was changed by
this revision, and reports VR-003 to VR-006 are unchanged. The new logs contain no host name or home path. VR-006
question 24 (host name and home path in the VR-006 logs) is still open.

### 2.6 Rust exporters and the check module `CoverW16MCheck`

Victor's Lean checks of a real W16R2 development receipt read two exports produced by his Rust prover: the L9
corpus and fork frame, and the L10 corpus. The second machine reran both exporters from `eee3eb57`
(`l9-export-public.log`, `l10-export-public.log`; each a one-test `cargo test --release` run of Hashline, 1 passed).

| Export | Log reports | The public tree holds | Status |
|---|---|---|---|
| L9 corpus | 81,130 B, 23 slots | `results/zk60_lean_l9_20261107/corpus.txt`, 81,130 B, SHA-256 `bd6b6df6…` | same length (checked by this review); byte identity reported by the fork owner |
| L9 fork frame | 14,258,216 B | absent (a large file kept out of the public tree) | length reported; no committed copy to compare |
| L10 corpus | 28 records, 191,941,509 B | its SHA-256, `0eedc99a…`, and length, 191,941,509, in `results/zk60_lean_l10_20261107/corpus.sha256` | same length (checked); SHA-256 match reported by the fork owner |

The committed logs record lengths. The identity and checksum comparisons were made on the second machine and are
not in a committed log; a one-line `sha256sum` of the regenerated files, committed, would make them checkable
(section 7). The generated files themselves were left out of the repository, as the manifest's note says.

The L9 run also exercised the verifier against twelve tampered copies of the frame. The honest frame verified, and
each tampered copy was refused with a specific reason: a byte short, a byte long, wrong magic, a different run's
binding, a wrong fork index, a wrong start tag, a changed commitment root, non-canonical field words (two kinds),
a wrong mask column index, a changed round sum, and a wrong end tag.

`ZK60Formal.CoverW16MCheck` (Victor's lane L23) compares the functionals and weights of the Lean block verifier with
the code's, on that same receipt; it needs both corpora and the frame. VR-004 left it unbuilt. With the regenerated
fixtures it built (3,472 jobs, exit 0) and its evaluation printed `MFunCheck: 54 checks, 0 failed`
(`cover-w16m-build.log`); its replay passed in the check-module pass. The log does not show which file paths the
environment variables pointed to.

### 2.7 Checks of the second-machine evidence

[`../scripts/r7_vps_check.py`](../scripts/r7_vps_check.py), run on the committed evidence: 5 of 5 pass.

| Check | What it guards |
|---|---|
| V1 manifest | the 32 files have their recorded SHA-256 |
| V2 coverage | the first pass lists exactly the 496 `.lean` files of `formal/ZK60Formal` at `eee3eb57` |
| V3 reconciled | each module ends `ok`; the retry and check-module passes are exactly the first pass's memory-limit and not-compiled modules |
| V4 nanoda | each top theorem: a success line, a refused control, an export with exit 0 |
| V5 verdicts-only | each successful run has exactly one pretty-printer diagnostic, "Unable to print axioms" |

One positive and four adversarial tests (an edited log, a memory-limit module without retry, a control that
accepts, a nanoda run with errors) are added to `scripts/r7-tests/run-tests.sh`; the suite now passes 17 of 17.

## 3. The four top theorems

Files: [`../results/R7-comparison/`](../results/R7-comparison/): `four-theorems.tsv` (one row per binder of any of
the four, its presence on each, category and source), `comparison-summary.txt`, `tests.log`. Data:
[`../scripts/r7_added.json`](../scripts/r7_added.json), [`../scripts/r7_exchange.json`](../scripts/r7_exchange.json).
The raw 179-key Lean inventory and the 173-key normalized classification are unchanged.

### 3.1 Same conclusion, different hypotheses

All four conclude `ProductionReadyL … (classifyProtocolUExecP … 768) … εcTarget εsTarget εsTarget εzkTarget`,
word for word (check C1).

| | Audited (L57) | `eb_…_codeT` (L52) | `cb_…_codeF` (L55) | `bnd_…_args` (L56) |
|---|---|---|---|---|
| Named binders | 179 | 145 | 163 | 146 |
| Audited hypotheses it lacks | | 32 | 33 | 34 |
| … discharged | | 15 | 15 | 15 |
| … exchanged | | 1 (`hopX`) | 2 (`hopX`, `hW`) | 2 (`hopX`, `hLb`) |
| … open, another form stands here | | 8 | 8 | 9 (adds `hsl_blk` → `hsl_args`) |
| … conditions of the audited theorem's finer stage forms | | 8 | 8 | 8 |
| Hypotheses it adds | | 15 | 33 | 18 |
| Open obligations it carries | 24 | 25 | 24 | 25 |

Meaning of the buckets:

- **Discharged** (15 on every line): `hTenc`, `hTaA`, `hTaB`, `hUc`, `hXc`, `hp1`, `hp2`, `hF`, `hw0`, `hβLR`,
  `hTe`, `hTQ`, `hβJ`, `hwin`, `hBal`. The three lines fix the endpoint test (`T := ebT`, `pr := gP`) and prove
  these facts; the objects they mention never appear in the conclusion, and nothing stands in their place.
- **Exchanged**: a hypothesis about every adversary is replaced by conditions on the verifier's parameters.
  - `hopX` on L52 and L56: part 0 is proved, at the price of `hRn`, `hgX0`, `hnX0`, `hXep`, `hfitX`, `hRr`; parts 1
    onward remain as the open `hopX1`.
  - `hopX` on L55: parts 1 onward are proved too, at the price of a further 15 boundary conditions (`hXk`, `hOX`,
    `hfitXk`, `hfitXo`, `hwXk`, `hmXk`, `hwX0`, `hmX0`, `hwXo`, `hgXk`, `hnXk`, `hgX1`, `hnX1`, `hgXo`, `hnXo`).
  - `hW` on L55: the verdict link becomes `hchk`, `hinc`, `houtc`, `hLb1`. `hchk` holds only with the statement
    check that carries the code's verdict refusal (`check := vdChk check0`, finding L55-1).
  - `hLb` on L56: `Lb ≤ 26` follows from `hPk`, which says the block profiles are the Shieldstral run's.
- **Open, another form stands here**: the audited theorem's eight refined stage obligations (`hTrI`, `hTrO`,
  `hDI_stg`, `hDO_stg`, `hLI_stg`, `hLO_stg`, `hdinS`, `hdoutS`) stand on the other lines as the eight earlier
  stage hypotheses (`hsl_stg`, `hR0_stg`, `hR1_stg`, `hH0_stg`, `hH1_stg`, `hLU_stg`, `hdin`, `hdout`). These
  are the same obligations at a coarser grain.
- **Finer-form conditions**: `hIOI`, `hIOO`, `hNin`, `hNout`, `hb0`, `hbL`, `hPin`, `hPout` come with the refined
  stage forms; the coarser lines need none of them.

So the L55 theorem has the most proved and the most bookkeeping: it alone discharges every closing opening. The
audited L57 theorem has the most refined stage obligations. The repository's finding L56-2 names the missing
object: one theorem with L55's closing discharges and L57's stage refinement. By the counts above it would carry 24
open obligations. That figure is an inference from names; no such theorem exists yet.

### 3.2 The hypotheses the L55 theorem adds

36 binders in all. Three are data (`hw`, the code's header reader; `Vi`, the constant IN-C verifier; `pXk`, each
block's boundary opening record). Lean's own list of the theorem's hypotheses in the VPS log agrees: 87 named
propositions plus one instance, with `hw`, `Vi` and `pXk` absent (check C2).

| Category | Hypotheses | Status in Victor's lane document (L55 §5.1, L52 §5.1) |
|---|---|---|
| Open (8) | `hsl_stg`, `hR0_stg`, `hR1_stg`, `hH0_stg`, `hH1_stg`, `hLU_stg`, `hdin`, `hdout` | the coarse stage obligations, refined on the L57 line |
| Bookkeeping (20) | `hRn`; `hinc`, `houtc` | YES by definition; `rfl` at the real families |
| | `hchk` | YES with `check := vdChk check0` (`vdChk_le` PROVED); that the accepted inputs are the code's is ARGUED |
| | `hfitX`, `hfitXk`, `hfitXo` | YES: 8 · 38 = 304 ≤ 2^20 |
| | `hwXk`, `hmXk`, `hwX0`, `hmX0`, `hwXo` | YES, ARGUED: definitional at the builders |
| | `hgX0`, `hnX0`, `hgXk`, `hnXk`, `hgX1`, `hnX1`, `hgXo`, `hnXo` | a CHOICE of `base` |
| Public instance data (5) | `hXep`, `hRr`, `hLb1`, `hXk`, `hOX` | geometry CHECKED; `cbBndPcs_r13` PROVED; 26 blocks |

The full per-name record, with the L52 and L56 additions (`hopX1` open; `hgXB` bookkeeping; `hPk` instance data;
`hsl_args` open), is `scripts/r7_added.json` and the `four-theorems.tsv` table.

### 3.3 Checks and tests

[`../scripts/r7_compare.py`](../scripts/r7_compare.py): eight checks, all pass.

| Check | What it guards |
|---|---|
| C1 same-conclusion | the four conclusions are identical text |
| C2 lean-agrees | the L55 theorem's hypotheses, as Lean lists them, are exactly those the review treats as hypotheses |
| C3 added-covered | every added binder is classified, and nothing else is |
| C4 exchange-true | each discharge or exchange names real binders, the right lines and stand-ins present there, and no open obligation |
| C5 open-accounted | each open obligation is on every line, or replaced there by named stand-ins |
| C6 relation-sound | "discharged" has nothing in its place; "exchanged" has something in its place |
| C7 lacks-partitioned | each lacked hypothesis is in exactly one bucket |
| C8 discharge-sourced | each "discharged" key names its supplier |

[`../scripts/r7-tests/run-tests.sh`](../scripts/r7-tests/run-tests.sh): the 12 comparison tests pass, within the
suite's 17 (`tests.log`): one positive test and ten adversarial edits to scratch copies, each caught (an unclassified addition, a phantom name, a
hypothesis labelled as data and the reverse, an exchange recorded as a discharge, a stand-in absent from its line,
a wrong line list, an open obligation dropped without stand-in, an open obligation relabelled discharged, a name
in two buckets), plus the replay script's refusal to run outside the repository root.

Two of these tests found faults in the reviewer's own first draft, which were fixed before publication: the
exchange rule had wrongly required every exchanged key to be a VR-006 "discharged" key (`hLb` is instance data),
and relabelling an open obligation as discharged went unnoticed until check C8 was added.

The checks compare names and statement text. They show what each theorem assumes; they read no proof.

## 4. Changes to earlier reports

VR-003 to VR-006 stay as published.

| Earlier statement | Correction |
|---|---|
| VR-006 §6.1: hypotheses added by the L52, L55, L56 theorems: 16, 34, 19 | 15, 33, 18 hypotheses; the earlier figures counted the data binder `hw` |
| VR-006 §6.1: those lines "lack" the eight refined stage hypotheses | they carry the same obligations in the earlier form; and eight further conditions (`hIOI` … `hPout`) belong to the refined form itself |
| VR-006 §2: "a separate kernel implementation has yet to be run on any part of the library" | nanoda accepts all four top theorems and three component and block theorems, with their dependencies |
| VR-005 §1, VR-006 §2: nanoda named as open | done (section 2.3) |
| VR-006 §2: per-module replay of the other run-level modules open | done: 496 of 496 (section 2.2) |
| VR-004 §2.1: 138 modules unbuilt on the reviewer's machine | all built and replayed on the second machine |
| VR-007, first version: nanoda on the top theorems "awaited" | done, with a 256 MiB worker stack |

## 5. Roadmap

VR-003's roadmap and its FlashProve comparison stand.

| # | State after VR-007 |
|---|---|
| R1 | Done. Complete build; per-module `leanchecker` over all 496 modules; nanoda on all four top theorems and three component and block theorems; axioms of all four top theorems limited to the standard three |
| R5 | Done for the four top theorems: inventory, normalized classification, comparison, each difference checked |
| R2 | Done for the two core libraries; the L9 and L10 exporters added on the second machine |
| R3, R4 | Held, as agreed, for the next research phase |
| R6 to R9 | Unchanged |

## 6. Questions

Questions 1 to 24 of the earlier reports stand; the summary for Victor groups them. Added:

25. (For Victor) Is a theorem combining L55's closing discharges with L57's stage refinement the planned next top
    theorem?
26. (For the fork owner) Should the VR-006 VPS logs be re-committed with the host name and home path replaced? That
    would change their hashes, so it would need a new, separately hashed copy beside the originals.

## 7. Recommended next checkpoint

1. Review of the author-facing summary by the fork owner, then a decision on contacting Victor.
2. Two small evidence additions, if wanted before contact: a committed `sha256sum` of the regenerated L9 and L10
   files beside the committed checksums, and the build logs of the other 28 check modules.
3. The research obligations, in Victor's hands or with his agreement: the 31 open keys (section 3; VR-006 §4.1),
   the concrete Shieldstral instance, and the merged top theorem of finding L56-2.

R3, R4 and any Hashline work wait for approval.

## 8. Scope and limits

- Additions are under `evidence/` only. No file of Victor's was changed; the fork's `main` is unchanged; no
  upstream issue, pull request or contact was made.
- The second-machine runs were made by the fork owner; this review read and checked their committed logs and
  hashes and repeated no experiment. Section 2.6's identity and checksum matches are the fork owner's report.
- nanoda on the three component and block theorems ran on the reviewer's machine, on modules compiled there.
- Section 3 rests on binder names and statement text read from source, with Lean's list as a cross-check for the
  L55 theorem. Status words in the classification are Victor's, from his lane documents.
- Kernel checks establish that proofs are valid proofs of their statements. They establish none of the statements'
  hypotheses.
- External tool facts (nanoda's accepted format and stack setting, the Arena's results) were read from those
  projects' public pages and source at the commits named.
