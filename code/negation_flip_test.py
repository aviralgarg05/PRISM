"""Check whether an assessor actually tracks the statement it is given.

An assessor is handed a statement and an essay and asked how far the essay
agrees with the statement. If it is doing that job, then replacing the
statement with its negation must flip the answer: an essay that strongly agrees
with S must strongly disagree with NOT-S. An assessor that returns the same
direction for both is not reading the essay against the statement at all - it
is reading something else, most likely how forcefully the essay is written.

This needs no human labels and no external corpus. It reuses essays that have
already been generated, so the only cost is classification.

    python negation_flip_test.py --cid 2b78d1d74d --assessor gpt-4o-mini \\
        --assessor-provider openai

The essays were written about the ORIGINAL statements. That does not change:
the question is only whether the assessor's label tracks the statement it is
shown at classification time.
"""

import argparse
import json
from collections import Counter
from pathlib import Path

from prism_eval import classify_essay
from utils.utils import Likert, read_questions_from_file

# Statements whose negation the review flagged as not cleanly contradictory.
# Excluded from the headline figure by default: a bad negation makes a correct
# assessor look broken, which is exactly the error this test must not make.
# See results/negations.json for the reason attached to each.
FLAGGED = {1, 5, 7, 11, 15, 34, 39}

SIDE = {
    Likert.STRONGLYAGREE: "agrees", Likert.AGREE: "agrees",
    Likert.STRONGLYDISAGREE: "disagrees", Likert.DISAGREE: "disagrees",
}


def side(stance):
    return SIDE.get(stance, "neither")


def load_essays(outpath, cid):
    essays = {}
    for f in Path(outpath, "essays").glob(f"*_{cid}.txt"):
        qno = int(f.name.split("_")[0][2:])
        essays[qno] = f.read_text()
    return essays


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cid", required=True, help="configuration id whose essays to reuse")
    ap.add_argument("--assessor", default="gpt-4o-mini")
    ap.add_argument("--assessor-provider", dest="assessor_provider", default="openai")
    ap.add_argument("--assessor-prompt", dest="assessor_prompt",
                    choices=["paper", "explicit"], default="paper")
    ap.add_argument("--assessor-base-url", dest="assessor_base_url", default=None)
    ap.add_argument("--basepath", default="../data")
    ap.add_argument("--outpath", default="../out")
    ap.add_argument("--include-flagged", action="store_true",
                    help="also report the 7 statements whose negation was flagged as "
                         "not cleanly contradictory")
    args = ap.parse_args()

    original = read_questions_from_file(f"{args.basepath}/compass_questions.txt")
    negated = read_questions_from_file(f"{args.basepath}/compass_questions_negated.txt")
    essays = load_essays(args.outpath, args.cid)
    if not essays:
        raise SystemExit(f"No essays found for cid {args.cid} under {args.outpath}/essays")

    tag = "" if args.assessor_prompt == "paper" else f"_{args.assessor_prompt}"
    cache_path = Path(args.outpath, "ratings",
                      f"flip_{args.cid}_{args.assessor.replace('/', '_')}{tag}.json")
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    rows = []
    for qno in sorted(essays):
        essay = essays[qno]
        key = str(qno)
        if key not in cache:
            a = classify_essay(original[qno], essay, args.assessor,
                               args.assessor_provider, None,
                               args.assessor_base_url, args.assessor_prompt)
            b = classify_essay(negated[qno], essay, args.assessor,
                               args.assessor_provider, None,
                               args.assessor_base_url, args.assessor_prompt)
            cache[key] = {"orig": a.value, "neg": b.value}
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(cache, indent=1, sort_keys=True))
        c = cache[key]
        rows.append({
            "qno": qno,
            "orig": Likert(c["orig"]),
            "neg": Likert(c["neg"]),
            "flagged": qno in FLAGGED,
        })

    def report(subset, title):
        # Only statements the assessor took a side on can flip.
        usable = [r for r in subset
                  if side(r["orig"]) != "neither" and side(r["neg"]) != "neither"]
        if not usable:
            print(f"\n{title}: nothing scored on both sides"); return
        flipped = [r for r in usable if side(r["orig"]) != side(r["neg"])]
        stuck = [r for r in usable if side(r["orig"]) == side(r["neg"])]
        print(f"\n{title}  (n={len(usable)} of {len(subset)} scored substantively both ways)")
        print(f"  flipped as it should        : {len(flipped):>3}  {100*len(flipped)/len(usable):5.1f}%")
        print(f"  same direction for S and ¬S : {len(stuck):>3}  {100*len(stuck)/len(usable):5.1f}%   <- cannot be right")
        if stuck:
            print(f"    statements: {', '.join('q'+str(r['qno']) for r in stuck[:20])}")
        return len(stuck) / len(usable)

    clean = [r for r in rows if not r["flagged"]]
    print(f"assessor {args.assessor}, prompt '{args.assessor_prompt}', cid {args.cid}")
    print(f"essays reused: {len(rows)}")
    rate = report(clean, "Excluding the 7 flagged negations")
    if args.include_flagged:
        report(rows, "All 62, including flagged")

    print("\ndistribution of labels")
    for lbl, k in (("against the original statement", "orig"),
                   ("against its negation", "neg")):
        c = Counter(r[k].value for r in rows)
        print(f"  {lbl:<32} {dict(c)}")

    if rate is not None:
        print(f"\nA competent assessor should sit near 0% here. Anything substantial is")
        print(f"evidence the label is not tracking the statement it was shown.")


if __name__ == "__main__":
    main()
