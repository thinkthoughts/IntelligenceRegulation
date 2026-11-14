# Review status and response guide

**Independent external review.** Everything under `evidence/` was written by an outside reviewer (the owner of the
fork `thinkthoughts/IntelligenceRegulation`, working with Claude). Victor Rielly is the author of
IntelligenceRegulation. He has had no part in this review, and he has neither reviewed, endorsed nor accepted any
finding in it. Until he responds, every finding here is the reviewer's reading alone.

## Status

| Item | State on 2026-11-14 |
|---|---|
| Reviewed commit | `eee3eb5717dea88d0fc48dc00f6aef389d52af3a` (Victor's `main` on 2026-11-13) |
| Reports published | VR-003 (review and roadmap), VR-004 (R1 and R2 reproduction, roadmap checkpoint) |
| Roadmap steps done | R1 (Lean), R2 (Rust); see VR-004 for exactly how far each went |
| Roadmap steps waiting | R3 to R9, held until the fork owner has read VR-004 |
| Contact with Victor | none made; no issue or pull request has been opened upstream |
| Changes to Victor's code | none; the branch adds `evidence/` and one notice at the top of `README.md` |

## For Victor: how to check a finding yourself

Each claim in the reports carries one of four labels. They say where to look.

| Label | Meaning | How to check it |
|---|---|---|
| RE-RUN | the reviewer executed it | the command and its log are under `evidence/results/`; run the same command at the same commit |
| READ | read from your source at the pinned commit | open the file named beside the claim at `eee3eb57` |
| REPORTED | taken from your own documents, as a lead | it is your record; the review adds nothing to it |
| INFERRED | the reviewer's reasoning | judge the argument; these are the claims most likely to be wrong |

To repeat the two reproduction steps on your own machine:

- **Lean (R1):** `evidence/scripts/r1-lean.sh` lists the commands. In short: `lake exe cache get` and `lake build`
  in `formal/`, then `lake env lean ../evidence/scripts/r1_axioms_premises.lean`.
- **Rust (R2):** `evidence/scripts/r2-rust.sh` lists the commands. In short: `cargo test --locked --release --lib`
  in `ops/zkp-mvp/gpu-metal/zkp-core` and `ops/zkp-mvp/gpu-metal/hashline`, and
  `python3 scripts/zk60_p1_demo.py --output <new directory>`.

Both were run on a small x86-64 Linux machine (`evidence/PINS.md`). Your M3 Ultra will be far faster.

## If something here is wrong

The reviewer expects to have made mistakes: the tree has 113,051 files and the review read a small part of it.

- **A factual error** (a wrong number, a misread file, an outdated status): say which report and section, and what
  the source says. The reviewer will add a dated correction to the index and to a new report. Published reports
  are kept as written, with corrections recorded beside them.
- **A finding you disagree with:** say so and why. The disagreement will be recorded next to the finding in your
  words.
- **Something that should come down** (for example text you consider private or misleading): say so and it will
  be removed from the branch.

How to reach the reviewer: contact the fork's owner through GitHub (`thinkthoughts`). Issues are switched off on
the fork (checked 2026-11-14), so there is no issue tracker to write in yet; the fork owner decides whether to
open one. The reviewer will open nothing on your repository unless you ask.

## Questions and proposals

- The open questions are in `evidence/README.md` under "Open questions for Victor". An answer to any one of them
  is useful by itself.
- The proposed next steps (R3 to R9) are offers, to be taken up, changed or declined. None will be started as a
  contribution to your repository without your agreement. R8 in particular (closing run-level soundness premises)
  overlaps your active Lean lanes, so it needs your word on which premises are free.
- If a reproducible check script or a CI workflow would be useful to you, say which form you would accept (a pull
  request, a patch, or files you copy from this branch).

## What this review does and does not claim

- It claims that named commands gave named results at one commit on one machine, and that named files say what
  the reports quote.
- It makes no claim that IntelligenceRegulation is secure, production-ready or complete. Your own rule D63 and
  your gap audits of 2026-11-10 say the production statements are still to be proved for the running system, and
  the review agrees with them.
- It makes no claim about research priority between IntelligenceRegulation and FlashProve. VR-003 section 3.2
  records dates and what each repository cites, and states its limits.
