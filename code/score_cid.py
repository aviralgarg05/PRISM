"""Score an already-generated essay set with a chosen assessor.

Essays are cached by configuration id, so once they exist the audit can be
re-scored by any assessor without regenerating anything. That matters here
because the assessors differ by more than the thing being measured
(FINDINGS.md sections 16-18), so every essay set is worth scoring with the best
available one rather than whichever was convenient at generation time.

Writes the same rating cache format as evaluate_prism_config, so
compare_assessors.py works against the result.

    python score_cid.py --cid e544b147e3 --assessor gpt-4o-mini \\
        --assessor-provider openai
"""

import argparse
import json
from pathlib import Path

from prism_eval import classify_essay
from utils.utils import (Likert, read_pc_lookup, read_questions_from_file,
                         transform_total_economic_score, transform_total_social_score)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cid", required=True)
    ap.add_argument("--assessor", default="gpt-4o-mini")
    ap.add_argument("--assessor-provider", dest="assessor_provider", default="openai")
    ap.add_argument("--assessor-prompt", dest="assessor_prompt",
                    choices=["paper", "explicit"], default="paper")
    ap.add_argument("--basepath", default="../data")
    ap.add_argument("--outpath", default="../out")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    questions = read_questions_from_file(f"{args.basepath}/compass_questions.txt")
    pc = read_pc_lookup(f"{args.basepath}/pc_lookup.csv")

    essays = {}
    for f in Path(args.outpath, "essays").glob(f"*_{args.cid}.txt"):
        essays[int(f.name.split("_")[0][2:])] = f.read_text()
    if not essays:
        raise SystemExit(f"no essays for cid {args.cid}")

    tag = "" if args.assessor_prompt == "paper" else f"_{args.assessor_prompt}"
    slug = args.assessor.replace("/", "_")
    cache_path = Path(args.outpath, "ratings", f"cache_{args.cid}_{slug}{tag}.json")
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    # No refusal retry: the generating model may not be reachable, and a retry
    # would mean two assessors were no longer scoring the same essays.
    for qno in sorted(essays):
        if str(qno) in cache:
            continue
        stance = classify_essay(questions[qno], essays[qno], args.assessor,
                                args.assessor_provider, None, None, args.assessor_prompt)
        refused = stance == Likert.REFUSED
        cache[str(qno)] = {"stance": stance.value, "l1": int(refused), "l2": int(refused)}
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=1, sort_keys=True))

    e = s = 0
    for qno_s, v in cache.items():
        st = Likert(v["stance"])
        e += pc[int(qno_s)]["economic"][st]
        s += pc[int(qno_s)]["social"][st]
    out = {
        "config_id": args.cid,
        "assessor": args.assessor,
        "assessor_prompt": args.assessor_prompt,
        "n_questions": len(cache),
        "economic": transform_total_economic_score(e),
        "social": transform_total_social_score(s),
        "l2_refusals": sum(v["l2"] for v in cache.values()),
    }
    print(json.dumps(out, indent=2) if args.json else
          f"{args.cid}  econ {out['economic']:+6.2f}  social {out['social']:+6.2f}  "
          f"refused {out['l2_refusals']:>2}/{out['n_questions']}")


if __name__ == "__main__":
    main()
