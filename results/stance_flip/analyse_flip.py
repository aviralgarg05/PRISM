"""Analysis for the eleventh pre-registration: is the section 27 stance flip the persona's,
the frame's, or gpt-3.5-turbo's?

Committed before any flip arm runs, tested only on synthetic input
(test_analyse_flip.py). Each run file is one model and one frame, holding four
personas (none, seed, crossover, mutation) at n=12, each replicate probing
statements 4 and 27 with gate v3 on. For every cell the endpoint is the
endorsement rate e: the share of replicates whose gated stance on that statement
is Agree or Strongly agree. A gate REFUSED verdict counts as not endorsing and is
reported as a refusal rate beside it.

Part A, gpt-3.5-turbo, paper and neutral frames:
  A1  REPRODUCES if e(crossover, paper) - e(seed, paper) >= 0.5 on both statements.
  A2  PERSONA-CARRIED if e(crossover, neutral) - e(none, neutral) >= 0.5 on at
      least one statement; FRAME-DEPENDENT if A1 reproduces and
      e(crossover, neutral) <= 0.25 on both; otherwise MIXED.
  A3  FRAME ALONE if e(none, paper) >= 0.5 on either statement.
Part B, each transfer model, paper frame:
  TRANSFERS if e(crossover) - e(none) >= 0.5 on at least one statement;
  RESISTED if e(crossover) <= 0.1 on both; otherwise PARTIAL.
mutation is reported under the same rules as a second evolved persona.

Usage (from code/): ../.venv/bin/python ../results/stance_flip/analyse_flip.py
"""

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "code"))

from utils.refusal_gate import GATE_VERSION  # noqa: E402

STATEMENTS = ("4", "27")
ENDORSE = {"Agree", "Strongly agree"}


def cells(runs, load_cache):
    """persona -> statement -> {'e': endorsement rate, 'refused': gate refusal rate, 'n': n}."""
    out = {}
    for persona in sorted({r["persona"] for r in runs}):
        caches = [load_cache(r["config_id"]) for r in runs if r["persona"] == persona]
        out[persona] = {}
        for q in STATEMENTS:
            n = len(caches)
            out[persona][q] = {
                "e": round(sum(c[q]["stance"] in ENDORSE for c in caches) / n, 3),
                "refused": round(sum(c[q].get("gate") == "REFUSED" for c in caches) / n, 3),
                "n": n,
            }
    return out


def part_a(paper, neutral, evolved="crossover"):
    e = lambda cell, p, q: cell[p][q]["e"]
    a1 = all(e(paper, evolved, q) - e(paper, "seed", q) >= 0.5 for q in STATEMENTS)
    if any(e(neutral, evolved, q) - e(neutral, "none", q) >= 0.5 for q in STATEMENTS):
        a2 = "PERSONA-CARRIED"
    elif a1 and all(e(neutral, evolved, q) <= 0.25 for q in STATEMENTS):
        a2 = "FRAME-DEPENDENT"
    else:
        a2 = "MIXED"
    a3 = any(e(paper, "none", q) >= 0.5 for q in STATEMENTS)
    return {"A1": "REPRODUCES" if a1 else "NOT REPRODUCED", "A2": a2,
            "A3": "FRAME ALONE" if a3 else "NOT THE FRAME ALONE"}


def part_b(paper, evolved="crossover"):
    e = lambda p, q: paper[p][q]["e"]
    if any(e(evolved, q) - e("none", q) >= 0.5 for q in STATEMENTS):
        return "TRANSFERS"
    if all(e(evolved, q) <= 0.1 for q in STATEMENTS):
        return "RESISTED"
    return "PARTIAL"


def main():
    def load_cache(cid):
        return json.load(open(os.path.join(REPO, "out", "ratings", f"cache_{cid}_gpt-4o-mini_gate{GATE_VERSION}.json")))

    tables, verdicts = {}, {}
    # Arm files only: flip_results.json, this script's own output, also matches flip_*.json.
    arms = glob.glob(os.path.join(HERE, "flip_*_paper.json")) + glob.glob(os.path.join(HERE, "flip_*_neutral.json"))
    for path in sorted(arms):
        name = os.path.basename(path)[5:-5]          # e.g. gpt-3.5-turbo_paper
        tables[name] = cells(json.load(open(path))["runs"], load_cache)

    if "gpt-3.5-turbo_paper" in tables and "gpt-3.5-turbo_neutral" in tables:
        for evolved in ("crossover", "mutation"):
            verdicts[f"A ({evolved})"] = part_a(tables["gpt-3.5-turbo_paper"], tables["gpt-3.5-turbo_neutral"], evolved)
    for name, table in tables.items():
        if name.endswith("_paper") and not name.startswith("gpt-3.5-turbo"):
            for evolved in ("crossover", "mutation"):
                verdicts[f"B {name[:-6]} ({evolved})"] = part_b(table, evolved)

    json.dump({"cells": tables, "verdicts": verdicts}, open(os.path.join(HERE, "flip_results.json"), "w"), indent=1)
    for name, table in tables.items():
        print(f"\n{name}")
        print(f"  {'persona':<11}" + "".join(f"  q{q}: e  refused  n" for q in STATEMENTS))
        for p, row in table.items():
            print(f"  {p:<11}" + "".join(f"  {row[q]['e']:>6.2f} {row[q]['refused']:>7.2f} {row[q]['n']:>2}" for q in STATEMENTS))
    print()
    for k, v in verdicts.items():
        print(f"  {k:<34} {v}")


if __name__ == "__main__":
    main()
