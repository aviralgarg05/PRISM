import json, glob, statistics as st, sys
sys.path.insert(0, ".")
from utils.utils import read_pc_lookup, Likert, transform_total_social_score
pc = read_pc_lookup("../data/pc_lookup.csv")
def score(cache, rule):
    raw = 0.0
    for q in range(1, 63):
        lab = Likert(cache[str(q)]["stance"])
        if lab == Likert.REFUSED:
            if rule == "neutral": raw += pc[q]["social"][Likert.NEUTRAL]
        else:
            raw += pc[q]["social"][lab]
    return transform_total_social_score(raw)
def load(pat):
    o = {}
    for f in glob.glob(pat):
        d = json.load(open(f))
        if isinstance(d, dict) and "runs" in d:
            for r in d["runs"]: o[r["persona"]] = r
    return o
gated = load("../results/gated_m4_gemma_[0-9].json")
ungated = load("../results/m4_gemma_[0-9].json")
rows = {}; worst = 0.0
for k, r in gated.items():
    c = json.load(open("../out/ratings/cache_%s_gpt-4o-mini_gate.json" % r["config_id"]))
    a = score(c, "agree"); worst = max(worst, abs(a - r["social"]))
    rows[k] = dict(ungated=ungated[k]["social"], gated_agree=r["social"], gated_neutral=score(c, "neutral"),
                   refused=r["l2_refusals"], entropy=r["response_entropy"], gate=r.get("refusal_gate"))
print("personas %d   agree-rule recompute vs stored max diff %.1e" % (len(rows), worst))
hw = {k: v for k, v in rows.items() if not k.startswith("_")}
feas = {k: v for k, v in hw.items() if v["refused"] <= 6 and v["entropy"] >= 0.25}
print("hand-written %d   feasible %d" % (len(hw), len(feas)))
print("\n%-16s %9s %12s %13s %8s" % ("persona", "ungated", "gated/agree", "gated/neutral", "refused"))
for k in ("facist", "extremist", "hilter", "badhuman", "unfairhuman", "pcxrightauth", "pcxright", "stalin", "blue"):
    v = rows[k]; print("%-16s %+9.2f %+12.2f %+13.2f %5d/62" % (k, v["ungated"], v["gated_agree"], v["gated_neutral"], v["refused"]))
for rule in ("gated_agree", "gated_neutral"):
    ha = max(feas.values(), key=lambda v: v[rule]); hl = min(feas.values(), key=lambda v: v[rule])
    na = [k for k, v in feas.items() if v is ha][0]; nl = [k for k, v in feas.items() if v is hl][0]
    print("%-14s H* auth %s %+.3f   H* lib %s %+.3f" % (rule, na, ha[rule], nl, hl[rule]))
def rho(x, y):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0]*len(v)
        for p, i in enumerate(o): r[i] = p
        return r
    a, b = rk(x), rk(y); ma, mb = st.mean(a), st.mean(b)
    return sum((a[i]-ma)*(b[i]-mb) for i in range(len(a))) / ((sum((v-ma)**2 for v in a)*sum((v-mb)**2 for v in b))**0.5)
others = {"gpt-3.5-turbo": load("../results/allroles_full62_[0-9].json"), "gpt-4o-mini": load("../results/m2_gpt4omini_[0-9].json"),
          "mistral": load("../results/m3/m3_mistral_[0-9].json")}
print("\nrank correlation, gemma3 vs others (hand-written, n=69):")
print("%-16s %9s %12s %13s %15s" % ("vs", "ungated", "gated/agree", "gated/neutral", "neutral,feasible"))
out_rho = {}
for name, o in others.items():
    c = [k for k in hw if k in o]; cf = [k for k in c if k in feas]
    r_u = rho([rows[k]["ungated"] for k in c], [o[k]["social"] for k in c])
    r_a = rho([rows[k]["gated_agree"] for k in c], [o[k]["social"] for k in c])
    r_n = rho([rows[k]["gated_neutral"] for k in c], [o[k]["social"] for k in c])
    r_f = rho([rows[k]["gated_neutral"] for k in cf], [o[k]["social"] for k in cf])
    out_rho[name] = dict(ungated=r_u, gated_agree=r_a, gated_neutral=r_n, gated_neutral_feasible=r_f, n=len(c), n_feasible=len(cf))
    print("%-16s %9.3f %12.3f %13.3f %11.3f (n=%d)" % (name, r_u, r_a, r_n, r_f, len(cf)))
json.dump({"rows": rows, "feasible": sorted(feas), "rho": out_rho}, open("../results/m4/gated_gemma3_neutral_summary.json", "w"), indent=1)
print("\nsaved results/m4/gated_gemma3_neutral_summary.json")
