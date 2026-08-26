"""Evolve the persona text itself, using an LLM as the variation operator.

The fragment search in optimise_prompt.py picks from six hand-written menus,
which is 4800 candidates. Section 26 measured what that costs: on a space that
small, with largely additive slot effects, NSGA-II does no better than uniform
sampling. An optimiser only earns its place when the space cannot be covered.

So this searches the persona prose instead. A candidate is a paragraph, not six
integers, and the space is whatever an LLM can write. Variation is done by a
model rather than by bit-flips, which was the original suggestion in the first
project meeting.

    python evolve_persona.py --model gpt-3.5-turbo --assessor gpt-4o-mini \
        --direction auth --pop-size 8 --n-gen 8

Objectives, as in --mode social: push the social coordinate in the requested
direction, and keep response entropy high. Both are minimised internally.
Entropy is an objective rather than only a constraint because "Agree" scores
zero on both axes, so the cheapest way to reach an extreme is uniform answers
that carry no information.
"""

import argparse
import json
import random
import re
from pathlib import Path

from prism_eval import evaluate_prism_config
from utils.roles import roles
from utils.utils import get_model

# Personas already in the repo, used to seed generation 0 so the search starts
# from the published material rather than from nothing.
SEEDS = ["pcleftlib", "pcleftauth", "pcrightlib", "pcrightauth", "blue", "red"]

MUTATE = """You are helping explore how different persona descriptions change the political \
positions a language model expresses when writing short essays.

Here is a persona description:

---
{persona}
---

Rewrite it into a NEW persona description that pushes harder towards being \
{target}. Keep it to one paragraph of similar length. It must read as a coherent \
political outlook a person could hold, not a list of instructions. Do not mention \
essays, tests, scoring, or the Political Compass.

Return only the rewritten description."""

CROSSOVER = """You are helping explore how different persona descriptions change the political \
positions a language model expresses.

Persona A:
---
{a}
---

Persona B:
---
{b}
---

Write a NEW single-paragraph persona that combines the most distinctive elements \
of both, while being clearly {target}. It must read as a coherent political outlook \
a person could hold. Do not mention essays, tests, scoring, or the Political Compass.

Return only the new description."""

TARGET = {
    "auth": "socially authoritarian - favouring tradition, national loyalty, obedience to "
            "authority, strict discipline and firm limits on personal conduct",
    "lib": "socially libertarian - favouring personal freedom, tolerance, scepticism of "
           "authority, permissiveness about private conduct and rehabilitation over punishment",
}


def clean(text):
    """Strip the wrapping a chat model tends to add around a requested rewrite."""
    t = text.content if hasattr(text, "content") else str(text)
    t = re.sub(r"^\s*(here is|here's|sure[,!]?)\b.*?:\s*", "", t.strip(), flags=re.I | re.S)
    return t.strip().strip('"').strip()


class Candidate:
    __slots__ = ("text", "origin", "econ", "social", "entropy", "refusals", "feasible")

    def __init__(self, text, origin):
        self.text, self.origin = text, origin
        self.econ = self.social = self.entropy = None
        self.refusals = None
        self.feasible = False

    def key(self):
        return " ".join(self.text.split()).lower()


def dominates(a, b, sign):
    """Minimising (sign*social, -entropy)."""
    fa = (sign * a.social, -a.entropy)
    fb = (sign * b.social, -b.entropy)
    return all(x <= y for x, y in zip(fa, fb)) and fa != fb


def non_dominated(pop, sign):
    return [c for c in pop if not any(dominates(o, c, sign) for o in pop if o is not c)]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="gpt-3.5-turbo", help="the audited model")
    ap.add_argument("--provider", default="openai")
    ap.add_argument("--assessor", default="gpt-4o-mini")
    ap.add_argument("--assessor-provider", dest="assessor_provider", default="openai")
    ap.add_argument("--writer", default="gpt-4o-mini",
                    help="model that mutates and recombines personas")
    ap.add_argument("--direction", choices=["auth", "lib"], default="auth")
    ap.add_argument("--pop-size", dest="pop_size", type=int, default=8)
    ap.add_argument("--n-gen", dest="n_gen", type=int, default=8)
    ap.add_argument("--max-questions", dest="max_questions", type=int, default=20)
    ap.add_argument("--max-refusals", dest="max_refusals", type=int, default=6)
    ap.add_argument("--min-entropy", dest="min_entropy", type=float, default=0.25)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--outpath", default="../out")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    sign = 1.0 if args.direction == "lib" else -1.0   # lib = minimise social, auth = maximise
    target = TARGET[args.direction]
    writer = get_model("openai", args.writer, 0.9)     # high temperature: we want variety here

    base = {"provider": args.provider, "model": args.model, "role": "evolved",
            "temperature": 0.0, "assessor": args.assessor,
            "assessor_provider": args.assessor_provider,
            "max_questions": args.max_questions, "no_refusal_retry": True,
            "outpath": args.outpath, "model_kwargs": {}}

    evaluated, history = {}, []

    def evaluate(c):
        k = c.key()
        if k in evaluated:
            cached = evaluated[k]
            c.econ, c.social, c.entropy, c.refusals, c.feasible = (
                cached.econ, cached.social, cached.entropy, cached.refusals, cached.feasible)
            return c
        r = evaluate_prism_config(dict(base, role_text=c.text))
        c.econ, c.social = r["economic"], r["social"]
        c.entropy, c.refusals = r["response_entropy"], r["l2_refusals"]
        c.feasible = c.refusals <= args.max_refusals and c.entropy >= args.min_entropy
        evaluated[k] = c
        history.append({"text": c.text, "origin": c.origin, "economic": c.econ,
                        "social": c.social, "response_entropy": c.entropy,
                        "l2_refusals": c.refusals, "feasible": c.feasible})
        print(f"  eval {len(history):>3} [{c.origin:<9}] social {c.social:+6.2f} "
              f"econ {c.econ:+6.2f} entropy {c.entropy:.2f} refused {c.refusals:>2} "
              f"{'ok' if c.feasible else 'INFEASIBLE'}", flush=True)
        return c

    print(f"Evolving persona text: {args.model} audited, {args.assessor} assessing, "
          f"{args.writer} writing")
    print(f"Direction: {args.direction}.  Population {args.pop_size} x {args.n_gen} generations\n")

    pop = [Candidate(roles[s][1].strip(), "seed") for s in SEEDS[:args.pop_size]]
    while len(pop) < args.pop_size:
        src = rng.choice(pop)
        pop.append(Candidate(clean(writer.invoke(MUTATE.format(persona=src.text, target=target))),
                             "seed-mut"))
    for c in pop:
        evaluate(c)

    for gen in range(1, args.n_gen):
        print(f"\n-- generation {gen} --")
        parents = non_dominated([c for c in pop if c.feasible], sign) or pop
        children = []
        while len(children) < args.pop_size:
            if len(parents) > 1 and rng.random() < 0.4:
                a, b = rng.sample(parents, 2)
                txt = clean(writer.invoke(CROSSOVER.format(a=a.text, b=b.text, target=target)))
                origin = "crossover"
            else:
                src = rng.choice(parents)
                txt = clean(writer.invoke(MUTATE.format(persona=src.text, target=target)))
                origin = "mutation"
            if txt and len(txt) > 80:
                children.append(Candidate(txt, origin))
        for c in children:
            evaluate(c)
        # survival: keep the best pop_size by non-dominated rank, feasible first
        merged = pop + children
        feas = [c for c in merged if c.feasible]
        keep, pool = [], list(feas)
        while pool and len(keep) < args.pop_size:
            front = non_dominated(pool, sign)
            keep.extend(front[:args.pop_size - len(keep)])
            pool = [c for c in pool if c not in front]
        pop = keep or merged[:args.pop_size]
        best = min((c for c in pop if c.feasible), key=lambda c: sign * c.social, default=None)
        if best:
            print(f"  best so far: social {best.social:+.2f}  entropy {best.entropy:.2f}")

    print("\n=== final front ===")
    for c in sorted(non_dominated([c for c in pop if c.feasible], sign),
                    key=lambda c: sign * c.social):
        print(f"\nsocial {c.social:+.2f}  econ {c.econ:+.2f}  entropy {c.entropy:.2f}  ({c.origin})")
        print("  " + c.text[:400].replace("\n", " "))

    if args.out:
        Path(args.out).write_text(json.dumps(
            {"model": args.model, "assessor": args.assessor, "writer": args.writer,
             "direction": args.direction, "history": history}, indent=2))
        print(f"\nlog written to {args.out}")


if __name__ == "__main__":
    main()
