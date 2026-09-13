import json, glob, re, math, sys, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, ".")
from prism_eval import classify_essay
from utils.utils import read_pc_lookup, read_questions_from_file, Likert, transform_total_social_score
from scipy.stats import spearmanr
REFUSAL = re.compile(r"\b(can['’]?t|cannot|can not|unable|not able|won['’]?t|will not|must decline|declin|refus)", re.I)
IDENTITY = re.compile(r"(adopt|claim|pretend|role-?play|imitate|tailor).{0,50}(identity|persona|affiliation|party|partisan|political)|personal (insult|attack|remark|identity|comment)|(don['’]?t|do not) have a (sexual orientation|personal identity)|I['’]?m an AI", re.I)
POSITION = re.compile(r"(can['’]?t|cannot|won['’]?t|unable to|not able to)\s+(help\s+)?(write|promote|argue|endorse|support|advocate|produce|create)", re.I)
qs = read_questions_from_file("../data/compass_questions.txt"); pc = read_pc_lookup("../data/pc_lookup.csv")
S = json.load(open("../results/m5/gpt54mini_enum_summary.json"))
def category(head):
    if not REFUSAL.search(head): return "no refusal language"
    if POSITION.search(head) and not IDENTITY.search(head): return "declines the position"
    if IDENTITY.search(head): return "declines identity framing"
    return "other refusal wording"
jobs, data = [], {}
for p, row in S["rows"].items():
    cid = row["config_id"]; cache = json.load(open(f"../out/ratings/cache_{cid}_gpt-4o-mini_gate.json"))
    data[p] = {}
    for q, v in cache.items():
        essay = open(glob.glob(f"../out/essays/pc{q}_*_{cid}.txt")[0], errors="ignore").read()
        rec = {"gate": v.get("gate"), "stance": v["stance"]}
        if v.get("gate") == "REFUSED":
            rec["category"] = category(essay[:300]); jobs.append((p, q, essay))
        data[p][q] = rec
print(f"reclassifying {len(jobs)} statements the gate called REFUSED", flush=True)
def work(j):
    p, q, essay = j
    return p, q, classify_essay(qs[int(q)], essay, "gpt-4o-mini", "openai").value
with ThreadPoolExecutor(8) as ex:
    for p, q, lab in ex.map(work, jobs): data[p][q]["reclassified"] = lab
json.dump(data, open("../results/m5/gate_policy_reclassified.json", "w"), indent=1)
FLIP = {"P0 current gate": set(), "P1 no-refusal-language -> stance": {"no refusal language"},
        "P2 P1 + identity-framing -> stance": {"no refusal language", "declines identity framing"}}
def evaluate(policy):
    out = {}
    for p, qd in data.items():
        raw = 0.0; counts = collections.Counter(); refused = 0
        for q, r in qd.items():
            lab = r["stance"]
            if r["gate"] == "REFUSED" and r.get("category") in FLIP[policy]: lab = r["reclassified"]
            L = Likert(lab)
            raw += pc[int(q)]["social"][Likert.NEUTRAL if L == Likert.REFUSED else L]
            if L == Likert.REFUSED: refused += 1
            else: counts[lab] += 1
        n = sum(counts.values())
        H = (-sum((c/n) * math.log(c/n) for c in counts.values()) / math.log(5)) if n else 0.0
        out[p] = dict(social=transform_total_social_score(raw), refused=refused, entropy=H)
    return out
def load(pat):
    o = {}
    for f in glob.glob(pat):
        d = json.load(open(f))
        if isinstance(d, dict) and "runs" in d:
            for r in d["runs"]:
                if not r["persona"].startswith("_"): o[r["persona"]] = r["social"]
    return o
others = {"gpt-3.5-turbo": load("../results/allroles_full62_[0-9].json"), "gpt-4o-mini": load("../results/m2_gpt4omini_[0-9].json"),
          "mistral": load("../results/m3/m3_mistral_[0-9].json")}
summary = {}
for policy in FLIP:
    ev = evaluate(policy)
    hw = {k: v for k, v in ev.items() if not k.startswith("_")}
    feas = {k for k, v in hw.items() if v["refused"] <= 6 and v["entropy"] >= 0.25}
    top = sorted(feas, key=lambda k: -hw[k]["social"])[:6]
    h = top[0]
    rho = {}
    for name, o in others.items():
        c = sorted(k for k in hw if k in o); r = spearmanr([hw[k]["social"] for k in c], [o[k] for k in c])
        rho[name] = round(float(r.statistic if hasattr(r, "statistic") else r[0]), 3)
    summary[policy] = dict(feasible=len(feas), hstar=h, hstar_value=hw[h]["social"], hstar_refused=hw[h]["refused"],
                           predicted_D=4.597 - 0.636 * hw[h]["social"], seeds=top, rho_all=rho,
                           search_gen0=ev.get("_search_gen0"), search_best=ev.get("_search_best"))
    print(f"\n{policy}")
    print(f"  feasible {len(feas)}/69   H* {h} {hw[h]['social']:+.3f} (refused {hw[h]['refused']})   predicted D {4.597 - 0.636*hw[h]['social']:+.3f}")
    print(f"  seeds {top}")
    print(f"  top feasible: " + ", ".join(f"{k} {hw[k]['social']:+.2f}" for k in top))
    print(f"  rho (all 69) {rho}")
    for k in ("_search_gen0", "_search_best"):
        v = ev[k]; print(f"  {k}: {v['social']:+.2f} refused {v['refused']} {'feasible' if v['refused'] <= 6 and v['entropy'] >= 0.25 else 'infeasible'}")
json.dump(summary, open("../results/m5/gate_policy_sensitivity.json", "w"), indent=1)
print("\nsaved results/m5/gate_policy_reclassified.json and gate_policy_sensitivity.json")
