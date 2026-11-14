# Source and environment pins

**Independent external review.** See [README.md](README.md).

## Sources

| Source | Location | Pin | Checked |
|---|---|---|---|
| IntelligenceRegulation, upstream | <https://github.com/VictorRielly/IntelligenceRegulation>, `main` | `eee3eb5717dea88d0fc48dc00f6aef389d52af3a` (Victor Rielly, 2026-11-10) | `git ls-remote`, 2026-11-13 |
| IntelligenceRegulation, this fork | <https://github.com/thinkthoughts/IntelligenceRegulation>, `main` | the same commit; `main` is untouched by the review | `git ls-remote`, 2026-11-13 and 2026-11-14 |
| Review branch | `formalize-now/intelligenceregulation-review` on the fork | branched from `eee3eb57`; adds `evidence/` and one notice in `README.md` | this branch |
| FlashProve | <https://github.com/anthropics/FlashProve>, `main` | `9e2bdd8ff5bf9c62f18263d7dac189b0400b260c`, version 0.16.0 | shallow clone, 2026-11-13 |
| RLT | <https://github.com/thinkthoughts/rlt>, `main` | `7d57ae8ab04e966edf1452afedf30cdd15a961a6` | shallow clone, 2026-11-13 |

## Toolchains declared by the repository

| What | Declared in | Value |
|---|---|---|
| Lean | `formal/lean-toolchain` | `leanprover/lean4:v4.34.1` |
| Mathlib | `formal/lakefile.toml`, `formal/lake-manifest.json` | `v4.34.1`, commit `d13f23b723b8a846827a245b89c10fc7d3f11612` |
| Lean options | `formal/lakefile.toml` | `autoImplicit = false`, `relaxedAutoImplicit = false` |
| Rust crates | `ops/zkp-mvp/gpu-metal/hashline/Cargo.lock`, `ops/zkp-mvp/gpu-metal/zkp-core/Cargo.lock` | built with `--locked` |

## The machine the reproduction ran on

One cloud sandbox, used for both R1 and R2. It is much smaller than the machines the repository's own records come
from (an Apple M3 Ultra with 256 GB, and an earlier WSL laptop).

| Item | Value |
|---|---|
| CPU | Intel Xeon @ 2.10 GHz, 2 cores, x86-64 |
| Memory | 8,024 MB, no swap; jobs are limited to about 6 GiB by the sandbox's control group (see `results/R1-lean/02-lake-build-pass2.log`) |
| OS | Ubuntu 24.04.5 LTS, Linux 6.18; commands ran as root, which matters for three Rust tests (VR-004 §3.2) |
| GPU | none |
| Lean | 4.34.1 (commit `5045d0056413266e57c625dcd7c365b10e377c52`), Lake 5.0.0, installed with elan |
| Kernel replay tool | `leanchecker`, the one shipped in the Lean 4.34.1 toolchain |
| Rust | rustc 1.97.0 (2d8144b78 2026-07-07), cargo 1.97.0 |
| Network | package registries and GitHub; the Mathlib build cache was reachable |

The exact environment line for each run is saved beside its log (`results/R1-lean/environment.txt`,
`results/R2-rust/environment.txt`).

## The VR-003 report

| Item | Value |
|---|---|
| Origin | the review document at its final revision (21), exported to Markdown on 2026-11-14 |
| SHA-256 of the export before the publication note was added | `8ab03fe2152d99fdcb210c4d67e788831b3297e3a7b5960056a2bd854fbcc33f` |
| Changes made at publication | the notice at the top, and the author line written as the fork owner's GitHub handle |
