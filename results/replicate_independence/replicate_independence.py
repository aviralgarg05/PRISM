"""Are n replicates actually n independent essays? Counts distinct essays per statement.

Usage: python replicate_independence.py groups.json   (run from the repo root)
groups.json is a list of [label, glob of confirmation result files].
"""
import json, glob, os, re, collections, hashlib, statistics as st, sys
groups = json.load(open(sys.argv[1]))
rx = re.compile(r"^pc(\d+)_.*_([0-9a-f]{10})\.txt$")
idx = {}
for name in os.listdir("out/essays"):
    m = rx.match(name)
    if m: idx[(int(m.group(1)), m.group(2))] = name
print("indexed %d essays" % len(idx), flush=True)
digest = {}
def h(q, cid):
    name = idx.get((q, cid))
    if name is None: return None
    if name not in digest:
        digest[name] = hashlib.md5(open(os.path.join("out/essays", name), "rb").read()).hexdigest()
    return digest[name]
print("%-40s %-18s %3s %6s %7s %5s %11s %9s" % ("confirmation", "arm", "n", "scores", "sd", "cids", "essays/stmt", "all-same"), flush=True)
for label, pat in groups:
    runs = []
    for f in sorted(glob.glob(pat)):
        try: d = json.load(open(f))
        except Exception: continue
        if isinstance(d, dict) and "runs" in d: runs += d["runs"]
    if not runs:
        print("%-40s (no runs for %s)" % (label, pat), flush=True); continue
    by = collections.defaultdict(list)
    for r in runs: by[r["persona"]].append(r)
    for p, rs in sorted(by.items()):
        sc = [r["social"] for r in rs]; distinct = same = seen = 0
        for q in range(1, 63):
            hs = set(x for x in (h(q, r["config_id"]) for r in rs) if x)
            if hs: seen += 1; distinct += len(hs); same += len(hs) == 1
        print("%-40s %-18s %3d %6d %7.3f %5d %11s %9s" % (label[:40], p[:18], len(rs), len(set(round(s, 6) for s in sc)),
              st.stdev(sc) if len(sc) > 1 else 0.0, len(set(r["config_id"] for r in rs)),
              ("%.1f" % (distinct / seen)) if seen else "none", ("%d/%d" % (same, seen)) if seen else "-"), flush=True)
