# Independent external review of IntelligenceRegulation

**This folder is an independent external review.** It was written by an outside reviewer (the owner of the fork
`thinkthoughts/IntelligenceRegulation`, working with Claude) about Victor Rielly's IntelligenceRegulation. Victor
has had no part in it and has neither reviewed, endorsed nor accepted any finding. The review makes no claim that
the project is production-secure, that its proofs are complete, or about research priority.

## Latest report

**[RPI-RLT-VR-005 — VPS verification and production premise audit](reports/RPI-RLT-VR-005.md)**, 2026-11-14.

In one paragraph: the fork owner reports that the whole Lean library builds on a 15 GiB machine and that the
newest top theorem depends on the three standard axioms only; those logs are still to be placed in this folder,
so the figures are marked "reported". The top theorem, `stgAlg_productionReadyL_epP_exec_real`, is a conditional
theorem about a parametric verifier. This review lists 103 hypotheses and obligations in its statement and
classifies them: 26 open cryptographic or protocol obligations, 18 already proved elsewhere in the repository on
parallel lines of work, 37 bookkeeping, 20 public instance data, 2 modelling. A checked proof term is established;
a production guarantee for the running application remains open, as the repository's own rule D63 and gap audits
say.

## Report history

| Report | Date | What it is | Evidence basis |
|---|---|---|---|
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
| Second machine (VPS, fork owner) | Ubuntu Linux, 15 GiB RAM, 8 GiB swap, Lean 4.34.1; reported, logs awaited |

## Reproduced versus reported

| Claim | Status | Where |
|---|---|---|
| Fork `main` equals Victor's `main` at `eee3eb57` | reproduced | VR-003 §5.1 |
| The 15 Lean files credited to FlashProve match FlashProve at its pinned commit | reproduced | VR-003 §5.1 |
| Zero `sorry`, `axiom`, `native_decide` in 497 Lean files | reproduced (text scan) | VR-003 §5.1 |
| Lean library builds | reproduced for 358 of 496 modules on the 6 GiB machine; complete build (3,840 jobs) reported from the VPS, logs awaited | VR-004 §2.1, VR-005 §2 |
| Axioms limited to `propext`, `Classical.choice`, `Quot.sound` | reproduced for 13 named component and block theorems; reported from the VPS for the central theorem, log awaited | VR-004 §2.2, VR-005 §2 |
| Second kernel check | reproduced with `leanchecker` on 358 modules; reported for `ZK60Formal.RunStgAlgTopR`; a separate kernel implementation (nanoda) still to do | VR-004 §2.3, VR-005 §2 |
| Run-level `ProductionReadyL` theorem holds from named hypotheses | proof term reported checked; 103 hypotheses and obligations listed from source and classified, 26 of them open; Lean-generated list awaited | VR-005 §3, §4 |
| End-to-end production guarantee for the running app | open, by the repository's own account (rule D63, gap audits of 2026-11-10) | VR-003 §4 |
| `zkp-core` tests pass | reproduced | VR-004 §3.1 |
| Hashline library tests pass | reproduced: 978 passed, 90 ignored by the author, 5 failed for environment or fixture reasons (4 pass once adjusted) | VR-004 §3.1, §3.2 |
| F12 forgery accepted before the fix and refused after | reproduced | VR-004 §3.3 |
| Throughput (32 to 34 proved tokens/s on an M3 Ultra) and all other timings | reported; no GPU or timing run was made | VR-003 §2.3 |
| Privacy gate results | reported; pre-F12 records | VR-003 §5.3 |
| Lean model equals the Rust code at production shape | reported as open (R6) | VR-003 §4.4 |

## Open questions for Victor

Full text: VR-003 §8 (questions 1 to 12), VR-004 §6 (13 to 15) and VR-005 §7 (16 to 18). In short:

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
18. Are the categories in `results/R5-premises/classification.tsv` right?

## Status

| Item | State on 2026-11-14 |
|---|---|
| Review | VR-003, VR-004 and VR-005 published |
| R1 (Lean) | complete build reported from a second machine; logs to be committed; per-module replay of run-level modules and nanoda remain |
| R2 (Rust) | done for the two core libraries |
| R5 (premise inventory) | tooling and tests done; classification from source text done; Lean-generated list awaited |
| Held | R3, R4, R6 to R9, and anything touching Hashline, until the fork owner has read VR-005 |
| Contact with Victor | none; no upstream issue or pull request |
| Changes to Victor's files | one notice at the top of `README.md` on this branch; everything else is under `evidence/` |

## Proposed next steps

1. Commit the VPS logs and the Lean-generated premise inventory (`results/R1-lean-vps/README.md` has the commands).
2. Revise the classification until the checker agrees with Lean's list.
3. Replay the remaining run-level modules with `leanchecker`, one module at a time; attempt nanoda.
4. Then choose among R3 (statement-fidelity pack), R4 (arithmetic certificates) and a reproduction kit.

Details: VR-005 §6 and §8; the full R1 to R9 table is in VR-004 §5.

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
| `results/R5-premises/` | premise inventories, the classification and the tool test log |
| `PINS.md` | source and environment pins |
| `RESPONSE-GUIDE.md` | status and how to respond |
