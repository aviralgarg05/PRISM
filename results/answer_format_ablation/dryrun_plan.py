"""Dry-run the answer-format ablation command with the evaluator stubbed.

Drives the real confirm_persona.py entry point with evaluate_prism_config replaced,
so the block plan, the per-run configs and the flag propagation can be checked
without a single API call. Prints, for each planned run: the persona, the
replicate, the config_id the real run would use, and whether that id is already
cached on this machine (a cache hit costs nothing).

    cd /Users/aviralgarg/stirling/PRISM/code
    /Users/aviralgarg/stirling/PRISM/.venv/bin/python \
        ../results/answer_format_ablation/dryrun_plan.py
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, ".")
REPO = Path(__file__).resolve().parents[2]
ESSAYS = REPO / "out" / "essays"
RATINGS = REPO / "out" / "ratings"

import confirm_persona as cp                      # noqa: E402
from prism_eval import config_id                  # noqa: E402

seen = []


def fake_eval(cfg):
    cid = config_id(cfg)
    cached_e = len(list(ESSAYS.glob(f"*_{cid}.txt")))
    cached_r = bool(list(RATINGS.glob(f"cache_{cid}_*")))
    seen.append(dict(cfg=cfg, cid=cid, essays=cached_e, ratings=cached_r))
    return {"config_id": cid, "economic": 0.0, "social": 0.0, "response_entropy": 0.5,
            "l2_refusals": 0, "refusal_gate": {"COMPLIED": 62},
            "refused_as": cfg.get("refused_as", "agree")}


cp.evaluate_prism_config = fake_eval
personas = str(REPO / "results/answer_format_ablation/personas_m5_gpt54mini_paired.json")
out = str(Path(tempfile.mkdtemp()) / "dryrun.json")
sys.argv = ["confirm_persona.py", "--personas", personas, "--reps", "6",
            "--provider", "openai", "--model", "gpt-5.4-mini",
            "--assessor", "gpt-4o-mini", "--assessor-provider", "openai",
            "--refusal-gate", "--refused-as", "neutral",
            "--block-seed", "401", "--sleep-between", "0", "--out", out]
cp.main()

texts = json.loads(Path(personas).read_text())
print("\n--- planned runs ---")
fresh = cached = 0
for i, s in enumerate(seen, 1):
    c = s["cfg"]
    label = c["prompt_label"]
    name = label[len("confirm-"):label.rindex("-r")]
    assert c["role_text"] == texts[name], f"{name}: persona text did not reach the config"
    assert c["refused_as"] == "neutral" and c["refusal_gate"] is True, "flags did not propagate"
    assert c["model_kwargs"] == {}, "no num_predict must be sent to a hosted model"
    hit = s["essays"] == 62 and s["ratings"]
    fresh += not hit
    cached += hit
    if i <= 10 or not hit:
        print(f"  {i:>2} {label:<34} cid {s['cid']}  "
              f"{'CACHED (free)' if hit else 'FRESH  (62 essays + 62 ratings)'}")
print(f"\n{len(seen)} runs planned: {cached} cached, {fresh} fresh "
      f"= {fresh * 62} essays to generate")
print("flags, persona texts and block structure all check out")
