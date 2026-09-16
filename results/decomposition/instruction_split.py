"""Exploratory, not pre-registered: split the per-model acquiescence decomposition by
whether the hand-written persona text itself tells the model which labels to answer with.

Reads only local files: code/utils/roles.py and results/decomposition/all_models_decomposition.json.
No network call. Writes results/decomposition/instruction_split.json.

Groups, by regex over the persona text in roles.py:
  strong : "Strongly Agree or Strongly Disagree"
  plain  : "either Agree or Disagree"
  none   : neither
Search-derived personas (names starting with "_") are excluded.

extreme_share = (Strongly agree + Strongly disagree) / answered statements, from cached
stance counts over all 62 statements; unavailable where the decomposition has no stance
counts (mistral, gemma3, gpt-5.4-mini gate v3). The gpt-5.4-mini (gate v3) block of the
decomposition file was built from results/m5/gate_v3_rescore.json, which is superseded by
gate_v3b_rescore.json, so it is skipped here.
"""
import json
import re
import statistics as st
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "code" / "utils"))
from roles import roles  # noqa: E402

STRONG = re.compile(r"strongly agree or strongly disagree", re.I)
PLAIN = re.compile(r"either agree or disagree", re.I)


def group(name):
    text = roles[name][1]
    if STRONG.search(text):
        return "strong"
    if PLAIN.search(text):
        return "plain"
    return "none"


def main():
    dec = json.load(open(BASE / "results/decomposition/all_models_decomposition.json"))["models"]
    out = {"groups": {g: sorted(n for n in roles if group(n) == g) for g in ("strong", "plain")},
           "models": {}}
    for model, md in dec.items():
        if "gate v3" in model:
            continue
        rows = {}
        for g in ("strong", "plain", "none"):
            beyond, ext = [], []
            for p in md["personas"]:
                n = p["persona"]
                if n.startswith("_") or n not in roles or group(n) != g:
                    continue
                beyond.append(abs(p["beyond_null"]))
                sc = p.get("stance_counts")
                if sc:
                    answered = sum(v for k, v in sc.items() if k != "Refused")
                    if answered:
                        ext.append((sc.get("Strongly agree", 0) + sc.get("Strongly disagree", 0)) / answered)
            rows[g] = {
                "n": len(beyond),
                "mean_abs_beyond_null": round(st.mean(beyond), 3) if beyond else None,
                "mean_extreme_share": round(st.mean(ext), 3) if ext else None,
            }
        out["models"][model] = rows
    (BASE / "results/decomposition/instruction_split.json").write_text(json.dumps(out, indent=1))
    for model, rows in out["models"].items():
        print(model, rows)


if __name__ == "__main__":
    main()
