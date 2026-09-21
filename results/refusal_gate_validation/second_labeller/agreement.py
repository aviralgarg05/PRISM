"""Agreement on the refusal-gate categories: labellers, the author and gate v3.

Run this only after every labeller has returned a filled sheet. It prints the
author's labels and the gate's verdicts case by case, so a labeller who runs it
early is no longer blind.

    .venv/bin/python results/refusal_gate_validation/second_labeller/agreement.py \
        sheet_A.csv [sheet_B.csv] [--names A B] [--gate prefilter ...] [--key key.json] \
        [--author-relabel NAME]

Each filled sheet needs a case_id column and a label column; other columns are
ignored, and rows may be in any order. Labels are REFUSED, DISCLAIMED or
COMPLIED (case-insensitive; R, D and C are accepted). A blank or unreadable
label is reported and left out of every comparison that involves that sheet.

Both labellers should be people other than the author (COLLECTING.md, the
collector's notes, which are not sent to labellers). If the author labelled one
sheet, name it with --author-relabel: that sheet is then left out of the author
comparison and reported as a test-retest of the author's own labels instead, not
as a second labeller.

What it prints:
  - the cases key.json marks as drafted with the case in view (see Codebook
    provenance below)
  - labeller vs labeller, three-way and binary
  - each labeller vs the author, binary only (the author's labels are binary)
  - each labeller vs gate v3, and vs any further verdict in key.json named with --gate
    (gate v3 is always kept), three-way and binary; for gate v3 and the pre-filter,
    the three-way disagreements that follow from the gate being unable to say
    DISCLAIMED are listed apart from the rest
  - every one of those comparisons on all cases and again without the marked cases.
    The mark is a lower bound, so no reduced figure is free of the codebook, and
    neither author figure is independent agreement with the author. On this sheet
    the marked cases include every one the author labelled REFUSED and every
    opening the pre-filter flags, so the reduced comparisons with the author and
    with gate v3 test only the NOT_REFUSED side; the script says so when it happens
  - the cases the author labelled REFUSED and gate v3 released, and whether each is
    marked; a labeller's REFUSED on a marked one is not independent evidence of a
    gate miss
  - for each comparison: n, observed agreement, Cohen's kappa with a bootstrap
    interval, the confusion table, and the case_ids that disagree

Binary means REFUSED against NOT_REFUSED, with DISCLAIMED and COMPLIED both
counted as NOT_REFUSED, because only REFUSED changes an essay's score.

Kappa moves with the marginals: when one category dominates, kappa can be low
while agreement is high (FINDINGS section 9, the llama3.2 pcleftlib row). Read it
beside observed agreement and the table, not alone.

Two definitions. INSTRUCTIONS.md section 3 follows the author's label convention
and departs from the gate's prompt (GATE_PROMPT in code/utils/refusal_gate.py) at
the DISCLAIMED boundary: a writer that says it cannot be the persona and then
argues its own view is REFUSED under the gate's prompt and DISCLAIMED under the
codebook. Three-way agreement between a labeller and a gate's model stage
therefore compares two definitions, not only a person and a gate; report it that
way. That applies to gate v3 only on the openings its pre-filter flags, where the
model stage ran. On an unflagged opening gate v3 answers COMPLIED without a
model, so a labeller's DISCLAIMED there is a three-way disagreement by
construction, whatever the definitions; report it separately.

Codebook provenance. The codebook was written with the author's labels in view,
so agreement with the author is not independent. key.json marks by provenance
the cases whose own text a rule, example or description in INSTRUCTIONS.md
sections 1, 3 and 4 was drafted from, quotes or repeats almost word for word, or
whose boundary a rule was written to settle (codebook_drafted_with_case_in_view,
with the reason in codebook_in_view_reason). The same rules push both labellers
towards the same label on those cases, so the mark bears on labeller vs labeller
and labeller vs gate as well as on labeller vs author. That mark is a lower bound,
so no comparison without those cases is free of the codebook, and the author
comparison without them is not independent agreement either. As applied, it marks
every case the author labelled REFUSED, and every opening the pre-filter flags:
without the marked cases no case is left that the author labelled REFUSED or on
which gate v3 says REFUSED, so the reduced comparisons with the author and with
gate v3 test only the NOT_REFUSED side and say nothing about REFUSED, and kappa
there is 0 or undefined whatever the labellers do (key.json, about.reduced_set).
Labeller vs labeller without the marked cases still counts any case a labeller
calls REFUSED.

What the sample can show. Every case was drawn from essays the persona-shown gate
v2 had already called REFUSED (FINDINGS section 38). Agreement here says whether
people apply the three categories consistently, and whether they side with the
author, on cases an earlier gate flagged. It can show a refusal gate v3 misses
among those cases, but not refusals the earlier gate never flagged: that needs the
sample of gate overturns and the sample not selected by any gate that FRAMING.md
names under RQ3. Even among those cases, the only gate v3 miss by the author's
labels is a case the codebook's substitute rule was drafted from, and whose
wording its first replacement marker paraphrased (key.json, about.selection), so
a labeller's REFUSED there is not independent evidence of a gate miss. On this
set gate v3's verdicts are the pre-filter's, case for case (FINDINGS section
38): its model stage runs on the 7 openings the pre-filter
flags (6 + 1 kept REFUSED in the FINDINGS section 34 gate v3 table) and returns
REFUSED on each, so it never changes a verdict here, and agreement with gate v3
here is agreement with the pre-filter. This sheet is the first part of FRAMING.md
experiment 6; the overturn sample and the unselected sample are not built.

Standard library only; no model is called.
"""
import argparse
import collections
import csv
import hashlib
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
THREE = ("REFUSED", "DISCLAIMED", "COMPLIED")
BINARY = ("REFUSED", "NOT_REFUSED")
ALIASES = {"R": "REFUSED", "D": "DISCLAIMED", "C": "COMPLIED",
           "REFUSE": "REFUSED", "DISCLAIM": "DISCLAIMED", "COMPLY": "COMPLIED", "COMPLIES": "COMPLIED"}


def binary(label):
    return None if label is None else ("REFUSED" if label == "REFUSED" else "NOT_REFUSED")


def read_rows(path):
    """Rows of a CSV as dicts with lower-cased keys, tolerating spreadsheet re-saves."""
    raw = pathlib.Path(path).read_bytes()
    for enc in ("utf-8-sig", "cp1252", "mac_roman"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        sys.exit(f"{path}: cannot decode as UTF-8, cp1252 or Mac Roman")
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(text.splitlines(keepends=True), dialect=dialect)
    return [{(k or "").strip().lower(): (v or "") for k, v in row.items()} for row in reader], enc


def load_sheet(path, key_cases):
    """{case_id: label or None}, plus a list of problems found."""
    rows, enc = read_rows(path)
    problems = []
    if not rows or "case_id" not in rows[0] or "label" not in rows[0]:
        sys.exit(f"{path}: needs case_id and label columns")
    labels, seen = {}, collections.Counter()
    for row in rows:
        cid = row["case_id"].strip()
        if not cid:
            continue
        seen[cid] += 1
        if cid not in key_cases:
            problems.append(f"unknown case_id {cid!r}")
            continue
        text = row["label"].strip().upper()
        label = ALIASES.get(text, text) or None
        if label is not None and label not in THREE:
            problems.append(f"{cid}: label {row['label']!r} is not REFUSED, DISCLAIMED or COMPLIED; left out")
            label = None
        labels[cid] = label
        # The opening is the labelled text; check it was not edited. Spreadsheets
        # may rewrite line endings, so compare with those normalised.
        if "opening" in row and row["opening"]:
            got = row["opening"].replace("\r\n", "\n").replace("\r", "\n")
            if enc == "utf-8-sig" and hashlib.sha256(got.encode("utf-8")).hexdigest() != key_cases[cid]["opening_sha256"]:
                problems.append(f"{cid}: opening differs from the one issued (label still used)")
    for cid, n in seen.items():
        if n > 1:
            problems.append(f"{cid}: appears {n} times; last row used")
    missing = sorted(set(key_cases) - set(labels))
    if missing:
        problems.append(f"{len(missing)} case_ids absent from the sheet: {', '.join(missing)}")
    blank = sorted(c for c, v in labels.items() if v is None)
    if blank:
        problems.append(f"{len(blank)} cases without a usable label: {', '.join(blank)}")
    for cid in missing:
        labels[cid] = None
    return labels, problems


def kappa(pairs):
    """Cohen's kappa over (a, b) pairs; None when chance agreement is 1."""
    n = len(pairs)
    if n == 0:
        return None, None
    po = sum(a == b for a, b in pairs) / n
    ca = collections.Counter(a for a, _ in pairs)
    cb = collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    if pe >= 1.0:
        return po, None
    return po, (po - pe) / (1 - pe)


def bootstrap(pairs, reps, seed=0):
    """Percentile 95% interval for kappa, resampling cases. Resamples where kappa
    is undefined are skipped and counted."""
    if reps <= 0 or not pairs:
        return None
    rng = random.Random(seed)
    vals, skipped = [], 0
    for _ in range(reps):
        sample = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        k = kappa(sample)[1]
        if k is None:
            skipped += 1
        else:
            vals.append(k)
    if len(vals) < reps / 2:
        return None
    vals.sort()
    return vals[int(0.025 * (len(vals) - 1))], vals[int(0.975 * (len(vals) - 1))], skipped


def table(pairs, cats, name_a, name_b):
    """Confusion table, rows = name_a, columns = name_b, with totals."""
    c = collections.Counter(pairs)
    w = max(12, max(len(x) for x in cats) + 1, len(name_a) + 1)
    corner = f"{name_a} \\ {name_b}"
    w = max(w, len(corner) - 2)
    lines = [f"    {corner:<{w + 3}}" + "".join(f"{x:>13}" for x in cats) + f"{'total':>8}"]
    for a in cats:
        lines.append(f"    {a:<{w + 3}}" + "".join(f"{c[(a, b)]:>13}" for b in cats)
                     + f"{sum(c[(a, b)] for b in cats):>8}")
    lines.append(f"    {'total':<{w + 3}}" + "".join(f"{sum(c[(a, b)] for a in cats):>13}" for b in cats)
                 + f"{len(pairs):>8}")
    return "\n".join(lines)


def compare(title, a, b, name_a, name_b, cats, reps, to_binary=False):
    """Print one comparison. a and b map case_id -> label (None = no label)."""
    ids = sorted(cid for cid in a if a[cid] is not None and b.get(cid) is not None)
    if to_binary:
        la = {cid: binary(a[cid]) for cid in ids}
        lb = {cid: binary(b[cid]) for cid in ids}
    else:
        la, lb = {cid: a[cid] for cid in ids}, {cid: b[cid] for cid in ids}
    pairs = [(la[cid], lb[cid]) for cid in ids]
    po, k = kappa(pairs)
    print(f"\n  {title}")
    if not pairs:
        print("    no case labelled by both")
        return None
    ci = bootstrap(pairs, reps)
    ktxt = "undefined (both sides used a single category)" if k is None else f"{k:.3f}"
    if k is not None and ci is not None:
        ktxt += f"  (bootstrap 95% {ci[0]:.3f} to {ci[1]:.3f}, {reps} resamples"
        ktxt += f", {ci[2]} undefined and skipped)" if ci[2] else ")"
    print(f"    n = {len(pairs)}   agreement = {sum(x == y for x, y in pairs)}/{len(pairs)} = {po:.3f}   kappa = {ktxt}")
    print(table(pairs, cats, name_a, name_b))
    diff = [cid for cid in ids if la[cid] != lb[cid]]
    if diff:
        print(f"    disagreements ({len(diff)}): " + ", ".join(f"{cid} {la[cid]}/{lb[cid]}" for cid in diff))
    return {"n": len(pairs), "agreement": po, "kappa": k, "diff": diff}


def by_construction(result, lab, gate_name, cases):
    """Split a three-way gate comparison's disagreements into those that follow from
    the gate being unable to say DISCLAIMED and the rest, and print both.

    The pre-filter never says DISCLAIMED. Gate v3 says DISCLAIMED only where the
    pre-filter flags the opening; elsewhere it answers COMPLIED without a model."""
    if not result or not result["diff"]:
        return
    if gate_name == "prefilter":
        forced = [cid for cid in result["diff"] if lab[cid] == "DISCLAIMED"]
        where = "the pre-filter cannot say DISCLAIMED"
    else:
        forced = [cid for cid in result["diff"]
                  if lab[cid] == "DISCLAIMED" and cases[cid]["gate"]["prefilter"] != "REFUSED"]
        where = "unflagged openings, where gate v3 cannot say DISCLAIMED"
    rest = [cid for cid in result["diff"] if cid not in forced]
    print(f"    of these, by construction ({where}): {len(forced)}"
          + (": " + ", ".join(forced) if forced else ""))
    print(f"    the rest: {len(rest)}" + (": " + ", ".join(rest) if rest else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("sheets", nargs="+", help="one or two filled copies of sheet.csv")
    ap.add_argument("--key", default=str(HERE / "key.json"))
    ap.add_argument("--names", nargs="+", help="short names for the labellers, in sheet order")
    ap.add_argument("--gate", action="append",
                    help="further gate verdict from key.json to compare with (repeatable); "
                         "gate_v3 is always compared as well")
    ap.add_argument("--boot", type=int, default=2000, help="bootstrap resamples for kappa intervals (0 = none)")
    ap.add_argument("--author-relabel", metavar="NAME",
                    help="name of a sheet the author labelled: left out of the author comparison and "
                         "reported as a test-retest of the author's own labels, not as a second labeller")
    args = ap.parse_args()

    if len(args.sheets) > 2:
        sys.exit("give one or two sheets")
    key = json.load(open(args.key))
    cases = key["cases"]
    # gate_v3 is always compared, and stays first so the reference line uses it.
    gates = ["gate_v3"] + [g for g in (args.gate or []) if g != "gate_v3"]
    gates = list(dict.fromkeys(gates))
    available = sorted(next(iter(cases.values()))["gate"])
    for g in gates:
        if g not in available:
            sys.exit(f"--gate {g!r} not in key.json; choose from {', '.join(available)}")
    names = args.names or [f"labeller_{chr(65 + i)}" for i in range(len(args.sheets))]
    if len(names) != len(args.sheets):
        sys.exit("--names needs one name per sheet")
    if len(set(names)) != len(names):
        sys.exit("--names must be distinct")
    if args.author_relabel is not None and args.author_relabel not in names:
        sys.exit(f"--author-relabel {args.author_relabel!r} is not one of the sheet names: {', '.join(names)}")

    labellers = {}
    print(f"key: {args.key} ({len(cases)} cases)")
    for name, path in zip(names, args.sheets):
        labels, problems = load_sheet(path, cases)
        labellers[name] = labels
        counts = collections.Counter(v for v in labels.values() if v is not None)
        print(f"{name}: {path}  " + ", ".join(f"{c} {counts[c]}" for c in THREE)
              + f", unlabelled {sum(v is None for v in labels.values())}")
        for p in problems:
            print(f"    warning: {p}")

    author = {cid: c["author_label"] for cid, c in cases.items()}
    gate = {g: {cid: c["gate"][g] for cid, c in cases.items()} for g in gates}

    # Cases the codebook was drafted with in view. Every labeller comparison is also
    # printed without them; the mark is a lower bound, so none of those reduced
    # figures is free of the codebook.
    in_view = sorted(cid for cid, c in cases.items() if c.get("codebook_drafted_with_case_in_view"))
    if in_view:
        print(f"\nmarked in key.json as drafted with the case in view, by provenance ({len(in_view)} cases; "
              f"a lower bound, see codebook_in_view_reason): {', '.join(in_view)}")

    def drop(lab):
        return {cid: v for cid, v in lab.items() if cid not in in_view}

    reduced = (f"without the {len(in_view)} marked cases; the mark is a lower bound, so this is not "
               "free of the codebook either")

    # When every author REFUSED (or every gate REFUSED) is among the marked cases, the
    # reduced comparison with that side tests only the NOT_REFUSED side.
    def one_sided(ref):
        left = [ref[cid] for cid in ref if cid not in in_view]
        return bool(in_view) and bool(left) and all(v != "REFUSED" for v in left)

    def one_sided_note(side):
        print(f"    note: every case on which {side} says REFUSED is among the marked cases, so this reduced "
              f"comparison contains none; it tests only the NOT_REFUSED side and says nothing about REFUSED, "
              "and kappa here is 0 or undefined whatever the labeller does (key.json, about.reduced_set).")

    if len(labellers) == 2:
        (na, a), (nb, b) = labellers.items()
        print(f"\n=== {na} vs {nb} ===")
        if args.author_relabel is not None:
            print(f"    note: {args.author_relabel} is the author relabelling, so this is not agreement "
                  "between two labellers other than the author.")
        compare("three-way", a, b, na, nb, THREE, args.boot)
        compare("binary (DISCLAIMED and COMPLIED as NOT_REFUSED)", a, b, na, nb, BINARY, args.boot, True)
        if in_view:
            print("    note: on the marked cases both labellers read rules drafted from those cases or "
                  "written to settle them, so agreement there is shaped by the codebook.")
            compare(f"three-way, {reduced}", drop(a), b, na, nb, THREE, args.boot)
            compare(f"binary, {reduced}", drop(a), b, na, nb, BINARY, args.boot, True)

    for name, lab in labellers.items():
        if name == args.author_relabel:
            print(f"\n=== test-retest: {name} (the author, relabelling) vs the author's earlier labels "
                  "(binary) ===")
            print("    note: not a second labeller (FRAMING.md experiment 6), and not blind to the "
                  "author's earlier reading; left out of the author comparison.")
            compare("binary, all cases", lab, author, name, "author_earlier", BINARY, args.boot, True)
            continue
        print(f"\n=== {name} vs author (binary; the author labelled REFUSED / NOT_REFUSED) ===")
        compare("binary, all cases", lab, author, name, "author", BINARY, args.boot, True)
        by_model = collections.defaultdict(dict)
        for cid, c in cases.items():
            by_model[c["model"]][cid] = lab[cid]
        for model, sub in sorted(by_model.items()):
            ids = [cid for cid, v in sub.items() if v is not None]
            same = sum(binary(sub[cid]) == author[cid] for cid in ids)
            print(f"    {model}, all its cases: agreement {same}/{len(ids)}")
        if in_view:
            compare(f"binary, without the {len(in_view)} marked cases; the mark is a lower bound, so this "
                    "is not independent agreement with the author either", drop(lab), author, name,
                    "author", BINARY, args.boot, True)
            if one_sided(author):
                one_sided_note("the author")

    n_flagged = sum(c["gate"]["prefilter"] == "REFUSED" for c in cases.values())
    for g in gates:
        for name, lab in labellers.items():
            print(f"\n=== {name} vs {g} ===")
            r3 = compare("three-way", lab, gate[g], name, g, THREE, args.boot)
            if g.startswith("gate_v3") or g == "prefilter":
                by_construction(r3, lab, g, cases)
            compare("binary (DISCLAIMED and COMPLIED as NOT_REFUSED)", lab, gate[g], name, g, BINARY,
                    args.boot, True)
            if in_view:
                r3r = compare(f"three-way, {reduced}", drop(lab), gate[g], name, g, THREE, args.boot)
                if g.startswith("gate_v3") or g == "prefilter":
                    by_construction(r3r, lab, g, cases)
                compare(f"binary, {reduced}", drop(lab), gate[g], name, g, BINARY, args.boot, True)
                if one_sided(gate[g]):
                    one_sided_note(g)
        if g.startswith("gate_v3"):
            print(f"    note: gate v3 answers COMPLIED, without a model, for any opening its pre-filter does "
                  f"not flag, so it can say DISCLAIMED only on the {n_flagged} flagged openings. A labeller's "
                  "DISCLAIMED on an unflagged opening is a three-way disagreement by construction, listed "
                  "apart above. The gate's model prompt and INSTRUCTIONS.md section 3 define DISCLAIMED "
                  f"differently, but that can matter only on the {n_flagged} flagged openings, where the "
                  "model stage ran.")
        elif g == "prefilter":
            print("    note: the pre-filter returns only REFUSED or COMPLIED, so every DISCLAIMED is a "
                  "three-way disagreement by construction; no model prompt, and so no definition of "
                  "DISCLAIMED, is involved.")
        elif g == "gate_v2_at_selection":
            print("    note: REFUSED on every case by construction of the sample, so agreement with it is "
                  "the share of cases a labeller calls REFUSED.")
        else:
            print("    note: the gate's model prompt and INSTRUCTIONS.md section 3 define DISCLAIMED "
                  "differently, so the three-way figures compare two definitions, not only labeller and gate.")

    print(f"\nreference, author vs {gates[0]} (binary):")
    compare("binary", author, gate[gates[0]], "author", gates[0], BINARY, args.boot, True)

    # A gate v3 miss, by the author's labels, is a case the author called REFUSED and
    # gate v3 released. If the codebook settles it from that very case, a labeller's
    # REFUSED there is not independent evidence that the gate missed a refusal.
    misses = sorted(cid for cid, c in cases.items()
                    if c["author_label"] == "REFUSED" and c["gate"]["gate_v3"] != "REFUSED")
    print(f"\ngate v3 misses by the author's labels: {len(misses)}" + (": " + ", ".join(misses) if misses else ""))
    if misses:
        marked = [cid for cid in misses if cid in in_view]
        print(f"    marked as drafted with the case in view: {', '.join(marked) if marked else 'none'}")
        for name, lab in labellers.items():
            print(f"    {name}: " + ", ".join(f"{cid} {lab[cid] or 'unlabelled'}" for cid in misses))
        if marked:
            print("    note: a labeller's REFUSED on a marked miss is not independent evidence of a gate miss; "
                  "the codebook rule that settles it was drafted from that case (codebook_in_view_reason).")


if __name__ == "__main__":
    main()
