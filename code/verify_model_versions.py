"""Check that every pinned model still resolves to the version recorded for it.

Run before any registered experiment:

    python verify_model_versions.py                      # hosted aliases
    python verify_model_versions.py --ollama http://localhost:11434

Exits non-zero if an alias now resolves to a different snapshot or an ollama
tag now has a different digest, because a result produced after that point is
not comparable with the earlier ones.
"""

import argparse
import json
import sys
import urllib.request

from utils.model_versions import OLLAMA_DIGESTS, OPENAI_PINNED


def check_openai():
    from openai import OpenAI

    client = OpenAI()
    ok = True
    for alias, snapshot in OPENAI_PINNED.items():
        kwargs = dict(model=alias, messages=[{"role": "user", "content": "Reply with the word ok."}])
        if alias.startswith("gpt-5"):
            kwargs["max_completion_tokens"] = 16
        else:
            kwargs.update(max_tokens=2, temperature=0)
        resolved = client.chat.completions.create(**kwargs).model
        match = resolved == snapshot
        ok &= match
        print(f"  {alias:<16} -> {resolved:<28} {'ok' if match else 'MOVED, pinned ' + snapshot}")
    return ok


def check_ollama(base_url):
    with urllib.request.urlopen(f"{base_url.rstrip('/')}/api/tags", timeout=20) as r:
        tags = {m["name"]: m["digest"] for m in json.load(r)["models"]}
    ok = True
    for tag, prefix in OLLAMA_DIGESTS.items():
        digest = tags.get(tag, "")
        match = digest.startswith(prefix)
        ok &= match
        print(f"  {tag:<16} {digest[:12] or 'missing':<14} {'ok' if match else 'CHANGED, recorded ' + prefix}")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ollama", help="ollama base URL to check digests against")
    ap.add_argument("--skip-openai", action="store_true")
    args = ap.parse_args()
    ok = True
    if not args.skip_openai:
        print("hosted aliases")
        ok &= check_openai()
    if args.ollama:
        print("ollama digests")
        ok &= check_ollama(args.ollama)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
