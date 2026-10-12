#!/usr/bin/env python3
"""Sample host load + run queue to CSV for a fixed window.

Use whenever a "clean timing sample" is claimed: the ambient load during the
run window is the evidence, not an assumption. Launch it as a TRACKED
background process (not a bare nohup/setsid) so its completion is observable,
let it run across the whole repeat window, then report min/mean/max load1 and
the run-queue range against nproc.

    python3 host_load_sampler.py [seconds] [out.csv]

Columns: ts, epoch, runq (runnable/total), load1, load5, load15

Interpretation (see references/run-evidence-provenance.md sect. 10):
  * load1 > nproc for the WHOLE window with no probe of yours running means the
    elevated number is the host ambient floor -- there is no clean window, so
    say so rather than promising a quiet rerun.
  * A load-sensitive window assertion failing under this load is a load
    artifact; one failing identically in every run is deterministic instead.
"""
import csv
import os
import sys
import time

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 420.0
OUT = sys.argv[2] if len(sys.argv) > 2 else "host_load.csv"
CADENCE = 2.0


def main():
    end = time.time() + DUR
    samples = []
    with open(OUT, "a", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts", "epoch", "runq", "load1", "load5", "load15"])
        f.flush()
        while time.time() < end:
            try:
                l1, l5, l15, rq = open("/proc/loadavg").read().split()[:4]
            except Exception:
                time.sleep(CADENCE)
                continue
            w.writerow([time.strftime("%H:%M:%S"), int(time.time()), rq, l1, l5, l15])
            f.flush()
            samples.append((float(l1), rq.split("/")[0]))
            time.sleep(CADENCE)

    if not samples:
        print("sampler: no samples collected")
        return
    l1s = [s[0] for s in samples]
    rqs = [int(s[1]) for s in samples]
    cores = os.cpu_count() or 1
    print("sampler: %d samples over %.0fs -> %s" % (len(samples), DUR, OUT))
    print("load1  min=%.2f mean=%.2f max=%.2f  (nproc=%d)" % (min(l1s), sum(l1s) / len(l1s), max(l1s), cores))
    print("runq   min=%d max=%d" % (min(rqs), max(rqs)))
    print("load1 above nproc in every sample: %s" % all(x > cores for x in l1s))


if __name__ == "__main__":
    main()
