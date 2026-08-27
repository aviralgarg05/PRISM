"""Confirm an evolved persona against its seed on the full 62-statement instrument.

evolve_persona.py searches on a 20-statement subset because the full instrument
is too expensive to evaluate hundreds of times. The subset is a surrogate, and
its coordinates are not comparable to full-instrument positions, so any gain it
reports has to be re-measured on all 62 statements before it means anything.

The gain also has to clear repeat noise, and that can only be judged on the
full instrument: the subset gain and the full-instrument noise floor are
different scales, and dividing one by the other says nothing. So each persona is
run several times with independent essay draws and the noise is measured here,
in the same units as the effect.

prompt_label is what buys those independent draws: it is part of the cache key
and nothing else, so varying it forces fresh essays for an otherwise identical
configuration without altering a single word of the prompt.

    python confirm_persona.py --personas /tmp/confirm_personas.json --reps 3
"""

import argparse
import json
import random
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from prism_eval import evaluate_prism_config


def with_retry(fn, what):
    """Long runs die to transient network faults; a 62-statement arm is too
    expensive to restart from zero because of one DNS blip."""
    delay = 5
    for attempt in range(6):
        try:
            return fn()
        except Exception as e:
            name = type(e).__name__
            if name not in ("APIConnectionError", "APITimeoutError", "RateLimitError",
                            "InternalServerError", "ConnectError"):
                raise
            if attempt == 5:
                raise
            print(f"  [{what} failed: {name}, retrying in {delay}s]", flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 120)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--personas", required=True,
                    help="json mapping name -> persona text (plus an optional "
                         "'subset' block carrying the search-time scores)")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--provider", default="openai")
    ap.add_argument("--model", default="gpt-3.5-turbo", help="the audited model")
    ap.add_argument("--assessor", default="gpt-4o-mini")
    ap.add_argument("--assessor-provider", dest="assessor_provider", default="openai")
    ap.add_argument("--out", default="../results/persona_confirm_full62.json")
    ap.add_argument("--sleep-between", dest="sleep_between", type=float, default=10.0)
    ap.add_argument("--block-seed", dest="block_seed", type=int, default=1,
                    help="seed for the randomised block ordering")
    ap.add_argument("--rep-offset", dest="rep_offset", type=int, default=0,
                    help="shift replicate numbers, so concurrent processes "
                         "cover disjoint replicates of the same personas")
    args = ap.parse_args()

    spec = json.loads(Path(args.personas).read_text())
    subset = spec.pop("subset", {})
    personas = {k: v for k, v in spec.items() if isinstance(v, str)}

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log = json.loads(out_path.read_text()) if out_path.exists() else {"runs": []}
    log.update({"model": args.model, "assessor": args.assessor,
                "n_questions": 62, "subset_scores": subset})
    done = {(r["persona"], r["rep"]) for r in log["runs"]}

    print(f"Confirming {len(personas)} personas x {args.reps} reps on the full "
          f"instrument: {args.model} audited, {args.assessor} assessing.\n")

    # Randomised complete blocks: one replicate of every persona per round, in a
    # shuffled order. Running each persona's replicates as a contiguous block
    # aliases persona with wall-clock position, and section 27's nine-run
    # confirmation did exactly that - all three arms inside one 44-minute
    # window, never interleaved - so its sds are a floor rather than an
    # estimate. Blocking costs nothing and removes the confound.
    rng = random.Random(args.block_seed)
    plan = []
    for rep in range(1, args.reps + 1):
        order = list(personas)
        rng.shuffle(order)
        plan.extend((n, rep + args.rep_offset) for n in order)

    for name, rep in plan:
            text = personas[name]
            if (name, rep) in done:
                print(f"{name} rep{rep}: already done")
                continue
            config = {
                "provider": args.provider, "model": args.model,
                "role": "evolved", "role_text": text, "temperature": 0.0,
                # Independent essay draw, identical prompt.
                "prompt_label": f"confirm-{name}-r{rep}",
                "assessor": args.assessor,
                "assessor_provider": args.assessor_provider,
                # Matches the conditions the search ran under; a retry here
                # would score a different essay from the one the refusal came
                # from, which is not what the search was measuring.
                "no_refusal_retry": True,
            }
            res = with_retry(lambda: evaluate_prism_config(config), f"{name} rep{rep}")
            row = {"persona": name, "rep": rep, "config_id": res["config_id"],
                   "economic": res["economic"], "social": res["social"],
                   "response_entropy": res["response_entropy"],
                   "l2_refusals": res["l2_refusals"],
                   "t_iso": datetime.now(timezone.utc).isoformat()}
            log["runs"].append(row)
            # Written after every arm so an interrupted run keeps what it paid for.
            out_path.write_text(json.dumps(log, indent=1))
            print(f"{name} rep{rep}: social {row['social']:+6.2f}  "
                  f"econ {row['economic']:+6.2f}  H {row['response_entropy']:.2f}  "
                  f"refused {row['l2_refusals']}/62", flush=True)
            time.sleep(args.sleep_between)

    print("\n" + "=" * 64)
    print(f"{'persona':<20} {'social mean':>12} {'sd':>6} {'econ mean':>10} {'n':>3}")
    stats = {}
    for name in personas:
        soc = [r["social"] for r in log["runs"] if r["persona"] == name]
        eco = [r["economic"] for r in log["runs"] if r["persona"] == name]
        if not soc:
            continue
        sd = statistics.stdev(soc) if len(soc) > 1 else float("nan")
        stats[name] = {"social_mean": statistics.mean(soc), "social_sd": sd,
                       "economic_mean": statistics.mean(eco), "n": len(soc)}
        print(f"{name:<20} {statistics.mean(soc):+12.2f} {sd:6.2f} "
              f"{statistics.mean(eco):+10.2f} {len(soc):>3}")
    log["summary"] = stats
    out_path.write_text(json.dumps(log, indent=1))

    if "seed" in stats:
        base = stats["seed"]["social_mean"]
        print("\ngain over the best hand-written seed, social axis:")
        for name, s in stats.items():
            if name != "seed":
                print(f"  {name:<18} {s['social_mean'] - base:+.2f}")


if __name__ == "__main__":
    main()
