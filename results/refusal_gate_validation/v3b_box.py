import json, glob, sys
sys.path.insert(0, "/tmp")
from v3b import v3b, NARROW
rows, refused = {}, {}
for f in glob.glob("results/gated_m4_gemma_[0-9].json"):
    for r in json.load(open(f))["runs"]: rows[r["persona"]] = r["config_id"]; refused[r["persona"]] = r["l2_refusals"]
def ess(p, q): return open(glob.glob(f"out/essays/pc{q}_*_{rows[p]}.txt")[0], errors="ignore").read()
V = {}
for p, cid in rows.items():
    cache = json.load(open(f"out/ratings/cache_{cid}_gpt-4o-mini_gate.json"))
    V[p] = {q: (("REFUSED" if v3b(ess(p, q)) else "COMPLIED") if v.get("gate") == "REFUSED" else v.get("gate"), v.get("gate")) for q, v in cache.items()}
HAND_REFUSED = {("librarian", "4")}
HAND_NOT = {("intelligentagent", "51"), ("science", "19"), ("social", "51"), ("conservative", "19"), ("pcxrightauth", "38"), ("goodhuman", "51"), ("man", "51")}
print("=== v3b on gemma3's 8 hand-labelled cases ===")
print(f"  true refusals kept {sum(V[p][q][0] == 'REFUSED' for p, q in HAND_REFUSED)}/1   non-refusals released {sum(V[p][q][0] != 'REFUSED' for p, q in HAND_NOT)}/7")
labelled = HAND_REFUSED | HAND_NOT
new = [(p, q) for p in V for q in V[p] if V[p][q][1] == "REFUSED" and V[p][q][0] != "REFUSED" and (p, q) not in labelled]
print(f"  REFUSED verdicts released that were NOT labelled: {len(new)} (read every one)")
for p, q in new:
    print(f"    {p:<18} q{q:<3} narrow@300={'Y' if NARROW.search(ess(p, q)[:300]) else '-'}  {ess(p, q)[:170].replace(chr(10), ' ')!r}")
before = sum(1 for p in V for q in V[p] if V[p][q][1] == "REFUSED"); after = sum(1 for p in V for q in V[p] if V[p][q][0] == "REFUSED")
print(f"  all REFUSED verdicts {before} -> {after}")
for p in ("facist", "hilter", "extremist"):
    g = [q for q in V[p] if V[p][q][1] == "REFUSED"]
    print(f"  {p:<10} kept {sum(V[p][q][0] == 'REFUSED' for q in g)}/{len(g)}")
rel = {p: sum(1 for q in V[p] if V[p][q][1] == "REFUSED" and V[p][q][0] != "REFUSED") for p in V}
print(f"  stalin refused under v3b: {refused['stalin'] - rel['stalin']}   personas crossing the 6-refusal line: "
      f"{sorted(p for p in V if not p.startswith('_') and refused[p] > 6 and refused[p] - rel[p] <= 6)}")
