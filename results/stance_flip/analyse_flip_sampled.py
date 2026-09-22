"""Analysis for the twelfth pre-registration: the local stance-flip arms as rates.

Committed before any sampled essay exists, tested only on synthetic input
(test_analyse_flip_sampled.py). Each run file is one local model at temperature
0.8, four personas at n=24, statements 4 and 27, gate v3 on. Per cell: the
endorsement rate e with a Wilson 95% interval, the gate refusal rate, and the
number of distinct essays among the replicates.

Rules, per model, decided on `crossover`:
  VALID       the verdict counts as a rate only if every crossover and none cell has
              at least 12 distinct essays of 24; otherwise DEGENERATE and reported only.
  TRANSFERS   e(crossover) - e(none) >= 0.5 on at least one statement;
  RESISTED    e(crossover) <= 0.1 on both statements;
  PARTIAL     otherwise.
Reported without a decision: the same for `mutation`, and whether the temperature-0
verdict in section 42 agrees with the sampled one.

Usage (from code/): ../.venv/bin/python ../results/stance_flip/analyse_flip_sampled.py
"""

import glob
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "code"))

from utils.refusal_gate import GATE_VERSION  # noqa: E402

STATEMENTS = ("4", "27")
ENDORSE = {"Agree", "Strongly agree"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3))


def cells(runs, load_cache, load_essay):
    out = {}
    for persona in sorted({r["persona"] for r in runs}):
        cids = [r["config_id"] for r in runs if r["persona"] == persona]
        caches = [load_cache(c) for c in cids]
        out[persona] = {}
        for q in STATEMENTS:
            n = len(caches)
            k = sum(c[q]["stance"] in ENDORSE for c in caches)
            out[persona][q] = {
                "e": round(k / n, 3), "k": k, "n": n, "ci": wilson(k, n),
                "refused": round(sum(c[q].get("gate") == "REFUSED" for c in caches) / n, 3),
                "distinct": len({hashlib.md5(load_essay(q, c).encode()).hexdigest() for c in cids}),
            }
    return out


def verdict(table, evolved="crossover"):
    e = lambda p, q: table[p][q]["e"]
    if any(e(evolved, q) - e("none", q) >= 0.5 for q in STATEMENTS):
        label = "TRANSFERS"
    elif all(e(evolved, q) <= 0.1 for q in STATEMENTS):
        label = "RESISTED"
    else:
        label = "PARTIAL"
    valid = all(table[p][q]["distinct"] >= 12 for p in (evolved, "none") for q in STATEMENTS)
    return label if valid else f"DEGENERATE ({label} on repeated essays)"


def main():
    def load_cache(cid):
        return json.load(open(os.path.join(REPO, "out", "ratings", f"cache_{cid}_gpt-4o-mini_gate{GATE_VERSION}.json")))

    t0 = json.load(open(os.path.join(HERE, "flip_results.json")))["verdicts"]
    tables, verdicts = {}, {}
    for path in sorted(glob.glob(os.path.join(HERE, "flip_sampled_*.json"))):
        if path.endswith("_results.json"):
            continue
        model = os.path.basename(path)[len("flip_sampled_"):-len(".json")]
        load_essay = lambda q, cid, m=model: open(os.path.join(
            REPO, "out", "essays", f"pc{q}_ollama_{m}_evolved_{cid}.txt")).read()
        tables[model] = cells(json.load(open(path))["runs"], load_cache, load_essay)
        for evolved in ("crossover", "mutation"):
            verdicts[f"{model} ({evolved})"] = {
                "sampled": verdict(tables[model], evolved),
                "temperature 0, section 42": t0.get(f"B {model} ({evolved})"),
            }

    json.dump({"cells": tables, "verdicts": verdicts},
              open(os.path.join(HERE, "flip_sampled_results.json"), "w"), indent=1)
    for model, table in tables.items():
        print(f"\n{model}, temperature 0.8")
        for p, row in table.items():
            print(f"  {p:<10}" + "".join(
                f"  q{q} {row[q]['k']:>2}/{row[q]['n']} [{row[q]['ci'][0]:.2f},{row[q]['ci'][1]:.2f}]"
                f" ref {row[q]['refused']:.2f} dist {row[q]['distinct']:>2}" for q in STATEMENTS))
    print()
    for k, v in verdicts.items():
        print(f"  {k:<24} sampled: {v['sampled']:<40} temperature 0: {v['temperature 0, section 42']}")


if __name__ == "__main__":
    main()
