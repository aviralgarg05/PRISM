# Framing and research questions

A proposal for the paper, written against Sandy's heading of 2026-09-15: a political audit
measures an interaction between model, prompt, assessor, scoring instrument and safety
policy, not a stable political property of the model, and automated prompt search makes those
dependencies visible.

Everything below cites a section of [FINDINGS.md](FINDINGS.md) or an outcome in
[PREREGISTRATION.md](PREREGISTRATION.md). Claims those documents have withdrawn are listed at
the end so they do not come back.

## The claim

A political-compass coordinate is the output of a configuration — scoring key, persona,
assessor, refusal rule, gate version — and this project can price each of those in the
instrument's own units. The strongest evidence is deterministic: on gemma3, re-scoring
**unchanged essays** under a refusal rule moves `facist` from −6.64 to +2.41 to 0.00 and
changes which persona is the model's libertarian extreme (§34). Nothing was regenerated, so
that result survives every open question in the file.

Search is the probe, not the claim. It earned its place by exposing an instrument defect no
hand-written audit would have found (§27, §28) and by showing that a reported effect is a
draw from a distribution an audit run once never sees (§36).

## RQ1. What does the instrument score when the respondent supplies no political content?

Answered, and it is arithmetic. "Agree" carries zero weight on both axes, 18 of 62 statements
carry any economic weight against 43 social (§20). Uniform "Strongly agree" scores social
**+4.359**, uniform "Strongly disagree" −4.359, uniform "Agree" +2.410, uniform Neutral 0.000
(§27, §31). A respondent with no political content therefore reaches 44% of a pole, and only
5 of 69 hand-written personas clear the null (§31). Decomposed: `pcxrightauth` measures +7.18,
of which +2.82 is content beyond the null, using 50% of its headroom (§31).

Still to run: the answer-format ablation (§36), which decides whether "content beyond the
null" can be said at all on gemma3, mistral and gpt-5.4-mini; the same decomposition on the
other four enumerations, which is free arithmetic over cached stances; a forced-choice control
on the same models and personas, to separate a property of the scoring key from a property of
essay-mediated elicitation.

## RQ2. How far does a reported position move under choices an audit does not declare?

- **Refusal rule.** gemma3: `facist` −6.64 → +2.41 → 0.00, `extremist` −5.92 → +2.41 → 0.00,
  `hilter` −3.28 → +2.41 → 0.00, each declined on 62 of 62 statements; the libertarian
  extreme becomes `pcxleft` at −6.411 (§34). On gpt-5.4-mini the same choice moves the
  headline effect: D = +1.365 [+0.793, +1.937] under the Neutral rule against
  +2.030 [+1.451, +2.609] under Agree (§35).
- **Gate version.** v2 → v3 moves H\* from +1.923 to +1.692 and turns a pre-registered
  prediction from inside the fitted range to outside it (§35).
- **Assessor.** A weak assessor moves mistral's unroled baseline 6.86 units and flips its
  quadrant (§8); two hosted assessors disagree by 1.25 to 3.71 units, mean 2.44, on the
  configurations where they disagree at all (§20), against repeat noise of 0.27 (§7).
- **Instrument length.** `--max-questions` keeps the 62-statement transform, so 80 of 116
  libertarian candidates sat bit-exactly on the floor and four candidates the surrogate called
  identical were 1.67 units apart on the full instrument (§27, §28).

Still to run: the strong-versus-strong assessor comparison on unroled baselines and on
confirmed boundary candidates. Under $25 on cached essays, never run, and a reviewer will ask.

## RQ3. Does a model's safety policy get reported as its politics?

The assessor records Refused only when no essay is provided, so a model that declines a persona
and then argues against it is scored as holding that stance (§34). Prevalence: gemma3 288 such
essays, 229 of them given a strong stance and 35 correctly Refused; gpt-3.5-turbo 15; mistral
14; gpt-4o-mini 1 (§34). On gpt-5.4-mini, 19 of the 69 hand-written personas are declined on
more than six statements, which makes them infeasible under the rule the search applies to its
own candidates (§35).

The gate is a component with its own error, not a fix: v1 called 9 of 20 ordinary essays
refusals; v2 passed a hand-labelled set 33/33 and 0/40 and then, in its first production use,
27 of 34 audited REFUSED verdicts were not refusals (§34). Gate v3 adds a first-person
pre-filter and releases those.

Still to run: a persona-blind gate ablation over the labelled openings, since the gate is the
one component shown the persona; a second labeller on the gate's categories; a second refusing
model, so the artefact is not a one-model result.

## RQ4. What is the measurement's resolution?

Two strong assessors agree within 0.72 units on identical essay sets, ordering preserved (§29).
Assessor nondeterminism with the essay held literally fixed is sd 0.252 (§36). Pooled
within-arm sd is 0.446 (§27). The ±0.75 equivalence bound rests on the first two, and both come
from small, role-conditioned samples, which is the weakest leg of the project. Against that,
§36 shows local-model replicates give 1.0 to 4.9 distinct essays per statement across twelve
runs, so several intervals are computed on duplicates.

Still to run: a small crossed design — personas × models × occasions × two strong assessors —
to replace an asserted bound with a measured standard error per facet, with model versions
pinned. Free alongside it: item-total correlations and a dimensionality check over the cached
stance matrices, which no audit using this instrument reports.

## RQ5. What must an audit declare, and does declaring it change a published conclusion?

The components exist: pre-registered decision rules with outcomes recorded including failures,
three refusal rules implemented and reported, a versioned gate with its failure modes on
record, and the requirement to say which statements moved, since statements 4 and 27 alone
carry 24% of one measured gain (§27).

The external check is done for the strongest case. §31's claim that the acquiescence property
belongs to the scoring rather than to this fork is confirmed against a published replication
package: Motoki et al. (Public Choice 2024) publish the per-statement weights, all 62 rows are
identical to this repository's key, "agree" carries zero weight throughout, and their own code
applies the ÷19.5 +2.41 transform (§37). So the paper reports a property of a published audit,
not a bug in one repository.

Still to run: the same check against two or three more audits, to say how widely the key
travels, and a reading of what those audits do with a refusal.

## What the existing results are for

| Result | Anchor | Serves | Caveat to carry |
| --- | --- | --- | --- |
| "Agree" = 0 on both axes; 18 vs 43 statements | §20 | RQ1, RQ5 | this fork's key until RQ5's reading is done |
| Acquiescence null ±4.359, Neutral 0.000 | §27, §31 | RQ1 | social-specific; economic moves at most 0.380 |
| 69-persona decomposition, headroom, modal share | §31 | RQ1 | one model, one assessor, n=1 per persona |
| gemma3 gated rescore on unchanged essays | §34 | RQ2, RQ3 | deterministic |
| Refusal rule moves D from +1.365 to +2.030 | §35 | RQ2 | one model |
| Gate v2 → v3 moves H\* and a prediction | §35 | RQ2, RQ5 | always name the version |
| Decline-then-write prevalence, four models | §34 | RQ3 | gemma3 supplies most of it |
| Gate v1 failure and v2 false positives | §34 | RQ3, RQ5 | labelled by one person |
| Assessor swap 6.86 units, quadrant flip | §8 | RQ2 | weak versus strong |
| Two hosted assessors 1.25–3.71, mean 2.44 | §20 | RQ2 | ten configurations |
| Surrogate saturation, 80/116 bit-exact | §27, §28 | RQ2 | search-visible instrument defect |
| Two strong assessors within 0.72 | §29 | RQ4 | n=3, role-conditioned, the easy regime |
| Distinct-essay counts 1.0–4.9 locally | §36 | RQ4 | local n=12 intervals overstate precision |
| Winner's curse up to 1.513 | §32 | RQ4, RQ5 | confirms the argmax, not the procedure |
| Five-model D table | §36 | RQ2 | three models have one search run each |

## Experiments, in order

| # | Experiment | Cost | Serves |
| --- | --- | --- | --- |
| 0 | Ethics and release note: an exposure protocol for anyone who reads essays written in the declined personas, and a policy on releasing the search-derived ones | half a day | all |
| 1 | Free arithmetic over cached stances: decomposition on all five enumerations, a three-rule table per model, item-total and dimensionality checks | none, 2–3 days | RQ1, RQ2, RQ4 |
| 2 | Persona-blind gate ablation over the labelled openings | under an hour | RQ3 |
| 3 | Strong-versus-strong assessor on unroled baselines and boundary candidates, pre-registered | ~$25 | RQ2, RQ4 |
| 4 | Answer-format ablation: winners confirmed with the "Strongly Agree or Strongly Disagree" sentence removed, 3 models, n=12, pre-registered at ±0.75 | ~$2 hosted, half a day local | RQ1, RQ3 |
| 5 | Forced-choice control on the same models and personas | ~$10 | RQ1 |
| 6 | Second labeller on the gate categories | 2 hours each | RQ3 |
| 7 | Crossed design for resolution, versions pinned | ~$100, 2–3 days | RQ4 |
| 8 | Read 3–5 published audits against §31 | reading, 3–4 days | RQ5 |
| 9 | Second refusing model, enumerated ungated and gated | 3–5 local days | RQ3 |

Item 4 has to land before any sentence about content beyond the null is written. Items 1 to 3
come first because they are cheaper in calendar time and item 3 can invalidate more of the
framing than item 4 can.

Item 0 is first for a reason. The search has already produced a persona that flips a model
into endorsing racial superiority (§27), and any labelling task involves reading essays
written in `hilter`, `facist` and `extremist` personas. A venue like FAccT or AIES will expect
an exposure protocol and a release policy before that work is described, and there is none in
the repository yet.

## Where the novelty has to sit

The premise that audits report a point and prompts move it is the field's starting position.
Röttger et al., ACL 2024, argue that Political Compass results are artefacts of constrained
elicitation and change again in open-ended settings. Wright et al., Findings of EMNLP 2024,
run 156k open-ended responses to the same 62 propositions across six models and 420 prompt
variations with stance labelling, which is structurally this pipeline. Domínguez-Olmedo et al.,
NeurIPS 2024, show survey responses are governed by ordering and labelling bias and propose
null baselines. Sclar et al., ICLR 2024, report performance as a spread over prompt formats
and use search to find that spread cheaply.

What is not in that literature, as far as I can tell:

1. The scoring key priced on held-fixed essays. Refusal and agreement are numerically
   identical under this key, so the audit silently imports an item-nonresponse coding rule,
   and the size of it can be stated in the instrument's own units.
2. Surrogate saturation as an instrument defect that only optimisation makes visible.
3. The audit protocol itself: pre-registered decision rules, a matched no-selection control,
   randomised complete blocks, and a public record of withdrawn claims.

## Risks

**Priority.** If other published audits weight "Agree" nonzero or handle refusals, the
indictment shrinks to a bug report on one fork. Experiment 8 settles it, and it costs reading
time.

**The assessor bound is circular.** Every coordinate in the project is gpt-4o-mini, and the
only strong-versus-strong check is n=3 on role-conditioned personas in the regime where
assessors agree best (§9, §29). That 0.72 became the ±0.75 decision threshold. Experiment 3
settles it and is lose-lose by design, so it is pre-registered either way: agreement there
reduces the assessor leg to "do not judge with a small local model", and disagreement above
two units means the paper can carry orderings but not positions.

## Withdrawn, and not to be used

- The linear relationship D = 4.574 − 0.628·H\*, r = −0.987 (§33). gpt-5.4-mini, the held-out
  model, returned +1.365 against a pre-registered +3.223 (§35), and gemma3's own point moved
  from +1.081 to +0.385 on a second run (§36).
- gemma3 as a confirmed prediction (§36).
- Any split of the gain between rewriting and selection. The selection term reversed sign on
  both models with two runs (§36).
- "Search never beats hand-written prompts", which came from a handicapped search (§30).

Each of those failures is evidence for the heading rather than against it: a quantity that
moves this much between runs of the same protocol is not a stable property of a model.
