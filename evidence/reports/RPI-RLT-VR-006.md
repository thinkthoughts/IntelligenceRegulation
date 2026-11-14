# RPI-RLT-VR-006 — Lean premise inventory reconciliation

> **Independent external review.** Written for the fork `thinkthoughts/IntelligenceRegulation` by an outside
> reviewer working with Claude (Anthropic). Victor Rielly, the author of IntelligenceRegulation, has had no part
> in it and has neither reviewed nor endorsed it. Index: [../README.md](../README.md).

2026-11-14 · thinkthoughts · reviewed commit `eee3eb5717dea88d0fc48dc00f6aef389d52af3a` · built on review
commit `41f67ade9ea201432fb0fec94280d1c81d9094ca`

## 1. Summary

1. **The VPS evidence is in the repository and its hashes verify.** The Lean library builds completely (3,840
   jobs) on a 15 GiB machine; the audited theorem and three other top theorems depend on `propext`,
   `Classical.choice` and `Quot.sound`; `leanchecker` accepts the run-level module at a 3.10 GiB peak. These rows
   move from "reported" to "logged". The whole-library replay left an empty log, so its memory failure stays
   reported (section 2).
2. **All 108 differences between Lean's list and VR-005's classification are explained.** 86 are the same
   hypotheses at a finer grain, 12 are conjunctions the tool split in two, and 6 are keys VR-005 lacked. Every
   section variable is a binder, and every one of Lean's 88 propositional binders except one type-class argument
   was already in VR-005 (section 3).
3. **The normalized inventory has 173 keys, each traced to Lean's 179.** 31 are open obligations, 19 are
   discharged conditionally elsewhere in the repository, 63 are bookkeeping, 58 public instance data, 2 modelling
   (section 4).
4. **VR-005 is corrected in three places.** `hD` is five open obligations and ten side conditions, where VR-005
   had one open row. The extractor's `mk` is an open obligation VR-005 omitted. And a merged top theorem would
   *exchange* hypotheses: VR-005's sentence that it "would shorten this list by 18" was wrong (section 5).
5. **Every "discharged" row is a conditional discharge.** Each is supplied by a parallel top theorem or a lemma
   that has hypotheses of its own; section 6 names them. Zero of the 31 open obligations is discharged on any of
   the four top theorems.
6. **Checks:** eight consistency checks pass on the committed evidence, and ten positive and negative tests of
   those checks pass (section 7).

The standing distinction holds. Lean confirms a proof term: if every hypothesis holds, `ProductionReadyL` follows
for a verifier given as parameters. A production guarantee needs each hypothesis established for one concrete
instance. Nothing in this report claims that guarantee.

## 2. The VPS evidence

Folder: [`../results/R1-lean-vps/`](../results/R1-lean-vps/). Committed by the fork owner in `41f67ade`.
`sha256sum -c SHA256SUMS`: 6 of 6 files agree (re-run by this review).

| Item | What the log shows | File |
|---|---|---|
| Machine | Ubuntu, Linux 6.8.0-138, x86-64, 4 cores, 15,992 MB RAM, 8 GB swap file | `environment.txt`, `environment-summary.txt` |
| Toolchain | Lean 4.34.1 (commit `5045d005`), Lake 5.0.0 | `environment.txt` |
| Commit | the summary names review commit `1bd9ebf`; `environment.txt` names `8482b31`. `formal/` is identical at both and equals `eee3eb57` | both files |
| `lake build` | `Build completed successfully (3840 jobs)`; 468 lines `Built ZK60Formal…` (452 modules of the default target, 15 adapted FlashProve files, the root); zero error lines. The log begins at job 3335, where the library's own modules start | `02-lake-build.log` |
| The module that failed in VR-004 | `Built ZK60Formal.RunExtractClassify (141s)` | `02-lake-build.log` |
| The audited module | `Built ZK60Formal.RunStgAlgTopR (10s)` | `02-lake-build.log` |
| Axioms | `rt_productionReady_r13`, `cb_productionReadyL_epP_codeF`, `stgAlg_productionReadyL_epP_exec_view`, `stgAlg_productionReadyL_epP_exec_real`: `propext`, `Classical.choice`, `Quot.sound`. Six further theorems the same; `trivialArith_circuitIff`: none | `03-axioms-premises.log` |
| Shape of the audited theorem | 196 binders = 92 data + 16 instance + 88 propositional hypotheses; conclusion head `ZK60.ProductionReadyL` | `03-axioms-premises.log` |
| `leanchecker ZK60Formal.RunStgAlgTopR` | exit status 0; 46.9 s; maximum resident set 3,248,856 kB (3.10 GiB) | `05-run-level-checker.log` |
| `leanchecker ZK60Formal`, whole library | the log file is empty (0 bytes). The memory failure (exit 137) is the fork owner's report; the folder holds no output for it | `04-leanchecker.log` |

Status of R1 after this evidence:

| Claim | VR-005 | Now |
|---|---|---|
| Complete build at `eee3eb57` on a second machine | reported | logged |
| Axioms of the central theorem | reported | logged |
| Kernel replay of the run-level module by `leanchecker` | reported | logged |
| Kernel replay of the other run-level modules | open | open; `scripts/r1-leanchecker-per-module.sh` does it one module per process |
| A separate kernel implementation (nanoda) | open | open |

`leanchecker` is Lean's own kernel run again over compiled files. Its acceptance of one module covers that
module's declarations, with imports taken as compiled.

## 3. Reconciling the inventories

Inputs, all preserved byte for byte: `results/R5-premises/inventory-lean.json` (Lean, SHA-256 `9d277a9f…`, equal to
the hash its generation log recorded), `inventory-static.json` (source text), `classification.tsv` (VR-005, 103
rows), `classification-check-lean.log` (108 differences).

### 3.1 Lean's list and the source text agree on the binders

| Count | Lean | Source text |
|---|---|---|
| Binders | 196 | 196 (173 in the statement + 23 section variables) |
| Named binders, in order | 179 names | the same 179 names in the same order |
| Instance binders | 17 | 17 |
| Propositional binders | 88 | 87 with names VR-005 treated as hypotheses, plus one instance |

Lean reports 16 instance binders in the VPS log and 17 in the JSON: the log counts as "instance" only those that
are data, and counts the seventeenth, `[Nonempty Coins]`, among the 88 propositions.

**Section variables.** VR-005 called the 23 section variables "candidates". Lean includes all 23. The two that are
hypotheses, `hpos` and `msg_place`, were already classified.

### 3.2 The 108 differences

The checker required 179 keys and found 103: 92 "missing" and 16 "extra".

| Class | Lean keys | What happened | Example |
|---|---|---|---|
| Matched | 87 | same key on both sides | `hblk`, `O.zk` |
| Nested proof fields of a bundle VR-005 classified as one row | 74 | Lean opens the bundle; VR-005 had the parent | `hD` → 15 fields; `hv` → 5; `hIA`, `hIH`, `hOA`, `hOH`, `hBA`, `hBH` → 7 each; `hb0`, `hbL` → 6 each |
| Conjunction split by the tool | 12 | `And` is a structure in Lean, so the tool listed `.left` and `.right` | `hW`, `hNin`, `hNout`, `hE`, `hwin`, `hread` |
| New: data binder with proof fields | 3 | VR-005's text reader could not see inside | `site`, `T`, `mk` |
| New: library type invariant | 2 | the tool listed the bound proof of `Fin` and the no-duplicates proof of `Finset` | `place`, `Xx` |
| New: instance parameter | 1 | a proposition-valued type-class argument | `inst` (`Nonempty Coins`) |
| **Total** | **179** | | |

The 92 "missing" are 74 + 12 + 6. The 16 "extra" are the ten bundle parents and the six conjunctions, which VR-005
keyed by the parent's name.

**Genuinely omitted hypotheses.** Among Lean's propositional binders: one, the instance `Nonempty Coins`, which
holds for any inhabited coin type. Among data binders that carry proofs: `site`, `T` and `mk`. Of all six new
keys, `mk` is the one that changes the list of open obligations.

### 3.3 Normalization

Rules ([`../scripts/r6_rules.json`](../scripts/r6_rules.json)), applied by
[`../scripts/r6_reconcile.py`](../scripts/r6_reconcile.py):

- a conjunction is one key, the binder's name;
- a hypothesis bundle stays split into its fields; a field inherits its parent's VR-005 category unless a rule
  gives it its own (seven fields of `hD` have their own);
- a data binder whose only listed proofs are a library type's invariants is one key, marked as such;
- every other key is as Lean lists it.

Outputs in [`../results/R6-reconciliation/`](../results/R6-reconciliation/):

| File | Content |
|---|---|
| `lean-key-map.tsv` | 179 rows: Lean key, binder index, kind, type head, normalized key, the VR-005 row it traces to, discrepancy class |
| `classification-normalized.tsv` | 173 rows: key, category, status, evidence, note, VR-005 category, change |
| `parallel-lines.json`, `discharge-audit.tsv` | section 6 |
| `check.log`, `tests.log` | section 7 |

## 4. The normalized classification

| Category | VR-005 (103 rows) | Normalized (173 keys) | Reason for the change |
|---|---|---|---|
| Open cryptographic or protocol obligation | 26 | 31 | `hD` (1) becomes 5 open fields; `mk` added |
| Discharged elsewhere, conditionally | 18 | 19 | `T` added |
| Bookkeeping or composition | 37 | 63 | bundle fields listed one by one; `site`, `place`, `Xx` |
| Public instance data | 20 | 58 | 42 geometry fields of the six commitment bundles; `hD.hK`; `inst` |
| Modelling assumption | 2 | 2 | unchanged |
| Requires Victor's ruling | 0 | 0 | unchanged (D79 remains the adjacent item, VR-005 §4.5) |

93 keys keep their VR-005 row unchanged, 59 are a parent's row repeated per field, 15 are refined from `hD`, and 6
are new. The larger totals are a finer grain; the set of obligations grew by `mk` and by the split of `hD`.

### 4.1 The remaining open obligations, exactly

31 keys: 22 whole hypotheses, 5 fields of `hD`, 4 fields of `O`.

| Group | Keys | Status in the repository's documents |
|---|---|---|
| Stage soundness on the transcript | `hdinS`, `hdoutS` | LEFT |
| Stage facts | `hTrI`, `hTrO`, `hDI_stg`, `hDO_stg`, `hLI_stg`, `hLO_stg` | ARGUED or LEFT |
| Block theorem wired into the run | `hblk` | proved at block level (`block_knowledge_r13_shield`); the wiring LEFT |
| Block facts at the run | `hsl_blk`, `hR0_blk`, `hR1_blk`, `hH0_blk`, `hH1_blk`, `hLU_blk` | ARGUED, LEFT |
| Input endpoint and its extractor | `hE`, `hread`, `hops`, `hcan`, `hdzero`, `mk` | NOT STARTED or LEFT |
| Kinds data: define schedules and LogUp | `hD.r0`, `hD.r1`, `hD.h0`, `hD.h1`, `hD.lu` | PARTLY PROVED: round-by-round soundness from the degree is proved; stage define degrees ARGUED; IN-C's LogUp bound LEFT |
| Completeness | `O.parts`, `O.refuse`, `O.counts` | OPEN (O8 to O10) |
| Zero knowledge | `O.zk`, with `hzk` | OPEN (O12), assumed as a premise |

The status words are the repository's own, taken from Victor's lane documents; the evidence column of
`classification-normalized.tsv` cites the place for each row.

## 5. Changes to VR-005

VR-005 stays as published. These points replace statements in it.

| VR-005 said | Correction |
|---|---|
| §4.1: 103 rows; 26 open, 18 discharged, 37 bookkeeping, 20 instance data, 2 modelling | 173 normalized keys; 31, 19, 63, 58, 2 |
| §4.2: `hD` is one open row, "partly proved" | five fields are open (`r0`, `r1`, `h0`, `h1`, `lu`); `hK` is instance data; nine fields are side conditions |
| §4.2: input-endpoint group `hE`, `hread`, `hops`, `hcan`, `hdzero` | add `mk`, the opening data an extractor can build (`SaltMk`, four proof fields). VR-003 §4.3 had named it |
| §3: section variables are "candidates; Lean decides" | all 23 are binders |
| §4, opening: "Lean's list may add proof fields inside `T`, `D`, `mk`" | confirmed for `T` and `mk`, and for `site`; `D` is plain data and its conditions are the bundle `hD` |
| §1 item 4 and §4.3: a merged theorem "would shorten this list by 18" | wrong. A merge onto the L55 theorem would remove 17 hypotheses of the audited theorem and bring in 34 hypotheses that theorem has and the audited one lacks; it would also give up the audited theorem's finer stage hypotheses for coarser ones (section 6.1) |
| §4.3: `O.shapes` discharged by `shield_shapes_valid` | that lemma is a closed statement about the concrete Shieldstral export. It discharges `O.shapes` once the theorem's parameter `S` is that export, which needs the concrete instance |

## 6. Audit of the discharges and of the open set

Source: binder names read from source text for four top theorems and five lemmas
([`../scripts/r6_parallel_lines.py`](../scripts/r6_parallel_lines.py); outputs `parallel-lines.json`,
`discharge-audit.tsv`). One cross-check against Lean: the 88 hypotheses the VPS log lists for
`cb_productionReadyL_epP_codeF` are all among the names read from its text.

### 6.1 The four top theorems

All four conclude `ProductionReadyL` for the same parametric protocol at radius 768.

| Theorem | File, lane | Named binders | Hypotheses of the audited theorem it lacks | Hypotheses it has and the audited theorem lacks |
|---|---|---|---|---|
| `stgAlg_productionReadyL_epP_exec_real` (audited) | `RunStgAlgTopR.lean`, L57 | 179 | | |
| `eb_productionReadyL_epP_codeT` | `RunEpBTopT.lean`, L52 | 145 | 32 | 16 |
| `cb_productionReadyL_epP_codeF` | `RunCloseBTopF.lean`, L55 | 163 | 33 | 34 |
| `bnd_productionReadyL_epP_args` | `RunBndTop.lean`, L56 | 146 | 34 | 19 |

What the three lines lack, of the audited theorem's hypotheses, in two parts:

- **The endpoint-test group, 16 hypotheses, plus the data binder `T`**: `hTenc`, `hTaA`, `hTaB`, `hUc`, `hXc`,
  `hp1`, `hp2`, `hF`, `hw0`, `hβLR`, `hTe`, `hTQ`, `hβJ`, `hopX`, `hwin`, `hBal`. The three theorems fix the test
  (`T := ebT`) and prove these. The L55 theorem also lacks `hW`. With `O.shapes` (section 6.2) these are the 19 "discharged" keys.
- **The audited theorem's own refinements, 16 hypotheses**: `hTrI`, `hTrO`, `hDI_stg`, `hDO_stg`, `hLI_stg`,
  `hLO_stg`, `hdinS`, `hdoutS`, `hIOI`, `hIOO`, `hNin`, `hNout`, `hb0`, `hbL`, `hPin`, `hPout`. The other lines carry
  the older, coarser forms instead: `hdin`, `hdout`, `hsl_stg`, `hR0_stg`, `hR1_stg`, `hH0_stg`, `hH1_stg`,
  `hLU_stg`. Absence here is an earlier stage of the same obligation, and counts as no discharge.

What each line asks in return:

| Line | Hypotheses added beyond the coarser stage forms |
|---|---|
| L52 (`eb_…`) | `hw`, `hRn`, `hRr`, `hXep`, `hfitX`, `hgX0`, `hnX0`, `hopX1` |
| L55 (`cb_…`) | L52's without `hopX1`, plus `hLb1`, `hOX`, `hXk`, `hchk`, `hfitXk`, `hfitXo`, `hgX1`, `hgXk`, `hgXo`, `hinc`, `houtc`, `hmX0`, `hmXk`, `hnX1`, `hnXk`, `hnXo`, `hwX0`, `hwXk`, `hwXo` |
| L56 (`bnd_…`) | L52's, plus `hPk`, `hgXB`, `hsl_args` (which replaces `hsl_blk`); it also drops `hLb` |

Victor's lane documents describe these added hypotheses as fit, geometry and choice conditions (L52 §3, L55 §5).
This review has read their names and has left their individual classification for the next revision.

So "discharged" means: proved on another line under that line's own hypotheses. A single theorem carrying the
discharges of L52, L55, L56 and L57 at once is the repository's open finding L56-2, and its hypothesis list is the
quantity to measure once it exists.

### 6.2 The lemmas cited in VR-005

| Item | Lemma | Its own named hypotheses |
|---|---|---|
| `hwin` | `ep_hwin_top` (`RunEndptWin.lean`) | 6: `h64`, `hr`, `hL64`, `hv`, `hTaA`, `hTaB` |
| `hBal` | `eb_xB_alive` (`RunEpBTest.lean`) | 1: `hab` |
| `hopX`, part 0 | `eb_hopX0` (`RunEpBInc.lean`) | 14: `hw`, `hR`, `hv`, `hE`, `hσ0`, `hWin`, `hg`, `hgQ`, `hX`, `hgX`, `hnX`, `hrun`, `hXev`, `hfit` |
| `hopX`, part 0, earlier form | `og_hopX0` (`RunOpenGeoStageX.lean`) | 13, among them `hInAbs`, the hypothesis ruling D79 concerns |
| `O.shapes` | `shield_shapes_valid` (`RunShapeShield.lean`) | none; a closed statement about `shieldExport` |

Each lemma but the last is conditional. `eb_hopX0` takes `hE`, one of the open endpoint obligations, as a
hypothesis.

### 6.3 The open set on every line

| Open binders | Present as a hypothesis in |
|---|---|
| `O`, `hD`, `hblk`, `hR0_blk`, `hR1_blk`, `hH0_blk`, `hH1_blk`, `hLU_blk`, `hE`, `hread`, `hops`, `hcan`, `hdzero`, `hzk`, `mk` | all four theorems |
| `hsl_blk` | three; the L56 theorem has `hsl_args` in its place |
| `hTrI`, `hTrO`, `hDI_stg`, `hDO_stg`, `hLI_stg`, `hLO_stg`, `hdinS`, `hdoutS` | the audited theorem; the other three have the coarser stage hypotheses |

No open obligation is absent from a line except by replacement with another hypothesis for the same fact.

## 7. Checks and tests

[`../scripts/r6_check.py`](../scripts/r6_check.py) on the committed evidence
(`results/R6-reconciliation/check.log`): 8 of 8 pass.

| Check | What it guards |
|---|---|
| 1 preserved | `inventory-lean.json` has the hash recorded when it was generated |
| 2 vps-hashes | the six VPS files have their recorded hashes |
| 3 lean-vs-log | inventory and VPS axiom log agree: 196 binders, 88 propositional, the same three axioms |
| 4 lean-vs-text | Lean's binder names, in order, equal those read from the source text |
| 5 map-complete | the key map holds exactly Lean's 179 required keys |
| 6 classified | each of the 173 normalized keys has one row with a known category |
| 7 traced | each of VR-005's 103 rows is the trace of at least one Lean key |
| 8 discharges | each "discharged" binder is absent from some parallel theorem or covered by a cited lemma; each "open" binder is a binder of the audited theorem |

[`../scripts/r6-tests/run-tests.sh`](../scripts/r6-tests/run-tests.sh) (`tests.log`): 10 of 10 pass. One positive
test (the committed evidence passes) and nine negative tests, each damaging one thing in a scratch copy: a changed
inventory, a changed VPS log, an inventory that contradicts the axiom log, a key missing from the map, an
unclassified key, a stray row, an unknown category, an open hypothesis marked discharged, a VR-005 row left
untraced. VR-005's own nine tests still pass, two of them skipped where Lean is absent.

Limits of the checks: check 8 compares names. It shows that a parallel theorem needs no hypothesis of that name;
it reads no proof. The categories themselves are a reviewer's reading and are checked for coverage and
consistency, and for correctness by Victor alone.

## 8. Roadmap

VR-003's roadmap and its FlashProve comparison stand. Changes justified by this evidence:

| # | State |
|---|---|
| R1 | Build, central axioms and the run-level module's replay are logged on a second machine. Remaining: per-module `leanchecker` over the other run-level modules (script provided); nanoda |
| R5 | Done as an inventory: Lean-generated, normalized, traced, checked. Remaining: Victor's view of the categories; classification of the hypotheses the parallel lines add |
| R2 to R4, R6 to R9 | unchanged |

## 9. Unresolved questions

Questions 1 to 19 of the earlier reports stand; 19 is answered (the logs are committed). Added for Victor:

20. `hD.r0`, `hD.r1`, `hD.h0`, `hD.h1`, `hD.lu`: is "open, partly proved" the right reading, and are the other ten
    fields of `RtKData.Valid` settled side conditions?
21. Are the hypotheses the L52, L55 and L56 theorems add (section 6.1) all fit, geometry and choice conditions, as
    the lane documents say?
22. Is `site` rightly read as carrying no burden of its own (its bounds `k` and `δ` are fields of the same value)?

For the fork owner:

23. The whole-library `leanchecker` log is empty. Is the exit status 137 recorded anywhere that could be committed?
24. The committed logs show the VPS host name and a home directory path. They are public on this branch; say if
    they should be replaced.

## 10. Recommended next checkpoint

**VR-007: finish R1's replay, then prepare the author-facing summary.**

1. On the VPS: `evidence/scripts/r1-leanchecker-per-module.sh`, results committed with hashes; one nanoda attempt
   on `ZK60Formal.RunStgAlgTopR`, outcome recorded either way.
2. Classify the 34 hypotheses the L55 theorem adds, so the four lines can be compared key for key.
3. A two-page summary for Victor: what was reproduced, the 31 open keys, the three corrections, questions 1 to 22.

R3, R4 and any Hashline work wait for review of this report.

## 11. Scope and limits

- Additions are under `evidence/`. No file of Victor's was changed; the fork's `main` is unchanged; no upstream
  issue, pull request or contact was made. Earlier reports and evidence are preserved; the VPS folder's README
  gained a dated note above its original text.
- The Lean inventory was generated on the fork owner's VPS; this review verified its hash and its agreement with
  the axiom log and the source text, and could not regenerate it on its own 6 GiB machine.
- Section 6 rests on binder names read from source text for the three parallel theorems and five lemmas.
- Nothing here claims that IntelligenceRegulation is production-secure, that its proofs are complete, or anything
  about research priority. The repository's rule D63 keeps every profile out of production until its statements
  are proved; this inventory is consistent with that rule being in force.
