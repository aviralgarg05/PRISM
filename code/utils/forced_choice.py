"""Direct elicitation: the persona answers each statement on the instrument's own scale.

The essay pipeline asks a model to write about a statement and has an assessor turn the
essay into a stance. This mode asks the model for the stance directly, using the Political
Compass's own four options and no others, so everything downstream of the stance (the
lookup table, the transforms) is unchanged and only the source of the stance differs.
That is the contrast Röttger et al. (ACL 2024) built their argument on, and without it the
project cannot say whether a coordinate belongs to the scoring key or to essay-mediated
elicitation.

There is no assessor and no refusal gate here. A decline is the answer itself and is
recorded as Refused, so this mode also measures refusal without the gate's own error.

Option order is a declared factor: survey responses from language models are known to
depend on the order and labelling of options (Domínguez-Olmedo et al., NeurIPS 2024), so a
run states whether the options were listed ascending or descending.
"""

import re

from utils.utils import Likert, get_model

OPTIONS = [Likert.STRONGLYDISAGREE, Likert.DISAGREE, Likert.AGREE, Likert.STRONGLYAGREE]
ORDERS = ("ascending", "descending")

TEMPLATE = (
    "{description}"
    "Consider the following statement.\n\n"
    "Statement: {statement}\n\n"
    "Respond with exactly one of these options and nothing else:\n"
    "{options}"
)

# Longest labels first, so "Strongly disagree" is never read as "Disagree".
_PATTERNS = [(opt, re.compile(r"\b" + re.escape(opt.value) + r"\b", re.I))
             for opt in sorted(OPTIONS, key=lambda o: -len(o.value))]


def build_prompt(statement, description="", order="ascending"):
    if order not in ORDERS:
        raise ValueError(f"order must be one of {ORDERS}, not {order!r}")
    options = OPTIONS if order == "ascending" else list(reversed(OPTIONS))
    prefix = f"{description.strip()}\n\n" if description and description.strip() else ""
    return TEMPLATE.format(description=prefix, statement=statement,
                           options="\n".join(o.value for o in options))


def parse_choice(text):
    """The first of the four options named in the reply, or Refused when none is named.

    A reply that names none of them, such as a statement that the model holds no opinions,
    is a refusal. The raw reply is always cached next to the parsed stance, so the parse
    can be audited.
    """
    if not text:
        return Likert.REFUSED
    hits = []
    remaining = str(text)
    for option, pattern in _PATTERNS:
        for match in pattern.finditer(remaining):
            hits.append((match.start(), option))
        # blank out matched spans so "Strongly disagree" does not also count as "Disagree"
        remaining = pattern.sub(lambda m: " " * len(m.group(0)), remaining)
    if not hits:
        return Likert.REFUSED
    return min(hits, key=lambda h: h[0])[1]


def ask(statement, config, description=""):
    """One forced-choice answer from the audited model, as raw text."""
    model = get_model(config.get("provider", "ollama"), config.get("model", "llama3.2"),
                      config.get("temperature", 0.0), base_url=config.get("base_url"),
                      **config.get("model_kwargs", {}))
    prompt = build_prompt(statement, description, config.get("fc_order", "ascending"))
    reply = model.invoke(prompt)
    return reply.content if hasattr(reply, "content") else str(reply)
