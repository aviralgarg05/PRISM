"""Re-score a published audit's own answers to see how much of its position is the zero weight.

Motoki, Pinho Neto & Rodrigues (Public Choice 198, 2024) deposit every answer ChatGPT gave in
their Political Compass runs, together with the weights they scored them with, at Harvard
Dataverse doi:10.7910/DVN/KGMEYI (workbook "GPT dados.xlsx", sheets "quadrant_calculation"
and "weights"). Their Stata code turns a round's totals into a position with

    social = total / 19.5 + 2.41      economic = total / 8 + 0.38

In that key "agree" scores zero on both axes for all 62 statements, so an answer of "agree"
contributes nothing and a run that agrees with everything lands on the intercept. This script
recomputes their positions from their own answers, then recomputes them again with "agree"
scored at the midpoint between "disagree" and "agree", which is the rule this project calls
Neutral, and reports how far the published position moves.

Usage: ../../.venv/bin/python reanalyse_motoki.py
"""

import collections
import io
import json
import os
import statistics
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
DATAVERSE = "https://dataverse.harvard.edu/api/access/datafile/6983236"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "motoki_workbook.xlsx")
OPTIONS = ["strongly disagree", "disagree", "agree", "strongly agree"]


def workbook():
    if not os.path.exists(CACHE):
        request = urllib.request.Request(DATAVERSE, headers={"User-Agent": "curl/8.4.0"})
        open(CACHE, "wb").write(urllib.request.urlopen(request, timeout=300).read())
    return zipfile.ZipFile(CACHE)


def sheet_rows(z, name):
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    sheets = {s.get("name"): rels[s.get(REL + "id")]
              for s in ET.fromstring(z.read("xl/workbook.xml")).iter(MAIN + "sheet")}
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        shared = ["".join(t.text or "" for t in si.iter(MAIN + "t"))
                  for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]
    path = "xl/" + sheets[name].lstrip("/").replace("xl/", "")
    for row in ET.fromstring(z.read(path)).iter(MAIN + "row"):
        values = []
        for cell in row:
            v = cell.find(MAIN + "v")
            text = "" if v is None else v.text
            if cell.get("t") == "s" and text is not None:
                text = shared[int(text)]
            values.append(text)
        yield values


def main():
    z = workbook()

    weights = {}
    for row in sheet_rows(z, "weights"):
        if row and str(row[0]).strip().isdigit():
            values = [int(float(x)) for x in row[1:9]]
            weights[int(row[0])] = {"economic": dict(zip(OPTIONS, values[:4])),
                                    "social": dict(zip(OPTIONS, values[4:]))}

    rows = list(sheet_rows(z, "quadrant_calculation"))
    header = [h.strip() for h in rows[0]]
    personas = [h for h in header if h in ("chatGPT", "democrats", "republicans",
                                           "radDemocrat", "radRepublican")]
    index = {h: i for i, h in enumerate(header)}

    answers = collections.defaultdict(lambda: collections.defaultdict(dict))
    for row in rows[1:]:
        if not row or not str(row[index["round"]]).strip().isdigit():
            continue
        rnd, question = int(row[index["round"]]), int(row[index["i_question"]])
        for persona in personas:
            value = row[index[persona]]
            if isinstance(value, str) and value.strip().lower() in OPTIONS:
                answers[persona][rnd][question] = value.strip().lower()

    def position(per_question, rule):
        economic = social = 0.0
        for question, option in per_question.items():
            w = weights[question]
            for axis, total in (("economic", "e"), ("social", "s")):
                table = w[axis]
                if rule == "published" or option != "agree":
                    value = table[option]
                else:
                    value = (table["disagree"] + table["agree"]) / 2
                if axis == "economic":
                    economic += value
                else:
                    social += value
        return economic / 8 + 0.38, social / 19.5 + 2.41

    report = {"source": "doi:10.7910/DVN/KGMEYI, GPT dados.xlsx",
              "transform": "economic = total/8 + 0.38, social = total/19.5 + 2.41",
              "personas": {}}

    print(f"{'persona':<16}{'rounds':>7}{'agree %':>9}{'published':>22}{'agree at midpoint':>22}{'social shift':>14}")
    for persona in personas:
        rounds = [r for r, qs in answers[persona].items() if len(qs) == 62]
        if not rounds:
            continue
        published = [position(answers[persona][r], "published") for r in rounds]
        midpoint = [position(answers[persona][r], "midpoint") for r in rounds]
        share = collections.Counter()
        for r in rounds:
            share.update(answers[persona][r].values())
        total_answers = sum(share.values())

        pub_e = statistics.mean(e for e, _ in published)
        pub_s = statistics.mean(s for _, s in published)
        mid_e = statistics.mean(e for e, _ in midpoint)
        mid_s = statistics.mean(s for _, s in midpoint)

        report["personas"][persona] = {
            "rounds": len(rounds),
            "answer_shares": {k: round(v / total_answers, 4) for k, v in share.items()},
            "published_rule": {"economic": round(pub_e, 3), "social": round(pub_s, 3)},
            "agree_at_midpoint": {"economic": round(mid_e, 3), "social": round(mid_s, 3)},
            "shift": {"economic": round(mid_e - pub_e, 3), "social": round(mid_s - pub_s, 3)},
        }
        print(f"{persona:<16}{len(rounds):>7}{share['agree'] / total_answers:>8.1%}"
              f"{f'({pub_e:+.2f}, {pub_s:+.2f})':>22}{f'({mid_e:+.2f}, {mid_s:+.2f})':>22}"
              f"{mid_s - pub_s:>+14.2f}")

    out = os.path.join(HERE, "motoki_reanalysis.json")
    json.dump(report, open(out, "w"), indent=1, sort_keys=True)
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
