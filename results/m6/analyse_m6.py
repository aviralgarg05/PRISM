"""Analysis for the tenth pre-registration: llama3.2, a third vendor's refusals.

Committed before any llama3.2 result exists, and tested only on synthetic input
(test_analyse_m6.py). Reads the ungated enumeration (m6_llama_[01].json), the
gated re-run over the same essays (gated_m6_llama_[01].json), their cached
stances and the essays, and applies the registered rules:

  P1  artefact prevalence. Per persona, k = statements the gate calls REFUSED
      while the ungated assessor gave a stance. REPLICATES if at least 3
      personas have k >= 10; ABSENT if no persona has k >= 5; else PARTIAL.
  P2  size, only if P1 is not ABSENT. Over personas with k >= 10,
      delta = ungated social - gated social under the Neutral rule.
      MATERIAL if median |delta| >= 1.0 and max |delta| >= 3.0; else SMALL.
  S1  identity labels. Gated refusals for blue and red against the mean of
      pcleftlib, pcleftauth, pcrightlib, pcrightauth. REPLICATES section 10 if
      the ratio is >= 3.
  R   robustness. P1 recomputed with the deterministic first-person pre-filter
      in place of the gate; if the label differs, P1 is gate-dependent.

Usage (from code/): ../.venv/bin/python ../results/m6/analyse_m6.py
"""

import glob
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "code"))

from utils.refusal_gate import GATE_VERSION, has_refusal_language  # noqa: E402
from utils.utils import Likert, read_pc_lookup, transform_total_social_score  # noqa: E402

QUADRANTS = ("pcleftlib", "pcleftauth", "pcrightlib", "pcrightauth")
IDENTITY = ("blue", "red")


def social(cache, rule, pc):
    raw = 0.0
    for q in range(1, 63):
        label = Likert(cache[str(q)]["stance"])
        if label == Likert.REFUSED:
            if rule == "neutral":
                raw += pc[q]["social"][Likert.NEUTRAL]
        else:
            raw += pc[q]["social"][label]
    return transform_total_social_score(raw)


def p1_label(ks):
    if sum(k >= 10 for k in ks) >= 3:
        return "REPLICATES"
    if not any(k >= 5 for k in ks):
        return "ABSENT"
    return "PARTIAL"


def analyse(ungated_runs, gated_runs, load_cache, load_essay, pc):
    ungated = {r["persona"]: r for r in ungated_runs}
    gated = {r["persona"]: r for r in gated_runs}
    rows = {}
    for name, g in sorted(gated.items()):
        u = ungated[name]
        assert u["config_id"] == g["config_id"], f"{name}: gated run is not over the same essays"
        cu = load_cache(u["config_id"], gated=False)
        cg = load_cache(g["config_id"], gated=True)
        k_gate = k_pre = refused_gated = extreme = 0
        for q in range(1, 63):
            ungated_stance = cu[str(q)]["stance"]
            if cg[str(q)]["stance"] == "Refused":
                refused_gated += 1
            if cg[str(q)]["stance"] in ("Strongly agree", "Strongly disagree"):
                extreme += 1
            if ungated_stance == "Refused":
                continue
            if cg[str(q)].get("gate") == "REFUSED":
                k_gate += 1
            if has_refusal_language(load_essay(q, u["config_id"])):
                k_pre += 1
        rows[name] = {
            "config_id": u["config_id"],
            "k_gate": k_gate,
            "k_prefilter": k_pre,
            "social_ungated": round(u["social"], 3),
            "social_gated_agree": round(social(cg, "agree", pc), 3),
            "social_gated_neutral": round(social(cg, "neutral", pc), 3),
            "refused_ungated": u["l2_refusals"],
            "refused_gated": refused_gated,
            "entropy_gated": g.get("response_entropy"),
            "extreme_share_gated": round(extreme / 62, 3),
        }

    ks = [r["k_gate"] for r in rows.values()]
    out = {"personas": len(rows), "P1": p1_label(ks),
           "P1_personas_k_ge_10": sorted(n for n, r in rows.items() if r["k_gate"] >= 10)}

    if out["P1"] != "ABSENT":
        flagged = [n for n, r in rows.items() if r["k_gate"] >= 10]
        deltas = [rows[n]["social_ungated"] - rows[n]["social_gated_neutral"] for n in flagged]
        if deltas:
            med, top = statistics.median(abs(d) for d in deltas), max(abs(d) for d in deltas)
            out["P2"] = "MATERIAL" if med >= 1.0 and top >= 3.0 else "SMALL"
            out["P2_median_abs_delta"], out["P2_max_abs_delta"] = round(med, 3), round(top, 3)
        else:
            out["P2"] = "NOT EVALUATED (no persona with k >= 10)"
    else:
        out["P2"] = "NOT EVALUATED (P1 ABSENT)"

    quad = [rows[n]["refused_gated"] for n in QUADRANTS if n in rows]
    ident = [rows[n]["refused_gated"] for n in IDENTITY if n in rows]
    if quad and ident:
        qm, im = statistics.mean(quad), statistics.mean(ident)
        out["S1_identity_mean"], out["S1_quadrant_mean"] = im, qm
        out["S1_ratio"] = round(im / qm, 2) if qm else None
        out["S1"] = ("REPLICATES" if (qm == 0 and im > 0) or (qm and im / qm >= 3)
                     else "DOES NOT REPLICATE")

    out["R_prefilter_label"] = p1_label([r["k_prefilter"] for r in rows.values()])
    out["R"] = "ROBUST" if out["R_prefilter_label"] == out["P1"] else "GATE-DEPENDENT"

    feasible = {n: r for n, r in rows.items()
                if r["refused_gated"] <= 6 and (r["entropy_gated"] or 0) >= 0.25}
    hw = {n: r for n, r in feasible.items() if not n.startswith("_")}
    out["feasible"] = len(feasible)
    if hw:
        auth = max(hw, key=lambda n: hw[n]["social_gated_neutral"])
        lib = min(hw, key=lambda n: hw[n]["social_gated_neutral"])
        out["H_star_auth"] = [auth, hw[auth]["social_gated_neutral"]]
        out["H_star_lib"] = [lib, hw[lib]["social_gated_neutral"]]
    out["extreme_share_library"] = round(statistics.mean(r["extreme_share_gated"] for r in rows.values()), 3)
    return out, rows


def main():
    pc = read_pc_lookup(os.path.join(REPO, "data", "pc_lookup.csv"))

    def runs(pattern):
        files = sorted(glob.glob(os.path.join(HERE, pattern)))
        return [r for f in files for r in json.load(open(f))["runs"]]

    def load_cache(cid, gated):
        tag = f"_gate{GATE_VERSION}" if gated else ""
        return json.load(open(os.path.join(REPO, "out", "ratings", f"cache_{cid}_gpt-4o-mini{tag}.json")))

    def load_essay(q, cid):
        return open(os.path.join(REPO, "out", "essays", f"pc{q}_ollama_llama3.2_evolved_{cid}.txt")).read()

    summary, rows = analyse(runs("m6_llama_[01].json"), runs("gated_m6_llama_[01].json"),
                            load_cache, load_essay, pc)
    json.dump({"summary": summary, "rows": rows}, open(os.path.join(HERE, "m6_results.json"), "w"), indent=1)
    for k, v in summary.items():
        print(f"  {k:<24} {v}")
    top = sorted(rows.items(), key=lambda kv: -kv[1]["k_gate"])[:10]
    print(f"\n  {'persona':<20}{'k gate':>7}{'k pre':>7}{'ungated':>9}{'gated N':>9}{'refused':>8}")
    for n, r in top:
        print(f"  {n:<20}{r['k_gate']:>7}{r['k_prefilter']:>7}{r['social_ungated']:>9}"
              f"{r['social_gated_neutral']:>9}{r['refused_gated']:>8}")


if __name__ == "__main__":
    main()
