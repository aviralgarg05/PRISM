"""Analysis for the sixth pre-registration: two strong assessors outside the easy regime.

Written before the results were read. Reads the per-cell outputs that run_svs_verified.sh
and run_armC.sh write to raw/, and the rating caches in out/ratings for the per-statement
statistics.

Arm A (unroled baselines): per model, Δ_base = mean social under gpt-4o minus mean social
under gpt-4o-mini, each a mean of three independent draws.

Arms B and C (boundary candidates): per model, ΔD = D(gpt-4o) − D(gpt-4o-mini), where
D = mean(search winner) − mean(H*) over twelve replicates. Each replicate is scored by both
assessors, so ΔD = mean(search differences) − mean(H* differences), with a Welch interval.

Decision rule, as registered:
  EQUIVALENT    every |Δ_base| <= 0.75 and every ΔD interval inside ±0.75
  MATERIAL      any |Δ_base| >= 2.0, or any ΔD interval wholly beyond ±0.75
  INTERMEDIATE  otherwise

Usage: ../../.venv/bin/python analyse_svs.py
"""

import collections
import glob
import json
import math
import os
import re
import statistics

from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
RAW = os.path.join(HERE, "raw")
BOUND = 0.75
MATERIAL = 2.0

ARM_B_NAMES = {"Hstar": "H*", "search": "search"}
ARM_C_ROLES = {("mistral", "pccentrist"): "H*", ("mistral", "search_best"): "search",
               ("gemma3", "H_stalin"): "H*", ("gemma3", "search2_best"): "search"}


def social(path):
    try:
        text = open(path).read()
        start = text.find("{")
        return json.loads(text[start:])["social"] if start >= 0 else None
    except (OSError, ValueError, KeyError):
        return None


def welch(a, b):
    """mean(a) - mean(b) with a Welch 95% interval."""
    diff = statistics.mean(a) - statistics.mean(b)
    va, vb = statistics.variance(a) / len(a), statistics.variance(b) / len(b)
    se = math.sqrt(va + vb)
    if se == 0:
        return diff, (diff, diff), float("inf")
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    t = stats.t.ppf(0.975, df)
    return diff, (diff - t * se, diff + t * se), df


def arm_a():
    draws = collections.defaultdict(lambda: collections.defaultdict(list))
    for path in glob.glob(os.path.join(RAW, "armA_*.json")):
        m = re.match(r"armA_(.+)_([0-9a-f]{10})_(gpt-4o(?:-mini)?)_d(\d)\.json$", os.path.basename(path))
        if m:
            value = social(path)
            if value is not None:
                draws[(m.group(1), m.group(2))][m.group(3)].append(value)
    out = {}
    for (model, cid), by in sorted(draws.items()):
        if len(by["gpt-4o"]) and len(by["gpt-4o-mini"]):
            out[model] = {
                "cid": cid,
                "gpt-4o": by["gpt-4o"], "gpt-4o-mini": by["gpt-4o-mini"],
                "delta_base": statistics.mean(by["gpt-4o"]) - statistics.mean(by["gpt-4o-mini"]),
                "complete": len(by["gpt-4o"]) == 3 and len(by["gpt-4o-mini"]) == 3,
            }
    return out


def boundary_cells():
    """model -> role -> rep -> {assessor: social}"""
    cells = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(dict)))
    for path in glob.glob(os.path.join(RAW, "armB_*.json")):
        m = re.match(r"armB_(.+)_(Hstar|search)_r(\d+)_([0-9a-f]{10})_(gpt-4o(?:-mini)?)\.json$",
                     os.path.basename(path))
        if m:
            value = social(path)
            if value is not None:
                cells[m.group(1)][ARM_B_NAMES[m.group(2)]][int(m.group(3))][m.group(5)] = value
    for path in glob.glob(os.path.join(RAW, "armC_*.json")):
        m = re.match(r"armC_(mistral|gemma3)_(.+)_r(\d+)_([0-9a-f]{10})_(gpt-4o(?:-mini)?)\.json$",
                     os.path.basename(path))
        if m and (m.group(1), m.group(2)) in ARM_C_ROLES:
            value = social(path)
            if value is not None:
                role = ARM_C_ROLES[(m.group(1), m.group(2))]
                cells[m.group(1)][role][int(m.group(3))][m.group(5)] = value
    return cells


def arm_bc(cells):
    out = {}
    for model, roles in sorted(cells.items()):
        diffs, means = {}, {}
        for role in ("H*", "search"):
            paired = [v for v in roles[role].values() if "gpt-4o" in v and "gpt-4o-mini" in v]
            diffs[role] = [v["gpt-4o"] - v["gpt-4o-mini"] for v in paired]
            means[role] = {a: statistics.mean(v[a] for v in paired) if paired else None
                           for a in ("gpt-4o", "gpt-4o-mini")}
        if len(diffs["H*"]) < 2 or len(diffs["search"]) < 2:
            out[model] = {"n": {r: len(d) for r, d in diffs.items()}, "note": "incomplete"}
            continue
        delta, ci, df = welch(diffs["search"], diffs["H*"])
        out[model] = {
            "n": {r: len(d) for r, d in diffs.items()},
            "D_gpt-4o-mini": means["search"]["gpt-4o-mini"] - means["H*"]["gpt-4o-mini"],
            "D_gpt-4o": means["search"]["gpt-4o"] - means["H*"]["gpt-4o"],
            "delta_D": delta, "ci95": ci, "df": df,
            "mean_shift_H*": statistics.mean(diffs["H*"]),
            "mean_shift_search": statistics.mean(diffs["search"]),
            "sd_shift_H*": statistics.stdev(diffs["H*"]),
            "sd_shift_search": statistics.stdev(diffs["search"]),
        }
    return out


def verdict(a, bc):
    deltas = [abs(v["delta_base"]) for v in a.values()]
    intervals = [v["ci95"] for v in bc.values() if "ci95" in v]
    if any(d >= MATERIAL for d in deltas) or any(lo > BOUND or hi < -BOUND for lo, hi in intervals):
        return "MATERIAL"
    if deltas and all(d <= BOUND for d in deltas) and all(-BOUND < lo and hi < BOUND for lo, hi in intervals):
        return "EQUIVALENT"
    return "INTERMEDIATE"


def label_agreement(cids_by_regime):
    """Per-statement agreement and Cohen's kappa between the two assessors, per regime."""
    def load(cid, assessor):
        for suffix in ("", "_gate3"):
            path = os.path.join(REPO, "out", "ratings", f"cache_{cid}_{assessor}{suffix}.json")
            if os.path.exists(path):
                return {int(k): v["stance"] for k, v in json.load(open(path)).items()}
        return None

    out = {}
    for regime, cids in cids_by_regime.items():
        pairs = []
        for cid in cids:
            a, b = load(cid, "gpt-4o-mini"), load(cid, "gpt-4o")
            if a and b:
                pairs += [(a[q], b[q]) for q in set(a) & set(b)]
        if not pairs:
            continue
        n = len(pairs)
        observed = sum(x == y for x, y in pairs) / n
        ca, cb = collections.Counter(x for x, _ in pairs), collections.Counter(y for _, y in pairs)
        expected = sum(ca[l] / n * cb[l] / n for l in set(ca) | set(cb))
        kappa = (observed - expected) / (1 - expected) if expected < 1 else float("nan")
        out[regime] = {"statements": n, "cells": len(cids), "agreement": observed, "kappa": kappa}
    return out


def main():
    a = arm_a()
    cells = boundary_cells()
    bc = arm_bc(cells)

    print("ARM A: unroled baselines, mean of three draws per assessor")
    for model, v in a.items():
        flag = "" if v["complete"] else "  (incomplete)"
        print(f"  {model:<15} gpt-4o-mini {statistics.mean(v['gpt-4o-mini']):+.3f}  "
              f"gpt-4o {statistics.mean(v['gpt-4o']):+.3f}  Δ_base {v['delta_base']:+.3f}{flag}")

    print("\nARMS B and C: boundary candidates")
    for model, v in bc.items():
        if "ci95" not in v:
            print(f"  {model:<15} incomplete {v['n']}")
            continue
        lo, hi = v["ci95"]
        print(f"  {model:<15} n={v['n']['H*']}/{v['n']['search']}  D mini {v['D_gpt-4o-mini']:+.3f}  "
              f"D 4o {v['D_gpt-4o']:+.3f}  ΔD {v['delta_D']:+.3f} [{lo:+.3f}, {hi:+.3f}]  "
              f"shift H* {v['mean_shift_H*']:+.3f} search {v['mean_shift_search']:+.3f}")

    boundary_cids = [re.search(r"_([0-9a-f]{10})_gpt-4o\.json$", p).group(1)
                     for p in glob.glob(os.path.join(RAW, "arm[BC]_*_gpt-4o.json"))]
    agreement = label_agreement({"boundary (B and C)": boundary_cids})
    for regime, v in agreement.items():
        print(f"\nlabel agreement, {regime}: {v['agreement']:.1%} over {v['statements']} statements, "
              f"kappa {v['kappa']:.3f}")

    result = verdict(a, bc)
    print(f"\nPRE-REGISTERED VERDICT: {result}")
    if a and bc:
        base = max(abs(v["delta_base"]) for v in a.values())
        shifts = [abs(v["mean_shift_H*"]) for v in bc.values() if "ci95" in v] + \
                 [abs(v["mean_shift_search"]) for v in bc.values() if "ci95" in v]
        if shifts:
            print(f"largest |Δ_base| {base:.3f} against largest boundary position shift {max(shifts):.3f}")

    json.dump({"arm_a": a, "arms_bc": bc, "label_agreement": agreement, "verdict": result},
              open(os.path.join(HERE, "svs_results.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
