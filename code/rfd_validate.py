"""Score an assessor against human-labelled stance data.

Every assessor result in this project so far compares one model against another.
That establishes disagreement but never who is right. Room For Debate (Saha,
Lakshmanan & Ng, Computational Linguistics 50(1), 2024) supplies the missing
side: 764 (claim, op-ed, human label) triples, two annotators with a third
adjudicating, Cohen's kappa 0.8285.

It fits this project unusually well. The articles have a median of 2,286
characters and 95% are at least 1,500, so they sit in the same band as the
essays being assessed — every other stance corpus checked is tweets or single
sentences. And 359 of the 764 argue *against* their claim, which is the case
the assessors get wrong.

    python rfd_validate.py --pickle RFD_claim_article_label.p \\
        --assessor mistral --assessor-provider ollama

The headline number is the bottom-left cell: how often the assessor reports
agreement on an article a human labelled as arguing against the claim.

The corpus is verbatim NYT op-eds under CC BY-NC-ND. Compute over it locally;
do not redistribute the text.
"""

import argparse
import json
import pickle
from collections import Counter
from pathlib import Path

from prism_eval import classify_essay
from utils.utils import Likert

# RFD's integer labels.
GOLD = {0: "pro", 1: "con", 2: "balanced"}

# The assessor answers on PRISM's six-point scale; RFD is three-way. Collapse
# the scale rather than the gold labels, and keep Refused visible instead of
# folding it into either side.
COLLAPSE = {
    Likert.STRONGLYAGREE: "pro", Likert.AGREE: "pro",
    Likert.STRONGLYDISAGREE: "con", Likert.DISAGREE: "con",
    Likert.NEUTRAL: "balanced", Likert.REFUSED: "refused",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pickle", required=True)
    ap.add_argument("--assessor", default="mistral")
    ap.add_argument("--assessor-provider", dest="assessor_provider", default="ollama")
    ap.add_argument("--assessor-prompt", dest="assessor_prompt",
                    choices=["paper", "explicit"], default="paper")
    ap.add_argument("--assessor-base-url", dest="assessor_base_url", default=None)
    ap.add_argument("--limit", type=int, default=None, help="score only the first N")
    ap.add_argument("--outpath", default="../out")
    args = ap.parse_args()

    data = pickle.loads(Path(args.pickle).read_bytes())
    items = sorted(data.items())
    if args.limit:
        items = items[:args.limit]

    tag = "" if args.assessor_prompt == "paper" else f"_{args.assessor_prompt}"
    cache_path = Path(args.outpath, "ratings",
                      f"rfd_{args.assessor.replace('/', '_')}{tag}.json")
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    for key, rec in items:
        if key in cache:
            continue
        stance = classify_essay(rec["claim"], rec["article"], args.assessor,
                                args.assessor_provider, None,
                                args.assessor_base_url, args.assessor_prompt)
        cache[key] = stance.value
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=1, sort_keys=True))

    pairs = [(GOLD[rec["label"]], COLLAPSE[Likert(cache[key])])
             for key, rec in items if key in cache]

    print(f"assessor {args.assessor}, prompt '{args.assessor_prompt}', n={len(pairs)}")
    print(f"human agreement on this corpus: Cohen's kappa 0.8285 (published)\n")

    cats = ["pro", "con", "balanced", "refused"]
    print("rows = human gold, columns = assessor")
    print(f"  {'':<10}" + "".join(f"{c:>10}" for c in cats) + f"{'n':>8}")
    for g in ["pro", "con", "balanced"]:
        row = [p for p in pairs if p[0] == g]
        counts = Counter(a for _, a in row)
        print(f"  {g:<10}" + "".join(f"{counts[c]:>10}" for c in cats) + f"{len(row):>8}")

    con = [p for p in pairs if p[0] == "con"]
    pro = [p for p in pairs if p[0] == "pro"]
    con_err = sum(1 for _, a in con if a == "pro")
    pro_err = sum(1 for _, a in pro if a == "con")

    print(f"\nDirectional error, against human gold:")
    print(f"  article argues AGAINST the claim, read as agreement : "
          f"{con_err}/{len(con)} = {100*con_err/max(len(con),1):.1f}%")
    print(f"  article argues FOR the claim, read as opposition    : "
          f"{pro_err}/{len(pro)} = {100*pro_err/max(len(pro),1):.1f}%")

    exact = sum(1 for g, a in pairs if g == a)
    print(f"\nthree-way accuracy: {exact}/{len(pairs)} = {100*exact/len(pairs):.1f}%")
    print("(a majority-class guesser scores 47.0% on this corpus, so accuracy alone "
          "flatters;\n the directional split above is the number that matters)")


if __name__ == "__main__":
    main()
