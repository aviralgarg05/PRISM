# Pre-registration: does search beat the best hand-written persona?

Written **before** the confirmation data was read. Committed so the decision
rule cannot be chosen after seeing the result — the winner's-curse analysis in
FINDINGS section 28 showed that a search log looks like a win under the null
often enough that a post-hoc rule would be worthless.

## The question

Three search methods have been run against this objective and none has beaten a
hand-written persona (FINDINGS sections 21, 23, 26, 27, 28). The remaining
objection was that they were all optimising a bounded surrogate and that the
best hand-written persona had never been properly established. Both are now
addressed: the surrogate is fixed, and all 69 non-empty personas in `roles.py`
have been scored on the full 62-statement instrument.

That enumeration gives the baseline:

- **H\* = `pcxrightauth`, social +7.18** (n=1 screening; +7.30 at n=3 earlier)
- runner-up `pcaxuth` +7.13 — effectively tied, so it is confirmed too
- best result from any search: **+6.46**
- only 5 of 69 personas clear the all-Strongly-agree null of +4.36

## The measurement

3 arms — H\*, `pcaxuth`, and the best search candidate — at **n=12 replicates**,
full instrument, gpt-3.5-turbo audited at temperature 0, gpt-4o-mini assessing,
independent essay draws forced through `prompt_label`.

Replicates run as **randomised complete blocks**: one replicate of every persona
per round, order shuffled per round, split across six concurrent processes
covering disjoint replicate indices. This is the fix for the confound in section
27, where all nine runs sat in one 44-minute window with each arm as a
contiguous block, so persona was aliased with wall-clock position.

Let **D = mean(best search) − mean(H\*)** on the social axis.

## The decision rule

| outcome | condition | framing |
| --- | --- | --- |
| **positive** | one-sided 95% lower bound on D ≥ **+0.50** | search beats hand-writing; the original paper survives |
| **negative** | 95% upper bound on D < **0** | search is measurably worse than hand-writing |
| **equivalent** | 90% CI on D lies entirely within **[−0.75, +0.75]** | a ceiling both routes reach; neither method is the story |
| **unresolved** | none of the above | the instrument cannot resolve the difference at this budget; say so and stop spending on it |

The ±0.75 equivalence bound is set by the instrument, not by convenience: the
assessor term between gpt-4o and gpt-4o-mini on identical essays is 0.72 units
(section 29), and the replicate sd for H\* is 0.73. Asserting equivalence
tighter than the instrument's own noise would not be credible.

**A gain that appears only at search time does not count.** The best of 48
single-draw evaluations sits well above the truth under the null; only the
confirmed n=12 mean is admissible as a result.

## Secondary, decided in advance

- Every position is reported beside the **+4.36 acquiescence null**. A persona
  below it has not demonstrated a political position at all.
- Economic position is reported alongside social. The objective optimised social
  only, and the evolved personas gave up 3.2 units of economic position to get
  there, so a social-axis win bought that way is reported as a trade, not a win.
- If the result is **equivalent** or **unresolved**, the next spend goes to a
  second audited model, not to a larger search budget on this one. A ceiling
  measured on one legacy model is not a finding.

---

## Outcome (recorded after the run)

| arm | n | social mean | sd |
| --- | --- | --- | --- |
| `pcxrightauth` (H\*) | 12 | +7.393 | 0.424 |
| `pcaxuth` | 12 | +7.030 | 0.390 |
| best search candidate | 12 | +6.562 | 0.666 |

D = −0.831, se 0.228, Welch df 18.7. Two-sided 95% upper bound **−0.353**.

**NEGATIVE**: the whole interval lies below zero. Search is measurably worse
than the best hand-written persona, and worse than the second-best one too.

Per the secondary rule above, the next spend goes to a second audited model,
not to a larger search budget on this one.

---

## Outcome, second and final round (all three models, one protocol)

The first round is superseded: its search arm had been run on a bounded
surrogate with the variation operator barred from the register that wins, and
on two of the three models no search had been run at all. Re-run under one
protocol — full instrument, freed operators, each model's own top-six seeds, a
matched no-selection control, n=12 randomised complete blocks:

| model | H\* | control | search | D | 95% CI | outcome |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-3.5-turbo | +7.393 | +7.611 | +7.051 | −0.342 | [−0.809, +0.126] | EQUIVALENT |
| gpt-4o-mini | +6.769 | +7.209 | +7.248 | +0.479 | [+0.098, +0.859] | UNRESOLVED |
| mistral 7B | +1.863 | +4.307 | +5.243 | +3.380 | [+3.194, +3.567] | POSITIVE |

The rule held under pressure three separate times. It stopped a noisy
three-client mistral run being written up as POSITIVE; it stopped search-time
maxima of +1.17 and +1.33 being written up as wins when confirmation put them at
−0.34 and +0.48; and it forced the withdrawal of a negative result that turned
out to be an artefact of how the search had been configured.

---

## Second pre-registration: a quantitative prediction, written before the run

Three models gave a monotone relationship — the weaker the hand-written
baseline, the more search buys:

| model | H\* | D |
| --- | --- | --- |
| gpt-3.5-turbo | +7.393 | −0.342 |
| gpt-4o-mini | +6.769 | +0.656 |
| mistral 7B | +1.863 | +3.380 |

But **fit and family are perfectly confounded** at three models: the two where
search buys nothing are exactly the two OpenAI models, and `roles.py` came out
of OpenAI work. Two explanations survive equally:

- **Fit** — search returns what the hand-written baseline leaves on the table,
  whatever the model.
- **Family** — GPT models are simply less movable beyond their baseline.

**gemma3 separates them.** It is a third family, and its enumeration (all 71
personas, full instrument) puts H\* = `stalin` at **+5.18** — between mistral's
+1.86 and the OpenAI models' +6.8 to +7.4. The two hypotheses therefore predict
different numbers for the same run:

| hypothesis | predicted D on gemma3 |
| --- | --- |
| **fit** (least squares through the three points, D = 4.586 − 0.628·H\*) | **+1.33**, call it +1.3 to +2.3 |
| **family** (non-GPT behaves like mistral) | **≈ +3.4** |

**Decision, fixed now:** run the same protocol on gemma3 — search arm, matched
no-selection control, best of each confirmed at n=12 in randomised complete
blocks against H\* = `stalin`.

- D in **[+0.6, +2.5]** → supports **fit**. Report the relationship as
  quantitative, and the earlier negative results as a property of the baseline
  rather than of the model family.
- D **above +2.8** → supports **family**. Withdraw the "gain tracks fit"
  framing; the pattern is about the vendor, and three models are not enough to
  say which.
- D **below +0.3** → both are wrong. gemma3 has a strong baseline *and* no
  headroom, so the relationship is not monotone in H\* and the whole framing
  needs rebuilding.

The line was fitted on n=3 and is a sketch, not an estimate; the prediction is
recorded so the outcome cannot be read as confirmation whichever way it lands.

### Outcome of the second pre-registration

| arm | n | social | sd |
| --- | --- | --- | --- |
| search | 12 | +6.572 | 0.382 |
| control | 12 | +6.384 | 0.660 |
| `stalin` (H\*) | 12 | +5.491 | 0.142 |

**D = +1.081, 95% CI [+0.829, +1.334]. Inside the fit band [+0.6, +2.5];
family (above +2.8) rejected.**

The same line, evaluated at gemma3's confirmed H\* of +5.491 rather than the
n=1 value of +5.18 used when the prediction was written, gives +1.14. Refitting
on four points leaves the slope at −0.628.
