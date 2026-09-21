#!/usr/bin/env bash
# Eleventh pre-registration, local transfer arms. Waits for the tenth
# pre-registration's run to finish, then runs gemma3 and mistral together and
# llama3.2 after them (two ollama clients at a time). Writes box_flip.log.
set -u
cd ~/prism/code
PY=../.venv/bin/python
set -a; . ../.env; set +a
LOG=../results/stance_flip/box_flip.log
: > "$LOG"
until grep -q "M6_DONE\|VERSIONS MOVED" ../results/m6/box_m6.log 2>/dev/null; do sleep 300; done
echo "=== m6 finished $(date -Iseconds)" >> "$LOG"
if ! $PY verify_model_versions.py --ollama http://localhost:11434 >> "$LOG" 2>&1; then
  echo "=== VERSIONS MOVED, not starting" >> "$LOG"; exit 1
fi
P=../results/stance_flip/personas_flip.json
run() {
  m=$1
  $PY confirm_persona.py --personas $P --reps 12 --question-ids 4,27 --refusal-gate --refused-as neutral \
    --provider ollama --model "$m" --base-url http://localhost:11434 --num-predict 1200 \
    --out ../results/stance_flip/flip_${m}_paper.json > ../results/stance_flip/flip_${m}_paper.log 2>&1
  echo "=== $m done $(date -Iseconds) exit $?" >> "$LOG"
}
run gemma3 & run mistral & wait
run llama3.2
echo "BOX_FLIP_DONE" >> "$LOG"
