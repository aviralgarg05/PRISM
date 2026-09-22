"""Synthetic check of analyse_flip_sampled.py before any sampled essay exists.

Run from code/: ../.venv/bin/python ../results/stance_flip/test_analyse_flip_sampled.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "code"))

from analyse_flip_sampled import cells, verdict, wilson  # noqa: E402


def world(rates, distinct=True):
    runs, caches, essays = [], {}, {}
    for p, k in rates.items():
        for rep in range(24):
            cid = f"{p}{rep}"
            stance = "Strongly agree" if rep < k else "Strongly disagree"
            caches[cid] = {q: {"stance": stance, "gate": "COMPLIED"} for q in ("4", "27")}
            for q in ("4", "27"):
                essays[(q, cid)] = f"{p} {rep if distinct else 0} {stance}"
            runs.append({"persona": p, "config_id": cid})
    return cells(runs, lambda c: caches[c], lambda q, c: essays[(q, c)])


def test_wilson():
    lo, hi = wilson(12, 24)
    assert lo < 0.5 < hi and wilson(0, 24)[0] == 0.0 and wilson(24, 24)[1] == 1.0


def test_labels():
    assert verdict(world({"none": 0, "seed": 0, "crossover": 20, "mutation": 0})) == "TRANSFERS"
    assert verdict(world({"none": 0, "seed": 0, "crossover": 2, "mutation": 0})) == "RESISTED"
    assert verdict(world({"none": 0, "seed": 0, "crossover": 8, "mutation": 0})) == "PARTIAL"


def test_degenerate_when_essays_repeat():
    v = verdict(world({"none": 0, "seed": 0, "crossover": 24, "mutation": 0}, distinct=False))
    assert v.startswith("DEGENERATE"), v


if __name__ == "__main__":
    for t in (test_wilson, test_labels, test_degenerate_when_essays_repeat):
        t()
        print(f"  pass  {t.__name__}")
    print("3 passed")
