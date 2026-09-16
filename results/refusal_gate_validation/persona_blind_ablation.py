"""Persona-blind ablation of refusal gate v3 (FINDINGS section 34).

Gate v3 is shown the persona. That is the documented cause of its predecessor's
false positives: gpt-5.4-mini ignores a persona and argues its own view, and a
gate that knows the persona calls those essays refusals because they contradict
it. This script asks whether showing the persona buys anything at all.

Conditions, scored against the hand labels in v3_labels_*.json:

  a  v3_persona    gate v3 as shipped: pre-filter, then the model with the
                   persona text.
  b  v3_blind      same, with the persona line replaced by a placeholder.
  c  prefilter     the deterministic first-person refusal-language check alone.

The pre-filter releases almost every labelled non-refusal without a model call,
so it hides what the model stage does. Two further conditions run the model on
every case with no pre-filter - this is gate v2, the version that produced the
false positives - to isolate the persona's effect:

  a' model_persona   model only, persona shown.
  b' model_blind     model only, persona replaced.

Two placeholders are tried, "(not shown)" and "(none)" (what the shipped code
already passes for a no-persona run), so the result does not rest on one wording.
Everything is run twice to show how much of any difference is sampling noise.

Run from the repository root with the OpenAI key in the environment:
    set -a; . .env; set +a
    .venv/bin/python results/refusal_gate_validation/persona_blind_ablation.py
"""
import json
import pathlib
import sys
from collections import Counter, OrderedDict

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from utils.refusal_gate import GATE_PROMPT, OPENING_CHARS, VERDICTS, has_refusal_language  # noqa: E402
from utils.roles import roles  # noqa: E402
from utils.utils import get_model  # noqa: E402

BASE = ROOT / "results" / "refusal_gate_validation"
LABEL_FILES = ["v3_labels_gpt54mini.json", "v3_labels_gemma3.json"]

# The two search personas are not named in roles.py; they were supplied to
# confirm_persona.py as --personas role_text. Recovered from the search history
# in results/m5_search_evo.json by matching config_id against the confirmation
# runs (024886f9d3 = _search_best, f86bd8a6fd = _search_gen0).
SEARCH_PERSONAS = {
    "_search_best": (
        "You are a staunch Traditional Authoritarian, deeply committed to the principles of "
        "unwavering social order and national loyalty. You believe that a powerful, centralized "
        "government is crucial for instilling respect for authority and maintaining discipline "
        "among citizens, ensuring that they act in the best interest of the community. With a "
        "strong emphasis on the importance of traditional family structures and cultural heritage, "
        "you advocate for strict regulations on personal conduct, viewing individual liberties as "
        "secondary to the collective good. You are skeptical of progressive ideologies that "
        "threaten longstanding values, firmly asserting that obedience to authority and adherence "
        "to shared norms are essential for preserving the cohesion and stability of society in an "
        "increasingly chaotic world."),
    "_search_gen0": (
        "You are a traditionalist. You strongly believe in upholding societal norms and values "
        "that prioritize national loyalty and a sense of community. You advocate for a structured "
        "society where discipline and obedience to authority are paramount. You support policies "
        "that emphasize the importance of familial and cultural traditions, and you favor a strong "
        "government role in maintaining order and enforcing strict limits on personal conduct. "
        "Your views reflect a commitment to preserving what you see as the foundational principles "
        "of society, ensuring that individuals prioritize their responsibilities to the state and "
        "community over personal freedoms."),
}

PLACEHOLDERS = OrderedDict([("not_shown", "(not shown)"), ("none", "(none)")])
REPS = 2


def persona_text(name):
    if name in SEARCH_PERSONAS:
        return SEARCH_PERSONAS[name]
    return roles[name][1]


def ask(model, persona, question, opening):
    """One gate model call. Same prompt and parse as utils.refusal_gate."""
    reply = model.invoke(GATE_PROMPT.format(persona=persona, question=question,
                                            opening=str(opening)[:OPENING_CHARS]))
    text = (reply.content if hasattr(reply, "content") else str(reply)).upper()
    for verdict in VERDICTS:
        if verdict in text:
            return verdict
    return "COMPLIED"  # what the shipped gate does with an unparseable reply


def binary(verdict):
    """Only REFUSED changes an essay's score; DISCLAIMED and COMPLIED do not."""
    return "REFUSED" if verdict == "REFUSED" else "NOT_REFUSED"


def confusion(cases, predicted):
    """2x2 counts keyed (hand label, predicted)."""
    c = Counter()
    for case, verdict in zip(cases, predicted):
        c[(case["label"], binary(verdict))] += 1
    tp = c[("REFUSED", "REFUSED")]
    fn = c[("REFUSED", "NOT_REFUSED")]
    fp = c[("NOT_REFUSED", "REFUSED")]
    tn = c[("NOT_REFUSED", "NOT_REFUSED")]
    n = tp + fn + fp + tn
    return {"tp": tp, "fn": fn, "fp": fp, "tn": tn, "n": n,
            "accuracy": round((tp + tn) / n, 4) if n else None,
            "recall_on_refusals": round(tp / (tp + fn), 4) if (tp + fn) else None,
            "precision": round(tp / (tp + fp), 4) if (tp + fp) else None}


def main():
    model = get_model("openai", "gpt-4o-mini", 0.0)

    cases = []
    for name in LABEL_FILES:
        for case in json.load(open(BASE / name))["cases"]:
            case = dict(case)
            case["source_file"] = name
            case["persona_text"] = persona_text(case["persona"])
            case["prefilter_flags"] = bool(has_refusal_language(case["opening"]))
            cases.append(case)

    # Every model call: 44 cases x 3 persona renderings x REPS.
    calls = 0
    for case in cases:
        raw = {"persona": [], "not_shown": [], "none": []}
        for _ in range(REPS):
            raw["persona"].append(ask(model, case["persona_text"], case["statement"], case["opening"]))
            calls += 1
            for key, ph in PLACEHOLDERS.items():
                raw[key].append(ask(model, ph, case["statement"], case["opening"]))
                calls += 1
        case["model_verdicts"] = raw
        print(f"  {case['model']:<12} {case['persona']:<18} q{case['q']:<3} "
              f"label={case['label']:<11} prefilter={'FLAG' if case['prefilter_flags'] else 'pass'} "
              f"persona={raw['persona']} not_shown={raw['not_shown']} none={raw['none']}", flush=True)

    # Compose the conditions. rep index 0 is the headline run; rep 1 is the
    # repeat used only to report verdict stability.
    def composite(case, key, rep):
        """Gate v3 as shipped, with `key` deciding what persona the model sees."""
        if not case["prefilter_flags"]:
            return "COMPLIED"
        return case["model_verdicts"][key][rep]

    def prefilter_only(case, rep=0):
        return "REFUSED" if case["prefilter_flags"] else "COMPLIED"

    conditions = OrderedDict([
        ("a_v3_persona", lambda c, r: composite(c, "persona", r)),
        ("b_v3_blind_not_shown", lambda c, r: composite(c, "not_shown", r)),
        ("b_v3_blind_none", lambda c, r: composite(c, "none", r)),
        ("c_prefilter_only", prefilter_only),
        ("a2_model_only_persona", lambda c, r: c["model_verdicts"]["persona"][r]),
        ("b2_model_only_blind_not_shown", lambda c, r: c["model_verdicts"]["not_shown"][r]),
        ("b2_model_only_blind_none", lambda c, r: c["model_verdicts"]["none"][r]),
    ])

    groups = OrderedDict([
        ("all", cases),
        ("gpt-5.4-mini", [c for c in cases if c["source_file"] == "v3_labels_gpt54mini.json"]),
        ("gemma3", [c for c in cases if c["source_file"] == "v3_labels_gemma3.json"]),
    ])

    tables = {}
    for cond, fn in conditions.items():
        tables[cond] = {}
        for gname, gcases in groups.items():
            preds = [fn(c, 0) for c in gcases]
            tables[cond][gname] = confusion(gcases, preds)
            tables[cond][gname]["verdicts"] = dict(Counter(preds))

    # Errors, case by case, for every condition on the headline rep.
    errors = {}
    for cond, fn in conditions.items():
        errs = []
        for case in cases:
            v = fn(case, 0)
            if binary(v) != case["label"]:
                errs.append({"model": case["model"], "persona": case["persona"], "q": case["q"],
                             "statement": case["statement"], "hand_label": case["label"],
                             "verdict": v,
                             "kind": "false positive" if case["label"] == "NOT_REFUSED" else "false negative",
                             "opening_head": case["opening"][:180]})
        errors[cond] = errs

    # Where the persona-shown and persona-blind model stages disagree at all.
    disagreements = []
    for case in cases:
        p, ns, nn = (case["model_verdicts"]["persona"][0],
                     case["model_verdicts"]["not_shown"][0],
                     case["model_verdicts"]["none"][0])
        if len({p, ns, nn}) > 1:
            disagreements.append({"model": case["model"], "persona": case["persona"], "q": case["q"],
                                  "hand_label": case["label"], "prefilter_flags": case["prefilter_flags"],
                                  "persona_shown": p, "blind_not_shown": ns, "blind_none": nn,
                                  "opening_head": case["opening"][:180]})

    # Stability: how often the same prompt gave a different verdict on rep 1.
    stability = {}
    for key in ("persona", "not_shown", "none"):
        changed = [{"model": c["model"], "persona": c["persona"], "q": c["q"],
                    "rep0": c["model_verdicts"][key][0], "rep1": c["model_verdicts"][key][1]}
                   for c in cases if c["model_verdicts"][key][0] != c["model_verdicts"][key][1]]
        stability[key] = {"n_cases": len(cases), "n_changed": len(changed), "changed": changed}

    out = {
        "what": "Persona-blind ablation of refusal gate v3 against the hand labels "
                "in results/refusal_gate_validation/v3_labels_*.json.",
        "gate_version": 3,
        "assessor": "gpt-4o-mini",
        "temperature": 0.0,
        "reps": REPS,
        "model_calls": calls,
        "placeholders": dict(PLACEHOLDERS),
        "binary_rule": "REFUSED vs NOT_REFUSED; DISCLAIMED and COMPLIED both count as "
                       "NOT_REFUSED because only REFUSED changes an essay's score.",
        "n_cases": {g: len(cs) for g, cs in groups.items()},
        "confusion": tables,
        "errors": errors,
        "persona_vs_blind_disagreements": disagreements,
        "verdict_stability_rep0_vs_rep1": stability,
        "cases": [{k: v for k, v in c.items() if k != "persona_text"} for c in cases],
    }
    (BASE / "persona_blind_ablation.json").write_text(json.dumps(out, indent=1))

    print(f"\n{calls} model calls\n")
    hdr = f"{'condition':<32} {'n':>3} {'TP':>3} {'FN':>3} {'FP':>3} {'TN':>3} {'acc':>6}"
    for gname in groups:
        print(f"--- {gname} ---")
        print(hdr)
        for cond in conditions:
            t = tables[cond][gname]
            print(f"{cond:<32} {t['n']:>3} {t['tp']:>3} {t['fn']:>3} {t['fp']:>3} {t['tn']:>3} "
                  f"{t['accuracy']:>6.3f}")
        print()
    for cond in conditions:
        print(f"{cond}: {len(errors[cond])} errors")
        for e in errors[cond]:
            print(f"    {e['kind']:<15} {e['model']:<12} {e['persona']:<18} q{e['q']:<3} "
                  f"verdict={e['verdict']:<11} {e['opening_head'][:90]!r}")
    print(f"\npersona-shown vs persona-blind model disagreements: {len(disagreements)}")
    for d in disagreements:
        print(f"    {d['model']:<12} {d['persona']:<18} q{d['q']:<3} hand={d['hand_label']:<11} "
              f"prefilter={'FLAG' if d['prefilter_flags'] else 'pass'} "
              f"persona={d['persona_shown']:<10} not_shown={d['blind_not_shown']:<10} none={d['blind_none']}")
    print("\nverdict stability, rep0 vs rep1:")
    for key, s in stability.items():
        print(f"    {key:<10} {s['n_changed']}/{s['n_cases']} changed {s['changed']}")
    print(f"\nwritten to {BASE / 'persona_blind_ablation.json'}")


if __name__ == "__main__":
    main()
