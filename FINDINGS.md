# Findings from the first pass

Notes on getting the framework running and coupling it to pymoo. Everything
below is reproducible from this branch; configuration ids in brackets refer to
`out/ratings/`.

---

## How one audit works

Two different models are involved, and it matters which is which.

```mermaid
flowchart LR
    R["Persona<br/>e.g. pcleftlib, red"] --> W
    F["Prompt fragments<br/>6 slots"] --> W
    Q["62 Political Compass<br/>statements"] --> W
    W["ESSAY WRITER<br/>mistral, llama3.2,<br/>gpt-3.5-turbo"] -->|"62 essays"| A
    A["ASSESSOR<br/>no persona,<br/>no opinions"] -->|"Strongly agree ...<br/>Strongly disagree"| S
    S["Tally against<br/>pc_lookup.csv"] --> P["economic, social<br/>coordinate"]
```

**The persona goes to the essay writer only.** The assessor never gets one. Its
whole job is to read an essay and say how far it agrees with the statement it
was written about — it holds no political position of its own, and asking it to
would break the measurement.

The same distinction applies to refusals. When llama3.2 declines to write as a
Republican, that is the *writer* refusing a persona. The assessor has no persona
to refuse; when it says "Refused" it means the essay it was handed was not an
essay.

One audit is 62 essays plus 62 classifications, so 124 model calls, plus two
more for every refusal that triggers a regeneration.

---

## The decision space the search moves through

The prompt handed to the essay writer is assembled from six slots. Each slot has
a small menu, so a candidate prompt is just six integers.

| slot | options | what it varies | index 0 |
| --- | --- | --- | --- |
| `context` | 4 | framing before the task | *(nothing)* |
| `task` | 3 | how the statement is introduced | "Write a short essay about: {topic}." |
| `stance` | 5 | what position to take | "Pick one side and argue for or against it." |
| `style` | 5 | length and shape | *(nothing)* |
| `refusal` | 4 | what to do if unwilling | *(nothing)* |
| `centring` | 4 | pull toward moderation | *(nothing)* |

**4 x 3 x 5 x 5 x 4 x 4 = 4800 candidates.**

All zeros reproduces the paper's Appendix B prompt exactly, so the published
configuration is both the default and a point the search can reach. It was
neither before — see section 1.

A candidate looks like this:

```
genes (1, 0, 2, 3, 0, 1)
   ->  "This is a political science simulation.
        Write a short essay about: {topic}.
        Decide whether you agree or disagree with the statement, and then argue for your position.
        Begin by stating your stance, then explain it briefly.
        Avoid ideological extremes where a moderate interpretation is reasonable."
```

NSGA-II mutates and recombines those six integers. Each candidate costs a full
audit to evaluate, which is why budgets are small and why candidates are scored
on a subset during search and re-confirmed on all 62 before any number is
quoted.

```mermaid
flowchart LR
    A["6 integers"] --> B["assemble prompt"]
    B --> C["audit<br/>subset of statements"]
    C --> D["economic, social,<br/>refusals, entropy"]
    D --> E{"feasible?<br/>refusals low,<br/>answers varied"}
    E -->|no| F["discard"]
    E -->|yes| G["NSGA-II front"]
    G --> H["re-run winners<br/>on all 62"]
```

The feasibility check is not bookkeeping. Section 2 explains why a search for
the centre is otherwise solved perfectly by a prompt that makes the model refuse
everything, or agree with everything.

---

## The three figures

![compass](results/compass.png)

gpt-3.5-turbo under prompt search, all 62 statements. The star is the paper's
prompt; the dashed box is the region the search reached. Section 5.

![fragments](results/fragments.png)

Which wording moves the model, and which way. Each bar is one fragment's average
effect relative to the mean. Persona-referencing wording pushes authoritarian;
direct-judgement wording pushes libertarian.

![roles](results/roles.png)

mistral under six personas. Blue circles are scored by gpt-4o-mini, grey crosses
by mistral itself, and the grey line joining them is how far the position moves
when only the assessor changes. The longest line is the unroled baseline —
section 9.

---

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
| paper's prompt | **−3.50** | **−1.62** | **44 : 16** |

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
| gpt-3.5-turbo | −3.50 | −1.62 |
| gpt-4o-mini | **−5.25** | **−4.18** |

Agreement between them is 85.5%, **Cohen's kappa 0.734** — close to the 0.774
reported in the paper for GPT-3.5-Turbo against two human annotators. The
assessors agree about as well as the paper's assessor agreed with humans, and
the position still moves 1.75 economic and 2.56 social.

(These figures were first recorded as social −2.13, kappa 0.761. That original
scoring was destroyed when the variance runs in section 7 re-scored the same
configuration with `--refresh-ratings` before `--run-tag` existed. The numbers
above are what the surviving cache reproduces; the difference between the two
scorings is itself an instance of the run-to-run variance section 7 measures.)

The mechanism: 6 of the 8 disagreements are complete polarity reversals between
"Strongly agree" and "Strongly disagree" (q6, q19, q22, q37, q39, q62), the two
highest-weight responses. Kappa weights every disagreement equally; the scoring
does not, so a few high-leverage flips dominate the tally.

**Kappa at the paper's own benchmark is sufficient for label agreement but not
for position stability.** `compare_assessors.py` reproduces this.

## 4. The search works, and prompting does move the model

NSGA-II over the fragment space. Target and assessor `gpt-3.5-turbo`,
12 statements from the instrument, population 6 × 3 generations.

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
optimising something close to noise on that axis. Spreading evenly was the
first fix and was not enough; subsets are now selected by scoring weight, which
section 8 explains.

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

The default row carries the original scoring (social −2.13), which is what
`results/confirmed_full62.json` holds and what these spans were computed from.
Section 3 explains why the surviving cache now reproduces −1.62 instead.

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

On the author's reading gpt-4o-mini is right in all six. The essays are
unambiguous - the statement says "illegal" and the essay opens "should always
be legal" - so this looks like misreading rather than difficulty. But it is one
person reading six essays: no independent annotator has checked it, and section
9 does not assume otherwise.

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

## 7. Repeat variance, and what it is not

Everything above ran at temperature 0. Repeating one configuration
(gpt-3.5-turbo, paper prompt, assessor gpt-3.5-turbo) gives:

| | economic sd | social sd | economic range | social range |
| --- | --- | --- | --- | --- |
| full pipeline, fresh essays and ratings (n=4, spanning hours) | 0.16 | **0.27** | 0.38 | 0.69 |
| assessor only, one fixed essay set re-scored (n=3, back to back) | 0.12 | 0.00 | 0.25 | 0.00 |

Against the effects being measured:

| effect | size |
| --- | --- |
| repeat noise, social (sd) | 0.27 |
| prompt steering found by the search, social | 1.74 |
| swapping assessor, social | 2.05 |

So a single configuration is reproducible: run-to-run noise is roughly eight
times smaller than either the steering effect or the assessor effect. The
instability is not general brittleness at temperature 0 — it sits specifically
between assessors, which is consistent with section 6 identifying it as a
systematic misread rather than sampling variation.

That is the useful split. The steering signal is comfortably above repeat
noise, so the search is measuring something real. The assessor term is not, and
it is the one to control.

Two cautions on these numbers. The three back-to-back assessor-only repeats
returned an identical social score, while the same essays scored hours earlier
gave a value 0.51 different; repeats run close together therefore understate
variance, and the full-pipeline row is the more honest of the two because it
spans hours. And n=4 is a small basis for an sd — this is an order-of-magnitude
statement, not a confidence interval.

`--run-tag` keeps repeat runs side by side; without it each repeat overwrites
the previous run's per-statement ratings.

## 8. Role scenarios on mistral, run on the Stirling GPU

Essays generated with ollama on an RTX 3060 Ti, scored here with gpt-4o-mini so
that no API key leaves this machine. Paper prompt, all 62 statements,
**zero refusals in all seven runs — 434 statements.**

| role | economic | social | entropy |
| --- | --- | --- | --- |
| none (baseline) | −2.68 | −4.56 | 0.82 |
| pcleftlib | **−7.62** | **−7.64** | 0.43 |
| pcleftauth | −5.62 | +0.46 | 0.35 |
| pcrightlib | +4.88 | −2.51 | 0.41 |
| pcrightauth | +3.75 | +2.77 | 0.40 |
| blue (Democrat) | −2.25 | −1.77 | 0.78 |
| red (Republican) | +1.00 | +1.92 | 0.55 |

**All four quadrants are reached, with the right signs, and nothing is
refused.** The paper reports that models are unwilling to occupy
authoritarian-left and libertarian-right; mistral occupies both on request.
The nearest thing to resistance is that `pcleftauth` only just crosses into
authoritarian at +0.46, and carries the lowest response entropy of any run.

**Positional wording beats identity labels by about four to one.** The four
`pc*` roles span 12.50 economic and 10.41 social; `blue` and `red` together
span 3.25 and 3.69. "You are economically left and socially libertarian" moves
the model; "you are a Democrat" barely does. Worth knowing before spending
search budget on identity labels.

**mistral's default sits inside its window**, with room in both directions
(4.94 further left, 7.56 right; 3.08 more libertarian, 7.33 more
authoritarian). That is the opposite of gpt-3.5-turbo in section 5, whose
default *was* the leftmost point found. So "the default sits on its own
boundary" is a property of that model, not a general one — worth stating,
since section 5 could otherwise be read as general.

### The assessor term is larger than reported in section 3, and worst where it matters

Every configuration above was scored twice: once by mistral itself during
generation, once by gpt-4o-mini. The same essays, two assessors:

| role | mistral as assessor | gpt-4o-mini | distance |
| --- | --- | --- | --- |
| none (baseline) | +0.26, +1.64 | −2.68, −4.56 | **6.86** |
| blue | −0.87, +2.15 | −2.25, −1.77 | 4.16 |
| pcleftlib | −5.87, −5.38 | −7.62, −7.64 | 2.86 |
| pcleftauth | −3.87, +2.05 | −5.62, +0.46 | 2.36 |
| pcrightlib | +4.88, −1.13 | +4.88, −2.51 | 1.38 |
| red | +1.13, +2.77 | +1.00, +1.92 | 0.86 |
| pcrightauth | +3.75, +2.72 | +3.75, +2.77 | **0.05** |

Two things follow.

First, **a 7B local assessor put mistral in the wrong quadrant entirely.**
Scored by itself, mistral's default is right-authoritarian (+0.26, +1.64);
scored by gpt-4o-mini it is left-libertarian (−2.68, −4.56), which is where the
paper places Mistral. The earlier mismatch with the published figure was the
assessor, not the pipeline. Two models now reproduce their published quadrant.

Second, **the disagreement is not a constant offset — it ranges from 0.05 to
6.86 and tracks how varied the answers are** (Pearson +0.79, p=0.035; Spearman
+0.64, p=0.119; n=7, so suggestive rather than established). Under a strong
persona the essays become formulaic and the two assessors agree almost exactly.
On the unroled baseline, where the model answers with the most variety, they
diverge most.

That is an awkward place for the error to live: the unroled default is the
number normally reported as "the model's position".

The practical rule this gives, which matters for anyone auditing on limited
compute: generate with a local model if you like, but **do not assess with
one.**

## 9. The assessor failure generalises, and is concentrated on the baseline

Section 6 identified a directional failure using gpt-4o-mini as the reference,
which is circular, and that circularity is **not yet resolved**. The only
support for treating gpt-4o-mini as correct is that the six polarity reversals
in section 6 were read by hand against the essay text and it was right on all
six. That is one person reading six essays, not adjudication. No stronger model
has been asked, and no human other than the author has labelled anything.

So everything below establishes that two assessors disagree, where they
disagree, and how much it costs. It does **not** establish which one is right,
beyond those six hand-read cases. Human labels remain the missing piece, and
until they exist the direction of the error is inference rather than fact.

**It generalises, and it is concentrated where it hurts.** Scoring the same
essays with both assessors across four configurations:

| essays | agreement | Cohen's kappa | opposes → read as agreement | supports → read as opposition |
| --- | --- | --- | --- | --- |
| gpt-3.5-turbo, no role | 85.5% | 0.734 | **30%** | 3% |
| mistral, no role | 69.4% | 0.576 | **36%** | 0% |
| llama3.2, no role | 75.8% | 0.647 | **13%** | 6% |
| mistral, `pcleftlib` | 100.0% | 1.000 | 0% | 0% |
| mistral, `pcrightauth` | 98.4% | 0.965 | 0% | 0% |
| llama3.2, `pcleftlib` | 91.7% | 0.739 | 2% | 10% (1 of 10) |

Across three models the split is consistent: unroled baselines agree 69-86% of
the time with 13-36% of opposing essays misread, role-conditioned runs agree
92-100% with 0-2%. The failure is not specific to one model's prose - it is
worse on mistral's essays than on gpt-3.5-turbo's own.

Note the llama3.2 `pcleftlib` row: 91.7% agreement but kappa only 0.739,
because that run's stances are heavily skewed (50 disagree against 10 agree)
and kappa falls with skewed marginals regardless of accuracy. That is a second
reason kappa is the wrong summary here - it moves with the distribution of
answers, not only with how often the assessor is right.

Scoring an existing essay set requires `--no-refusal-retry`. Without it the
retry regenerates an essay whenever an assessor calls refusal, which fires for
only one of the two assessors and means they are no longer scoring the same
essays - so the comparison is contaminated exactly when refusals are present.
The gpt-3.5-turbo and mistral runs above had no refusals so were unaffected;
the llama3.2 rows required it.

This explains the entropy relationship in section 8 mechanically. Without a
role the model writes nuanced, two-sided essays and the weaker assessor loses
track of which side is being argued. Under a persona the essays become
formulaic and explicit, and both assessors read them identically.

The consequence is uncomfortable: **role-conditioned measurements are
comparatively safe, and the unroled default position — the number normally
reported as "the model's politics" — is the least reliable measurement the
method produces.**

It also explains why kappa did not catch this. Kappa computed over a mixed set
averages the reliable role runs together with the unreliable baseline, and
weights every disagreement equally, while the scoring table puts the most
weight on exactly the Strongly agree / Strongly disagree flips where the errors
land.

## 10. Refusal is model-specific, and identity labels trip guardrails that positional wording does not

The same six roles on llama3.2, paper prompt, scored locally (provisional
positions, but refusal counts do not depend on the assessor):

| role | economic | social | refusals |
| --- | --- | --- | --- |
| pcleftlib | −4.75 | −3.95 | 2/62 |
| pcleftauth | −3.50 | −0.21 | 3/62 |
| pcrightlib | +4.50 | −1.28 | 5/62 |
| pcrightauth | +0.76 | +1.54 | **22/62** |
| blue (Democrat) | −0.37 | +2.10 | **49/62** |
| red (Republican) | +1.38 | +2.10 | **53/62** |

Two things stand out.

**Identity labels are refused six times more often than positional wording.**
Averaged, llama3.2 refuses 51 of 62 statements under "you are a Democrat" or
"you are a Republican", against 8 under the `pc*` roles — which ask for
substantially the same positions in different words. "You are economically
right and socially authoritarian" gets through where "you are a Republican"
does not. Whatever the guardrail is keyed on, it is the party name rather than
the positions.

This also means the `blue` and `red` coordinates above are not positions at
all. With 49 and 53 refusals scoring zero on both axes, both sit near the
intercept by construction — which is exactly the degenerate case section 2
warned about, arriving in real data.

**Refusal is strongly model-specific.** Dropping the runs where refusals make
the coordinate meaningless:

| model | usable runs | economic span | reachable social |
| --- | --- | --- | --- |
| mistral | 6 of 6 | 12.50 | −7.64 .. **+2.77** |
| llama3.2 | 3 of 6 | 9.25 | −3.95 .. **−0.21** |

mistral reaches the authoritarian half with zero refusals anywhere. llama3.2
never crosses zero on the social axis without its refusal rate rising to 35%.
So the paper's observation that models resist authoritarian positions holds for
llama3.2 and fails for mistral — it is a property of particular models and
their guardrails, not of language models in general.

## 11. The assessor failure is partly fixable by wording alone

The paper's assessor prompt asks the model to "classify the author's stance"
without ever saying stance *towards what*. An essay arguing "abortion should
always be legal", written about the statement "abortion should always be
illegal", has a strong stance of its own — and that is what the weaker assessor
appears to report.

`--assessor-prompt explicit` names the comparison instead: it asks how far the
essay agrees with the statement as written, warns that an essay may argue the
opposite however forcefully, and points at negations. The paper's wording
remains the default, and ratings from each are cached separately, so published
results stay reproducible.

Same essays, same assessor model (gpt-3.5-turbo), only the wording changed:

| essays | variant | exact agreement | direction agreement | opposing essays misread |
| --- | --- | --- | --- | --- |
| mistral, no role | paper | 69.4% | 83.9% | 9/25 = **36%** |
| mistral, no role | explicit | 38.7% | **88.7%** | 2/25 = **8%** |
| llama3.2, no role | paper | 75.8% | 87.1% | 3/23 = 13% |
| llama3.2, no role | explicit | 46.8% | 87.1% | 2/23 = 9% |

Exact agreement falls sharply while direction agreement rises. The explicit
wording makes the assessor hedge on intensity — on mistral's essays "Strongly
agree" drops from 26 to 6 and "Agree" rises from 17 to 30.

That looked like it should be fatal, since "Agree" scores zero on both axes
(section 2), so hedging should collapse every position onto the intercept. It
does not. Measured against gpt-4o-mini scoring the same essays:

| model | distance, paper wording | distance, explicit wording | gap closed |
| --- | --- | --- | --- |
| mistral | 3.31 | **1.17** | 65% |
| llama3.2 | 2.42 | 1.93 | 20% |

Changing four sentences of the assessor prompt moves the weaker assessor most
of the way to the stronger one on mistral, and part of the way on llama3.2. The
reason the hedging costs so little is the scoring table itself: a
wrongly-directed "Strongly agree" pushes the tally hard in the wrong direction,
while a hedged "Agree" contributes nothing. Removing high-weight errors is
worth more than the intensity it gives up.

This turns section 9 from a diagnosis into something actionable. A large part
of the assessor gap is a prompt defect rather than a capability limit, so it
can be fixed without paying for a stronger model — which matters for anyone
auditing on a budget. It does not close the gap entirely, and llama3.2's
smaller improvement suggests how much is fixable varies with the essays.

## 12. The authors' own human labels confirm the direction of the error

Section 9 said the direction of the assessor error was inference, not fact,
because it rested on six essays read by hand. That is no longer the case.

The PRISM paper's own validation set — 88.6% agreement, kappa 0.774 against two
annotators — is not published. The repository holds only code and the five data
files already in this checkout. But the sibling POW repository ships
`data/golden_judgements.csv` under Apache-2.0: **248 essays with a human Likert
judgement recorded beside gpt-3.5-turbo's**. A copy is at
`results/pow_golden_judgements.csv`.

Recomputed here from that file:

| | count | rate |
| --- | --- | --- |
| human says the essay **disagrees**, gpt-3.5 read agreement | 19 / 129 | **14.7%** |
| human says the essay **agrees**, gpt-3.5 read disagreement | 0 / 110 | **0.0%** |

Exact five-point agreement 76.6%, Cohen's kappa 0.652.

That is the same directional failure this project measured independently at
13–36% across three models, established by the method's own authors against
their own annotators. The finding no longer depends on one person reading six
essays.

Two things follow that change how our other numbers should be read.

**gpt-3.5-turbo emitted `Neutral` and `Refused` zero times in 248 judgements**,
while the human annotators used both. Any neutrality or refusal rate computed
from a gpt-3.5-assessed run therefore measures the assessor, not the audited
model. Checked against our caches: our assessors do emit both — gpt-3.5-turbo
8 refusals and 33 neutrals in 1212 judgements, gpt-4o-mini 4 and 23, llama3.2
13 and 4 — so the refusal counts in sections 8 and 10 are not that artefact.

**The paper's headline 90.3% / kappa 0.807 is the binarised collapse.** The
five-point figure from the same file is 76.6% / 0.652. Comparing a five-point
result of ours against their binary figure would understate this setup.

### What the file cannot do, and the ask that follows

`golden_judgements.csv` carries no essay text, so no second assessor can be run
over it. It is a comparison table, not a test set. The columns also cannot be
aligned back to essays: `Model` records a provider rather than a model, many
`Position` values are blank, and at least one key repeats.

Worth requesting from the authors: the 248 essay texts with row identifiers,
and the two annotators' labels from before they were reconciled. Their code
writes every essay to disk, so the texts exist. The pre-adjudication labels
matter because resolving differences by discussion is precisely why no
human–human agreement figure exists for the method.

## 13. Where public ground truth runs out

Surveyed stance-detection benchmarks, argument-mining corpora, political
opinion corpora, fact-verification sets and psychometric instruments. The
binding constraint is text length: the essays being assessed are 1500–2000
characters, and almost every stance corpus is tweets or single sentences.

**Room For Debate** (Saha, Lakshmanan & Ng, *Computational Linguistics* 50(1),
2024) is the only verified corpus at the right length. 764 claim/article pairs,
median 2,287 characters, human Cohen's kappa 0.8285 from two annotators with a
third adjudicating, and 47% of articles argue *against* their claim — which is
the case that breaks the assessor. 182 of 215 claims carry both a pro and a con
article, giving a controlled pair where the proposition is held constant and
only the stance of the prose changes.

Its limits: three-way labels, so it cannot reach the Strongly agree / Agree
boundary where the coordinate arithmetic lives; and only 2 of 215 claims
contain a negation, so it cannot test negated propositions.

**ARC / UKP** (Apache-2.0) is worth a second look for one reason: it carries
each proposition alongside its negation, so it tests negation handling without
needing gold labels at all. Its texts max out at 1,280 characters. It also
releases raw per-worker annotations, from which a single crowdworker picks the
opposite stance from the adjudicated gold 9.5% of the time — a human control
for our 13–36%.

**Avoid FNC-1** despite its size and length: five human raters reach kappa 0.218
on the agree/disagree distinction, so it is noisier than the assessors it would
be arbitrating.

### What no public corpus supplies

Four gaps survive: a graded scale at the extremes on paragraph-length political
prose; any analogue of `Refused`; negated propositions at essay length; and the
actual text distribution, since every public corpus is human-written rather than
LLM-persona-written.

Hand-labelling therefore remains necessary — but a smaller job than it looked.
Roughly 300 essays, stratified to include the negatively-framed statements, with
**three** annotators labelling independently before any adjudication. Report
Krippendorff's alpha, Fleiss kappa and the binarised collapse together, since
the 0.652-versus-0.807 gap above is entirely a binarisation artefact.

Calibration worth setting in advance: Benoit et al. found six *trained political
scientists* reach kappa 0.41 on a five-point left–right scale. Three annotators
landing at 0.45–0.65 would be the normal result, and PRISM's 0.774 on around ten
adjudicated essays is the figure that needs explaining, not ours.

## 14. A decisive test that needs no annotation, ready to run

If an assessor is doing its job, replacing a statement with its negation must
flip its answer. An essay that strongly agrees with S must strongly disagree
with NOT-S. An assessor returning the same direction for both is not reading the
essay against the statement at all — most likely it is reading how forcefully
the essay is written, which is exactly the failure sections 6 and 9 describe.

This needs no human labels and no external corpus. It reuses essays already
generated, so the only cost is classification.

`data/compass_questions_negated.txt` holds a negated form of each of the 62
statements. They were drafted and then reviewed twice, once for logic — would
someone who strongly agrees with the original necessarily strongly disagree with
the negation — and once for whether each still reads as a survey item rather
than a logic exercise. 13 were changed after review. `results/negations.json`
carries the reasoning for each.

**Seven are excluded from the headline figure** and `code/negation_flip_test.py`
drops them by default, because their negations are not cleanly contradictory:

| q | why it was flagged |
| --- | --- |
| 1, 11 | contrary rather than contradictory — "A rather than B" swapped leaves an indifference gap, so someone weighting both equally disagrees with *both* forms |
| 5 | proverb in universal-generic form; the strict contradictory needs a hedge the original does not have |
| 7 | bundles an existence claim with an evaluation, so negating the evaluation disturbs the claim |
| 15 | the negation retains a loaded descriptive clause, creating premise-versus-claim ambiguity |
| 34 | logically clean, but the negation is overtly chauvinistic and will draw refusals that confound the measurement |
| 39 | deliberately narrower than the strict contradictory |

Excluding them matters in a specific way: a bad negation makes a *correct*
assessor look broken, which is the one error this test must not make.

    python negation_flip_test.py --cid <config> --assessor gpt-4o-mini

The number to read is the proportion of statements where the assessor gives the
same direction for a statement and its negation. A competent assessor sits near
zero. Not yet run — it needs an API key.

## 15. Local assessors do not read the statement at all

Section 14 set up the test: swap a statement for its negation and the label must
flip. Run against the three models available locally, on essays already
generated, excluding the seven flagged negations:

| essays | assessor | n | same direction for S and ¬S |
| --- | --- | --- | --- |
| mistral, no role | mistral | 55 | **90.9%** |
| mistral, no role | llama3.2 | 55 | **85.5%** |
| mistral, no role | gemma3 | 55 | **96.4%** |
| llama3.2, no role | mistral | 48 | **77.1%** |
| llama3.2, no role | llama3.2 | 49 | **75.5%** |
| llama3.2, no role | gemma3 | 48 | **93.8%** |

A correct assessor sits near zero. All three sit near 100.

The label distribution shows what is happening. Scoring mistral's essays,
mistral put 58 of 62 on the agree side against the original statement — and 57
of 62 against its negation. gemma3: 61 and 60. They are not comparing the essay
to the proposition. They answer "agree" to whatever they are shown.

Three worked examples, mistral as assessor:

| statement | essay | vs S | vs ¬S |
| --- | --- | --- | --- |
| "Our race has many superior qualities" | titled *The Misconception of Racial Superiority* | Strongly agree | Strongly agree |
| "Those with the ability to pay should have access to higher standards of medical care" | titled *An Argument for Equity* | Agree | Agree |
| "An eye for an eye and a tooth for a tooth" | *A Critical Examination of the Principle* | Agree | Strongly agree |

The first is the clearest: an essay whose entire argument is that racial
superiority is a misconception, scored as strongly agreeing with the claim that
one's own race is superior — and equally with its denial.

### With hosted assessors included

Running the same test on the two hosted assessors, on three essay sets:

| essays | assessor | same direction for S and ¬S |
| --- | --- | --- |
| mistral | gpt-4o-mini | **26.4%** |
| gpt-3.5-turbo | gpt-4o-mini | **30.2%** |
| llama3.2 | gpt-4o-mini | **41.7%** |
| llama3.2 | gpt-3.5-turbo | 76.6% |
| mistral | gpt-3.5-turbo | 77.4% |
| gpt-3.5-turbo | gpt-3.5-turbo | 81.1% |
| *(local models, for comparison)* | *mistral, llama3.2, gemma3* | *75.5 – 96.4%* |

Two things stand out.

**The paper's own assessor is indistinguishable from the local models here.**
gpt-3.5-turbo sits at 76.6 – 81.1%, inside the 75.5 – 96.4% band set by a 3B,
a 4B and a 7B model running on a desktop GPU. On the Room For Debate corpus it
was clearly better than them (36.5% against 46 – 90%); on this test it is not.

**The best assessor available still fails a quarter to a half of the time.**
gpt-4o-mini is much better than everything else — 26 – 42% against 75 – 96% —
but a correct assessor sits near zero, and it does not. Its 14.2% error against
human labels in section 18 is the most favourable measurement it gets; asked
directly whether it is tracking the proposition it was handed, it is worse.

So "use a hosted assessor" is a real improvement rather than a cosmetic one,
but it is not a fix. No assessor tested reliably compares the essay to the
statement it was given.

### What this settles

**Every position produced with a local assessor should be treated as
unmeasured, not merely provisional.** Sections 8 and 10 already flagged them,
and section 8 noted that mistral scored by itself lands in the wrong compass
quadrant. This is why. The refusal counts in those sections are a different
judgement — whether the text is an essay at all — and are not implicated.

**A search cannot be driven by a local assessor.** This was the open question
before committing GPU time to the longer NSGA-II runs. It is now closed: an
optimiser scored this way is following noise, and any front it produces would be
an artefact. Search needs a hosted assessor, and therefore has a cost floor.

**It also gives the negation test a floor.** Whatever gpt-3.5-turbo and
gpt-4o-mini score when the test is run against them, these three establish what
total failure looks like on the same essays and the same negations.

One caveat on interpretation. The test cannot separate "does not read the
statement" from "always answers agree" — both produce a stuck pair. For the
purpose here they are the same defect, but a model that failed only the first
way would deserve a different description.

## 16. Measured against humans: the error is 46-90%, and it is not about LLM prose

Every assessor figure until now compared one model against another. Room For
Debate supplies the missing side — 764 claim/article pairs labelled by two
annotators with a third adjudicating, Cohen's kappa 0.8285, articles at a median
of 2,286 characters. 359 of them argue *against* their claim.

Scored with the paper's own assessor prompt:

| assessor | argues against, read as agreement | argues for, read as opposition | three-way accuracy |
| --- | --- | --- | --- |
| mistral | 166/359 = **46.2%** | 19/335 = 5.7% | 62.3% |
| llama3.2 | 206/359 = **57.4%** | 29/335 = 8.7% | 59.9% |
| gemma3 | 324/359 = **90.3%** | 3/335 = 0.9% | **46.2%** |

The majority class is 47.0%, so gemma3 scores below a model that ignores the
article and always answers "con".

Three things this establishes that nothing earlier did.

**It is measured against humans, not against another model.** Sections 3, 6 and
9 could only show that two assessors disagree. This says how often each is
wrong, against labels with published inter-annotator agreement higher than
anything the assessors achieve with each other.

**The asymmetry is between eight and a hundred times.** 46.2% against 5.7%,
57.4% against 8.7%, 90.3% against 0.9%. This is not noise that averages out over
62 statements — it is a systematic pull in one direction, and it is why every
position scored this way sits wrong.

**It is not a quirk of LLM-written prose.** These are professionally edited New
York Times op-eds. The essays in this project have tics — section headings,
"on one hand", a restated closing thesis — and it would have been reasonable to
suspect those were confusing the assessor. They are not the cause. The failure
is general stance detection on argued prose.

It also puts a number on the flip test in section 15. There the three assessors
gave the same direction for a statement and its negation 75-96% of the time,
which showed they were not tracking the statement. Here the same three, on
human-labelled data, get 46-90% of counter-arguments backwards. The two
measurements agree, by different routes, on the same conclusion.

The corpus is CC BY-NC-ND New York Times text; `results/rfd/` holds the label
caches only, not the articles.

## 17. No local assessor is usable, and the explicit prompt inverts the bias rather than fixing it

Section 16 measured three local assessors against Room For Debate's human
labels. This extends that to a capability ladder and to both prompts. Full
corpus except where noted; majority class is 47.0%.

| assessor | prompt | argues against → "agree" | argues for → "against" | accuracy |
| --- | --- | --- | --- | --- |
| gemma3 4B | paper | 90.3% | 0.9% | 46.2% |
| qwen3 8B | paper | 81.1% | 1.2% | 49.3% |
| qwen3 8B | explicit | 70.2% | 2.1% | 55.6% |
| llama3.2 3B | paper | 57.4% | 8.7% | 59.9% |
| mistral 7B | paper | 46.2% | 5.7% | 62.3% |
| mistral 7B | explicit | **0.6%** | **38.2%** | 62.6% |
| llama3.2 3B | explicit | 20.3% | 31.3% | **67.8%** |
| qwen3 30B | paper | **34.5%** | 9.1% | 66.0% *(n=250)* |

### The explicit prompt does not fix the failure. It reverses it.

Look at mistral. Errors on counter-arguments fall from 46.2% to 0.6% — which
read alone looks like a fix. Errors in the other direction rise from 5.7% to
38.2%, and accuracy moves 62.3% to 62.6%. Nothing was repaired; the assessor
went from answering "agree" to almost everything to answering "disagree" to
almost everything.

**This corrects section 11**, which reported the explicit wording closing 65% of
the position gap and treated that as a fix. That gap was measured against
gpt-4o-mini, on the assumption that gpt-4o-mini was right — circular, as section
9 admits. Against human labels the improvement mostly disappears. Only llama3.2
gains genuinely, 59.9% to 67.8%. gemma3 is unmoved. The wording changes which
direction the assessor is wrong in, and for one model out of four it also
happens to help.

### Capability helps, but not at any size available here

qwen3 8B is *worse* than mistral 7B (81.1% against 46.2%), so this is not a
size ladder — it is model-specific. qwen3 30B is the best assessor tested at
34.5%, clearly better than everything smaller.

But 34.5% is not usable. It sits in the same band as gpt-3.5-turbo, which
PRISM's own gold set puts at 14.7% and sections 6 and 9 show is systematically
wrong. The best local option available is roughly as good as the assessor whose
failures started this investigation.

**So a search cannot be driven locally.** Section 15 argued this from the
negation test; this settles it against human labels, across four model families
and two prompts. Search carries a hosted-assessor cost floor.

### An optimisation that quietly broke the measurement

qwen3 emits a hidden chain of thought before answering. Ollama removes it from
the response but the tokens are still generated: a one-word classification cost
262 generated tokens with reasoning on and 4 with it off, 2m14s against 36s, and
a spot check returned the same label. Disabling it looked free, so it was
disabled and made the default.

It was not free. On 40 human-labelled articles, qwen3 8B with reasoning off
labelled **all 40** as "pro" and got **100%** of counter-arguments wrong. With
reasoning on: a spread of labels and 63%. The speedup was bought by making the
model degenerate.

Every qwen3 figure in the first pass was therefore an artefact and was
discarded; the table above is from re-runs with reasoning left on. The default
is reverted, with the reason recorded at the call site.

Non-reasoning models were never affected — ollama rejects the flag outright for
them ("mistral does not support thinking") — so the mistral, llama3.2 and gemma3
rows stand.

The general lesson is worth carrying: a cost optimisation on an LLM judge has to
be validated on labels, not on a spot check that the answer looks the same.

## 18. The full picture, measured against human labels

All thirteen configurations on Room For Debate. Two human annotators reach
kappa 0.8285 on this corpus; majority class is 47.0%.

| assessor | prompt | argues against → "agree" | argues for → "against" | accuracy | kappa |
| --- | --- | --- | --- | --- | --- |
| gemma3 4B | paper | 90.3% | 0.9% | 46.2% | 0.065 |
| gemma3 4B | explicit | 93.0% | 0.3% | 44.5% | 0.036 |
| qwen3 8B | paper | 81.1% | 1.2% | 49.3% | 0.122 |
| qwen3 8B | explicit | 70.2% | 2.1% | 55.6% | 0.211 |
| llama3.2 3B | paper | 57.4% | 8.7% | 59.9% | 0.277 |
| mistral 7B | paper | 46.2% | 5.7% | 62.3% | 0.352 |
| mistral 7B | explicit | 0.6% | 38.2% | 62.6% | 0.385 |
| llama3.2 3B | explicit | 20.3% | 31.3% | 67.8% | 0.409 |
| qwen3 30B | paper | 34.5% | 9.1% | 66.0% | 0.412 *(n=250)* |
| **gpt-3.5-turbo** | paper | **36.5%** | 7.2% | 68.1% | 0.444 |
| gpt-3.5-turbo | explicit | 20.1% | 13.7% | 73.7% | 0.533 |
| **gpt-4o-mini** | **paper** | **14.2%** | 9.3% | **77.4%** | **0.604** |
| gpt-4o-mini | explicit | 4.7% | 25.4% | 76.7% | 0.575 |

### Two corpora agree on the number

PRISM's own gold set puts gpt-3.5-turbo's directional error at 14.7%
(section 12). Room For Debate puts gpt-4o-mini's at 14.2%. Different corpora,
different annotators, different domain — political compass essays against New
York Times op-eds — and the best assessor lands in the same band the paper's
own annotators found for theirs.

gpt-3.5-turbo is worse here, at 36.5%. That is the upper end of the 13-36%
range measured across three models in section 9, so the two lines of evidence
close on each other rather than diverging.

### The explicit prompt shifts the boundary; whether that helps depends where you start

Every model except gemma3 moves the same way: fewer counter-arguments read as
agreement, more supporting articles read as opposition. It is one shift, applied
to models sitting at different places.

| | accuracy change |
| --- | --- |
| qwen3 8B | 49.3 → 55.6 (+6.3) |
| llama3.2 3B | 59.9 → 67.8 (+7.9) |
| gpt-3.5-turbo | 68.1 → 73.7 (+5.6) |
| mistral 7B | 62.3 → 62.6 (+0.3, overshoots) |
| gpt-4o-mini | 77.4 → 76.7 (−0.7, overshoots) |
| gemma3 4B | 46.2 → 44.5 (−1.7, unresponsive) |

It helps models in the middle by five to eight points and overshoots at both
ends — mistral lands at 0.6%/38.2%, gpt-4o-mini at 4.7%/25.4%, both having
traded one bias for the opposite one. **The best configuration overall is
gpt-4o-mini with the paper's own prompt**, which is worth stating plainly: the
wording change is a real improvement for weaker assessors and a mild
disimprovement for the best one.

This refines section 17 rather than reversing it. There the claim was that the
prompt inverts rather than fixes; with the hosted models included it is clearer
that it moves a decision boundary in one direction, which repairs a model biased
one way and breaks one already balanced.

### Nothing reaches human agreement

The best assessor scores kappa 0.604 against gold. The two humans scored 0.8285
against each other. The gap is not closed by capability, by prompt, or by both
together, and every position in this project — and in the paper — rests on
labels produced somewhere on this table.

## 19. Re-scored with the best assessor: the numbers move, the claims hold

Sections 5, 8 and 10 were scored with whichever assessor was convenient at
generation time. Section 18 established that assessors differ by more than the
effect being measured, so every essay set was re-scored with the best available
one — gpt-4o-mini, paper prompt, 14.2% directional error against human labels.

**gemma3**, all seven runs, gpt-4o-mini scored:

| role | economic | social | refusals |
| --- | --- | --- | --- |
| none | −4.37 | −0.87 | 0 |
| pcleftlib | −2.00 | **−5.33** | 0 |
| pcleftauth | −4.37 | +4.00 | 0 |
| pcrightlib | +1.63 | −0.97 | 0 |
| pcrightauth | +1.50 | **+4.82** | 0 |
| blue | −3.25 | −2.31 | 0 |
| red | +1.50 | +3.69 | 1 |

Its unroled baseline moves from (−0.37, +2.72) self-scored to (−4.37, −0.87) —
four units on economic, 3.6 on social, from changing nothing but the reader.
Same pattern as mistral in section 8, and for the same reason.

**llama3.2**, gpt-4o-mini scored:

| role | economic | social | refusals |
| --- | --- | --- | --- |
| none | −1.31 | −1.85 | 4 |
| pcleftlib | −4.25 | −4.62 | 0 |
| pcleftauth | −3.25 | −2.56 | 1 |
| pcrightlib | **+6.63** | −3.85 | 2 |
| pcrightauth | +3.13 | −0.26 | **14** |
| blue | −4.25 | −1.64 | **33** |
| red | +1.50 | +0.72 | **43** |

### What survives the change of assessor

Three qualitative claims were made on numbers that have now all moved. They
survive:

- **Section 5, "the default sits on the boundary of its own window."** Re-scored,
  gpt-3.5-turbo's economic range becomes −5.25 to +5.38 (span 10.62, was 8.88)
  and social −5.38 to +4.67 (span 10.05, was 11.28). The baseline at −5.25 is
  still the leftmost point found.
- **Section 10, "identity labels are refused far more than positional wording."**
  Under gpt-4o-mini llama3.2 refuses 33 and 43 statements under `blue` and `red`
  against 0 to 14 under the `pc*` roles. The counts fall — the local assessor
  had over-reported refusals — but the six-fold gap holds.
- **Section 10, "llama3.2 cannot reach the authoritarian half."** Its only
  positive social score is `red` at +0.72, on a run with 43 refusals. Excluding
  unusable runs it still never crosses zero.

**Refusal is model-specific, now across three models.** mistral refused nothing
across 434 statements, gemma3 once, llama3.2 heavily and only under party
labels. The paper's observation that models resist authoritarian positions
holds for one of the three.

The distinction worth keeping: **the coordinates in this project are only as
good as the assessor that produced them, and they move by several units when it
changes. The structural claims — which quadrants are reachable, what gets
refused, where a default sits inside its own range — have so far been robust to
that.**

## 20. The search is viable on the social axis and not on the economic one

An optimiser does not need an unbiased assessor. It needs one that *ranks*
candidates consistently — a constant bias cancels when comparing two prompts.
So the question that decides whether any of the search work survives sections
15 to 19 is not "how wrong is the assessor" but "does the ordering change when
the assessor does".

Ten configurations have now been scored by both hosted assessors. Three of them
the two agreed on exactly; those inflate any correlation, so the honest figure
excludes them:

| | all 10 | the 7 they actually disagree on |
| --- | --- | --- |
| social, Spearman | +0.99 | **+0.96** |
| economic, Spearman | +0.83 | **+0.54** |

Among those seven the position itself moves 1.25 to 3.71 units, mean 2.44. So
the assessors disagree substantially about *where* each candidate sits and
almost entirely agree about *how they order* — on the social axis. On economic
the ordering is only weakly preserved.

### Why the two axes differ, structurally

| axis | statements carrying any weight | total achievable swing |
| --- | --- | --- |
| economic | **18 of 62** | 160 |
| social | **43 of 62** | 390 |

The economic coordinate rests on 18 statements, the social one on 43. A single
mislabelled statement therefore has 2.4 times the leverage on economic. That is
not a property of the models or the prompt — it is in `pc_lookup.csv`, and it
predicts exactly what has now been measured twice by unrelated routes:

- changing assessor preserves rank on social (+0.96) but not economic (+0.54)
- reducing the instrument preserved rank on social (+0.90) but not economic
  (+0.67, and −0.40 on a second sample) — section 5 and section 8

### What follows

**A search optimising the social axis is on defensible ground.** Its rankings
survive both a change of assessor and a change of instrument, which are the two
things most likely to have invalidated it.

**A search optimising the economic axis is not.** Its rankings are fragile to
both. Any economic result needs repeated scoring and wider error bars, and the
fragment-versus-role economic comparison in section 8 should be read as
indicative only — which is what it was already labelled, now with a mechanism.

This is the first thing in this file that makes the optimisation programme look
workable rather than undermined. The assessor is badly wrong in absolute terms
and still usable for the thing a search actually needs, on one of the two axes.

## What is not yet done

- **No independent adjudication exists.** Which assessor is right is supported
  only by six essays the author read by hand (section 6). A gpt-4o adjudication
  was written into section 9 and removed because it had never been run. Human
  labels, even on a sample, are the single thing most needed — every claim
  about the *direction* of the assessor error rests on that gap being filled.
- The fragment search had no valid economic signal: the subset it used carried
  economic weight on only 3 of 12 statements. `--max-questions` now selects by
  scoring weight, but the mistral fragment search predates that fix, so the
  fragment-versus-role comparison in section 8 is sound on the social axis and
  a lower bound on the economic one.
- Budgets are small — 12 to 18 evaluations against 4800 candidates. No search
  here has converged, and every window is a lower bound rather than a boundary.
- Only two of the four window directions were run on gpt-3.5-turbo. Role
  scenarios covered all four quadrants, but only on mistral and llama3.2.
- llama3.2's role positions (section 10) were scored by a local assessor and
  are provisional. Its refusal counts do not depend on the assessor and are
  not provisional.
- Repeat variance (section 7) was measured on one configuration only, n=4, and
  the underlying ratings were overwritten before `--run-tag` existed, so it
  cannot be recomputed from this repository.
- The `results/` figures marked in `unregenerable_figures.json` came from
  terminal output rather than from artefacts here, and cannot be re-derived.

## Practical notes

- Essays and assessor ratings are both cached by configuration hash, so
  re-evaluating a candidate costs nothing — measured 7.35s → 0.001s. This
  matters for search, where an EA re-generates the same genotype often.
- One audit is 124 sequential model calls, plus two per refusal.
- `--base-url` reaches any OpenAI-compatible endpoint, or a remote Ollama
  server. Sampling parameters are translated per provider.
- Do not run a search against a local Ollama server on a laptop. It evaluates
  candidates back to back; `--sleep-between` defaults to 45s for that reason.
