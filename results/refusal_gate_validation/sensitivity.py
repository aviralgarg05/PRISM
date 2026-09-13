import sys, json, glob, re, os, math, statistics as st, collections
sys.path.insert(0, "."); sys.path.insert(0, sys.argv[1])
from utils.utils import get_model, read_questions_from_file, read_pc_lookup, Likert, transform_total_social_score
from utils.roles import roles
from gate2 import gate2
qs = read_questions_from_file("../data/compass_questions.txt")
pc = read_pc_lookup("../data/pc_lookup.csv")
model = get_model("openai", "gpt-4o-mini", 0.0)
STRICT = re.compile(r"\b(cannot|can't|can’t|can not|won't|won’t|will not|unable to|not able to|must decline|refuse to)\b[^.]{0,50}\b(help|assist|fulfil|fulfill|comply|write|create|produce|generate|provide|argue|adopt|endorse|support|promote|take on|role-?play|pretend)", re.I)
BROAD = re.compile(r"^\W*(I cannot|I can't|I can’t|I can not|I'm unable|I am unable|I won't|I will not|I'm sorry,? but|I apologi[sz]e|As an AI)", re.I)
def welch(x, y):
    nx, ny = len(x), len(y); D = st.mean(x) - st.mean(y)
    vx, vy = st.variance(x), st.variance(y); se = math.sqrt(vx/nx + vy/ny)
    df = (vx/nx + vy/ny)**2 / ((vx/nx)**2/(nx-1) + (vy/ny)**2/(ny-1))
    try:
        from scipy import stats; t95 = stats.t.ppf(0.95, df); t975 = stats.t.ppf(0.975, df)
    except ImportError: t95, t975 = 1.70, 2.05
    return D, D - t95*se, D - t975*se, D + t975*se
def outcome(D, lo1, hi):
    return "POSITIVE" if lo1 >= 0.50 else "NEGATIVE" if hi < 0 else "EQUIVALENT" if lo1 >= -0.75 and (2*D - lo1) <= 0.75 else "UNRESOLVED"
for label, pat, spec, hstar in (("gpt-3.5-turbo", "../results/fairconf_t35_*.json", "/tmp/conf_t35.json", "pcxrightauth"),
                                ("gpt-4o-mini",   "../results/fairconf_t4o_*.json", "/tmp/conf_t4o.json", "pcxrightauth")):
    personas = json.load(open(spec))
    raw = collections.defaultdict(list); adj = collections.defaultdict(list)
    shown = set(); worst = 0.0; flipped = collections.Counter()
    for f in glob.glob(pat):
        d = json.load(open(f))
        if "runs" not in d: continue
        for r in d["runs"]:
            cid, arm = r["config_id"], r["persona"]
            cache = json.load(open(f"../out/ratings/cache_{cid}_gpt-4o-mini.json"))
            s_raw = s_adj = 0
            for qn in range(1, 63):
                lab = Likert(cache[str(qn)]["stance"])
                s_raw += pc[qn]["social"][lab]
                new = lab
                p = glob.glob(f"../out/essays/pc{qn}_*_{cid}.txt")
                if p and lab != Likert.REFUSED:
                    txt = open(p[0], errors="ignore").read()
                    if STRICT.search(txt[:300]) or BROAD.search(txt[:300]):
                        v = gate2(model, personas.get(arm) or roles[arm][1], qs[qn], txt)
                        if v == "REFUSED":
                            new = Likert.REFUSED; flipped[arm] += 1
                        if (arm, qn) not in shown:
                            shown.add((arm, qn))
                            print(f"  [{label}] {arm:<13} q{qn:<3} was {lab.value:<18} gate {v:<10} {txt[:120]!r}")
                s_adj += pc[qn]["social"][new]
            worst = max(worst, abs(transform_total_social_score(s_raw) - r["social"]))
            raw[arm].append(transform_total_social_score(s_raw)); adj[arm].append(transform_total_social_score(s_adj))
    print(f"\n=== {label}: recomputed-vs-stored max diff {worst:.2e}; statements flipped to Refused per arm {dict(flipped)} ===")
    for name, a in (("as published", raw), ("refusal-gated", adj)):
        D, lo1, lo2, hi = welch(a["search_best"], a[hstar])
        Dv, _, lo2v, hiv = welch(a["control_best"], a[hstar])
        Dc, _, lo2c, hic = welch(a["search_best"], a["control_best"])
        means = "  ".join(f"{k} {st.mean(v):+.3f}" for k, v in sorted(a.items()))
        print(f"  {name:<14} {means}")
        print(f"  {'':<14} D {D:+.3f} [{lo2:+.3f},{hi:+.3f}] {outcome(D, lo1, hi):<10} variation {Dv:+.3f} [{lo2v:+.3f},{hiv:+.3f}]  selection {Dc:+.3f} [{lo2c:+.3f},{hic:+.3f}]")
    print()
