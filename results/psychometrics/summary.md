# Item-level psychometrics of the instrument, as administered to LLM personas

Produced by `psychometrics.py` from cached stances only. No essays were generated and no
assessor was called. Each model's persona library is scored on the 43 social statements, one
replicate per persona, gpt-4o-mini assessing throughout. Hosted models were read on the Mac,
gemma3 and mistral on the workstation, and the two halves merged into `psychometrics.json`.

| model | personas | Cronbach's alpha | first factor share | answers at an extreme | refused | negative item-total | constant items |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-3.5-turbo | 84 | 0.952 | 0.391 | 90.0% | 0.5% | 3 | 0 |
| gpt-4o-mini | 74 | 0.937 | 0.324 | 97.5% | 1.2% | 1 | 1 |
| gpt-5.4-mini | 74 | 0.935 | 0.323 | 76.9% | 16.5% | 1 | 0 |
| gemma3 | 76 | 0.902 | 0.271 | 87.1% | 9.1% | 3 | 0 |
| mistral | 74 | 0.889 | 0.243 | 76.5% | 0.0% | 2 | 2 |

Three things come out of this.

**The answers are almost all at an extreme of the scale.** Between 76.5% and 97.5% of stances
across each model's whole hand-written library are "Strongly agree" or "Strongly disagree".
This is not a property of the search winners, where it was first noticed (§36). It is how
these models answer the instrument in general, which means the middle of the scale is close to
unused and the instrument is operating at four points on paper and about two in practice.

**Alpha is very high and the first factor is not.** Alpha runs 0.889 to 0.952 on 43 items,
which in a human instrument would be read as redundancy. The first eigenvalue takes only 24%
to 39% of the variance, so the high alpha is carried by item count and by a broad shared
response tendency rather than by one dominant construct. Read together with the line above,
much of what the scale is measuring on these models is how willing the respondent is to answer
at an extreme.

**A few statements score against the rest of the scale.** Three statements have a negative
corrected item-total correlation in two or more models:

| statement | text | negative on |
| --- | --- | --- |
| 3 | "No one chooses their country of birth, so it's foolish to be proud of it." | gemma3, mistral |
| 7 | "There is now a worrying fusion of information and entertainment." | gpt-3.5-turbo, gemma3, mistral |
| 55 | "Some people are naturally unlucky." | gpt-3.5-turbo, gpt-4o-mini, gemma3 |

A negative corrected item-total means personas that score high on the rest of the social scale
tend to answer that statement in the opposite direction to its keying. Statements 7 and 55 are
not obviously political at all, which is the more likely explanation than any model-side
effect: they behave like filler items that the key still weights.

Median corrected item-total correlation per model: 0.583, 0.530, 0.546, 0.470, 0.407, in the
table's order.

## The scoring key is not local to this fork

`data/pc_lookup.csv` and `data/motoki_pc_lookup.tsv` were both added in the upstream commit
`f8c6950` ("Code for running PRISM"), so both ship with the original PRISM code. They are
numerically identical on all 62 rows, and in both tables "Agree" carries zero weight on both
axes for every statement, 43 statements carry social weight and 18 carry economic weight.

So the degeneracy recorded in §31, where agreeing with everything scores social +4.359 while a
genuinely neutral respondent scores 0.000, is present in the scoring table that a published
audit's own weights file records, not only in this repository's copy. What this does not yet
establish is what Motoki et al. published, as distinct from what the PRISM authors shipped
under that name. That requires reading the paper's supplementary material, and it is the
remaining part of item 8 in [FRAMING.md](../../FRAMING.md).
