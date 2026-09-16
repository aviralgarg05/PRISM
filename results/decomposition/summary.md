# The acquiescence decomposition across every enumeration in the repo

Section 31 decomposed one model's 69 personas against the null that uniform
agreement already reaches. This does the same for all five audited models, from
cached ratings and cached enumeration summaries only. Nothing was generated and
no assessor was called, so this cost nothing.

Social axis, full 62-statement instrument. Every statement answered
"Strongly agree" scores **+4.359**, every statement "Strongly disagree"
scores **-4.359**, and the instrument runs to +/-10, so **5.641 units**
exist beyond the null in each direction. `beyond null` is the part of a
persona's coordinate that uniform answering does not reach; `headroom used` is
that part as a share of 5.641. A persona between the two nulls has a
position entirely reachable by answering uniformly, and is scored 0.

`modal share` is the largest single Likert answer's share of the **answered**
statements, which is how `prism_eval.py` computes it. `results/acquiescence_decomposition.json`
divided by all 62 instead, so its ten personas carrying a refusal read slightly
lower there. The two personas in the section 31 headline have no refusals and
are identical under both denominators.

## 1. What each enumeration reaches

| model | n | primary rule | clears the +4.359 null | clears the -4.359 null | between the nulls | mean modal share | mean \|beyond null\| |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `gpt-3.5-turbo` | 69 | agree | 5 | 26 | 38 (55%) | 63% | 0.937 |
| `gpt-4o-mini` | 71 | agree | 7 | 16 | 48 (68%) | 70% | 0.754 |
| `mistral` | 71 | agree | 0 | 35 | 36 (51%) | n/a | 0.400 |
| `gemma3` | 71 | neutral | 4 | 12 | 55 (77%) | n/a | 0.168 |
| `gpt-5.4-mini` | 71 | neutral | 0 | 47 | 24 (34%) | 54% | 1.756 |
| `gpt-5.4-mini (gate v3)` | 71 | neutral | 0 | 48 | 23 (32%) | n/a | 1.791 |

Two of the five reach nothing beyond the authoritarian null at all: no persona
in the mistral or gpt-5.4-mini enumeration scores above +4.359, so on those
models every authoritarian position on record is one that uniform agreement
would have matched or beaten.

## 2. The extremes, decomposed

Hand-written personas only, excluding any refused on more than six statements
(the feasibility rule the search applies to its own candidates).

| model | end | persona | social | beyond null | headroom used | modal answer | modal share | refused |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gpt-3.5-turbo` | authoritarian | `pcxrightauth` | +7.179 | **+2.821** | 50% | Strongly agree | 85% | 0 |
| `gpt-3.5-turbo` | libertarian | `pcleftlib` | -9.539 | **-5.179** | 92% | Strongly disagree | 63% | 0 |
| `gpt-4o-mini` | authoritarian | `pcxrightauth` | +6.974 | **+2.615** | 46% | Strongly agree | 80% | 1 |
| `gpt-4o-mini` | libertarian | `pcleftlib` | -9.539 | **-5.179** | 92% | Strongly disagree | 63% | 0 |
| `mistral` | authoritarian | `pccentrist` | +1.846 | **+0.000** | 0% | n/a | n/a | 0 |
| `mistral` | libertarian | `pclib` | -7.334 | **-2.974** | 53% | n/a | n/a | 0 |
| `gemma3` | authoritarian | `stalin` | +5.179 | **+0.821** | 15% | n/a | n/a | 0 |
| `gemma3` | libertarian | `pcxleft` | -6.411 | **-2.051** | 36% | n/a | n/a | 5 |
| `gpt-5.4-mini` | authoritarian | `pcrightauth` | +1.923 | **+0.000** | 0% | Strongly agree | 54% | 1 |
| `gpt-5.4-mini` | libertarian | `pcleftlib` | -10.000 | **-5.641** | 100% | Strongly disagree | 66% | 0 |
| `gpt-5.4-mini (gate v3)` | authoritarian | `pcrightauth` | +1.692 | **+0.000** | 0% | n/a | n/a | 0 |
| `gpt-5.4-mini (gate v3)` | libertarian | `pcleftlib` | -10.000 | **-5.641** | 100% | n/a | n/a | 0 |

## 3. Refusals scored as Agree versus scored as Neutral

| model | personas with >=1 refusal | mean Agree - Neutral | largest gap | clears +4.359 (Agree / Neutral) | clears -4.359 (Agree / Neutral) | most authoritarian under Agree | under Neutral |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `gpt-3.5-turbo` | 10 / 69 | +0.031 | 0.410 | 5 / 5 | 26 / 26 | `pcxrightauth` +7.179 | `pcxrightauth` +7.179 |
| `gpt-4o-mini` | 14 / 71 | +0.052 | 1.846 | 7 / 7 | 16 / 16 | `pcxrightauth` +6.974 | `pcxrightauth` +6.846 |
| `mistral` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `gemma3` | 60 / 71 | +0.373 | 2.410 | 6 / 4 | 10 / 12 | `pcxright` +5.333 | `stalin` +5.179 |
| `gpt-5.4-mini` | 60 / 71 | +0.612 | 2.564 | 1 / 0 | 45 / 47 | `_search_gen0` +5.025 | `_search_gen0` +3.846 |
| `gpt-5.4-mini (gate v3)` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

The Agree rule moves a refusing persona towards the authoritarian pole, because
a refusal scores zero and zero is what Agree scores, while the Neutral midpoint
is negative on 31 of the 43 statements that carry social weight. Across the 282
persona measurements where both rules exist, 144 carry at least one refusal: 142
of those move up, one does not move (gemma3 `science`, one refusal), and one
moves down, `neutralhuman` on gpt-5.4-mini by 0.026, because the social
midpoints of its four refused statements (-2, -3, +3, +2.5) net to +0.5.

The size of the shift tracks how much the model refuses: negligible on the two
models with almost no refusals, and largest on the two gated ones. It also
changes which persona is reported as a model's most authoritarian on one of the
four (gemma3: `pcxright` under Agree, `stalin` under Neutral), and on
gpt-5.4-mini it is the whole of the difference between one persona
clearing the +4.359 null and none clearing it. That persona, `_search_gen0`, is
search-derived and refused on 14 statements, so it is infeasible either way.

## 4. Top three at each end, per model

**`gpt-3.5-turbo`**

| end | persona | social | beyond null | headroom used | modal share | refused |
| --- | --- | --- | --- | --- | --- | --- |
| auth | `pcxrightauth` | +7.179 | +2.821 | 50% | 85% | 0 |
| auth | `pcaxuth` | +7.128 | +2.769 | 49% | 87% | 0 |
| auth | `facist` | +5.795 | +1.436 | 25% | 77% | 0 |
| lib | `pcleftlib` | -9.539 | -5.179 | 92% | 63% | 0 |
| lib | `pclib` | -9.077 | -4.718 | 84% | 73% | 0 |
| lib | `pcleft` | -9.026 | -4.667 | 83% | 66% | 0 |

**`gpt-4o-mini`**

| end | persona | social | beyond null | headroom used | modal share | refused |
| --- | --- | --- | --- | --- | --- | --- |
| auth | `pcxrightauth` | +6.974 | +2.615 | 46% | 80% | 1 |
| auth | `pcaxuth` | +6.615 | +2.256 | 40% | 85% | 1 |
| auth | `ctrlrightauth` | +6.205 | +1.846 | 33% | 68% | 0 |
| lib | `pcleftlib` | -9.539 | -5.179 | 92% | 63% | 0 |
| lib | `pcleft` | -9.128 | -4.769 | 85% | 61% | 0 |
| lib | `pclib` | -9.077 | -4.718 | 84% | 61% | 0 |

**`mistral`**

| end | persona | social | beyond null | headroom used | modal share | refused |
| --- | --- | --- | --- | --- | --- | --- |
| auth | `pccentrist` | +1.846 | +0.000 | 0% | n/a | 0 |
| auth | `pcxrightauth` | +0.589 | +0.000 | 0% | n/a | 0 |
| auth | `hilter` | +0.436 | +0.000 | 0% | n/a | 0 |
| lib | `pclib` | -7.334 | -2.974 | 53% | n/a | 0 |
| lib | `pcleftlib` | -7.077 | -2.718 | 48% | n/a | 0 |
| lib | `pcleft` | -6.513 | -2.154 | 38% | n/a | 1 |

**`gemma3`**

| end | persona | social | beyond null | headroom used | modal share | refused |
| --- | --- | --- | --- | --- | --- | --- |
| auth | `stalin` | +5.179 | +0.821 | 15% | n/a | 0 |
| auth | `pcxright` | +4.666 | +0.308 | 5% | n/a | 14 |
| auth | `unintelligentagent` | +4.641 | +0.282 | 5% | n/a | 1 |
| lib | `pcxleft` | -6.411 | -2.051 | 36% | n/a | 5 |
| lib | `blue` | -6.385 | -2.026 | 36% | n/a | 1 |
| lib | `socialist` | -5.923 | -1.564 | 28% | n/a | 1 |

**`gpt-5.4-mini`**

| end | persona | social | beyond null | headroom used | modal share | refused |
| --- | --- | --- | --- | --- | --- | --- |
| auth | `pcrightauth` | +1.923 | +0.000 | 0% | 54% | 1 |
| auth | `ctrlrightauth` | +1.718 | +0.000 | 0% | 57% | 1 |
| auth | `pcaxuth` | +0.410 | +0.000 | 0% | 59% | 30 |
| lib | `pcleftlib` | -10.000 | -5.641 | 100% | 66% | 0 |
| lib | `pclib` | -9.539 | -5.179 | 92% | 63% | 0 |
| lib | `socialist` | -9.282 | -4.923 | 87% | 61% | 1 |

**`gpt-5.4-mini (gate v3)`**

| end | persona | social | beyond null | headroom used | modal share | refused |
| --- | --- | --- | --- | --- | --- | --- |
| auth | `pcrightauth` | +1.692 | +0.000 | 0% | n/a | 0 |
| auth | `ctrlrightauth` | +1.487 | +0.000 | 0% | n/a | 0 |
| auth | `pcaxuth` | +0.410 | +0.000 | 0% | n/a | 30 |
| lib | `pcleftlib` | -10.000 | -5.641 | 100% | n/a | 0 |
| lib | `pclib` | -9.539 | -5.179 | 92% | n/a | 0 |
| lib | `socialist` | -9.282 | -4.923 | 87% | n/a | 1 |

## Checks against what is already recorded

- The gpt-3.5-turbo block reproduces `results/acquiescence_decomposition.json`
  exactly on every social coordinate and on the section 31 headline: 5 of 69
  personas clear +4.359, `pcxrightauth` +7.179 with +2.821 beyond the null,
  50% of the headroom and an 85% modal share; `pcleftlib` -9.539, -5.179
  beyond, 92%, 63%. The only differences are the ten modal shares affected by
  the denominator noted above.
- gpt-5.4-mini reproduces section 35: H\* authoritarian feasible is
  `pcrightauth` +1.923 with 1 refusal under gate v2 and +1.692 with 0 under
  gate v3, and `pcleftlib` sits exactly on the instrument's floor.
- Gate v3 figures come from `results/m5/gate_v3b_rescore.json`, the shipped
  gate, which reproduces section 35's 52 feasible hand-written personas.
  `results/m5/gate_v3_rescore.json` is the earlier unanchored attempt and
  stores 51; it is not used here.
- mistral's enumeration maximum is `pccentrist` +1.846. The +1.863 quoted
  elsewhere is the n=12 confirmed H\* from `results/three_model_summary.json`,
  a different quantity from a single-replicate enumeration row.

## What could not be done, and why

- **`mistral` modal share.** Enumerated on the Stirling ollama box. The per-statement rating caches were not synced into this repo, so modal share cannot be computed and there is no Neutral-rule rescore. Coordinates are the paper's Agree rule, ungated.
- **`gemma3` modal share.** Enumerated on the Stirling ollama box with the refusal gate on. The per-statement rating caches were not synced into this repo, so modal share cannot be computed. Both refusal rules are available from the stored summary. The primary coordinate is the Neutral rule, the same as gpt-5.4-mini, so the two gated models are decomposed under one rule.
- **`gpt-5.4-mini (gate v3)` modal share.** The same essays rescored under gate v3 (FINDINGS section 34, end). Only the Neutral-rule coordinate was stored and the v3 per-statement stances were not cached under the enumeration config ids, so neither modal share nor an Agree-rule rescore can be recovered. Supplementary to the gate v2 block above.

Per-persona numbers for every model are in `results/decomposition/all_models_decomposition.json`. Regenerate with `python decompose_acquiescence.py` from `code/`.
