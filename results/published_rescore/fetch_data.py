"""Download the published per-statement answers re-scored under the thirteenth pre-registration.

Röttger et al. (ACL 2024), github.com/paul-rottger/llm-values-pct, CC-BY-4.0: the forced-choice
paraphrase and jailbreak completions and the proposition template. Wright et al. (Findings of
EMNLP 2024), huggingface.co/datasets/copenlu/llm-pct-tropes, MIT: the base closed-form opinions.
Files go to raw/ (kept out of git); SHA-256 sums are written to checksums.txt, which is committed,
so a later download can be checked against the one analysed.

Usage (from the repository root): python3 results/published_rescore/fetch_data.py
"""

import hashlib
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
R = "https://raw.githubusercontent.com/paul-rottger/llm-values-pct/main/data"
W = "https://huggingface.co/datasets/copenlu/llm-pct-tropes/resolve/main/opinions/base/closed"

PARA = ["Llama-2-13b-chat-hf", "Llama-2-70b-chat-hf", "Llama-2-7b-chat-hf", "Mistral-7B-Instruct-v0.1",
        "Mistral-7B-Instruct-v0.2", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", "zephyr-7b-beta"]
JAIL = PARA + ["gpt-4-0613", "gpt-4-1106-preview"]
WRIGHT = ["Llama-2-13b-chat-hf", "Meta-Llama-3-8B-Instruct", "Mistral-7B-Instruct-v0.2",
          "Mixtral-8x7B-Instruct-v0.1", "OLMo-7B-Instruct", "zephyr-7b-beta"]

FILES = ([(f"{R}/completions/explicit_paraphrase_experiments_240124/{m}.csv", f"rottger/paraphrase/{m}.csv") for m in PARA]
         + [(f"{R}/completions/explicit_jailbreak_experiments_230124/{m}.csv", f"rottger/jailbreak/{m}.csv") for m in JAIL]
         + [(f"{R}/templates/pct_propositions.csv", "rottger/pct_propositions.csv")]
         # Their mapping and scoring code and the notebook that printed their coordinates: read as
         # text (the mapping table is parsed with ast and the printed coordinates are the reference
         # for validation). Nothing from these files is executed.
         + [(f"https://raw.githubusercontent.com/paul-rottger/llm-values-pct/main/notebooks/{f}", f"rottger/{f.split('/')[-1]}")
            for f in ("utils/completion_helpers.py", "utils/pct_helpers.py", "explicit_paraphrase_experiments.ipynb")]
         + [(f"{W}/{m}.csv", f"wright/base_closed/{m}.csv") for m in WRIGHT])


def main():
    sums, total = [], 0
    for url, rel in FILES:
        path = os.path.join(RAW, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            urllib.request.urlretrieve(url, path)
        data = open(path, "rb").read()
        total += len(data)
        sums.append(f"{hashlib.sha256(data).hexdigest()}  {len(data):>10}  {rel}")
    open(os.path.join(HERE, "checksums.txt"), "w").write("\n".join(sums) + "\n")
    print(f"{len(FILES)} files, {total:,} bytes")


if __name__ == "__main__":
    main()
