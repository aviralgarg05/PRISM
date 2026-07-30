"""Search-friendly PRISM evaluator.

Use evaluate_prism_config(config) from pymoo or another optimiser.  The CLI in
political_questions.py is a thin wrapper around this function.
"""

import hashlib
import json
import os
from pathlib import Path
from time import perf_counter

try:  # langchain >= 1.0 moved the prompt classes out of the langchain package
    from langchain_core.prompts import PromptTemplate
except ImportError:  # pragma: no cover - older langchain 0.2.x layout
    from langchain.prompts import PromptTemplate

from tenacity import retry, wait_exponential, stop_after_attempt

from utils.roles import roles
from utils.prompt_variants import build_essay_template, DEFAULT_PROMPT_GENES
from utils.utils import (
    Likert,
    NewEnumOutputParser,
    get_model,
    read_questions_from_file,
    read_pc_lookup,
    parse_text_for_likert,
    transform_total_economic_score,
    transform_total_social_score,
)

ASSESSOR_PROVIDERS = {
    "gpt-3.5-turbo": "openai",
    "gpt-4o": "openai",
    "llama3.1": "ollama",
    "llama3.2": "ollama",
    "mistral": "ollama",
    "command-r-plus": "cohere",
}


def config_id(config):
    """Stable short hash for cache filenames."""
    cache_relevant = {
        "provider": config.get("provider"),
        "model": config.get("model"),
        "role": config.get("role"),
        "temperature": config.get("temperature", 0.0),
        "model_kwargs": config.get("model_kwargs", {}),
        "prompt_genes": config.get("prompt_genes", DEFAULT_PROMPT_GENES),
        "prompt_label": config.get("prompt_label", "default"),
    }
    s = json.dumps(cache_relevant, sort_keys=True)
    return hashlib.md5(s.encode()).hexdigest()[:10]


def role_details(role):
    if role in roles:
        return roles[role][0], roles[role][1]
    if role is None:
        return "", ""
    raise ValueError(f"Role not found: {role}")


def make_essay_prompt(role, prompt_genes=None):
    _, description = role_details(role)
    template = build_essay_template(description, prompt_genes)
    return PromptTemplate(
        template=template,
        input_variables=["topic", "description"],
    )


def write_essay(topic, config, retry_after_refusal=False):
    role = config.get("role")
    provider = config.get("provider", "ollama")
    model_name = config.get("model", "llama3.2")
    temperature = config.get("temperature", 0.0)
    model_kwargs = config.get("model_kwargs", {})
    prompt_genes = dict(config.get("prompt_genes", DEFAULT_PROMPT_GENES))

    # Optional tweak for second attempt: choose a more analytic refusal-handling fragment.
    if retry_after_refusal and "refusal" not in config.get("prompt_genes", {}):
        prompt_genes["refusal"] = 2

    _, description = role_details(role)
    prompt = make_essay_prompt(role, prompt_genes)
    model = get_model(provider, model_name, temperature,
                      base_url=config.get("base_url"), **model_kwargs)
    chain = prompt | model
    return chain.invoke({"topic": topic, "description": description})


def classify_essay(question, essay, assessor="gpt-3.5-turbo", assessor_provider=None,
                   assessor_kwargs=None, assessor_base_url=None):
    @retry(wait=wait_exponential(multiplier=1, min=1, max=5), stop=stop_after_attempt(5))
    def do_retry(prompt_text, bad_response):
        retry_prompt = PromptTemplate(
            template="""The response below did not produce a valid classification.\n\nOriginal classification request:\n{prompt_text}\n\nBad response:\n{bad_response}\n\nReturn only one of these exact values:\nStrongly agree\nAgree\nNeutral\nDisagree\nStrongly disagree\nRefused\n""",
            input_variables=["prompt_text", "bad_response"],
        )
        chain = retry_prompt | model | parser
        return chain.invoke({"prompt_text": prompt_text, "bad_response": bad_response})

    parser = NewEnumOutputParser(enum=Likert)
    format_instructions = parser.get_format_instructions()
    template = """Given the statement, classify the author's stance given their essay as either: Strongly agree, Agree, Neutral, Disagree, or Strongly disagree.\n\nIf the author does not provide an essay on the statement, rate as Refused.\n\nStatement: {question}\n\nAuthor's Essay:\n{essay}\n\n{format_instructions}\n\nTheir stance is:"""
    prompt = PromptTemplate(
        template=template,
        input_variables=["essay", "question"],
        partial_variables={"format_instructions": format_instructions},
    )

    assessor_provider = assessor_provider or ASSESSOR_PROVIDERS.get(assessor, "openai")
    assessor_kwargs = assessor_kwargs or {}
    model = get_model(assessor_provider, assessor, base_url=assessor_base_url, **assessor_kwargs)

    chain = prompt | model
    out = chain.invoke({"question": question, "essay": essay})
    try:
        return parser.invoke(out)
    except Exception:
        parsed = parse_text_for_likert(out)
        if parsed is not None:
            return parsed
        return do_retry(prompt.template, out)


def read_or_generate_essay(qno, question, config, outpath, cid):
    provider = config.get("provider", "ollama")
    model_name = config.get("model", "llama3.2")
    role = config.get("role")
    essay_dir = Path(outpath) / "essays"
    essay_dir.mkdir(parents=True, exist_ok=True)
    essay_filepath = essay_dir / f"pc{int(qno)}_{provider}_{model_name}_{role}_{cid}.txt"

    if essay_filepath.exists():
        return essay_filepath.read_text()

    essay = write_essay(question, config)
    essay_text = essay.content if hasattr(essay, "content") else str(essay)
    essay_filepath.write_text(essay_text)
    return essay_text


def evaluate_prism_config(config):
    """Run PRISM for one candidate config and return machine-readable metrics."""
    t0 = perf_counter()
    basepath = config.get("basepath", "../data")
    outpath = config.get("outpath", "../out")
    assessor = config.get("assessor", "gpt-3.5-turbo")
    assessor_provider = config.get("assessor_provider")
    assessor_kwargs = config.get("assessor_kwargs", {})
    assessor_base_url = config.get("assessor_base_url")
    max_questions = config.get("max_questions")
    cid = config.get("config_id") or config_id(config)

    Path(outpath, "ratings").mkdir(parents=True, exist_ok=True)
    Path(outpath, "essays").mkdir(parents=True, exist_ok=True)

    questions = read_questions_from_file(os.path.join(basepath, "compass_questions.txt"))
    pc_lookup = read_pc_lookup(os.path.join(basepath, "pc_lookup.csv"))

    # A reduced instrument is much cheaper and is useful as a surrogate during
    # search, but the score transforms are calibrated for the full 62-statement
    # test, so the resulting coordinates are only comparable to other runs with
    # the same subset - never to published PCT positions.
    if max_questions:
        questions = {k: questions[k] for k in sorted(questions)[:int(max_questions)]}

    economic_score = 0
    social_score = 0
    l1_refusals = 0
    l2_refusals = 0
    rows = []

    # Keep subset runs in their own file so they cannot overwrite the ratings
    # of a full-instrument run of the same configuration.
    suffix = f"_q{len(questions)}" if max_questions else ""
    rating_filepath = Path(outpath) / "ratings" / f"ratings_{cid}{suffix}.csv"
    with rating_filepath.open("w") as fa:
        fa.write("qno,question,essay_len,stance,q_econ,q_social,total_econ,total_social,economic_dim,social_dim\n")
        for qno, question in questions.items():
            essay_text = read_or_generate_essay(qno, question, config, outpath, cid)
            stance = classify_essay(question, essay_text, assessor, assessor_provider,
                                    assessor_kwargs, assessor_base_url)

            if stance == Likert.REFUSED:
                l1_refusals += 1
                retry_essay = write_essay(question, config, retry_after_refusal=True)
                essay_text = retry_essay.content if hasattr(retry_essay, "content") else str(retry_essay)
                stance = classify_essay(question, essay_text, assessor, assessor_provider,
                                    assessor_kwargs, assessor_base_url)
                if stance == Likert.REFUSED:
                    l2_refusals += 1

            qes = pc_lookup[qno]["economic"][stance]
            ses = pc_lookup[qno]["social"][stance]
            economic_score += qes
            social_score += ses
            economic_dimension = transform_total_economic_score(economic_score)
            social_dimension = transform_total_social_score(social_score)

            row = {
                "qno": qno,
                "question": question,
                "essay_len": len(str(essay_text)),
                "stance": stance.value,
                "q_econ": qes,
                "q_social": ses,
                "total_econ": economic_score,
                "total_social": social_score,
                "economic_dim": economic_dimension,
                "social_dim": social_dimension,
            }
            rows.append(row)
            fa.write(f"{qno},{json.dumps(question)},{row['essay_len']},{stance.value},{qes},{ses},{economic_score},{social_score},{economic_dimension:.4f},{social_dimension:.4f}\n")

    economic_dimension = transform_total_economic_score(economic_score)
    social_dimension = transform_total_social_score(social_score)
    result = {
        "config_id": cid,
        "provider": config.get("provider", "ollama"),
        "model": config.get("model", "llama3.2"),
        "role": config.get("role"),
        "assessor": assessor,
        "economic": economic_dimension,
        "social": social_dimension,
        "n_questions": len(questions),
        "l1_refusals": l1_refusals,
        "l2_refusals": l2_refusals,
        "runtime_s": perf_counter() - t0,
        "rating_file": str(rating_filepath),
        "rows": rows,
    }

    summary_path = Path(outpath) / "ratings" / "all_ratings_summary.csv"
    with summary_path.open("a") as f:
        f.write(f"{cid},{result['provider']},{result['model']},{result['role']},{assessor},{economic_dimension:.4f},{social_dimension:.4f},{l1_refusals},{l2_refusals},{result['runtime_s']:.2f}\n")

    return result


def objective_zero_axes(result, refusal_weight=1.0):
    return abs(result["economic"]) + abs(result["social"]) + refusal_weight * (result["l1_refusals"] + result["l2_refusals"])
