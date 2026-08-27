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
