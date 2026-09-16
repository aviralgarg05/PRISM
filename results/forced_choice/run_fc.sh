#!/usr/bin/env bash
# Eighth pre-registration: forced choice, three hosted models, five personas, n=12.
# Replicates 1-6 ascending option order, 7-12 descending. One process per model x order.
set -uo pipefail
cd /Users/aviralgarg/stirling/PRISM/code
PY=../.venv/bin/python
OUT=../results/forced_choice
pids=()
for M in gpt-3.5-turbo gpt-4o-mini gpt-5.4-mini; do
  $PY confirm_persona.py --personas "$OUT/personas_$M.json" --reps 6 --rep-offset 0 --block-seed 501 \
      --provider openai --model "$M" --forced-choice --fc-order ascending \
      --sleep-between 1 --out "$OUT/fc_${M}_asc.json" > "$OUT/fc_${M}_asc.log" 2>&1 &
  pids+=($!)
  $PY confirm_persona.py --personas "$OUT/personas_$M.json" --reps 6 --rep-offset 6 --block-seed 502 \
      --provider openai --model "$M" --forced-choice --fc-order descending \
      --sleep-between 1 --out "$OUT/fc_${M}_desc.json" > "$OUT/fc_${M}_desc.log" 2>&1 &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; echo "process $p exit $?"; done
echo FC_DONE
