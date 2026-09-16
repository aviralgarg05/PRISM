"""Item-level psychometrics of the Political Compass instrument as administered to LLM personas.

No new generation and no assessor calls: every number here comes from the cached stance
files in out/ratings, keyed by the config_id recorded in the enumeration results.

For each audited model this reports, over the personas enumerated on it:
  - the share of answers at an extreme of the scale (response style),
  - the corrected item-total correlation of each social statement,
  - Cronbach's alpha over the social items,
  - the eigenvalue shares of the social item correlation matrix (dimensionality),
  - how many social items are constant across the whole persona library.

Usage: ../../.venv/bin/python psychometrics.py
"""

import collections
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "code"))

from utils.utils import Likert, read_pc_lookup  # noqa: E402

STANCE = {
    "strongly agree": Likert.STRONGLYAGREE,
    "agree": Likert.AGREE,
    "neutral": Likert.NEUTRAL,
    "disagree": Likert.DISAGREE,
    "strongly disagree": Likert.STRONGLYDISAGREE,
    "refused": Likert.REFUSED,
}
EXTREME = {Likert.STRONGLYAGREE, Likert.STRONGLYDISAGREE}


def persona_cids():
    """model -> persona -> config_id, from every enumeration result in results/."""
    found = collections.defaultdict(dict)

    def walk(node, model):
        if isinstance(node, dict):
            model = node.get("model", model)
            for key in ("runs", "rows"):
                seq = node.get(key)
                if isinstance(seq, list):
                    for row in seq:
                        if isinstance(row, dict) and "config_id" in row and "persona" in row:
                            m = row.get("model", model) or "unknown"
                            found[m].setdefault(row["persona"], row["config_id"])
            for value in node.values():
                walk(value, model)
        elif isinstance(node, list):
            for value in node:
                walk(value, model)

    for path in glob.glob(os.path.join(REPO, "results", "**", "*.json"), recursive=True):
        try:
            walk(json.load(open(path)), None)
        except Exception:
            continue
    return found


def stances(cid, assessor="gpt-4o-mini"):
    """The 62 cached stances for one configuration, gated cache preferred."""
    for suffix in ("_gate3", "_gate2", "_gate", ""):
        path = os.path.join(REPO, "out", "ratings", f"cache_{cid}_{assessor}{suffix}.json")
        if os.path.exists(path):
            raw = json.load(open(path))
            out = {}
            for q, rec in raw.items():
                stance = rec.get("stance") if isinstance(rec, dict) else rec
                if isinstance(stance, str) and stance.strip().lower() in STANCE:
                    out[int(q)] = STANCE[stance.strip().lower()]
            return out, os.path.basename(path)
    return None, None


def alpha(matrix):
    """Cronbach's alpha over columns (items) of a personas x items matrix."""
    k = matrix.shape[1]
    item_var = matrix.var(axis=0, ddof=1).sum()
    total_var = matrix.sum(axis=1).var(ddof=1)
    if total_var == 0 or k < 2:
        return None
    return (k / (k - 1)) * (1 - item_var / total_var)


def main():
    lookup = read_pc_lookup(os.path.join(REPO, "data", "pc_lookup.csv"))
    social_items = sorted(q for q in lookup if any(v != 0 for v in lookup[q]["social"].values()))

    report = {}
    for model, personas in sorted(persona_cids().items()):
        rows, names, extreme, refused, total_answers, missing = [], [], 0, 0, 0, 0
        for persona, cid in sorted(personas.items()):
            got, _ = stances(cid)
            if not got or len(got) < 62:
                missing += 1
                continue
            row = []
            for q in social_items:
                likert = got.get(q)
                row.append(float(lookup[q]["social"][likert]))
                if likert in EXTREME:
                    extreme += 1
                if likert == Likert.REFUSED:
                    refused += 1
                total_answers += 1
            rows.append(row)
            names.append(persona)

        if len(rows) < 10:
            report[model] = {"personas_scored": len(rows), "skipped_no_cache": missing,
                             "note": "too few cached personas for item statistics"}
            continue

        matrix = np.array(rows)
        constant = [social_items[i] for i in range(matrix.shape[1]) if matrix[:, i].std() == 0]
        keep = [i for i in range(matrix.shape[1]) if matrix[:, i].std() > 0]
        varying = matrix[:, keep]
        total = varying.sum(axis=1)

        item_total = {}
        for pos, i in enumerate(keep):
            rest = total - varying[:, pos]
            if rest.std() == 0:
                continue
            item_total[social_items[i]] = round(float(np.corrcoef(varying[:, pos], rest)[0, 1]), 3)

        corr = np.corrcoef(varying, rowvar=False)
        eigenvalues = np.sort(np.linalg.eigvalsh(corr))[::-1]
        shares = (eigenvalues / eigenvalues.sum()).round(3)

        negative = {q: r for q, r in item_total.items() if r < 0}
        report[model] = {
            "personas_scored": len(rows),
            "skipped_no_cache": missing,
            "social_items": len(social_items),
            "items_constant_across_library": constant,
            "extreme_answer_share": round(extreme / total_answers, 3),
            "refused_share": round(refused / total_answers, 3),
            "cronbach_alpha_social": round(alpha(varying), 3) if alpha(varying) else None,
            "eigenvalue_shares_top5": [float(x) for x in shares[:5]],
            "first_factor_share": float(shares[0]),
            "item_total_correlations": item_total,
            "items_with_negative_item_total": negative,
            "median_item_total": round(float(np.median(list(item_total.values()))), 3),
        }

    out = os.path.join(HERE, "psychometrics.json")
    json.dump(report, open(out, "w"), indent=1, sort_keys=True)

    print(f"{'model':<16}{'personas':>9}{'alpha':>8}{'factor1':>9}{'extreme':>9}{'neg items':>10}{'const':>7}")
    for model, r in sorted(report.items()):
        if "note" in r:
            print(f"{model:<16}{r['personas_scored']:>9}   {r['note']}")
            continue
        print(f"{model:<16}{r['personas_scored']:>9}{r['cronbach_alpha_social']:>8}"
              f"{r['first_factor_share']:>9}{r['extreme_answer_share']:>9}"
              f"{len(r['items_with_negative_item_total']):>10}{len(r['items_constant_across_library']):>7}")
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
