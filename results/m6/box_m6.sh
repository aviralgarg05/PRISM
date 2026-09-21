#!/usr/bin/env bash
# Tenth pre-registration on the workstation: llama3.2 enumeration, then the gated
# re-score over the same essays. Two clients at a time. Writes results/m6/box_m6.log.
set -u
cd ~/prism/code
PY=../.venv/bin/python
set -a; . ../.env; set +a
LOG=../results/m6/box_m6.log
: > "$LOG"
if ! $PY verify_model_versions.py --ollama http://localhost:11434 >> "$LOG" 2>&1; then
  echo "=== VERSIONS MOVED, not starting" >> "$LOG"; exit 1
fi
stage() {
  tag=$1; shift
  echo "=== $tag start $(date -Iseconds)" >> "$LOG"
  pids=()
  for i in 0 1; do
    $PY confirm_persona.py --personas ../results/m6/personas_llama32_$i.json --reps 1 \
      --provider ollama --model llama3.2 --base-url http://localhost:11434 --num-predict 1200 \
      --assessor gpt-4o-mini "$@" --out ../results/m6/${tag}_$i.json > ../results/m6/${tag}_$i.log 2>&1 &
    pids+=($!)
  done
  codes=""
  for p in "${pids[@]}"; do wait "$p"; codes="$codes $?"; done
  echo "=== $tag done $(date -Iseconds) exits$codes" >> "$LOG"
}
stage m6_llama
stage gated_m6_llama --refusal-gate --refused-as neutral
echo "M6_DONE" >> "$LOG"
