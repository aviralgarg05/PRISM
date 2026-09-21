"""Persona files for the llama3.2 enumeration (tenth pre-registration).

Uses exactly the texts the other five enumerations used, and proves it: every
text is checked by reproducing the config id gemma3's enumeration recorded for
it. The 69 hand-written personas are the roles.py text with surrounding
whitespace stripped; the two search-derived personas are recovered from the
committed results by the same check. Writes two shards, so the workstation can
run two clients.

Usage (from code/): ../.venv/bin/python ../results/m6/build_llama_personas.py
"""

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "code"))

from prism_eval import config_id  # noqa: E402
from utils.roles import roles  # noqa: E402


def gemma_cid(name, text):
    return config_id({"provider": "ollama", "model": "gemma3", "role": "evolved", "role_text": text,
                      "temperature": 0.0, "model_kwargs": {"num_predict": 1200},
                      "prompt_label": f"confirm-{name}-r1"})


def main():
    runs = [r for f in sorted(glob.glob(os.path.join(HERE, "..", "m4", "m4_gemma_[0-9].json")))
            for r in json.load(open(f))["runs"]]
    recorded = {r["persona"]: r["config_id"] for r in runs}

    texts = {}
    for name, cid in recorded.items():
        if name in roles and gemma_cid(name, roles[name][1].strip()) == cid:
            texts[name] = roles[name][1].strip()

    wanted = {n: c for n, c in recorded.items() if n not in texts}

    def walk(node):
        if isinstance(node, str) and len(node) > 80:
            for name, cid in wanted.items():
                if name not in texts and gemma_cid(name, node.strip()) == cid:
                    texts[name] = node.strip()
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for path in sorted(glob.glob(os.path.join(HERE, "..", "**", "*.json"), recursive=True)):
        if len(texts) == len(recorded):
            break
        try:
            walk(json.load(open(path)))
        except Exception:
            continue

    missing = sorted(set(recorded) - set(texts))
    if missing:
        sys.exit(f"could not reproduce the enumerated text for: {missing}")

    names = sorted(texts)
    shards = [names[0::2], names[1::2]]
    for i, shard in enumerate(shards):
        out = os.path.join(HERE, f"personas_llama32_{i}.json")
        json.dump({n: texts[n] for n in shard}, open(out, "w"), indent=1)
        print(f"{os.path.basename(out)}: {len(shard)} personas")
    print(f"all {len(texts)} texts reproduce gemma3's recorded config ids")


if __name__ == "__main__":
    main()
