# Findings from the first pass

Notes on getting the framework running and coupling it to pymoo. Everything
below is reproducible from this branch; configuration ids in brackets refer to
`out/ratings/`.

## 1. The default prompt was not the paper's prompt

`utils/prompt_variants.py` did not reproduce Appendix B, and the search space
could not express it:

- `DEFAULT_PROMPT_GENES` selected the stance fragment *"Pick the side that best
  aligns with your role and argue for it"*, which was sent even for no-role
  baseline runs — instructing the model to adopt a persona that did not exist.
- `STYLE` had no empty option, so all 3072 candidates carried a length
  instruction the paper never used.

This is not cosmetic. Auditing `gpt-3.5-turbo` with itself as assessor, no role,
all 62 statements:

| prompt | economic | social | agree : disagree |
| --- | --- | --- | --- |
| previous default | +0.005 | +1.69 | 57 : 4 |
| paper's prompt | **−3.50** | **−2.13** | **44 : 16** |

The paper places GPT-3.5-Turbo in the economically-left, socially-liberal
quadrant. Only the corrected prompt lands there. Since GPT-3.5-Turbo is in
Figure 3, this doubles as an end-to-end validation of the toolchain — it now
reproduces a published position, which it did not before.

Fixed by putting the Appendix B wording at index 0 of `STANCE` and `STYLE` and
defaulting all genes to 0, so a default run is a replication. Space is now 4800.

Two things generalise: a search cannot report how far prompting moves a model
from its default if the default is an unintended variant, and a prompt space
should always contain the published prompt as a reachable point.

## 2. The centre-seeking objective has a degenerate optimum

In `data/pc_lookup.csv`, **"Agree" scores exactly 0 on both axes for all 62
statements**. Only "Strongly agree", "Disagree" and "Strongly disagree" carry
weight. Consequences for `objective_zero_axes = |economic| + |social| + w·refusals`:

| strategy | economic | social | objective |
| --- | --- | --- | --- |
| always Agree | +0.38 | +2.41 | 2.79, no refusal penalty |
| always Disagree | −0.24 | −2.41 | 2.66, no refusal penalty |
| always Refuse | +0.38 | +2.41 | 2.79 + 62w |

Against an achievable range of ±10 on both axes. A prompt inducing bland
uniform agreement therefore scores well while expressing no position at all,
and "refuse everything" and "agree with everything" produce *identical*
coordinates, so position alone cannot distinguish them.

`evaluate_prism_config` now also returns the stance distribution, a normalised
`response_entropy` and `modal_share`, and the search constrains on refusal
count and entropy so these optima are infeasible rather than optimal.

## 3. Assessor choice moves the position by about as much as prompting does

The same 62 essays (config `2b78d1d74d`), scored by two assessors:

| assessor | economic | social |
| --- | --- | --- |
| gpt-3.5-turbo | −3.50 | −2.13 |
| gpt-4o-mini | **−5.25** | **−4.18** |

Agreement between them is 87.1%, **Cohen's kappa 0.761** — statistically
indistinguishable from the 0.774 reported in the paper for GPT-3.5-Turbo
against two human annotators. The assessors agree as well as the paper's
assessor agreed with humans, and the position still moves ~1.75 economic and
~2.05 social.

The mechanism: 6 of the 8 disagreements are complete polarity reversals between
"Strongly agree" and "Strongly disagree" (q6, q19, q22, q37, q39, q62), the two
highest-weight responses. Kappa weights every disagreement equally; the scoring
does not, so a few high-leverage flips dominate the tally.

**Kappa at the paper's own benchmark is sufficient for label agreement but not
for position stability.** `compare_assessors.py` reproduces this.

## 4. The search works, and prompting does move the model

NSGA-II over the fragment space. Target and assessor `gpt-3.5-turbo`,
12 statements spread across the instrument, population 6 × 3 generations.

| | economic | social | \|e\|+\|s\| | entropy |
| --- | --- | --- | --- | --- |
| baseline, paper's prompt (seeded) | −0.24 | +2.20 | 2.44 | 0.35 |
| best found | +0.13 | **+0.46** | **0.59** | 0.83 |

So yes — the position can be steered, here by 1.74 on the social axis. The
winner is not degenerate: entropy *rose* from 0.35 to 0.83, so answers became
more varied rather than more uniform. The winning combination was "Begin by
stating your stance, then explain it briefly" + "Do not promote harm; instead,
explain the political reasoning behind the stance" + "Avoid ideological
extremes where a moderate interpretation is reasonable".

**But sections 3 and 4 must be read together: the 1.74 steering effect is the
same order of magnitude as the ~2-unit shift from merely changing assessor.**
Until assessor variance is controlled, part of any measured steering may be
measurement noise. Suggested remedy: score each candidate with several
assessors and report a variance band on the front.

An earlier run failed to beat the baseline, for two harness reasons now fixed:
the baseline was never sampled into the population, and `--max-questions` took
a *prefix* of the instrument. The prefix matters — `gpt-3.5-turbo` scores
economic −0.12 on the first 12 statements but −3.50 on all 62, because the
opening statements carry almost no economic weight, so the search was
optimising something close to noise on that axis. Subsets are now spread evenly.

## What is not yet done

- The mistral and llama3.2 runs were all made with the pre-fix prompt and need
  re-running before they can be cited. They are not used in any claim above.
- Only `--mode centre` has been exercised; `--mode window` is implemented but
  untested, so the reachable-region result does not exist yet.
- Budgets so far are tiny (18 evaluations against 4800 candidates). Nothing
  here should be read as a converged search.
- No repeated sampling, so there is no variance estimate on any single position.

## Practical notes

- Essays and assessor ratings are both cached by configuration hash, so
  re-evaluating a candidate costs nothing — measured 7.35s → 0.001s. This
  matters for search, where an EA re-generates the same genotype often.
- One audit is 124 sequential model calls, plus two per refusal.
- `--base-url` reaches any OpenAI-compatible endpoint, or a remote Ollama
  server. Sampling parameters are translated per provider.
- Do not run a search against a local Ollama server on a laptop. It evaluates
  candidates back to back; `--sleep-between` defaults to 45s for that reason.
