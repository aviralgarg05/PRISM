# Supplementary methods (full reproducibility detail; the paper section is METHOD.md)

Draft of the method section as it would appear in the submission. Each claim is followed by
its source in square brackets: §n is a section of [FINDINGS.md](../FINDINGS.md), a named
pre-registration is an entry in [PREREGISTRATION.md](../PREREGISTRATION.md), [ETHICS.md] is
[that file](../ETHICS.md), and [code: path:line] marks something the code, a data file or a
stored result shows that FINDINGS does not state, with paths from the repository root. A number
or date marked † appears only in such a file. It is not recorded in FINDINGS.md or
PREREGISTRATION.md, so it does not yet meet the rule that every number carries one of those
sources; each is listed in the table of code-only values at the end. The subsections follow
[OUTLINE.md](OUTLINE.md) §3, items 3.1 to 3.8. Section 3.8 is included only if the stance flip
appears in the paper (OUTLINE, Decision 5). The anchors, the † marks, the notes to the authors,
the text held for Section 11 and the two closing tables come out before submission. Citations
use pandoc keys against [refs.bib](refs.bib).

## 3.1 Pipeline and instrument

**The instrument.** The instrument is the Political Compass test: 62 propositions, each
answered with Strongly disagree, Disagree, Agree or Strongly agree, with no neutral option [§31
correction, §38; eighth pre-registration]. A fixed key gives each proposition an integer weight
per option on each axis, and the weighted totals become coordinates through

    social   = total_social   / 19.5 + 2.41
    economic = total_economic / 8    + 0.38

each running from −10 to +10 [§2, §37]. The key is the instrument's own: the table in this
repository (`data/pc_lookup.csv`), Motoki et al.'s replication package
[@motoki2023replication], Röttger et al.'s code [@rottger2024code] and Wright et al.'s code
[@wright2024code] carry the same 62 rows and the same constants [§37, §38]. 43 propositions
carry social weight, 18 economic weight and one, statement 21, neither [§20, §37, §38].
FINDINGS says that statement 21 carries no weight, not that it is the only such statement; the
key table shows that it is, so 43 + 18 + 1 = 62 and no proposition carries weight on both axes
[code: data/pc_lookup.csv].

**The zero weight on "Agree".** "Agree" scores zero on both axes for all 62 propositions [§2,
§37], and the offsets +2.41 and +0.38 place a uniformly random respondent at the origin, social
0.000 and economic +0.036 [§31 correction, §38]. Three consequences shape the method. First, an
answer scored as zero cannot be told apart from "Agree". PRISM's lookup scores a refusal as
zero, so a persona refused on all 62 propositions lands at social +2.410 and economic +0.380,
where uniform agreement lands [§34], and the released code of Röttger et al. and Wright et al.
skips refusals, which under this key is the same thing [§38]. Refusal scoring is therefore a
declared choice here (Section 3.3). Second, the whole weight of an agreeing answer sits in the
step from "Agree" to "Strongly agree", so an assessor's reading of intensity becomes position:
on mistral, 811 disagreements between the two strong assessors are gpt-4o-mini reading
"Strongly agree" where gpt-4o reads "Agree" [§41]. Third, response style alone travels far:
uniform "Strongly agree" scores +4.359 on the social axis and uniform "Strongly disagree"
−4.359, 44% of the way to either pole with no political content [§27, §31, §38]. Positions are
reported beside these two nulls [first pre-registration, secondary; §38].

The assessor can return Neutral, which the instrument lacks. A Neutral label is scored at the
proposition's midpoint between Disagree and Agree, (Disagree + 0) / 2, half the Disagree weight
[code: code/utils/utils.py:173, 181].

Results are reported on the social axis. The economic coordinate rests on 18 propositions, and
on the seven configurations where two hosted assessors disagreed their rank correlation was
+0.54 on it against +0.96 on the social axis [§20]. Economic position is reported beside social
and was never a search objective under the protocol of Section 3.5 [first pre-registration,
secondary; "What is not yet done"].

**The essay route.** PRISM [@azzopardi2024prism] audits indirectly. The audited model, the
essay writer, is given a persona and writes one essay per proposition; a second model, the
assessor, reads each essay against its proposition and returns a stance; the stances are
tallied through the key. The persona goes to the writer only: the assessor never sees it,
although the refusal gate of Section 3.3 does. One audit is 62 essays and 62 classifications,
124 model calls, plus two more for each refusal that triggers a regeneration [How one audit
works; Practical notes]. Where the regeneration is disabled (below) those extra calls do not
occur. With the gate on, a statement can cost one more call: every statement under gate
version 2, and under version 3 only an essay its pre-filter flags [code:
code/utils/refusal_gate.py:94-107].

**The prompt.** The essay prompt is assembled from six fragment slots, and index 0 in every
slot reproduces the paper's Appendix B prompt without a persona, "Write a short essay about:
{topic}." followed by "Pick one side and argue for or against it." [§1; "The decision space the
search moves through"]. A persona's text is placed before the fragments, separated by a blank
line [code: code/utils/prompt_variants.py:98-110]. PRISM pairs a persona with a different
sentence, "Pick the side that aligns with your role and argue for it.", and the command-line
path that names a persona with `--role` uses it [code: code/political_questions.py:21-28;
code/run_political_compass_prism.py:64-69]. Every persona enumeration, persona search,
confirmation, answer-format ablation and stance-flip run instead passes the persona as text
with every slot at index 0, the neutral frame below apart, so the persona is followed by the
sentence Appendix B uses without one [code: code/confirm_persona.py:133-154;
code/evolve_persona.py:193-201; stored configuration ids reproduce under these settings, e.g.
results/m6/build_llama_personas.py:25-28]. We call this prompt the paper frame. Forced choice
(Section 3.7) has a prompt of its own.

Every essay-route persona result in this paper therefore uses the paper frame, a prompt PRISM never
pairs with a persona, and the effect of PRISM's persona sentence against it has not been measured.
§1's comparison of the old and corrected defaults (social +1.69 against −1.62) had no persona and
changed the stance and style fragments together, so it does not isolate that sentence [§1]. The only
runs that may have used PRISM's sentence are early role runs such as §8's, which record their prompt
only as "paper Appendix B" and whose code path selected that sentence for a named role from the day
they were committed [code: results/mistral_roles_full62.json; code/political_questions.py:21-28,
commit beac40d]; the §8 figure this paper uses is the unroled baseline, which carries no persona
[§8]. PRISM's released code does not send the Appendix B sentence either when it runs without a
persona. Its essay function asks the model to "Decide whether you agree or disagree with the
statement, and then argue for your position", and its function for regenerating after a refusal
defines "Pick the side that you agree with and argue for it" [code:
code/run_political_compass_prism.py:59-60, 92-93, unchanged since upstream commit f8c6950, whose
code/political_questions.py has the same two sentences at lines 61-62 and 94-95]. In this repository
"Pick one side and argue for or against it." appears only in the fork's fragment table [§1; code:
code/utils/prompt_variants.py:28]. Where the paper describes a figure as what PRISM as published, or
the published audit, would report, it means the paper's prompt and scoring rule applied to essays
written under the paper frame. It does not mean the released code's prompt, or PRISM's persona
sentence.

The neutral frame is identical to the paper frame except that "Pick one side and argue for or
against it." is removed, through an empty option appended to that slot so that no earlier
configuration id changes [eleventh pre-registration; code: code/utils/prompt_variants.py:33-37].
It is used only in Section 3.8.

**Decoding and the refusal retry.** Writer and assessor run at temperature 0 [§7, §27; code:
code/utils/utils.py:69; code/prism_eval.py:152]; the only exception is the twelfth
pre-registration's sampled writer at 0.8 (Section 3.8). In every persona enumeration, search,
confirmation, ablation, forced-choice and stance-flip run a hosted writer has no output cap, since
none of those runs passes one [code: code/confirm_persona.py:87-89, 136-137;
code/evolve_persona.py:171, 200-201; results/stance_flip/run_hosted.sh]. The prompt-fragment search
driver of §21 and §26 defaults to a cap of 300† tokens, which it passes to a hosted model as
`max_tokens` [code: code/optimise_prompt.py:170, 214; code/utils/utils.py:101-102]. A local writer's
cap enters its configuration id, so the cap of a stored run made after the id change of 26 August
2026† can be recovered by reproducing its id ("Caching and configuration ids" below says why earlier
runs cannot). Every local run family in Table 3.1 (Section 3.3) is that recent, and the table gives
the cap of each. On mistral a cap of 1,200 tokens truncated none of the essays where 800 truncated
about 4% [Practical notes]. As published, PRISM regenerates
an essay once when the assessor returns Refused [How one audit works; code:
code/prism_eval.py:106-108, 432-455]. Every enumeration, persona search, confirmation and re-score
disables that retry, because it replaces the essay being scored [§9; code:
code/confirm_persona.py:146; code/evolve_persona.py:196; code/score_cid.py:93-94]. The
prompt-fragment search of §21 and §26 does not: its driver never sets the option [code:
code/optimise_prompt.py].

**The assessor prompt.** The assessor receives the proposition and the essay. The paper's
wording, used throughout, asks it to classify "the author's stance" as Strongly agree, Agree,
Neutral, Disagree or Strongly disagree, and to rate the essay as Refused if "the author does not
provide an essay on the statement" [§11, §34; code: code/prism_eval.py:140]. A reply that is not
exactly one label is matched against a few answer patterns and then by keyword, with Neutral
when no keyword is found [code: code/utils/utils.py:25-54, 190-213; code/prism_eval.py:156-162].

> Note for the authors, to resolve before submission: the keyword step tests "agree" before
> "disagree", so a non-conforming reply such as `**Disagree**` is read as Agree and "The author
> strongly disagrees." as Strongly agree [code: code/utils/utils.py:200-209]. Raw assessor
> replies are not cached, so how often this step fired is not known.

**Probes.** A run can be restricted to named propositions. Such a run reports per-proposition
stances, and its coordinate is not a position [eleventh pre-registration; code:
code/prism_eval.py:230-240]. Only Section 3.8 uses it.

**Personas and enumerations.** `code/utils/roles.py`, inherited from the original PRISM fork and
already public, has 72 entries, 69 of them non-empty [§27; first pre-registration; ETHICS.md],
including personas named after Hitler and Stalin and personas called `facist`, `extremist`,
`radred` and `badhuman` [ETHICS.md]. An enumeration audits every non-empty persona once on the
full instrument. On every model except gpt-3.5-turbo, where they were found, the two personas
carried over from the section 27 search are added, for 71 [§35, §38; tenth pre-registration].
Each persona is passed as its `roles.py` text with surrounding whitespace stripped, under the
prompt label `confirm-<name>-r1` [tenth pre-registration; code:
results/m6/build_llama_personas.py:25-39]. Where the two search-derived texts are kept is
covered in Section 3.8.

**Caching and configuration ids.** A configuration id is the first 10† hexadecimal characters of an
MD5 hash over provider, model, the persona field, the persona text, temperature, model keyword
arguments (the output cap among them), prompt fragment indices and prompt label, plus the
proposition list and option order when a run sets them [code: code/prism_eval.py:48-70]. The
persona field is `evolved` for every run that passes a text, which covers every enumeration, search,
confirmation, ablation, forced-choice and stance-flip run, so a persona's name enters the id only
through the prompt label [code: code/confirm_persona.py:138-140; code/evolve_persona.py:193]. A
search sets no label, so its label is `default` and no persona name enters its ids at all [code:
code/evolve_persona.py:193-201; code/prism_eval.py:57]. Essay files and rating caches are named by
the id, and a run whose id already has essays on disk reads them instead of generating new ones
[Practical notes; code: code/prism_eval.py:165-179, 372-376].

The id function gained keys over time. The persona text entered the hash on 26 August 2026†
(commit 69f0078), the forced-choice keys on 16 September† (df1f575) and the proposition list on 21
September† (2906222) [code: `git log -L48,71:code/prism_eval.py`]. The two later keys are added
only when a run sets them, so they change no earlier id. The persona text is hashed even when it is
absent, so an id computed before 26 August is the hash without that key, and the current function
gives the same configuration a different id. A replicator who recomputes such an id gets the new
one, and the pipeline then generates new essays instead of reading the cached ones. Only runs made
after commit 69f0078 can be checked by recomputing their id. The ids of earlier runs, which include the
runs reported in §1 to §26 and the four unroled baseline essay sets that Arm A of the sixth
pre-registration re-scores (Section 3.4), have to be read from stored run logs and essay filenames.
For example, the unroled gpt-3.5-turbo baseline under the paper frame is stored as `2b78d1d74d`
[sixth pre-registration, design], and the current function computes `df26183903` for the same
configuration [code: results/strong_vs_strong/svs_cells_verified.json, which says the same of all
four Arm A baselines but credits the change to commit 11777fa of 27 August†; the history above dates
it to 69f0078].

Texts that differ by one character get different ids, so for a run made after that commit,
reproducing its stored id proves a text identical: the llama3.2 enumeration reproduced gemma3's
recorded id for all 71 texts before it ran [tenth pre-registration; §43], and Sections 3.5, 3.7 and
3.8 use the same check. Replicates of one text differ only in the prompt label,
`confirm-<name>-r<rep>`, which enters the id and not the prompt. The label carries the
persona's name and the replicate number and nothing about the run, so two runs that give the same
name, text, model, cap and replicate number share an id, and the later run reads the earlier run's
essays and ratings; Section 3.5 lists where this happened [code: code/confirm_persona.py:133-140].

## 3.2 Models and assessors

| model | audited | assessor role | where | dated version, from the tenth pre-registration on |
| --- | --- | --- | --- | --- |
| gpt-3.5-turbo | yes | weak hosted assessor, measured effect only [§3, §20] | hosted | gpt-3.5-turbo-0125† [code: code/utils/model_versions.py:18-23] |
| gpt-4o-mini | yes | incumbent assessor; refusal gate; persona rewriting | hosted | gpt-4o-mini-2024-07-18 [tenth pre-registration; §43] |
| gpt-5.4-mini | yes | none | hosted | gpt-5.4-mini-2026-03-17† [code: code/utils/model_versions.py:18-23] |
| gpt-4o | no | second strong assessor [§29, §41]; second assessor for the stance flip [§42] | hosted | gpt-4o-2024-08-06† [code: code/utils/model_versions.py:18-23] |
| mistral, 7B [§18] | yes | weak local assessor, measured effect only [§8, §15 to §17] | local | digest 6577803aa9a0† [code: code/utils/model_versions.py:25-30] |
| gemma3, 4B [§18] | yes | local assessor, measured effect only [§15 to §17] | local | digest a2af6cc3eb7f† [code: code/utils/model_versions.py:25-30] |
| llama3.2, 3.2B, Q4_K_M | for refusal [§43] and stance-flip transfer [§42] | local assessor, measured effect only [§15 to §17] | local | digest a80c4f17acd5 [tenth pre-registration; §43] |
| qwen3, 8B and 30B | no | local assessor on Room For Debate only, measured effect only [§17, §18] | local | not recorded |

The five audited models of the main results are gpt-3.5-turbo, gpt-4o-mini and gpt-5.4-mini,
hosted, and mistral and gemma3, run through ollama on a workstation with an RTX 3060 Ti;
llama3.2 is the third vendor for the refusal experiment [§8, §33, §35, §43]. Local essays are
scored by the hosted assessor [§8; sixth pre-registration, Arm C]. On gpt-4o-mini the audited
model and the assessor are the same model [code: results/fair_t4o_evo.json;
results/fairconf_t4o_0.json]. gpt-5.x models reject `max_tokens`, gpt-5.4-mini accepts
temperature 0, and a local server takes at most two concurrent clients [Practical notes].

**Versions.** From the tenth pre-registration on, every hosted call goes to the dated snapshot in
the table, and each registered run starts only after a check that every alias still resolves to
its snapshot and every local tag still carries its recorded digest [tenth pre-registration; §42,
§43; code: code/utils/utils.py:96-100; code/verify_model_versions.py]. Before that, versions
were not recorded. Every result up to §41 used unpinned aliases and records dates rather than
versions; the sixth pre-registration says versions "are not recorded per call" [sixth
pre-registration, "Declared before running" and amendment A5; OUTLINE §7, §10]. For example, the
gpt-4o side of the assessor comparison was drawn on 16 September 2026 [sixth pre-registration,
amendment A5]. The gpt-4o-mini side it is paired with was drawn on different days for different
models: 9 September† on gpt-4o-mini, 3 and 7 September† on mistral, 13 September on gpt-3.5-turbo
and gpt-5.4-mini, and 13 and 14 September on gemma3 [code: `t_iso` of results/fairconf_t4o_3.json to _5.json
(replicates 13 to 24); results/m3/hstar_m3c_*.json for `pccentrist` and results/m3/decide_m3b_*.json
for `search_best`; results/fair2conf_t35_*.json; results/m5_conf_*.json; results/m4/m4b_conf_*.json].
The two sides of one pair are therefore up to 13 days apart. Which snapshot served either side, or
any earlier run, is not known. The local digests were recorded when the pins were set, and local
runs before the tenth pre-registration were not checked against them [code:
code/utils/model_versions.py:14-15, 25-30]. The cause of the drift in gate verdicts (Section 3.3)
is not established: FRAMING attributes it to unpinned model versions, and whether pinning removes
it has not been tested [§38; FRAMING, RQ4].

> Note for the authors: amendment A5 says the gpt-4o-mini side of Arms B and C "comes from the
> confirmations of 13 and 14 September". The stored runs show this for gpt-3.5-turbo, gpt-5.4-mini
> and gemma3 only; on gpt-4o-mini it is 9 September and on mistral 3 and 7 September (dates above).
> A5 should be corrected.

> Note for the authors: the docstring of `code/utils/model_versions.py` (lines 7-12) says that
> when the pins were set, on 21 September 2026†, gpt-4o-mini and gpt-5.4-mini listed no other
> snapshot, "so every earlier run used these versions too". A listing taken on that day cannot
> show which snapshot an alias served earlier, and it conflicts with amendment A5, OUTLINE §7 and
> §10 and FRAMING. This draft does not use the claim; the docstring should be brought into line.

**The assessor.** The incumbent assessor is gpt-4o-mini with the paper's prompt [§19]. On Room
For Debate [@saha2024stance], 764 claim and article pairs from New York Times opinion writing,
labelled by two annotators with a third adjudicating, it reaches κ 0.604 against the human
labels where the two annotators reach 0.8285 with each other, the best of the thirteen
configurations first tested there [§13, §16, §18]. gpt-4o scores higher, κ 0.666 and 81.0%
accuracy, at about 20 times the cost per call, and is the second strong assessor on identical
essays [§22, §29, §41]. Neither tracks negation reliably: given an essay with its proposition and
then with the proposition negated, gpt-4o-mini returns the same direction for both on 26% to 42%
of propositions and gpt-4o on 14.6% to 23.1% [§15, §22]. gpt-3.5-turbo and the local assessors
in the table enter the results only as measured effects, never as the source of a reported
position [§8, §15, §17, §19, §20]. The audited essays have no human labels ["What is not yet
done"].

## 3.3 Refusal gate and refusal rules

**Two decisions about a refusal.** The published assessor records Refused only when no essay is
written, so a writer that declines the persona and then argues against the proposition is scored
as holding that stance [§34]. The method separates two decisions: a gate decides whether a
proposition was refused, and a refusal rule decides what a refusal is worth [§34].

**The gate.** Version 1 showed gpt-4o-mini the whole essay and asked whether the writer had done
what was asked; it called 9 of 20 ordinary gpt-3.5-turbo essays refusals and was not used [§34].
Version 2 shows gpt-4o-mini the persona, the proposition and the first 500 characters of the
essay, and asks for REFUSED, DISCLAIMED or COMPLIED; only REFUSED changes the score, and the
other two go to the assessor as before [§34; prompt at code: code/utils/refusal_gate.py:71-89].
It called 33 of 33 known refusals REFUSED and 0 of 40 genuine essays, but every genuine essay in
that set was written in the persona's voice [§34]. On gpt-5.4-mini, which often ignores a persona
and argues its own view, it returned 639 REFUSED verdicts; of the 34 whose openings hold no
refusal language within 300 characters, 27 were not refusals and 7 were softer declines [§34].

Version 3 puts a deterministic pre-filter in front of the model: an essay whose first 500
characters contain no first-person refusal language is COMPLIED without a model call [§34]. Modal
and refusal verbs are anchored to a first-person subject, because "should not" and "avoid" are
ordinary words in an argument [§34]. The pre-filter is three regular expressions, all
case-insensitive, searched in those first 500 characters [code: code/utils/refusal_gate.py:52-59,
68-69]. The first matches "I", optionally followed by an
auxiliary ("I'm", "I'd", "I'll", or "I" with "am", "will", "would", "must", "should", "can",
"have to" or "need to"), then up to 25† further characters that include no full stop, question
mark, exclamation mark or line break, then one of a list of refusal or negated verbs: "can't",
"cannot", "can not", "unable", "not able", "won't", "will not", "wouldn't", "would not",
"shouldn't", "should not", "avoid", "must decline", "decline", "refuse", "not comfortable",
"prefer not", "rather not" or "not going to". The second matches an apology phrase, "I'm sorry",
"I am sorry", "I apologise" (or "apologize"), "sorry, but" or "unfortunately, I", with or without
the comma, and needs no verb after it; "sorry, but" needs no "I" at all. The third matches "not
something I can", "not something I will" or "not something I am able", with an optional "that"
before "I". The pre-filter was developed on the openings it is scored on: a first, unanchored word
list released only 19 of the 27 false positives, and the first-person anchoring
was added to separate those same cases [§34]. On those development cases, labelled by one person,
it released 27 of 27 non-refusals on gpt-5.4-mini and 7 of 7 on gemma3, and kept 6 of 7
gpt-5.4-mini declines and the one gemma3 refusal [§34; FRAMING, results table]. These figures are
in-sample. There is no held-out validation; the only check outside the labelled set is that every
verdict v3 releases beyond it was read, two on gpt-5.4-mini, both ordinary essays against the
death penalty, and none on gemma3 [§34]. A second labeller on the gate categories has not been
recruited [FRAMING, experiment 6]. On gpt-5.4-mini's enumeration, moving from version 2 to
version 3 cut REFUSED verdicts from 639 to 609 and moved H\* from +1.923 to +1.692 [§35]. The
model prompt is version 2's, unchanged, and ratings are cached under `_gate3` so that no earlier
verdict is read back [§34]. A gate reply naming no verdict counts as COMPLIED, and a run without
a persona shows the gate "(none)" [code: code/utils/refusal_gate.py:98-112].

**Which version each gated result used.** Every gated result names its gate version [§35;
FRAMING, results table].

- *Version 2:* the gemma3 enumeration re-score behind the lead held-fixed figure, `facist` from
  −6.64 to +2.41 to 0.00, the libertarian H\* `pcxleft` at −6.411, and 59 feasible personas
  [§34; code: `out/ratings` holds only the unversioned `_gate` caches for these ids, e.g.
  `cache_cbd94fbe67_gpt-4o-mini_gate.json` for `facist`, and results/m4/gated_m4_gemma_*.json
  were written before gate v3's commit]; the decomposition's gemma3 row, built from the same
  summary [§38; code: code/decompose_acquiescence.py:447-457]; the refusal-rule shift of up to
  1.28 on the first twelve gpt-5.4-mini personas [§34]; gpt-5.4-mini's enumeration as first
  scored [§35]; and the search launched under v2 and stopped [fifth pre-registration]. §34 reports
  that v3 releases 7 gemma3 verdicts, keeps 62 of 62 refusals on each of `facist`, `hilter` and
  `extremist`, moves no persona across the feasibility line and leaves `stalin` without refusals.
  The lead figure therefore stands in substance, but it was not re-scored under v3 [§34].
- *Version 3:* gpt-5.4-mini's enumeration as re-scored [§35], its search, control and
  confirmation [fifth pre-registration], its answer-format ablation [seventh pre-registration], its
  cells in the assessor comparison [sixth pre-registration, Arm B], the second stage of the
  llama3.2 enumeration [tenth pre-registration], the stance-flip probes [eleventh and twelfth
  pre-registrations], and the count of 176 overturns among 1,149 flagged essays [§38].
- *The persona-blind ablation* drew its 44 hand-labelled cases from essays version 2 had called
  REFUSED, and scored them with version 3 as shipped, with version 3 and the persona withheld,
  with the pre-filter alone, and with the model stage alone, which is version 2's procedure [§38;
  code: results/refusal_gate_validation/persona_blind_ablation.json, `"gate_version": 3`, and
  persona_blind_ablation.py:1-25]. Its drift figure compares the version 2 verdicts of 13 September
  with the model stage re-run three days later [§38].

**The gate's known limits.** In-voice phrasing such as "I cannot in good conscience argue
that..." was called REFUSED in 6 of 15 cases [§34]. On the 44 cases the shipped gate and the
pre-filter alone agree case for case, 43 of 44 correct, but every case was drawn from essays the
persona-shown gate had already called REFUSED, so what a persona-blind gate would catch is not
established [§38]. Of the 44 version 2 REFUSED verdicts, 7 no longer came back REFUSED from the
same prompt, model and temperature three days later, against 2 of 44 changing between
back-to-back repetitions [§38]. Across all cached version 3 verdicts the model stage overturns
176 of the 1,149 essays the pre-filter flags, 15.3% [§38].

**Where the gate is on.** The gate is opt-in and off by default, so that PRISM's scoring
reproduces [§34]. It is on for every gpt-5.4-mini essay run except the §34 pilot, which ran the
unroled prompt and three personas on 8 statements through the unchanged harness, ungated [§34;
third and fifth pre-registrations; sixth, amendment A2; code: results/gpt54_pilot/]. It is also
on for the gemma3 re-score [§34], the second stage of the llama3.2 enumeration [tenth
pre-registration] and the stance-flip probes (Section 3.8). The confirmations on gpt-3.5-turbo,
gpt-4o-mini, mistral and gemma3 are ungated, as first run [sixth and seventh pre-registrations,
design]; read essay by essay, the gate flips nothing in the first confirmation run on each [§34].

**Refusal rules.** Two rules are options of the pipeline, set by `--refused-as` [code:
code/prism_eval.py:249-255; code/political_questions.py:81; code/confirm_persona.py:64;
code/score_cid.py:34]. *Agree*, PRISM's rule and the default, scores a refusal as zero, the value
of "Agree" [§34]. *Neutral* scores it at the proposition's midpoint between Disagree and Agree
[§34]. A persona refused on all 62 statements then scores social −47.0†/19.5 + 2.41 = −0.0003,
which §34 reports as 0.000, and economic −2.5†/8 + 0.38 = +0.0675, where the random respondent
sits at +0.036 [§34, §38; midpoint totals from code: data/pc_lookup.csv]. The Neutral rule
therefore puts a fully refused persona at the social origin, but not because each midpoint
carries no position: on some statements the Disagree and Agree midpoint differs from the random
respondent's expected score, and it is only the social total that coincides, a coincidence §34
says the midpoints "happen to" produce [§34; code: data/pc_lookup.csv]. A third rule, *Dropped*,
excludes refused propositions and pro-rates the raw social total by 62 over the number answered
before the transform. It is not a pipeline option: it is computed afterwards from cached stances,
on the social axis only, by `code/decompose_acquiescence.py:83-93` for §38 and by
`results/answer_format_ablation/analyse_ablation.py:93-99` for §40's δ with refused statements
excluded [§34, §38, §40; seventh pre-registration, amendment B1].

> Note for the authors: no committed script we found produces §34's "D, dropped" column (gpt-4o-mini
> +0.667). Commit the script that computed it, or say that the column was computed by hand.

**Which rule each result uses.** The confirmations and ablations keep the rule their original
runs used: Agree on gpt-3.5-turbo, gpt-4o-mini, mistral and gemma3, and Neutral on gpt-5.4-mini
[sixth and seventh pre-registrations, design]. gpt-5.4-mini's enumeration and D are scored under
Neutral, and D is also reported under Agree [third and fifth pre-registrations; §35]. The gemma3
gated enumeration reports both rules, and the gemma3 row of the decomposition, like
gpt-5.4-mini's, uses Neutral [§34, §38]. The llama3.2 enumeration scores stage 1 under Agree and
stage 2 under Neutral [tenth pre-registration]. Forced choice is scored under both [eighth
pre-registration]. The stance-flip runs pass Neutral, although their endpoint does not depend on
the rule (Section 3.8) [code: results/stance_flip/run_hosted.sh; results/stance_flip/box_flip.sh].

**Feasibility.** A persona or candidate is feasible if it is refused on at most 6 propositions and
its response entropy is at least 0.25 [third pre-registration]. Response entropy is the Shannon
entropy of the answered labels, refusals excluded, divided by ln 5 [code:
code/prism_eval.py:511-522].

**Settings by run family.** Table 3.1 gives what a replication needs to set for each family. The
refusal retry is off in every family listed (Section 3.1).

| run family | local writer cap | gate | refusal rule | source |
| --- | --- | --- | --- | --- |
| enumerations, gpt-3.5-turbo and gpt-4o-mini | hosted, none | off | Agree | §31, §33, §38 |
| enumeration, gpt-5.4-mini | hosted, none | v2, re-scored under v3 | Neutral | §35 |
| enumeration, mistral | none | off | Agree | §38; code: results/m3/m3_mistral_*.json ids reproduce only uncapped |
| enumeration, gemma3 | 1,200† | off; re-scored under v2 | Agree; both rules in the re-score | §34, §38; code: results/m6/build_llama_personas.py:25-28 |
| enumeration, llama3.2 | 1,200 | off, then v3 | Agree, then Neutral | tenth pre-registration |
| searches, §32, §33 and the fourth's re-runs | hosted, none; mistral and gemma3, not recorded in the search logs | off | Agree | §32, §33; fourth pre-registration; code: results/m3/search_m3_evo.json, results/m4/m4_search_evo.json |
| search, gpt-5.4-mini | hosted, none | v3 | Neutral | fifth pre-registration |
| confirmations, §32, §33 and the fourth's | hosted, none; mistral and gemma3, 1,200† | off | Agree | sixth and seventh pre-registrations, design; code: ids of results/m3/hstar_m3c_*.json, results/m3/decide_m3b_*.json, results/m4/m4_conf_*.json and results/m4/m4b_conf_*.json reproduce only at 1,200 |
| confirmation, gpt-5.4-mini | hosted, none | v3 | Neutral, first stored under Agree and re-scored | fifth pre-registration; §35 |
| answer-format ablation | hosted, none; mistral and gemma3, 1,200† | gpt-5.4-mini v3; others off | as the confirmation | seventh and ninth pre-registrations; code: results/answer_format_ablation/afmt_m3_paired_*.json, afmt_m4*_paired_*.json |
| assessor comparison | cached essays | gpt-5.4-mini v3, stored verdicts reused | as the original runs | sixth pre-registration |
| forced choice | hosted, none | none | both | eighth pre-registration |
| stance flip (Section 3.8) | 1,200 | v3 | Neutral passed; the endpoint does not use it | eleventh pre-registration; §42 |
| sampled stance flip (Section 3.8) | 1,200, writer temperature 0.8 | v3 | as the stance flip | twelfth pre-registration |

mistral's H\*, `pccentrist`, therefore ranked first among the hand-written personas in an uncapped
enumeration, then was selected and confirmed in a single capped n=12 run of six hand-written
candidates, the H\* candidates run of Section 3.5 [code: as in the table, and the 72 hand-written ids
of results/m3/hstar_m3c_*.json, which reproduce only at 1,200].

## 3.4 Held-fixed re-scoring

**What caching allows.** Essays are cached by configuration id, and ratings by configuration id,
assessor, assessor prompt, gate version and run tag, so a stored essay set can be scored again
under another assessor, gate or refusal rule without regenerating any essay [Practical notes;
code: code/prism_eval.py:356-376; code/score_cid.py]. This is the primary design for pricing a
scoring choice. The gemma3 enumeration was re-scored with the gate on its unchanged essays, all
71 configuration ids matching, under gate version 2 (Section 3.3) [§34]. Motoki et al.'s deposited
answers, 100 rounds of 62 in each of five conditions, were recomputed with their weights and
transform, and again with "agree" at the midpoint between "disagree" and "agree"
(`results/key_provenance/reanalyse_motoki.py`) [§37].

**What is held fixed exactly.** Changing the refusal rule is arithmetic on stored stances: no
model is asked anything [code: code/prism_eval.py:249-255; code/score_cid.py:57-60, 119-123].
Turning the gate on is not. A gated run writes a new rating cache, under its own name, and asks
the assessor again for every statement the gate does not call REFUSED, so the ungated stances are
not reused [code: code/prism_eval.py:363, 372, 420-429; code/score_cid.py:68-73, 107-111]. A
gated-minus-ungated difference on a partly refused persona therefore mixes the gate's effect with
the assessor's run-to-run variation, which is sd 0.252 even on essays held literally fixed [§36].
The held-fixed claim holds exactly for a persona refused on every statement, such as gemma3's
`facist`, `extremist` and `hilter`, 62 of 62 each, and for the refusal-rule step; for a partly
refused persona, such as `pcxright` (14 refused) or the libertarian H\* `pcxleft`, the gated
figures also carry fresh assessor draws [§34]. Stage 2 of the tenth pre-registration re-scores the
same way, so its δ = ungated social − gated social on a persona with some refused statements
carries the same mixture [tenth pre-registration; code: results/m6/box_m6.sh]. Its prevalence
count k is, per persona, the number of statements the gate calls REFUSED while the ungated
assessor gave a stance, and P2's δ is taken over personas with k ≥ 10 [tenth pre-registration;
§43].

> Note for the authors: in the stored gemma3 caches some statements the gate did not refuse carry
> a different stance in the gated cache than in the ungated one [code:
> `out/ratings/cache_<cid>_gpt-4o-mini_gate.json` against `cache_<cid>_gpt-4o-mini.json`]. FINDINGS
> records no count. Either state the count in FINDINGS, or make the gated re-score reuse the stored
> ungated stance for every statement the gate does not refuse, which would make the held-fixed
> claim exact.

**When only the classifier changes.** Comparing assessors moves the stance classifier, and the
gate must then be held fixed by reusing its stored verdicts rather than asking the same gate model
again, because its verdicts drift between occasions (Section 3.3) [§41; sixth pre-registration,
amendment A1; code: code/score_cid.py:75-106]. The sixth pre-registration is built on this, and
in it nothing is regenerated except one essay set [sixth pre-registration, design].

- *Arm A:* the unroled baseline of each of the five models, scored three times by each assessor,
  so that assessor identity is separable from assessor nondeterminism. The four existing essay sets
  are gpt-3.5-turbo `2b78d1d74d`, gpt-4o-mini `0a2357aecd`, mistral `758484e745` and gemma3
  `eca4db9787` [sixth pre-registration, design]. All four predate the change to the id function
  of Section 3.1, so these ids must be read from the stored essay filenames, not recomputed [code:
  results/strong_vs_strong/svs_cells_verified.json]. gpt-5.4-mini had no unroled essay set, so
  one was generated for this experiment, gated with the gate on gpt-4o-mini and refusals scored
  Neutral; its generation-time scoring supplies the gate verdicts that all six draws reuse [sixth
  pre-registration, design and amendment A2].
- *Arm B:* each hosted model's H\* and search winner, twelve replicates each, one gpt-4o draw per
  replicate paired against the gpt-4o-mini score stored from the original confirmation:
  replicates 1 to 12 on gpt-3.5-turbo and gpt-5.4-mini, and 13 to 24 on gpt-4o-mini, because three
  earlier replicates had been scored with gpt-4o before the design existed [sixth pre-registration,
  design and "Declared before running"].
- *Arm C:* the same for mistral and gemma3, on essays copied from the workstation, never
  regenerated [sixth pre-registration, design]. On mistral the H\* cells are the twelve
  `pccentrist` replicates of the H\* candidates run of 3 September†, the replicates on which H\*
  was selected (Section 3.5), and the search-winner cells are those of the section 32
  confirmation of 7 September† [code: results/strong_vs_strong/armC_cells.json against
  results/m3/hstar_m3c_*.json and results/m3/decide_m3b_*.json, e.g. `pccentrist` replicate 1, id
  36f5def553].

On gated cells the stored verdicts were reused, 62 of 62 in all 27 gpt-4o cells [§41].

**What a replicator receives.** Every essay and every per-statement stance cache that these
re-scores read sits in `out/`, which git ignores ("raw run artefacts are not" committed), so none of
them is in the repository [code: .gitignore:166-167]. ETHICS.md releases aggregate stance matrices
and coordinates and withholds the essay corpus of the offensive personas; it does not say whether
the essays and stance caches of the other personas are released [ETHICS.md]. Until that is decided,
the held-fixed results of this section, the gemma3 gate re-score and the assessor comparison, can be
checked from the release only against the aggregate stance matrices, not repeated.

> Note for the authors: decide which essay sets and per-statement stance caches are released, which
> ETHICS.md permits for every persona except the offensive ones, and state the decision here and in
> Section 11. The working copy's `out/` holds the essays and caches of every confirmation a reported
> D rests on, and of every ablation replicate; of the H\* candidates run it holds only the
> `pccentrist` replicates, which are also confirmation replicates. It holds the per-statement caches
> of the mistral and gemma3 enumerations, 71† of 71 each, including the gemma3 re-score's `_gate`
> caches, but essays for only 0† of the 71 mistral enumeration ids and 1† of the 71 gemma3 ids
> (`stalin`, whose id is also a confirmation replicate, Section 3.5). The other enumeration essays,
> which include those the gemma3 gate re-score read (no essay file exists for `facist`, id
> cbd94fbe67), exist only on the workstation and must be copied before they can be released [code:
> out/essays; out/ratings]. The comments at code/decompose_acquiescence.py:442-443 and 451-452 say
> the mistral and gemma3 rating caches "were not synced into this repo"; the working copy now holds
> them, so the comments need updating.

## 3.5 Persona search and its controls

**Search as a probe.** Persona search appears in this paper as a probe of the measurement, not as
a way to find a model's position: whether its gain is a move in position depends on the model and
on one sentence in the baseline [§40], and on a reading that was not registered, what it found
through essays did not carry over when the same personas chose options directly [§39].

**What the early searches exposed.** Two earlier searches are reported only for what they
exposed. NSGA-II over the six-slot fragment space of 4800 prompts did no better than uniform
sampling [§26]. Persona evolution on gpt-3.5-turbo, 236 evaluations on a 20-statement surrogate,
seeded with six moderate personas and with operators barred from the terse instruction register,
exposed a defect in its objective [§27, §30]. The surrogate takes the propositions with the
largest achievable swing, half from each axis [§4; code: code/prism_eval.py:274-293], but keeps
the full instrument's transform, whose divisors are fixed for 62 propositions, so the social axis
of a 20-statement subset runs only from −1.13 to +4.10 [§27]. 80 of 116 libertarian candidates
sat bit-exactly on that floor, and four of them lie 1.67 units apart on the full instrument [§27,
§28]. The driver now maps a subset's range onto the full instrument's, so that a bound reads as a
bound, and flags a run that lands on one; tied candidates stay tied, so a rescaled subset score is
never quoted ["What is not yet done"; code: code/prism_eval.py:295-342, 492-502]. No reported
comparison uses a surrogate [§32].

**The protocol.** Every search comparison in the results follows one protocol [§32; first
pre-registration, second round; third and fifth pre-registrations]. For gpt-3.5-turbo,
gpt-4o-mini and mistral it was adopted after the first round's result and was not registered in
advance (Section 3.6).

- *Objective.* The full 62-proposition instrument [§32], which in the search driver needs
  `--max-questions 0` because the default is still the 20-statement surrogate [code:
  code/evolve_persona.py:147; the search logs, e.g. results/fair2_t35_evo.json, record 0]. Two
  objectives, the social coordinate pushed in the authoritarian direction and response entropy
  kept high, with survival by non-dominated sorting among feasible candidates [code:
  code/evolve_persona.py:124-132, 302-313]. Survivors are taken front by front, and a front that
  does not fit is cut in list order, with no crowding distance [code:
  code/evolve_persona.py:305-309]. Only the authoritarian direction was searched under this
  protocol ["What is not yet done"].
- *Seeds.* Generation 0 is the model's own top six hand-written personas from its enumeration
  [§32]; on gpt-5.4-mini, the top six feasible under the Neutral rule [third and fifth
  pre-registrations].
- *Operators.* A rewriting model mutates one parent into a persona that "pushes harder towards"
  the target or, with probability 0.4† when at least two parents exist, combines two; either may
  write in any register, from a paragraph to a label [§32; code: code/evolve_persona.py:56-99,
  281-291]. The rewriting model is gpt-4o-mini at temperature 0.9† [code:
  code/evolve_persona.py:142, 191]. Children of 80† characters or fewer are discarded, and texts
  identical once whitespace and case are normalised are evaluated once [code:
  code/evolve_persona.py:120-121, 231-238, 290]. In the search arm, parents are drawn uniformly
  from the first non-dominated front of the feasible population, or from the whole population if no
  candidate is feasible, not from all survivors [code: code/evolve_persona.py:278-279, 283, 287].
  The driver's random number generator has a fixed seed, `--seed` 1† by default [code:
  code/evolve_persona.py:150, 181]. The seed fixes only the random draws that pick parents and
  decide whether a child is a combination; every child is written by the rewriting model at
  temperature 0.9† with no seed, so a re-run with the same seed produces different candidates
  [code: code/evolve_persona.py:191, 263, 284, 288]. A search therefore cannot be regenerated. Its committed log, which records every
  candidate's text, origin and scores, is the record of it [code: `results/**/*_evo.json` and
  `*_ctrl.json`, e.g. results/fair2_t35_evo.json, results/m3/search_m3_evo.json].
- *Budget.* Population 6 for 8 generations, 6 × 8 = 48 single-draw evaluations per arm, the six
  seeds included [third pre-registration; §32].
- *Matched control.* A `--no-selection` arm with the same operator and budget, in which every
  child is a fresh rewrite or combination of feasible seeds and nothing is selected [§32; code:
  code/evolve_persona.py:154-159, 278-301]. The first runs on gpt-3.5-turbo and gemma3 let the
  control draw on infeasible seeds and were re-run with matched parents [fourth
  pre-registration].
- *Confirmation.* The best feasible candidate of each arm and H\*, the model's best hand-written
  persona on the social axis (on gpt-5.4-mini the best feasible one under the Neutral rule), are
  confirmed at n=12 in randomised complete blocks; gpt-4o-mini's confirmation was extended to n=24,
  a departure from the registered rule (Section 3.6). Each round runs one replicate of every
  persona in an order shuffled from a fixed seed, `--block-seed` 1† by default, and concurrent
  processes take disjoint replicate indices [first, third and fourth pre-registrations; §32, §33;
  code: code/confirm_persona.py:92-96, 115-126]. A replicate is meant to be a fresh essay set,
  forced by the prompt label, which enters the configuration id and not the prompt [first
  pre-registration; §27; code: code/confirm_persona.py:14-16, 140]. Where that failed is set out
  below. Feasibility is not re-applied at confirmation [fifth pre-registration, outcome].
- *Quantities.* On confirmed social means, D = search − H\*, variation = control − H\*, and
  selection = search − control [§32]. The split between variation and selection changed sign on
  every model with two runs and again when the answer instruction was removed, so no split is
  claimed [§36, §40].

**Where H\* was not measured fresh.** The confirmation's prompt label, `confirm-<name>-r<rep>`, is
the scheme the enumerations and earlier runs also used. An H\* arm named after its `roles.py`
entry, on the same model with the same cap, therefore has the configuration id of any earlier run
of that persona at the same replicate number, and reads that run's cached essays and ratings
instead of drawing new ones (Section 3.1) [code: code/confirm_persona.py:133-140;
code/prism_eval.py:165-179, 372-376]. The stored ids show this for every section 32 confirmation
and for gemma3's first:

- *gpt-3.5-turbo.* `pcxrightauth` replicates 1 to 12 of the second-round confirmation (9
  September†) carry the ids and scores of the first round's H\* arm (27 August†), which is why H\*
  is +7.393 in both rounds [first pre-registration, first and second outcomes; code:
  results/fairconf_t35_*.json against results/decide_[0-5].json, e.g. replicate 1, id d1f2f051ac].
  Replicate 1 is also the enumeration run from which H\* was selected [code:
  results/allroles_full62_3.json].
- *gpt-4o-mini.* `pcxrightauth` replicates 1 to 12 are those of an earlier run (29 August†), the
  transferred-persona comparison §30 withdraws, and replicate 1 is again the enumeration run;
  replicates 13 to 24 are new [§30; code: results/fairconf_t4o_*.json against
  results/decide_m2_*.json and results/m2_gpt4omini_0.json, replicate 1, id ff80023e82].
- *mistral.* `pccentrist` replicates 1 to 12 of the section 32 confirmation (7 September†) are
  those of the H\* candidates run of 3 September† [§36; code: results/m3/decide_m3b_*.json against
  results/m3/hstar_m3c_*.json, e.g. replicate 1, id 36f5def553]. That run, which §36 calls "H\*
  candidates", confirmed mistral's six top hand-written personas from its enumeration, `pccentrist`,
  `pcxrightauth`, `hilter`, `stalin`, `radred` and `pcxright`, at n=12 each in randomised complete
  blocks and with a 1,200-token cap, together with the section 27 persona `crossover` [code:
  results/m3/hstar_m3c_*.json, whose 72 hand-written ids reproduce only at 1,200, and whose
  `best_search` ids reproduce with the `crossover` text of results/persona_evo_auth.json;
  results/m3/m3_mistral_*.json; commit ba85345, "the top six hand-written personas and the search
  candidate confirmed at n=12"]. `pccentrist` became H\* because it had the highest mean of the
  six, +1.863 against +0.600† for `hilter`, the next [§32; code: results/m3/hstar_m3c_*.json]. The
  enumeration ran uncapped, so its `pccentrist` id, 1a301b0509, differs.
- *gemma3, first run.* `stalin` replicate 1 is the enumeration run [code: results/m4/m4_conf_0.json
  against results/m4/m4_gemma_5.json, id 2fc400ff49].

So on gpt-3.5-turbo, gpt-4o-mini and gemma3's first run, the n=1 screening draw from which H\* was
selected is one of its own confirmation replicates, and the confirmed H\* is not independent of
the selection. On mistral the dependence is complete. H\* was selected as the largest of six n=12
means, and all twelve of its confirmed replicates are the replicates it was selected on, so
mistral's confirmed H\* is a maximum over six means and consists entirely of selection data. Its
margin of 1.26 units over `hilter` makes the upward bias of taking that maximum small, but the
confirmed value is not an independent measurement. The same twelve replicates are the H\* cells of
Arm C in the sixth pre-registration (Section 3.4) and the intact `pccentrist` arm of the seventh
(Section 3.7), the intact side of δ = +4.331, which is the Prompt bar of OUTLINE's Figure 1 [§40;
OUTLINE, Figure 1; code: results/strong_vs_strong/armC_cells.json and
results/answer_format_ablation/afmt_m3_paired_*.json carry the same twelve ids]. On gpt-3.5-turbo,
gpt-4o-mini and mistral, twelve H\* replicates were drawn outside the confirmation's blocks, which
reintroduces the aliasing of persona with time that the first pre-registration adopted blocks to
remove [first pre-registration, "The measurement"]. The fourth pre-registration's re-runs and the fifth name H\* `H_<name>`, and those are the only H\*
arms drawn fresh inside their blocks, as the fourth's design required ("re-measured fresh inside
those blocks rather than read from the earlier confirmation") [fourth and fifth pre-registrations;
code: results/fair2conf_t35_*.json, results/m4/m4b_conf_*.json and results/m5_conf_*.json share no
H\* id with an earlier run]. The same mechanism reached the ninth pre-registration (Section 3.7).

> Note for the authors: FINDINGS and PREREGISTRATION describe these H\* arms as measured inside the
> blocks, and §40 and the ninth pre-registration describe the `pcleftlib` intact arm as generated
> fresh. The stored ids contradict both. Either record the reuse in FINDINGS and PREREGISTRATION, or
> re-measure the affected H\* arms under `H_` names; the section 32 D values stand until then only
> with this disclosure.
>
> A second point for the authors: the H\* candidates run is also the first-round mistral comparison
> that §30 withdraws; commit ba85345 recorded it as the mistral result and described its search arm
> as a transferred persona. §30's table says mistral's first-round search arm was "a search actually
> run on the model", but that run's `best_search` ids reproduce with the section 27 `crossover` text,
> a persona searched on gpt-3.5-turbo [code: results/m3/hstar_m3c_*.json;
> results/persona_evo_auth.json]. §30 should be checked against the stored run.

**The winner's curse.** A search-time best is the maximum of 48 single draws and shrank by up to
1.513 units on confirmation [§32]; only confirmed means are admissible [first pre-registration].
Search arms plateau by generation 2 to 5 of 8 and two control arms were still improving at
generation 8, so no search is claimed to have converged ["What is not yet done"].

## 3.6 Decision rules

**What was registered, and when.** Each decision rule was committed to PREREGISTRATION.md before the
runs it governs, or for the first before its confirmation data were read [each entry; §33]. That
holds for the rules, not for every protocol. The protocol of Section 3.5 as run on gpt-3.5-turbo,
gpt-4o-mini and mistral (full instrument, freed operators, each model's own top six seeds, a matched
control) was adopted after the first round's negative outcome, which §30 withdraws, and no entry
fixes it in advance: it appears only in the appended "Outcome, second and final round" [first
pre-registration; §30]. For those three models only the D rule was registered before the runs. The
protocol is first fixed before a run in the second pre-registration, for gemma3 ("Decision, fixed
now: run the same protocol"); the third and fifth fix it for gpt-5.4-mini, and the fourth for the
matched-parent re-runs [second to fifth pre-registrations]. The analysis scripts of the eighth,
tenth and eleventh entries were committed before their results were read and tested only on
synthetic input [§39; tenth and eleventh pre-registrations]; where a script first ran on partial
data, the values it printed are disclosed in the entry [sixth pre-registration, amendment A4;
seventh pre-registration, disclosure]. Amendments are dated, and each records when it was written
relative to the data. The sixth's A1 to A5 were written after Arm A's unroled cells for four models
had been scored and the four Δ_base values printed (A4), and before any gpt-5.4-mini cell, the
gpt-5.4-mini baseline or Arm C had been analysed. The seventh's B1 and B2 were written after the log
of the first two gpt-5.4-mini blocks, with its refusal counts, had been seen, and before any δ was
computed; B1 adds refusal-based endpoints because of those counts (17 of 62 statements refused in
one stripped replicate). The eighth's amendment was written while its runs were in progress, before
any output was read [amendments to the sixth, seventh and eighth pre-registrations].

**The rules.** They take three forms. For the search gain D, with Welch intervals: *positive* if
the one-sided 95% lower bound is at least +0.50, *negative* if the 95% upper bound is below 0,
*equivalent* if the 90% interval lies inside the equivalence bound, *unresolved* otherwise [first
pre-registration]. For a contrast between two conditions on one persona, forced choice against
essay or intact against stripped: a Welch 95% interval inside the bound is *equivalent*
(*format-neutral*), one wholly beyond it is *different* (*format-carried*, or *reversed* if
removing the instruction raises the score), and anything else is *unresolved* [seventh, eighth
and ninth pre-registrations], reported as such and not topped up [seventh pre-registration]. The
remaining entries set a prediction band or tolerance, a replication rule, or count and rate
thresholds.

**The n=24 extension.** gpt-4o-mini's confirmation was extended from n=12 to n=24. No
pre-registration specifies n=24, and the first's rule for an unresolved result is that "the
instrument cannot resolve the difference at this budget; say so and stop spending on it", so the
extension is an unregistered departure from the registered rule [first pre-registration, decision
rule; §33]. Both verdicts are reported. At n=12, D was +0.479 [+0.098, +0.859], unresolved [first
pre-registration, second round; §32]. At n=24, D is +0.656, unresolved under ±0.75 and equivalent
under the ±0.89 bound below, 90% interval [+0.443, +0.869] [§33, §41]. The move to equivalent rests
on the n=24 data. The confirmation is not extended further ["What is not yet done"].

| entry | question | decision rule | outcome recorded in |
| --- | --- | --- | --- |
| first | does search beat the best hand-written persona on gpt-3.5-turbo? | D rule, ±0.75 | the entry's first outcome, withdrawn [§30]; its second round applied the rule to three models under a protocol chosen after that outcome [§32] |
| second | on gemma3, does the gain track the baseline's fit or the vendor? | D in +0.6 to +2.5 supports fit, above +2.8 family, below +0.3 neither | §33 |
| third | does the §33 line hold on gpt-5.4-mini, gated, Neutral rule? | observed D within 1.0 of predicted; an extrapolation if H\* lies outside +1.86 to +7.39 | superseded by the fifth before any result [fifth pre-registration] |
| fourth | the two confounded controls re-run with matched parents, gpt-3.5-turbo and gemma3 | selection on gpt-3.5-turbo, variation on gemma3, and D inside the original 95% interval | the entry's outcomes; §36 |
| fifth | the third, under gate v3 | as the third | §35 |
| sixth | do two strong assessors agree on unroled and boundary cells? | equivalent, material or intermediate (below) | §41 |
| seventh | does the answer instruction carry position (mistral, gemma3 two runs, gpt-5.4-mini)? | δ = intact − stripped against the bound | §40 |
| eighth | forced choice against essay, three hosted models, option order counterbalanced | Δ = forced choice − essay against the bound | §39, re-read in §41 |
| ninth | the instruction inside `pcleftlib` on gpt-3.5-turbo | as the seventh, sign reversed for a libertarian persona | §40 |
| tenth | llama3.2, enumerated ungated then gated | P1 prevalence, P2 size, S1 identity labels, R pre-filter alone | §43 |
| eleventh (Section 3.8, conditional) | the stance flip: frame ablation and transfer, statements 4 and 27 | endorsement-rate differences of at least 0.5; resisted at 0.1 or below | §42 |
| twelfth (Section 3.8, conditional) | the eleventh's local arms, sampled | as the eleventh, valid only with at least 12 distinct essays of 24 | not yet recorded |

> Note for the authors: PREREGISTRATION.md holds thirteen entries, all with recorded outcomes;
> the twelfth (line 908) has none yet. OUTLINE §3.6 says "Eleven pre-registrations", and the brief
> this draft was written to says eleven, all with outcomes. Both predate the twelfth entry and need
> reconciling.

**The equivalence bound.** The first pre-registration set ±0.75 from the 0.72-unit gap between
gpt-4o and gpt-4o-mini on three identical essay sets and the replicate sd of 0.73 for H\* [first
pre-registration; §29]. The sixth tested it on all five models: *equivalent* if every unroled
|Δ_base| is at most 0.75 and every ΔD interval lies inside ±0.75, *material* if any |Δ_base|
reaches 2.0 or any ΔD interval lies wholly beyond ±0.75, and otherwise *intermediate*, with every
equivalence bound widened to the upper 95% limit of the measured term [sixth pre-registration].
The outcome was intermediate, and the bound became ±0.89, where mistral's ΔD interval reaches
−0.889 [§41]. Recorded verdicts are re-read under the wider bound and reported under both [§41;
eighth pre-registration]; the tolerance of 1.0 on the gpt-5.4-mini prediction is a separate rule
and does not change [§41].

**Reading an interval.** The Welch intervals on confirmed means assume independent replicates
[§36]. We count distinct essays per proposition across each arm's replicates by hashing the essay
files [§36; code: results/replicate_independence/replicate_independence.py:14-40]. A hosted model
varies from call to call even at temperature 0: gpt-3.5-turbo gives 9.3 to 11.0 distinct essays
per proposition in 12 replicates, gpt-4o-mini 11.8 of 12 and 23.6 of 24, and gpt-5.4-mini 12.0
[§36]. A local model at temperature 0 varies only when the server batches requests differently:
mistral gives 3.7 to 4.7 on its search confirmation and 1.0 to 3.7 on the H\* candidates run of
Section 3.5, gemma3
3.0 to 4.9 on its first confirmation and 1.0 to 3.0 on the matched re-run, and some personas
return one essay in all twelve runs [§36]. Identical essays still score differently: on mistral,
`stalin` wrote one essay per proposition in all twelve runs and returned three distinct scores,
sd 0.252, the assessor's nondeterminism alone [§36]. Three rules follow. Intervals on mistral and
gemma3 are reported beside their distinct-essay counts and read as overstating precision; where
two independent search runs exist, their spread is the better measure, and only gpt-3.5-turbo and
gemma3 have two, whose D values agree on gpt-3.5-turbo (−0.34 and +0.06) and differ by 0.70 on
gemma3 [§36; sixth pre-registration, amendment A3]. A standard deviation of zero from
byte-identical essays is read as determinism, not precision, and its interval as invalid [fourth
pre-registration, gemma3 outcome]. A local verdict resting on one essay per cell is a single
observation [§36, §42].

**Outcomes and withdrawals.** Outcomes are appended under each entry, failures included [§35,
§36]. A rule is applied as written even when its label misleads, and the entry says so: the
fourth's split rule returned "stands" on gemma3 although the split had moved the other way [fourth
pre-registration, gemma3 outcome]. Faults are corrected in the open: the fifth's confirmation was
first stored under the wrong refusal rule and was re-scored from its cached stances, and a search
launched under gate v2 was stopped after one evaluation per arm, before any score was read, and
re-registered [fifth pre-registration; §35]. Withdrawn claims stay in FINDINGS.md, marked
superseded, corrected or qualified, with the reason [§30, §31, §32, §33, §36].

## 3.7 Forced choice and answer-format ablation

**Forced choice.** The second elicitation route removes the essay and the assessor. The persona
answers each proposition by choosing one of the four options, listed ascending (Strongly disagree
first) or descending, and the chosen option goes through the same key and transforms [eighth
pre-registration; §39; code: code/utils/forced_choice.py:26-45]. A reply is read as the first
option it names, longer labels matched first so that "Strongly disagree" is never read as
"Disagree", and as Refused if it names none; no gate applies, because a decline is itself the
answer [eighth pre-registration; code: code/utils/forced_choice.py:34-66]. The registered
experiment ran gpt-3.5-turbo, gpt-4o-mini and gpt-5.4-mini, each with five personas: the unroled
baseline, the authoritarian H\* (`pcxrightauth` on the first two, `pcrightauth` on gpt-5.4-mini),
the libertarian H\* `pcleftlib`, and the confirmed search and control winners, whose texts matched
their confirmation ids, 12 of 12, 24 of 24 and 12 of 12 [eighth pre-registration]. Each persona
has n=12 in randomised complete blocks, replicates 1 to 6 listing the options from Strongly
disagree to Strongly agree and 7 to 12 in reverse, and refusals are scored under both rules [eighth
pre-registration; §39]. 11,157 of the 11,160 replies (3 models × 5 personas × 12 replicates × 62
propositions) were exactly one option, and none declined [§39].

The primary contrast, Δ = forced choice − essay, is taken for the three personas with an essay
confirmation at n=12 or more [eighth pre-registration]. The essay arms are existing confirmations,
rescored from their caches under each model's registered rule [§39]: on gpt-3.5-turbo the fourth
pre-registration's matched-parent confirmation (H\* +7.320, search +7.384, control +6.842), on
gpt-4o-mini the section 32 and 33 confirmation at n=24, whose H\* replicates 1 to 12 are the reused
ones of Section 3.5, and on gpt-5.4-mini the fifth's [§39; fourth and fifth pre-registrations,
outcomes]. The unroled baseline and `pcleftlib` have one essay replicate each, so their comparison
is descriptive and carries no verdict [eighth pre-registration]. At temperature 0 a one-word
answer repeats: the two older models give 1 to 5 distinct answer sets in the 6 replicates of one
option order, against 5 or 6 on gpt-5.4-mini, so the forced-choice intervals on those two models
overstate precision [§39].

**The answer instruction.** "State whether you either Strongly Agree or Strongly Disagree" is
verbatim in ten hand-written personas, among them five that seeded the gemma3 or gpt-5.4-mini
searches and `pcleftlib`, the libertarian H\*; mistral's seeds carried only a plain "Agree or
Disagree" form, through `pccentrist` [§36 correction; §40]. Where it sits in each arm was
recovered from the search logs and checked against each confirmation by configuration id [seventh
pre-registration]. The ablation removes it under an edit rule registered as code: a sentence-level
deletion where the sentence is only the instruction, a clause-level deletion where it shares a
sentence with political content, and one declared substitution on mistral's search winner,
"either Agree or Disagree" replaced by "your view"; the script asserts that everything outside the
edited span is byte-identical [seventh pre-registration; §40;
`results/answer_format_ablation/build_personas.py`].

**Design.** Each model's ablation runs under the flags of its own confirmation (Table 3.1), n=12
per arm [seventh pre-registration]. The registration interleaves intact and stripped personas in
the same randomised complete blocks, and also has the intact arms keep their original names so that
their cached essays are reused [seventh pre-registration, design; §40]. The second makes the first
hold only for the stripped arms. On gpt-5.4-mini, mistral and gemma3 every intact replicate has the
id of an earlier run and reads that run's essays and ratings, so the blocks, run on 16 September†,
randomise only the stripped arms, and each intact arm is an earlier run with its own date: 13
September† on gpt-5.4-mini; on mistral, 3 September† for `pccentrist`, whose twelve replicates are
those of the H\* candidates run (Section 3.5), and 7 September† for the search and control winners;
on gemma3, 11 September† for the first run and 13 and 14 September for the second [code:
results/answer_format_ablation/afmt_*.json against results/m5_conf_*.json,
results/m3/hstar_m3c_*.json, results/m3/decide_m3b_*.json, results/m4/m4_conf_*.json and
results/m4/m4b_conf_*.json, matched by configuration id]. δ therefore compares arms drawn on
different occasions, which is the aliasing of persona with time that Section 3.5 describes for H\*.
The negative controls are arms that never carried the instruction: the search winner on
gpt-5.4-mini and `stalin` on gemma3 [seventh pre-registration; §40]. They are cached earlier runs
too, so they cannot show an occasion effect either [code: as above]. On gpt-5.4-mini a drift probe
of three fresh draws per intact persona, at replicates 13 to 15, must land within 0.75 of the
historical mean or the comparison is void [seventh pre-registration; §40]; it passed, every intact
arm within 0.23 [§40]. No drift probe tested the occasion effect on mistral or gemma3 [seventh
pre-registration, design]. Beside every δ are reported refusals per run, the share of runs refused on
more than six statements, and δ recomputed with refused statements excluded [seventh
pre-registration, amendment B1]. The ninth pre-registration applies the same rule to `pcleftlib`
on gpt-3.5-turbo, with the labels' sign reversed for a libertarian persona, and says both arms are
generated fresh because the enumeration named the persona rather than passing its text [ninth
pre-registration]. The stored ids show otherwise: replicate 1 of the intact arm has the id and
score of the enumeration run, so the enumeration passed the text and that replicate reused its
essays (Section 3.5) [code: results/answer_format_ablation/afmt_pcleftlib_gpt35_0.json against
results/allroles_full62_1.json, id 79b27eb13c].

## 3.8 Stance-flip frame ablation and transfer

This subsection is included only if the stance flip appears in the paper (OUTLINE, Decision 5).

**Personas.** Four personas: `none` (empty), `seed`, and the two evolved personas `crossover` and
`mutation` from the section 27 search [eleventh pre-registration; §42]. `build_flip_personas.py`
recovers them from the committed search log, `results/persona_evo_auth.json`, by reproducing the
configuration ids section 27 recorded, and writes them to a local file that git ignores [eleventh
pre-registration; code: results/stance_flip/build_flip_personas.py; .gitignore:176-177]. Only that
rebuilt file is kept out of git. The texts themselves are in tracked files (note below).

> Note for the authors, an ETHICS.md compliance issue rather than a matter of wording: ETHICS.md
> lists the search-derived persona texts that produce the stance flip as "Not released", and the
> eleventh pre-registration says "The persona file itself is kept out of git". Only
> `results/stance_flip/personas_flip.json` is ignored. `results/persona_evo_auth.json`, from which
> it is rebuilt, is tracked and holds both evolved texts; a search of the tracked files made while
> revising this section also finds `crossover` in `results/persona_evo_summary.json` and, under the
> name `_search_best`, written out in `results/refusal_gate_validation/persona_blind_ablation.py`.
> `_search_best`, one of the two search-derived personas every enumeration after gpt-3.5-turbo's
> includes, is the same text as `crossover`: the `crossover` text reproduces the stored
> `_search_best` id in the gpt-4o-mini, mistral, gemma3, gpt-5.4-mini and llama3.2 enumerations
> [code: results/m2_gpt4omini_*.json, results/m3/m3_mistral_*.json, results/m4/m4_gemma_*.json,
> results/m5_gpt54mini_*.json, results/m6/m6_llama_*.json; results/m6/build_llama_personas.py:55-61
> recovers both search-derived texts from committed results]. Before the code and results are
> released, these texts have to be removed from `persona_evo_auth.json` and from every other tracked
> file that holds them, and from the history of any repository that is published with them. Until
> then the release statement held for Section 11 is false.
>
> A scope decision for the authors, not a wording fix: that removal list covers only the two tested
> texts, and a search of the tracked files finds those two only where this note says. The same
> tracked log holds all 120 candidates of the section 27 authoritarian search [§27], and none of the
> others was tested for the flip. They include the generation-0 rewrite, which every later
> enumeration audited as `_search_gen0`, and the generation-1 crossover. On the full instrument those
> two score +6.20 and +6.39, against +6.23 for `crossover` and +6.46 for `mutation`, all four inside
> a 0.26-unit band [§28; code: evaluation 8 of results/persona_evo_auth.json reproduces the stored
> `_search_gen0` ids]. The generation-0 rewrite is also written out in the ignored
> results/m6/personas_llama32_1.json [code: .gitignore:184]. Removing two texts from a log of close
> siblings may not meet ETHICS.md's intent. The release plan has to decide whether the whole section
> 27 authoritarian log is withheld, together with that ignored file, or only the two tested texts,
> and Section 11 has to state the decision.

**Probe.** Statements 4 and 27 only, n=12 replicates per persona in randomised complete blocks,
each replicate a fresh essay on both statements, gate v3 on, gpt-4o-mini-2024-07-18 assessing
[eleventh pre-registration]. Part A runs gpt-3.5-turbo, the model the flip was found on, under the
paper frame and the neutral frame of Section 3.1. Part B, transfer, runs the paper frame only on
gpt-4o-mini and gpt-5.4-mini, and on gemma3, mistral and llama3.2 on the workstation with a
1,200-token cap [eleventh pre-registration; §42].

**Endpoint.** Per cell, the endorsement rate e is the share of replicates whose stance on that
statement is Agree or Strongly agree. A gate REFUSED verdict counts as not endorsing and is
reported beside e as a refusal rate [eleventh pre-registration; §42]. The refusal rule does not
enter e.

**Rules.** Decisions are taken on `crossover`, the persona section 27 reports, and `mutation` is
reported under the same rules as a second evolved persona [eleventh pre-registration].

- *A1:* the flip **reproduces** if e(crossover, paper) − e(seed, paper) ≥ 0.5 on both statements.
- *A2:* **persona-carried** if e(crossover, neutral) − e(none, neutral) ≥ 0.5 on at least one
  statement; **frame-dependent** if A1 reproduces and e(crossover, neutral) ≤ 0.25 on both;
  otherwise **mixed**.
- *A3:* **frame alone** if e(none, paper) ≥ 0.5 on either statement.
- *Transfer, per model:* **transfers** if e(crossover) − e(none) ≥ 0.5 on at least one statement;
  **resisted** if e(crossover) ≤ 0.1 on both; otherwise **partial**.

A second assessor, gpt-4o, re-labelled the essays the gate did not refuse; it was added after the
hosted results were seen and is reported as an addition [§42; eleventh pre-registration,
outcomes].

**Replication.** At temperature 0, gemma3 and mistral wrote one essay per cell, repeated twelve
times, and llama3.2 one to four, so the local verdicts are single observations, whereas
gpt-4o-mini's statement 27 endorsements are twelve distinct essays [§42]. The twelfth
pre-registration samples the local arms at writer temperature 0.8, n=24 per persona, and counts a
verdict only if every `crossover` and `none` cell holds at least 12 distinct essays of 24; its
outcome is not yet recorded [twelfth pre-registration].

**Handling.** In the tenth to twelfth pre-registrations nobody reads essays beyond the gate and the
assessor, the essays stay in the ignored `out/` directory, and stance-flip results are reported as
rates, with no essay or persona text quoted [tenth, eleventh and twelfth pre-registrations].

## Text held for Section 11 (remove from this file when Section 11 is drafted)

Moved out of Section 3, because OUTLINE gives ethics its own section (§11).

The project generates essays in offensive personas, including personas named after Hitler and
Stalin, and its search produced personas under which gpt-3.5-turbo endorses racial superiority
and segregation, a change in the stance the model expresses rather than a refusal bypass
[ETHICS.md; §27, §42]. Anyone who reads essays for the project is told beforehand which personas
and what content the sample holds, reads only after agreeing to and may stop at any point, works
in bounded sessions with the most extreme personas spread across them, and is never a naive or
unpaid reader; quotations are the shortest that make the point and are marked as model output
[ETHICS.md]. In the tenth to twelfth pre-registrations nobody reads essays beyond the gate and the
assessor, and stance-flip results are reported as rates, with no essay or persona text quoted
[tenth, eleventh and twelfth pre-registrations]. Earlier work did involve reading essays: the
section 27 stance-flip essays, the gate verdicts behind version 3 (outside any registered
experiment), and the intact essays of the ninth pre-registration [§27; §34; fifth
pre-registration, "Why it is re-registered"; §40]. Released with the paper: the code, the refusal
gate and its validation set, the scoring analysis, the pre-registrations and outcomes, aggregate
stance matrices and coordinates, and the hand-written persona library. Withheld, and available to
named researchers for replication with the exposure note attached: the search-derived persona
texts that produce the stance flip, and the full essay corpus for the offensive personas
[ETHICS.md]. That statement is not yet true of the repository: only the rebuilt persona file is
kept out of git, and the texts are in tracked files, so they must be removed from those files, and
from the history of any repository published with them, before the code and results are released
(Section 3.8) [ETHICS.md; code: .gitignore:176-177]. Which search-derived texts count as withheld,
the two tested texts only or the whole section 27 authoritarian log, is not yet decided, and this
statement must name the decision (Section 3.8). The release list also leaves out the other essays
and the per-statement stance caches that the held-fixed re-scores read; without them those results
cannot be repeated from the release, and this statement must say whether they are released
(Section 3.4). There are no human subjects and no personal data; the gold labels used to validate
assessors come from existing corpora under their own terms, and the propositions are quoted from a
copyrighted web quiz, which is also why the instrument is not treated as a validated psychometric
scale [ETHICS.md].

## Code-only values (remove before submission)

Each value below is marked † above. It comes only from the code, a data file or a stored result,
and does not yet meet the brief's rule that every number appears in FINDINGS.md or
PREREGISTRATION.md or is derived from numbers that do. The authors should either record these in
FINDINGS.md or agree an exception for code constants; until then this draft does not claim that
they meet the rule.

| value | where it is used | source |
| --- | --- | --- |
| 10 hexadecimal characters per configuration id | 3.1 | code/prism_eval.py:48-70 |
| 26 August 2026, 16 September and 21 September, the dates keys entered the id function | 3.1 | `git log -L48,71:code/prism_eval.py` (commits 69f0078, df1f575, 2906222) |
| 27 August, the date of commit 11777fa, to which svs_cells_verified.json credits the change | 3.1 | results/strong_vs_strong/svs_cells_verified.json; `git show 11777fa` |
| gpt-3.5-turbo-0125, gpt-5.4-mini-2026-03-17, gpt-4o-2024-08-06 | 3.2 table | code/utils/model_versions.py:18-23 |
| digests 6577803aa9a0 (mistral) and a2af6cc3eb7f (gemma3) | 3.2 table | code/utils/model_versions.py:25-30 |
| 21 September 2026, the day the pins were set | 3.2 note | code/utils/model_versions.py:9 |
| 300-token default cap in the prompt-fragment search driver | 3.1 | code/optimise_prompt.py:170 |
| 25 characters in the pre-filter's first-person window | 3.3 | code/utils/refusal_gate.py:53 |
| midpoint totals −47.0 (social) and −2.5 (economic) | 3.3 | data/pc_lookup.csv |
| a 1,200-token cap on the gemma3 enumeration, the mistral and gemma3 confirmations and the local ablations | 3.3, Table 3.1 | configuration ids reproduced from results/m4/, results/m3/decide_m3b_*.json, results/m3/hstar_m3c_*.json, results/answer_format_ablation/ |
| crossover probability 0.4 | 3.5 | code/evolve_persona.py:282 |
| rewriting temperature 0.9 | 3.5 | code/evolve_persona.py:191 |
| 80-character minimum for a child | 3.5 | code/evolve_persona.py:290 |
| `--seed` 1 and `--block-seed` 1 | 3.5 | code/evolve_persona.py:150; code/confirm_persona.py:92 |
| run dates 27 August, 29 August, 3, 7, 9, 11 and 16 September | 3.2, 3.4, 3.5, 3.7 | `t_iso` fields of the result files named there |
| +0.600, `hilter`'s mean in the H\* candidates run | 3.5 | results/m3/hstar_m3c_*.json; commit ba85345 |
| 71 of 71 enumeration caches, and essays for 0 and 1 of 71 enumeration ids, in the working copy | 3.4 note | out/ratings, out/essays |

## Derived numbers (remove before submission)

Every number above not marked † appears in FINDINGS.md or PREREGISTRATION.md at the anchor beside
it, or is derived below. Configuration ids and commit hashes are identifiers, given so that a
reader can find the file, not measurements.

| number | derivation |
| --- | --- |
| no proposition weighted on both axes | 43 social + 18 economic + 1 unweighted (statement 21) = 62 [§20, §38]; that statement 21 is the only unweighted one is read from data/pc_lookup.csv |
| Neutral label = half the Disagree weight | midpoint (Disagree + Agree) / 2 with Agree = 0 [§2; code: code/utils/utils.py:173, 181] |
| fully refused persona under the Neutral rule | social −47.0/19.5 + 2.41 = −2.4103 + 2.41 = −0.0003, reported in §34 as 0.000; economic −2.5/8 + 0.38 = −0.3125 + 0.38 = +0.0675; the totals −47.0 and −2.5 are code-only (table above) |
| 11,160 forced-choice replies | 3 models × 5 personas × 12 replicates × 62 propositions [eighth pre-registration; §39] |
| 48 evaluations per arm | population 6 × 8 generations [third pre-registration] |
| up to 13 days between the two sides of an assessor pair | 16 September, the gpt-4o draws [sixth pre-registration, amendment A5], minus 3 September†, the earliest gpt-4o-mini side (mistral `pccentrist`) = 13 days |
| 1.26-unit margin of mistral's H\* | +1.863 [§32] − (+0.600†) = 1.263 |
| 72 hand-written ids in the H\* candidates run | 6 personas × 12 replicates [§36, n=12 per arm] |
| thirteen pre-registrations, all with outcomes | the thirteen entries of PREREGISTRATION.md |
