"""Build the persona files for the answer-format ablation (FRAMING item 4, FINDINGS section 36).

WHAT IS BEING TESTED
--------------------
Several of the confirmed winners tell the audited model which label to answer with
("state whether you Strongly Agree or Strongly Disagree"). With 96-100% of answers
at an extreme of the scale on gemma3 and gpt-5.4-mini, part of the measured gain may
be an answer-format effect rather than a move in political position. The direct test
is to confirm the same winners with that instruction removed and nothing else changed.

The winners are not hard-coded here. They are recovered from the search logs
(argmax social over feasible candidates, which is how evolve_persona.py reports a
winner) and then checked against the confirmation runs by recomputing
prism_eval.config_id() for each stored run: a winner is only accepted if its md5
config id reproduces the ids actually confirmed. That check is what makes the quoted
text provably the text that was run.

THE EDIT
--------
Two strip levels are defined, both recorded verbatim below:

  clause  delete only the span that names the response labels. Used wherever the
          directive sits inside a sentence that also carries political content, so
          that no political content is removed with it.
  sentence  delete the whole sentence plus the single separator in front of it
          (a space, or the newline + indentation of the roles.py seeds). Used where
          the sentence is nothing but the directive.

Every edit is a pure deletion of one contiguous span, except one declared
substitution on the mistral search winner, where the label menu is the object of the
verb and deleting it alone leaves an ungrammatical sentence:

    Clearly express either "Agree" or "Disagree" on political issues, ...
    Clearly express your view on political issues, ...

The script asserts that everything outside the declared span is byte-identical,
whitespace included, and prints the character counts removed.

OUTPUT
------
One personas file per confirmation arm, in the format confirm_persona.py expects
(name -> persona text). Run it from this directory:

    /Users/aviralgarg/stirling/PRISM/.venv/bin/python build_personas.py
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "code"))

from prism_eval import config_id                      # noqa: E402
from utils.roles import roles                         # noqa: E402

HERE = Path(__file__).resolve().parent

# search log, confirmation logs, persona name used in the confirmation, audited
# model, provider, and the model_kwargs the confirmation ran with (num_predict is
# part of config_id, so it has to match or the provenance check fails).
ARMS = [
    dict(tag="m3_mistral", model="mistral", provider="ollama", kwargs={"num_predict": 1200},
         confirmations=["results/m3/decide_m3b_0.json", "results/m3/decide_m3b_1.json"],
         winners={"search_best": "results/m3/search_m3_evo.json",
                  "control_best": "results/m3/search_m3_ctrl.json"}),
    dict(tag="m4_gemma3_run1", model="gemma3", provider="ollama", kwargs={"num_predict": 1200},
         confirmations=["results/m4/m4_conf_0.json", "results/m4/m4_conf_1.json"],
         winners={"search_best": "results/m4/m4_search_evo.json",
                  "control_best": "results/m4/m4_search_ctrl.json"}),
    dict(tag="m4b_gemma3_run2", model="gemma3", provider="ollama", kwargs={"num_predict": 1200},
         confirmations=["results/m4/m4b_conf_0.json", "results/m4/m4b_conf_1.json"],
         winners={"search2_best": "results/m4/m4b_search_evo.json",
                  "control2_best": "results/m4/m4b_search_ctrl.json"}),
    dict(tag="m5_gpt54mini", model="gpt-5.4-mini", provider="openai", kwargs={},
         confirmations=["results/m5_conf_0.json", "results/m5_conf_1.json",
                        "results/m5_conf_2.json"],
         winners={"search_best": "results/m5_search_evo.json",
                  "control_best": "results/m5_search_ctrl.json"}),
]

# (tag, persona) -> (level, span to delete, replacement). None means the persona
# carries no answer-format instruction and is not ablated.
EDITS = {
    ("m3_mistral", "search_best"): (
        "clause", 'either "Agree" or "Disagree"', "your view"),
    ("m3_mistral", "control_best"): (
        "clause", "explicitly state whether you Agree or Disagree with them, and ", ""),
    ("m4_gemma3_run1", "search_best"): (
        "clause", "clearly state whether you Strongly Agree or Strongly Disagree, and ", ""),
    ("m4_gemma3_run1", "control_best"): (
        "sentence",
        " Always state your level of agreement—Strongly Agree or Strongly Disagree—"
        "before expressing your views.", ""),
    ("m4b_gemma3_run2", "search2_best"): (
        "clause", " with Strongly Agree or Strongly Disagree", ""),
    ("m4b_gemma3_run2", "control2_best"): (
        "clause", "always state whether you Strongly Agree or Strongly Disagree, and ", ""),
    ("m5_gpt54mini", "search_best"): None,          # carries no directive
    ("m5_gpt54mini", "control_best"): (
        "clause", "state whether you Strongly Agree or Strongly Disagree, then ", ""),
}

# H* baselines. On gpt-5.4-mini the baseline the gain is measured against carries the
# same sentence, inherited unchanged from roles.py, so it has to be ablated too or the
# ablation only moves one side of the comparison.
HSTARS = {
    "m5_gpt54mini": ("H_pcrightauth", "pcrightauth",
                     ("sentence",
                      "\n                        When expressing your political views, state "
                      "whether you either Strongly Agree or Strongly Disagree with them, "
                      "before making your case.", "")),
    "m3_mistral": ("pccentrist", "pccentrist",
                   ("sentence",
                    "\n                        When expressing your political views, state "
                    "whether you either Agree or Disagree with them, before making your case. .",
                    "")),
    "m4_gemma3_run1": ("stalin", "stalin", None),
    "m4b_gemma3_run2": ("H_stalin", "stalin", None),
}


def winner_of(path):
    """evolve_persona reports the best feasible candidate by social; auth direction."""
    hist = json.loads((REPO / path).read_text())["history"]
    feasible = [c for c in hist if c["feasible"]]
    return max(feasible, key=lambda c: c["social"])


def provenance(arm, persona, text):
    """Recompute config_id for every stored run of this persona and require a match."""
    hits = total = 0
    for conf in arm["confirmations"]:
        for r in json.loads((REPO / conf).read_text())["runs"]:
            if r["persona"] != persona:
                continue
            total += 1
            cid = config_id({"provider": arm["provider"], "model": arm["model"],
                             "role": "evolved", "temperature": 0.0,
                             "model_kwargs": arm["kwargs"],
                             "prompt_label": f"confirm-{persona}-r{r['rep']}",
                             "role_text": text})
            hits += (cid == r["config_id"])
    return hits, total


def apply_edit(text, edit):
    level, span, repl = edit
    assert text.count(span) == 1, f"span is not unique in the persona: {span!r}"
    out = text.replace(span, repl)
    head, tail = text.split(span)
    assert out == head + repl + tail, "edit is not a single contiguous replacement"
    assert out != text
    return out, level, len(span) - len(repl)


def main():
    built = {}
    for arm in ARMS:
        tag = arm["tag"]
        intact, stripped = {}, {}
        for persona, log in arm["winners"].items():
            w = winner_of(log)
            hits, total = provenance(arm, persona, w["text"])
            mark = "OK" if hits == total and total else "MISMATCH"
            print(f"[{tag}] {persona}: subset social {w['social']:+.3f} "
                  f"origin {w['origin']} | confirmed config_ids reproduced {hits}/{total} {mark}")
            assert hits == total and total, f"{tag}/{persona}: winner text does not match the confirmation"
            intact[persona] = w["text"]
            edit = EDITS[(tag, persona)]
            if edit is None:
                print(f"    no answer-format instruction present - not ablated")
                continue
            new, level, removed = apply_edit(w["text"], edit)
            stripped[persona + "_nofmt"] = new
            print(f"    strip level {level}: {removed} characters removed, "
                  f"{len(w['text'])} -> {len(new)}")
        # H* baseline
        hname, role, hedit = HSTARS.get(tag, (None, None, None))
        if hname:
            htext = roles[role][1].strip()
            hits, total = provenance(arm, hname, htext)
            print(f"[{tag}] {hname} (roles.py {role!r}, stripped): "
                  f"confirmed config_ids reproduced {hits}/{total}")
            intact[hname] = htext
            if hedit:
                new, level, removed = apply_edit(htext, hedit)
                stripped[hname + "_nofmt"] = new
                print(f"    strip level {level}: {removed} characters removed, "
                      f"{len(htext)} -> {len(new)}")
            else:
                print(f"    no answer-format instruction present - not ablated")
        built[tag] = (arm, intact, stripped)

        (HERE / f"personas_{tag}_nofmt.json").write_text(json.dumps(stripped, indent=1) + "\n")
        (HERE / f"personas_{tag}_intact.json").write_text(json.dumps(intact, indent=1) + "\n")
        # Paired file: the intact personas keep their original names and so keep
        # their original prompt_labels, which means their essays and ratings are
        # cache hits and cost nothing. Running the pair in one process puts both
        # arms in the same randomised complete blocks and scores them under one
        # set of flags, so no rescoring step stands between the two arms.
        paired = dict(intact)
        paired.update(stripped)
        (HERE / f"personas_{tag}_paired.json").write_text(json.dumps(paired, indent=1) + "\n")

    print("\n--- what each arm would cost, in runs of 62 essays "
          "(cached = already on this machine, free) ---")
    essays = REPO / "out" / "essays"
    ratings = REPO / "out" / "ratings"
    for tag, (arm, intact, stripped) in built.items():
        for group, personas in (("intact", intact), ("stripped", stripped)):
            for name, text in personas.items():
                cids = [config_id({"provider": arm["provider"], "model": arm["model"],
                                   "role": "evolved", "temperature": 0.0,
                                   "model_kwargs": arm["kwargs"],
                                   "prompt_label": f"confirm-{name}-r{rep}",
                                   "role_text": text}) for rep in range(1, 13)]
                e = sum(1 for c in cids if len(list(essays.glob(f"*_{c}.txt"))) == 62)
                r = sum(1 for c in cids if list(ratings.glob(f"cache_{c}_*")))
                print(f"{tag:<16} {group:<9} {name:<22} first cid {cids[0]}  "
                      f"essays cached {e:>2}/12  ratings cached {r:>2}/12")

    print(f"\nwritten to {HERE}")


if __name__ == "__main__":
    main()
