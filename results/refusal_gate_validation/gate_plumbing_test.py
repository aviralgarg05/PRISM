import sys, json, glob, shutil, os, hashlib
sys.path.insert(0, ".")
T = sys.argv[1]
import prism_eval
from utils.refusal_gate import GATE_VERSION
from utils.utils import Likert, read_questions_from_file
from utils.roles import roles
run = next(r for r in json.load(open("../results/fairconf_t35_0.json"))["runs"] if r["persona"] == "pcxrightauth")
cid = run["config_id"]
for p in glob.glob(f"../out/essays/*_{cid}.txt"): shutil.copy(p, f"{T}/essays/")
shutil.copy(f"../out/ratings/cache_{cid}_gpt-4o-mini.json", f"{T}/ratings/")
ungated = f"{T}/ratings/cache_{cid}_gpt-4o-mini.json"
before = hashlib.md5(open(ungated, "rb").read()).hexdigest()
qs = read_questions_from_file("../data/compass_questions.txt"); q_of = {v: k for k, v in qs.items()}
calls = {"gate": 0, "classify": 0, "write": 0}
def fake_gate(persona, question, essay, *a, **k):
    calls["gate"] += 1
    assert persona and "Authoritarian" in persona, "persona text not passed to the gate"
    q = q_of[question]
    return "REFUSED" if q in (4, 27) else "DISCLAIMED" if q == 58 else "COMPLIED"
def fake_classify(*a, **k):
    calls["classify"] += 1; return Likert.STRONGLYAGREE
def no_write(*a, **k):
    calls["write"] += 1; raise AssertionError("write_essay must not be called")
prism_eval.gate_verdict, prism_eval.classify_essay, prism_eval.write_essay = fake_gate, fake_classify, no_write
base = {"provider": "openai", "model": "gpt-3.5-turbo", "role": "evolved", "role_text": roles["pcxrightauth"][1].strip(),
        "temperature": 0.0, "assessor": "gpt-4o-mini", "assessor_provider": "openai", "no_refusal_retry": True,
        "config_id": cid, "basepath": "../data", "outpath": T}
def check(name, cond): print(("  PASS " if cond else "  FAIL ") + name); assert cond, name

r1 = prism_eval.evaluate_prism_config(dict(base))
check("ungated run reads the existing cache (no gate, no classify)", calls["gate"] == 0 and calls["classify"] == 0)
check(f"ungated score matches published {run['social']:+.3f}", abs(r1["social"] - run["social"]) < 1e-9)
check("ungated result reports refusal_gate=None", r1["refusal_gate"] is None)

r2 = prism_eval.evaluate_prism_config(dict(base, refusal_gate=True))
check(f"gated run calls the gate 62 times (got {calls['gate']})", calls["gate"] == 62)
check(f"gated run skips classify for the 2 REFUSED statements (got {calls['classify']})", calls["classify"] == 60)
gated = f"{T}/ratings/cache_{cid}_gpt-4o-mini_gate{GATE_VERSION}.json"
check("gated ratings go to a separate _gate cache", os.path.exists(gated))
gc = json.load(open(gated))
check("q4 and q27 scored Refused under the gate", gc["4"]["stance"] == "Refused" and gc["27"]["stance"] == "Refused")
check("DISCLAIMED is scored normally", gc["58"]["stance"] == "Strongly agree" and gc["58"]["gate"] == "DISCLAIMED")
check("verdict stored per statement", all("gate" in v for v in gc.values()))
check(f"result counts {r2['refusal_gate']}", r2["refusal_gate"] == {"REFUSED": 2, "DISCLAIMED": 1, "COMPLIED": 59})
check("refused statements counted in l2_refusals", r2["l2_refusals"] == 2)
check("ungated cache byte-identical after the gated run", hashlib.md5(open(ungated, "rb").read()).hexdigest() == before)
check("gated rating CSV is separately named", any("_gate" in os.path.basename(p) for p in glob.glob(f"{T}/ratings/ratings_*.csv")))

g0, c0 = calls["gate"], calls["classify"]
r3 = prism_eval.evaluate_prism_config(dict(base, refusal_gate=True))
check("second gated run is served from the gated cache", calls["gate"] == g0 and calls["classify"] == c0)
check("cached gated run reports the same counts", r3["refusal_gate"] == r2["refusal_gate"])
check("write_essay never called", calls["write"] == 0)
print("ALL PLUMBING CHECKS PASSED")
