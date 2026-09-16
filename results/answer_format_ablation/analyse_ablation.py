"""Pre-registered analysis for the answer-format ablation.

Written before the runs, so the decision rule cannot be chosen after seeing the
numbers. Give it the confirmation logs produced by confirm_persona.py; it pairs every
persona X with its ablated twin X_nofmt and applies the rule below.

    python analyse_ablation.py ../results/answer_format_ablation/afmt_m5_paired.json

PRIMARY ENDPOINT, per persona
    delta = mean social(intact) - mean social(stripped), n = 12 per arm,
    Welch t 95% interval.

DECISION at the project's +/-0.75 resolution bound (FINDINGS section 29):
    interval inside (-0.75, +0.75)   FORMAT-NEUTRAL  the sentence carries no
                                     measurable position
    interval entirely above +0.75    FORMAT-CARRIED  the sentence carries at least
                                     0.75 units of the persona's score
    interval entirely below -0.75    REVERSED        removing it raises the score
    anything else                    UNRESOLVED      reported as such, not topped up

SECONDARY, same runs, no extra cost: response entropy, gate-scored refusals per run,
and (for the local models) distinct essays per statement across the twelve replicates.

AMENDMENT B1/B2 (16 September 2026, written after the first A1 blocks were seen and
before any delta was computed): beside every delta, refusals per run and the share of
runs refused on more than six statements; delta recomputed with refused statements
excluded and the raw total pro-rated to 62; and the share of answered statements at an
extreme of the scale. These need the per-statement rating caches, read from
--outpath. A format-carried verdict that comes with a rise in refusals is a result
about whether the persona is played, not a position effect.

NINTH PRE-REGISTRATION: for a libertarian persona pass --libertarian, which applies the
labels with the sign reversed (interval wholly below -0.75 is format-carried).

DERIVED, which is what decides the framing claim: D, the variation term and the
selection term recomputed with every arm that carries the sentence stripped, against
the published values for the same confirmation.
"""

import argparse
import collections
import glob
import json
import math
import os
import statistics
import sys

from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "code"))
from utils.utils import (Likert, read_pc_lookup,  # noqa: E402
                         transform_total_social_score)

BOUND = 0.75


def welch(a, b):
    ma, mb = statistics.mean(a), statistics.mean(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    se = math.sqrt(va / len(a) + vb / len(b))
    if se == 0:
        return ma - mb, ma - mb, ma - mb, float("inf")
    df = (va / len(a) + vb / len(b)) ** 2 / (
        (va / len(a)) ** 2 / (len(a) - 1) + (vb / len(b)) ** 2 / (len(b) - 1))
    t = stats.t.ppf(0.975, df)
    d = ma - mb
    return d, d - t * se, d + t * se, df


def verdict(lo, hi, libertarian=False):
    if libertarian:
        lo, hi = -hi, -lo
    if -BOUND < lo and hi < BOUND:
        return "FORMAT-NEUTRAL"
    if lo > BOUND:
        return "FORMAT-CARRIED"
    if hi < -BOUND:
        return "REVERSED"
    return "UNRESOLVED"


def load_stances(outpath, cid, gated):
    """Per-statement stances for one run, from its rating cache."""
    suffix = "_gate3" if gated else ""
    path = os.path.join(outpath, "ratings", f"cache_{cid}_gpt-4o-mini{suffix}.json")
    if not os.path.exists(path):
        return None
    return {int(q): Likert(v["stance"]) for q, v in json.load(open(path)).items()}


def excluded_social(stances, lookup):
    """Social coordinate with refused statements dropped and the raw total pro-rated to 62."""
    answered = {q: s for q, s in stances.items() if s != Likert.REFUSED}
    if not answered:
        return None
    raw = sum(lookup[q]["social"][s] for q, s in answered.items())
    return transform_total_social_score(raw * 62 / len(answered))


def distinct_essays(outpath, cids):
    """Mean over statements of the number of distinct essay texts across these runs."""
    per_q = collections.defaultdict(set)
    for cid in cids:
        for f in glob.glob(os.path.join(outpath, "essays", f"*_{cid}.txt")):
            per_q[os.path.basename(f).split("_")[0]].add(open(f).read())
    return statistics.mean(len(v) for v in per_q.values()) if per_q else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--outpath", default=os.path.join(HERE, "..", "..", "out"))
    ap.add_argument("--libertarian", action="store_true")
    args = ap.parse_args()
    lookup = read_pc_lookup(os.path.join(HERE, "..", "..", "data", "pc_lookup.csv"))

    soc = collections.defaultdict(list)
    ent = collections.defaultdict(list)
    ref = collections.defaultdict(list)
    exc = collections.defaultdict(list)
    ext = collections.defaultdict(list)
    cids = collections.defaultdict(list)
    header = {}
    for path in args.logs:
        d = json.loads(open(path).read())
        header = {k: d.get(k) for k in ("model", "assessor", "refusal_gate", "refused_as")}
        for r in d["runs"]:
            p = r["persona"]
            soc[p].append(r["social"])
            ent[p].append(r["response_entropy"])
            ref[p].append(r["l2_refusals"])
            cids[p].append(r["config_id"])
            st = load_stances(args.outpath, r["config_id"], bool(header.get("refusal_gate")))
            if st:
                e = excluded_social(st, lookup)
                if e is not None:
                    exc[p].append(e)
                answered = [s for s in st.values() if s != Likert.REFUSED]
                if answered:
                    ext[p].append(sum(s in (Likert.STRONGLYAGREE, Likert.STRONGLYDISAGREE)
                                      for s in answered) / len(answered))
    print(f"{header}\n")

    print(f"{'persona':<24} {'n':>3} {'social':>9} {'sd':>6} {'entropy':>8} {'refused':>8} "
          f"{'runs>6':>7} {'extreme':>8} {'distinct':>9}")
    for p in sorted(soc):
        over = sum(x > 6 for x in ref[p]) / len(ref[p])
        de = distinct_essays(args.outpath, cids[p])
        print(f"{p:<24} {len(soc[p]):>3} {statistics.mean(soc[p]):+9.3f} "
              f"{(statistics.stdev(soc[p]) if len(soc[p]) > 1 else 0):6.3f} "
              f"{statistics.mean(ent[p]):8.3f} {statistics.mean(ref[p]):8.2f} {over:7.0%} "
              f"{(statistics.mean(ext[p]) if ext[p] else float('nan')):8.1%} "
              f"{(f'{de:9.2f}' if de is not None else '      n/a')}")

    print(f"\nprimary endpoint: intact - stripped, equivalence bound +/-{BOUND}")
    any_pair = False
    for p in sorted(soc):
        twin = p + "_nofmt"
        if twin not in soc:
            continue
        any_pair = True
        d, lo, hi, df = welch(soc[p], soc[twin])
        print(f"  {p:<22} delta {d:+.3f} [{lo:+.3f}, {hi:+.3f}]  df {df:.1f}  "
              f"{verdict(lo, hi, args.libertarian)}")
        de, *_ = welch(ent[p], ent[twin])
        dr, *_ = welch(ref[p], ref[twin])
        print(f"  {'':<22} entropy {de:+.3f}   refusals/run {dr:+.2f}")
        if len(exc[p]) > 1 and len(exc[twin]) > 1:
            dx, lx, hx, _ = welch(exc[p], exc[twin])
            print(f"  {'':<22} delta, refused excluded {dx:+.3f} [{lx:+.3f}, {hx:+.3f}]  "
                  f"(secondary, amendment B1)")
    if not any_pair:
        print("  no X / X_nofmt pairs found in these logs")

    # Derived terms. Names differ between confirmations, so pick by substring.
    def pick(kind):
        names = [p for p in soc if kind in p and not p.endswith("_nofmt")]
        return names[0] if names else None

    s, c = pick("search"), pick("control")
    h = next((p for p in soc if p not in (s, c) and not p.endswith("_nofmt")), None)
    if s and c and h:
        def arm(name):
            return name + "_nofmt" if name + "_nofmt" in soc else name
        print("\nderived, every arm that carries the sentence stripped "
              f"(search={arm(s)}, control={arm(c)}, H*={arm(h)}):")
        for a, b, lab in ((arm(s), arm(h), "D  search - H*"),
                          (arm(c), arm(h), "variation  control - H*"),
                          (arm(s), arm(c), "selection  search - control")):
            d, lo, hi, _ = welch(soc[a], soc[b])
            print(f"  {lab:<28} {d:+.3f} [{lo:+.3f}, {hi:+.3f}]")
        print("  published, same confirmation, intact arms:")
        for a, b, lab in ((s, h, "D  search - H*"), (c, h, "variation  control - H*"),
                          (s, c, "selection  search - control")):
            d, lo, hi, _ = welch(soc[a], soc[b])
            print(f"  {lab:<28} {d:+.3f} [{lo:+.3f}, {hi:+.3f}]")


if __name__ == "__main__":
    main()
