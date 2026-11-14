# RPI-RLT-VR-004 — Review publication and independent reproduction (R1, R2)

> **Independent external review.** Written for the fork `thinkthoughts/IntelligenceRegulation` by an outside
> reviewer working with Claude (Anthropic). Victor Rielly, the author of IntelligenceRegulation, has had no part
> in it and has neither reviewed nor endorsed it. Index: [../README.md](../README.md).

2026-11-14 · thinkthoughts · reviewed commit `eee3eb5717dea88d0fc48dc00f6aef389d52af3a`

This report records two reproduction steps from the VR-003 roadmap, run on one small cloud machine, and the
roadmap checkpoint that follows from them. Every command and log is under `evidence/scripts/` and
`evidence/results/`.

## 1. Summary

| Step | Outcome on the reviewer's machine | Reach |
|---|---|---|
| R1 Lean build | 358 of 496 Lean modules compiled with the declared toolchain; one module, `ZK60Formal.RunExtractClassify`, exceeded the machine's 6 GiB memory limit on every attempt, and the 108 modules that import it were therefore left unbuilt | partial |
| R1 axioms | 13 named component and block theorems depend on `propext`, `Classical.choice`, `Quot.sound` only; `trivialArith_circuitIff` depends on zero axioms | component and block level |
| R1 kernel replay | `leanchecker` (shipped with Lean 4.34.1) accepted all 358 compiled modules | every compiled module |
| R1 central theorems | the run-level `…productionReadyL…` theorems sit in the unbuilt part; their axioms and premises were read from source text only | open on this machine |
| R2 `zkp-core` | 83 passed, 0 failed, 2 ignored (benchmarks) | complete |
| R2 Hashline library | 978 passed, 90 ignored, 5 failed, 0 unfinished, of 1,073; each failure traced to the environment (section 3.2) | complete; 4 of the 5 pass once the environment is adjusted, 1 needs a fixture outside the public tree |
| R2 F12 control | 8 of 8 F12 tests pass, the eighth once its four archived receipts are placed where it reads them | complete |
| R2 demo | `scripts/zk60_p1_demo.py`: passed, 9 steps, 6 of 6 rejection controls refused | complete (a component demo, by its own description) |

**What this establishes.** The Lean modules that compiled here contain real, kernel-checked proofs under the three
standard axioms, confirmed by a second pass of the kernel over the compiled files. The Rust verifier's tests,
including the F12 forgery control, behave on an unrelated x86-64 Linux machine as the repository records.

**What stays open.** A checked conditional theorem is a different thing from a discharged production guarantee.
The run-level theorems are implications from named hypotheses (83 named hypotheses in the statement of the newest
one, section 2.4), and on this machine even their compilation is unconfirmed. Tests show that the implementation
behaves as intended on the cases tested; they are separate from the formal security proofs, and the tie between
the two is the open item VR-003 called R6.

## 2. R1 — Lean

Commands: [`../scripts/r1-lean.sh`](../scripts/r1-lean.sh). Logs: [`../results/R1-lean/`](../results/R1-lean/).
Environment: [`../PINS.md`](../PINS.md) and `results/R1-lean/environment.txt`.

### 2.1 Build

| Item | Result | Log |
|---|---|---|
| Toolchain | Lean 4.34.1 and Lake 5.0.0, installed by elan from `formal/lean-toolchain` | `environment.txt` |
| Mathlib cache | 8,908 files downloaded and unpacked, exit 0 | `01-cache-get.log` |
| `lake build`, first pass | 3,840 jobs listed; started 05:14 UTC, ended 05:50 UTC; one failure: `ZK60Formal.RunExtractClassify`, `Lean exited with code 137` | `02-lake-build-pass1.log` |
| Retry of that module alone | killed again at 44 s | `02b-lake-build-retry-single.log` |
| Second pass with a swap file added | killed again at 238 s; the kernel log reads `Memory cgroup out of memory: Killed process (lean) … anon-rss:6081216kB` | `02-lake-build-pass2.log` |
| Modules compiled | 358 of 496 | `modules-built.txt` |
| Modules left unbuilt | 138: `RunExtractClassify`, 108 further modules of the default target that depend on it, and 29 check modules outside the default target, which the build never attempts | `modules-not-built.txt` |

Reading: the failure is a memory ceiling on the reviewer's machine (about 6 GiB per job). It is consistent with the
repository's own record of a 9.61 GiB peak for the merged check on a 256 GB machine. It says nothing against the
module. A machine with 16 GB or more should settle it.

One difference from VR-003: that report quoted the repository's figure of 3,703 build jobs. Lake listed 3,840 jobs
here. The two counts may differ in how dependencies are counted; the reviewer has left the difference unexplained.

### 2.2 Axioms of the theorems that compiled

Script: [`../scripts/r1_axioms_available.lean`](../scripts/r1_axioms_available.lean) (it lives outside the
library and changes nothing in it). Log: `03-axioms-available.log`.

| Theorem | Axioms reported by `#print axioms` |
|---|---|
| `ZK60.Exec.Block.Join.R13H.block_knowledge_r13_shield` | `propext`, `Classical.choice`, `Quot.sound` |
| `ZK60.Exec.Block.Join.R13H.block_knowledge_r13_rung` | the same three |
| `ZK60.D76.leaky_not_productionReadyL` | the same three |
| `ZK60.RunShape.Shield.shield_circuitIff` | the same three |
| `ZK60.Assembly.semanticHiding_of_zeroKnowledge` | the same three |
| `ZK60.Sound.mproduct_sound_shift`, `mproduct_offset_accepts` (the F12 fix and the F12 defect) | the same three |
| `ZK60.Sound.opening_sound_extracted`, `MerkleEnc.merkle_binding`, `sumcheck_sound`, `logup_block_bound`, `rs_proximity_half` | the same three |
| `ZK60.trivialArith_circuitIff` | none |

The same log gives the shape of the block theorem's statement: `block_knowledge_r13_shield` takes 48 binders, of
which 21 are propositional hypotheses. It is a conditional theorem too, at block level.

### 2.3 Kernel replay

`lake env leanchecker <module>` was run once for each of the 358 compiled modules. Result: 358 of 358 exit 0
(`04-leanchecker-built-modules.log`). `ZK60Formal.CircuitHelpers` ran past 20 minutes while sharing the machine
and was stopped; run alone it finished with exit 0 in under three minutes, and both attempts are in the log.

`leanchecker` is Lean's own kernel run a second time over the compiled files. It guards against a proof accepted
by the elaborator and rejected by the kernel, and against tampered compiled files. A replay with nanoda, an
independent implementation of the kernel, remains to be done.

### 2.4 The central production-readiness theorems

These are in modules downstream of `RunExtractClassify`, so Lean could not be asked about them here. The full
script for that question is ready: [`../scripts/r1_axioms_premises.lean`](../scripts/r1_axioms_premises.lean).

What could be read from the source text at `eee3eb57`, with no Lean run
(`05-top-theorem-statement-static.txt`):

- The newest top theorem, `stgAlg_productionReadyL_epP_exec_real` (`formal/ZK60Formal/RunStgAlgTopR.lean`), has
  a statement 309 lines long with 83 named hypotheses, and concludes `ProductionReadyL … εcTarget εsTarget
  εsTarget εzkTarget` for the classifier protocol.
- Among the hypotheses are the ones VR-003 section 4.3 listed as open: `hblk`, `hdinS`, `hdoutS`, `hdzero`,
  `hread`, `hE`, and `hzk`. Many of the others are range and bookkeeping conditions.
- VR-003's static scan found zero `sorry`, `axiom` or `native_decide` in all 497 files, including these.

So the position is unchanged from VR-003 and from the repository's gap audits of 2026-11-10: the top theorem is
an implication whose hypotheses are still to be discharged, and no concrete end-to-end instance exists yet.

## 3. R2 — Rust

Commands: [`../scripts/r2-rust.sh`](../scripts/r2-rust.sh) and
[`../scripts/r2-hashline-per-test.sh`](../scripts/r2-hashline-per-test.sh).
Logs: [`../results/R2-rust/`](../results/R2-rust/). Scope: the current crates under `ops/zkp-mvp/gpu-metal/`, CPU
only, release profile, `--locked`.

### 3.1 Results

| Suite | Passed | Failed | Ignored | Unfinished | Log |
|---|---|---|---|---|---|
| `zkp-core`, library tests | 83 | 0 | 2 | 0 | `zkp-core-lib-release.log` |
| Hashline, library tests, one process per test | 978 | 5 | 90 | 0 | `hashline-per-test.tsv` |
| F12 tests (names containing `f12`) | 8 | 0 | 0 | 0 | `f12-control.log`, `f12-control-archived-receipts.log` |

The first attempt ran the whole Hashline suite in one process (`hashline-lib-release.log`). It was killed for
memory after 613 passes, and 30 fork tests had already failed for want of a fixture path. The per-test run
replaced it: each test in its own process, with `HL_R13_LOADER_FIXTURES` set to the in-repository fixtures, which
is the override the test source itself names.

### 3.2 Every failure, and its cause

| Test | Cause | After adjusting the environment |
|---|---|---|
| 30 `private_block::run::fork` tests (first attempt only) | default fixture path `ops/zkp-mvp/loader-fixtures/` is absent from the public tree; the fixtures are tracked at `results/zk60_1b_native_20261017/r13/loader-fixtures/` | pass with `HL_R13_LOADER_FIXTURES` set |
| `a20_the_receipt_write_is_the_same_files_bytes_list_and_refusals_at_every_writer_count` | expects a write into a read-only directory to be refused; the reviewer's machine runs as root, which may write anywhere | passes as a non-root user (`hashline-nonroot-rerun.log`) |
| `a22_the_server_proves_the_r13_export_as_stack_prove_does_and_carries_on_after_every_refusal` | same cause | passes as a non-root user |
| `a23_the_server_with_shared_blocks_proves_the_r13_export_as_stack_prove_does` | same assertion at the same source line | passes as a non-root user (962 s) |
| `accuracy_v2_dense_witness_matches_all_nineteen_independent_integer_traces` | reads `independent_trace.tsv`, a file listed in `SNAPSHOT_20261017_EXCLUDED_LARGE_FILES.json` and absent from the public tree | fixture unavailable |
| `a_toy_receipt_made_before_f12_is_refused` | reads four archived receipts at a path absent from the public tree; byte-identical copies are tracked under `results/` | passes with the copies placed at that path in a scratch checkout |

No failure points at a defect in the verifier. Three kinds of portability limit appear: a default fixture path
that exists only on the author's machine, tests that assume a non-root user, and one fixture kept outside the
repository.

### 3.3 The F12 control

Finding F12 (VR-003 section 1) was a soundness defect in the mask commitment's product test, found by the Lean
work and fixed on 2026-11-04. Reproduced here:

- `f12_the_pre_f12_start_accepts_the_forgery`: the old starting point accepts the forged opening. Pass.
- `f12_the_first_functional_is_certified_only_up_to_the_blinding_sum`: the fixed verifier refuses it. Pass.
- `f12_control_an_honest_commitment_rejects_a_shifted_first_functional`. Pass.
- Version separation: an opening or receipt made under one version fails under the other, and 30 block and 19 run
  pre-F12 profile strings are refused by name. Pass (4 tests).
- Four archived pre-F12 toy receipts are refused by the current verifier (`expected statement mismatch`). Pass.

### 3.4 Receipt verification with public fixtures

`python3 scripts/zk60_p1_demo.py --output <dir>` ran from a clean clone in 72 s: it registers public synthetic weights,
proves one feed-forward component with private input, output and intermediate values, verifies the saved receipt
in a separate process, and checks that the verifier refuses six wrong inputs. Result: `status: passed`, 9 steps,
6 rejection controls (`p1-demo.log`, `p1-demo-manifest.json`). The script's own documentation states the limits: it
is a component demo on a synthetic fixture, and a pass says nothing about privacy being established.

Negative controls inside the Hashline suite (tampered receipts, wrong digests, refused chains) are part of the 978
passing tests; the fork tests named `…refuses…` and `…is_refused…` are examples.

### 3.5 What was left out

| Item | State |
|---|---|
| Hashline integration tests (`ops/zkp-mvp/gpu-metal/hashline/tests/`, 27 files) | left unrun; each builds its own release binary, beyond this machine's time |
| Other crates (`private-block-kernel`, `private-block-kernel-shaped`, root `hashline/`, `zkvm-block/`, `apps/`) | left unrun |
| The 600 `Cargo.toml` files in snapshot trees under `ops/zkp-mvp/` | out of scope; they are archived copies |
| Metal and CUDA backends | out of scope; no GPU |
| Python suite (`python3 -m unittest discover -s tests`) | left unrun |
| 90 ignored Hashline tests | marked `#[ignore]` by the author (benchmarks and tests needing large or private inputs) |

## 4. Corrections and refinements to VR-003

VR-003 is kept as written. These points refine it.

| VR-003 statement | Refinement |
|---|---|
| Section 5.1: Hashline tests "326 of 1,073 passed … time-limited" | superseded by section 3.1 above |
| Section 7, R1: "job count equal to the recorded one" (3,703) | Lake lists 3,840 jobs at this commit on Linux; a job-count match is a poor acceptance test and should be replaced by "every module of the default target compiles" |
| Section 7, R1: "a Linux machine with 16 GB or more" | confirmed from below: 6 GiB is too little for `RunExtractClassify` |
| Section 7, R1: "a re-check with nanoda or lean4checker" | `leanchecker` now ships inside the Lean toolchain and was used; nanoda remains |
| Section 5.3: "check scripts need editing before a second party can run them" | the Lean build itself needed no edit: `lake exe cache get` and `lake build` work from a clean clone |
| Section 5.3: large artifacts outside the repository | now concrete: one Hashline test and one F12 test need files outside the public tree; for the F12 test the tracked copies suffice |

## 5. Roadmap checkpoint

The order of VR-003's roadmap stands, with these changes.

| # | Candidate | State after R1 and R2 | Proposed next action | RLT role |
|---|---|---|---|---|
| R1 | Lean rebuild, axioms, second kernel | three-quarters done: components and blocks confirmed; run-level modules need a larger machine | finish on a machine with 16 GB or more: `lake build`, `r1_axioms_premises.lean`, `leanchecker` on the remaining modules, then nanoda | pins only |
| R2 | Rust tests and F12 control | done for the two core libraries on CPU | integration tests and the demo on a larger machine; offer the three portability notes to Victor | pins only |
| R5 | Machine-generated premise register | raised in priority: section 2.4 shows the question "what remains" has a mechanical answer (83 named hypotheses), and the `#premises` command in `r1_axioms_premises.lean` is the first piece of it | classify the hypotheses of `stgAlg_productionReadyL_epP_exec_real` as open, bookkeeping, modelling, ruling or public data, and compare with the audit's 47 rows | design model only |
| R3 | Statement-fidelity pack | unchanged; needs reading, no heavy machine | proceed after review of this report | current capability: source registry and correspondence records |
| R4 | Arithmetic certificates | unchanged | feasibility measurement first | current kernel for small closed facts; generators for eight-digit and nine-digit products are a proposed extension |
| R6 | Lean versus Rust on a full Shieldstral T128 run | unchanged; needs Victor's corpus | wait for Victor | none |
| R7 | Privacy evidence after F12 | unchanged; question 3 for Victor | wait for Victor's answer | none |
| R8 | Closing run-level soundness | unchanged; overlaps Victor's lanes | wait for Victor's word on free premises | none |
| R9 | Soundness margin and query count | unchanged | analysis can start from public sources (FlashProve's protocol document, the Lean per-opening theorems) | none |

Demonstrations that would most benefit IntelligenceRegulation, in the reviewer's reading:

1. **A complete, second-party Lean check** (finish R1). It is the one result that turns the project's central
   formal claim into independent evidence, and it needs only a larger machine.
2. **The premise register** (R5). It makes progress toward rule D63 measurable by anyone and keeps status pages
   exact.
3. **A portable reproduction kit** (from R1 and R2): a container recipe and CI workflow that run the Lean build,
   the axiom listing and the two Rust suites as a non-root user with the fixture path set. This is infrastructure
   Victor could adopt directly.
4. **The statement-fidelity pack** (R3), for readers who need to know what the gate says before they care how it
   is proved.

Items 1 to 3 involve Lean and Rust only. RLT contributes to item 4 with what it has today (pinned source excerpts
and correspondence records) and to R4 with its kernel, where larger arithmetic needs a proposed extension. The
FlashProve comparison of VR-003 section 3 is unchanged by this report; R9 is where it bears on future work.

## 6. Open questions for Victor

The twelve questions of VR-003 section 8 stand. Three are added by this work:

13. Is the default R13 fixture path (`ops/zkp-mvp/loader-fixtures/`) meant to be created by a setup step, or
    should the tests default to the tracked copy under `results/zk60_1b_native_20261017/r13/loader-fixtures/`?
14. Could `independent_trace.tsv` for the three dense fixtures be published, so that
    `accuracy_v2_dense_witness_matches_all_nineteen_independent_integer_traces` runs from a clean clone?
15. What memory does `ZK60Formal.RunExtractClassify` need when compiled alone on your machine?

## 7. Unfinished

- R1: 109 modules of the default target uncompiled; axioms and Lean-elaborated premises of the run-level theorems;
  nanoda.
- R2: integration tests, other crates, the Python suite.
- Discoverability: see the index, section "Where to find this review".
