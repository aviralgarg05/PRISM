#!/usr/bin/env bash
# Arm C of the sixth pre-registration: mistral and gemma3 boundary candidates.
# Essays were copied from the workstation (never regenerated); every call rescores cached text.
# Held fixed as in the original confirmations: ungated, refusals scored as Agree.
set -uo pipefail
cd /Users/aviralgarg/stirling/PRISM/code
PY=../.venv/bin/python
OUT=../results/strong_vs_strong
mkdir -p "$OUT/raw"
$PY - <<'PYLIST' | while read -r model persona rep cid; do
import json
cells = json.load(open("../results/strong_vs_strong/armC_cells.json"))
for key, rows in sorted(cells.items()):
    model, persona = key.split("|")
    for rep, cid in rows:
        print(model, persona, rep, cid)
PYLIST
  for assessor in gpt-4o gpt-4o-mini; do
    $PY score_cid.py --cid "$cid" --assessor "$assessor" --json \
      > "$OUT/raw/armC_${model}_${persona}_r${rep}_${cid}_${assessor}.json" 2>> "$OUT/armC_errors.log"
  done
done
echo ARMC_DONE
