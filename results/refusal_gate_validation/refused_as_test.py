import sys, json, glob, shutil, subprocess
sys.path.insert(0, ".")
T = sys.argv[1]
import prism_eval
from utils.utils import Likert, read_pc_lookup, transform_total_social_score
from utils.roles import roles
pick = None
for f in sorted(glob.glob("../results/fairconf_t4o_[0-9].json")):
    for r in json.load(open(f))["runs"]:
        c = json.load(open(f"../out/ratings/cache_{r['config_id']}_gpt-4o-mini.json"))
        if r["persona"] == "pcxrightauth" and any(v["stance"] == "Refused" for v in c.values()):
            pick = (r, c); break
    if pick: break
run, cache = pick; cid = run["config_id"]
for p in glob.glob(f"../out/essays/*_{cid}.txt"): shutil.copy(p, f"{T}/essays/")
shutil.copy(f"../out/ratings/cache_{cid}_gpt-4o-mini.json", f"{T}/ratings/")
pc = read_pc_lookup("../data/pc_lookup.csv")
raw_n = sum(pc[q]["social"][Likert.NEUTRAL] if cache[str(q)]["stance"] == "Refused" else pc[q]["social"][Likert(cache[str(q)]["stance"])] for q in range(1, 63))
expect_neutral = transform_total_social_score(raw_n)
def boom(*a, **k): raise AssertionError("no model call expected")
prism_eval.classify_essay = prism_eval.gate_verdict = prism_eval.write_essay = boom
base = {"provider": "openai", "model": "gpt-4o-mini", "role": "evolved", "role_text": roles["pcxrightauth"][1].strip(),
        "temperature": 0.0, "assessor": "gpt-4o-mini", "assessor_provider": "openai", "no_refusal_retry": True,
        "config_id": cid, "basepath": "../data", "outpath": T}
def check(n, c): print(("  PASS " if c else "  FAIL ") + n); assert c, n
refused = sum(1 for v in cache.values() if v["stance"] == "Refused")
print(f"  using {run['persona']} cid {cid} with {refused} refused statement(s), stored social {run['social']:+.4f}")
r_default = prism_eval.evaluate_prism_config(dict(base))
check("default reproduces the stored score", abs(r_default["social"] - run["social"]) < 1e-9)
check("default records refused_as='agree'", r_default["refused_as"] == "agree")
r_n = prism_eval.evaluate_prism_config(dict(base, refused_as="neutral"))
check(f"neutral gives the independently computed {expect_neutral:+.4f} (got {r_n['social']:+.4f})", abs(r_n["social"] - expect_neutral) < 1e-9)
check("neutral records refused_as='neutral'", r_n["refused_as"] == "neutral")
check("neutral differs from agree when a refusal is present", abs(r_n["social"] - r_default["social"]) > 1e-6)
try:
    prism_eval.evaluate_prism_config(dict(base, refused_as="bogus")); check("invalid value rejected", False)
except ValueError:
    check("invalid value rejected", True)
out = subprocess.run([sys.executable, "score_cid.py", "--cid", cid, "--outpath", T, "--basepath", "../data", "--json", "--refused-as", "neutral"],
                     capture_output=True, text=True)
sc = json.loads(out.stdout[out.stdout.index("{"):])
check(f"score_cid --refused-as neutral agrees ({sc['social']:+.4f})", abs(sc["social"] - expect_neutral) < 1e-9)
print("ALL REFUSED_AS CHECKS PASSED")
