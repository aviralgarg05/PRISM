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
from utils.refusal_gate import gate_verdict, GATE_VERSION
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
    ap.add_argument("--refused-as", dest="refused_as", choices=["agree", "neutral"], default="agree",
                    help="score a refused statement as 'agree' (the paper: zero, same as "
                    "Agree) or 'neutral' (that statement's midpoint, so a "
                    "refusal carries no position); see FINDINGS section 34")
    ap.add_argument("--refusal-gate", dest="refusal_gate", action="store_true",
                    help="score declined personas as Refused; see utils/refusal_gate.py")
    ap.add_argument("--role-text", dest="role_text", default=None,
                    help="persona text shown to the refusal gate, if known")
    ap.add_argument("--gate-assessor", dest="gate_assessor", default=None,
                    help="model that runs the refusal gate, if it should differ from "
                    "--assessor. Holding the gate fixed while the stance classifier "
                    "changes is what lets an assessor comparison move one component "
                    "at a time; see FINDINGS section 34")
    ap.add_argument("--run-tag", dest="run_tag", default=None,
                    help="suffix for the rating cache filename, so repeated draws with "
                    "the same assessor do not read each other's cache")
    ap.add_argument("--basepath", default="../data")
    ap.add_argument("--outpath", default="../out")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    questions = read_questions_from_file(f"{args.basepath}/compass_questions.txt")
    pc = read_pc_lookup(f"{args.basepath}/pc_lookup.csv")
    if args.refused_as == "neutral":
        for q in pc:
            for axis in ("economic", "social"):
                pc[q][axis][Likert.REFUSED] = pc[q][axis][Likert.NEUTRAL]

    essays = {}
    for f in Path(args.outpath, "essays").glob(f"*_{args.cid}.txt"):
        essays[int(f.name.split("_")[0][2:])] = f.read_text()
    if not essays:
        raise SystemExit(f"no essays for cid {args.cid}")

    tag = ("" if args.assessor_prompt == "paper" else f"_{args.assessor_prompt}") + (f"_gate{GATE_VERSION}" if args.refusal_gate else "")
    if args.run_tag:
        tag += f"_{args.run_tag}"
    slug = args.assessor.replace("/", "_")
    cache_path = Path(args.outpath, "ratings", f"cache_{args.cid}_{slug}{tag}.json")
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    # Holding the gate fixed means reusing the verdicts it already gave, not asking the
    # same gate model again: its verdicts drift between occasions (FINDINGS section 38,
    # 7 of 44 changed in three days). When the gate assessor differs from --assessor and
    # its gated cache exists for this cid, take the stored verdict per statement and only
    # query the gate for statements it never scored.
    stored_gate = {}
    if args.refusal_gate and args.gate_assessor and args.gate_assessor != args.assessor:
        prompt_tag = "" if args.assessor_prompt == "paper" else f"_{args.assessor_prompt}"
        gate_cache = Path(args.outpath, "ratings",
                          f"cache_{args.cid}_{args.gate_assessor.replace('/', '_')}"
                          f"{prompt_tag}_gate{GATE_VERSION}.json")
        if gate_cache.exists():
            stored_gate = {k: v.get("gate") for k, v in json.loads(gate_cache.read_text()).items()
                           if isinstance(v, dict) and "gate" in v}
    gate_reused = gate_drawn = 0

    # No refusal retry: the generating model may not be reachable, and a retry
    # would mean two assessors were no longer scoring the same essays.
    for qno in sorted(essays):
        if str(qno) in cache:
            continue
        gate = None
        if args.refusal_gate and str(qno) in stored_gate:
            gate = stored_gate[str(qno)]
            gate_reused += 1
        elif args.refusal_gate:
            gate = gate_verdict(args.role_text, questions[qno], essays[qno],
                                args.gate_assessor or args.assessor,
                                args.assessor_provider)
            gate_drawn += 1
        if gate == "REFUSED":
            stance = Likert.REFUSED
        else:
            stance = classify_essay(questions[qno], essays[qno], args.assessor,
                                    args.assessor_provider, None, None, args.assessor_prompt)
        refused = stance == Likert.REFUSED
        cache[str(qno)] = {"stance": stance.value, "l1": int(refused), "l2": int(refused)}
        if args.refusal_gate:
            cache[str(qno)]["gate"] = gate
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
        "gate_assessor": (args.gate_assessor or args.assessor) if args.refusal_gate else None,
        "gate_verdicts_reused": gate_reused if args.refusal_gate else None,
        "gate_verdicts_drawn": gate_drawn if args.refusal_gate else None,
        "run_tag": args.run_tag,
        "assessor_prompt": args.assessor_prompt,
        "refused_as": args.refused_as,
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
