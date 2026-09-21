"""Synthetic check of analyse_m6.py, so the rules are tested before any llama3.2 data exists.

Run from code/: ../.venv/bin/python ../results/m6/test_analyse_m6.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "code"))

from analyse_m6 import analyse, p1_label  # noqa: E402
from utils.utils import read_pc_lookup  # noqa: E402

pc = read_pc_lookup(os.path.join(HERE, "..", "..", "data", "pc_lookup.csv"))
REFUSAL = "I cannot write this essay. Instead, here is the other side."
ESSAY = "Strongly agree. The case for this statement is simple."


def world(n_declined):
    """Personas 0..n_declined-1 decline-then-write on 20 statements; the rest comply."""
    names = [f"p{i}" for i in range(6)] + ["blue", "red", "pcleftlib", "pcleftauth", "pcrightlib", "pcrightauth"]
    ungated, gated, caches, essays = [], [], {}, {}
    for i, n in enumerate(names):
        cid = f"c{i}"
        declines = i < n_declined
        cu, cg = {}, {}
        for q in range(1, 63):
            d = declines and q <= 20
            ident = n in ("blue", "red") and q <= 30
            cu[str(q)] = {"stance": "Refused" if ident else "Strongly disagree" if d else "Strongly agree"}
            cg[str(q)] = {"stance": "Refused" if (d or ident) else "Strongly agree",
                          "gate": "REFUSED" if d else "COMPLIED"}
            essays[(q, cid)] = REFUSAL if d else ESSAY
        caches[(cid, False)], caches[(cid, True)] = cu, cg
        ungated.append({"persona": n, "config_id": cid, "social": 0.0 if declines else 4.359,
                        "l2_refusals": sum(v["stance"] == "Refused" for v in cu.values())})
        gated.append({"persona": n, "config_id": cid, "response_entropy": 0.4})
    return analyse(ungated, gated, lambda c, gated: caches[(c, gated)], lambda q, c: essays[(q, c)], pc)


def test_labels():
    assert p1_label([10, 10, 10, 0]) == "REPLICATES"
    assert p1_label([4, 4, 0]) == "ABSENT"
    assert p1_label([5, 0, 0]) == "PARTIAL"
    assert p1_label([10, 10, 0]) == "PARTIAL"


def test_replicates_world():
    summary, rows = world(n_declined=3)
    assert summary["P1"] == "REPLICATES", summary
    assert rows["p0"]["k_gate"] == 20 and rows["p0"]["k_prefilter"] == 20
    assert summary["R"] == "ROBUST"
    assert summary["S1"] == "REPLICATES"   # identity refuses 30, quadrants 0
    assert summary["P2"] in ("MATERIAL", "SMALL")


def test_absent_world():
    summary, _ = world(n_declined=0)
    assert summary["P1"] == "ABSENT"
    assert summary["P2"].startswith("NOT EVALUATED")


if __name__ == "__main__":
    for t in (test_labels, test_replicates_world, test_absent_world):
        t()
        print(f"  pass  {t.__name__}")
    print("3 passed")
