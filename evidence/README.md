# Independent external review of IntelligenceRegulation

**This folder is an independent external review.** It was written by an outside reviewer (the owner of the fork
`thinkthoughts/IntelligenceRegulation`, working with Claude) about Victor Rielly's IntelligenceRegulation. Victor
has had no part in it and has neither reviewed, endorsed nor accepted any finding. The review makes no claim that
the project is production-secure, that its proofs are complete, or about research priority.

## Latest report

**[RPI-RLT-VR-004 — Review publication and independent reproduction (R1, R2)](reports/RPI-RLT-VR-004.md)**,
2026-11-14.

In one paragraph: on a small x86-64 Linux machine, 358 of the 496 Lean modules compiled with the declared
toolchain and all 358 passed a second kernel check; the named component and block theorems depend on the three
standard axioms only. One module needed more memory than the machine had, so the run-level production-readiness
theorems remain uncompiled here; they are conditional theorems with open hypotheses in any case. The Rust
verifier's library tests and the F12 forgery control behave as the repository records; every test failure seen
traced to the reviewer's environment or to a fixture kept outside the public tree.

## Report history

| Report | Date | What it is | Evidence basis |
|---|---|---|---|
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
| Reproduction machine | 2 cores, 8 GB (about 6 GiB usable per job), Ubuntu 24.04, x86-64, CPU only |

## Reproduced versus reported

| Claim | Status | Where |
|---|---|---|
| Fork `main` equals Victor's `main` at `eee3eb57` | reproduced | VR-003 §5.1 |
| The 15 Lean files credited to FlashProve match FlashProve at its pinned commit | reproduced | VR-003 §5.1 |
| Zero `sorry`, `axiom`, `native_decide` in 497 Lean files | reproduced (text scan) | VR-003 §5.1 |
| Lean library builds | reproduced for 358 of 496 modules; the rest need more than 6 GiB | VR-004 §2.1 |
| Axioms limited to `propext`, `Classical.choice`, `Quot.sound` | reproduced for 13 named component and block theorems; reported for the run-level theorems | VR-004 §2.2 |
| Second kernel check | reproduced with `leanchecker` on 358 modules; nanoda still to do | VR-004 §2.3 |
| Run-level `ProductionReadyL` theorem holds from named hypotheses | reported; statement read from source (83 named hypotheses) | VR-004 §2.4 |
| End-to-end production guarantee for the running app | open, by the repository's own account (rule D63, gap audits of 2026-11-10) | VR-003 §4 |
| `zkp-core` tests pass | reproduced | VR-004 §3.1 |
| Hashline library tests pass | reproduced: 978 passed, 90 ignored by the author, 5 failed for environment or fixture reasons (4 pass once adjusted) | VR-004 §3.1, §3.2 |
| F12 forgery accepted before the fix and refused after | reproduced | VR-004 §3.3 |
| Throughput (32 to 34 proved tokens/s on an M3 Ultra) and all other timings | reported; no GPU or timing run was made | VR-003 §2.3 |
| Privacy gate results | reported; pre-F12 records | VR-003 §5.3 |
| Lean model equals the Rust code at production shape | reported as open (R6) | VR-003 §4.4 |

## Open questions for Victor

Full text: VR-003 §8 (questions 1 to 12) and VR-004 §6 (13 to 15). In short:

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

## Status

| Item | State on 2026-11-14 |
|---|---|
| Review | VR-003 published; VR-004 published |
| Implementation | R1 partial (needs a machine with 16 GB or more), R2 done for the two core Rust libraries |
| Held | R3 to R9, until the fork owner has read VR-004 |
| Contact with Victor | none; no upstream issue or pull request |
| Changes to Victor's files | one notice at the top of `README.md` on this branch; everything else is under `evidence/` |

## Proposed next steps

1. Finish R1 on a larger machine (complete build, axioms and premises of the run-level theorems, nanoda).
2. Build the machine-generated premise register (R5).
3. Package R1 and R2 as a container recipe and CI workflow that Victor could adopt.
4. Statement-fidelity pack (R3).

Details and the full R1 to R9 table: VR-004 §5.

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
| `results/R1-lean/`, `results/R2-rust/` | logs and result tables |
| `PINS.md` | source and environment pins |
| `RESPONSE-GUIDE.md` | status and how to respond |
