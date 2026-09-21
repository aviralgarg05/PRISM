"""Statement probing and the neutral frame leave every existing config id unchanged.

Run directly: python test_statement_probe.py
"""

import glob
import json
import os

from prism_eval import config_id
from utils.prompt_variants import STANCE, build_essay_template
from utils.roles import roles

HERE = os.path.dirname(os.path.abspath(__file__))


def test_existing_enumeration_ids_unchanged():
    runs = [r for f in sorted(glob.glob(os.path.join(HERE, "..", "results", "m4", "m4_gemma_[0-9].json")))
            for r in json.load(open(f))["runs"]]
    hand = [r for r in runs if r["persona"] in roles]
    same = sum(config_id({"provider": "ollama", "model": "gemma3", "role": "evolved",
                          "role_text": roles[r["persona"]][1].strip(), "temperature": 0.0,
                          "model_kwargs": {"num_predict": 1200},
                          "prompt_label": f"confirm-{r['persona']}-r1"}) == r["config_id"] for r in hand)
    assert same == len(hand) == 69, same


def test_question_ids_change_the_id_and_order_does_not_matter():
    base = {"provider": "openai", "model": "gpt-3.5-turbo", "role": "evolved", "role_text": "x"}
    a = config_id(dict(base, question_ids=[4, 27]))
    b = config_id(dict(base, question_ids=[27, 4]))
    assert a == b and a != config_id(base)


def test_neutral_frame_drops_only_the_stance_sentence():
    paper = build_essay_template("PERSONA", {"stance": 0})
    neutral = build_essay_template("PERSONA", {"stance": len(STANCE) - 1})
    assert STANCE[-1] == "" and STANCE[0] in paper and STANCE[0] not in neutral
    assert neutral == paper.replace("\n\n" + STANCE[0], "")


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"{len(tests)} passed")
