"""Dated model versions, so a result can be reproduced after an alias moves.

A hosted alias such as "gpt-4o" is a pointer that the provider can move to a new
snapshot without notice. Section 38 found seven of 44 gate verdicts changing in
three days on unpinned endpoints, which is the reason this file exists.

get_model() maps each alias below to its snapshot when it talks to the real
OpenAI endpoint. The configured model name is left unchanged, so config ids and
cached ratings stay valid: on 2026-09-21 every alias here resolved to exactly
the snapshot it is pinned to, and gpt-4o-mini and gpt-5.4-mini list no other
snapshot, so every earlier run used these versions too. gpt-4o lists three
snapshots and its alias pointed at 2024-08-06.

Ollama models cannot be addressed by digest through the chat API, so their
digests are recorded here and checked before a run by verify_model_versions.py.
"""

OPENAI_PINNED = {
    "gpt-4o-mini": "gpt-4o-mini-2024-07-18",
    "gpt-4o": "gpt-4o-2024-08-06",
    "gpt-3.5-turbo": "gpt-3.5-turbo-0125",
    "gpt-5.4-mini": "gpt-5.4-mini-2026-03-17",
}

# Digest prefixes as reported by the workstation's ollama /api/tags on 2026-09-21.
OLLAMA_DIGESTS = {
    "llama3.2:latest": "a80c4f17acd5",
    "mistral:latest": "6577803aa9a0",
    "gemma3:latest": "a2af6cc3eb7f",
}


def pinned_openai_model(model_name, base_url=None):
    """The dated snapshot for an OpenAI alias, or the name unchanged.

    Only applies on the real OpenAI endpoint: an OpenAI-compatible service at
    another base_url has its own model names.
    """
    if base_url:
        return model_name
    return OPENAI_PINNED.get(model_name, model_name)


def ollama_tag(model_name):
    """Ollama reports untagged models as ':latest'."""
    return model_name if ":" in model_name else f"{model_name}:latest"
