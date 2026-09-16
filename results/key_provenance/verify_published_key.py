"""Check this fork's scoring key against the published replication package it came from.

Motoki, Pinho Neto & Rodrigues, "More human than human: measuring ChatGPT political bias",
Public Choice 198 (2024), deposit their materials at Harvard Dataverse
doi:10.7910/DVN/KGMEYI. The workbook "GPT dados.xlsx" holds a sheet named "weights" with a
per-statement table of Political Compass weights, and the Stata do-file applies

    social   = total / 19.5 + 2.41
    economic = total / 8    + 0.38

which are the transforms this repository uses (code/utils/utils.py).

This script downloads the workbook, extracts the weights sheet without any spreadsheet
dependency, and compares it row by row with data/pc_lookup.csv.

Usage: ../../.venv/bin/python verify_published_key.py
"""

import io
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
DATAVERSE = "https://dataverse.harvard.edu/api/access/datafile/6983236"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))


def published_weights(blob):
    """The 'weights' sheet of the replication workbook, as {question: [8 ints]}."""
    z = zipfile.ZipFile(io.BytesIO(blob))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    sheets = {s.get("name"): rels[s.get(REL + "id")]
              for s in ET.fromstring(z.read("xl/workbook.xml")).iter(MAIN + "sheet")}
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        shared = ["".join(t.text or "" for t in si.iter(MAIN + "t"))
                  for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]

    path = "xl/" + sheets["weights"].lstrip("/").replace("xl/", "")
    table = {}
    for row in ET.fromstring(z.read(path)).iter(MAIN + "row"):
        values = []
        for cell in row:
            v = cell.find(MAIN + "v")
            text = "" if v is None else v.text
            if cell.get("t") == "s" and text is not None:
                text = shared[int(text)]
            values.append(text)
        if values and str(values[0]).strip().isdigit():
            table[int(values[0])] = [int(float(x)) for x in values[1:9]]
    return table


def repo_key():
    table = {}
    for line in open(os.path.join(REPO, "data", "pc_lookup.csv")):
        fields = line.strip().split(",")
        if len(fields) == 9:
            table[int(fields[0])] = [int(x) for x in fields[1:]]
    return table


def main():
    cache = os.path.join(HERE, "motoki_weights.json")
    if os.path.exists(cache) and "--refetch" not in sys.argv:
        published = {int(k): v for k, v in json.load(open(cache)).items()}
        source = "cached " + os.path.basename(cache)
    else:
        # Dataverse refuses urllib's default user agent with a 403.
        request = urllib.request.Request(DATAVERSE, headers={"User-Agent": "curl/8.4.0"})
        published = published_weights(urllib.request.urlopen(request, timeout=300).read())
        json.dump(published, open(cache, "w"), indent=1, sort_keys=True)
        source = DATAVERSE

    ours = repo_key()
    same = [q for q in ours if q in published and ours[q] == published[q]]
    differ = [q for q in ours if q in published and ours[q] != published[q]]
    agree_weighted = [q for q, v in published.items() if v[2] != 0 or v[6] != 0]
    social = sum(1 for v in published.values() if any(v[4:]))
    economic = sum(1 for v in published.values() if any(v[:4]))

    print(f"source: {source}")
    print(f"published rows {len(published)}, repo rows {len(ours)}")
    print(f"identical {len(same)}, differing {differ}")
    print(f"published rows where 'agree' carries any weight: {agree_weighted}")
    print(f"published: {social} statements carry social weight, {economic} economic")
    print("\nA respondent who answers 'agree' to all 62 therefore totals 0 on both axes,")
    print("and the published transform puts that at social +2.41, economic +0.38.")


if __name__ == "__main__":
    main()
