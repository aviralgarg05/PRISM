"""Search the prompt fragment space with pymoo.

The prompt handed to the audited model is assembled from six independently
selectable fragments (see utils/prompt_variants.py), so a candidate prompt is
just a vector of six integers. That makes the question "how far can prompting
move this model's political position" a small combinatorial search problem,
which is what this module hands to pymoo.

Three modes:

  --mode centre   Minimise |economic| and |social| as two objectives. The
                  resulting front shows how far each axis can be pulled toward
                  the origin, and what it costs on the other axis.

  --mode window   Minimise the signed coordinates in a chosen direction, e.g.
                  --direction left-lib pushes toward economic left and social
                  libertarian. Running all four directions traces the outer
                  boundary of the region the model can be prompted into - the
                  Overton window of the model under prompting rather than under
                  hand-written personas.

  --mode social   Steer the social axis only, trading it against response
                  variety. Preferred over the other two: the economic
                  coordinate rests on 18 of the 62 statements against 43 for
                  social, so a single mislabelled statement has 2.4 times the
                  leverage there, and candidate rankings survive a change of
                  assessor on social (Spearman +0.96) but not on economic
                  (+0.54). Optimising economic spends evaluations on an
                  ordering that does not reproduce. Direction comes from
                  --direction, whose social component is used.

All modes carry two constraints, and they are not optional bookkeeping.
Position on its own cannot distinguish a genuinely centrist audit from a
degenerate one: "Agree" scores zero on both axes for all 62 statements, and
strongly agreeing with left- and right-coded statements cancels out. So an
unconstrained search for the origin is solved perfectly by any prompt that
makes the model refuse everything, or agree with everything, without expressing
a political position at all. The constraints below rule out both.

  refusals        at most --max-refusals statements refused after retry
  response spread response_entropy at least --min-entropy

Evaluation is expensive - one candidate is up to 124 model calls - so results
are cached on disk by configuration hash and memoised in-process. Use
--max-questions to evaluate candidates on a subset of the instrument during
search and confirm the winners on the full 62.
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.optimize import minimize
from pymoo.termination import get_termination

from prism_eval import evaluate_prism_config
from utils.prompt_variants import decode_prompt_genes, prompt_gene_space_sizes

DIRECTIONS = {
    "left-lib": (1.0, 1.0),      # minimise economic and social -> down-left
    "left-auth": (1.0, -1.0),
    "right-lib": (-1.0, 1.0),
    "right-auth": (-1.0, -1.0),
}


class PromptSearchProblem(ElementwiseProblem):
    """One candidate = one integer vector over the prompt fragment space."""

    def __init__(self, base_config, mode="centre", direction="left-lib",
                 max_refusals=6, min_entropy=0.25, verbose=True, sleep_between=0.0):
        self.sizes = prompt_gene_space_sizes()
        self.gene_names = list(self.sizes)
        self.base_config = base_config
        self.mode = mode
        self.weights = DIRECTIONS[direction]
        self.max_refusals = max_refusals
        self.min_entropy = min_entropy
        self.verbose = verbose
        # A search evaluates candidates back to back with no natural pause. On a
        # laptop running the models locally that is a sustained thermal load,
        # quite unlike running single audits by hand. Pause between candidates
        # unless the models are hosted elsewhere.
        self.sleep_between = sleep_between
        self.history = []
        self._cache = {}

        super().__init__(
            n_var=len(self.gene_names),
            n_obj=2,
            n_ieq_constr=2,
            xl=np.zeros(len(self.gene_names), dtype=int),
            xu=np.array([self.sizes[g] - 1 for g in self.gene_names], dtype=int),
            vtype=int,
        )

    def genes(self, x):
        return {g: int(v) for g, v in zip(self.gene_names, x)}

    def evaluate_genes(self, genes):
        key = tuple(sorted(genes.items()))
        if key in self._cache:
            return self._cache[key]
        config = dict(self.base_config, prompt_genes=genes)
        result = evaluate_prism_config(config)
        result.pop("rows", None)
        self._cache[key] = result
        # Only after a real evaluation: cache hits cost nothing and need no pause.
        if self.sleep_between:
            time.sleep(self.sleep_between)
        return result

    def _evaluate(self, x, out, *args, **kwargs):
        genes = self.genes(x)
        r = self.evaluate_genes(genes)

        if self.mode == "centre":
            f = [abs(r["economic"]), abs(r["social"])]
        elif self.mode == "social":
            # Steer social, and maximise variety as a second objective rather
            # than only fencing it off as a constraint. A front then shows what
            # the steering costs in how varied the answers stay, which is the
            # trade-off that matters given "Agree" scores zero on both axes.
            _, ws = self.weights
            f = [ws * r["social"], -r["response_entropy"]]
        else:
            we, ws = self.weights
            f = [we * r["economic"], ws * r["social"]]

        # pymoo treats g <= 0 as satisfied.
        g = [r["l2_refusals"] - self.max_refusals,
             self.min_entropy - r["response_entropy"]]

        out["F"] = np.array(f, dtype=float)
        out["G"] = np.array(g, dtype=float)

        record = {"genes": genes, "economic": r["economic"], "social": r["social"],
                  "l2_refusals": r["l2_refusals"], "response_entropy": r["response_entropy"],
                  "modal_share": r["modal_share"], "feasible": bool(g[0] <= 0 and g[1] <= 0)}
        self.history.append(record)
        if self.verbose:
            print(f"  eval {len(self.history):>3}  econ {r['economic']:+6.2f}  "
                  f"social {r['social']:+6.2f}  refused {r['l2_refusals']:>2}  "
                  f"entropy {r['response_entropy']:.2f}  "
                  f"{'ok' if record['feasible'] else 'INFEASIBLE'}  {genes}",
                  flush=True)
        return out


def read_arguments():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--provider", default="ollama")
    p.add_argument("--model", default="llama3.2")
    p.add_argument("--role", default=None)
    p.add_argument("--temp", type=float, default=0.0)
    p.add_argument("--assessor", default="llama3.2")
    p.add_argument("--assessor-provider", dest="assessor_provider", default="ollama")
    p.add_argument("--base-url", dest="base_url", default=None)
    p.add_argument("--assessor-base-url", dest="assessor_base_url", default=None)
    p.add_argument("--basepath", default="../data")
    p.add_argument("--outpath", default="../out")
    p.add_argument("--num-predict", dest="num_predict", type=int, default=300)

    p.add_argument("--mode", choices=["centre", "window", "social"], default="centre")
    p.add_argument("--direction", choices=sorted(DIRECTIONS), default="left-lib",
                   help="Used by --mode window and --mode social.")
    p.add_argument("--max-refusals", dest="max_refusals", type=int, default=6)
    p.add_argument("--min-entropy", dest="min_entropy", type=float, default=0.25,
                   help="Reject candidates whose answers are too uniform to be a "
                        "position rather than a response style.")

    p.add_argument("--max-questions", dest="max_questions", type=int, default=None,
                   help="Evaluate candidates on a subset of the instrument. Strongly "
                        "recommended during search; confirm winners on all 62.")
    p.add_argument("--pop-size", dest="pop_size", type=int, default=8)
    p.add_argument("--n-gen", dest="n_gen", type=int, default=4)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--random-search", dest="random_search", action="store_true",
                   help="Sample uniformly instead of running NSGA-II, same budget and "
                        "same feasibility rules. The control for whether the optimiser "
                        "is earning its keep on a space this small.")
    p.add_argument("--sleep-between", dest="sleep_between", type=float, default=45.0,
                   help="Seconds to pause after each evaluation. A search runs "
                        "candidates back to back, which on a laptop serving the "
                        "models locally is a sustained thermal load. Set to 0 when "
                        "the models are hosted elsewhere (--base-url or an API).")
    p.add_argument("--out", default=None, help="Write the full search log here as JSON.")
    return p.parse_args()


def main():
    args = read_arguments()

    base_config = {
        "provider": args.provider,
        "model": args.model,
        "role": args.role,
        "temperature": args.temp,
        "assessor": args.assessor,
        "assessor_provider": args.assessor_provider,
        "base_url": args.base_url,
        "assessor_base_url": args.assessor_base_url,
        "basepath": args.basepath,
        "outpath": args.outpath,
        "max_questions": args.max_questions,
        "model_kwargs": {"num_predict": args.num_predict} if args.num_predict else {},
    }

    problem = PromptSearchProblem(
        base_config, mode=args.mode, direction=args.direction,
        max_refusals=args.max_refusals, min_entropy=args.min_entropy,
    )

    budget = args.pop_size * args.n_gen
    print(f"Search space: {np.prod([problem.sizes[g] for g in problem.gene_names])} "
          f"candidates over {problem.gene_names}")
    print(f"Budget: up to {budget} evaluations "
          f"(pop {args.pop_size} x {args.n_gen} generations), duplicates cached.")
    print(f"Mode: {args.mode}"
          + (f" direction={args.direction}" if args.mode == "window" else "")
          + f" | constraints: refusals<={args.max_refusals}, entropy>={args.min_entropy}\n")

    # Seed the paper's prompt (all-zero genes) as the first individual. Random
    # sampling will usually miss a single specific point in a 4800-candidate
    # space, and a search that never evaluates the published default cannot
    # report how far prompting moves a model away from it - nor keep it if it
    # is already the best answer, which in the first run it was.
    rng = np.random.default_rng(args.seed)
    seeded = np.vstack([
        np.zeros((1, problem.n_var), dtype=int),
        rng.integers(problem.xl, problem.xu + 1, size=(args.pop_size - 1, problem.n_var)),
    ]) if args.pop_size > 1 else np.zeros((1, problem.n_var), dtype=int)

    if args.random_search:
        # The obvious question about running an EA on 4800 candidates with a
        # budget in the tens: would uniform sampling of the same budget do as
        # well? Without this the optimisation framing is an assumption. Same
        # problem, same evaluation cache, same feasibility rules - only the
        # proposal distribution changes.
        rng2 = np.random.default_rng(args.seed)
        budget = args.pop_size * args.n_gen
        seen, results = set(), []
        # the paper's prompt is seeded here too, so both arms start level
        cands = [np.zeros(problem.n_var, dtype=int)]
        while len(cands) < budget:
            c = rng2.integers(problem.xl, problem.xu + 1)
            cands.append(c.astype(int))
        for c in cands:
            out = {}
            problem._evaluate(c, out)
            results.append((tuple(int(v) for v in c), out))
        print(f"\nRandom search over {len(results)} evaluations "
              f"({len(problem._cache)} distinct candidates actually scored)")
        feas = [r for r in problem.history if r["feasible"]]
        if feas:
            key = (lambda r: r["social"]) if args.direction.startswith("left") else (lambda r: -r["social"])
            best = min(feas, key=key)
            print(f"  best social {best['social']:+.2f}  entropy {best['response_entropy']:.2f}  {best['genes']}")
        if args.out:
            Path(args.out).write_text(json.dumps({
                "base_config": base_config, "mode": args.mode, "algorithm": "random",
                "direction": args.direction, "history": problem.history}, indent=2))
            print(f"Search log written to {args.out}")
        return

    algorithm = NSGA2(
        pop_size=args.pop_size,
        sampling=seeded,
        crossover=SBX(prob=0.9, eta=15, vtype=float, repair=RoundingRepair()),
        mutation=PM(prob=0.4, eta=20, vtype=float, repair=RoundingRepair()),
        eliminate_duplicates=True,
    )

    res = minimize(problem, algorithm, get_termination("n_gen", args.n_gen),
                   seed=args.seed, verbose=False)

    print("\n=== Pareto set ===")
    if res.X is None:
        print("No feasible candidate found. Loosen --max-refusals or --min-entropy, "
              "or use a model that refuses less.")
    else:
        X = np.atleast_2d(res.X)
        for x in X:
            genes = problem.genes(x)
            r = problem.evaluate_genes(genes)
            print(f"econ {r['economic']:+6.2f}  social {r['social']:+6.2f}  "
                  f"refused {r['l2_refusals']:>2}  entropy {r['response_entropy']:.2f}")
            for name, frag in decode_prompt_genes(genes).items():
                if frag:
                    print(f"    {name:<9} {frag}")
            print()

    if args.out:
        Path(args.out).write_text(json.dumps({
            "base_config": base_config,
            "mode": args.mode,
            "direction": args.direction if args.mode == "window" else None,
            "history": problem.history,
        }, indent=2))
        print(f"Search log written to {args.out}")


if __name__ == "__main__":
    main()
