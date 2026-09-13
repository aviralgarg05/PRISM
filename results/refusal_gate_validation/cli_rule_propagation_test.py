"""Every entry point must hand --refusal-gate and --refused-as to each evaluation.

A patch once inserted refused_as after the first matching line in
confirm_persona.py, which was the log header rather than the per-run config, so
a gated confirmation silently scored refusals as Agree. This drives the real
entry points with the evaluator stubbed and checks what actually reaches it.
"""
import sys, json, os, tempfile, types, importlib
sys.path.insert(0, ".")
T = tempfile.mkdtemp()
def check(name, cond): print(("  PASS " if cond else "  FAIL ") + name); assert cond, name
captured = []
def fake_eval(cfg):
    captured.append(dict(cfg))
    return {"config_id": "x", "economic": 0.0, "social": 1.0, "response_entropy": 0.5, "l2_refusals": 0,
            "refusal_gate": {"COMPLIED": 62}, "refused_as": cfg.get("refused_as", "agree"), "rows": [], "n_questions": 62}
import confirm_persona as cp
cp.evaluate_prism_config = fake_eval
spec = os.path.join(T, "p.json"); json.dump({"a": "You are a persona.", "subset": {}}, open(spec, "w"))
out = os.path.join(T, "o.json")
sys.argv = ["confirm_persona.py", "--personas", spec, "--reps", "2", "--refusal-gate", "--refused-as", "neutral",
            "--sleep-between", "0", "--out", out]
cp.main()
check("confirm_persona: every run config has refused_as='neutral'", captured and all(c.get("refused_as") == "neutral" for c in captured))
check("confirm_persona: every run config has refusal_gate=True", all(c.get("refusal_gate") is True for c in captured))
check("confirm_persona: every stored row records refused_as='neutral'", all(r["refused_as"] == "neutral" for r in json.load(open(out))["runs"]))
captured.clear()
import evolve_persona as ev
ev.evaluate_prism_config = fake_eval
class W:
    n = 0
    def invoke(self, p):
        W.n += 1; return types.SimpleNamespace(content="You are a firm traditionalist who values order, duty and national loyalty above personal preference, variant %d." % W.n)
ev.get_model = lambda *a, **k: W()
sys.argv = ["evolve_persona.py", "--pop-size", "2", "--n-gen", "2", "--seeds", "pccentrist,red", "--max-questions", "0",
            "--refusal-gate", "--refused-as", "neutral", "--out", os.path.join(T, "e.json")]
ev.main()
check("evolve_persona: every evaluation has refused_as='neutral'", captured and all(c.get("refused_as") == "neutral" for c in captured))
check("evolve_persona: every evaluation has refusal_gate=True", all(c.get("refusal_gate") is True for c in captured))
src = open("political_questions.py").read()
cfg_start = src.index('"no_refusal_retry": args.no_refusal_retry,')
block = src[cfg_start - 1500: cfg_start + 400]
check("political_questions: refused_as is inside the same dict as no_refusal_retry",
      '"refused_as": args.refused_as,' in block and src.count('"refused_as": args.refused_as,') == 1)
print("ALL CLI PROPAGATION CHECKS PASSED")
