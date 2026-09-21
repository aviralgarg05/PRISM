# Related work

Draft. Citations use pandoc syntax against [refs.bib](refs.bib): `@key` in running text, `[@key]`
in parentheses. Every number carries its source in square brackets, a section of
[FINDINGS.md](../FINDINGS.md) (§n) or an entry in [PREREGISTRATION.md](../PREREGISTRATION.md);
the anchors come out before submission. A provenance table closes the file.

## Political audits of LLMs

Most political audits of language models give the model a fixed questionnaire and report where it
lands. The usual instrument is the Political Compass test: 62 propositions, each answered with
one of four options, turned into an economic and a social coordinate by a fixed key [§37, §39].
@hartmann2023political put the test and voting-advice statements to ChatGPT in pre-registered
experiments and reported a pro-environmental, left-libertarian orientation.
@rutinowski2024selfperception gave ChatGPT the test repeatedly, beside other political and
personality questionnaires. @motoki2024more asked ChatGPT to answer as a partisan respondent,
compared those answers with its default over 100 rounds per condition, and reported a systematic
bias towards the Democrats in the United States, Lula in Brazil and the Labour Party in the
United Kingdom; the re-score below uses the five conditions whose compass positions their
replication package computes, the default and four US partisan impersonations [§37].
@feng2023pretraining placed pretrained models on the compass, reading encoder models by mask
filling and generative models through a stance detector, and traced the leanings from pretraining
data into downstream hate-speech and misinformation classifiers. @rozado2024political gave a
battery of orientation tests to conversational and base models, mapped free-text replies onto the
permitted answers with an LLM, and compared the base models with a reference that answers at
random. PRISM [@azzopardi2024prism], the method audited here, asks indirectly: the model writes an
essay on each statement in a persona, and an LLM assessor labels the essay's stance.

A second line of work asks what these coordinates measure. @rottger2024political show that models
give substantively different answers when they are not forced to choose, that the answers change
with how they are forced, and that they are not robust to paraphrase. @wright2024tropes elicit
open-ended and closed-form answers to the same propositions under 420 prompt variations that cross
demographic personas with differently worded instructions, closed-form and open-ended, label the
open-ended stances with an LLM, and find that the personas move the result [§38].
@ceron2024beyond test the reliability and consistency of stances on voting-advice statements and
discard the statements that fail. @kamal2025detailed find
that decoding parameters barely move compass scores while prompt phrasing and fine-tuning do. The
scoring key gets less attention. It is the instrument's own: Röttger et al.'s released code
[-@rottger2024code] adapts it from the Political Compass site's JavaScript, Wright et al.'s code
[-@wright2024code] and Motoki et al.'s replication package [-@motoki2023replication] carry the same
table and transforms, and Kamal et al. submit answers to the site, noting that its aggregation is
not public [§37, §38]. Under that key "Agree" carries zero weight on both axes, so a respondent
who agrees with everything lands at (0.38, 2.41), economic then social, which Röttger et al.'s code
records the live site returning [§38]. Both released codebases skip an answer that does not map to
an option, refusals included, and PRISM as published scores a refusal as "Agree"; under this key
each is numerically identical to recording agreement, and neither Röttger et al. nor Wright et al.
remark on it [§34, §38].

What this paper adds is the coding rule priced on held-fixed responses, which none of Röttger et
al., Wright et al. or Ceron et al. do [§38]. Re-scoring Motoki et al.'s deposited answers with
"agree" at the midpoint moves a published condition by up to 2.68 units on the social axis; that
is one published audit, and their conclusion, a comparison between conditions, is not overturned
[§37].

## Prompt and format sensitivity

That an evaluation result depends on incidental prompt choices is established well beyond
political audits. @sclar2024quantifying show that meaning-preserving changes of prompt format
produce large spreads in few-shot accuracy, argue that a result should be reported as a spread
over plausible formats rather than as a single number, and estimate that spread with
FormatSpread, which treats formats as the arms of a bandit and searches them by Bayesian
optimisation within a fixed budget and without access to model weights.
@dominguezolmedo2024questioning find that language models' survey answers are governed by
ordering and labelling biases, and that once answer order is randomised the answers trend towards
those of a uniformly random respondent. On the Political Compass that respondent sits at the
origin, economic +0.036 and social 0.000, because the key's offsets put it there [§38], so
answers driven by position bias under randomised order would score at the origin in expectation.
Within political audits the same dependence is documented by Röttger et al. for the forcing
prompt, by Wright et al. for personas and answer format, and by Kamal et al. for phrasing, while
@hartmann2023political report an orientation that holds across prompt variations and languages.
That a reported coordinate moves with the prompt is therefore the field's starting position, and
this paper does not claim it.

What this paper adds is a price for those choices under pre-registered decision rules whose
outcomes are reported when they fail: asking the same persona on the same model to choose an
option instead of writing an essay moves it by up to 4.15 units [§39; eighth pre-registration],
and an instruction telling the model which labels to answer with, written into hand-written
personas and kept by search, carries 1.10 to 4.33 units of position in eight of the ten personas
ablated [§40; seventh and ninth pre-registrations].

## LLM judges and response style

Open-ended and indirect audits replace the respondent's choice with a judge's reading of text. Feng
et al. use a stance detector, Rozado an LLM that sends replies it judges invalid back to be asked
again, Wright et al. an instruction-tuned LLM with a category for replies that take no side, and
PRISM an LLM assessor. @zheng2023judging find that strong LLM judges agree with human preferences
about as well as humans agree with one another, and document position, verbosity and
self-enhancement biases. Refusal is where a model's safety policy meets the judge. XSTest
[@rottger2024xstest] separates full compliance, full refusal and partial refusal, the last
including replies that refuse and then answer anyway. PRISM's assessor records a refusal only when
no essay is written, so a model that declines a persona and then argues against it is scored as
holding a stance; on gemma3, of 288 essays that open by declining and then go on, 229 were scored
as a strong stance [§34]. On unchanged gemma3 essays, a persona the model declined on all 62
statements sits at −6.64 on the social axis as PRISM was published, a safety decline read as a
stance, which this paper counts under the model's safety policy rather than under the assessor;
gated, it sits at +2.41 with refusals scored as agreement and at 0.00, the instrument's social
origin, with refusals at each statement's midpoint [§34, §38]. How far that decline is read
from no position therefore depends on the refusal rule. Response style is the respondent's side of
the same problem. @tjuatja2024biases test LLMs for human survey response biases, acquiescence among
them, and find that RLHF-tuned models react less than their base models to wording changes that
shift human answers, and more to perturbations that should leave answers unchanged. In this
project's audits, between 76.5% and 97.5% of stances across each hand-written library sit at an
extreme of the scale, measured with one replicate per persona and one assessor on the 43 statements
that carry social weight [§37], and the share depends on how a stance is asked as well as on who
answers: on gpt-5.4-mini the search winner, which carries no answer instruction, is 96% extreme
through essays and 39% when asked to choose directly, while the arms that carry the instruction
stay at 82% to 97%, and on gpt-3.5-turbo and gpt-4o-mini every persona arm stays at 98% to 100% in
both modes [§39, §40]. Uniform "Strongly agree" and uniform "Strongly disagree" land at +4.359 and
−4.359 on the social axis [§31, §38], so a position between those values is one that uniform
agreement or disagreement alone would reach [§38].

What this paper adds is that part of the judge's effect is the scoring key: on held-fixed essays a
second strong assessor moves positions by up to 1.77 units and differences between personas by at
most 0.65, and on one model the disagreement is almost entirely intensity, chiefly "Strongly agree"
read as "Agree", which the zero weight on "Agree" turns into position [§41].

## Search as a probe of a system under test

Search-based software engineering treats testing as optimisation over a system's inputs, guided by
a fitness function towards inputs that an oracle judges to fail; the two are separate components
[see @sorokin2026stellar, sec. II]. For learned systems, DeepJanus [@riccio2020frontier] searches
for the frontier of behaviours, the inputs at which a deep learning system starts to misbehave, and
judges the system by whether that frontier lies inside its valid input domain. STELLAR
[@sorokin2026stellar] carries the approach to LLM applications, evolving text inputs with NSGA-II
over stylistic, content and perturbation features and scoring each response with an LLM-based
oracle. Red-teaming with language models [@perez2022red] generates test cases for a target model by
methods ranging from zero-shot generation to reinforcement learning, and flags harmful replies with
a classifier. FormatSpread is the evaluation-side counterpart, searching for the best and worst
formats to bound a spread [@sclar2024quantifying]. When the fitness function or the oracle is
itself a model, or a cheaper proxy for the full evaluation, what search finds is partly a property
of that evaluation. STELLAR benchmarks its LLM judge against human labels before it searches
[@sorokin2026stellar, sec. IV], and Perez et al. note that a flawed classifier yields false
positives and false negatives [-@perez2022red, sec. 9.1]; in both, the evaluation is validated or
assumed first, and what the search then finds is read as a failure of the system under test.
Neither uses the search to find where the evaluation itself changes. The persona search in this
project was not built for that either. It also has a model-based fitness, computed by the assessor
through the scoring key, and it was run to push the social coordinate as far as it would go; what
it found was repeatedly a property of the measurement rather than of the model.

What this paper adds is a defect in the measurement that only optimisation made visible.
FormatSpread searches a declared nuisance dimension to bound a spread; here the optimiser's own
objective turned out to be at fault. Optimising against a 20-statement surrogate exposed a
transform that saturates, tying 80 of 116 libertarian candidates bit-exactly at its floor although
four of them lie 1.67 units apart on the full instrument [§27, §28]. Checking what later searches
returned turned up further dependences on the measurement: search kept the inherited instruction
telling the model which labels to answer with, and on gemma3 the whole of its gain was that
instruction [§40]; and the gpt-3.5-turbo search winner scores 4.15 units lower when asked to choose
an option directly [§39]. Under the full-instrument protocol that replaced the surrogate [§32],
every search comparison is a mean confirmed at n=12 (n=24 on gpt-4o-mini) against the best
hand-written persona in randomised complete blocks [§32, §33, §35; first pre-registration] (on the
two local models, one to five distinct essays per statement, so their intervals overstate
precision [§36]). Each search arm runs beside a no-selection control on the same operator and
budget, drawing on the same pool of parents except in the first runs on gpt-3.5-turbo and gemma3,
whose controls drew parents from infeasible seeds the search arm could not use and were re-run
with matched parents [§32, §36; fourth pre-registration]. No comparison rests on a search-time
best, which shrank by up to 1.513 units on confirmation across the first run of this protocol on
each of four models [§32, §33].

## Provenance of numbers

Bibliographic years, volumes and pages come from the records named in `refs.bib`, not from the
project files. Every other number is listed here.

| number | meaning | source |
| --- | --- | --- |
| 62 | Political Compass propositions; statements on which gemma3 declined `facist` | §37, §38; §34 table |
| four | answer options per proposition | §39 |
| 100 rounds; five conditions | Motoki et al.: rounds per condition; conditions whose compass positions the package computes (the default and four US partisan impersonations), which §37 re-scores | §37 |
| 420 | prompt variations in Wright et al. | §38 |
| zero | weight on "Agree", both axes | §37, §38 |
| (0.38, 2.41) | position (economic, social) of uniform "Agree"; returned by the live site in one of two runs recorded in Röttger et al.'s code | §38 |
| 2.68 | largest social-axis shift of a Motoki et al. condition with "agree" at the midpoint | §37 |
| +0.036, 0.000 | economic and social position of the uniformly random respondent | §38 |
| 4.15 | largest move between forced choice and essay, same persona and model; the gpt-3.5-turbo search winner's drop under forced choice | §39 |
| 1.10 to 4.33; eight of ten | answer-instruction effect; personas format-carried of those ablated | §40 |
| 229 of 288 | gemma3 decline-then-write essays scored as a strong stance | §34 |
| −6.64, +2.41, 0.00 | gemma3 `facist` on the social axis: ungated, gated with refusal as Agree, gated with refusal at the midpoint (the instrument's social origin) | §34; origin §38 |
| 76.5% to 97.5% | stances at an extreme across each hand-written library, on the 43 statements that carry social weight, one replicate per persona, one assessor | §37 |
| 43 | statements that carry social weight | §37 |
| 96%; 39%; 98% to 100% | extreme answers of gpt-5.4-mini's search winner through essays; the same under forced choice; every persona arm on gpt-3.5-turbo and gpt-4o-mini, in both modes | §39 Secondary |
| 82% to 97% | forced-choice extreme answers of gpt-5.4-mini arms that carry the answer instruction | §39 Secondary |
| +4.359, −4.359 | uniform "Strongly agree" and "Strongly disagree", social axis | §31, §38 |
| 1.77; 0.65 | largest position move and largest difference move under a second strong assessor | §41 |
| 20 | statements in the search surrogate | §27 |
| 80 of 116 | libertarian candidates tied bit-exactly at the surrogate floor | §27 |
| four; 1.67 | tied candidates re-scored; their spread on the full instrument | §28 |
| n=12; n=24 | replicates behind each confirmed search comparison; gpt-4o-mini's, topped up | §32, §33, §35; first pre-registration |
| one to five | distinct essays per statement across the twelve replicates on the two local models | §36 |
| 1.513; four | largest shrink from search-time best to confirmed mean, across the runs whose search-time best FINDINGS records; those runs are the first run of the §32 protocol on each of four models | §32, §33 (§32 search arms: +8.564 − 7.051 = 1.513 on gpt-3.5-turbo, +8.102 − 7.248 = 0.854 on gpt-4o-mini, +5.641 − 5.243 = 0.398 on mistral 7B; §33 gemma3: search +6.769 − 6.572 = 0.197, control +7.179 − 6.384 = 0.795; maximum 1.513) |
