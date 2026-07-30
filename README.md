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


## Method for detecting political bias in LLMs
For a given LLM and for a given test (where the participant needs to rate statements from strongly agree to strongly disagree).
- Assign a role.
- Ask LLM given the role, to write an essay on the topic.
- Rate whether the author of the essay (strongly) agrees/disagrees.
- Tally up the results.