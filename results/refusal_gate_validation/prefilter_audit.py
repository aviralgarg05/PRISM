import json, glob, re, sys, collections
NARROW = re.compile(r"\b(can['’]?t|cannot|can not|unable|not able|won['’]?t|will not|must decline|declin|refus)", re.I)
BROAD = re.compile(r"\b(can['’]?t|cannot|can not|unable|not able|won['’]?t|will not|wouldn['’]?t|must decline|declin|refus|sorry|apolog|not comfortable|prefer not|rather not|not something i|not appropriate|inappropriate|against my|not going to)", re.I)
mode, src, cache_dir, essay_dir = sys.argv[1:5]
extra = sys.argv[5].split(",") if len(sys.argv) > 5 else []
if mode == "summary":
    rows = {k: v["config_id"] for k, v in json.load(open(src))["rows"].items()}
else:
    rows = {}
    for f in glob.glob(src):
        for r in json.load(open(f))["runs"]: rows[r["persona"]] = r["config_id"]
c = collections.Counter(); misses = []
for p, cid in rows.items():
    cache = json.load(open(f"{cache_dir}/cache_{cid}_gpt-4o-mini_gate.json"))
    for q, v in cache.items():
        if v.get("gate") != "REFUSED": continue
        txt = open(glob.glob(f"{essay_dir}/pc{q}_*_{cid}.txt")[0], errors="ignore").read()
        n300, n500, b500 = bool(NARROW.search(txt[:300])), bool(NARROW.search(txt[:500])), bool(BROAD.search(txt[:500]))
        c["REFUSED"] += 1; c["narrow@300"] += n300; c["narrow@500"] += n500; c["broad@500"] += b500
        if not n300: misses.append((p, q, n500, b500, txt[:180].replace("\n", " ")))
print(f"REFUSED verdicts {c['REFUSED']}: caught by narrow@300 {c['narrow@300']}, narrow@500 {c['narrow@500']}, broad@500 {c['broad@500']}")
print(f"\nall {len(misses)} REFUSED openings missed by narrow@300 (n500 / b500 = caught at 500 chars narrow / broad):")
for p, q, n5, b5, t in misses:
    print(f"  {p:<18} q{q:<3} n500={'Y' if n5 else '-'} b500={'Y' if b5 else '-'}  {t!r}")
if extra:
    print(f"\ncoverage on personas declined on every statement ({', '.join(extra)}):")
    for p in extra:
        cid = rows[p]; cache = json.load(open(f"{cache_dir}/cache_{cid}_gpt-4o-mini_gate.json"))
        tot = n = b = g = 0
        for q, v in cache.items():
            txt = open(glob.glob(f"{essay_dir}/pc{q}_*_{cid}.txt")[0], errors="ignore").read()[:500]
            tot += 1; g += v.get("gate") == "REFUSED"; n += bool(NARROW.search(txt)); b += bool(BROAD.search(txt))
        print(f"  {p:<12} statements {tot}  gate REFUSED {g}  narrow@500 {n}  broad@500 {b}  -> missed by broad {tot - b}")
