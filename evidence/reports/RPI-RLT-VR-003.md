# RPI-RLT-VR-003 — IntelligenceRegulation independent technical review

> **Independent external review.** Written for the fork `thinkthoughts/IntelligenceRegulation` by an outside
> reviewer working with Claude (Anthropic). Victor Rielly, the author of IntelligenceRegulation, has had no part
> in it and has neither reviewed nor endorsed it.
>
> **Publication note (2026-11-14, RPI-RLT-VR-004).** This file is the VR-003 report as completed on 2026-11-13,
> exported to Markdown from the review document at its final revision (21). Two things were added at publication
> and nothing else was changed: this notice, and the author line, which the export printed as a mention chip and
> which is written here as the fork owner's GitHub handle. Later results (the R1 and R2 reproduction runs) are in
> [RPI-RLT-VR-004.md](RPI-RLT-VR-004.md); where they refine a statement made here, that report says so and this
> text is left as written. Index: [../README.md](../README.md).

Nov 13, 2026 · thinkthoughts

Read-only review and research roadmap of Victor Rielly's IntelligenceRegulation at commit `eee3eb57`, compared with Anthropic's FlashProve 0.16.0 and assessed against RLT main.

## Sources and pins

Every finding below is read from these revisions. The fork and Victor's upstream are byte-identical at the pinned commit, so the review speaks about Victor's tree as published.

| Source | Location | Pin | Read how |
| --- | --- | --- | --- |
| IntelligenceRegulation (fork) | [thinkthoughts/IntelligenceRegulation](https://github.com/thinkthoughts/IntelligenceRegulation), `main` | `eee3eb5717dea88d0fc48dc00f6aef389d52af3a` (Victor Rielly, 2026-11-10) | shallow clone, 113,051 files, 5.0 GB checkout |
| IntelligenceRegulation (upstream) | [VictorRielly/IntelligenceRegulation](https://github.com/VictorRielly/IntelligenceRegulation), `main` | same SHA `eee3eb57` (`git ls-remote`, 2026-11-13) | remote heads listed; history read from a treeless clone (2,351 commits, all authored by Victor Rielly) |
| FlashProve | [anthropics/FlashProve](https://github.com/anthropics/FlashProve), `main` | `9e2bdd8ff5bf9c62f18263d7dac189b0400b260c`, version 0.16.0 (commit dated 2026-10-30) | shallow clone; README, `docs/protocol.md`, `guide/performance.md`, `lean/THEOREM.md`, `lean/GAPS.md`, `PUBLISHED-WORKS.md` |
| RLT | [thinkthoughts/rlt](https://github.com/thinkthoughts/rlt), `main` | `7d57ae8ab04e966edf1452afedf30cdd15a961a6` (PR #23, RLT-007 handoff) | shallow clone; `docs/RLT-007-HANDOFF.md`, `sources/registry.yaml`, `statements/`, `correspondence/` |
| FlashProve announcement | press coverage dated 2026-11-02 to 2026-11-05 (see Sources) | publication dates as printed | web search and one fetched article |

Three inputs named in the assignment were unavailable to this review and are treated as open: Victor's public statement containing the sentence "How can we develop intelligence at a manageable rate worldwide?" (the phrase is absent from the repository; the nearest in-repo text is `docs/VISION.md`), the summaries of RPI-RLT-VR-001 and VR-002 (the assignment file lists them without their content), and the site formalize.now/rlt (the RLT repository was read directly instead).

Evidence labels used throughout: **READ** (source text at the pin), **RE-RUN** (executed in this review's workspace), **REPORTED** (the repository's own record, taken as a lead), **INFERRED** (this review's reasoning).

## 1. Executive summary

IntelligenceRegulation is a working research prototype of private, provable AI inference: a zero-knowledge receipt that an approved, public model produced a result on data that stays hidden. Its purpose, stated in `docs/VISION.md`, is governance infrastructure: a way for parties to agree that everyone runs approved AI while keeping their own inputs and outputs confidential.

**What the project contributes.** The repository's current milestone, P1, hides inputs, outputs and every intermediate activation while the weights are public. This is the complement of FlashProve, which hides weights and publishes prompt and reply. Together the two cover the two halves of the question "which model ran, on whose data"; P3, the project's later milestone, aims to hide both.

**What is built (READ, REPORTED).**

- **Hashline**, a Rust prover and verifier: Ligero-style hiding polynomial commitments over Goldilocks and its quadratic extension, BLAKE3 Merkle trees, Fiat-Shamir on a hash chain, LogUp lookups and a masked sumcheck, over an exact integer model of the transformer.
- **Registered run profiles** at Llama-3-8B, TinyLlama-1.1B and Shieldstral-1.0-3B shapes, a parallel "commit, fork, join" mode (D55), CPU and Apple Metal backends, and an end-to-end media-classifier app (`apps/proven-media`).
- **Measured speed** on one M3 Ultra, 8B shapes with synthetic weights, 128 tokens: 22.9 proved tokens/s proof-only on 2026-11-04, rising to 32.5 to 34.2 in the later Phase A table (`MVP_STATUS.md`). The media app's classifier stream is at 16.8 tokens/s in a development mode.
- **A Lean 4 development** of 497 files and about 180,000 lines (`formal/`), started 2026-11-04, with the production statements approved by Victor and a large body of proved component theorems.

**Where the formal work stands.** The approved gate is `ProductionReadyL` in `formal/ZK60Formal/Statements.lean`. The component layers (hiding lemmas, sumcheck, LogUp, proximity, Merkle binding, Fiat-Shamir composition, per-block knowledge soundness at all 26 Shieldstral layers) are proved. The run-level top theorem is proved as an implication from named premises; closing those premises, a concrete end-to-end instance, completeness and zero knowledge of the run are the open work. The repository's own gap audits of 2026-11-10 state this plainly, and this review's reading agrees.

**Three findings that matter most.**

1. **The formalization has already paid for itself.** Lean step L3 exposed a real soundness defect in the Rust verifier (finding F12: the mask commitment certified its first functional only up to a prover-chosen constant). It was reproduced in Rust, fixed the same day under new profile versions, and the fix is proved in `SoundMProduct.lean`.
2. **The project audits itself to an unusual depth.** Thirteen "unmeetable premise" defects in the Lean model were found and repaired by its own lanes by 2026-11-10. The remaining risk is concentrated in the tie between Lean and the running Rust/Metal code and in the open run-level obligations.
3. **Independent reproducibility is the widest gap, and the best opening for outside help.** The evidence trail is extensive (714 result folders), yet builds and checks have run on Victor's machines, about 446 GiB of large artifacts live outside the repository, and the repository carries no CI configuration. A reproducible, pinned re-check by a second party is achievable now and would add evidence the project currently lacks.

**What this review re-ran (RE-RUN).** The fork matches upstream at `eee3eb57`. All 15 Lean files credited to FlashProve match their upstream counterparts at the pinned commit, with differences consistent with the NOTICE. A static scan of 497 Lean files found zero `sorry`, `axiom`, `admit` or `native_decide` uses outside comments. All 46 cited theorem and definition names checked exist in the tree. The `zkp-core` unit tests pass on x86-64 Linux (83 passed, 0 failed, 2 ignored), and the first 326 of 1,073 Hashline library tests passed with 0 failures before the time limit. A full Lean build and GPU runs were outside this review's means and remain REPORTED.

## 2. Architecture and completed capabilities

The system proves an exact integer transformer forward pass with a hash-based, transparent-setup argument, and separates what is hidden from what is public at the statement level.

### 2.1 Private and public information (P1)

| Class | Items | Carried by |
| --- | --- | --- |
| Hidden | input tokens, outputs, every intermediate activation | salted Merkle commitments (input root, hidden-output root, one boundary commitment per block boundary under D12a) |
| Public | model weights, profile and shapes, token count T, width d, layer count L, whether the request was served, any output part chosen for publication (the classifier verdict) | the statement; allowed leakage is named in Lean as `classifyLeak` (`StatementsD76Leak.lean`) |
| Later (P3) | weights hidden too, with authenticated model identity | proposed; `ZK60_PRIVACY_REQUIREMENTS.md` |

### 2.2 Components

| Component | Where | What it is | Status |
| --- | --- | --- | --- |
| Integer model | Rust witness builder; Lean `ModelInt.lean`, `Circuit*.lean` | 8-bit calibrated model: integer matrix products, lookup tables for exp, SiLU and rsqrt, exact rounding | built; Lean model matched the Rust witness on the R13 fixture, 69,018 checks, 0 failed (REPORTED), at development shapes |
| Hashline prover and verifier | `ops/zkp-mvp/gpu-metal/hashline` (current), `zkp-core`, root `hashline/` (earlier copy) | Rust; about 1,400 `#[test]` functions across the current crate and `zkp-core` (READ) | built |
| Commitment | `pcs.rs`, `merkle.rs`, `zk.rs` | Ligero-style: Reed-Solomon rows (rate 1/4; rate 1/2 at the unique-decoding radius under conditional ruling D59), column checks (256, or 280 at W16R2), salted BLAKE3 Merkle leaves, pad rows for hiding | built; per-opening soundness and hiding proved in Lean for the model of the code |
| Sumcheck and masks | `sumcheck.rs`, mask commitment `M` | sumcheck with CFS masking polynomials and a last-round extension | built; F12 defect in `M`'s product test found by Lean and fixed |
| Lookups | LogUp with committed helper columns | range, requantization and nonlinearity tables; 52% of a block's committed rows are LogUp helpers (REPORTED) | built; `logup_block_bound` proved |
| Fiat-Shamir | `transcript.rs` | BLAKE3 hash chain; `challenge_fp2` from two 128-bit halves; vector challenges by repeated squeezes | built; chain and vector-challenge models proved (`FSChain*.lean`, `FSWide*.lean`) |
| Run composition | D12a sequential run; D55 "commit, fork, join" | one transcript per run; D55 proves a request's blocks in parallel | D12a registered; D55 an opt-in prototype profile, measured |
| Stages | IN-C, 26 or 32 blocks, OUT-C; token-I/O | tokens to first block, blocks, verdict or next token | built for the classifier and token-I/O profiles |
| Backends | CPU; Apple Metal (`gpu-metal` feature); CUDA (`gpu-cuda` feature, cudarc) | proof bytes byte-identical across CPU and GPU under one seed (REPORTED) | CPU and Metal current; CUDA measured earlier on an RTX 4070 laptop, RTX 5090 port planned |
| Privacy gate | Rust and Python tooling over verifier captures | 18-part empirical leak hunt on the shipped prover's output | passed 12 of 12 registered D55 bundles on 2026-11-04; those records predate the F12 byte change (see section 5) |
| Application | `apps/proven-media` | media classifier with Shieldstral-1.0-3B, receipts verified end to end, testnet contracts | development mode; the active binary predates the F12 fix (gap audit GB-7) |
| Other lines | `zkvm-block/`, `zkvm-model/` (RISC Zero 3.0.6, Groth16); `zk_lattice/`, `zkmatrix-rs/`; music provenance | intermediate zkVM route for a tiny private block; earlier lattice route; a separate provenance PoC | retained as comparison rows and history |
| Governance of the work | `docs/zkmatrix-poc/ZK60_DECISIONS.md` (D1 to D79), `MVP_STATUS.md`, `PROGRESS_*.md`, resource guard | every security and product ruling recorded with date and owner; numbers labelled MEASURED, COUNTED, MODEL or EXTERNAL | active, current to 2026-11-10 |

### 2.3 Completed, measured, proven, proposed

| Kind | Content |
| --- | --- |
| Completed implementation | the prover and verifier, three model-shape profiles, D55, CPU and Metal backends, the media app, the privacy-gate tooling |
| Measured behavior (Victor's M3 Ultra, synthetic weights at 8B shapes, T = 128) | proof-only 32.5 to 34.2 tokens/s; production stream 32.4 to 32.6; one request about 18 to 24; receipt verification about 2.3 s; classifier app stream 16.8 tokens/s |
| Proven guarantees (Lean, for models of the code) | hiding lemmas for openings, sumcheck masks, Merkle salts and `M`; soundness of sumcheck, LogUp, proximity and column tests; Merkle binding and straight-line extraction; Fiat-Shamir on the chain with composition; per-block knowledge soundness at all 26 Shieldstral layers (`block_knowledge_r13_shield`) |
| Counted (paper accounting) | whole-run interactive soundness about 2^-97.78 for 8B T128 at W16R2, Q = 280; target `q·2^-100 + 2^-100` |
| Proposed or ahead | a closed end-to-end theorem at a concrete instance; run-level completeness and zero knowledge; production acceptance by a Lean verifier; W16R3 profile; RTX 5090 CUDA port; throughput at or above 110 tokens/s (D64); P3 weight hiding |

## 3. FlashProve comparison matrix

The two systems answer complementary questions with related hash-based toolkits and different commitment designs. Throughput figures come from different hardware, workloads and privacy models, so they sit side by side as context rather than as a ranking.

| Dimension | FlashProve 0.16.0 (`9e2bdd8f`) | IntelligenceRegulation P1 (`eee3eb57`) |
| --- | --- | --- |
| Question answered | which committed model produced this reply? | did the approved public model produce this result on private data? |
| Hidden | model weights (and which experts ran) | inputs, outputs, intermediate activations |
| Public | prompt, reply, architecture, quantization scales, a served-or-refused bit | weights, shapes, T, d, L, a served bit, a chosen output part (verdict) |
| Model and scale shown | Llama 4 Maverick, public 4-bit conversion, 1,024-token context | Llama-3-8B shapes with synthetic weights at T = 128; Shieldstral-1.0-3B classifier at T = 128; TinyLlama-1.1B |
| Throughput | 111.23 ± 0.92 tokens/s prefill at 24 requests per batch; 17.41 ± 0.15 at one request (`guide/performance.md`) | 32.5 to 34.2 tokens/s proof-only, one request; 32.4 to 32.6 production stream (`MVP_STATUS.md`) |
| Hardware | one NVIDIA H100 80 GB, CUDA 13.2 | one Apple M3 Ultra (Metal and CPU); CUDA path for RTX 5090 planned |
| Proof and verification | 18.78 MB per proof; about 21 s on one CPU thread | receipt verification about 2.3 s for the 8B T128 request (REPORTED) |
| Field | Goldilocks with Reed-Solomon codes (field 0); 2^61 − 1 with circle codes (field 1); a larger field for challenges | Goldilocks with its quadratic extension F\_p\[u\]/(u² − 7) for challenges |
| Hash | BLAKE2b, modelled as a random oracle | BLAKE3, modelled as a random oracle (D19) |
| Commitment and proximity | zero-knowledge IOPP for constrained interleaved codes (Chiesa, Fenzi, Weissenberg, ePrint 2026/391): folds, code switching, distances up to the Johnson radius with out-of-domain samples, proof of work before position sampling | Ligero-style direct column test on Reed-Solomon rows at the unique-decoding radius (δ/3 at rate 1/4, δ/2 at rate 1/2 under D59), pad rows for hiding |
| Sumcheck | zero-knowledge sumcheck with the paper's hiding polynomial | sumcheck with CFS masking polynomials opened from a mask commitment `M` |
| Lookups | log-derivative family (cites Papini and Haböck 2023/1284, Haböck 2022/1530, Arya, Celer) | LogUp with committed helper columns and a (β, γ) tuple fold |
| Fiat-Shamir | hash chain; challenges recomputed by the verifier | hash chain; vector challenges by repeated squeezes |
| Arithmetic semantics | exact integer model; range checks keep equations from holding only modulo the prime | exact integer model; range checks carry the same role (`CircuitIff`) |
| Security statements | `sound`, `soundAndBinding`, `completeOnCanServe`, `zeroKnowledgeOnCanServe`, `refusedHandsOutNoProof`, `repliesFit` | `CircuitIff`, `Complete`, `KnowledgeSound`, `Binding`, `ZeroKnowledgeL`, `SemanticHidingL`, gate `ProductionReadyL` |
| Error figures | soundness about q/2^124 + 2^-101; completeness 2^-40; zero knowledge at most 2^-154 within 2^64 queries and 688,127 replies | targets: soundness and binding q·2^-100 + 2^-100; completeness 2^-40; zero knowledge q·2^-128 + R·2^-120 for q, R ≤ 2^64 |
| Lean status | six closed theorems about one concrete Lean verifier at full size; `sound` also accepted by the independent checker nanoda | approved statements; component and per-block theorems proved; the run-level gate proved from named premises (section 4) |
| Lean scale (counted in each clone) | 29,563 `.lean` files, about 6.0 million lines, Lean 4.29.1 | 497 `.lean` files, about 180,000 lines plus 2,882 adapted lines, Lean 4.34.1 |
| Tie from Lean to programs | C++ verifier and CUDA prover tested against Lean; batches outside the completeness and zero-knowledge theorems | Rust verifier parts mirrored in executable Lean and tested on development receipts; whole-run Lean verifier ahead |
| Semantic-hiding corollary | absent | stated (`SemanticHidingL`) and derived generically from zero knowledge (`semanticHiding_of_zeroKnowledge`) |
| Maintenance and licence | research artifact, unmaintained, Apache-2.0 | active research prototype, Apache-2.0 |

### 3.1 Chronology

Dates for IntelligenceRegulation are commit author dates from the repository's history; dates for FlashProve are its commit date and press coverage.

| Date | Event | Evidence |
| --- | --- | --- |
| 2025-12-07 | First commits: README with the governance vision, ComputationMonitor | `8aa304b` |
| 2026-06-09 | zkMatrix proof-of-concept plan and prototypes | `6f7a854`, `90bf653` |
| 2026-07-03 to 07-10 | Lattice route; Goldilocks NTT; LogUp-GKR literature review and design | `c9c8856`, `0856f72`, `c509160` |
| 2026-09-02 | Hashline skeleton (Goldilocks, Fp2, NTT, BLAKE3 Merkle, transcript), sumcheck engine with Ligero/Brakedown-class PCS, first zero-knowledge lane | `f56c0b3`, `34e7dd2` |
| 2026-09-04 to 09-09 | P1 and P3 privacy sets recorded and reaffirmed | `ZK60_PRIVACY_REQUIREMENTS.md` |
| 2026-09-20 | Random-oracle modelling accepted (D19); first run-level privacy gate | `ZK60_DECISIONS.md`, `9e3e129` |
| 2026-10-30 | FlashProve initial public release commit | `9e2bdd8f` |
| 2026-11-02 | FlashProve announced | press coverage |
| 2026-11-04 | Repository made public (D62), Apache-2.0 licence, D63 Lean rule, statements approved, first mention of FlashProve in commits, 15 FlashProve Lean files adapted with attribution, throughput target raised to FlashProve's level (D64) | `19178f3`, `ac38c07`, NOTICE |
| 2026-11-04 | F12 soundness defect found by Lean and fixed | `MVP_STATUS.md`, `SoundMProduct.lean` |
| 2026-11-10 | Gap audits; rulings D76 to D78; Lean lane L57 checked on the merged tree | HEAD `eee3eb57` |

### 3.2 Attribution reading

- **Shared ingredients are published prior art.** Goldilocks, Reed-Solomon proximity testing, Merkle commitments, sumcheck, log-derivative lookups, lookup-table nonlinearities and Fiat-Shamir in the random-oracle model appear in both; FlashProve's `PUBLISHED-WORKS.md` cites its sources part by part, and Hashline's README names Ligero and Brakedown.
- **The designs diverge where it counts.** The proximity layer (folding and code switching at the Johnson radius versus a direct column test at unique decoding), the privacy model (weights versus data) and the statement set differ.
- **One direct reuse exists, and it is credited.** Fifteen Lean files under `formal/ZK60Formal/ThirdParty/FlashProve/` are adapted from FlashProve under Apache-2.0, recorded in NOTICE with the upstream commit; this review's diff confirms the match (section 5).
- **Timing.** Hashline's core design is recorded in commits dated two months before FlashProve's release; the repository became public two days after the announcement, so those earlier dates rest on the author-recorded history. FlashProve's repository contains no reference to Victor's project (grep, RE-RUN).
- **Conclusion (INFERRED).** The evidence read supports independent development along a shared public literature, followed by open, attributed reuse of FlashProve's Lean coding-theory library by IntelligenceRegulation.

## 4. Formal verification and security-obligation inventory

The D63 statements are precisely written and approved; the components beneath them are proved; the end-to-end theorem about the running app is the open work. Ruling D63 (Victor, 2026-11-04) holds every profile out of production until both statements are proved in Lean.

### 4.1 The declarations in `formal/ZK60Formal/Statements.lean`

| Declaration | What it states | Status at `eee3eb57` |
| --- | --- | --- |
| `CircuitIff` | constraints are satisfiable for (x, y) exactly when x is admissible and y is the integer model's output | proved for the sanity instance (`trivialArith_circuitIff`) and for the app's per-block-shape model (`shield_circuitIff`, `RunShapeShield.lean:265`); on its own it constrains the protocol only through `KnowledgeSound` (audit GB-9) |
| `Complete` | honest receipts are accepted with the model's public output, except with probability εc | statement approved; target arithmetic proved; the run's honest-segment obligations O8 to O10 are open premises |
| `KnowledgeSound` | a straight-line extractor recovers an admissible input behind the commitment, except with probability εs(q) | proved per opening, per sub-protocol and per block; at run level proved from named premises |
| `Binding` | each commitment opens to one value, except with probability εb(q) | proved for the classify input commitment at its real geometry (radius 768 of 2,048 columns; lane L48, instance `classifyProtocolUExecEp`) |
| `ZeroKnowledge`, `SemanticHiding`, `ProductionReady` | instance-leak forms, where the instance declares its own leakage | retained for the existing proofs; superseded as approved statements by ruling D76; bridged in `StatementsD76Bridge.lean` |
| `ZeroKnowledgeL` | one simulator, shown only the public output and the named leakage Λ, for q, R ≤ 2^64 | approved statement; ingredients proved (`Hiding*.lean`); the run's zero knowledge enters the gate as premise O12 |
| `SemanticHidingL` | any property of the hidden input is guessed at most ε better with a receipt than from the public part and Λ | approved statement; follows generically from zero knowledge (`semanticHiding_of_zeroKnowledge`, `Assembly.lean:264`) |
| `ProductionReadyL` | the gate: all of the above at targets εc = 2^-40, εs = εb = q·2^-100 + 2^-100, εzk = q·2^-128 + R·2^-120 | conditional top theorems; the latest are `stgAlg_productionReadyL_epP_exec_view` and `_exec_real` (`RunStgAlgTop.lean`, `RunStgAlgTopR.lean`); `leaky_not_productionReadyL` shows the gate rejects a protocol that publishes its input |

### 4.2 What is proved beneath the gate (READ; build status REPORTED)

| Layer | Representative theorems | Files |
| --- | --- | --- |
| Hiding of openings and masks | `openedValues_uniform`, `openingView_law_eq`, `cfsView_law_eq`, `mOpenView_law_eq`, `merkle_hiding`, `block_view_law_eq` | `Hiding*.lean` |
| Refusal bit | `refusal_output_must_be_leaked`, `logup_attempt_prob_le` | `HidingRefusal.lean` |
| Interactive soundness | `schwartzZippel`, `sumcheck_sound`, `logup_block_bound`, `zerocheck_sound` | `Sound*.lean` |
| Commitment tests | `column_test_sound`, `rs_proximity_third`, `rs_proximity_half`, `opening_sound`, `groups_sound`, `mopening_sound` | `SoundColumnTest.lean`, `SoundProximity*.lean`, `SoundOpening.lean`, `SoundGroups.lean`, `SoundMProduct.lean` |
| Random-oracle layer | `collision_prob_le`, `merkle_binding`, `extract_sound`, `opening_sound_extracted` | `SoundRO.lean`, `SoundMerkle.lean`, `SoundExtract.lean`, `SoundOpeningRO.lean` |
| Fiat-Shamir | `fs_sound_of_rbr`, `chain_sound`, `chain_sound_wide`, `fs_logup_chain_sound`, `fs_opening_knowledge_code`, `fs_chain_sound_sched` | `FS*.lean` |
| Blocks | `block_knowledge_r13_shield` (all 26 real layers), `block_knowledge_r13_rung`, `block_knowledge_look_w16r2_rung` | `BlockR13StmtDone.lean`, `BlockLookDone.lean` |
| Run | header, verdict link, closing openings at real geometry, input-root extraction, alive and doom covers in part | `Run*.lean` |

The repository reports each lane's files as building with zero `sorry` and with axioms limited to `propext`, `Classical.choice` and `Quot.sound`, via `results/zk60_lean_resume_20261109/check_lean_merge.sh`. This review's static scan agrees on the absence of `sorry`, `axiom` and `native_decide`; the build and the `#print axioms` output are REPORTED.

### 4.3 Remaining security obligations at HEAD

| Obligation | Kind | State |
| --- | --- | --- |
| Stage covers `hdin`, `hdout`, input endpoint `hdzero`; stages' define, LogUp and doom facts; the "claims true" link | soundness, run level | open; lane L60 named as owner |
| Wiring the proved block statement into the run (`hblk`) | soundness, run level | waits on boundary-slot widening (L46-3, L56-3) |
| Input endpoint's extractor group (`hread`, `hE`, `mk`) | soundness | open; lane L58 |
| O8 to O10: honest segments accepted; refusals only at counted sites | completeness | open; slot arithmetic ahead |
| O12: zero knowledge of the whole run | privacy | assumed as a premise (audit GA-2); block-level ingredients proved |
| A concrete Shieldstral T128 instance with the public data as a Lean value | instance | ahead (GA-4, GB-3) |
| An executable whole-run Lean verifier, run on real T128 receipts | Lean-to-code tie | ahead (GB-4, GB-6); approved as the production acceptance rule in D63 §6.3 |
| Lean mirrors for CLI door checks, pre-header checks, run header, block pre-checks | Lean-to-code tie | ahead (GB-5) |
| Token-I/O 8B run: a protocol instance and gate statement | scope | ahead; the current gate targets the classifier run |
| D55 fork-join composition | scope | the classify path is the sequential D12a verifier; D55 soundness accounting is a shipping condition of ruling D55 |
| D79: where the classify run absorbs the input root | ruling | open with Victor; the Lean side is already proved for the code as written |

### 4.4 Assumptions a reader accepts

- BLAKE3 as a random oracle, in the stronger reading that its compression function is ideal (D19b).
- The Lean verifier and honest prover equal the Rust and Metal programs; today this rests on tests at development shapes (T = 32, one or two blocks, mostly synthetic weights) plus one real Shieldstral layer-0 check.
- The Lean integer model equals the code's forward pass; compared on one synthetic block and one width-16 rung (GB-8).
- Masks are uniform; the code draws them from a CSPRNG seeded by OS entropy.
- Weights are public (P1). P3 requires a new statement, since the current simulator receives the weights (GB-13).
- Timing and other side channels sit outside every theorem; lane notes already record two data-dependent fast paths for the privacy gate to watch.

### 4.5 Relationship between the formal statements and the implementation

The Lean models follow the code closely, including its departures from textbook protocols, and that closeness has produced results in both directions. Lean found the F12 soundness defect in Rust; the code in turn exposed thirteen premises in Lean that the real run could never meet, each repaired in Lean. The production path today is the Rust verifier; the Lean verifier becomes the acceptance authority once the executable whole-run form exists.

## 5. Reproducibility and evidence assessment

The repository's internal evidence discipline is strong; evidence produced by a second party on a second machine is the missing layer.

### 5.1 What this review re-ran

| Check | Method | Result |
| --- | --- | --- |
| Fork equals upstream | `git ls-remote` on both | both `main` at `eee3eb57` |
| FlashProve attribution | diff of the 15 files under `ThirdParty/FlashProve/` against FlashProve `lean/` at `9e2bdd8f` | 15 of 15 have an upstream file at the same relative path; 12 differ by 2 to 11 lines (headers, module paths, small fixes); `Prob/Count.lean`, `Code/Third.lean` and `Code/Half.lean` are cut down, as the NOTICE says |
| Proof hygiene, static | grep over 497 `.lean` files | zero `sorry`, `admit`, `axiom` or `native_decide` uses outside comments; `autoImplicit = false` in `lakefile.toml` |
| Cited declarations exist | grep for 46 theorem and definition names cited by `README`, `MVP_STATUS.md` and the lane documents | 46 of 46 found at the stated files |
| `zkp-core` unit tests | `cargo test --locked --lib`, x86-64 Linux, 2 cores, debug profile | 83 passed, 0 failed, 2 ignored |
| Hashline library tests | same, on `ops/zkp-mvp/gpu-metal/hashline`, CPU only | 326 of 1,073 passed with 0 failures when this report closed; the run was time-limited on a 2-core debug build |

The Rust result is new evidence in a small way: the repository's records come from an Apple M3 Ultra and an earlier WSL laptop, and these tests also pass on a third, unrelated x86-64 machine.

### 5.2 Strengths of the existing evidence

- **Labelled numbers.** Every figure carries MEASURED, COUNTED, MODEL, ESTIMATE or EXTERNAL, and lane documents separate PROVED, CHECKED and ARGUED.
- **Negative controls.** Lean-versus-Rust comparisons record deliberately altered copies being refused (for example 27 of 27, 25 of 25).
- **A/B timing in both orders** for performance changes, with receipts verified and byte-identity gates across CPU and GPU.
- **A decisions register** (D1 to D79) with dated rulings, and corrections recorded when a number was wrong (D77a).
- **Self-reported gaps.** The two gap audits of 2026-11-10 list the open premises and the faithfulness limits more severely than an outside reader would on first pass.

### 5.3 Gaps an outside reproducer meets

| Gap | Evidence | Effect |
| --- | --- | --- |
| Front page lags the tree | `README.md` "Where it stands (2026-11-04)" says the Lean proofs are ahead; `MVP_STATUS.md` records proof lanes through L57 by 2026-11-10 | a first-time reader underestimates the formal work and misses the audit's caveats |
| Privacy-gate records and the F12 fix | `MVP_STATUS.md` states the D55 gate records and all `/1` captures were invalidated by the fix; this review found no record there of a re-gate on `/2` bundles | the README's gate sentence describes pre-fix bytes |
| Machine-specific tooling | 40 files under `scripts/` and the Lean check folder hard-code `/Users/victorrielly/...` or `/home/victor/...` | check scripts need editing before a second party can run them |
| Large artifacts outside the repository | `SNAPSHOT_20261017_EXCLUDED_LARGE_FILES.json` lists 14,914 excluded files; `CLAUDE.md` puts about 446 GiB on the retired laptop | receipts and corpora behind several CHECKED claims are unavailable to a cloner |
| Continuous integration | the repository has no `.github` directory | every build and axiom audit is a local run on the author's machine |
| Independent proof checking | the statements document sets a rule of re-checking with nanoda or lean4checker; this review found no record of such a run | the kernel result rests on one checker |
| Deployed binary | the app's active classifier binary predates the F12 fix (GB-7) | demo receipts carry no soundness claim, as D65 already says |
| Single author and agent lanes | 2,351 commits by one human author; proofs written by AI lanes and checked by a coordinator | human review of statement files and instance fields is the scarce resource |
| Performance on synthetic weights | 8B timings use synthetic diagonal weights at true geometry (`MVP_STATUS.md`) | dense trained-weight cost is unmeasured at 8B |

A small correction for Victor to consider: `ZK60_LEAN_PRODUCTION_STATEMENTS.md` §5 says FlashProve has no leak-hunting check on shipped output; FlashProve's `docs/how-hiding-is-checked.md` describes its self-checks, tests and audits of weight hiding, so the comparison deserves a second look.

## 6. RLT/Lean correspondence opportunities

RLT's strongest contribution here is its discipline around sources, assumptions and correspondence; the cryptographic mathematics belongs in Lean. RLT main (`7d57ae8a`) is a first-order arithmetic checker under Robinson's Q, while IntelligenceRegulation's theorems live in probability over random oracles, finite fields and polynomials.

| Need in IntelligenceRegulation | RLT mechanism on main today | Fit | Extension required |
| --- | --- | --- | --- |
| Source fidelity: pin exactly what was claimed, where | `sources/registry.yaml` with commit pins and verbatim excerpts, checked by `scripts/check_excerpts.py`; `rlt validate` | direct: register IntelligenceRegulation at `eee3eb57` and FlashProve at `9e2bdd8f`, with excerpts of D63, D76, the README claims and `Statements.lean` | none for GitHub-hosted files |
| Detecting drift between the approved English and the Lean text | reviewed transcriptions with hashes; correspondence documents (`docs/…-CORRESPONDENCE.md`) | direct as a review format: one row per declaration, English clause beside Lean clause | none; the content is human review |
| Reading-point conventions: separate proof validity, source fidelity, semantic correspondence | statement records (`rlt-statement/1`) with `kernel`, `source`, `semantic`, `physical` fields; `rlt explain` | maps cleanly onto the project's PROVED, CHECKED, ARGUED labels | a record variant whose proof is a Lean declaration at a pinned commit, since today's record expects an RLT proof file |
| Independent arithmetic verification of parameter facts | kernel proofs of closed natural-number statements under ROBINSON-Q; decimal convention NAT-DEC; Lean comparison files | good for closed facts: 15 × 270,336 = 4,055,040 ≤ 201,326,592; 66,977,792 + 131,072 = 2^26; 2·768 + 256 + 256 = 2,048; 55,852,891 ≤ 67,108,864 | proof generators for multiplication and comparison at eight-digit and nine-digit sizes; feasibility within the 1,000,000-node limit to be measured |
| Assumption tracking for conditional theorems | `rlt deps`, `rlt compose` with conditional assemblies and "discharged by composition" reporting; staleness exit code | the right model for the 47-row premise register and the top theorems' hypothesis lists | a reader for Lean hypothesis lists; RLT composes its own theorems only |
| Evidence correspondence: tie a result folder to the claim it supports | manifests pinned by SHA-256; `research/h45-lemma-12-1/reproduce.sh` pattern | direct as a packaging pattern for a reviewable fork branch | none |
| Field arithmetic, primality of the Goldilocks prime, 7 as a non-residue | outside current practice (bounded primality `Prime_B` reaches small primes) | better served by Lean | substantial; low priority |
| Soundness, zero knowledge, random-oracle bounds | outside the logic | Lean only | out of RLT's scope by design |

In summary: three RLT capabilities transfer today with zero kernel change (source pinning with excerpt checks, correspondence review format, reproducible evidence packaging); two need modest tooling (Lean-backed statement records, arithmetic generators at larger sizes); the security mathematics stays with Lean.

## 7. Prioritized research and demonstration roadmap

Nine candidates, ordered by value to IntelligenceRegulation per unit of effort; the first five are achievable from a fork with public inputs, the last four advance the research itself and depend on Victor's machines, corpora or rulings.

| # | Candidate | Type | Effort (ESTIMATE) | Needs Victor | RLT adds value |
| --- | --- | --- | --- | --- | --- |
| R1 | Clean-room Lean rebuild, axiom audit and second kernel | reproducibility | 1 to 2 days | no | pins only |
| R2 | Portable Rust test and receipt-verification run, with the F12 forgery control | reproducibility | 1 day | no | pins only |
| R3 | Statement-fidelity pack: English, Lean and instance fields side by side | verification demonstration | 2 to 3 days | review only | yes |
| R4 | Arithmetic certificates for the run's parameter facts | verification demonstration | 2 to 4 days | no | yes, central |
| R5 | Machine-generated premise register for the top theorem | verification tooling | 3 to 5 days | no | design model |
| R6 | Lean-versus-Rust agreement on a full Shieldstral T128 run | verification demonstration | days, on his machine | yes | no |
| R7 | Privacy re-gate on post-F12 bundles, plus an independent distinguishing experiment | privacy evidence | days | partly | no |
| R8 | Closing run-level soundness: stage covers and the endpoint | research | weeks | coordination | no |
| R9 | Soundness margin and query count: the path from 2^-97.78 to the 100-bit target | research | 1 to 2 weeks of analysis | rulings | no |

### R1. Clean-room Lean rebuild, axiom audit and second kernel

- **Source and claim:** `formal/README.md`: every file builds with zero `sorry`, and `#print axioms` shows only `propext`, `Classical.choice`, `Quot.sound`; `MVP_STATUS.md`: full build of 3,703 jobs; `ZK60_LEAN_PRODUCTION_STATEMENTS.md` §5: a re-check with nanoda or lean4checker.
- **Significance:** converts the central formal claim from the author's report into second-party evidence, and exercises the project's own stated rule.
- **Current status:** REPORTED by the coordinator's scripts on the M3 Ultra; static scan confirmed here; second-kernel run unrecorded.
- **Dependencies and effort:** Lean 4.34.1, Mathlib v4.34.1 with its build cache, a Linux machine with 16 GB or more (the merged check peaked at 9.61 GiB), a path-independent copy of `check_lean_merge.sh`.
- **Expected evidence:** build log with job count, an axiom listing for `stgAlg_productionReadyL_epP_exec_real`, `block_knowledge_r13_shield` and the 46 names in section 5, the checker's verdict, a container recipe and CI workflow in the fork.
- **Accept:** green build, job count equal to the recorded one for this commit, axioms within the three, checker accepts. **Reject:** any `sorry`, extra axiom, failing file or checker refusal, each reported with file and line.
- **RLT:** registers the two pins; the checking is Lean's.

### R2. Portable Rust tests and receipt verification

- **Source and claim:** `MVP_STATUS.md` 2026-11-04: the F12 forgery is reproduced in `hashline/src/zk_f12_tests.rs` and rejected after the fix; old `/1` profile versions are refused by name; `docs/zkmatrix-poc/ZK60_P1_DEMO.md`: a one-command CPU demo with rejection controls.
- **Significance:** shows the verifier's behavior, including its most important fix, on hardware the author has never touched.
- **Current status:** `zkp-core` 83 of 83 passing here; the Hashline suite partly run (326 of 1,073 passing, 0 failing, time-limited).
- **Dependencies and effort:** Rust toolchain, release profile, 8 or more cores for a reasonable wall time; fixtures that live in the repository.
- **Expected evidence:** full test log, the list of tests that need out-of-repository fixtures, demo output with its rejection controls.
- **Accept:** all in-repository tests pass and every tamper control is refused. **Reject:** a failing test or an accepted tampered receipt; a test that needs a missing fixture is recorded as a reproducibility gap.
- **RLT:** none beyond pins.

### R3. Statement-fidelity pack

- **Source and claim:** `ZK60_DECISIONS.md` rows D63 and D76; `ZK60_LEAN_PRODUCTION_STATEMENTS.md` §1 to §4; `Statements.lean`; instance fields `Leak`, `PubOut`, `admissible`, `opensIn` of `classifyProtocolUExecEp`; `classifyLeak`.
- **Significance:** Lean checks proofs; people check that definitions say what was meant. The audit found the gate once admitted a protocol that publishes its input (GB-1, since closed). A compact, pinned, reviewable table is what a regulator or auditor would read first.
- **Current status:** audited internally in the faithfulness audit §2; an outside review is absent.
- **Dependencies and effort:** reading only; optionally further adversarial toy instances in the style of `leaky_not_productionReadyL` (an accept-everything verifier against `KnowledgeSound`, an always-refusing prover against `Complete`).
- **Expected evidence:** RLT source-registry entries with checked excerpts, a correspondence document, the toy theorems in a scratch Lean file outside the library.
- **Accept:** each English clause maps to a Lean clause with differences listed; each toy protocol fails the gate. **Reject:** a toy that passes, which becomes a finding for Victor.
- **RLT:** yes; this is its registry and correspondence workflow applied unchanged.

### R4. Arithmetic certificates for parameter facts

- **Source and claim:** L57 document: 15 × 270,336 = 4,055,040 against 201,326,592; `MVP_STATUS.md`: lookup count 66,977,792 within 2^26 with margin 131,072; R13 budget 55,852,891 of 67,108,864; D77a: radius 768 of 2,048 columns with 256 checked.
- **Significance:** these closed facts are the joints where a transcription slip silently weakens a bound; D77a records one such correction already. Independent certificates in a second prover are cheap and easy for an outsider to read.
- **Current status:** proved in Lean inside larger files; an independent restatement is absent.
- **Dependencies and effort:** RLT proof generators for decimal multiplication and comparison at these sizes; a feasibility measurement against the kernel's node limit comes first.
- **Expected evidence:** RLT proof files, statement records naming the Lean declaration and source excerpt for each number, a Lean comparison file.
- **Accept:** RLT kernel accepts each fact under ROBINSON-Q and the numbers match the pinned excerpts. **Reject:** a mismatch between a documented number and the Lean constant, or a fact beyond the kernel's limits, recorded as such.
- **RLT:** central.

### R5. Machine-generated premise register

- **Source and claim:** `ZK60_LEAN_GAP_AUDIT_PREMISES_20261110.md`: 47 register rows at `2155ede8`; `MVP_STATUS.md`: the citable top theorem changed several times on 2026-11-10 as premises were discharged.
- **Significance:** the list of undischarged hypotheses is the project's true progress meter toward D63. Generating it from the Lean source keeps status pages exact and makes "what remains" checkable by anyone.
- **Current status:** hand-maintained in audit and lane documents.
- **Dependencies and effort:** a Lean metaprogram or script that prints the binders of a named theorem, a classification file (open, bookkeeping, modelling, ruling, public data), a staleness check keyed on the source hash.
- **Expected evidence:** a generated register for `stgAlg_productionReadyL_epP_exec_real`, a diff against the audit's 47 rows, a CI step that fails when the list changes without the classification being updated.
- **Accept:** the generated list reproduces the audit's rows at `2155ede8` and yields the current list at HEAD. **Reject:** premises present in Lean and missing from the documents, reported as findings.
- **RLT:** its composition and dependency reports are the design model; the implementation is Lean-side.

### R6. Lean-versus-Rust agreement on a full Shieldstral T128 run

- **Source and claim:** audit GB-6: every Lean-versus-Rust test is on small development receipts; `MVP_STATUS.md`: layer 0 of the real T128 export agreed on 210 checks with 27 of 27 negative controls, and the seven weight folds wait on a corpus kept outside the repository.
- **Significance:** this is the tie between theorem and program, and the precondition for production acceptance by a Lean verifier (D63 §6.3).
- **Current status:** one layer of 26; whole-run executable verifier ahead.
- **Dependencies and effort:** Victor's corpus and machine, or a published fixture bundle; Shieldstral weights under their licence.
- **Expected evidence:** per-layer check counts, negative-control counts, the corpus manifest with hashes.
- **Accept:** all 26 layers and both stages agree with every control caught. **Reject:** any disagreement, located to layer and check.
- **RLT:** none.

### R7. Privacy evidence after the F12 fix

- **Source and claim:** `README.md`: the 18-part gate passes on all 12 registered D55 bundles (CPU-made) and GPU-made bundles still owe a pass; `MVP_STATUS.md`: those records were invalidated by the F12 byte change.
- **Significance:** zero knowledge of the run is still a premise in Lean (O12), so empirical evidence carries the privacy claim for now.
- **Current status:** pre-fix records; post-fix status to be confirmed with Victor.
- **Dependencies and effort:** the gate tooling and fresh `/2` captures; for an independent experiment, a script written without the gate's code that compares receipt-visible distributions for two inputs sharing the same leakage.
- **Expected evidence:** gate results on `/2` CPU and GPU bundles; the independent experiment's statistics with its power stated.
- **Accept:** 18 of 18 parts on every bundle and no detectable difference at the stated power. **Reject:** any failing part or a reproducible distinguisher.
- **RLT:** none.

### R8. Closing run-level soundness

- **Source and claim:** `MVP_STATUS.md` and the L57 document: open stage facts (`StgDefAt`, `StgLkAt`, `StgDoomAt`), covers `hdin`, `hdout`, `hdzero`, the endpoint extractor group, and the wiring of `block_knowledge_r13_shield` into the run.
- **Significance:** this is the core research path to the first closed theorem of FlashProve's shape for a data-hiding protocol.
- **Current status:** active lanes L58 and L60.
- **Dependencies and effort:** weeks; coordination with Victor's lanes to avoid duplicate work. A self-contained entry point is IN-C's LogUp round-by-round bound, whose model is written in L57 §5 with the proof left open.
- **Expected evidence:** a top theorem with a strictly shorter hypothesis list (measured by R5).
- **Accept:** the premise is removed and the merged check stays green. **Reject:** a proof that needs a changed statement, which goes to Victor as a ruling.
- **RLT:** none.

### R9. Soundness margin and query count

- **Source and claim:** `ZK60_LEAN_PRODUCTION_STATEMENTS.md` §3: interactive whole-run count 2^-97.78 at W16R2, Q = 280, against a target of 100 bits per query; D59: rate 1/2 at the unique-decoding radius, conditional on due diligence; D27.
- **Significance:** the target must be met or re-ruled before production; the choice interacts with speed (D64 asks for 110 tokens/s). FlashProve's public design shows two levers this project has yet to use: proof-of-work grinding and proximity testing beyond unique decoding with out-of-domain samples.
- **Current status:** counted on paper; the q-dependent Lean figure at a concrete instance is ahead.
- **Dependencies and effort:** analysis first; any protocol change means a new profile version, a re-proof and a privacy re-gate.
- **Expected evidence:** a table of options (larger challenge field, grinding bits, column count, code-switching) with soundness, proof size and prover cost for each, checked against the Lean per-opening theorems.
- **Accept:** an option meeting 100 bits at the 8B T128 workload with measured cost. **Reject:** options that reach the target only by weakening the approved statements.
- **RLT:** none; parameter arithmetic from the chosen option could later feed R4.

## 8. Outstanding questions for Victor

These are collected for a later conversation; this review made no contact.

1. **Public statement.** Where is the text containing "How can we develop intelligence at a manageable rate worldwide?", and is `docs/VISION.md` still the current statement of purpose?
2. **Public history.** On what date did the repository first become public, and does any external timestamp (a preprint, a talk, the two zkMatrix PDFs in the root) anchor the September design dates?
3. **Privacy gate after F12.** Has the 18-part gate been re-run on `/2` bundles, CPU-made and GPU-made? Which sentence should the README carry today?
4. **Second kernel.** Has nanoda or lean4checker been run over the merged tree, as the statements document's rule says?
5. **Reproduction kit.** Would a path-independent copy of `check_lean_merge.sh` and a CI workflow be welcome as a contribution? Which fixtures from the 446 GiB outside the repository could be published as a small hashed bundle?
6. **Help wanted.** Which open premises are free for an outside contributor without colliding with lanes L58 and L60?
7. **Soundness target.** Is the plan to reach 100 bits per query by parameters (field, grinding, columns), or to rule on a lower target for a first production profile?
8. **D55 and the gate.** Will the fork-join run get its own `ProductionReadyL` instance, or is the sequential D12a run the first production target?
9. **Token-I/O.** When does the 8B next-token run get a protocol instance in Lean, given W16R3 (D78) folds the token stages into the next profile?
10. **P3.** Is reuse of FlashProve's weight-hiding construction under consideration for P3, and does the statement need a simulator without access to the weights (GB-13) before that work starts?
11. **Trained weights at 8B.** Is a dense trained-weight timing planned on the M3 Ultra before the RTX 5090 port?
12. **Governance link.** How does a P1 receipt connect to the vision's model-approval registry: who publishes the approved weights digest, and where does a verifier obtain it?

## 9. Recommended first implementation phase

Begin with R1 to R4 as one evidence branch on the fork; together they take about one to two weeks, use public inputs only, and give Victor four things he can assess independently. This phase waits for approval; this review stops here.

| Step | Deliverable in the fork branch | Done when |
| --- | --- | --- |
| 1. Pin and register | `evidence/PINS.md`; RLT registry entries for both repositories with checked excerpts | `rlt validate` passes on the registry |
| 2. R1 Lean rebuild | container recipe, CI workflow, build log, axiom listing, second-kernel verdict | acceptance criteria of R1 met, or findings filed in the branch |
| 3. R2 Rust run | full test log on Linux x86-64, F12 forgery control, demo output | acceptance criteria of R2 met, with a list of fixture gaps |
| 4. R3 statement pack | correspondence document for the seven approved declarations and four instance fields; scratch toy theorems | each clause mapped; toys fail the gate |
| 5. R4 arithmetic | feasibility note, then RLT certificates for the four parameter facts with Lean comparison | kernel accepts, numbers match excerpts |
| 6. Hand-off note | one page: what was reproduced, what differed, the open questions of section 8 | ready for Victor to read in ten minutes |

Constraints carried into that phase: library Lean files, Rust sources and shared documents stay unchanged; new files live under one `evidence/` folder; authorship and NOTICE attributions are preserved; GPU work stays out of scope. R5 follows naturally once R1's build environment exists.

## Scope and limits of this review

- **Read-only.** No source change, commit, pull request, issue or outreach was made. Build output for the Rust tests went to a temporary directory outside the checkout.
- **Lean build.** The workspace had 2 cores and 7 GB of memory, below the 9.61 GiB peak the project records; Lean proof status is therefore REPORTED plus a static scan.
- **Coverage.** The tree holds 113,051 files. This review read the README, NOTICE, SECURITY, VISION, `Statements.lean`, the production-statements document, both gap audits, the top 30 KB of `MVP_STATUS.md`, the L57 lane document, selected rulings, and directory inventories; the 714 result folders were sampled by name.
- **Rust sources.** Hashline's source was inventoried and its tests run; a line-by-line security review of the prover was outside scope.
- **GPU.** No GPU experiment was run; all performance figures are the repository's.
- **Chronology.** Commit dates are author-recorded; press dates are as printed.
- **Inputs unavailable.** Victor's public statement, the VR-001 and VR-002 summaries, and the FlashProve paper's full text (the PDF is in the clone; its content was read through the repository's documents).

## Sources

- [VictorRielly/IntelligenceRegulation](https://github.com/VictorRielly/IntelligenceRegulation) and the fork [thinkthoughts/IntelligenceRegulation](https://github.com/thinkthoughts/IntelligenceRegulation), commit `eee3eb57`
- [anthropics/FlashProve](https://github.com/anthropics/FlashProve), commit `9e2bdd8f`, version 0.16.0
- [thinkthoughts/rlt](https://github.com/thinkthoughts/rlt), commit `7d57ae8a`
- [Anthropic open-sources FlashProve to prove which AI model wrote an answer](https://thenextweb.com/news/anthropic-flashprove-provable-inference-ai-model-identity), The Next Web, 2026-11-05
- [Anthropic Open-Sources FlashProve: What Provable LLM Inference Means for Developers](https://dkwebsolutions.medium.com/anthropic-open-sources-flashprove-what-provable-llm-inference-means-for-developers-9b1cb804223f) (search result; announcement date 2026-11-02)
