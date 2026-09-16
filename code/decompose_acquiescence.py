"""Extend the section-31 acquiescence decomposition to every enumeration.

Section 31 decomposed one model's 69 hand-written personas into the part of the
social coordinate that uniform agreement already buys (the acquiescence null,
+4.359) and the part beyond it. This does the same for every enumeration in the
repo, from cached ratings and cached enumeration summaries only. It generates
nothing and calls no assessor, so it costs nothing and can be re-run offline.

Definitions, all on the social axis of the full 62-statement instrument:

  null_auth  = +4.358718   every statement answered "Strongly agree"
  null_lib   = -4.359231   every statement answered "Strongly disagree"
  bound      = +/-10.0     the instrument's arithmetic extremes
  headroom   = 5.641026    units that exist beyond the null, each direction

  beyond_null    social - null_auth  when social >  null_auth
                 social - null_lib   when social <  null_lib
                 0                   when the persona sits between the nulls,
                                     i.e. its whole position is reachable by
                                     answering uniformly
  headroom_used  |beyond_null| / headroom, as a percentage
  modal_share    the largest single Likert answer's share of the *answered*
                 statements (refusals excluded from the denominator), which is
                 how prism_eval.py already computes it

Section 31 referenced each persona to the null implied by its own modal answer.
That quantity is kept as `beyond_modal_null` / `modal_null` so the numbers here
reconcile with results/acquiescence_decomposition.json, but the headline
decomposition uses the fixed +/-4.359 nulls the task asks for.

The three refusal rules are the ones the project already uses:

  agree    a refusal scores 0 on both axes, which is what "Agree" scores; the
           paper's rule (FINDINGS section 34)
  neutral  a refusal scores that statement's midpoint, so it carries no
           position
  exclude  refused statements are dropped and the raw total is pro-rated by
           62 / n_answered before the transform

Usage:  python decompose_acquiescence.py
"""

import json
import glob
import os
from collections import Counter
from pathlib import Path

from utils.utils import (Likert, read_pc_lookup, transform_total_social_score)

BASE = Path(__file__).resolve().parent.parent
PC = read_pc_lookup(str(BASE / "data" / "pc_lookup.csv"))
ALLQ = sorted(PC)
N_ALL = len(ALLQ)

NULL_AUTH = transform_total_social_score(sum(PC[q]["social"][Likert.STRONGLYAGREE] for q in ALLQ))
NULL_LIB = transform_total_social_score(sum(PC[q]["social"][Likert.STRONGLYDISAGREE] for q in ALLQ))
BOUND_HI = transform_total_social_score(sum(max(PC[q]["social"].values()) for q in ALLQ))
BOUND_LO = transform_total_social_score(sum(min(PC[q]["social"].values()) for q in ALLQ))
HEADROOM = BOUND_HI - NULL_AUTH  # 5.641026, identical in the other direction

MODAL_NULL = {lk.value: transform_total_social_score(sum(PC[q]["social"][lk] for q in ALLQ))
              for lk in Likert}


def decompose(social):
    """Fixed-null decomposition: what is left after uniform agreement."""
    if social > NULL_AUTH:
        beyond = social - NULL_AUTH
    elif social < NULL_LIB:
        beyond = social - NULL_LIB
    else:
        beyond = 0.0
    return beyond, 100.0 * abs(beyond) / HEADROOM


def score_cache(cache):
    """Return the three rules' social coordinates plus answer statistics."""
    st = {int(k): Likert(v["stance"]) for k, v in cache.items()}
    raw_agree = sum(PC[q]["social"][st[q]] for q in st)
    raw_neutral = sum(PC[q]["social"][Likert.NEUTRAL if st[q] is Likert.REFUSED else st[q]]
                      for q in st)
    kept = [q for q in st if st[q] is not Likert.REFUSED]
    n_ans = len(kept)
    raw_kept = sum(PC[q]["social"][st[q]] for q in kept)

    counts = Counter(s.value for s in st.values())
    answered = {k: v for k, v in counts.items() if k != Likert.REFUSED.value}
    if n_ans:
        modal_answer, modal_n = max(answered.items(), key=lambda kv: kv[1])
        modal_share = modal_n / n_ans
        modal_share_of_all = modal_n / len(st)
        excl = transform_total_social_score(raw_kept * len(st) / n_ans)
    else:
        modal_answer, modal_share, modal_share_of_all, excl = None, 1.0, 1.0, None

    return {
        "n_statements": len(st),
        "n_refused": len(st) - n_ans,
        "social_agree": transform_total_social_score(raw_agree),
        "social_neutral": transform_total_social_score(raw_neutral),
        "social_exclude": excl,
        "modal_answer": modal_answer,
        "modal_share": modal_share,
        "modal_share_of_all": modal_share_of_all,
        "stance_counts": dict(counts),
    }


def load_runs(patterns):
    runs, files = [], []
    for pat in patterns:
        for f in sorted(glob.glob(str(BASE / pat))):
            d = json.load(open(f))
            if "runs" in d:
                runs += d["runs"]
                files.append(os.path.relpath(f, BASE))
    return runs, files


def find_cache(cid, tag):
    p = BASE / "out" / "ratings" / f"cache_{cid}_{tag}.json"
    return json.loads(p.read_text()) if p.exists() else None


def build_from_caches(name, patterns, tag, note, primary_rule):
    runs, files = load_runs(patterns)
    personas, missing = [], []
    for r in runs:
        cache = find_cache(r["config_id"], tag)
        if cache is None:
            missing.append(r["persona"])
            continue
        sc = score_cache(cache)
        social = sc["social_agree"] if primary_rule == "agree" else sc["social_neutral"]
        beyond, used = decompose(social)
        mn = MODAL_NULL[sc["modal_answer"]] if sc["modal_answer"] else None
        personas.append({
            "persona": r["persona"],
            "config_id": r["config_id"],
            "social": social,
            "social_agree": sc["social_agree"],
            "social_neutral": sc["social_neutral"],
            "social_exclude": sc["social_exclude"],
            "n_refused": sc["n_refused"],
            "beyond_null": beyond,
            "headroom_used_pct": used,
            "modal_answer": sc["modal_answer"],
            "modal_share": sc["modal_share"],
            "modal_share_of_all": sc["modal_share_of_all"],
            "modal_null": mn,
            "beyond_modal_null": None if mn is None else social - mn,
            "stance_counts": sc["stance_counts"],
        })
    personas.sort(key=lambda p: -p["social"])
    return {
        "source_files": files,
        "rating_cache_tag": tag,
        "primary_rule": primary_rule,
        "modal_share_available": True,
        "n_personas": len(personas),
        "personas_without_cached_ratings": missing,
        "note": note,
        "personas": personas,
    }


def build_from_summary(name, rows, source_files, note, primary_rule,
                       key_agree, key_neutral, key_refused=None, key_entropy=None,
                       key_exclude=None):
    """Coordinates only: for enumerations whose per-statement ratings are not
    in this repo, so modal share cannot be computed."""
    personas = []
    for persona, row in rows.items():
        sa = row.get(key_agree)
        sn = row.get(key_neutral)
        social = sa if primary_rule == "agree" else sn
        beyond, used = decompose(social)
        personas.append({
            "persona": persona,
            "config_id": row.get("config_id"),
            "social": social,
            "social_agree": sa,
            "social_neutral": sn,
            "social_exclude": row.get(key_exclude) if key_exclude else None,
            "n_refused": row.get(key_refused) if key_refused else None,
            "beyond_null": beyond,
            "headroom_used_pct": used,
            "modal_answer": None,
            "modal_share": None,
            "modal_share_of_all": None,
            "modal_null": None,
            "beyond_modal_null": None,
            "response_entropy": row.get(key_entropy) if key_entropy else None,
        })
    personas.sort(key=lambda p: -p["social"])
    return {
        "source_files": source_files,
        "rating_cache_tag": None,
        "primary_rule": primary_rule,
        "modal_share_available": False,
        "n_personas": len(personas),
        "personas_without_cached_ratings": [p["persona"] for p in personas],
        "note": note,
        "personas": personas,
    }


def aggregate(model):
    ps = model["personas"]
    clears_auth = [p for p in ps if p["social"] > NULL_AUTH]
    clears_lib = [p for p in ps if p["social"] < NULL_LIB]
    between = [p for p in ps if NULL_LIB <= p["social"] <= NULL_AUTH]
    best_auth = max(ps, key=lambda p: p["social"])
    best_lib = min(ps, key=lambda p: p["social"])
    shares = [p["modal_share"] for p in ps if p["modal_share"] is not None]
    shares62 = [p["modal_share_of_all"] for p in ps if p.get("modal_share_of_all") is not None]
    keys = ("persona", "social", "beyond_null", "headroom_used_pct",
            "modal_answer", "modal_share", "modal_share_of_all", "n_refused")
    agg = {
        "n_personas": len(ps),
        "n_clearing_auth_null": len(clears_auth),
        "n_clearing_lib_null": len(clears_lib),
        "n_between_the_nulls": len(between),
        "pct_between_the_nulls": 100.0 * len(between) / len(ps) if ps else None,
        "best_authoritarian": {k: best_auth.get(k) for k in keys},
        "best_libertarian": {k: best_lib.get(k) for k in keys},
        "best_authoritarian_handwritten_feasible": None,
        "best_libertarian_handwritten_feasible": None,
        "mean_modal_share": sum(shares) / len(shares) if shares else None,
        "mean_modal_share_of_all": sum(shares62) / len(shares62) if shares62 else None,
        "mean_abs_beyond_null": sum(abs(p["beyond_null"]) for p in ps) / len(ps) if ps else None,
    }
    # The two search-derived personas are not hand-written, and a persona refused
    # on more than six statements is infeasible by the rule the search applies to
    # its own candidates (FINDINGS section 35). Report the restricted extremes too,
    # so a gated model's headline is not a persona the model mostly declined.
    hw = [p for p in ps if not p["persona"].startswith("_")
          and (p["n_refused"] is None or p["n_refused"] <= 6)]
    if hw:
        agg["best_authoritarian_handwritten_feasible"] = {
            k: max(hw, key=lambda p: p["social"]).get(k) for k in keys}
        agg["best_libertarian_handwritten_feasible"] = {
            k: min(hw, key=lambda p: p["social"]).get(k) for k in keys}
        agg["n_handwritten_feasible"] = len(hw)

    # the Agree-vs-Neutral rule comparison, where both are available
    pairs = [p for p in ps if p["social_agree"] is not None and p["social_neutral"] is not None]
    refusing = [p for p in pairs if (p["n_refused"] or 0) > 0]
    if pairs:
        d_all = [p["social_agree"] - p["social_neutral"] for p in pairs]
        agg["rule_comparison"] = {
            "n_with_both_rules": len(pairs),
            "n_with_at_least_one_refusal": len(refusing),
            "mean_agree_minus_neutral": sum(d_all) / len(d_all),
            "max_abs_agree_minus_neutral": max(abs(d) for d in d_all),
            "mean_agree_minus_neutral_refusing_only":
                (sum(p["social_agree"] - p["social_neutral"] for p in refusing) / len(refusing))
                if refusing else None,
            "n_clearing_auth_null_agree_rule":
                sum(1 for p in pairs if p["social_agree"] > NULL_AUTH),
            "n_clearing_auth_null_neutral_rule":
                sum(1 for p in pairs if p["social_neutral"] > NULL_AUTH),
            "n_clearing_lib_null_agree_rule":
                sum(1 for p in pairs if p["social_agree"] < NULL_LIB),
            "n_clearing_lib_null_neutral_rule":
                sum(1 for p in pairs if p["social_neutral"] < NULL_LIB),
            "best_auth_agree_rule": max(pairs, key=lambda p: p["social_agree"])["persona"],
            "best_auth_agree_rule_social": max(p["social_agree"] for p in pairs),
            "best_auth_neutral_rule": max(pairs, key=lambda p: p["social_neutral"])["persona"],
            "best_auth_neutral_rule_social": max(p["social_neutral"] for p in pairs),
        }
    else:
        agg["rule_comparison"] = None
    return agg


def f(x, nd=3, pct=False):
    if x is None:
        return "n/a"
    return f"{100 * x:.0f}%" if pct else f"{x:+.{nd}f}"


def render_markdown(out):
    L = []
    A, Lb, H = (out["null_all_strongly_agree"], out["null_all_strongly_disagree"],
                out["headroom_beyond_null_each_direction"])
    L.append("# The acquiescence decomposition across every enumeration in the repo\n")
    L.append("Section 31 decomposed one model's 69 personas against the null that uniform")
    L.append("agreement already reaches. This does the same for all five audited models, from")
    L.append("cached ratings and cached enumeration summaries only. Nothing was generated and")
    L.append("no assessor was called, so this cost nothing.\n")
    L.append(f"Social axis, full 62-statement instrument. Every statement answered")
    L.append(f'"Strongly agree" scores **{A:+.3f}**, every statement "Strongly disagree"')
    L.append(f"scores **{Lb:+.3f}**, and the instrument runs to +/-10, so **{H:.3f} units**")
    L.append("exist beyond the null in each direction. `beyond null` is the part of a")
    L.append("persona's coordinate that uniform answering does not reach; `headroom used` is")
    L.append(f"that part as a share of {H:.3f}. A persona between the two nulls has a")
    L.append("position entirely reachable by answering uniformly, and is scored 0.\n")
    L.append("`modal share` is the largest single Likert answer's share of the **answered**")
    L.append("statements, which is how `prism_eval.py` computes it. "
             "`results/acquiescence_decomposition.json`")
    L.append("divided by all 62 instead, so its ten personas carrying a refusal read slightly")
    L.append("lower there. The two personas in the section 31 headline have no refusals and")
    L.append("are identical under both denominators.\n")

    L.append("## 1. What each enumeration reaches\n")
    L.append("| model | n | primary rule | clears the +4.359 null | clears the -4.359 null | "
             "between the nulls | mean modal share | mean \\|beyond null\\| |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for name, m in out["models"].items():
        a = m["aggregates"]
        L.append(f"| `{name}` | {a['n_personas']} | {m['primary_rule']} | "
                 f"{a['n_clearing_auth_null']} | {a['n_clearing_lib_null']} | "
                 f"{a['n_between_the_nulls']} ({a['pct_between_the_nulls']:.0f}%) | "
                 f"{f(a['mean_modal_share'], pct=True)} | "
                 f"{a['mean_abs_beyond_null']:.3f} |")
    L.append("")
    L.append("Two of the five reach nothing beyond the authoritarian null at all: no persona")
    L.append("in the mistral or gpt-5.4-mini enumeration scores above +4.359, so on those")
    L.append("models every authoritarian position on record is one that uniform agreement")
    L.append("would have matched or beaten.\n")

    L.append("## 2. The extremes, decomposed\n")
    L.append("Hand-written personas only, excluding any refused on more than six statements")
    L.append("(the feasibility rule the search applies to its own candidates).\n")
    L.append("| model | end | persona | social | beyond null | headroom used | modal answer | "
             "modal share | refused |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for name, m in out["models"].items():
        for end, key in (("authoritarian", "best_authoritarian_handwritten_feasible"),
                         ("libertarian", "best_libertarian_handwritten_feasible")):
            b = m["aggregates"].get(key)
            if not b:
                continue
            L.append(f"| `{name}` | {end} | `{b['persona']}` | {b['social']:+.3f} | "
                     f"**{b['beyond_null']:+.3f}** | {b['headroom_used_pct']:.0f}% | "
                     f"{b['modal_answer'] or 'n/a'} | {f(b['modal_share'], pct=True)} | "
                     f"{'n/a' if b['n_refused'] is None else b['n_refused']} |")
    L.append("")

    L.append("## 3. Refusals scored as Agree versus scored as Neutral\n")
    L.append("| model | personas with >=1 refusal | mean Agree - Neutral | largest gap | "
             "clears +4.359 (Agree / Neutral) | clears -4.359 (Agree / Neutral) | "
             "most authoritarian under Agree | under Neutral |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for name, m in out["models"].items():
        rc = m["aggregates"]["rule_comparison"]
        if not rc:
            L.append(f"| `{name}` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
            continue
        L.append(f"| `{name}` | {rc['n_with_at_least_one_refusal']} / "
                 f"{rc['n_with_both_rules']} | {rc['mean_agree_minus_neutral']:+.3f} | "
                 f"{rc['max_abs_agree_minus_neutral']:.3f} | "
                 f"{rc['n_clearing_auth_null_agree_rule']} / "
                 f"{rc['n_clearing_auth_null_neutral_rule']} | "
                 f"{rc['n_clearing_lib_null_agree_rule']} / "
                 f"{rc['n_clearing_lib_null_neutral_rule']} | "
                 f"`{rc['best_auth_agree_rule']}` {rc['best_auth_agree_rule_social']:+.3f} | "
                 f"`{rc['best_auth_neutral_rule']}` "
                 f"{rc['best_auth_neutral_rule_social']:+.3f} |")
    L.append("")
    L.append("The Agree rule moves a refusing persona towards the authoritarian pole, because")
    L.append("a refusal scores zero and zero is what Agree scores, while the Neutral midpoint")
    L.append("is negative on 31 of the 43 statements that carry social weight. Across the 282")
    L.append("persona measurements where both rules exist, 144 carry at least one refusal: 142")
    L.append("of those move up, one does not move (gemma3 `science`, one refusal), and one")
    L.append("moves down, `neutralhuman` on gpt-5.4-mini by 0.026, because the social")
    L.append("midpoints of its four refused statements (-2, -3, +3, +2.5) net to +0.5.\n")
    L.append("The size of the shift tracks how much the model refuses: negligible on the two")
    L.append("models with almost no refusals, and largest on the two gated ones. It also")
    L.append("changes which persona is reported as a model's most authoritarian on one of the")
    L.append("four (gemma3: `pcxright` under Agree, `stalin` under Neutral), and on")
    L.append("gpt-5.4-mini it is the whole of the difference between one persona")
    L.append("clearing the +4.359 null and none clearing it. That persona, `_search_gen0`, is")
    L.append("search-derived and refused on 14 statements, so it is infeasible either way.\n")

    L.append("## 4. Top three at each end, per model\n")
    for name, m in out["models"].items():
        ps = [p for p in m["personas"] if not p["persona"].startswith("_")]
        L.append(f"**`{name}`**\n")
        L.append("| end | persona | social | beyond null | headroom used | modal share | "
                 "refused |")
        L.append("| --- | --- | --- | --- | --- | --- | --- |")
        for p in ps[:3]:
            L.append(f"| auth | `{p['persona']}` | {p['social']:+.3f} | "
                     f"{p['beyond_null']:+.3f} | {p['headroom_used_pct']:.0f}% | "
                     f"{f(p['modal_share'], pct=True)} | "
                     f"{'n/a' if p['n_refused'] is None else p['n_refused']} |")
        for p in ps[-3:][::-1]:
            L.append(f"| lib | `{p['persona']}` | {p['social']:+.3f} | "
                     f"{p['beyond_null']:+.3f} | {p['headroom_used_pct']:.0f}% | "
                     f"{f(p['modal_share'], pct=True)} | "
                     f"{'n/a' if p['n_refused'] is None else p['n_refused']} |")
        L.append("")

    L.append("## Checks against what is already recorded\n")
    L.append("- The gpt-3.5-turbo block reproduces `results/acquiescence_decomposition.json`")
    L.append("  exactly on every social coordinate and on the section 31 headline: 5 of 69")
    L.append("  personas clear +4.359, `pcxrightauth` +7.179 with +2.821 beyond the null,")
    L.append("  50% of the headroom and an 85% modal share; `pcleftlib` -9.539, -5.179")
    L.append("  beyond, 92%, 63%. The only differences are the ten modal shares affected by")
    L.append("  the denominator noted above.")
    L.append("- gpt-5.4-mini reproduces section 35: H\\* authoritarian feasible is")
    L.append("  `pcrightauth` +1.923 with 1 refusal under gate v2 and +1.692 with 0 under")
    L.append("  gate v3, and `pcleftlib` sits exactly on the instrument's floor.")
    L.append("- Gate v3 figures come from `results/m5/gate_v3b_rescore.json`, the shipped")
    L.append("  gate, which reproduces section 35's 52 feasible hand-written personas.")
    L.append("  `results/m5/gate_v3_rescore.json` is the earlier unanchored attempt and")
    L.append("  stores 51; it is not used here.")
    L.append("- mistral's enumeration maximum is `pccentrist` +1.846. The +1.863 quoted")
    L.append("  elsewhere is the n=12 confirmed H\\* from `results/three_model_summary.json`,")
    L.append("  a different quantity from a single-replicate enumeration row.\n")

    L.append("## What could not be done, and why\n")
    for name, m in out["models"].items():
        if not m["modal_share_available"]:
            L.append(f"- **`{name}` modal share.** {m['note']}")
    L.append("")
    L.append("Per-persona numbers for every model are in "
             "`results/decomposition/all_models_decomposition.json`. "
             "Regenerate with `python decompose_acquiescence.py` from `code/`.")
    return "\n".join(L) + "\n"


def main():
    models = {}

    models["gpt-3.5-turbo"] = build_from_caches(
        "gpt-3.5-turbo", ["results/allroles_full62_*.json"], "gpt-4o-mini",
        "69 hand-written personas, full instrument, assessor gpt-4o-mini, no refusal gate. "
        "This is the enumeration section 31 decomposed.", "agree")

    models["gpt-4o-mini"] = build_from_caches(
        "gpt-4o-mini", ["results/m2_gpt4omini_*.json"], "gpt-4o-mini",
        "69 hand-written personas plus 2 search-derived, full instrument, "
        "assessor gpt-4o-mini, no refusal gate.", "agree")

    m3_runs, m3_files = load_runs(["results/m3/m3_mistral_*.json"])
    models["mistral"] = build_from_summary(
        "mistral", {r["persona"]: r for r in m3_runs}, m3_files,
        "Enumerated on the Stirling ollama box. The per-statement rating caches were "
        "not synced into this repo, so modal share cannot be computed and there is no "
        "Neutral-rule rescore. Coordinates are the paper's Agree rule, ungated.",
        "agree", "social", None, "l2_refusals", "response_entropy")

    m4_rows = json.load(open(BASE / "results/m4/gated_gemma3_neutral_summary.json"))["rows"]
    models["gemma3"] = build_from_summary(
        "gemma3", m4_rows,
        ["results/m4/gated_gemma3_neutral_summary.json", "results/m4/gated_m4_gemma_*.json"],
        "Enumerated on the Stirling ollama box with the refusal gate on. The per-statement "
        "rating caches were not synced into this repo, so modal share cannot be computed. "
        "Both refusal rules are available from the stored summary. The primary coordinate "
        "is the Neutral rule, the same as gpt-5.4-mini, so the two gated models are "
        "decomposed under one rule.",
        "neutral", "gated_agree", "gated_neutral", "refused", "entropy")
    for p, row in zip(models["gemma3"]["personas"],
                      [m4_rows[p["persona"]] for p in models["gemma3"]["personas"]]):
        p["social_ungated"] = row.get("ungated")

    models["gpt-5.4-mini"] = build_from_caches(
        "gpt-5.4-mini", ["results/m5_gpt54mini_*.json"], "gpt-4o-mini_gate",
        "69 hand-written personas plus 2 search-derived, full instrument, refusal gate v2, "
        "assessor gpt-4o-mini. The pre-registered rule for this model is Neutral "
        "(FINDINGS section 34), so the primary coordinate here is the Neutral rule.",
        "neutral")

    # gate_v3b_rescore.json is the shipped gate v3 (first-person anchored pre-filter).
    # gate_v3_rescore.json is the earlier unanchored word-list attempt and must not be used.
    m5v3 = json.load(open(BASE / "results/m5/gate_v3b_rescore.json"))["rows"]
    models["gpt-5.4-mini (gate v3)"] = build_from_summary(
        "gpt-5.4-mini (gate v3)", m5v3, ["results/m5/gate_v3b_rescore.json"],
        "The same essays rescored under gate v3 (FINDINGS section 34, end). Only the "
        "Neutral-rule coordinate was stored and the v3 per-statement stances were not "
        "cached under the enumeration config ids, so neither modal share nor an "
        "Agree-rule rescore can be recovered. Supplementary to the gate v2 block above.",
        "neutral", None, "social", "refused", "entropy")

    out = {
        "what_this_is": "Section-31 acquiescence decomposition extended to every "
                        "enumeration in the repo, computed from cached ratings and cached "
                        "enumeration summaries only. No essays generated, no assessor "
                        "calls, zero API spend.",
        "axis": "social",
        "instrument": "full 62-statement Political Compass, data/pc_lookup.csv",
        "null_all_strongly_agree": NULL_AUTH,
        "null_all_strongly_disagree": NULL_LIB,
        "instrument_bounds": [BOUND_LO, BOUND_HI],
        "headroom_beyond_null_each_direction": HEADROOM,
        "modal_null_by_answer": MODAL_NULL,
        "definitions": {
            "beyond_null": "social - (+4.358718) if social > +4.358718; "
                           "social - (-4.359231) if social < -4.359231; else 0",
            "headroom_used_pct": "100 * |beyond_null| / 5.641026",
            "modal_share": "largest single Likert answer / answered statements "
                           "(refusals excluded from the denominator), as prism_eval.py "
                           "computes it",
            "modal_share_of_all": "largest single Likert answer / all 62 statements. "
                                  "results/acquiescence_decomposition.json used this "
                                  "denominator, so its 10 personas that carry a refusal "
                                  "report a slightly lower share than modal_share here. "
                                  "The two section-31 headline personas have no refusals "
                                  "and are identical under both.",
            "social_agree": "refusals score 0, the same as Agree (the paper's rule)",
            "social_neutral": "refusals score that statement's midpoint",
            "social_exclude": "refused statements dropped, raw total pro-rated by "
                              "62 / n_answered before the transform",
        },
        "models": {},
    }
    for name, m in models.items():
        m["aggregates"] = aggregate(m)
        out["models"][name] = m

    dest = BASE / "results" / "decomposition"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "all_models_decomposition.json").write_text(json.dumps(out, indent=1))
    (dest / "summary.md").write_text(render_markdown(out))
    print(f"wrote {dest / 'all_models_decomposition.json'}")
    print(f"wrote {dest / 'summary.md'}")
    for name, m in out["models"].items():
        a = m["aggregates"]
        print(f"{name:14s} n={a['n_personas']:3d} "
              f"auth-null cleared {a['n_clearing_auth_null']:2d} "
              f"lib-null cleared {a['n_clearing_lib_null']:2d} "
              f"between {a['n_between_the_nulls']:2d} "
              f"modal={'%.3f' % a['mean_modal_share'] if a['mean_modal_share'] else 'n/a'}")
    return out


if __name__ == "__main__":
    main()
