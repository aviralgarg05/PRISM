# PRISM
Preference Revelation through Indirect Stimulus Methodology (PRISM) is a flexible approach for auditing biases in Large Language Models (LLMs).

![The PRISM](./data/methodology.png)

See how we used PRISM in our paper [POW: Political Overton Windows of Large Language Models](https://github.com/CIS-PHAWM/POW).

## Citation
```
@article{azzopardi2024prismmethodologyauditingbiases,
      title={PRISM: A Methodology for Auditing Biases in Large Language Models}, 
      author={Leif Azzopardi and Yashar Moshfeghi},
      year={2024},
      eprint={2410.18906},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2410.18906}, 
}

```

## Installing
- Instal python 3.11.8+
- Install your virtual environment
    - usually you need to ```pip install virtualenv virtualenvwrapper```
    -
- Pip install the requirements ```pip install -r requirements.txt```
- cd to the ```code``` directory
- run ```python political_questions.py --provider=openai --model=gpt-4o --role="man"```
- or ```python political_questions.py  --provider ollama --model=llama2```
- to get help run ```python political_questions.py  --help``` 
- if you remove role, it will run it without a role.
- Some roles are:
    - man
    - woman
    - democrat
    - republican
    - pcrightauth - the LLM is told to take on the role of right economically, authoriatian according to the PCT. 
    - pcleftauth -- as above but left and auth.
    - pcrightlib -- etc.
    - pcleflib -- etc.

- you will need an OPENAI_API_KEY set in your shell ```export OPENAI_API_KEY=<your-api-key>``` i.e. go into ~/.profile or ~/.zsrchc


## Running fully locally (Ollama, no API key)

`requirements.txt` is a full `pip freeze` from a CUDA Linux workstation - it pins
nvidia-* wheels, torch and a spaCy model URL, and will not install on Apple
Silicon. Use `requirements-local.txt` instead, and Python 3.11 (the pinned
LangChain/pydantic stack does not build on 3.13+).

```
python3.11 -m venv .venv
.venv/bin/pip install -r requirements-local.txt
ollama serve &
ollama pull llama3.2
cd code
../.venv/bin/python political_questions.py \
    --provider ollama --model llama3.2 \
    --assessor llama3.2 --assessor-provider ollama \
    --role red --json
```

The default assessor is `gpt-3.5-turbo`, which needs an OpenAI key and bills per
evaluation. Passing `--assessor`/`--assessor-provider` as above keeps the whole
loop offline and free; see `ASSESSOR_PROVIDERS` in `code/prism_eval.py` for the
recognised assessors. Note that swapping the assessor changes the measurement
instrument, so local-assessor scores should be validated against the
`gpt-3.5-turbo` assessor on a sample before being reported.

Essays are cached under `--outpath` (default `../out`) and keyed by a hash of
the model, role, sampling parameters and prompt genes, so re-running an
identical configuration is nearly free. Assessor ratings are *not* cached and
are re-run every time.

### Prompt search space

`code/utils/prompt_variants.py` decomposes the essay prompt into six
independently selectable fragments (`context`, `task`, `stance`, `style`,
`refusal`, `centring`), each exposed as an integer-valued CLI flag:

```
../.venv/bin/python political_questions.py --provider ollama --model llama3.2 \
    --prompt-context 2 --prompt-stance 3 --prompt-centring 1 --json
```

`code/prism_eval.py:evaluate_prism_config(config)` is the same evaluation as a
callable, returning economic/social coordinates and refusal counts, for use as
an objective function from an optimiser.


## Running on Colab (no local compute, no API key)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/aviralgarg05/PRISM/blob/local-run-setup/notebooks/prism_colab.ipynb)

`notebooks/prism_colab.ipynb` installs Ollama on a Colab GPU runtime and runs
the whole audit there, so neither the audited model nor the assessor touches
your own machine. Select a T4 runtime; a 62-statement audit of a 7B model takes
roughly 5-10 minutes.

One audit is 124 sequential model calls (62 essays plus 62 classifications),
and every refusal adds a regenerated essay and a second classification on top.
A refusal-heavy configuration therefore costs close to twice a compliant one,
which is worth remembering before running a search over many configurations.


## Running against a hosted endpoint

`--base-url` points the client somewhere other than the default. Combined with
`--provider openai` this reaches any OpenAI-compatible service, several of
which have a free tier that needs only a signup, no card:

| Service | Base URL | Example model |
| --- | --- | --- |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| Cerebras | `https://api.cerebras.ai/v1` | `llama-3.3-70b` |
| OpenRouter | `https://openrouter.ai/api/v1` | any model tagged `:free` |

The OpenAI client reads its key from `OPENAI_API_KEY`, so set that to the key
for whichever service you are using:

```
export OPENAI_API_KEY=<key for the service above>
cd code
python political_questions.py \
    --provider openai --model llama-3.3-70b-versatile \
    --base-url https://api.groq.com/openai/v1 \
    --assessor llama-3.3-70b-versatile --assessor-provider openai \
    --assessor-base-url https://api.groq.com/openai/v1 \
    --role red --json
```

Google AI Studio also has a free tier and needs no `--base-url`, since the
`google` provider is supported directly - `pip install langchain-google-genai`,
set `GOOGLE_API_KEY`, then `--provider google --model gemini-2.0-flash`. The
Gemini family appears in the PRISM paper, so those results are comparable to
the published figures.

Free tiers are rate limited, and one audit is 124 requests plus two per
refusal. If you hit a limit, use `--max-questions` to shorten the instrument.

`--base-url` also works with `--provider ollama`, which is how you point at an
Ollama server running on another machine:

```
python political_questions.py --provider ollama --model mistral \
    --base-url http://<host>:11434 --json
```

## Searching the prompt space

`code/optimise_prompt.py` hands the prompt fragment space to pymoo. A candidate
is six integers indexing the fragment sets in `utils/prompt_variants.py`, so
the space is 4800 candidates, with the paper's own prompt at all zeros.

```
python optimise_prompt.py \
    --provider openai --model gpt-3.5-turbo \
    --assessor gpt-3.5-turbo --assessor-provider openai \
    --mode centre --max-questions 12 --num-predict 0 \
    --pop-size 6 --n-gen 3 --sleep-between 0
```

`--mode centre` minimises |economic| and |social|. `--mode window` minimises
the signed coordinates in one of four directions, so running all four traces
the region the model can be prompted into.

Two constraints are applied and they are not bookkeeping. "Agree" scores zero
on both axes for every statement, and strongly agreeing with left- and
right-coded statements cancels out, so an unconstrained search for the origin
is solved perfectly by any prompt that makes the model refuse everything or
agree with everything. `--max-refusals` and `--min-entropy` make those
degenerate answers infeasible rather than optimal.

The paper's prompt is seeded as the first individual, so the search always
knows the published baseline and can be asked how far it improves on it.

Run this against hosted models. A search evaluates candidates back to back;
`--sleep-between` defaults to 45 seconds precisely because an unpaced run
against a local Ollama server is a sustained thermal load on a laptop, and
throttling then corrupts the recorded runtimes. Set it to 0 when the models
are remote.

## Validating the assessor

The assessor is part of the instrument. `code/compare_assessors.py` scores the
same essays with two assessors and reports agreement, Cohen's kappa and the
mean signed Likert shift:

```
python compare_assessors.py --cid <config_id> --a gpt-3.5-turbo --b gpt-4o-mini
```

This is worth doing before trusting any position. Two assessors agreeing at
kappa 0.761 - indistinguishable from the 0.774 the paper reports against human
annotators - still moved the same essays by 1.75 on economic and 2.05 on
social, because disagreements concentrate on Strongly agree/Strongly disagree
flips, which carry the largest weights in the scoring table. Kappa weights
every disagreement equally; the score does not.

## Keeping the load down

A full audit is 124 sequential model calls, and each refusal adds two more.
On a laptop that is a sustained load; these flags reduce it:

- `--max-questions 15` scores a subset of the instrument. Note that the score
  transforms are calibrated for the full 62-statement test, so subset
  coordinates compare only to other runs using the same subset - not to
  published PCT positions. Subset runs are written to their own ratings file.
- `--num-predict 300` caps the essay length; the prompt only asks for 2-4
  sentences, so the tail of a long generation is wasted work.
- Essays are cached by configuration hash, so re-running a configuration you
  have already evaluated costs only the classification calls.

## Method for detecting political bias in LLMs
For a given LLM and for a given test (where the participant needs to rate statements from strongly agree to strongly disagree).
- Assign a role.
- Ask LLM given the role, to write an essay on the topic.
- Rate whether the author of the essay (strongly) agrees/disagrees.
- Tally up the results.