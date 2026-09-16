#!/usr/bin/env bash
# Amendment A2 of the sixth pre-registration: generate the gpt-5.4-mini unroled baseline,
# then three draws per assessor, all reusing the generation-time gate verdicts.
set -uo pipefail
cd /Users/aviralgarg/stirling/PRISM/code
PY=../.venv/bin/python
OUT=../results/strong_vs_strong
$PY political_questions.py --provider openai --model gpt-5.4-mini \
    --assessor gpt-4o-mini --assessor-provider openai \
    --refusal-gate --refused-as neutral --no-refusal-retry --json > "$OUT/gpt54mini_baseline_generation.json" 2> "$OUT/gpt54mini_baseline_generation.err"
CID=$($PY -c "import json; print(json.load(open('$OUT/gpt54mini_baseline_generation.json'))['config_id'])")
echo "baseline cid $CID"
for a in gpt-4o gpt-4o-mini; do
  for d in 1 2 3; do
    $PY score_cid.py --cid "$CID" --assessor "$a" --gate-assessor gpt-4o-mini \
        --refusal-gate --refused-as neutral --run-tag "svsA_d$d" --json \
        > "$OUT/raw/armA_gpt-5.4-mini_${CID}_${a}_d${d}.json" 2>> "$OUT/armA_gpt54mini.err"
  done
done
echo ARMA_GPT54MINI_DONE
