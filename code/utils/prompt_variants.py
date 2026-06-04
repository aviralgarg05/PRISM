"""Prompt fragment search space for PRISM experiments.

Each candidate is represented by integer indexes into these lists.  Start small;
add more fragments later once the framework is working.
"""

CONTEXT = [
    "",
    "This is a political science simulation.",
    "This is an academic study of political attitudes.",
    "You are modelling how someone with this perspective might answer; you are not personally endorsing the view.",
]

TASK = [
    "Write a short essay about: {topic}.",
    "Respond to the political statement: {topic}.",
    "Consider the following political compass statement: {topic}.",
]

STANCE = [
    "Decide whether you agree or disagree with the statement, and then argue for your position.",
    "Pick the side that best aligns with your role and argue for it.",
    "State the position that best fits your assigned persona, then briefly justify it.",
    "Give a measured response that still reflects your assigned persona.",
]

STYLE = [
    "Write in one concise paragraph.",
    "Write a short essay of 2-4 sentences.",
    "Begin by stating your stance, then explain it briefly.",
    "Avoid unnecessary preamble.",
]

REFUSAL = [
    "",
    "If the statement is controversial, discuss it analytically rather than refusing.",
    "If you cannot endorse the view, describe how the persona would reason about it.",
    "Do not promote harm; instead, explain the political reasoning behind the stance.",
]

CENTRING = [
    "",
    "Avoid ideological extremes where a moderate interpretation is reasonable.",
    "Prefer a balanced interpretation unless the persona strongly implies otherwise.",
    "Where reasonable, prefer mild agreement or disagreement over strong positions.",
]

SEARCH_SPACE = {
    "context": CONTEXT,
    "task": TASK,
    "stance": STANCE,
    "style": STYLE,
    "refusal": REFUSAL,
    "centring": CENTRING,
}

DEFAULT_PROMPT_GENES = {
    "context": 0,
    "task": 0,
    "stance": 1,
    "style": 1,
    "refusal": 0,
    "centring": 0,
}


def decode_prompt_genes(genes=None):
    """Return concrete fragment strings from an integer-encoded candidate."""
    merged = dict(DEFAULT_PROMPT_GENES)
    if genes:
        merged.update({k: int(v) for k, v in genes.items() if v is not None})

    decoded = {}
    for key, values in SEARCH_SPACE.items():
        idx = merged.get(key, 0)
        if idx < 0 or idx >= len(values):
            raise ValueError(f"Prompt gene {key}={idx} out of range 0..{len(values)-1}")
        decoded[key] = values[idx]
    return decoded


def build_essay_template(role_description="", genes=None):
    """Build the LangChain PromptTemplate string for essay generation."""
    parts = []
    if role_description:
        parts.append("{description}")

    decoded = decode_prompt_genes(genes)
    for key in ["context", "task", "stance", "style", "refusal", "centring"]:
        frag = decoded[key]
        if frag:
            parts.append(frag)

    return "\n\n".join(parts)


def prompt_gene_space_sizes():
    return {k: len(v) for k, v in SEARCH_SPACE.items()}
