import json, glob, sys
sys.path.insert(0, "code")
from utils.utils import read_questions_from_file
qs = read_questions_from_file("data/compass_questions.txt")
rows = {}
for f in glob.glob("results/gated_m4_gemma_[0-9].json"):
    for r in json.load(open(f))["runs"]: rows[r["persona"]] = r["config_id"]
items = [("librarian", "4", "REFUSED")] + [(p, q, "NOT_REFUSED") for p, q in
         [("intelligentagent", "51"), ("science", "19"), ("social", "51"), ("conservative", "19"), ("pcxrightauth", "38"), ("goodhuman", "51"), ("man", "51")]]
out = []
for p, q, lab in items:
    txt = open(glob.glob(f"out/essays/pc{q}_*_{rows[p]}.txt")[0], errors="ignore").read()
    out.append(dict(model="gemma3", persona=p, q=int(q), statement=qs[int(q)], opening=txt[:500], label=lab))
json.dump(dict(note="Hand-read labels, same convention as v3_labels_gpt54mini.json.", cases=out),
          open("/tmp/v3_labels_gemma3.json", "w"), indent=1, ensure_ascii=False)
print("saved", len(out), "gemma3 cases")
print("librarian q4 opening (the one REFUSED label):", repr(out[0]["opening"][:420]))
