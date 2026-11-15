# RPI-RLT-VR-007 — Independent replay and author-facing review

> **Independent external review.** Written for the fork `thinkthoughts/IntelligenceRegulation` by an outside
> reviewer working with Claude (Anthropic). Victor Rielly, the author of IntelligenceRegulation, has had no part
> in it and has neither reviewed nor endorsed it. Index: [../README.md](../README.md).

2026-11-14 · thinkthoughts · reviewed commit `eee3eb5717dea88d0fc48dc00f6aef389d52af3a` · built on review
commit `5a7c536b107123303fa2fb854bace9bedb4c7525`

## 1. Summary

1. **An independent kernel accepts three of Victor's theorems.** nanoda, a Lean kernel written separately in Rust,
   checks the block-level knowledge-soundness theorem `block_knowledge_r13_shield` with its 38,128 dependencies,
   the F12 fix `mproduct_sound_shift` with 17,840, and `trivialArith_circuitIff`. A pinned exporter and checker
   pair compatible with Lean 4.34.1 exists, so the earlier blocker is gone (section 2.3).
2. **The run-level replays are ready for the VPS and await it.** A per-module replay script with memory and time
   guards was inspected, trial-run and tested here. The commands for the per-module replay, nanoda on the four top
   theorems and the out-of-memory diagnostic are in `results/R7-vps/README.md` (section 2).
3. **The four top theorems prove the same conclusion under different hypothesis sets.** Each parallel theorem
   discharges the same 15 endpoint hypotheses, exchanges one or two others for conditions on the verifier's
   parameters, and carries the older, coarser form of eight stage obligations. Counted as open obligations: 24 on
   the audited theorem and on the L55 theorem, 25 on the L52 and L56 theorems (section 3). Fewer hypotheses on a line
   are a different statement, and none of the four is stronger than another by count alone.
4. **The L55 theorem's additions are classified.** It adds 33 hypotheses (VR-006 said 34, counting the data binder
   `hw`): 20 bookkeeping, 5 public instance data, and 8 open, the 8 being the coarse stage obligations (section 3.2).
5. **The author-facing summary is written** ([`../SUMMARY-FOR-VICTOR.md`](../SUMMARY-FOR-VICTOR.md)). It leads
   with Victor's objectives and results, and keeps the chronology and attribution reading in its own section.

No claim here concerns production security. The repository's rule D63 keeps every profile out of production until
its statements are proved, and the findings are consistent with that rule being in force.

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

Awaited. Instructions: [`../results/R7-vps/README.md`](../results/R7-vps/README.md), steps 0 to 2. Together with
VR-004 (358 modules accepted here) and VR-006 (`ZK60Formal.RunStgAlgTopR` accepted on the VPS), the run covers the
remaining 108 modules of the default target. The 29 check modules outside the default target are recorded
`not-compiled` unless they are built first.

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

What this establishes: for these three theorems, a kernel implemented separately from Lean's accepts every
declaration they depend on, including Mathlib's, under the three standard axioms. The run-level theorems are
awaited (`results/R7-vps/README.md`, step 3).

The VR-006 axiom log covers the audited theorem, its `_view` variant, the L55 theorem and the R13 run theorem.
The L52 and L56 top theorems are added to the VPS steps (step 3), so that all four top theorems have a logged
axiom list.

### 2.4 The whole-library memory failure

The VR-006 log of the whole-library replay is empty. Step 4 of the VPS instructions copies the kernel's own record
of a memory kill, sanitized, or writes that none was found. Until that file exists, the failure stays the fork
owner's report.

### 2.5 Earlier evidence intact

`r6_check.py` passes all eight checks, including the SHA-256 of all six VPS files and of the Lean inventory. No
file under `results/R1-lean`, `R1-lean-vps`, `R2-rust`, `R5-premises` or `R6-reconciliation` was changed, and no
earlier report was edited. VR-006 question 24 (host name and home path in the committed VPS logs) is still open;
the files were left as committed so that their hashes stay valid.

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

[`../scripts/r7-tests/run-tests.sh`](../scripts/r7-tests/run-tests.sh): 12 of 12 pass (`tests.log`): one positive
test and ten adversarial edits to scratch copies, each caught (an unclassified addition, a phantom name, a
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
| VR-006 §2: "a separate kernel implementation has yet to be run on any part of the library" | nanoda has now checked three theorems and their dependencies |
| VR-005 §1, VR-006 §2: nanoda named as open | a compatible pair is pinned; run-level runs await the VPS |

## 5. Roadmap

VR-003's roadmap and its FlashProve comparison stand.

| # | State after VR-007 |
|---|---|
| R1 | Second kernel established for component and block theorems. Remaining: per-module `leanchecker` and nanoda on the run-level theorems (VPS) |
| R5 | Extended to all four top theorems; each difference classified and checked |
| R3, R4 | Held, as agreed, for the next research phase |
| R2, R6 to R9 | Unchanged |

## 6. Questions

Questions 1 to 24 of the earlier reports stand; the summary for Victor groups them. Added:

25. (For Victor) Is a theorem combining L55's closing discharges with L57's stage refinement the planned next top
    theorem?
26. (For the fork owner) Should the VR-006 VPS logs be re-committed with the host name and home path replaced? That
    would change their hashes, so it would need a new, separately hashed copy beside the originals.

## 7. Recommended next checkpoint

1. VPS: steps 0 to 5 of `results/R7-vps/README.md`.
2. A short follow-up (VR-007b) that reads those logs and fills sections 2.2 to 2.4.
3. Review of the author-facing summary by the fork owner, then a decision on contacting Victor.

R3, R4 and any Hashline work wait for approval.

## 8. Scope and limits

- Additions are under `evidence/` only. No file of Victor's was changed; the fork's `main` is unchanged; no
  upstream issue, pull request or contact was made.
- nanoda ran on the reviewer's machine on modules compiled there. The run-level modules could not be compiled here.
- Section 3 rests on binder names and statement text read from source, with Lean's list as a cross-check for the
  L55 theorem. Status words in the classification are Victor's, from his lane documents.
- External tool facts (nanoda's accepted format, the Arena's results) were read from those projects' public pages
  and source at the commits named.
