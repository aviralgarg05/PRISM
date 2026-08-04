"""Compare two assessors scoring the same essays.

The assessor is part of the measurement instrument, not a detail of it. The
PRISM paper used GPT-3.5-Turbo and validated it against two human annotators,
reporting 88.6% agreement and Cohen's kappa of 0.774. Any substitute assessor
needs the same check before its numbers mean anything, because a cheap local
model that systematically reads essays as agreement would manufacture exactly
the acquiescence pattern one might then report as a finding.

This reads two rating caches produced for the same configuration by different
assessors and reports raw agreement, Cohen's kappa, and where they diverge.

  python compare_assessors.py --cid 55c2c3c592 --a llama3.2 --b gpt-3.5-turbo
"""

import argparse
import json
from collections import Counter
from pathlib import Path

LEVELS = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree", "Refused"]
# Ordered so that "how far apart were they" is meaningful for the substantive levels.
ORDER = {lv: i for i, lv in enumerate(LEVELS[:5])}


def load(outpath, cid, assessor):
    p = Path(outpath) / "ratings" / f"cache_{cid}_{assessor.replace('/', '_')}.json"
    if not p.exists():
        raise SystemExit(f"No ratings cache for assessor {assessor!r} at {p}.\n"
                         f"Run the audit with --assessor {assessor} first.")
    return {int(k): v["stance"] for k, v in json.loads(p.read_text()).items()}


def cohens_kappa(pairs):
    """Unweighted Cohen's kappa over the observed label set."""
    n = len(pairs)
    if not n:
        return float("nan")
    labels = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    observed = sum(1 for a, b in pairs if a == b) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    expected = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    if expected == 1.0:
        return float("nan")  # both assessors gave one constant label
    return (observed - expected) / (1 - expected)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cid", required=True, help="Configuration id (see config_id in the run output).")
    ap.add_argument("--a", required=True, help="First assessor.")
    ap.add_argument("--b", required=True, help="Second assessor.")
    ap.add_argument("--outpath", default="../out")
    args = ap.parse_args()

    ra, rb = load(args.outpath, args.cid, args.a), load(args.outpath, args.cid, args.b)
    common = sorted(set(ra) & set(rb))
    if not common:
        raise SystemExit("The two caches share no statements.")

    pairs = [(ra[q], rb[q]) for q in common]
    agree = sum(1 for x, y in pairs if x == y)

    kappa = cohens_kappa(pairs)
    print(f"Statements compared : {len(common)}")
    print(f"Raw agreement       : {agree}/{len(common)} = {100*agree/len(common):.1f}%")
    if kappa != kappa:  # NaN
        print("Cohen's kappa       : undefined - at least one assessor gave a "
              "near-constant label, so there is no variance to correct for. "
              "That is itself the finding: read the distribution below.")
    else:
        print(f"Cohen's kappa       : {kappa:.3f}   "
              f"(paper reports 0.774 for GPT-3.5-Turbo against humans)")

    print(f"\nDistribution")
    da, db = Counter(ra[q] for q in common), Counter(rb[q] for q in common)
    print(f"  {'level':<19}{args.a:>16}{args.b:>16}")
    for lv in LEVELS:
        if da[lv] or db[lv]:
            print(f"  {lv:<19}{da[lv]:>16}{db[lv]:>16}")

    # A systematic shift matters more than scattered noise: it means one
    # assessor reads the same essays as consistently more agreeable.
    both = [(x, y) for x, y in pairs if x in ORDER and y in ORDER]
    if both:
        shift = sum(ORDER[y] - ORDER[x] for x, y in both) / len(both)
        print(f"\nMean shift ({args.b} relative to {args.a}) over the {len(both)} "
              f"statements both scored substantively: {shift:+.2f} Likert levels")
        if abs(shift) >= 0.5:
            print("  A shift this large means the two assessors are not "
                  "interchangeable; positions scored by them cannot be compared.")

    # Whether the disagreements are symmetric noise or a directional failure.
    # Averaged over all statements the two can look similar; split by what the
    # essay actually did they may not. Taking --b as the reference is a
    # convenience, not a ground truth: check some disagreements against the
    # essay text before believing the direction.
    def side(s):
        if s in ("Strongly agree", "Agree"):
            return "agrees"
        if s in ("Strongly disagree", "Disagree"):
            return "disagrees"
        return "other"

    opp = same = opp_err = same_err = 0
    for q in common:
        ref, other = side(rb[q]), side(ra[q])
        if ref == "disagrees":
            opp += 1
            opp_err += other == "agrees"
        elif ref == "agrees":
            same += 1
            same_err += other == "disagrees"

    if opp and same:
        print(f"\nDirectionality of {args.a}'s disagreements, taking {args.b} as reference")
        print(f"  essay opposes the statement : {opp_err}/{opp} read as agreement "
              f"= {100*opp_err/opp:.0f}%")
        print(f"  essay supports the statement: {same_err}/{same} read as disagreement "
              f"= {100*same_err/same:.0f}%")
        hi, lo = max(opp_err/opp, same_err/same), min(opp_err/opp, same_err/same)
        worst = max(opp_err, same_err)
        if hi == 0:
            print("  No directional errors at all - the two assessors read every essay "
                  "the same way round.")
        elif worst < 3:
            # A ratio between one error and one error says nothing. Report the
            # counts and stop rather than dressing up noise as a pattern.
            print(f"  Too few errors ({opp_err + same_err} in total) to call a direction.")
        elif lo == 0 or hi / lo >= 3:
            print("  Strongly asymmetric: this is a directional failure to detect one "
                  "side, not symmetric noise, and it biases every position it touches.")

    disagreements = [(q, x, y) for q, (x, y) in zip(common, pairs) if x != y]
    if disagreements:
        print(f"\nDisagreements ({len(disagreements)}):")
        for q, x, y in disagreements[:20]:
            print(f"  q{q:<3} {args.a}={x:<18} {args.b}={y}")
        if len(disagreements) > 20:
            print(f"  ... and {len(disagreements)-20} more")


if __name__ == "__main__":
    main()
