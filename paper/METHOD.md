# 3. Method

## 3.1 Pipeline and instrument

**Instrument.** The Political Compass test has 62 propositions answered Strongly disagree, Disagree,
Agree or Strongly agree, with no neutral option [§31 correction, §38]. A fixed key weights each
option on each axis, and totals become coordinates on −10 to +10: social = total_social / 19.5 +
2.41, economic = total_economic / 8 + 0.38 [§2, §37]. 43 propositions carry social weight, 18
economic, and statement 21 neither [§20, §38].

**The zero weight on "Agree".** "Agree" scores zero on both axes for every proposition [§2, §37], so
a refusal scored as zero is agreement: PRISM puts a persona refused throughout at social +2.410,
uniform agreement's position [§34], and the released code of Röttger et al. [@rottger2024code] and
Wright et al. [@wright2024code], which share the key with Motoki et al. [@motoki2023replication],
skips refusals, the same thing [§37, §38]. Uniform "Strongly agree" and "Strongly disagree" score
±4.359 on the social axis; positions are reported beside these nulls [§27, §31, §38; first
pre-registration], on the social axis with economic position beside it [§20; first pre-registration,
secondary].

**Essay route.** In PRISM [@azzopardi2024prism] the audited model, the writer, writes one essay per
proposition under a persona; the assessor, which never sees the persona, labels each under the
paper's prompt as one of five stances, among them a Neutral scored midway between Disagree and
Agree, or Refused, tallied through the key [How one audit works; §11, §34; S3.1].

**Prompt.** Every persona enumeration, search, confirmation, answer-format ablation and stance-flip
run, bar Section 3.8's neutral frame, puts the persona's text before the paper's Appendix B prompt,
"Write a short essay about: {topic}." then "Pick one side and argue for or against it." [§1; S3.1]:
the paper frame. PRISM's persona sentence, "Pick the side that aligns with your role and argue for
it.", has an unmeasured effect; early role runs may have used it, and none is reported as a persona
result [§8, §10; tenth pre-registration; S3.1]. "PRISM as published" means the paper's prompt and
scoring on paper-frame essays.

**Decoding.** Writer and assessor run at temperature 0, bar Section 3.8's sampled writer [§7, §27;
twelfth pre-registration]. PRISM's regeneration after a Refused label, which replaces the essay
being scored, is off in every enumeration, persona search, confirmation and re-score [How one audit
works; §9], but not in the separate prompt-fragment driver behind the hosted weak-against-strong
assessor comparison, whose two assessors may therefore have scored different essays [§9, §20; S3.1].
Hosted writers are uncapped in the persona runs listed under Prompt and in forced choice; local caps
are in Supplementary Table 3.1.

**Personas.** The inherited library has 69 non-empty entries of 72 [§27; first pre-registration]. An
enumeration audits each once on the full instrument, adding on every later model two personas from
the early gpt-3.5-turbo persona search (Section 3.5), for 71 [§35, §38; tenth pre-registration]. The
library includes personas named after Hitler and Stalin, and that search produced personas under
which gpt-3.5-turbo endorsed racial superiority, so anyone who reads essays from here on follows
ETHICS.md's exposure protocol [ETHICS.md; §27, §42]. Its release policy withholds those
search-derived texts and the offensive personas' essays; Section 11 states what the release
contains.

> Note for the authors: remove those texts from tracked files, `results/persona_evo_auth.json` among
> them, before release (S3.8).

**Configuration ids.** Essays and ratings are cached under a hash of generation settings, persona
text and prompt label; a run whose id has essays on disk reads them, so a reproduced id proves a
text identical [Practical notes; tenth pre-registration]. The id once omitted the persona text, so
earlier runs' ids, Arm A's baselines among them, are read from stored logs, not recomputed (S3.1).
Replicates differ only in the label, which enters the id, not the prompt.

## 3.2 Models and assessors

The audited models are gpt-3.5-turbo, gpt-4o-mini and gpt-5.4-mini, hosted, and mistral (7B) and
gemma3 (4B) through ollama [§8, §18, §35]; llama3.2 (Meta, 3.2B) is added for the refusal
experiment, the artefact's third vendor, and for stance-flip transfer [§42, §43; tenth
pre-registration]. From the tenth pre-registration on, the assessor is pinned to
gpt-4o-mini-2024-07-18, and the tenth, the eleventh's local arms and the twelfth ran only after a
version check [tenth pre-registration; eleventh and twelfth, outcomes; §43]. Earlier results used
unpinned aliases, versions "not recorded per call" [sixth pre-registration, amendment A5].

The incumbent assessor, gpt-4o-mini with the paper's prompt, scores every essay, gpt-4o-mini's own
included [§8, §19; S3.2]. Best of thirteen configurations tested on Room For Debate
[@saha2024stance], it reaches κ 0.604 against human stance labels, where annotators reach 0.8285
[§16, §18], and gpt-4o, the second strong assessor, κ 0.666 [§22, §29, §41]. Weaker assessors enter
only as measured effects; the audited essays have no human labels [§8, §17, §20; "What is not yet
done"].

## 3.3 Refusal gate and refusal rules

**Two decisions.** The published assessor records Refused only when no essay is written, so a writer
that declines the persona and then argues against the proposition is scored as holding that stance;
a gate decides whether a proposition was refused, a refusal rule what it is worth [§34].

**The gate.** Version 2 shows gpt-4o-mini the persona, the proposition and the essay's first 500
characters and returns REFUSED, DISCLAIMED or COMPLIED; only REFUSED changes the score. It called 33
of 33 known refusals REFUSED and 0 of 40 genuine in-voice essays, but on gpt-5.4-mini, which often
ignores the persona, 34 of its 639 REFUSED verdicts had no refusal language in their first 300
characters, and 27 of those were not refusals [§34]. Version 3 marks COMPLIED, with no model call,
any essay whose first 500 characters hold no first-person refusal language. On its development
openings it released 27 of 27 non-refusals on gpt-5.4-mini and 7 of 7 on gemma3, keeping 6 of 7
declines and the one gemma3 refusal, in-sample and from one labeller [§34; FRAMING, results table];
it cut REFUSED verdicts on gpt-5.4-mini's enumeration from 639 to 609 [§35]. Ambiguous in-voice
phrasing was called REFUSED in 6 of 15 cases [§34].

**Where it is on.** The gate, opt-in so that PRISM's scoring reproduces [§34], is on, as version 3
unless stated, for gpt-5.4-mini bar an ungated pilot, for the llama3.2 enumeration's second stage
and for the stance-flip probes [§35; fifth, tenth, eleventh and twelfth pre-registrations]. The
gemma3 re-score behind the lead held-fixed figure used version 2; version 3 keeps its 62 of 62
refusals on `facist`, `hilter` and `extremist`, so the figure stands in substance [§34]. Other
models' confirmations are ungated; the gate flips nothing in the first run on each [§34].

**Refusal rules.** *Agree*, PRISM's default, scores a refusal as zero; *Neutral* scores it midway
between Disagree and Agree, putting a fully refused persona at social 0.000; *Dropped*, computed
afterwards, excludes refused propositions and pro-rates the social total to 62 [§34, §38; seventh
pre-registration, amendment B1]. Confirmations and ablations keep their original rule: Neutral on
gpt-5.4-mini, whose D is also given under Agree, and Agree elsewhere [sixth and seventh
pre-registrations; §35]. A persona is feasible if refused on at most 6 propositions with normalised
response entropy of at least 0.25 [third pre-registration].

## 3.4 Held-fixed re-scoring

**Design.** Ratings are cached apart from essays, so a stored essay set can be re-scored under
another assessor, gate or refusal rule without regenerating anything, the primary design for pricing
a scoring choice [Practical notes]. The gemma3 enumeration was re-scored with the gate on unchanged
essays, all 71 ids matching [§34], and Motoki et al.'s deposited answers [@motoki2023replication]
with "agree" at zero and at the midpoint [§37]. Röttger et al.'s and Wright et al.'s released answers
were re-scored the same way, with no model call, under four codings: published, "agree" at the
midpoint, unknown or missing statements at the midpoint, and both [§44; thirteenth
pre-registration]. Röttger et al.'s completions are mapped to options by a re-implementation of their
own string matcher, whose table is read from their source and never executed, and it reproduces all
20 coordinates their notebook printed to within 0.000049 [§44]. Wright et al. printed no coordinates,
so their re-score follows their code path without an external check, and position 50 of their
question list, an older statement than the current instrument's, is mapped as their notebook maps it
[§44]. Section 11 states whether the essays and stance
caches these re-scores read are released; without them the re-scores can be checked but not repeated
(S3.4).

**Exactness.** A refusal-rule change is arithmetic on stored stances. Gating is exact only for
personas refused throughout, such as gemma3's `facist` [§34]: elsewhere the assessor is asked again
wherever the gate lets a statement through, so the difference also carries assessor variation, sd
0.252 on identical essays [§36].

**Assessor comparison.** To move only the classifier, the gate's stored verdicts are reused, because
they drift, 7 of 44 changing over three days [§38; sixth pre-registration, amendment A1]. Arm A
scores each model's unroled baseline three times per assessor; Arms B and C pair one gpt-4o draw
with the stored gpt-4o-mini score on twelve replicates of each model's H\* and search winner, B on
the hosted models and C on copied mistral and gemma3 essays [sixth pre-registration]. The gpt-4o
draws were made on 16 September and the stored gpt-4o-mini side on earlier days, under unpinned
aliases, so a change of snapshot between the two cannot be excluded [sixth pre-registration,
amendment A5; S3.2].

## 3.5 Persona search and its controls

**Scope.** Persona search probes the measurement and does not locate a model [§39, §40]. No reported
comparison uses the 20-statement surrogate of the early persona search on gpt-3.5-turbo, which tied
80 of 116 libertarian candidates at its floor [§27, §28, §32].

**Protocol** [§32; first, third and fifth pre-registrations]. The objective is the full instrument,
the social coordinate pushed authoritarian and response entropy kept high, with survival by
non-dominated sorting among feasible candidates; under this protocol only the authoritarian
direction was searched, and the economic axis not at all ["What is not yet done"]. From the model's
top six hand-written personas, gpt-4o-mini mutates a parent towards the target or combines two, in
any register: 48 single-draw evaluations per arm, population 6 over 8 generations [third
pre-registration]. A matched `--no-selection` control rewrites feasible seeds with the same operator
and budget, selecting nothing; on gpt-3.5-turbo and gemma3 it was re-run after drawing on infeasible
seeds [fourth pre-registration]. Each arm's best feasible candidate and H\*, the best hand-written
persona, are confirmed at n=12 in randomised complete blocks; only confirmed means are admissible,
search-time bests having shrunk by up to 1.513 [§32; first pre-registration]. Feasibility is not
re-applied at confirmation: gpt-5.4-mini's search best exceeded the limit in 3 of its 12
confirmation runs [fifth pre-registration, outcome; §35]. On confirmed means, D = search − H\*,
variation = control − H\* and selection = search − control; the split changed sign on every model
with two runs, so none is claimed [§36, §40]. No search is claimed to have converged, and none can
be regenerated ["What is not yet done"; S3.5].

**H\* reuse.** An H\* arm named after its library entry shares ids, and so cached essays, with
earlier same-model, same-cap runs of that persona at the same replicate numbers. On gpt-3.5-turbo
and gpt-4o-mini, H\* replicates 1 to 12 come from earlier runs, and there and on gemma3's first run
replicate 1 is the enumeration draw H\* was selected on (S3.5). On mistral, `pccentrist`, selected
as the largest of six n=12 means, was confirmed on those same twelve replicates, so its +1.863 [§32]
is not an independent measurement; they are also Arm C's H\* cells and the intact side of δ = +4.331
[§40]. Only the fourth pre-registration's re-runs and the fifth drew H\* fresh inside their blocks.

## 3.6 Decision rules

**Registration.** Each decision rule was committed before the runs it governs, or for the first
before its confirmation data were read [§33]. The protocol of Section 3.5 as run on gpt-3.5-turbo,
gpt-4o-mini and mistral was adopted after the first round's negative outcome, later withdrawn, and
first fixed in advance by the second pre-registration, for gemma3 [first and second
pre-registrations; §30]. The eighth and the tenth to thirteenth analysis scripts were committed
before results were read; entries disclose where a script first ran on partial data [§39; tenth and
eleventh pre-registrations; sixth, amendment A4; seventh, disclosure]. Amendments are dated: the
sixth's A1 to A5 were written after Arm A was scored on four models and before any gpt-5.4-mini or
Arm C cell was analysed; the seventh's B1 and B2 after the first two gpt-5.4-mini blocks' refusal
counts were seen and before any δ was computed [amendments to the sixth and seventh
pre-registrations]. Every entry has a recorded outcome, the third's through the fifth, which
superseded it before any result [fifth pre-registration].

**Rules.** For D, with Welch intervals: *positive* if the one-sided 95% lower bound is at least
+0.50, *negative* if the 95% upper bound is below 0, *equivalent* if the 90% interval lies inside
the equivalence bound, *unresolved* otherwise [first pre-registration]. A two-condition contrast on
one persona is *equivalent* (*format-neutral*) if its Welch 95% interval lies inside the bound,
*different* (*format-carried* or *reversed*) if wholly beyond it, otherwise *unresolved*, not topped
up [seventh to ninth pre-registrations].

**Resolution bound.** ±0.75 came from the 0.72-unit gap between gpt-4o and gpt-4o-mini on three
essay sets and the H\* replicate sd of 0.73 [first pre-registration; §29]. The sixth
pre-registration's five-model test was *intermediate*, which widened the bound to ±0.89, the upper
95% limit of the measured term; verdicts are reported under both [§41; sixth pre-registration].
gpt-4o-mini's D was +0.479 at n=12, 95% interval [+0.098, +0.859], unresolved under ±0.75; extending
its confirmation to n=24, an unregistered departure from the first pre-registration's rule, gave
+0.656, 90% interval [+0.443, +0.869], equivalent only under ±0.89 [first pre-registration; §32,
§33, §41]. The ±0.89 re-reading covered only n=24; n=12 was never judged against it [§41].

**Independence of replicates.** Welch intervals assume independent replicates, but at temperature 0
hosted models give 9.3 to 12.0 distinct essays per proposition in 12 replicates and local models 1.0
to 4.9 [§36]. Local intervals are therefore read as overstating precision, a zero sd from
byte-identical essays as determinism, and a verdict on one essay per cell as a single observation
[§36, §42; fourth pre-registration].

## 3.7 Forced choice and answer-format ablation

**Forced choice.** The second route removes essay and assessor: the persona picks one of the four
options per proposition, scored through the same key, with no gate [eighth pre-registration; §39].
Each hosted model ran five personas (unroled baseline, authoritarian H\*, libertarian H\*
`pcleftlib`, search and control winners) at n=12 in randomised complete blocks, option order
reversed in half the replicates [eighth pre-registration]. Δ = forced choice − essay is tested for
the three personas with essay confirmations, rescored from cache; on the two older models 1 to 5
distinct answer sets in 6 replicates mean the forced-choice intervals overstate precision [§39].

**Answer-format ablation.** "State whether you either Strongly Agree or Strongly Disagree" is
verbatim in ten hand-written personas, including gemma3 and gpt-5.4-mini seeds and `pcleftlib` [§36
correction; §40]. mistral's seeds, `pccentrist` among them, carried only a plain "Agree or Disagree"
form, which the same rule removes; on mistral's search winner the rule makes its one declared
substitution, "either Agree or Disagree" replaced by "your view" [seventh pre-registration; §36
correction; §40]. The rule, registered as code, checks that text outside the edit is byte-identical
[seventh pre-registration]. Each ablation runs n=12 per arm under its model's confirmation flags, δ
= intact − stripped, and the ninth pre-registration applies the rule, sign reversed, to `pcleftlib`
on gpt-3.5-turbo [seventh and ninth pre-registrations]. Intact arms kept their names to reuse cached
essays, so on gpt-5.4-mini, mistral and gemma3 they are earlier runs and δ compares different
occasions (S3.7); on gpt-3.5-turbo, replicate 1 of the intact `pcleftlib` arm reuses the enumeration
draw, contrary to the ninth pre-registration's statement that both arms were generated fresh (S3.5).
A drift probe on gpt-5.4-mini landed every intact arm within 0.23 of its historical mean against a
registered 0.75; none was run locally [seventh pre-registration; §40]. Beside δ are refusals and δ
with refused statements excluded [seventh pre-registration, amendment B1].

## 3.8 Stance-flip frame ablation and transfer

Four personas, `none` (empty), `seed` (the Republican `red`, seed of the early gpt-3.5-turbo search
of Section 3.5) and that search's `crossover` and `mutation`, ran on statements 4 and 27 at n=12 in
randomised complete blocks, gate version 3 on, gpt-4o-mini-2024-07-18 assessing [eleventh
pre-registration; §27, §42]. Part A runs gpt-3.5-turbo under the paper frame and a neutral frame
without "Pick one side"; Part B, transfer, runs the paper frame on the other five models. The
endpoint, the endorsement rate e, is the share of replicates labelled Agree or Strongly agree, a
gate refusal counting as not endorsing. Decided on `crossover` [eleventh pre-registration]: the flip
reproduces if e(crossover) − e(seed) ≥ 0.5 on both statements under the paper frame; it is
persona-carried if e(crossover) − e(none) ≥ 0.5 on either under the neutral frame, and the frame's
alone if e(none, paper) ≥ 0.5 on either; a model transfers if e(crossover) − e(none) ≥ 0.5 on either
statement and resists if e(crossover) ≤ 0.1 on both. A gpt-4o re-labelling was added after the
hosted results were seen [§42; eleventh pre-registration, outcomes]. At temperature 0 gemma3 and
mistral wrote one essay per cell and llama3.2 one to four, so these local verdicts are single
observations; the twelfth pre-registration re-ran those arms at writer temperature 0.8, n=24, requiring at
least 12 distinct essays of 24 in every `crossover` and `none` cell [§42; twelfth pre-registration].
