"""Addition to the eleventh pre-registration, decided after the hosted results were seen
and reported as such: re-label every flip essay with gpt-4o and compare the
endorse / not-endorse call with gpt-4o-mini's. Essays whose gate verdict was
REFUSED are left out, because the endpoint already counts them as not endorsing.

Usage (from code/): ../.venv/bin/python ../results/stance_flip/second_assessor.py [model ...]
"""

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "code"))

from prism_eval import classify_essay  # noqa: E402
from utils.refusal_gate import GATE_VERSION  # noqa: E402
from utils.utils import read_questions_from_file  # noqa: E402

ENDORSE = {"Agree", "Strongly agree"}


def main():
    questions = dict(read_questions_from_file(os.path.join(REPO, "data", "compass_questions.txt")))
    out, agree, total = [], 0, 0
    models = sys.argv[1:]   # optional: only these models' arm files, written to their own output
    arms = sorted(glob.glob(os.path.join(HERE, "flip_*_paper.json")) + glob.glob(os.path.join(HERE, "flip_*_neutral.json")))
    if models:
        arms = [a for a in arms if os.path.basename(a).split("_")[1] in models]
    for path in arms:
        d = json.load(open(path))
        model = d.get("model") or os.path.basename(path).split("_")[1]
        for r in d["runs"]:
            cache = json.load(open(os.path.join(REPO, "out", "ratings", f"cache_{r['config_id']}_gpt-4o-mini_gate{GATE_VERSION}.json")))
            for q in ("4", "27"):
                if cache[q].get("gate") == "REFUSED":
                    continue
                provider = "ollama" if model in ("gemma3", "mistral", "llama3.2") else "openai"
                essay_path = os.path.join(REPO, "out", "essays", f"pc{q}_{provider}_{model}_evolved_{r['config_id']}.txt")
                essay = open(essay_path).read()
                label = classify_essay(questions[int(q)], essay, "gpt-4o", "openai", {}, None, None)
                label = getattr(label, "value", label)
                mini = cache[q]["stance"]
                same = (label in ENDORSE) == (mini in ENDORSE)
                agree += same; total += 1
                out.append({"file": os.path.basename(path), "persona": r["persona"], "rep": r["rep"], "q": q,
                            "gpt-4o-mini": mini, "gpt-4o": label, "same_endorsement_call": same})
    name = "second_assessor.json" if not models else "second_assessor_" + "_".join(models) + ".json"
    json.dump({"n": total, "agree": agree, "rows": out}, open(os.path.join(HERE, name), "w"), indent=1)
    print(f"endorse/not-endorse agreement, gpt-4o vs gpt-4o-mini: {agree}/{total}")
    for row in out:
        if not row["same_endorsement_call"]:
            print("  differs:", row["file"], row["persona"], row["rep"], "q" + row["q"], row["gpt-4o-mini"], "->", row["gpt-4o"])


if __name__ == "__main__":
    main()
