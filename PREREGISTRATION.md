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

---

## Third pre-registration: gpt-5.4-mini, a current model that refuses

Committed while its enumeration was still running: 18 of 71 personas scored,
H\* not yet determined.

### Why the protocol changes

gpt-5.4-mini declines extreme personas outright (FINDINGS section 34), so the
section 32 protocol cannot run on it unchanged. Two changes, fixed now:

- `--refusal-gate` on every run, so a declined persona is scored Refused and
  the essay written in its place is not scored as the persona's stance.
- `--refused-as neutral`, so a refusal carries no position. Under the paper's
  rule a refusal scores as Agree, which would reward an authoritarian search for
  eliciting refusals.

### H\*

The best **feasible** hand-written persona on the social axis under the neutral
rule. Feasible means refused on at most 6 statements with response entropy at
least 0.25, the same rule `evolve_persona.py` applies to its own candidates. A
persona the model mostly declines is not a hand-written prompt that steers it.

### The prediction

The section 33 line refitted under the neutral rule (FINDINGS section 34):

**D = 4.597 − 0.636·H\***, evaluated at H\* confirmed at n=12, and also reported
at the n=1 screening value.

- Observed D within 1.0 of predicted: the relationship holds on a fifth model.
- Further than 1.0: it does not.
- If confirmed H\* lies outside +1.86 to +7.39, the range the line was fitted on,
  this is a test of extrapolation, and a miss counts against extending the line
  beyond that range.

### Protocol

As section 32 apart from the two flags above: full 62-statement instrument;
`evolve_persona.py` at population 6 for 8 generations, seeded with
gpt-5.4-mini's top six feasible hand-written personas under the neutral rule;
a matched `--no-selection` control; the best of each arm confirmed at n=12 in
randomised complete blocks against H\*. Same decision rule: positive if the
one-sided 95% lower bound on D is at least +0.50, negative if the 95% upper
bound is below 0, equivalent if the 90% interval lies within ±0.75.

D is also reported under the paper's Agree rule, from the same ratings.

---

## Fourth pre-registration: re-running the controls that drew on infeasible seeds

### What went wrong

In sections 32 and 33 the `--no-selection` control took parents from every seed,
feasible or not, while the search arm only ever selects feasible parents. On
gpt-3.5-turbo the control started from 2 infeasible seeds of 6 (`pcaxuth` and
`pcxright`, both at response entropy 0.24 against a floor of 0.25); on gemma3
from 2 (`pcxright`, refused on 10 statements, and `biasedagent`, entropy 0.16).
gpt-4o-mini and mistral had none. D compares the search arm with H\* and does
not involve the control, so it is unaffected. The variation/selection split on
those two models is confounded.

The logs cannot settle it. Text similarity attributes 41 of 42 gemma3 search-arm
children to `pcxright`, a seed that arm could never have used, so similarity is
not evidence of lineage.

### Design

Both arms re-run on gpt-3.5-turbo and on gemma3 with the corrected driver
(`74f6074`), with the same seeds, budget and flags as the originals, reading the
same cached seed evaluations. The new search best, the new control best and H\*
are then confirmed at n=12 in randomised complete blocks, with H\* re-measured
fresh inside those blocks rather than read from the earlier confirmation.

### Decision rule, fixed now

- **gpt-3.5-turbo.** Published selection alone: −0.560 [−1.070, −0.050]. If the
  re-run's 95% interval for selection alone includes zero or lies above it, "selection
  is harmful on gpt-3.5-turbo" is withdrawn as an artefact of the parent
  asymmetry. If it stays below zero with the interval excluding zero, it stands.
- **gemma3.** Published variation alone: +0.893 [+0.468, +1.318]. If the re-run's
  variation alone is lower by more than 0.5, the published split overstated the
  rewriting's share on gemma3.
- **D on both** is re-measured as a replication. A re-run D outside the original
  95% interval (gpt-3.5-turbo [−0.809, +0.126]; gemma3 [+0.829, +1.334]) is
  reported as a failed replication of that model's D.

### Screening values, recorded before the search started

- Enumeration complete: 69 hand-written personas, 50 feasible under the rule above.
- H\* at screening (n=1, neutral rule): `pcrightauth` at +1.923.
- Inside the fitted range of +1.86 to +7.39 at screening, by 0.06. Whether the final test is an extrapolation is decided at the confirmed value, as stated above.
- Predicted D at the screening value: 4.597 − 0.636 × 1.923 = **+3.374**.
- Seeds, the top six feasible hand-written personas under the neutral rule: `pcrightauth` +1.92, `ctrlrightauth` +1.72, `pcauth` +0.05, `conservative` -2.21, `ctrlleftauth` -2.21, `pcright` -2.36.

---

## Fifth pre-registration: gpt-5.4-mini under gate v3

Supersedes the screening values recorded under the third pre-registration.

### Why it is re-registered

After the third pre-registration and its screening values were committed and the
search had started, reading the essays behind gpt-5.4-mini's refusal counts showed
the gate calling ordinary essays refusals when they contradicted the persona
(FINDINGS section 34). The search was stopped after one evaluation per arm, before
any of its scores were looked at. Gate v3 (commit `6aa7544`) requires first-person
refusal language before the model is asked.

### What changes

- Gate v3, with gated ratings cached under `_gate3`; no verdict from the earlier
  gate is reused.
- Everything else in the third pre-registration stands: refusals scored as
  Neutral; H\* is the best feasible hand-written persona under the neutral rule
  (at most 6 refusals, entropy at least 0.25); the same search protocol and seeds;
  the same decision rule; D also reported under the Agree rule.

### Screening values under gate v3, recorded before relaunch

Computed from the enumeration's existing essays: statements the v3 check
releases were classified with the paper's assessor, and statements it keeps
retain their earlier verdict.

- Feasible: 52 of 69.
- H\* at screening: `pcrightauth` at +1.692, with 0 refusals.
- Predicted D: 4.597 − 0.636 × 1.692 = **+3.521**.
- Outside the fitted range of +1.86 to +7.39, by 0.17. Unless the confirmed H\* comes back inside that range, this is a test of extrapolation, and a miss counts against extending the section 33 line below +1.86.
- Seeds: `pcrightauth`, `ctrlrightauth`, `pcauth`, `conservative`, `ctrlleftauth`, `pcright`.

### Outcome of the fourth pre-registration: gpt-3.5-turbo

Both arms re-run with matched parents, then confirmed at n=12 in randomised
complete blocks with H\* re-measured inside the same blocks.

| arm | n | social | sd | search-time best |
| --- | --- | --- | --- | --- |
| search | 12 | +7.384 | 0.528 | +8.410 |
| H\* (`pcxrightauth`) | 12 | +7.320 | 0.673 | – |
| control | 12 | +6.842 | 0.629 | +7.897 |

Both arms started from the same one infeasible seed of six.

| | confounded run | re-run |
| --- | --- | --- |
| D = search − H\* | −0.342 [−0.809, +0.126] | +0.064 [−0.450, +0.578] |
| variation alone | +0.218 [−0.200, +0.636] | −0.479 [−1.030, +0.073] |
| selection alone | −0.560 [−1.070, −0.050] | **+0.543 [+0.050, +1.035]** |

- **"Selection is harmful on gpt-3.5-turbo": withdrawn.** The re-run interval
  lies above zero; the sign reverses.
- **D replicates**, inside the original interval.

gemma3's re-run is still running.

### Outcome of the fifth pre-registration

Search, matched control and H\* were confirmed at n=12 in randomised complete
blocks with gate v3 on.

The confirmation was first stored with refusals scored as Agree, because
`confirm_persona.py` passed `--refused-as` to its log header and not to each run
(fixed in `83ea1af`). The stances are cached, so every run was rescored from them
under the pre-registered Neutral rule. The search arms scored with the Neutral
rule throughout.

| arm | n | social, Neutral rule | sd | refused per run |
| --- | --- | --- | --- | --- |
| control best | 12 | +5.047 | 0.697 | 0.0 |
| search best | 12 | +3.525 | 0.836 | 5.5 |
| H\* `pcrightauth` | 12 | +2.160 | 0.421 | 0.1 |

- Confirmed H\*: +2.160, inside the fitted range, so the in-range criterion applies.
- D under the Neutral rule: +1.365 [+0.793, +1.937]. Predicted at the confirmed
  H\*: +3.223. Observed minus predicted: −1.858.
- **The relationship does not hold**: further than 1.0 from the prediction. It
  also fails under the Agree rule (D +2.030 against a predicted +3.214, −1.184).
- By the decision rule D is POSITIVE: search beats the best hand-written persona.
- Selection alone −1.521 [−2.174, −0.869]; variation alone +2.887 [+2.393, +3.380].
- The search best exceeded the 6-refusal feasibility limit in 3 of its 12
  confirmation runs. The pre-registration did not say to re-check feasibility at
  confirmation, so this is reported and not applied.

### Outcome of the fourth pre-registration: gemma3

Both arms re-run with matched parents, then confirmed at n=12 in randomised
complete blocks with H\* re-measured inside the same blocks.

| arm | n | social | sd | search-time best |
| --- | --- | --- | --- | --- |
| search | 12 | +5.872 | 0.232 | +7.282 |
| H\* (`stalin`) | 12 | +5.487 | 0.000 | – |
| control | 12 | +7.632 | 0.020 | +7.641 |

Both arms started from the same two infeasible seeds of six.

| | original run | re-run |
| --- | --- | --- |
| D = search − H\* | +1.081 [+0.829, +1.334] | +0.385 [+0.237, +0.532] |
| variation alone | +0.893 [+0.468, +1.318] | +2.145 [+2.133, +2.158] |
| selection alone | +0.188 [−0.275, +0.651] | −1.761 [−1.908, −1.613] |

- **The split rule, as written, returns "stands".** It only asked whether
  variation alone fell by more than 0.5, and it rose by 1.25 instead. The rule did
  not anticipate a move in the other direction, and there was one: selection went
  from +0.19 to −1.76. The gemma3 split does not replicate in either direction,
  and "stands" is not a confirmation.
- **D: failed replication**, outside the original interval.
- **The re-run's intervals are not valid.** H\* produced byte-identical essays on
  all 62 statements in all 12 runs, so its sd of 0.000 reflects deterministic
  generation rather than precision, and the control arm returned only 2 distinct
  scores in 12 runs. On a local model at temperature 0 the only replicate
  variation comes from request batching in the server, and here it nearly
  vanished. The difference between the two gemma3 search runs, 0.70 in D, is the
  honest measure of uncertainty, and it is far wider than either run's interval.
- Against the section 33 pre-registration, the re-run D of +0.385 falls between
  its bands, above +0.3 and below +0.6.
