"""How often does gate v3's model stage overturn its pre-filter, across the whole corpus?

The 44 hand-labelled cases cannot answer this: the pre-filter flags only 7 of
them and all 7 are true refusals, so the model stage never faces a flagged
non-refusal there. This reads every verdict the shipped v3 gate has already
cached (`out/ratings/cache_*_gpt-4o-mini_gate3.json`) and compares it with the
pre-filter applied to the same essay. No API calls.

Writes its table into persona_blind_ablation.json under "corpus_prefilter_vs_model".

    .venv/bin/python results/refusal_gate_validation/prefilter_vs_model_corpus.py
"""
import collections
import glob
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
from utils.refusal_gate import has_refusal_language  # noqa: E402

OUT = ROOT / "results" / "refusal_gate_validation" / "persona_blind_ablation.json"


def main():
    tot = collections.Counter()
    anomalies = []
    missing = 0
    # gpt-4o-mini only: that is the assessor the gate was validated with, and
    # other assessors' gate3 caches are being written by concurrent work.
    files = sorted(glob.glob(str(ROOT / "out/ratings/cache_*_gpt-4o-mini_gate3.json")))
    for f in files:
        cid = re.match(r".*cache_([0-9a-f]+)_", f).group(1)
        for q, v in json.load(open(f)).items():
            g = v.get("gate")
            if g is None:
                continue
            hits = glob.glob(str(ROOT / f"out/essays/pc{q}_*_{cid}.txt"))
            if not hits:
                missing += 1
                continue
            txt = open(hits[0], errors="ignore").read()
            flag = has_refusal_language(txt)
            tot[(flag, g)] += 1
            if not flag and g != "COMPLIED":
                anomalies.append({"cid": cid, "q": q, "gate": g,
                                  "essay": pathlib.Path(hits[0]).name,
                                  "head": txt[:300]})

    flagged = sum(v for k, v in tot.items() if k[0])
    overturned = sum(v for k, v in tot.items() if k[0] and k[1] != "REFUSED")
    table = {
        "snapshot_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(timespec="seconds"),
        "cache_files": len(files),
        "assessor": "gpt-4o-mini",
        "n_verdicts": sum(tot.values()),
        "essays_not_found": missing,
        "counts": {f"prefilter_{'FLAG' if k[0] else 'pass'}__gate_{k[1]}": v for k, v in tot.items()},
        "prefilter_flagged": flagged,
        "model_overturned_flagged": overturned,
        "model_overturn_rate": round(overturned / flagged, 4) if flagged else None,
        "anomalies_unflagged_but_not_complied": anomalies,
        "note": "A verdict stored by the shipped gate can only be REFUSED or DISCLAIMED if the "
                "pre-filter flagged the essay, so an unflagged non-COMPLIED row means the essay "
                "file changed after the verdict was cached.",
    }
    for k, v in sorted(tot.items(), key=lambda kv: -kv[1]):
        print(f"  prefilter={'FLAG' if k[0] else 'pass':<4} gate={k[1]:<11} {v}")
    print(f"\n{sum(tot.values())} stored v3 verdicts; pre-filter flagged {flagged}; "
          f"model overturned {overturned} ({overturned / flagged:.1%}); "
          f"anomalies {len(anomalies)}; essays not found {missing}")

    if OUT.exists():
        d = json.loads(OUT.read_text())
        d["corpus_prefilter_vs_model"] = table
        OUT.write_text(json.dumps(d, indent=1))
        print(f"merged into {OUT}")
    else:
        print("persona_blind_ablation.json not found; run persona_blind_ablation.py first")


if __name__ == "__main__":
    main()
