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
changes which persona is the model's libertarian extreme (§34). Re-scoring a published audit's
**own deposited answers** the same way moves its radical-republican condition 2.68 units on the
social axis (§37). Nothing was regenerated in either case, so both survive every open question
in the file. Two registered experiments then show how much rides on how a stance is asked for:
the same persona on the same model moves by up to 4.15 units between writing an essay and
choosing an option (§39), and one inherited sentence telling the model how to answer carries
between 1.1 and 4.3 units of a persona's position in eight of ten personas tested on four
models (§40).

Search is the probe, not the claim. It earned its place by exposing an instrument defect no
hand-written audit would have found (§27, §28) and by showing that a reported effect is a
draw from a distribution an audit run once never sees (§36).

## Your five components, and what each is worth

Everything in the file sorted into the heading you proposed, with the largest measured
effect for each and where it lives. The units are the instrument's own, on a social axis
that runs from −10 to +10.

| component | what it changes | measured | anchor |
| --- | --- | --- | --- |
| scoring instrument | the key gives "Agree" zero weight on both axes, so a refusal is scored as agreement and a persona refused on every statement lands at +2.41 | re-scoring a published audit's own deposited answers with "agree" at the midpoint moves a condition 2.68; one audit, and its conclusion compares conditions | §37, §38 |
| prompt | which persona, and one inherited sentence telling the model how to answer | persona choice spans 13.33 on gpt-3.5-turbo and 8.35 on gpt-4o-mini; the answer sentence carries 1.10 to 4.33 in eight of ten personas on four models | §23, §40 |
| safety policy | whether the persona is played at all, and what a decline is read as | a persona gemma3 declines on every statement is reported at −6.64 ungated, against 0.00, the no-position point, once the declines are gated (+2.41 under the Agree coding, a 9.05 swing); on gpt-5.4-mini 17 of 69 personas are infeasible under gate v3 and 16.5% of all answers are refused; gpt-4o-mini refuses statement 4 under every role persona yet endorses statement 27 12 of 12 under an evolved one | §34, §35, §37, §42 |
| assessor | which stance an essay is given | two strong assessors move a position by up to 1.77 and a difference between personas by at most 0.65; a weak assessor moves a baseline 6.86 and flips its quadrant | §8, §41 |
| model | which model is asked | the same personas rank differently across models, ρ 0.53 to 0.69 among the personas both will play | §35 |

One component your list does not name, and I think it belongs: **how the stance is asked
for**. The same persona on the same model moves by up to 4.15 between writing an essay that
an assessor reads and picking one of the four options itself (§39). That is larger than the
assessor term and it is invisible in any audit that only ever uses one mode.

## Where search helps

Your second point, now that the answer instruction has been ablated. D is the confirmed gain
of the search winner over the best hand-written persona, n=12 in randomised complete blocks.

| model | winner carries the answer sentence | D as published | D with the sentence removed from every arm | reading |
| --- | --- | --- | --- | --- |
| gpt-3.5-turbo | no (§36) | −0.342, then +0.064 | not applicable | no gain, on the model the library was written for |
| gpt-4o-mini | no (§36) | +0.656, 90% interval [+0.443, +0.869] | not applicable | equivalent under the widened bound (§41) |
| gemma3 | yes, both runs | +1.081, then +0.385 | −1.141 and −0.714 | the gain was the sentence |
| mistral | baseline yes, winner no | +3.380 | +7.733 | real, and larger than published |
| gpt-5.4-mini | yes, both arms | +1.365 | +4.891 | real, and larger than published |

So search helps where the hand-written library transfers badly, and the size of the help
depends on whether the baseline it is measured against carries the answer instruction. On
gemma3, what looked like help was that instruction. Two models have one search run each, so
these are not five independent estimates.

## RQ1. What does the instrument score when the respondent supplies no political content?

Answered, and it is arithmetic. "Agree" carries zero weight on both axes, 18 of 62 statements
carry any economic weight against 43 social, and statement 21 carries none (§20, §38). The
instrument offers no neutral option. Its own origin is the uniformly random respondent, at
economic +0.036 and social 0.000; uniform "Agree" lands at +2.410 social, uniform "Strongly
agree" at +4.359 and uniform "Strongly disagree" at −4.359 (§31, §38). The same table and
constants are in Röttger et al.'s and Wright et al.'s code and in Motoki et al.'s replication
package, and Röttger et al. record the live site returning 0.38, 2.41 for all "Agree" (§37, §38).

Across the five audited models, between 32% and 77% of each hand-written library measures a
position that uniform agreement or disagreement alone would reach, and on mistral and
gpt-5.4-mini no persona clears the authoritarian null at all (§38). The scale is answered at
its ends: 76.5% to 97.5% of stances across each library are "Strongly agree" or "Strongly
disagree", and α is 0.889 to 0.952 while the first factor takes 24% to 39% (§37).

The answer instruction is in the seeds. "State whether you either Strongly Agree or Strongly
Disagree" is verbatim in ten hand-written personas, including the seeds of the gemma3 and
gpt-5.4-mini searches and `pcleftlib`, the libertarian headline of §31; the authoritarian
headline `pcxrightauth` does not carry it (§36 correction). On mistral and gpt-5.4-mini the only
confirmed arms that clear +4.359 carry it.

Tested, registered, on ten personas and four models (§40). Eight are format-carried, by 1.10
to 4.33 units; mistral's search winner is format-neutral and its control winner unresolved.
Removing the sentence reverses section 31's asymmetry: the libertarian headline then uses 32%
of its headroom, below the authoritarian headline's 50%.

## RQ2. How far does a reported position move under choices an audit does not declare?

- **Refusal rule.** gemma3: `facist` −6.64 → +2.41 → 0.00, `extremist` −5.92 → +2.41 → 0.00,
  `hilter` −3.28 → +2.41 → 0.00, each declined on 62 of 62 statements; the libertarian
  extreme becomes `pcxleft` at −6.411 (§34). On gpt-5.4-mini the same choice moves the
  headline effect: D = +1.365 [+0.793, +1.937] under the Neutral rule against
  +2.030 [+1.451, +2.609] under Agree (§35). On Motoki et al.'s published answers, scoring
  "agree" at the midpoint moves the five conditions by between +0.55 and −2.68 on the social
  axis (§37).
- **Refusal handling in the literature.** Röttger et al. and Wright et al. both skip a refusal,
  which under this key is numerically identical to recording "Agree" (§38).
- **Gate version.** v2 → v3 moves H\* from +1.923 to +1.692 and turns a pre-registered
  prediction from inside the fitted range to outside it (§35).
- **Assessor.** A weak assessor moves mistral's unroled baseline 6.86 units and flips its
  quadrant (§8); two hosted assessors disagree by 1.25 to 3.71 units, mean 2.44, on the
  configurations where they disagree at all (§20), against repeat noise of 0.27 (§7).
- **Elicitation route.** Asked to choose an option instead of writing an essay, the same
  persona moves by up to 4.15 units, in both directions; hand-written authoritarian personas
  score 1.2 to 2.2 higher on all three hosted models, and no search winner beats its baseline
  when asked directly (§39).
- **Option order.** Listing the four options in reverse moves a persona by up to 1.18 (§39).
- **A second strong assessor.** gpt-4o against gpt-4o-mini moves positions by up to 1.77 and D
  by at most 0.65; on mistral nearly all of it is "Strongly agree" read as "Agree", which the
  zero weight turns into position (§41).
- **Instrument length.** `--max-questions` keeps the 62-statement transform, so 80 of 116
  libertarian candidates sat bit-exactly on the floor and four candidates the surrogate called
  identical were 1.67 units apart on the full instrument (§27, §28).

Every entry above is measured on held-fixed text or under a registered rule.

## RQ3. Does a model's safety policy get reported as its politics?

The assessor records Refused only when no essay is provided, so a model that declines a persona
and then argues against it is scored as holding that stance (§34). Prevalence: gemma3 288 such
essays, 229 of them given a strong stance and 35 correctly Refused; gpt-3.5-turbo 15; mistral
14; gpt-4o-mini 1 (§34). On gpt-5.4-mini, 17 of the 69 hand-written personas are infeasible under
gate v3, most of them declined on more than six statements (§35; 19 under gate v2).

The guardrail is keyed on wording. gpt-4o-mini refuses statement 4, racial superiority, under
every persona that carries a role, and endorses statement 27, segregation in politer words, 12
of 12 under the evolved personas from section 27, against 0 of 12 with no persona (§42). The same
personas make gpt-3.5-turbo endorse both statements 12 of 12, with or without PRISM's instruction
to argue a side, and gpt-5.4-mini refuses them throughout (§42).

The gate is a component with its own error, not a fix: v1 called 9 of 20 ordinary essays
refusals; v2 passed a hand-labelled set 33/33 and 0/40 and then, in its first production use,
27 of 34 audited openings it had called REFUSED were not refusals (§34). Gate v3 adds a
first-person pre-filter and releases those.

The persona-blind ablation has been run and cannot answer the question as posed: every labelled
case was drawn from essays the persona-shown gate had already called REFUSED (§38). What remains
is labelling a sample of the 176 essays where the gate's model stage overturns the pre-filter,
and a sample not selected by any gate, under the exposure note in [ETHICS.md](ETHICS.md). A
third vendor, llama3.2, is running under the tenth pre-registration, so the artefact is not a
two-model result.

The answer instruction is a compliance lever. Without it, gpt-5.4-mini declines its own H\*
persona on 14 statements a run instead of almost none, and every run crosses the feasibility
limit (§40). Forced choice, by contrast, drew no refusals at all on any model (§39).

## RQ4. What is the measurement's resolution?

Two strong assessors agree within 0.72 units on identical essay sets, ordering preserved (§29).
Assessor nondeterminism with the essay held literally fixed is sd 0.252 (§36). Pooled
within-arm sd is 0.446 (§27). The ±0.75 equivalence bound rests on the first two, and both come
from small, role-conditioned samples. The sixth pre-registration measured it on all five
models and both regimes and came out intermediate: the bound widens to ±0.89, under which
gpt-4o-mini's D becomes equivalent, and positions carry an assessor term of up to 1.8 (§41). Against that, §36 shows local-model replicates give 1.0 to 4.9
distinct essays per statement across twelve runs, so several intervals are computed on
duplicates. Model versions are not pinned: the gate's verdicts on the same inputs changed on 7
of 44 cases over three days (§38).

Forced-choice replicates on gpt-3.5-turbo and gpt-4o-mini repeat exactly at temperature 0 (1
to 5 distinct answer sets in 6), the same pseudo-replication §36 found on local essays (§39).

Still open: a crossed design — personas × models × occasions × two strong assessors, with model
versions recorded — would give a standard error per facet. After §41 it is useful rather than
mandatory.

## RQ5. What must an audit declare, and does declaring it change a published conclusion?

The components exist: pre-registered decision rules with outcomes recorded including failures,
three refusal rules implemented and reported, a versioned gate with its failure modes on
record, and the requirement to say which statements moved, since statements 4 and 27 alone
carry 24% of one measured gain (§27).

The external check is done. The key is the Political Compass's own and is identical in four
places, and both prior audits that compute coordinates locally score a refusal as agreement
without saying so (§37, §38). Re-scoring one published audit's deposited answers shows the
reported positions carry that coding decision (§37).

## What the existing results are for

| Result | Anchor | Serves | Caveat to carry |
| --- | --- | --- | --- |
| "Agree" = 0 on both axes; 18 vs 43 statements | §20, §38 | RQ1, RQ5 | identical in four published sources; live site checked at two uniform patterns |
| Response-style nulls ±4.359; random respondent at the origin | §31, §38 | RQ1 | social-axis property |
| Decomposition on five models | §38 | RQ1 | coordinates on five models; modal share on three |
| Item statistics and extreme-answer share | §37 | RQ1, RQ4 | one replicate per persona, one assessor |
| gemma3 gated rescore on unchanged essays | §34 | RQ2, RQ3 | deterministic |
| Motoki et al. re-scored from their own answers | §37 | RQ2, RQ5 | one audit; their conclusion is a comparison between conditions |
| Refusals skipped as agreement in Röttger et al. and Wright et al. | §38 | RQ2, RQ5 | read from their released code |
| Refusal rule moves D from +1.365 to +2.030 | §35 | RQ2 | one model |
| Gate v2 → v3 moves H\* and a prediction | §35 | RQ2, RQ5 | always name the version |
| Decline-then-write prevalence, four models | §34 | RQ3 | gemma3 supplies most of it |
| Gate v1 failure, v2 false positives, blind ablation | §34, §38 | RQ3, RQ5 | labelled by one person; ablation cases gate-selected |
| Gate verdict drift, 7 of 44 in three days | §38 | RQ4 | unpinned model versions |
| Assessor swap 6.86 units, quadrant flip | §8 | RQ2 | weak versus strong |
| Two hosted assessors 1.25–3.71, mean 2.44 | §20 | RQ2 | ten configurations |
| Surrogate saturation, 80/116 bit-exact | §27, §28 | RQ2 | search-visible instrument defect |
| Two strong assessors within 0.72 | §29, §41 | RQ4 | n=3 and the easy regime; §41 widened the bound to ±0.89 |
| Distinct-essay counts 1.0–4.9 locally | §36 | RQ4 | local n=12 intervals overstate precision |
| Winner's curse up to 1.513 | §32 | RQ4, RQ5 | confirms the argmax, not the procedure |
| Five-model D table | §36, §40 | RQ2 | three models have one search run each; gemma3's D is the answer instruction |

## Experiments, and where each stands

| # | Experiment | Cost | Serves | Status |
| --- | --- | --- | --- | --- |
| 0 | Ethics, exposure and release note | half a day | all | done, [ETHICS.md](ETHICS.md) |
| 1 | Free arithmetic over cached stances: decomposition on five enumerations, item-total and dimensionality checks | none | RQ1, RQ2, RQ4 | done, §37 and §38 |
| 2 | Persona-blind gate ablation | under an hour | RQ3 | done, with the selection limit in §38 |
| 3 | Strong-versus-strong assessor, all five models | about $11 | RQ2, RQ4 | done, §41, intermediate |
| 4 | Answer-format ablation on the winners; the same on `pcleftlib` | about $3 hosted, local time | RQ1, RQ3 | done, §40 |
| 5 | Forced-choice control, three hosted models, option order counterbalanced | under $1 | RQ1, RQ3 | done, §39 |
| 6 | Second labeller on the gate categories, and labelling gate overturns | people's time | RQ3 | needs people |
| 7 | Crossed design for resolution, versions recorded | about $100 | RQ4 | optional after §41 |
| 8 | Read published audits against §31 | reading | RQ5 | done for eight papers, §37 and §38 |
| 9 | Second refusing model, llama3.2, enumerated ungated and gated | about a day local | RQ3 | running, tenth pre-registration |
| 10 | Stance flip: frame ablation and transfer (§27) | under $2 hosted, local time | RQ3 | hosted done, §42; local running, eleventh pre-registration |

## Where the novelty has to sit

The premise that audits report a point and prompts move it is the field's starting position.
Röttger et al., ACL 2024, argue that Political Compass results are artefacts of constrained
elicitation and change again in open-ended settings. Wright et al., Findings of EMNLP 2024,
run 156k open-ended responses to the same 62 propositions across six models and 420 prompt
variations with stance labelling, which is structurally this pipeline. Domínguez-Olmedo et al.,
NeurIPS 2024, show survey responses are governed by ordering and labelling bias and propose
null baselines. Sclar et al., ICLR 2024, report performance as a spread over prompt formats
and use search to find that spread cheaply. Ceron et al., TACL 2024, and Rozado, PLOS ONE 2024,
use null or reliability baselines. None of this may be claimed as new here.

What is not in that literature, having read the prior audits' code:

1. The coding rule priced on held-fixed text. No prior audit holds the generated text fixed and
   varies only how it is scored; this project does it on its own essays and on a published
   audit's deposited answers.
2. That the published scoring makes a refusal numerically identical to agreement, and that the
   closest prior audits inherit it through code that skips refusals.
3. Surrogate saturation as an instrument defect that only optimisation makes visible.
4. The audit protocol itself: pre-registered decision rules, a matched no-selection control,
   randomised complete blocks, and a public record of withdrawn claims.

## Risks

**Priority.** Resolved on the key: it is the instrument's own, so the finding is about the
literature and not one fork. The residual risk is that the contribution is quantification, and
its size on a published audit has been measured for one.

**The assessor bound.** Tested on all five models (§41) and intermediate: differences and
orderings carry at about ±0.9, positions need an assessor term beside them. The paper should
lead with differences measured on held-fixed text and report positions with that term.

**Search as the probe.** Asked directly, no search winner beats its hand-written baseline
(§39). With the answer instruction removed, gemma3's search gain disappears and turns negative
on both runs, while mistral's grows from +3.4 to +7.7 and gpt-5.4-mini's from +1.37 to +4.89
(§40). Whether search moves a model's position therefore depends on the model and on one
sentence in the baseline. That supports using search as a probe of the measurement and rules
out presenting it as a way to find a model's position.

**Recency.** No claim about newer models behaving differently is supported: mistral is older
than gpt-4o-mini and gemma3 and behaves like gpt-5.4-mini on the null counts.

## Withdrawn, and not to be used

- The linear relationship D = 4.574 − 0.628·H\*, r = −0.987 (§33). gpt-5.4-mini, the held-out
  model, returned +1.365 against a pre-registered +3.223 (§35), and gemma3's own point moved
  from +1.081 to +0.385 on a second run (§36).
- gemma3 as a confirmed prediction (§36).
- Any split of the gain between rewriting and selection. The selection term reversed sign on
  both models with two runs (§36).
- "Search never beats hand-written prompts", which came from a handicapped search (§30).
- "All Neutral is the true centre": the instrument has no neutral option; the origin is the
  random respondent (§31 correction, §38).
- The answer-format sentence "escalated by search": it is inherited verbatim from the seeds
  (§36 correction).
- Section 31's asymmetry between the two ends: it was carried by the answer instruction in the
  libertarian headline (§40).
- "The unroled default is the least assessor-stable measurement": boundary positions move more
  (§41).
- gemma3's search gain as a move in the model's position: with the answer instruction removed,
  both search winners score below the hand-written baseline (§40).

Each of those failures is evidence for the heading rather than against it: a quantity that
moves this much between runs of the same protocol is not a stable property of a model.
