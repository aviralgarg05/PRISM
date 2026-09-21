"""Synthetic check of analyse_flip.py before any flip arm runs.

Run from code/: ../.venv/bin/python ../results/stance_flip/test_analyse_flip.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "code"))

from analyse_flip import cells, part_a, part_b  # noqa: E402


def table(rates, refuse=()):
    """rates: persona -> endorsement count out of 12 on both statements."""
    runs, caches = [], {}
    for p, k in rates.items():
        for rep in range(12):
            cid = f"{p}{rep}"
            stance = "Strongly agree" if rep < k else "Strongly disagree"
            gate = "REFUSED" if p in refuse else "COMPLIED"
            caches[cid] = {q: {"stance": "Refused" if gate == "REFUSED" else stance, "gate": gate} for q in ("4", "27")}
            runs.append({"persona": p, "config_id": cid})
    return cells(runs, lambda c: caches[c])


def test_persona_carried():
    paper = table({"none": 0, "seed": 0, "crossover": 12, "mutation": 12})
    neutral = table({"none": 0, "seed": 0, "crossover": 10, "mutation": 2})
    v = part_a(paper, neutral)
    assert v == {"A1": "REPRODUCES", "A2": "PERSONA-CARRIED", "A3": "NOT THE FRAME ALONE"}, v
    assert part_a(paper, neutral, "mutation")["A2"] == "FRAME-DEPENDENT"


def test_frame_alone():
    paper = table({"none": 8, "seed": 0, "crossover": 12, "mutation": 12})
    neutral = table({"none": 0, "seed": 0, "crossover": 1, "mutation": 1})
    v = part_a(paper, neutral)
    assert v["A3"] == "FRAME ALONE" and v["A2"] == "FRAME-DEPENDENT", v


def test_transfer_labels_and_refusals():
    assert part_b(table({"none": 0, "seed": 0, "crossover": 9, "mutation": 0})) == "TRANSFERS"
    resisted = table({"none": 0, "seed": 0, "crossover": 12, "mutation": 0}, refuse=("crossover",))
    assert resisted["crossover"]["4"] == {"e": 0.0, "refused": 1.0, "n": 12}
    assert part_b(resisted) == "RESISTED"
    assert part_b(table({"none": 0, "seed": 0, "crossover": 3, "mutation": 0})) == "PARTIAL"


if __name__ == "__main__":
    for t in (test_persona_carried, test_frame_alone, test_transfer_labels_and_refusals):
        t()
        print(f"  pass  {t.__name__}")
    print("3 passed")
