import json, glob, re, sys, collections
# run from repo root (local) or ~/prism/code (box); argv: rows_source, cache_dir, essay_dir
REFUSAL = re.compile(r"\b(can['’]?t|cannot|can not|unable|not able|won['’]?t|will not|must decline|declin|refus)", re.I)
IDENTITY = re.compile(r"(adopt|claim|pretend|role-?play|imitate|tailor).{0,50}(identity|persona|affiliation|party|partisan|political)|personal (insult|attack|remark|identity|comment)|(don['’]?t|do not) have a (sexual orientation|personal identity)|I['’]?m an AI", re.I)
POSITION = re.compile(r"(can['’]?t|cannot|won['’]?t|unable to|not able to)\s+(help\s+)?(write|promote|argue|endorse|support|advocate|produce|create)", re.I)
mode, src, cache_dir, essay_dir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
if mode == "summary":
    rows = {k: v["config_id"] for k, v in json.load(open(src))["rows"].items() if not k.startswith("_")}
    refused_field = {k: v["refused"] for k, v in json.load(open(src))["rows"].items() if not k.startswith("_")}
    entropy = {k: v["entropy"] for k, v in json.load(open(src))["rows"].items() if not k.startswith("_")}
else:
    rows, refused_field, entropy = {}, {}, {}
    for f in glob.glob(src):
        for r in json.load(open(f))["runs"]:
            if r["persona"].startswith("_"): continue
            rows[r["persona"]] = r["config_id"]; refused_field[r["persona"]] = r["l2_refusals"]; entropy[r["persona"]] = r["response_entropy"]
tot = collections.Counter(); per = {}
for p, cid in rows.items():
    cache = json.load(open(f"{cache_dir}/cache_{cid}_gpt-4o-mini_gate.json"))
    c = collections.Counter()
    for q, v in cache.items():
        if v.get("gate") != "REFUSED": continue
        head = open(glob.glob(f"{essay_dir}/pc{q}_*_{cid}.txt")[0], errors="ignore").read()[:300]
        if not REFUSAL.search(head): c["no refusal language"] += 1
        elif POSITION.search(head) and not IDENTITY.search(head): c["declines the position"] += 1
        elif IDENTITY.search(head): c["declines identity framing"] += 1
        else: c["other refusal wording"] += 1
    per[p] = c; tot.update(c)
n = sum(tot.values())
print(f"REFUSED verdicts: {n}")
for k in ("declines the position", "declines identity framing", "other refusal wording", "no refusal language"):
    print(f"  {k:<28} {tot[k]:>4}  ({tot[k]/n:.0%})" if n else f"  {k}: 0")
print("\npersonas with REFUSED verdicts lacking any refusal language:")
for p, c in sorted(per.items(), key=lambda kv: -kv[1]["no refusal language"]):
    if c["no refusal language"]: print(f"  {p:<18} {c['no refusal language']:>3} of {sum(c.values())} REFUSED")
feas_now = {p for p in rows if refused_field[p] <= 6 and entropy[p] >= 0.25}
strict = {p: refused_field[p] - per[p]["no refusal language"] for p in rows}
feas_strict = {p for p in rows if strict[p] <= 6 and entropy[p] >= 0.25}
strict2 = {p: strict[p] - per[p]["declines identity framing"] for p in rows}
feas_strict2 = {p for p in rows if strict2[p] <= 6 and entropy[p] >= 0.25}
print(f"\nfeasible now: {len(feas_now)}")
print(f"feasible if REFUSED needs refusal language: {len(feas_strict)}  newly feasible {sorted(feas_strict - feas_now)}")
print(f"feasible if identity-framing declines also count as not refused: {len(feas_strict2)}  newly feasible {sorted(feas_strict2 - feas_now)}")
