import sys, json, os, types
sys.path.insert(0, ".")
import evolve_persona as ev
from utils.roles import roles
T = sys.argv[1]
BAD = roles["pcxrightauth"][1].strip()
captured, prompts = [], []
def fake_eval(cfg):
    captured.append(cfg)
    bad = cfg["role_text"].strip() == BAD
    return {"economic": 0.0, "social": (sum(map(ord, cfg["role_text"])) % 100) / 10.0,
            "response_entropy": 0.5, "l2_refusals": 20 if bad else 0, "subset_saturated": [], "config_id": "x"}
class FakeWriter:
    n = 0
    def invoke(self, prompt):
        prompts.append(prompt); FakeWriter.n += 1
        return types.SimpleNamespace(content="You are a firm traditionalist who values order and duty above personal preference, variant %d." % FakeWriter.n)
ev.evaluate_prism_config = fake_eval
ev.get_model = lambda *a, **k: FakeWriter()
def check(name, cond): print(("  PASS " if cond else "  FAIL ") + name); assert cond, name
def run(extra, out):
    captured.clear(); prompts.clear()
    sys.argv = ["evolve_persona.py", "--model", "gpt-5.4-mini", "--assessor", "gpt-4o-mini", "--writer", "gpt-4o-mini",
                "--direction", "auth", "--max-questions", "0", "--pop-size", "3", "--n-gen", "3",
                "--seeds", "pccentrist,red,pcxrightauth", "--refusal-gate", "--refused-as", "neutral",
                "--out", os.path.join(T, out)] + extra
    ev.main()
for arm, extra in (("control", ["--no-selection"]), ("search", [])):
    run(extra, arm + ".json")
    check(f"{arm}: every evaluation carries refusal_gate=True", all(c.get("refusal_gate") is True for c in captured))
    check(f"{arm}: every evaluation carries refused_as='neutral'", all(c.get("refused_as") == "neutral" for c in captured))
    check(f"{arm}: every evaluation is the full instrument on gpt-5.4-mini",
          all(c.get("max_questions") == 0 and c.get("model") == "gpt-5.4-mini" for c in captured))
    check(f"{arm}: 3 seeds + 2 batches of 3 = 9 evaluations (got {len(captured)})", len(captured) == 9)
    check(f"{arm}: the infeasible seed is never used as a parent", all(BAD not in p for p in prompts))
try:
    sys.argv = ["evolve_persona.py", "--pop-size", "3", "--seeds", "pccentrist,red,pcxrightauth,stalin", "--max-questions", "0"]
    ev.main(); check("more seeds than --pop-size is rejected", False)
except SystemExit as e:
    check("more seeds than --pop-size is rejected", "silently drop" in str(e))
print("ALL EVOLVE PLUMBING CHECKS PASSED")
