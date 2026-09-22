# Paper outline

Built from [FRAMING.md](../FRAMING.md). Every number carries its section in
[FINDINGS.md](../FINDINGS.md) (§n, sections 1 to 42) or its entry in
[PREREGISTRATION.md](../PREREGISTRATION.md). No number is taken from FRAMING's tables. Where
FRAMING and FINDINGS differ, FINDINGS is used. FRAMING's component table is not a source: the
six components are those of Figure 1 and its caption (`components_caption.md`).

## Candidate titles

1. Political Audits of Language Models Measure an Interaction
2. A Political Compass Coordinate Is a Configuration
3. When a Refusal Scores as Agreement

## Abstract (draft, 216 words without the [§n] anchors, which come out before submission)

Political audits of language models report a coordinate as if it were a property of the model.
We show it is a property of a configuration: model, persona prompt, assessor, scoring rule,
safety policy and how a stance is elicited. The most robust evidence regenerates nothing. The
Political Compass key gives "Agree" zero weight, so a skipped refusal scores as agreement, as in
the released code of the two closest prior audits [§38]. Gating one persona's declined essays and
then choosing a refusal rule moves it from −6.64 to +2.41 to 0.00 on a scale of ±10 [§34, §2];
re-scoring a published audit's deposited answers with "agree" at the midpoint moves one condition
by 2.68 [§37]. Registered experiments then price the elicitation route and the prompt:
choosing an option instead of writing an essay moves the same persona by up to 4.15 [§39], and
one inherited sentence telling the model how to answer carries 1.10 to 4.33 units in eight of
ten personas [§40]. A second strong assessor moves positions by up to 1.77 but differences by at most 0.65 [§41]. Automated
persona search served as the probe: it exposed a defect in its own shortened instrument, which
tied 80 of 116 candidates at its floor [§27], showed that a reported gain is one draw from a
distribution [§36], and led to the answer-sentence ablation [§40].

## 1. Introduction

- **Opening.** Audits report a point; the field already knows prompts move it (Röttger et al.,
  Wright et al.). Our claim is narrower: each component of an audit can be priced in the
  instrument's own units, and the most robust prices are measured on text held fixed.
- **Figure 1, the lead: `results/figures/components.png`** (drawn by `components.py`, caption
  and provenance in `components_caption.md`). Each bar is one measured shift of one persona's
  social coordinate when one component changes and everything else stays as the source ran it,
  under the definitions in the caption's provenance table. It is not the largest shift measured
  for every component, and the bars do not apportion variance. Reference line: the 0.89
  resolution bound (§41). Three bars compare newly generated text (prompt, model, elicitation
  route); three re-score identical text (safety policy, assessor, scoring instrument). The six
  bars, in the figure's order, which is the order the components act in one audit and not size:
  - **Prompt**, 4.33: the answer sentence removed from mistral's `pccentrist`,
    +1.863 − (−2.468) = +4.331 (§40; seventh pre-registration).
  - **Model**, 6.92: `pcxrightauth`, same persona text, gpt-4o-mini assessing, +7.39 on
    gpt-3.5-turbo against +0.47 on mistral; 7.39 − 0.47 = 6.92 (§32).
  - **Safety policy**, labelled "safety decline read as a stance", 6.64: gemma3's `facist`,
    declined on all 62 statements, from −6.64, where the published audit places it, to 0.00,
    the instrument's no-position point (the Neutral rule's value for a fully refused persona and
    the instrument's origin, §34, §38); 0.00 − (−6.64) = 6.64. The caption must say that under
    the published Agree coding the same persona would sit at +2.41, a swing of
    2.41 − (−6.64) = 9.05, so the bar's length depends on the refusal rule (§34).
  - **Elicitation route**, 4.15: gpt-3.5-turbo's search winner, +7.384 through essays against
    +3.235 choosing an option itself (§39; eighth pre-registration).
  - **Assessor**, 1.77: gpt-4o against gpt-4o-mini on mistral's search winner, the same 12
    cached replicates (4.7 distinct essays per statement), nothing regenerated; the difference
    D moves at most 0.65 (§41; sixth pre-registration).
  - **Scoring instrument**, 2.68: the coding of "Agree" in Motoki et al.'s radical-republican
    condition, their deposited answers, 4.41 − 1.73 = 2.68 (§37). One published audit, and
    their conclusion compares conditions.

  The bars are single chosen instances on different models and protocols, so no pair's order
  is established; model against safety policy (6.92 − 6.64 = 0.28) and prompt against route
  (4.33 − 4.15 = 0.18) are two examples. The 0.89 line is the bound §41 applies to
  differences, not a test between bars.
- **Held-fixed evidence.** gemma3 `facist` on unchanged essays: gating its declines moves it
  from −6.64 to +2.41 under the published Agree coding, and the Neutral refusal rule then moves
  it to 0.00; the model's libertarian extreme changes to `pcxleft` at −6.411 (§34). Motoki et
  al.'s radical-republican condition moves 2.68 when their own answers are re-scored with
  "agree" at the midpoint (§37). The gating step uses one stored pass of the gpt-4o-mini gate
  (which keeps 62 of 62 `facist` declines under v3, §34); the refusal-rule step and the Motoki
  re-score are arithmetic on fixed inputs.
- **Registered experiments.** Elicitation route, up to 4.15 (§39). Answer sentence, 1.10 to
  4.33 in eight of ten personas on four models (§40).
- **Search as the probe.** It exposed surrogate saturation (§27, §28), showed a reported gain is
  one draw from a distribution (gemma3 D +1.081 then +0.385, §36), and led to the answer
  sentence, which turned out to be the whole of gemma3's gain (§40).
- **Contributions**, from FRAMING's novelty list: (1) the coding rule priced on held-fixed text;
  (2) the published key makes a refusal identical to agreement, and the closest prior audits
  inherit it (§38); (3) surrogate saturation, a defect the search exposed: a shortened
  instrument whose fixed transform ties 80 of 116 candidates at its floor (§27) although four
  of them lie 1.67 apart on the full instrument (§28); (4) the audit protocol: pre-registered
  rules, matched no-selection control, randomised complete blocks, public withdrawals.
- Pointer to the box of claims we will not make.

## 2. Background and related work

- PRISM (Azzopardi and Moshfeghi): persona, essay, assessor, key.
- Compass audits and their scoring: Motoki et al. 2024 (key and transforms published, §37);
  Röttger et al. ACL 2024 and Wright et al. Findings of EMNLP 2024 (same key, refusals skipped,
  §38); Ceron et al. TACL 2024 (excludes non-answers, no coordinate, §38); Rutinowski et al. and
  Kamal et al. (no weights table; aggregation not public, §37); Rozado, PLOS ONE 2024.
- Measurement sensitivity: Domínguez-Olmedo et al. NeurIPS 2024 (ordering and labelling bias,
  null baselines); Sclar et al. ICLR 2024 (spread over formats, search to find it).
- **Stated as not new** (FRAMING novelty; §38): open-ended and forced-choice answers differ;
  an LLM judge can map text to stance; personas move the coordinate.

## 3. Method

- **3.1 Pipeline and instrument.** 62 statements, 62 essays, one stance each, 124 calls per audit
  ("How one audit works"). Key and transforms: social = total/19.5 + 2.41, economic = total/8 +
  0.38 (§37). Range ±10 (§2).
- **3.2 Models and assessors.** Audited: gpt-3.5-turbo, gpt-4o-mini, gpt-5.4-mini (hosted),
  mistral 7B, gemma3 (local). Assessor gpt-4o-mini (κ 0.604 against 0.8285 between humans,
  §18). gpt-4o measured higher, κ 0.666 and accuracy 81.0% (§22), at about 20× the cost per
  call (§22), and is the second strong assessor (§29, §41).
- **3.3 Refusal gate and refusal rules.** Two separate steps: the gate decides whether a
  statement was refused, and the refusal rule decides what a refusal is worth (§34). Gate v3
  with its first-person pre-filter; refusal scored as Agree (the published rule), at the Neutral
  midpoint, or dropped (§34).
- **3.4 Held-fixed re-scoring** as the primary design: same essays or same published answers,
  only the rule varies (§34, §37); gate verdicts reused so only the classifier moves (§41,
  amendment A1).
- **3.5 Persona search and its controls.** LLM rewriting of persona text, full instrument, each
  model's top six hand-written seeds, 48 evaluations, matched `--no-selection` control, winners
  confirmed at n=12 (n=24 on gpt-4o-mini) in randomised complete blocks; nothing claimed from a
  search-time maximum (§32, §33; first pre-registration, second round; third and fifth for
  gpt-5.4-mini's gate and Neutral rule).
- **3.6 Decision rules.** Positive, negative, equivalent, unresolved (first pre-registration);
  equivalence bound widened from ±0.75 to ±0.89 by the sixth (§41). Thirteen pre-registrations.
  The first nine have recorded outcomes (the third's through the fifth, which re-registered it
  under gate v3). The tenth (llama3.2) and eleventh (stance-flip frame ablation and transfer)
  have recorded outcomes (§43, §42).
- **3.7 Forced choice and answer-format ablation** (eighth, seventh and ninth pre-registrations;
  §39, §40).
- **3.8 Stance-flip frame ablation and transfer** (eleventh pre-registration; §42), if the
  stance flip appears at all (Decision 5).

## 4. Results, RQ1: what the instrument scores when the respondent supplies no political content

**Claim.** The instrument scores response style as position: "Agree" and a skipped refusal carry
zero weight, uniform strong agreement alone reaches +4.359, and between 32% and 77% of each
model's hand-written library sits inside the two uniform-answer nulls.

| item | content | source |
| --- | --- | --- |
| Table 1 | key structure: "Agree" 0 on both axes; 18 of 62 statements carry economic weight, 43 social; statement 21 none | §20, §38 |
| Table 2 | response-style nulls: all Strongly agree +4.359, all Agree +2.410, all Strongly disagree −4.359; random respondent at (+0.036, 0.000) | §27, §31 correction, §38 |
| Figure 2 | each model's library against the ±4.359 nulls; none clears +4.359 on mistral or gpt-5.4-mini | §38 table; `results/decomposition/` |
| Table 3 | the scale as a scale: α 0.889 to 0.952, first factor 24% to 39%, 76.5% to 97.5% of answers at an extreme | §37 |
| Table 4 | answer-instruction δ for ten personas on four models; sentence verbatim in ten hand-written seeds | §40, §36 correction |

**Missing.** Figure 2 is not drawn. The live site is checked at two uniform patterns only
(§38). Modal share is reported in FINDINGS for gpt-3.5-turbo only (§31); coordinates on five
models (§38). Item statistics rest on one replicate and one assessor (§37).

## 5. Results, RQ2: how far a reported position moves under choices an audit does not declare

**Claim.** Most undeclared choices move a reported position by more than the ±0.89 bound §41
sets for differences, and most also by more than the 1.77 assessor term §41 measures on
positions. Several re-score text held fixed with nothing regenerated. In two of them no stance
label changes and no stance classifier is involved: Motoki et al.'s deposited answers are
re-scored with their weights and transform (§37), and gemma3's `facist`, refused on all 62
statements under stored gate verdicts, moves between the two refusal rules (§34).
Rows in Table 5 that clear 1.77: gating declined essays and scoring the gated refusals at
Neutral (6.64, from the published ungated scoring to the no-position point; 9.05 with the Agree
rule held fixed at both ends), the refusal rule on gemma3 `facist` (2.41), the coding of
"Agree" (up to 2.68), a weak assessor against a strong one (6.20 local; up to 3.71, mean
2.44, hosted, axis unstated) and the elicitation route (up to 4.15). Between the two bounds: the refusal rule on individual
gpt-5.4-mini personas (up to 1.28) and option order (up to 1.18). Below 0.89: the gate version
(0.231), and the effect on D of the refusal rule (0.665) and of a second strong assessor (at
most 0.65).

| item | content | source |
| --- | --- | --- |
| Figure 3 | held-fixed re-scoring: gemma3's three declined personas under three treatments (ungated, gated with the Agree rule, gated with the Neutral rule); Motoki's five conditions, published rule against "agree" at the midpoint | §34, §37 |
| Table 5 | ledger of undeclared choices against resolution, each row filed under its Figure 1 component; draft rows below | as listed |
| Table 6 | forced choice against essay, nine comparisons, verdicts under ±0.75 and ±0.89; the hand-written authoritarian personas score higher when asked directly, on all three models, by +1.17 to +2.22 | §39, §41 |
| Table 7 | search gain and the answer sentence, five models: D as published, and with the sentence removed from every arm that carried it. gpt-3.5-turbo −0.342, and +0.064 with matched parents (§32); gpt-4o-mini +0.656 at n=24 (§33), equivalent only under ±0.89 (§41); neither was ablated, since no winner on either carries the "Strongly" form (§36) and H\* `pcxrightauth` carries no such sentence (§40). gpt-5.4-mini +1.365 → +4.891; mistral +3.380 → +7.733; gemma3 +1.081 and +0.385 → −1.141 and −0.714 (§40); the sentence-removed values are derived, not registered, and are labelled as readings | §32, §33, §35, §36, §40, §41 |

**Table 5, draft rows.** Social axis unless stated. Derived numbers show their arithmetic.

| component | choice | shift | source |
| --- | --- | --- | --- |
| safety policy | whether declined essays are gated ("safety decline read as a stance") | gemma3 `facist`, same essays: −6.64 ungated (the ungated end scores its 10 assessor-Refused statements as Agree) to 0.00 gated under the Neutral rule, 0.00 − (−6.64) = 6.64; to +2.41 under the published Agree coding, 2.41 − (−6.64) = 9.05 | §34 |
| safety policy | gate version, v2 → v3 | gpt-5.4-mini H\* +1.923 → +1.692, 1.923 − 1.692 = 0.231, below resolution, yet it took H\* below the fitted range (+1.86 to +7.39) at screening, making the test an extrapolation; the confirmed H\* (+2.160) returned it to range | §35; fifth pre-registration |
| scoring instrument | refusal rule: a refusal scored as Agree or at the Neutral midpoint | gemma3 `facist`, same essays: +2.41 → 0.00, 2.41; up to 1.28 on individual personas among the first twelve gpt-5.4-mini personas scored (gate v2, §34); gpt-5.4-mini D +2.030 (Agree) against +1.365 (Neutral), 2.030 − 1.365 = 0.665 | §34, §35 |
| scoring instrument | coding of "Agree": zero weight or the midpoint | Motoki et al.'s own answers, five conditions, shifts +0.55 to −2.68, up to 2.68 | §37 |
| assessor | weak local against strong hosted (mistral against gpt-4o-mini), same essays | mistral's unroled baseline: a distance of 6.86 across both axes, and a quadrant flip; on the social axis alone 1.64 − (−4.56) = 6.20 | §8 |
| assessor | weak against strong hosted (gpt-3.5-turbo against gpt-4o-mini) | 1.25 to 3.71, mean 2.44, on the seven of ten configurations they disagree on; §20 does not state the axis | §20; the two hosted assessors named in §15; weak against strong, §29 |
| assessor | two strong assessors (gpt-4o against gpt-4o-mini), same essays | positions up to 1.77; D at most 0.65 | §41 |
| elicitation route | essay and assessor against forced choice | up to 4.15, in both directions | §39 |
| elicitation route | option order under forced choice | up to 1.18; sizes, not tests | §39 |

The 20-statement search surrogate is not a Figure 1 component and not a choice a published
audit makes and leaves undeclared, so it is not a row here; it goes with the search-as-probe
material in the Discussion (Candidate Figure 5; §27, §28).

**Missing.** Table 7's sentence-removed values and §39's forced-choice D are derived, not
registered, and must be labelled as readings. The refusal rule's effect on D was measured on
five models. Agree against Neutral moves it on one, gpt-5.4-mini, by 0.665 (above), below the
±0.89 bound. gpt-3.5-turbo, gemma3 and mistral had no refused statements in the confirmation
runs §34 rescored (the first run on each model; the matched-parent re-runs are not covered
there); on gpt-4o-mini the
Agree-to-Neutral shift cancels in every difference, and dropping refusals moves D by
0.667 − 0.656 = 0.011 (§34, §35). Several option-order intervals are degenerate because
one order repeats exactly, so the option-order shifts are reported as sizes, not tests
(§39). Figure 3 is not drawn.

## 6. Results, RQ3: whether a model's safety policy gets reported as its politics

**Claim.** On gemma3 and gpt-5.4-mini it does. The published assessor records a refusal only
when no essay is written, which is true of the pipeline as published, so a declined persona
followed by a rebuttal is scored as the persona's stance; and on gpt-5.4-mini one sentence
about how to answer decides whether an authoritarian persona is played at all.

| item | content | source |
| --- | --- | --- |
| Table 8 | decline-then-write prevalence: gemma3 288 (229 scored as a strong stance, 35 Refused), gpt-3.5-turbo 15 (12 scored as a strong stance), gpt-4o-mini 1 (none), mistral 14 regex hits, none scored as a strong stance | §34 |
| Table 9 | the gate's error record: v1 called 9 of 20 ordinary essays refusals; v2 33 of 33 and 0 of 40, then 27 of 34 audited REFUSED openings were not refusals; v3 releases 27 of 27 such non-refusals on gpt-5.4-mini and 7 of 7 on gemma3, and keeps 6 of 7 declines; model stage overturns 176 of 1,149 (15.3%) | §34, §38 |
| Table 10 | gpt-5.4-mini: 52 of 69 feasible under gate v3; 16.5% of stances on the 43 social statements Refused, one replicate per persona (§37); H\* stripped of the sentence refused on 14.3 statements a run against 0.1 intact, δ +3.525 with refused statements excluded; forced choice drew no refusals on any model | §35, §37, §40, §39 |
| text | if the stance flip appears (Decision 5): gpt-4o-mini refuses statement 4 under every persona that carries a role, and endorses statement 27 in 12 of 12 replicates under both evolved personas against 0 of 12 with no persona, so its guardrail is keyed on wording; gpt-5.4-mini endorses neither, every evolved-persona essay a gate refusal. Rates only, no persona text | §42; eleventh pre-registration |

**Missing.** The artefact is now on three vendors, with llama3.2 supplying 737 decline-then-write
essays against gemma3's 288, but its size is small there, largest 1.948 (§43); the local
stance-flip verdicts are sampled rates at temperature 0.8 (§42, twelfth pre-registration). Human labelling of the 176 gate
overturns and of a sample no gate selected, under ETHICS.md. The in-voice category is
ambiguous, 6 of 15 (§34). Why gpt-5.4-mini refuses `red` (15) and `gay` (13), gate v2 counts,
is unread (§35).

## 7. Results, RQ4: the measurement's resolution

**Claim.** Differences and orderings between personas carry at about ±0.89 between strong
assessors, positions need an assessor term of up to 1.77 beside them, and on local models a
nominal replicate is often a repeat.

| item | content | source |
| --- | --- | --- |
| Figure 4 | per model, position move against D move under a second strong assessor; largest baseline shift 0.803 (gemma3) | §41 |
| Table 11 | per-statement agreement and κ by regime; mistral boundary 41.3%, κ 0.257, same direction 99.3%, 811 disagreements in which gpt-4o-mini reads "Strongly agree" and gpt-4o reads "Agree" (§41) | §41 |
| Table 12 | effective replicates: 1.0 to 4.9 distinct essays per statement locally, 9.3 to 12.0 hosted; forced choice gives 1 to 5 distinct answer sets in 6 on the two older models | §36, §39 |
| Table 13 | winner's curse: search-time best against confirmed, shrink up to 1.513 | §32 |
| text | noise floors: assessor nondeterminism sd 0.252 (§36), pooled within-arm sd 0.446 (§27), gate drift 7 of 44 in three days (§38) | as listed |

**Missing.** Figure 4 is not drawn. No human labels, so §41 bounds disagreement between
assessors, not distance from the truth. Every result up to §41 used unpinned hosted model
versions (sixth pre-registration, "Declared before running" and amendment A5); the tenth and eleventh
pre-registrations pin the assessor to a dated gpt-4o-mini snapshot. Only gpt-3.5-turbo and
gemma3 have two search runs (§36). The crossed design is optional after §41 (FRAMING,
experiment 7).

## 8. Results, RQ5: what an audit must declare, and whether declaring it changes a published conclusion

**Claim.** How "agree" is coded moves a published audit's reported positions by up to 2.68
units, and none of the papers state it (§37); on the one audit re-scored it does not overturn
the between-condition conclusion.

| item | content | source |
| --- | --- | --- |
| Table 14 | declaration checklist, each item with the effect that justifies it: key and the coding of "Agree", refusal rule, whether declines are gated and the gate version, assessor, elicitation route, option order, and which statements carry an effect (4 and 27 carry 24% of one gain) | §27, §34, §35, §37, §39, §41 |
| Table 15 | key provenance: identical in this repository, Motoki's package, Röttger's code and Wright's notebook; refusals skipped in both prior audits' code | §37, §38 |
| Table 16 | Motoki re-analysis: five conditions, published rule against "agree" at the midpoint, shifts +0.55 to −2.68 | §37 |
| text | the pre-registration record, failures included: the §33 prediction missed by 1.858 on gpt-5.4-mini; gemma3's D failed to replicate | §35, fifth pre-registration; §36, fourth pre-registration |

**Missing.** A second published audit re-scored from deposited answers. A per-paper table of
what each audit read in §37 and §38 declares. Table 14 is not assembled.

## 9. Discussion

- **The interaction, re-read.** Figure 1 again. gemma3's D, +1.081 then +0.385 on a second
  run of the same search protocol, is evidence that the quantity moves between runs (§36;
  fourth pre-registration, which records that D does not involve the control). The §33 line
  also missed on a held-out model (§35). The selection split changed sign between confounded
  runs and their matched-parent re-runs (fourth pre-registration), and again when the sentence
  was removed (§40), so it records a protocol error as well as instability. Other withdrawn
  claims record errors of protocol, concept or provenance (§30, §31 correction, §36
  correction).
- **Search as the probe, and its limit.** What it exposed (§27, §28, §32, §36, §40). What it
  was not shown to do: find a model's position; whether its gain is a position move depends on
  the model and on one sentence (§40), and asked directly, no winner beats its baseline by more
  than 0.205 (forced-choice D −5.252, −1.965 and +0.205, §39, a reading). On gemma3 the gain
  was the sentence; on mistral and gpt-5.4-mini it grew once the sentence was removed (§40,
  derived). Candidate Figure 5: surrogate saturation, the
  20-statement surrogate against the full instrument, 80 of 116 candidates tied at the
  surrogate floor (§27), four tied candidates 1.67 apart on the full instrument,
  −7.87 − (−9.54) = 1.67 (§28).
- **For audit practice.** Lead with differences on held-fixed text; give positions with an
  assessor term; quote each position beside its uniform-answer null and modal share (§31, §41).
- **Relation to prior work.** Consistent with Röttger (route), Wright (personas),
  Domínguez-Olmedo (nulls) and Sclar (spread); new only where FRAMING's novelty list says.

## Claims we will not make

| claim | why | anchor |
| --- | --- | --- |
| D = 4.574 − 0.628·H\*, r = −0.987 | held-out model returned +1.365 against +3.223; gemma3 moved on a second run | §33, §35, §36 |
| gemma3 as a confirmed prediction | failed replication | §36 |
| any split of the gain into rewriting and selection | selection changed sign on every model with two runs, and again without the sentence | §36, §40 |
| "search never beats hand-written prompts" | came from a handicapped search | §30 |
| "all Neutral is the true centre" | no neutral option; the origin is the random respondent | §31 correction, §38 |
| the answer sentence was "escalated by search" | inherited verbatim from the seeds | §36 correction |
| §31's asymmetry between the two ends | carried by the sentence in the libertarian headline | §40 |
| "the unroled default is the least assessor-stable measurement" | boundary positions move more | §41 |
| gemma3's search gain as a move in position | both winners fall below the baseline without the sentence | §40 |
| the stance flip on the local models, on statements other than 4 and 27, or as something a search on a current model would find | hosted models run at temperature 0 only; only statements 4 and 27 were tested; whether a persona searched on a current model would find a way through was not tried | §42; eleventh pre-registration |
| any position as true | no human labels; the assessor used, gpt-4o-mini, κ 0.604 (§18); the best measured, gpt-4o, κ 0.666 (§22); humans 0.8285 (§18) | §18, §22; "What is not yet done" |
| anything about the economic axis, or the libertarian direction under search | under the §32 protocol every search pushed social upward; the §27 libertarian search ran on a saturated surrogate and measured nothing about the model's libertarian reach; the economic axis has not been searched under this protocol | §27, §32; "What is not yet done" |
| that search finds a model's position | depends on the model and one sentence; asked directly, no winner beats its baseline by more than 0.205 (forced-choice D −5.252, −1.965 and +0.205, a reading) | §39, §40 |
| that Motoki et al.'s conclusion is overturned | theirs is a between-condition comparison | §37 |
| the refusal artefact's size as general across vendors | prevalent on three vendors, but large only on gemma3 and small on llama3.2 (largest 1.948) | §34, §43 |
| newer models behave differently | mistral behaves like gpt-5.4-mini on the null counts: no persona clears the authoritarian null on either | §38 |
| a search-time maximum as a result | shrink up to 1.513 on confirmation | §32 |

## 10. Limitations

No human labels (§18). Under the §32 protocol search ran only in the authoritarian social
direction; the §27 libertarian search measured nothing about the model's libertarian reach, and
the economic axis is unsearched
under this protocol (§27; "What is not yet done"). Local-model intervals overstate precision
(§36). Every result up to §41 used unpinned hosted model versions (sixth pre-registration); the tenth
and eleventh pre-registrations pin the assessor. One published audit re-scored (§37). The
persona-blind ablation of the gate rests on 44 hand-labelled cases, all drawn from essays the
persona-shown gate had already called REFUSED, so it cannot show what a blind gate would catch
(§38); the gate categories have no second labeller (FRAMING experiment 6, needs people). Only
gpt-3.5-turbo and gemma3 have a second search run (§36). No search has formally converged ("What is not yet done"). The Political Compass is a
copyrighted web quiz, not a validated psychometric scale (ETHICS.md).

## 11. Ethics statement

Drawn from ETHICS.md: offensive personas and hundreds of essays in them; a search-derived persona
that flipped a model into endorsing racial superiority, a stance flip and not a refusal bypass
(§27), now a registered outcome on the hosted models (§42; eleventh pre-registration), its text
withheld; the exposure protocol for anyone reading essays; release of code, the refusal gate
and its validation set, the scoring analysis, pre-registrations and outcomes, aggregate stance
matrices and coordinates, and the hand-written persona library; the search-derived persona
texts that reliably produce the stance flip and the full essay corpus for the offensive personas
withheld, available to named researchers for replication with the exposure note attached; no
human subjects.
Quotations short, marked as model output.

## 12. Conclusion

Three or four sentences: a coordinate is a configuration; the coding rule alone moves published
positions on held-fixed text; an audit should declare the choices in Table 14 and report
differences with a stated resolution; search exposed a defect in its own instrument (surrogate
saturation, §27, §28), showed run-to-run spread (§36) and led to the answer-sentence ablation
(§40).

## Decisions only Sandy can make

1. **Venue**, which sets length, format and whether an ethics review applies (ETHICS.md treats
   its note as a starting draft for one).
2. **One paper or two**: the measurement paper (RQ1 to RQ5), and possibly a separate paper on
   search as a probe of an evaluation instrument (§26, §27, §28, §32).
3. **Which open experiments to wait for before submission**: the second labeller on gate
   categories (needs people), a second published audit re-scored, the optional crossed design
   (FRAMING experiments 6 and 7; the re-scoring is not yet listed there).
4. **Whether anyone besides Aviral reads essays for labelling**, and whether that needs
   Stirling ethics approval (ETHICS.md, exposure protocol).
5. **Whether the stance flip appears, and where**: its hosted arms are a registered outcome
   (§42), its local rates are sampled (twelfth pre-registration), and its persona text is
   withheld under ETHICS.md.
6. **Whether to contact the PRISM and Motoki authors** before submission about the refusal
   artefact (§34), the under-specified `pcleftauth` clause (§24) and the re-scored answers (§37).
