# Independent external review of IntelligenceRegulation

**This folder is an independent external review.** It was written by an outside reviewer (the owner of the fork
`thinkthoughts/IntelligenceRegulation`, working with Claude) about Victor Rielly's IntelligenceRegulation. Victor
has had no part in it and has neither reviewed, endorsed nor accepted any finding. The review makes no claim that
the project is production-secure, that its proofs are complete, or about research priority.

## Latest report

**[RPI-RLT-VR-007 — Independent replay and author-facing review](reports/RPI-RLT-VR-007.md)**, 2026-11-14, with
the **[two-page summary for Victor Rielly](SUMMARY-FOR-VICTOR.md)**.

In one paragraph: nanoda, a Lean kernel implemented separately in Rust, accepts Victor's block-level
knowledge-soundness theorem with its 38,128 dependencies and the F12 fix with 17,840, and refuses both when one of
the three standard axioms is withheld. The four production-readiness top theorems in the repository prove the
same conclusion under different hypotheses: the three parallel ones each discharge 15 endpoint facts that the
newest one assumes and exchange one or two others for conditions on the verifier's parameters; each of the four
carries 24 or 25 open obligations. Run-level kernel
replays on the larger machine are prepared and awaited (`results/R7-vps/README.md`). Production readiness remains
conditional, as the repository's rule D63 and gap audits say.

## Report history

| Report | Date | What it is | Evidence basis |
|---|---|---|---|
| [RPI-RLT-VR-007](reports/RPI-RLT-VR-007.md) | 2026-11-14 | nanoda on three theorems; replay script inspected and trial-run; the four top theorems compared and checked; summary for Victor | logs in `results/R7-*`, checks and tests re-run; VPS steps awaited |
| [RPI-RLT-VR-006](reports/RPI-RLT-VR-006.md) | 2026-11-14 | VPS logs read and hash-checked; Lean-generated premise inventory reconciled, normalized and checked; corrections to VR-005 | logs and Lean output in `results/`, checks re-run |
| [RPI-RLT-VR-005](reports/RPI-RLT-VR-005.md) | 2026-11-14 | VPS results as reported, premise inventory and classification of the top theorem, tooling with tests | source read, tools re-run; VPS logs awaited |
| [RPI-RLT-VR-004](reports/RPI-RLT-VR-004.md) | 2026-11-14 | reproduction of R1 (Lean) and R2 (Rust), roadmap checkpoint | commands re-run, logs in `results/` |
| [RPI-RLT-VR-003](reports/RPI-RLT-VR-003.md) | 2026-11-13 | full technical review: architecture, FlashProve comparison, formal-verification inventory, roadmap R1 to R9 | source read at pinned commits, a few checks re-run |
| RPI-RLT-VR-002 | earlier | preliminary investigation | text unavailable to this review; unpublished here |
| RPI-RLT-VR-001 | earlier | preliminary investigation | text unavailable to this review; unpublished here |

VR-001 and VR-002 were preliminary investigations by the fork owner. Their texts could not be recovered for this
branch, and VR-003 was written without them. Their findings count as reported leads; VR-003 and VR-004 are the
source-verified record.

## Source commits and toolchains

Full table: [PINS.md](PINS.md).

| What | Pin |
|---|---|
| IntelligenceRegulation (Victor's `main`, and this fork's `main`) | `eee3eb5717dea88d0fc48dc00f6aef389d52af3a` |
| FlashProve | `9e2bdd8ff5bf9c62f18263d7dac189b0400b260c` (0.16.0) |
| RLT | `7d57ae8ab04e966edf1452afedf30cdd15a961a6` |
| Lean, Mathlib | 4.34.1, `v4.34.1` (as declared in `formal/`) |
| Rust | rustc and cargo 1.97.0, `--locked` |
| Reproduction machine (VR-004, VR-005 tooling) | 2 cores, 8 GB (about 6 GiB usable per job), Ubuntu 24.04, x86-64, CPU only |
| Second machine (VPS, fork owner) | Ubuntu, Linux 6.8, x86-64, 4 cores, 15,992 MB RAM, 8 GB swap, Lean 4.34.1; logs in `results/R1-lean-vps/` |

## Reproduced versus reported

| Claim | Status | Where |
|---|---|---|
| Fork `main` equals Victor's `main` at `eee3eb57` | reproduced | VR-003 §5.1 |
| The 15 Lean files credited to FlashProve match FlashProve at its pinned commit | reproduced | VR-003 §5.1 |
| Zero `sorry`, `axiom`, `native_decide` in 497 Lean files | reproduced (text scan) | VR-003 §5.1 |
| Lean library builds | reproduced for 358 of 496 modules on the 6 GiB machine; complete build (3,840 jobs) logged on the second machine | VR-004 §2.1, VR-006 §2 |
| Axioms limited to `propext`, `Classical.choice`, `Quot.sound` | reproduced for 13 named component and block theorems; logged on the second machine for the central theorem and three other top theorems | VR-004 §2.2, VR-006 §2 |
| Second kernel check | reproduced with `leanchecker` on 358 modules; logged for `ZK60Formal.RunStgAlgTopR` (3.10 GiB peak); the whole-library form's memory failure is reported, its log is empty; nanoda, a separate kernel, accepts three component and block theorems, run-level awaited | VR-004 §2.3, VR-006 §2, VR-007 §2.3 |
| Run-level `ProductionReadyL` theorem holds from named hypotheses | proof term checked on the second machine; Lean lists 196 binders, 88 propositional; 173 normalized keys classified, 31 of them open | VR-006 §3, §4 |
| Four top theorems: same conclusion; what each discharges, exchanges and leaves open | checked from names and statement text, cross-checked against Lean for the L55 theorem | VR-007 §3 |
| End-to-end production guarantee for the running app | open, by the repository's own account (rule D63, gap audits of 2026-11-10) | VR-003 §4 |
| `zkp-core` tests pass | reproduced | VR-004 §3.1 |
| Hashline library tests pass | reproduced: 978 passed, 90 ignored by the author, 5 failed for environment or fixture reasons (4 pass once adjusted) | VR-004 §3.1, §3.2 |
| F12 forgery accepted before the fix and refused after | reproduced | VR-004 §3.3 |
| Throughput (32 to 34 proved tokens/s on an M3 Ultra) and all other timings | reported; no GPU or timing run was made | VR-003 §2.3 |
| Privacy gate results | reported; pre-F12 records | VR-003 §5.3 |
| Lean model equals the Rust code at production shape | reported as open (R6) | VR-003 §4.4 |

## Open questions for Victor

Grouped for Victor in [SUMMARY-FOR-VICTOR.md](SUMMARY-FOR-VICTOR.md). Full text: VR-003 §8 (1 to 12), VR-004 §6 (13 to 15), VR-005 §7 (16 to 18), VR-006 §9 (20 to 24), VR-007 §6 (25, 26). In short:

1. Where is the public statement of purpose, and is `docs/VISION.md` current?
2. When did the repository first become public?
3. Has the privacy gate been re-run on post-F12 (`/2`) bundles?
4. Has nanoda or another independent checker been run over the merged Lean tree?
5. Would a path-independent check script and CI workflow be welcome?
6. Which open premises are free for an outside contributor?
7. How will the 100-bit soundness target be reached or re-ruled?
8. Will the D55 fork-join run get its own gate instance?
9. When does the token-I/O run get a Lean protocol instance?
10. Is FlashProve's weight-hiding construction under consideration for P3?
11. Is a trained-weight 8B timing planned?
12. How does a receipt connect to the model-approval registry of the vision?
13. Should the R13 fixture path default to the tracked copy?
14. Could `independent_trace.tsv` be published?
15. How much memory does `RunExtractClassify` need alone?
16. Which theorem is the one to cite as the top theorem today, and is a merged one planned?
17. Is D79 closed by the Lean repair?
18. Are the categories right? (now `results/R6-reconciliation/classification-normalized.tsv`)
20. Are five fields of `hD` open and the other ten settled side conditions?
21. Are the hypotheses added by the L52, L55 and L56 top theorems all fit, geometry and choice conditions?
22. Does `site` carry a burden of its own?
25. Is a theorem combining L55's closing discharges with L57's stage refinement the planned next top theorem?

## Status

| Item | State on 2026-11-14 |
|---|---|
| Review | VR-003 to VR-007 published; summary for Victor drafted |
| R1 (Lean) | complete build, central axioms and the run-level module's replay logged on a second machine; nanoda accepts three component and block theorems; per-module replay and nanoda on run-level theorems prepared, awaiting the VPS |
| R2 (Rust) | done for the two core libraries |
| R5 (premise inventory) | the audited theorem reconciled with Lean; all four top theorems compared and checked |
| Held | R3, R4, R6 to R9, and anything touching Hashline, until the fork owner approves |
| Contact with Victor | none; no upstream issue or pull request |
| Changes to Victor's files | one notice at the top of `README.md` on this branch; everything else is under `evidence/` |

## Proposed next steps

1. The VPS steps in `results/R7-vps/README.md`: per-module replay, nanoda on the four top theorems, axioms of the L52 and L56 theorems, the out-of-memory diagnostic.
2. A short follow-up report reading those logs.
3. Review of the summary for Victor, then a decision on contacting him.
4. Then choose among R3 (statement-fidelity pack), R4 (arithmetic certificates) and a reproduction kit.

## Where to find this review

- The review lives on the branch `formalize-now/intelligenceregulation-review` of the fork:
  <https://github.com/thinkthoughts/IntelligenceRegulation/tree/formalize-now/intelligenceregulation-review/evidence>
- **Limitation.** The fork's default branch is `main`, which is kept identical to Victor's. GitHub's landing page
  for the fork therefore shows Victor's README without any notice, and a visitor sees this review only by
  switching branch or by following the link above. The notice at the top of `README.md` is visible on this branch
  alone (checked 2026-11-14 by fetching both branches' README files).

## How to respond

[RESPONSE-GUIDE.md](RESPONSE-GUIDE.md): how to reproduce a finding, report an error, ask for a correction, or
discuss a proposed step.

## Layout

| Path | Content |
|---|---|
| `reports/` | the reports, newest listed first above |
| `scripts/` | the exact commands run, and two Lean files that only query the library |
| `results/R1-lean/`, `results/R2-rust/` | logs and result tables of VR-004 |
| `results/R1-lean-vps/` | the second machine's results: reported figures and the steps for placing its logs |
| `results/R5-premises/` | premise inventories (Lean-generated and source-based), the VR-005 classification, the tool test log |
| `results/R6-reconciliation/` | the key map, the normalized classification, the discharge audit, check and test logs |
| `results/R7-nanoda/`, `results/R7-local-trial/` | nanoda results; trial of the replay script |
| `results/R7-comparison/` | the four-theorem table, its summary, check and test logs |
| `results/R7-vps/` | steps for the larger machine; its results, when committed |
| `SUMMARY-FOR-VICTOR.md` | the two-page summary for the author |
| `PINS.md` | source and environment pins |
| `RESPONSE-GUIDE.md` | status and how to respond |
