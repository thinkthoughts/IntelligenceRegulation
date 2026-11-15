# IntelligenceRegulation: an independent technical review, in two pages

> **Independent external review**, written for Victor Rielly by the owner of the fork
> `thinkthoughts/IntelligenceRegulation` with Claude (Anthropic). Victor has not reviewed or endorsed it. Every
> figure below is traced in the reports listed at the end. Version of 2026-11-15, with the second machine's
> evidence of review commit `51480d81`; source commit `eee3eb57`.

## Your project and what it has built

IntelligenceRegulation sets out to make AI governance verifiable: a receipt that an approved, public model
produced a result, while the data it ran on stays private (`docs/VISION.md`). Its first milestone, P1, hides
inputs, outputs and every intermediate activation; the weights are public. P3 adds hidden weights with
authenticated model identity.

What exists at `eee3eb57`, from the repository's own records:

- **Hashline**, a Rust prover and verifier for an exact integer transformer: Ligero-style hiding commitments over
  Goldilocks, BLAKE3 Merkle trees, masked sumcheck, LogUp lookups, Fiat-Shamir on a hash chain.
- **Three registered model shapes** (Llama-3-8B, TinyLlama-1.1B, Shieldstral-1.0-3B), parallel "commit, fork,
  join" proving (D55), CPU and Apple Metal backends, and an end-to-end media-classifier application.
- **Measured speed** of 32.5 to 34.2 proved tokens/s (proof only) at 8B shapes on one M3 Ultra.
- **A Lean 4 formalization** of about 180,000 lines, begun on 2026-11-04, with production statements you approved
  (`ZK60_LEAN_PRODUCTION_STATEMENTS.md`) and a production rule (D63) that ties deployment to their proof.
- **A soundness defect found by your own formalization** (F12, in the mask commitment's product test), reproduced
  in Rust and fixed on the same day, with the fix proved in Lean.
- **Unusually thorough self-audit**: a decisions register, labelled numbers, and two gap audits (2026-11-10) that
  state the open premises plainly.

## How it differs from FlashProve

The two systems answer complementary questions. FlashProve (0.16.0) shows which committed model produced a reply,
with the weights hidden and the prompt and reply public. IntelligenceRegulation shows that the approved public
model produced a result on data that stays hidden. Both draw on the same published toolkit (sumcheck,
log-derivative lookups, Reed-Solomon proximity, Fiat-Shamir with a hash). They diverge where it matters: proximity
testing (FlashProve folds and switches codes up to the Johnson radius; Hashline tests columns at the unique-decoding
radius), the privacy model, and the statement set. Your statements include a semantic-hiding corollary derived from
zero knowledge, which FlashProve's set lacks. FlashProve's Lean theorems are closed for one concrete verifier at
full size; yours are proved component by component, with the run level conditional (below). Throughput figures
come from different hardware, models and privacy goals, so they sit side by side as context.

## What we reproduced independently

On two machines unrelated to yours (a 2-core cloud workspace and a 4-core, 16 GB Linux server):

| Result | Reproduced |
|---|---|
| The whole Lean library builds with Lean 4.34.1 | yes: 3,840 jobs, exit 0 |
| Lean's kernel, run again over the compiled files (`leanchecker`), one module at a time | all 496 modules accepted, including the 29 check modules; one module needs about 12 GB |
| A kernel implemented separately from Lean (nanoda, in Rust) | accepts all four top theorems (L52, L55, L56, L57), each with the 36,463 to 37,344 declarations it depends on, and also `block_knowledge_r13_shield` and the F12 fix; each is refused once `Classical.choice` is withheld |
| Axioms | all four top theorems depend on `propext`, `Classical.choice` and `Quot.sound` only |
| Your Rust exporters for the L9 and L10 Lean fixtures | regenerate files of the committed lengths (identity, and the L10 checksum, on the fork owner's comparison); `CoverW16MCheck` then passes, 54 checks, 0 failed |
| Rust tests on x86-64 Linux | `zkp-core` 83 pass; Hashline 978 pass, 5 fail for environment or fixture reasons, 4 of them pass once adjusted |
| The F12 control | the pre-fix verifier accepts the forgery; the fixed one refuses it; old receipts are refused |
| The P1 component demo | passes, with 6 of 6 rejection controls |

All 15 Lean files you adapted from FlashProve match FlashProve at its pinned commit, as your NOTICE states.

## What remains conditional or unverified

Two kernels confirm that the proofs are valid; neither can confirm a theorem's hypotheses. That line runs through
everything below.

- **The run-level theorem is a checked implication.** `stgAlg_productionReadyL_epP_exec_real` proves
  `ProductionReadyL` for a verifier given as parameters, from 196 binders. Reconciled with Lean's own list, 31 keys
  are open obligations: stage soundness on the transcript, the wiring of the block theorem into the run, the input
  endpoint's extractor (including `mk`), five fields of `hD`, completeness (O8 to O10), and zero knowledge of the
  run (O12). This matches your gap audits.
- **Your four parallel top theorems** (lanes L52, L55, L56, L57) reach the same conclusion. L52, L55 and L56 each
  discharge 15 endpoint hypotheses that L57 assumes, and exchange a few others for conditions on the verifier's
  parameters; all four carry 24 or 25 open obligations. Finding L56-2's merged theorem is the natural next object.
- **A concrete instance** (the Shieldstral T128 verifier as Lean values) has yet to be written; 121 of the
  normalized keys are bookkeeping or public data of the kind such an instance would settle at once.
- **Unverified by us**: the timing figures, the privacy-gate results (whose records predate the F12 fix), and the
  Lean–Rust agreement at production shape.

## Where outside contributors can help

1. **Keeping the checking independent as the library grows**: a CI workflow that rebuilds the library and runs
   the per-module replay and nanoda on each new top theorem. The scripts exist; nanoda needs a
   `stack_size_bytes` of 256 MiB for your top theorems, and one module needs about 12 GB.
2. **Specific open obligations**, chosen with you so lanes stay separate: for example IN-C's LogUp round-by-round
   bound, whose model is written (L57 §5.3).
3. **The concrete Shieldstral instance**, and the merged top theorem of finding L56-2.
4. **Reproducibility**: publishing the small fixtures some tests read from outside the public tree, and a
   portable default for the R13 fixture path.
5. **Privacy evidence after F12**: a re-run of the gate on post-fix bundles, and an experiment written separately
   from the gate's code.

## Where RLT adds specific value

RLT is a small first-order proof checker developed by the fork owner. Its current capabilities fit a narrow part of
this work: recording exactly which source text a claim comes from (pinned excerpts), keeping proof validity,
source fidelity and correspondence to the running system as separate verdicts, and certifying small closed
arithmetic facts behind your bounds (for example 15 × 270,336 = 4,055,040 ≤ 201,326,592). Certificates at these
sizes need proof generators that RLT has yet to have. The cryptographic mathematics belongs in Lean. RLT
demonstrations are a later, optional phase, offered for your judgment.

## On chronology and attribution

This is a separate question from the technical findings above, and the review treats it separately. The commit
history records Hashline's core design two months before FlashProve's release; the repository became public two
days after the announcement, so those earlier dates rest on author-recorded history. The shared ingredients are
published prior art, and the one direct reuse (15 Lean files) is openly credited. The review draws no conclusion
about copying or priority in either direction.

## Questions for you

1. Which top theorem should a reader cite today, and is the L55 + L57 merge planned?
2. Are the 31 open keys, and their categories, the list you would give? (`classification-normalized.tsv`)
3. Has the privacy gate been re-run on post-F12 bundles?
4. Which open obligations are free for an outside contributor?
5. Is D79 closed by the Lean repair?
6. How will the 100-bit soundness target be met: parameters, grinding, or a ruling?
7. Could the R13 fixtures and `independent_trace.tsv` default to, or be published in, the public tree?
8. Would a CI workflow, or the reproduction scripts, be welcome as a contribution?

The full list (26 questions) is in the reports.

## The record

Index: [`README.md`](README.md). Reports: VR-003 (the full review, with the FlashProve comparison), VR-004
(Lean and Rust reproduction), VR-005 and VR-006 (the premise inventory), VR-007 (independent kernel, the four top
theorems, this summary).
