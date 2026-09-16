#!/usr/bin/env bash
# Seventh pre-registration, gpt-5.4-mini: waits for Stage A1, then runs Stage A2 and the drift probe.
set -uo pipefail
cd /Users/aviralgarg/stirling/PRISM/code
PY=../.venv/bin/python
OUT=../results/answer_format_ablation
until grep -q AFMT_A1_DONE "$OUT/afmt_m5_a1.log" 2>/dev/null; do sleep 60; done
echo "A1 finished, starting A2 $(date -u +%FT%TZ)"
$PY confirm_persona.py --personas "$OUT/personas_m5_gpt54mini_paired.json" \
  --reps 6 --rep-offset 6 --block-seed 402 --provider openai --model gpt-5.4-mini \
  --assessor gpt-4o-mini --assessor-provider openai --refusal-gate --refused-as neutral \
  --sleep-between 5 --out "$OUT/afmt_m5_paired.json" > "$OUT/afmt_m5_a2.log" 2>&1
echo "A2 exit $? $(date -u +%FT%TZ)"
$PY confirm_persona.py --personas "$OUT/personas_m5_gpt54mini_intact.json" \
  --reps 3 --rep-offset 12 --block-seed 403 --provider openai --model gpt-5.4-mini \
  --assessor gpt-4o-mini --assessor-provider openai --refusal-gate --refused-as neutral \
  --sleep-between 5 --out "$OUT/afmt_m5_drift.json" > "$OUT/afmt_m5_drift.log" 2>&1
echo "drift exit $? $(date -u +%FT%TZ)"
echo M5_A2_DRIFT_DONE
