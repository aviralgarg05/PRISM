"""get_model talks to the dated snapshot on OpenAI and leaves everything else alone.

Run directly: python test_model_versions.py
"""

import os

from utils.model_versions import OPENAI_PINNED, pinned_openai_model
from utils.utils import get_model


def test_aliases_map_to_snapshots():
    for alias, snapshot in OPENAI_PINNED.items():
        assert pinned_openai_model(alias) == snapshot


def test_other_endpoints_and_names_untouched():
    assert pinned_openai_model("gpt-4o", base_url="https://example.invalid/v1") == "gpt-4o"
    assert pinned_openai_model("gpt-4o-2024-11-20") == "gpt-4o-2024-11-20"
    assert pinned_openai_model("some-other-model") == "some-other-model"


def test_get_model_uses_snapshot():
    os.environ.setdefault("OPENAI_API_KEY", "sk-test-not-used")
    assert get_model("openai", "gpt-4o-mini").model_name == "gpt-4o-mini-2024-07-18"
    assert get_model("openai", "gpt-4o", base_url="https://example.invalid/v1").model_name == "gpt-4o"


def test_ollama_untouched():
    assert get_model("ollama", "mistral").model == "mistral"


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"{len(tests)} passed")
