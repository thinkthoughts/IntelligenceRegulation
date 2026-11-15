# Trial of the replay script on the reviewer's machine (VR-007 §2.1)

> **Independent external review.** Victor Rielly has had no part in it.

Machine: 2 cores, 8 GB, about 6 GiB per job; Lean 4.34.1; commit `eee3eb57`. Four runs of
`evidence/scripts/r1_replay_modules.py`, each with a module list (`*-modules-requested.txt`):

| Prefix | Purpose | Options | Outcome |
|---|---|---|---|
| `a-` | normal run: two compiled modules, one this machine could not compile, one name that does not exist | defaults | `ZK60Formal.Statements` ok (399 s, 3,455 MB); `ZK60Formal.SoundMProduct` ok (7 s, 3,280 MB); the other two recorded `not-compiled`; a second invocation recorded nothing new (resume) |
| `b-` | memory guard | `--max-rss-mb 200` | killed at 914 MB, recorded `memory-limit` |
| `c-` | time guard | `--timeout 1` | killed after 1 s, recorded `timeout` |
| `d-` | failure path | `--checker false` | recorded `failed`, exit 1, entry written to the failures log |

The guard kills the whole process group; after the runs no checker process was left except one already-reaped
(`<defunct>`) entry. The peak figures include `lake` and the loading of the imported compiled files.
