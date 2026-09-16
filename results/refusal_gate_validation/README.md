# Refusal gate validation (FINDINGS section 34)

Scripts as run. `gate2.py` holds the prompt; it is identical to
`GATE_PROMPT` in `code/utils/refusal_gate.py`. `gate_local.py` and `gate_box.py`
are the first, whole-essay gate that was rejected.

## Rejected whole-essay gate (gate_local.py)

| gpt-3.5-turbo set | REFUSED | COMPLIED |
| --- | --- | --- |
| outright refusals (3) | 3 | 0 |
| regex refuse-then-essay (15) | 11 | 4 |
| "As an AI I have no opinions, however" (20) | 16 | 4 |
| ordinary essays (20) | **9** | 11 |

## Kept opening-only gate (gate2_local.py, gate2_box.py)

| set | REFUSED | DISCLAIMED | COMPLIED |
| --- | --- | --- | --- |
| gpt-3.5-turbo outright refusals (3) | 3 | 0 | 0 |
| gpt-3.5-turbo regex refuse-then-essay, in-persona voice (15) | 6 | 3 | 6 |
| gpt-3.5-turbo "As an AI I have no opinions, however" (20) | 0 | 20 | 0 |
| gpt-3.5-turbo ordinary essays (20) | 0 | 3 | 17 |
| gemma3 facist / hilter / extremist (30) | 30 | 0 | 0 |
| gemma3 stalin (20) | 0 | 13 | 7 |

## Effect on the four-model table (sensitivity.py)

Gate flipped 0 statements in the gpt-3.5-turbo and gpt-4o-mini confirmation
arms. Recomputed scores matched stored values with maximum difference 0.

## Plumbing (gate_plumbing_test.py)

16 of 16 checks passed with the gate and classifier stubbed.

## Persona-blind ablation (persona_blind_ablation.py)

Does showing the gate the persona help or hurt? 44 hand-labelled cases
(`v3_labels_*.json`, 8 REFUSED / 36 NOT_REFUSED), 264 gpt-4o-mini calls, run
twice. Results in `persona_blind_ablation.json`.

| condition | refusals kept (8) | false positives (36) | correct |
| --- | --- | --- | --- |
| gate v3 as shipped, persona shown | 7 | 0 | 43/44 |
| gate v3, persona = "(not shown)" | 3 | 0 | 39/44 |
| gate v3, persona = "(none)" | 5 | 0 | 41/44 |
| pre-filter alone | 7 | 0 | 43/44 |
| model stage alone, persona shown (= gate v2) | 8 | 29 | 15/44 |
| model stage alone, "(not shown)" | 4 | 16 | 24/44 |
| model stage alone, "(none)" | 6 | 13 | 29/44 |

**What this set can and cannot show.** Every gpt-5.4-mini case in the label
files, and the gemma3 cases too, was selected from essays the persona-shown gate
v2 had already called REFUSED. So the persona-shown model catching all 8 refusals
and flagging 29 of 36 non-refusals follows from how the set was drawn, and a
refusal that only a blind gate would catch cannot appear in it. The table
therefore does not establish that blinding loses refusals or that showing the
persona doubles false positives. It does show that on these cases the shipped
gate and the pre-filter alone give identical verdicts, case for case, on both
repetitions.

**The verdicts drifted.** Seven of the 44 cases that gate v2 called REFUSED on
13 September no longer return REFUSED from the same prompt, model and temperature
three days later, against 2 of 44 that change between the two repetitions run
back to back here. The model behind the gate moved between occasions.

The two search personas (`_search_best`, `_search_gen0`) are not in `roles.py`;
their prose was recovered from `results/persona_evo_auth.json` (the
`_search_best` text is also in `persona_evo_summary.json` and
`m5_search_ctrl.json`) by matching `config_id` (024886f9d3, f86bd8a6fd) against
the confirmation runs.

## Pre-filter vs model stage on the whole corpus (prefilter_vs_model_corpus.py)

No API calls. 7,812 verdicts already cached by the shipped v3 gate across 126
`cache_*_gpt-4o-mini_gate3.json` files: the pre-filter flags 1,149 and the model
overturns 176 of them (157 DISCLAIMED, 19 COMPLIED), 15.3%. So the model stage
is not inert at scale even though it changes nothing on the labelled set.
