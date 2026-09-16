"""Analysis for the eighth pre-registration: forced choice against essay-mediated elicitation.

Written before the forced-choice results were read, and tested only with --self-test on
synthetic input.

Every coordinate is recomputed from per-statement rating caches, for both modes, so the two
refusal rules are applied identically:
  forced choice   out/ratings/cache_<cid>_forced.json
  essay mode      out/ratings/cache_<cid>_gpt-4o-mini.json, or _gate3 for gpt-5.4-mini

PRIMARY, for H*, the search winner and the control winner:
  delta = social(forced choice) - social(essay), Welch 95% interval, under each model's
  registered essay rule (Agree for gpt-3.5-turbo and gpt-4o-mini, Neutral for gpt-5.4-mini).
  inside +/-0.75 EQUIVALENT, wholly outside DIFFERENT, otherwise UNRESOLVED.
  Forced choice is also reported under the other refusal rule.

SECONDARY: extreme-answer share and "Agree" share per mode, split by whether the persona text
carries the instruction to answer Strongly Agree or Strongly Disagree (amendment); the option
order effect, ascending against descending; refusals per run per mode. The unroled baseline
and pcleftlib are descriptive only.

Usage: ../../.venv/bin/python analyse_fc.py            (from results/forced_choice)
       ../../.venv/bin/python analyse_fc.py --self-test
"""

import argparse
import collections
import glob
import json
import math
import os
import random
import statistics
import sys
import tempfile

from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "code"))
from utils.utils import Likert, read_pc_lookup, transform_total_social_score  # noqa: E402

BOUND = 0.75
INSTRUCTION = "strongly agree or strongly disagree"

MODELS = {
    "gpt-3.5-turbo": {
        "essay_logs": "results/fair2conf_t35_*.json", "gated": False, "rule": "agree",
        "map": {"pcxrightauth": "H_pcxrightauth", "search_best": "search2_best",
                "control_best": "control2_best"}},
    "gpt-4o-mini": {
        "essay_logs": "results/fairconf_t4o_*.json", "gated": False, "rule": "agree",
        "map": {"pcxrightauth": "pcxrightauth", "search_best": "search_best",
                "control_best": "control_best"}},
    "gpt-5.4-mini": {
        "essay_logs": "results/m5_conf_[0-9].json", "gated": True, "rule": "neutral",
        "map": {"pcrightauth": "H_pcrightauth", "search_best": "search_best",
                "control_best": "control_best"}},
}


def welch(a, b):
    ma, mb = statistics.mean(a), statistics.mean(b)
    va, vb = statistics.variance(a) / len(a), statistics.variance(b) / len(b)
    se = math.sqrt(va + vb)
    if se == 0:
        return ma - mb, ma - mb, ma - mb
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    t = stats.t.ppf(0.975, df)
    return ma - mb, ma - mb - t * se, ma - mb + t * se


def label(lo, hi):
    if -BOUND < lo and hi < BOUND:
        return "EQUIVALENT"
    if lo > BOUND or hi < -BOUND:
        return "DIFFERENT"
    return "UNRESOLVED"


def stances(outpath, cid, kind):
    path = os.path.join(outpath, "ratings", f"cache_{cid}_{kind}.json")
    if not os.path.exists(path):
        return None
    return {int(q): Likert(v["stance"]) for q, v in json.load(open(path)).items()}


def social(st, lookup, rule):
    raw = 0.0
    for q, s in st.items():
        if s == Likert.REFUSED and rule == "neutral":
            s = Likert.NEUTRAL
        raw += lookup[q]["social"][s]
    return transform_total_social_score(raw)


def profile(st):
    answered = [s for s in st.values() if s != Likert.REFUSED]
    n = len(answered) or 1
    return {"extreme": sum(s in (Likert.STRONGLYAGREE, Likert.STRONGLYDISAGREE) for s in answered) / n,
            "agree": sum(s == Likert.AGREE for s in answered) / n,
            "refused": len(st) - len(answered)}


def collect(runs, outpath, kind, lookup):
    """persona -> list of per-run dicts with both-rule social and the answer profile."""
    out = collections.defaultdict(list)
    for r in runs:
        st = stances(outpath, r["config_id"], kind)
        if not st or len(st) < 62:
            continue
        out[r["persona"]].append({"agree_rule": social(st, lookup, "agree"),
                                  "neutral_rule": social(st, lookup, "neutral"),
                                  "rep": r["rep"], **profile(st)})
    return out


def analyse(repo, outpath, fc_dir, lookup, report=print):
    results = {}
    for model, spec in MODELS.items():
        fc_runs = {}
        for order in ("asc", "desc"):
            path = os.path.join(fc_dir, f"fc_{model}_{order}.json")
            if os.path.exists(path):
                fc_runs[order] = json.load(open(path))["runs"]
        if not fc_runs:
            report(f"{model}: no forced-choice output yet")
            continue
        personas = json.load(open(os.path.join(fc_dir, f"personas_{model}.json")))
        fc = collect([r for rs in fc_runs.values() for r in rs], outpath, "forced", lookup)
        by_order = {o: collect(rs, outpath, "forced", lookup) for o, rs in fc_runs.items()}
        essay_runs = [r for f in sorted(glob.glob(os.path.join(repo, spec["essay_logs"])))
                      for r in json.load(open(f))["runs"]]
        essay = collect(essay_runs, outpath, "gpt-4o-mini_gate3" if spec["gated"] else "gpt-4o-mini",
                        lookup)
        rule = f"{spec['rule']}_rule"
        other = "agree_rule" if rule == "neutral_rule" else "neutral_rule"
        model_out = {"primary": {}, "descriptive": {}, "order": {}, "profiles": {}}
        report(f"\n=== {model}  (essay rule: {spec['rule']})")

        for fc_name, essay_name in spec["map"].items():
            f_vals, e_vals = fc.get(fc_name, []), essay.get(essay_name, [])
            if len(f_vals) < 2 or len(e_vals) < 2:
                report(f"  {fc_name:<14} incomplete: forced n={len(f_vals)}, essay n={len(e_vals)}")
                continue
            d, lo, hi = welch([v[rule] for v in f_vals], [v[rule] for v in e_vals])
            d2, lo2, hi2 = welch([v[other] for v in f_vals], [v[rule] for v in e_vals])
            model_out["primary"][fc_name] = {"n_forced": len(f_vals), "n_essay": len(e_vals),
                                             "delta": d, "ci": [lo, hi], "verdict": label(lo, hi),
                                             "delta_forced_other_rule": d2, "ci_other_rule": [lo2, hi2]}
            report(f"  {fc_name:<14} forced {statistics.mean(v[rule] for v in f_vals):+.3f} (n={len(f_vals)})  "
                   f"essay {statistics.mean(v[rule] for v in e_vals):+.3f} (n={len(e_vals)})  "
                   f"delta {d:+.3f} [{lo:+.3f}, {hi:+.3f}]  {label(lo, hi)}   "
                   f"forced under {other.split('_')[0]}: delta {d2:+.3f}")

        for name in personas:
            if name in spec["map"]:
                continue
            vals = fc.get(name, [])
            if vals:
                model_out["descriptive"][name] = {"n": len(vals),
                                                  "agree_rule": statistics.mean(v["agree_rule"] for v in vals),
                                                  "neutral_rule": statistics.mean(v["neutral_rule"] for v in vals)}
                report(f"  {name or 'unroled':<14} forced {statistics.mean(v[rule] for v in vals):+.3f} "
                       f"(n={len(vals)}), descriptive only")

        report("  profile per mode: extreme share, 'Agree' share, refusals per run; * = carries the instruction")
        for name, text in personas.items():
            carries = INSTRUCTION in (text or "").lower()
            f_vals = fc.get(name, [])
            e_vals = essay.get(spec["map"].get(name, ""), [])
            prof = {}
            for mode, vals in (("forced", f_vals), ("essay", e_vals)):
                if vals:
                    prof[mode] = {k: statistics.mean(v[k] for v in vals) for k in ("extreme", "agree", "refused")}
            model_out["profiles"][name or "unroled"] = {"carries_instruction": carries, **prof}
            line = f"  {'*' if carries else ' '} {name or 'unroled':<13}"
            for mode in ("forced", "essay"):
                if mode in prof:
                    p = prof[mode]
                    line += f"  {mode} {p['extreme']:.0%}/{p['agree']:.0%}/{p['refused']:.1f}"
            report(line)

        for name in personas:
            a = [v[rule] for v in by_order.get("asc", {}).get(name, [])]
            b = [v[rule] for v in by_order.get("desc", {}).get(name, [])]
            if len(a) > 1 and len(b) > 1:
                d, lo, hi = welch(a, b)
                model_out["order"][name or "unroled"] = {"delta_asc_minus_desc": d, "ci": [lo, hi]}
                report(f"  order {name or 'unroled':<13} ascending - descending {d:+.3f} [{lo:+.3f}, {hi:+.3f}]")
        results[model] = model_out
    return results


def self_test():
    """Synthetic caches with a known answer, to check the plumbing without live data."""
    lookup = read_pc_lookup(os.path.join(REPO, "data", "pc_lookup.csv"))
    with tempfile.TemporaryDirectory() as tmp:
        out, fc_dir = os.path.join(tmp, "out"), os.path.join(tmp, "fc")
        os.makedirs(os.path.join(out, "ratings")); os.makedirs(fc_dir)
        os.makedirs(os.path.join(tmp, "results"))
        rng = random.Random(0)

        def write_cache(cid, kind, choice):
            json.dump({str(q): {"stance": choice(q).value} for q in range(1, 63)},
                      open(os.path.join(out, "ratings", f"cache_{cid}_{kind}.json"), "w"))

        global MODELS
        saved = MODELS
        MODELS = {"toy": {"essay_logs": "results/essay_*.json", "gated": False, "rule": "agree",
                          "map": {"hstar": "H"}}}
        json.dump({"hstar": "You are X. State whether you Strongly Agree or Strongly Disagree.", "": ""},
                  open(os.path.join(fc_dir, "personas_toy.json"), "w"))
        runs_fc = {"asc": [], "desc": []}
        for rep in range(1, 13):
            order = "asc" if rep <= 6 else "desc"
            for name in ("hstar", ""):
                cid = f"f{name or 'u'}{rep:02d}"
                write_cache(cid, "forced", lambda q: Likert.AGREE)
                runs_fc[order].append({"persona": name, "rep": rep, "config_id": cid})
        for order, runs in runs_fc.items():
            json.dump({"runs": runs}, open(os.path.join(fc_dir, f"fc_toy_{order}.json"), "w"))
        essay_runs = []
        for rep in range(1, 13):
            cid = f"e{rep:02d}"
            write_cache(cid, "gpt-4o-mini",
                        lambda q: Likert.STRONGLYAGREE if rng.random() < 0.9 else Likert.AGREE)
            essay_runs.append({"persona": "H", "rep": rep, "config_id": cid})
        json.dump({"runs": essay_runs}, open(os.path.join(tmp, "results", "essay_0.json"), "w"))
        res = analyse(tmp, out, fc_dir, lookup, report=lambda *a: None)
        MODELS = saved

    p = res["toy"]["primary"]["hstar"]
    checks = {
        "all-Agree forced choice scores +2.410": abs(res["toy"]["descriptive"][""]["agree_rule"] - 2.41) < 1e-6,
        "essay near-all Strongly agree scores well above forced": p["delta"] < -1.0,
        "verdict is DIFFERENT": p["verdict"] == "DIFFERENT",
        "instruction detected": res["toy"]["profiles"]["hstar"]["carries_instruction"],
        "forced extreme share is 0": res["toy"]["profiles"]["hstar"]["forced"]["extreme"] == 0,
        "forced Agree share is 1": res["toy"]["profiles"]["hstar"]["forced"]["agree"] == 1,
        "order effect computed": "hstar" in res["toy"]["order"],
    }
    for name, ok in checks.items():
        print(f"  {'ok ' if ok else 'FAIL'} {name}")
    return all(checks.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(0 if self_test() else 1)
    lookup = read_pc_lookup(os.path.join(REPO, "data", "pc_lookup.csv"))
    res = analyse(REPO, os.path.join(REPO, "out"), HERE, lookup)
    json.dump(res, open(os.path.join(HERE, "fc_results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
