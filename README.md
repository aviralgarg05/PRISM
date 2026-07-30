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


## Running locally with Ollama

`requirements.txt` is a `pip freeze` from a CUDA Linux workstation and will not
install on Apple Silicon. Use `requirements-local.txt`, with Python 3.11.

```
python3.11 -m venv .venv
.venv/bin/pip install -r requirements-local.txt
ollama serve &
ollama pull llama3.2
cd code
../.venv/bin/python political_questions.py \
    --provider ollama --model llama3.2 \
    --assessor llama3.2 --assessor-provider ollama --json
```

The default assessor is `gpt-3.5-turbo` and needs `OPENAI_API_KEY`. Passing
`--assessor`/`--assessor-provider` as above keeps everything offline, but the
assessor is part of the instrument - see `FINDINGS.md`.

Essays and assessor ratings are cached by configuration hash under `--outpath`,
so re-evaluating a configuration is free.

## Added in this branch

- `--base-url` / `--assessor-base-url` reach any OpenAI-compatible endpoint, or
  an Ollama server on another machine (`--base-url http://<host>:11434`).
- `--max-questions N` scores a subset spread across the instrument. Subset
  coordinates are not comparable to full 62-statement positions.
- `code/optimise_prompt.py` searches the prompt fragment space with pymoo.
- `code/compare_assessors.py` scores the same essays with two assessors and
  reports agreement and Cohen's kappa.

```
python optimise_prompt.py --provider openai --model gpt-3.5-turbo \
    --assessor gpt-3.5-turbo --assessor-provider openai \
    --mode centre --max-questions 12 --num-predict 0 \
    --pop-size 6 --n-gen 3 --sleep-between 0
```

Run searches against hosted models. `--sleep-between` defaults to 45s because
an unpaced search against a local Ollama server is a sustained load on a laptop.

**`FINDINGS.md` records what these runs turned up**, including a prompt fidelity
problem that changed the baseline, and how far the measured position moves when
the assessor is swapped.

## Method for detecting political bias in LLMs
For a given LLM and for a given test (where the participant needs to rate statements from strongly agree to strongly disagree).
- Assign a role.
- Ask LLM given the role, to write an essay on the topic.
- Rate whether the author of the essay (strongly) agrees/disagrees.
- Tally up the results.