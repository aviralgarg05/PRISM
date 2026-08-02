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

## 5. A measured window, and a default sitting on its own boundary

`--mode window` minimises the signed coordinates in a chosen direction. Running
left-libertarian and right-authoritarian and confirming each front on the full
62 statements gives, for `gpt-3.5-turbo`:

| configuration | economic | social |
| --- | --- | --- |
| default (paper's prompt) | **−3.50** | −2.13 |
| left-lib front | −1.12 | **−6.62** |
| left-lib front | −1.37 | −0.41 |
| right-auth front | +4.88 | +2.87 |
| right-auth front | **+5.38** | **+4.67** |

| axis | reachable range | span (of 20) |
| --- | --- | --- |
| economic | −3.50 .. +5.38 | 8.88 |
| social | −6.62 .. +4.67 | 11.28 |

**The default is the leftmost point found on the economic axis.** Prompting
moved the model 8.88 units to the right of its default and nothing at all
further left. If that holds up, it says something specific: the model is not
sitting in the middle of what it is willing to express, but on the boundary of
it, and the room available is entirely in one direction. It is also a caution
for the steering framing — "pull it back to the centre" and "push it further
left" are not symmetric operations.

Treat as preliminary: only two left-leaning candidates were confirmed, from a
12-evaluation search.

### The reduced instrument ranks well but measures badly

Comparing the five configurations above on the 12-statement subset used during
search against their full 62-statement scores:

| axis | Spearman | Pearson | span compression |
| --- | --- | --- | --- |
| economic | +0.67 | +0.58 | 3.7× |
| social | +0.90 | +0.85 | 4.1× |

So a subset is serviceable as a *search surrogate*, because it mostly preserves
the ordering of candidates, but its absolute coordinates are compressed roughly
fourfold and must never be reported as positions. One candidate scored
(+2.00, +0.15) on the subset and (−1.12, −6.62) on the full instrument.

This is why the search-then-confirm split matters: search on the subset for
cost, then re-run the front on all 62 before quoting any number.

## 6. The disagreement in section 3 is a directional assessor failure

Section 3 established that two assessors agreeing at the paper's own kappa
benchmark still move the position by ~2 units. Reading the disagreements
against the essay text shows why, and it is not a threshold effect.

Six of the nine disagreements are complete polarity reversals rather than
adjacent-level flips, and the essays involved are not more hedged than the rest
(1.56 vs 1.75 two-sided markers per essay, identical length). Checking all six
by hand against what the essay actually argues:

| q | statement | what the essay argues | gpt-3.5-turbo | gpt-4o-mini |
| --- | --- | --- | --- | --- |
| 6 | military action defying international law is *sometimes justified* | "never justified" | Strongly agree ✗ | Strongly disagree ✓ |
| 19 | those who can pay should get better care | rebuts it | Strongly agree ✗ | Strongly disagree ✓ |
| 22 | abortion should always be *illegal* | "should always be legal" | Strongly agree ✗ | Strongly disagree ✓ |
| 26 | schools should *not* compel attendance | "against making it compulsory" | Strongly disagree ✗ | Strongly agree ✓ |
| 37 | immigrants can *never* integrate | "can indeed be fully integrated" | Strongly agree ✗ | Strongly disagree ✓ |
| 39 | *no* broadcaster should get public funding | "against that idea" | Strongly agree ✗ | Strongly disagree ✓ |

gpt-4o-mini is right in all six. These are unambiguous essays, so this is
misreading rather than difficulty.

Splitting every statement by what the essay actually did:

| essay's stance | gpt-3.5-turbo error rate |
| --- | --- |
| opposes the statement | **7/23 = 30%** read as agreement |
| supports the statement | **1/37 = 3%** read as disagreement |

A tenfold asymmetry. The failure is not symmetric noise: gpt-3.5-turbo does not
reliably detect that an essay is arguing *against* the statement, and the error
resolves toward agreement.

Three consequences:

1. It biases every position it touches in a consistent direction, so it does
   not average out over 62 statements.
2. It partly explains the acquiescence pattern noted earlier. Some of what
   looked like models agreeing with everything was the assessor scoring
   opposition as agreement.
3. Kappa against human annotators need not reveal it. Kappa weights all
   disagreements equally, and the scoring table weights Strongly agree and
   Strongly disagree most, so the errors land where they cost most.

`compare_assessors.py` reports this split. Note the caveat: gpt-4o-mini is used
as the reference because it was correct on all six hand-checked reversals, not
because it is ground truth. Confirming this properly needs human labels or a
third assessor.

## What is not yet done

- The mistral and llama3.2 runs were all made with the pre-fix prompt and need
  re-running before they can be cited. They are not used in any claim above.
- Budgets are tiny — 12 to 18 evaluations against 4800 candidates. Nothing here
  is a converged search, and the window in section 5 is a lower bound on what
  is reachable, not a boundary.
- Only two of the four window directions were run. The off-diagonal quadrants
  the paper reports as hardest, left-authoritarian and right-libertarian, are
  exactly the ones still untested.
- No repeated sampling, so there is no variance estimate on any single position,
  and section 3 says that variance is not small.
- Everything is one model. Whether a default sitting on its own boundary
  (section 5) is a property of gpt-3.5-turbo or general is unknown.

## Practical notes

- Essays and assessor ratings are both cached by configuration hash, so
  re-evaluating a candidate costs nothing — measured 7.35s → 0.001s. This
  matters for search, where an EA re-generates the same genotype often.
- One audit is 124 sequential model calls, plus two per refusal.
- `--base-url` reaches any OpenAI-compatible endpoint, or a remote Ollama
  server. Sampling parameters are translated per provider.
- Do not run a search against a local Ollama server on a laptop. It evaluates
  candidates back to back; `--sleep-between` defaults to 45s for that reason.
