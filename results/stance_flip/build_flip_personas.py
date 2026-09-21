"""Persona file for the eleventh pre-registration (the section 27 stance flip).

The two evolved personas and their seed are recovered from the committed search
log (results/persona_evo_auth.json) and proven by reproducing the config ids the
section 27 confirmation recorded. The output file is written locally and kept out
of git under ETHICS.md's release policy: the evolved texts are the ones that
produce the flip. "none" is the empty persona.

Usage (from code/): ../.venv/bin/python ../results/stance_flip/build_flip_personas.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "code"))

from prism_eval import config_id  # noqa: E402


def cid(name, text):
    return config_id({"provider": "openai", "model": "gpt-3.5-turbo", "role": "evolved", "role_text": text,
                      "temperature": 0.0, "model_kwargs": {}, "prompt_label": f"confirm-{name}-r1"})


def main():
    conf = json.load(open(os.path.join(HERE, "..", "persona_confirm_full62.json")))
    target = {r["persona"]: r["config_id"] for r in conf["runs"] if r["rep"] == 1}
    found = {}

    def walk(node):
        if isinstance(node, str) and len(node) > 60:
            for name, want in target.items():
                if name not in found:
                    for text in (node, node.strip()):
                        if cid(name, text) == want:
                            found[name] = text
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(json.load(open(os.path.join(HERE, "..", "persona_evo_auth.json"))))
    missing = sorted(set(target) - set(found))
    if missing:
        sys.exit(f"could not reproduce: {missing}")
    out = {"none": "", "seed": found["seed"], "crossover": found["crossover"], "mutation": found["mutation"]}
    path = os.path.join(HERE, "personas_flip.json")
    json.dump(out, open(path, "w"), indent=1)
    print(f"wrote {os.path.basename(path)}: {list(out)}; all three texts reproduce section 27's config ids")


if __name__ == "__main__":
    main()
