#!/usr/bin/env bash
# Twelfth pre-registration on the workstation: the local flip arms at temperature 0.8,
# n=24, two ollama clients at a time. Writes box_flip_sampled.log.
set -u
cd ~/prism/code
PY=../.venv/bin/python
set -a; . ../.env; set +a
LOG=../results/stance_flip/box_flip_sampled.log
: > "$LOG"
if ! $PY verify_model_versions.py --ollama http://localhost:11434 >> "$LOG" 2>&1; then
  echo "=== VERSIONS MOVED, not starting" >> "$LOG"; exit 1
fi
P=../results/stance_flip/personas_flip.json
run() {
  m=$1
  $PY confirm_persona.py --personas $P --reps 24 --question-ids 4,27 --refusal-gate --refused-as neutral \
    --temperature 0.8 --provider ollama --model "$m" --base-url http://localhost:11434 --num-predict 1200 \
    --out ../results/stance_flip/flip_sampled_${m}.json > ../results/stance_flip/flip_sampled_${m}.log 2>&1
  echo "=== $m done $(date -Iseconds) exit $?" >> "$LOG"
}
echo "=== start $(date -Iseconds)" >> "$LOG"
run gemma3 & run mistral & wait
run llama3.2
echo "BOX_FLIP_SAMPLED_DONE" >> "$LOG"
