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

DERIVED, which is what decides the framing claim: D, the variation term and the
selection term recomputed with every arm that carries the sentence stripped, against
the published values for the same confirmation.
"""

import argparse
import collections
import json
import math
import statistics

BOUND = 0.75


def welch(a, b):
    ma, mb = statistics.mean(a), statistics.mean(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    se = math.sqrt(va / len(a) + vb / len(b))
    if se == 0:
        return ma - mb, ma - mb, ma - mb, float("inf")
    df = (va / len(a) + vb / len(b)) ** 2 / (
        (va / len(a)) ** 2 / (len(a) - 1) + (vb / len(b)) ** 2 / (len(b) - 1))
    # 95% two-sided t, close enough for df >= 10; 2.201 is t(.975, 11).
    t = 2.201 if df < 20 else 2.093 if df < 40 else 1.96
    d = ma - mb
    return d, d - t * se, d + t * se, df


def verdict(lo, hi):
    if -BOUND < lo and hi < BOUND:
        return "FORMAT-NEUTRAL"
    if lo > BOUND:
        return "FORMAT-CARRIED"
    if hi < -BOUND:
        return "REVERSED"
    return "UNRESOLVED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    args = ap.parse_args()

    soc = collections.defaultdict(list)
    ent = collections.defaultdict(list)
    ref = collections.defaultdict(list)
    header = {}
    for path in args.logs:
        d = json.loads(open(path).read())
        header = {k: d.get(k) for k in ("model", "assessor", "refusal_gate", "refused_as")}
        for r in d["runs"]:
            soc[r["persona"]].append(r["social"])
            ent[r["persona"]].append(r["response_entropy"])
            ref[r["persona"]].append(r["l2_refusals"])
    print(f"{header}\n")

    print(f"{'persona':<24} {'n':>3} {'social':>9} {'sd':>6} {'entropy':>8} {'refused':>8}")
    for p in sorted(soc):
        print(f"{p:<24} {len(soc[p]):>3} {statistics.mean(soc[p]):+9.3f} "
              f"{(statistics.stdev(soc[p]) if len(soc[p]) > 1 else 0):6.3f} "
              f"{statistics.mean(ent[p]):8.3f} {statistics.mean(ref[p]):8.2f}")

    print(f"\nprimary endpoint: intact - stripped, equivalence bound +/-{BOUND}")
    any_pair = False
    for p in sorted(soc):
        twin = p + "_nofmt"
        if twin not in soc:
            continue
        any_pair = True
        d, lo, hi, df = welch(soc[p], soc[twin])
        print(f"  {p:<22} delta {d:+.3f} [{lo:+.3f}, {hi:+.3f}]  df {df:.1f}  {verdict(lo, hi)}")
        de, *_ = welch(ent[p], ent[twin])
        dr, *_ = welch(ref[p], ref[twin])
        print(f"  {'':<22} entropy {de:+.3f}   refusals/run {dr:+.2f}")
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
