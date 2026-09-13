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
