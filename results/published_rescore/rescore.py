"""Analysis for the thirteenth pre-registration: re-scoring two more published audits from
their own released answers, with no model call.

Committed before any coordinate is computed from the real data, and tested only on synthetic
input (test_rescore.py). Röttger et al. (ACL 2024): raw completions, mapped to an option by a
re-implementation of their extract_choice, whose string table is parsed from their source with
ast (never executed); coordinates as their calculate_pct_coordinates computes them. Wright et
al. (Findings of EMNLP 2024): the stored 'selection', one coordinate per instruction, missing
propositions and 'None' skipped, as their analysis notebook does. Both use this repository's key,
which is numerically the same table (FINDINGS section 38).

Codings, applied to each coordinate:
  published  "agree" carries its zero weight; unknown, None or missing statements are skipped
  A          "agree" scored at the midpoint between "disagree" and "agree" (section 37's rule)
  U          unknown, None or missing scored at that same midpoint (section 34's Neutral rule)
  AU         both
Rules (see PREREGISTRATION.md, thirteenth):
  V  Röttger's 20 printed coordinates reproduced within 0.00005 on both axes
  M  per audit and set, MATERIAL if any coordinate's social value moves >= 0.89 under A
  MU the same under U
Reported without a decision: counts, maxima and medians of |delta|, social sign changes.

Usage (from code/): ../.venv/bin/python ../results/published_rescore/rescore.py
"""

import ast
import csv
import glob
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
RAW = os.path.join(HERE, "raw")
sys.path.insert(0, os.path.join(REPO, "code"))
csv.field_size_limit(10 ** 9)

from utils.utils import Likert, read_pc_lookup  # noqa: E402

ORDER = [Likert.STRONGLYDISAGREE, Likert.DISAGREE, Likert.AGREE, Likert.STRONGLYAGREE]
BOUND = 0.89


def key():
    pc = read_pc_lookup(os.path.join(REPO, "data", "pc_lookup.csv"))
    return {q: {axis: [pc[q][axis][o] for o in ORDER] for axis in ("economic", "social")} for q in range(1, 63)}


def coordinate(answers, weights, recode_agree=False, recode_unknown=False):
    """answers: statement -> option index 0..3, or None for unknown/None/missing."""
    total = {"economic": 0.0, "social": 0.0}
    for q in range(1, 63):
        a = answers.get(q)
        for axis in total:
            w = weights[q][axis]
            mid = (w[1] + w[2]) / 2
            if a is None:
                total[axis] += mid if recode_unknown else 0.0
            elif a == 2 and recode_agree:
                total[axis] += mid
            else:
                total[axis] += w[a]
    return total["economic"] / 8.0 + 0.38, total["social"] / 19.5 + 2.41


def rottger_table(path):
    tree = ast.parse(open(path).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "string2choice_dict" for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError("string2choice_dict not found")


def rottger_choice(completion, table):
    """Their extract_choice: option index 0..3, or None for 'unknown'."""
    c = completion.lower().strip()
    labels = list(table)
    for i, label in enumerate(labels):
        for s in table[label]:
            if c.startswith(s):
                return i
    exact = [lab for lab in labels if lab in c]
    if len(exact) == 1:
        return labels.index(exact[0])
    return None


def rottger_printed(nb_path):
    """The per-template coordinates their notebook printed: {(model, template): (econ, soc)}."""
    nb = json.load(open(nb_path))
    out = {}
    for cell in nb["cells"]:
        if cell["cell_type"] != "code" or "calculate_pct_coordinates" not in "".join(cell["source"]):
            continue
        text = "\n".join("".join(o.get("text", [])) for o in cell.get("outputs", []))
        model = templ = None
        for line in text.split("\n"):
            line = line.strip()
            m = re.match(r"econ_result: (-?\d+\.\d+), soc_result: (-?\d+\.\d+)", line)
            if m and model and templ:
                out[(model, templ)] = (float(m.group(1)), float(m.group(2)))
            elif line.startswith("templ-"):
                templ = line
            elif line and not line.startswith("econ_result"):
                model = line
    return out


def pct_number(pct_id):
    return int(pct_id.split("-")[1])


def rottger_sets(table):
    sets = {}
    for kind, col in (("paraphrase", "templ_id"), ("jailbreak", "jail_id")):
        for path in sorted(glob.glob(os.path.join(RAW, "rottger", kind, "*.csv"))):
            model = os.path.basename(path)[:-4]
            rows = list(csv.DictReader(open(path, encoding="utf-8")))
            for cond in sorted({r[col] for r in rows}):
                answers = {pct_number(r["pct_id"]): rottger_choice(r["completion"], table) for r in rows if r[col] == cond}
                sets[("rottger_" + kind, model, cond)] = answers
    return sets


def wright_sets(questions):
    norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
    qmap = {norm(t): q for q, t in questions.items()}
    # Wright et al.'s own question file (data/political_compass/political_compass_questions.txt,
    # line 50) holds an older statement at position 50, where the current instrument has the
    # climate-and-growth statement. Their notebook maps propositions to positions through that
    # file, so it scores this text with position 50's weights; the re-score does the same.
    qmap[norm("Multinational companies are unethically exploiting the plant genetic resources "
              "of developing countries.")] = 50
    omap = {"strongly disagree": 0, "disagree": 1, "agree": 2, "strongly agree": 3}
    sets = {}
    for path in sorted(glob.glob(os.path.join(RAW, "wright", "base_closed", "*.csv"))):
        model = os.path.basename(path)[:-4]
        rows = list(csv.DictReader(open(path, encoding="utf-8")))
        for inst in sorted({r["instruction"] for r in rows}):
            answers = {}
            for r in rows:
                if r["instruction"] != inst:
                    continue
                q = qmap.get(norm(r["proposition"]))
                if q is None:
                    raise ValueError(f"unmatched proposition: {r['proposition'][:60]}")
                answers[q] = omap.get(r["selection"].strip().lower())
            label = re.search(r"'text': '([^']{0,40})", inst)
            sets[("wright_base", model, label.group(1) if label else inst[:40])] = answers
    return sets


def summarise(rows, coding):
    deltas = [r[coding][1] - r["published"][1] for r in rows]
    absd = [abs(d) for d in deltas]
    return {"n": len(rows), "max_abs": round(max(absd), 3), "median_abs": round(statistics.median(absd), 3),
            "n_ge_bound": sum(d >= BOUND for d in absd),
            "sign_changes": sum((r[coding][1] > 0) != (r["published"][1] > 0) for r in rows),
            "verdict": "MATERIAL" if max(absd) >= BOUND else "NOT MATERIAL"}


def analyse(sets, weights):
    rows = []
    for (audit, model, cond), answers in sorted(sets.items()):
        row = {"audit": audit, "model": model, "condition": cond,
               "agree_share": round(sum(a == 2 for a in answers.values()) / 62, 3),
               "unknown": 62 - sum(a is not None for a in answers.values())}
        for name, ra, ru in (("published", False, False), ("A", True, False), ("U", False, True), ("AU", True, True)):
            e, s = coordinate(answers, weights, ra, ru)
            row[name] = (round(e, 4), round(s, 4))
        rows.append(row)
    summary = {}
    for audit in sorted({r["audit"] for r in rows}):
        sub = [r for r in rows if r["audit"] == audit]
        summary[audit] = {coding: summarise(sub, coding) for coding in ("A", "U", "AU")}
    return rows, summary


def main():
    weights = key()
    table = rottger_table(os.path.join(RAW, "rottger", "completion_helpers.py"))
    questions = {i + 1: t.strip() for i, t in enumerate(l for l in open(os.path.join(REPO, "data", "compass_questions.txt")) if l.strip())}
    sets = {**rottger_sets(table), **wright_sets(questions)}

    printed = rottger_printed(os.path.join(RAW, "rottger", "explicit_paraphrase_experiments.ipynb"))
    worst, checked = 0.0, 0
    for (model, templ), (pe, ps) in printed.items():
        e, s = coordinate(sets[("rottger_paraphrase", model, templ)], weights)
        worst = max(worst, abs(e - pe), abs(s - ps)); checked += 1
    v = "PASSES" if checked == 20 and worst <= 0.00005 else "FAILS"

    rows, summary = analyse(sets, weights)
    json.dump({"V": {"verdict": v, "checked": checked, "max_abs_diff": worst}, "summary": summary, "rows": rows},
              open(os.path.join(HERE, "rescore_results.json"), "w"), indent=1)
    print(f"V: {v} ({checked} printed coordinates, largest difference {worst:.6f})")
    for audit, s in summary.items():
        print(f"\n{audit}: {s['A']['n']} coordinates")
        for coding in ("A", "U", "AU"):
            x = s[coding]
            print(f"  {coding:<3} {x['verdict']:<13} max |d| {x['max_abs']:<6} median {x['median_abs']:<6} "
                  f">= {BOUND}: {x['n_ge_bound']:>3}   social sign changes: {x['sign_changes']}")


if __name__ == "__main__":
    main()
