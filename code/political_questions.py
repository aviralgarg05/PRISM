import argparse
import json

from prism_eval import evaluate_prism_config, objective_zero_axes
from utils.prompt_variants import prompt_gene_space_sizes, DEFAULT_PROMPT_GENES


def parse_model_kwargs(args):
    return {k: v for k, v in {
        "top_p": args.top_p,
        "top_k": args.top_k,
        "num_ctx": args.num_ctx,
        "num_predict": args.num_predict,
        "repeat_penalty": args.repeat_penalty,
    }.items() if v is not None}


def parse_prompt_genes(args):
    genes = dict(DEFAULT_PROMPT_GENES)
    for k in genes:
        v = getattr(args, f"prompt_{k}")
        if v is not None:
            genes[k] = v
    return genes


def read_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", type=str, default="ollama")
    parser.add_argument("--model", type=str, default="llama3.2")
    parser.add_argument("--role", type=str, default=None)
    parser.add_argument("--temp", type=float, default=0.0)
    parser.add_argument("--assessor", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--assessor-provider", type=str, default=None)
    parser.add_argument("--basepath", type=str, default="../data")
    parser.add_argument("--outpath", type=str, default="../out")

    # Ollama / model parameters
    parser.add_argument("--top-p", dest="top_p", type=float, default=None)
    parser.add_argument("--top-k", dest="top_k", type=int, default=None)
    parser.add_argument("--num-ctx", dest="num_ctx", type=int, default=None)
    parser.add_argument("--num-predict", dest="num_predict", type=int, default=None)
    parser.add_argument("--repeat-penalty", dest="repeat_penalty", type=float, default=None)

    # Integer-coded prompt genes
    for gene, size in prompt_gene_space_sizes().items():
        parser.add_argument(f"--prompt-{gene}", type=int, default=None, help=f"0..{size-1}")

    parser.add_argument("--json", action="store_true", help="Print result as JSON for scripts/optimisers")
    return parser.parse_args()


def main():
    args = read_arguments()
    config = {
        "provider": args.provider,
        "model": args.model,
        "role": args.role,
        "temperature": args.temp,
        "assessor": args.assessor,
        "assessor_provider": args.assessor_provider,
        "basepath": args.basepath,
        "outpath": args.outpath,
        "model_kwargs": parse_model_kwargs(args),
        "prompt_genes": parse_prompt_genes(args),
    }

    result = evaluate_prism_config(config)
    result_no_rows = {k: v for k, v in result.items() if k != "rows"}
    result_no_rows["objective_zero_axes"] = objective_zero_axes(result)

    if args.json:
        print(json.dumps(result_no_rows, indent=2))
    else:
        print("Configuration")
        print("-------------")
        print(json.dumps(config, indent=2))
        print("Result")
        print("------")
        print(json.dumps(result_no_rows, indent=2))


if __name__ == "__main__":
    main()
