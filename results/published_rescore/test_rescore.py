"""Synthetic check of rescore.py before any real coordinate is computed.

Run from code/: ../.venv/bin/python ../results/published_rescore/test_rescore.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "code"))

from rescore import analyse, coordinate, key, rottger_choice  # noqa: E402

W = key()
TABLE = {"1) strongly disagree": ["1) strongly disagree", "strongly disagree"], "2) disagree": ["2) disagree", "disagree"],
         "3) agree": ["3) agree", "agree"], "4) strongly agree": ["4) strongly agree", "strongly agree"]}


def test_published_nulls():
    assert [round(x, 3) for x in coordinate({q: 2 for q in range(1, 63)}, W)] == [0.38, 2.41]   # all Agree
    assert [round(x, 3) for x in coordinate({}, W)] == [0.38, 2.41]                              # all unknown, skipped
    assert round(coordinate({q: 3 for q in range(1, 63)}, W)[1], 3) == 4.359                     # all Strongly agree


def test_recodings():
    all_agree = {q: 2 for q in range(1, 63)}
    assert round(coordinate(all_agree, W, recode_agree=True)[1], 3) == round(coordinate({}, W, recode_unknown=True)[1], 3)
    assert coordinate(all_agree, W, recode_unknown=True) == coordinate(all_agree, W)   # U leaves answered statements alone


def test_choice_mapping():
    assert rottger_choice("3) Agree", TABLE) == 2
    assert rottger_choice("Strongly disagree", TABLE) == 0
    assert rottger_choice("I'm sorry, I cannot comply.", TABLE) is None
    assert rottger_choice("My view: 2) disagree", TABLE) == 1


def test_material_rule():
    sets = {("x", "m", "c1"): {q: 2 for q in range(1, 63)}, ("x", "m", "c2"): {q: 1 for q in range(1, 63)}}
    rows, summary = analyse(sets, W)
    assert summary["x"]["A"]["verdict"] == "MATERIAL"          # all-Agree moves from +2.41 to the midpoint
    assert summary["x"]["U"]["verdict"] == "NOT MATERIAL"      # nothing unknown


if __name__ == "__main__":
    for t in (test_published_nulls, test_recodings, test_choice_mapping, test_material_rule):
        t()
        print(f"  pass  {t.__name__}")
    print("4 passed")
