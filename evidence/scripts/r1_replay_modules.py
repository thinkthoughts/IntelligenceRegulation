#!/usr/bin/env python3
"""Independent external review (RPI-RLT-VR-007, closing step R1). Replays compiled modules of the Lean library
through `leanchecker`, one module per process, and records exit status, wall time and peak memory for each.

Run from the repository root, after `lake build` in formal/ has completed:

  python3 evidence/scripts/r1_replay_modules.py [--out DIR] [--modules FILE] [--max-rss-mb N] [--timeout S]
                                                [--include-root] [--limit K]

Behaviour, stated so it can be checked before a run:
  * One `lake env leanchecker <module>` at a time. Nothing runs in parallel.
  * Memory guard: every second the script sums the resident memory of the checker's process group (from /proc).
    When the sum passes --max-rss-mb (default 9000) the group is killed and the module is recorded as
    `memory-limit`. The guard is the script's own; it needs no root and no cgroup.
  * Time guard: --timeout seconds per module (default 1800); a module that passes it is killed and recorded as
    `timeout`.
  * The root module `ZK60Formal` is skipped unless --include-root is given. It imports the whole library, and a
    whole-library replay is the run that was killed for memory on the review's second machine.
  * Resumable: a module already in the result file is skipped. Delete the file to start again.
  * It writes only under --out (default evidence/results/R1-lean-vps): 06-replay-per-module.tsv,
    06-replay-summary.txt, and 06-replay-failures.log when something fails. It changes no file of the library.
  * Paths under the home directory and the host name are replaced by `~` and `<host>` in everything it writes.
"""
import argparse, os, signal, socket, subprocess, sys, time

def group_rss_kb(pgid):
    total = 0
    for d in os.listdir("/proc"):
        if not d.isdigit(): continue
        try:
            if os.getpgid(int(d)) != pgid: continue
            with open(f"/proc/{d}/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        total += int(line.split()[1]); break
        except (ProcessLookupError, FileNotFoundError, PermissionError):
            continue
    return total

def sanitize(text):
    home = os.path.expanduser("~"); host = socket.gethostname()
    if home and home != "/": text = text.replace(home, "~")
    if host: text = text.replace(host, "<host>")
    return text

def run_one(cmd, cwd, max_rss_kb, timeout):
    t0 = time.time(); peak = 0; status = None
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
    pgid = p.pid
    while p.poll() is None:
        rss = group_rss_kb(pgid); peak = max(peak, rss)
        if rss > max_rss_kb: status = "memory-limit"
        elif time.time() - t0 > timeout: status = "timeout"
        if status:
            try: os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError: pass
            break
        time.sleep(1)
    out = p.communicate()[0].decode("utf-8", "replace")
    rc = p.returncode
    if status is None: status = "ok" if rc == 0 else "failed"
    return status, rc, time.time() - t0, peak, out

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="evidence/results/R1-lean-vps")
    ap.add_argument("--modules", help="file with one module name per line; default: every .lean file under formal/ZK60Formal")
    ap.add_argument("--max-rss-mb", type=int, default=9000)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--include-root", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="stop after this many modules (for a trial run)")
    ap.add_argument("--checker", default="lake env leanchecker", help="command placed before the module name")
    a = ap.parse_args()
    formal = os.path.abspath("formal")
    if not os.path.isdir(os.path.join(formal, "ZK60Formal")):
        sys.exit("run from the repository root: formal/ZK60Formal not found")
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    if a.modules:
        mods = [l.strip() for l in open(a.modules) if l.strip() and not l.startswith("#")]
    else:
        mods = sorted(os.path.join(r, f)[len(formal) + 1:-5].replace(os.sep, ".")
                      for r, _, fs in os.walk(os.path.join(formal, "ZK60Formal")) for f in fs if f.endswith(".lean"))
        if a.include_root: mods.append("ZK60Formal")
    if not a.include_root: mods = [m for m in mods if m != "ZK60Formal"]
    res = os.path.join(out, "06-replay-per-module.tsv")
    done = set()
    if os.path.exists(res):
        done = {l.split("\t")[0] for l in open(res).read().splitlines()[1:]}
    else:
        open(res, "w").write("module\tstatus\texit\tseconds\tpeak_rss_mb\n")
    n = 0
    for m in mods:
        if m in done: continue
        if a.limit and n >= a.limit: break
        olean = os.path.join(formal, ".lake/build/lib/lean", m.replace(".", os.sep) + ".olean")
        if not os.path.exists(olean):
            row = (m, "not-compiled", "", "0", "0")
        else:
            status, rc, secs, peak, text = run_one(a.checker.split() + [m], formal, a.max_rss_mb * 1024, a.timeout)
            row = (m, status, str(rc), f"{secs:.0f}", f"{peak / 1024:.0f}")
            if status != "ok":
                with open(os.path.join(out, "06-replay-failures.log"), "a") as f:
                    f.write(f"=== {m}: {status}, exit {rc}, {secs:.0f} s, peak {peak / 1024:.0f} MB\n" + sanitize(text[-3000:]) + "\n")
        with open(res, "a") as f: f.write("\t".join(row) + "\n")
        print("\t".join(row), flush=True); n += 1
    rows = [l.split("\t") for l in open(res).read().splitlines()[1:]]
    count = {}
    for r in rows: count[r[1]] = count.get(r[1], 0) + 1
    top = sorted((r for r in rows if r[4].isdigit()), key=lambda r: -int(r[4]))[:5]
    slow = sorted((r for r in rows if r[3].isdigit()), key=lambda r: -int(r[3]))[:5]
    lines = [f"modules recorded: {len(rows)} of {len(mods)} listed",
             "by status: " + ", ".join(f"{k}={v}" for k, v in sorted(count.items())),
             f"guards: max resident memory {a.max_rss_mb} MB, timeout {a.timeout} s per module; root module included: {a.include_root}",
             "largest peak memory (MB): " + ", ".join(f"{r[0]}={r[4]}" for r in top),
             "longest (s): " + ", ".join(f"{r[0]}={r[3]}" for r in slow),
             "checker: " + a.checker, "finished: " + time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())]
    open(os.path.join(out, "06-replay-summary.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if set(count) <= {"ok"} and len(rows) == len(mods) else 1

if __name__ == "__main__":
    sys.exit(main())
