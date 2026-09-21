#!/usr/bin/env bash
# Eleventh pre-registration, hosted arms. Run from code/.
set -u
PY=../.venv/bin/python
set -a; . ../.env; set +a
$PY verify_model_versions.py || { echo "VERSIONS MOVED, not starting"; exit 1; }
P=../results/stance_flip/personas_flip.json
common="--personas $P --reps 12 --question-ids 4,27 --refusal-gate --refused-as neutral --sleep-between 2"
$PY confirm_persona.py $common --model gpt-3.5-turbo --out ../results/stance_flip/flip_gpt-3.5-turbo_paper.json > ../results/stance_flip/flip_gpt-3.5-turbo_paper.log 2>&1 &
$PY confirm_persona.py $common --model gpt-3.5-turbo --prompt-genes '{"stance": 5}' --out ../results/stance_flip/flip_gpt-3.5-turbo_neutral.json > ../results/stance_flip/flip_gpt-3.5-turbo_neutral.log 2>&1 &
$PY confirm_persona.py $common --model gpt-4o-mini --out ../results/stance_flip/flip_gpt-4o-mini_paper.json > ../results/stance_flip/flip_gpt-4o-mini_paper.log 2>&1 &
$PY confirm_persona.py $common --model gpt-5.4-mini --out ../results/stance_flip/flip_gpt-5.4-mini_paper.json > ../results/stance_flip/flip_gpt-5.4-mini_paper.log 2>&1 &
wait
echo HOSTED_FLIP_DONE
