#!/usr/bin/env bash
# Experiment 3 of FRAMING.md: strong-versus-strong assessor (gpt-4o-mini vs gpt-4o).
# Cell list and costs: results/strong_vs_strong/svs_cells_verified.json
#
# Run from /Users/aviralgarg/stirling/PRISM/code, after:  set -a; . ../.env; set +a
# Every command RESCORES CACHED ESSAYS. Nothing is regenerated.
# Estimated spend for the whole file: $6.44 (gpt-4o input dominates). DO NOT run it in one
# go under a $2 cap - run ARM A ($1.22) and each ARM B block separately, or lift the cap.
set -uo pipefail
PY=/Users/aviralgarg/stirling/PRISM/.venv/bin/python
OUT=../results/strong_vs_strong
mkdir -p "$OUT/raw"

# --- guard: the three code fixes must land first (see svs_cells_verified.json) ---
$PY score_cid.py --help | grep -q -- --gate-assessor || { echo "score_cid.py needs --gate-assessor (the gate must stay on gpt-4o-mini while the classifier moves to gpt-4o)"; exit 1; }
$PY score_cid.py --help | grep -q -- --run-tag       || { echo "score_cid.py needs --run-tag (Arm A takes three draws per assessor)"; exit 1; }

# ============================== ARM A: unroled baselines ==============================
# Three independent assessor draws per assessor per baseline, so the assessor-identity term
# is separated from assessor nondeterminism (sd 0.252, FINDINGS section 36).
# gpt-5.4-mini has NO unroled essays; its cell does not exist yet (see prereqs).
armA () {  # $1 cid  $2 assessor  $3 model-label
  for d in 1 2 3; do
    $PY score_cid.py --cid "$1" --assessor "$2" --run-tag "svsA_d$d" --json \
      | tee "$OUT/raw/armA_$3_$1_$2_d$d.json"
  done
}
armA 2b78d1d74d gpt-4o      gpt-3.5-turbo   # 25468 input tok/draw
armA 0a2357aecd gpt-4o      gpt-4o-mini   # 42523 input tok/draw
armA 758484e745 gpt-4o      mistral   # 34848 input tok/draw
armA eca4db9787 gpt-4o      gemma3   # 46501 input tok/draw

armA 2b78d1d74d gpt-4o-mini gpt-3.5-turbo   # 25468 input tok/draw
armA 0a2357aecd gpt-4o-mini gpt-4o-mini   # 42523 input tok/draw
armA 758484e745 gpt-4o-mini mistral   # 34848 input tok/draw
armA eca4db9787 gpt-4o-mini gemma3   # 46501 input tok/draw

# ======================= ARM B: boundary candidates (H* and search winner) ============
# One gpt-4o draw per replicate essay set, paired against the gpt-4o-mini score already
# stored from the original confirmation (free, one draw, declared as such).

# --- gpt-3.5-turbo  H*  persona=H_pcxrightauth  gate=False  refused_as=agree  283015 input tok  0 gate calls ---
$PY score_cid.py --cid e3b9969979 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r1_e3b9969979_gpt-4o.json"   # 23539 tok
$PY score_cid.py --cid 72b7f29be1 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r2_72b7f29be1_gpt-4o.json"   # 23472 tok
$PY score_cid.py --cid 4f92a0a713 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r3_4f92a0a713_gpt-4o.json"   # 23846 tok
$PY score_cid.py --cid de32bbc087 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r4_de32bbc087_gpt-4o.json"   # 23558 tok
$PY score_cid.py --cid 310a7081b7 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r5_310a7081b7_gpt-4o.json"   # 23453 tok
$PY score_cid.py --cid 41077f40f4 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r6_41077f40f4_gpt-4o.json"   # 23851 tok
$PY score_cid.py --cid f89aca1864 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r7_f89aca1864_gpt-4o.json"   # 23439 tok
$PY score_cid.py --cid f06e4a88cd --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r8_f06e4a88cd_gpt-4o.json"   # 23990 tok
$PY score_cid.py --cid a87f632db4 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r9_a87f632db4_gpt-4o.json"   # 23568 tok
$PY score_cid.py --cid 257893bc61 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r10_257893bc61_gpt-4o.json"   # 23366 tok
$PY score_cid.py --cid ec0ff39fb9 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r11_ec0ff39fb9_gpt-4o.json"   # 23260 tok
$PY score_cid.py --cid 0dc5a70dbf --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r12_0dc5a70dbf_gpt-4o.json"   # 23673 tok

# --- gpt-3.5-turbo  search  persona=search2_best  gate=False  refused_as=agree  294001 input tok  0 gate calls ---
$PY score_cid.py --cid 196b62107c --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r1_196b62107c_gpt-4o.json"   # 24273 tok
$PY score_cid.py --cid 575c31d510 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r2_575c31d510_gpt-4o.json"   # 24283 tok
$PY score_cid.py --cid 5ddf0ae144 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r3_5ddf0ae144_gpt-4o.json"   # 24507 tok
$PY score_cid.py --cid 723a666bea --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r4_723a666bea_gpt-4o.json"   # 24856 tok
$PY score_cid.py --cid 9dfb329edc --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r5_9dfb329edc_gpt-4o.json"   # 24482 tok
$PY score_cid.py --cid 4bdc9d8204 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r6_4bdc9d8204_gpt-4o.json"   # 24442 tok
$PY score_cid.py --cid 45efae88e7 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r7_45efae88e7_gpt-4o.json"   # 24735 tok
$PY score_cid.py --cid 187e5b8676 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r8_187e5b8676_gpt-4o.json"   # 24502 tok
$PY score_cid.py --cid 4efa950421 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r9_4efa950421_gpt-4o.json"   # 24623 tok
$PY score_cid.py --cid 6fe7ac04ad --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r10_6fe7ac04ad_gpt-4o.json"   # 24575 tok
$PY score_cid.py --cid d8c99fc2c0 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r11_d8c99fc2c0_gpt-4o.json"   # 24223 tok
$PY score_cid.py --cid 4169e064c2 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r12_4169e064c2_gpt-4o.json"   # 24500 tok

# --- gpt-4o-mini  H*  persona=pcxrightauth  gate=False  refused_as=agree  457473 input tok  0 gate calls ---
$PY score_cid.py --cid a565da6c63 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r13_a565da6c63_gpt-4o.json"   # 37600 tok
$PY score_cid.py --cid 43d9efc5de --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r14_43d9efc5de_gpt-4o.json"   # 37967 tok
$PY score_cid.py --cid 88e0bc7ac4 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r15_88e0bc7ac4_gpt-4o.json"   # 38598 tok
$PY score_cid.py --cid 4a2a5c9cce --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r16_4a2a5c9cce_gpt-4o.json"   # 38216 tok
$PY score_cid.py --cid 15b8d664b2 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r17_15b8d664b2_gpt-4o.json"   # 38236 tok
$PY score_cid.py --cid f505019cdb --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r18_f505019cdb_gpt-4o.json"   # 37852 tok
$PY score_cid.py --cid c47d4ae6b0 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r19_c47d4ae6b0_gpt-4o.json"   # 38297 tok
$PY score_cid.py --cid b6e1fcddec --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r20_b6e1fcddec_gpt-4o.json"   # 38479 tok
$PY score_cid.py --cid 5e94f53bb3 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r21_5e94f53bb3_gpt-4o.json"   # 38294 tok
$PY score_cid.py --cid 33bf678e87 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r22_33bf678e87_gpt-4o.json"   # 37999 tok
$PY score_cid.py --cid d04d51dc1b --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r23_d04d51dc1b_gpt-4o.json"   # 38024 tok
$PY score_cid.py --cid 37f91d3a86 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r24_37f91d3a86_gpt-4o.json"   # 37911 tok

# --- gpt-4o-mini  search  persona=search_best  gate=False  refused_as=agree  461789 input tok  0 gate calls ---
$PY score_cid.py --cid b7ae94f5ad --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r13_b7ae94f5ad_gpt-4o.json"   # 38271 tok
$PY score_cid.py --cid 56d19932d9 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r14_56d19932d9_gpt-4o.json"   # 38352 tok
$PY score_cid.py --cid 916b249f3a --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r15_916b249f3a_gpt-4o.json"   # 38564 tok
$PY score_cid.py --cid 327e1ece5d --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r16_327e1ece5d_gpt-4o.json"   # 38820 tok
$PY score_cid.py --cid e157e4cc50 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r17_e157e4cc50_gpt-4o.json"   # 38665 tok
$PY score_cid.py --cid c278ccfd32 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r18_c278ccfd32_gpt-4o.json"   # 38615 tok
$PY score_cid.py --cid 248a4a615e --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r19_248a4a615e_gpt-4o.json"   # 38283 tok
$PY score_cid.py --cid f4863c1ce9 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r20_f4863c1ce9_gpt-4o.json"   # 38206 tok
$PY score_cid.py --cid dbcf8efab1 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r21_dbcf8efab1_gpt-4o.json"   # 38615 tok
$PY score_cid.py --cid d0e0b014c6 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r22_d0e0b014c6_gpt-4o.json"   # 38053 tok
$PY score_cid.py --cid 6e85b0bec0 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r23_6e85b0bec0_gpt-4o.json"   # 38691 tok
$PY score_cid.py --cid 9c475ffbf8 --assessor gpt-4o --json \
    | tee "$OUT/raw/armB_gpt-4o-mini_search_r24_9c475ffbf8_gpt-4o.json"   # 38654 tok

# --- gpt-5.4-mini  H*  persona=H_pcrightauth  gate=True  refused_as=neutral  237084 input tok  6 gate calls ---
ROLE="$(cat "$OUT/personas/gpt-5.4-mini_H_pcrightauth.txt")"
$PY score_cid.py --cid c4e7c6af6a --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r1_c4e7c6af6a_gpt-4o.json"   # 19563 tok, 0 gate calls
$PY score_cid.py --cid f18e036869 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r2_f18e036869_gpt-4o.json"   # 19939 tok, 0 gate calls
$PY score_cid.py --cid 8f8724d40f --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r3_8f8724d40f_gpt-4o.json"   # 19735 tok, 2 gate calls
$PY score_cid.py --cid 8e1fd6ff5f --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r4_8e1fd6ff5f_gpt-4o.json"   # 19561 tok, 1 gate calls
$PY score_cid.py --cid 948a63b6e3 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r5_948a63b6e3_gpt-4o.json"   # 19688 tok, 0 gate calls
$PY score_cid.py --cid 928ffa2166 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r6_928ffa2166_gpt-4o.json"   # 19630 tok, 0 gate calls
$PY score_cid.py --cid e579475bf2 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r7_e579475bf2_gpt-4o.json"   # 19793 tok, 0 gate calls
$PY score_cid.py --cid 7d8a1e69b4 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r8_7d8a1e69b4_gpt-4o.json"   # 19870 tok, 0 gate calls
$PY score_cid.py --cid c9f75355d1 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r9_c9f75355d1_gpt-4o.json"   # 19669 tok, 0 gate calls
$PY score_cid.py --cid b649da92ac --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r10_b649da92ac_gpt-4o.json"   # 19705 tok, 1 gate calls
$PY score_cid.py --cid 1cfab38f11 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r11_1cfab38f11_gpt-4o.json"   # 19899 tok, 1 gate calls
$PY score_cid.py --cid ded2393fcc --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r12_ded2393fcc_gpt-4o.json"   # 20032 tok, 1 gate calls

# --- gpt-5.4-mini  search  persona=search_best  gate=True  refused_as=neutral  281833 input tok  71 gate calls ---
ROLE="$(cat "$OUT/personas/gpt-5.4-mini_search_best.txt")"
$PY score_cid.py --cid 7a655b49b4 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r1_7a655b49b4_gpt-4o.json"   # 23350 tok, 6 gate calls
$PY score_cid.py --cid 4a92b81798 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r2_4a92b81798_gpt-4o.json"   # 23386 tok, 5 gate calls
$PY score_cid.py --cid 3eca387592 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r3_3eca387592_gpt-4o.json"   # 23218 tok, 7 gate calls
$PY score_cid.py --cid 62e49c8571 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r4_62e49c8571_gpt-4o.json"   # 23611 tok, 5 gate calls
$PY score_cid.py --cid 1db8ecfece --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r5_1db8ecfece_gpt-4o.json"   # 23672 tok, 7 gate calls
$PY score_cid.py --cid c7a32b6137 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r6_c7a32b6137_gpt-4o.json"   # 23897 tok, 6 gate calls
$PY score_cid.py --cid 680869655b --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r7_680869655b_gpt-4o.json"   # 23364 tok, 4 gate calls
$PY score_cid.py --cid 47e74b4ae7 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r8_47e74b4ae7_gpt-4o.json"   # 23842 tok, 6 gate calls
$PY score_cid.py --cid 61aad4b11d --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r9_61aad4b11d_gpt-4o.json"   # 23393 tok, 8 gate calls
$PY score_cid.py --cid 4e1c234b1b --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r10_4e1c234b1b_gpt-4o.json"   # 22583 tok, 7 gate calls
$PY score_cid.py --cid 287a0f458c --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r11_287a0f458c_gpt-4o.json"   # 24092 tok, 3 gate calls
$PY score_cid.py --cid de6cc82256 --assessor gpt-4o --gate-assessor gpt-4o-mini \
    --refusal-gate --refused-as neutral --role-text "$ROLE" --json \
    | tee "$OUT/raw/armB_gpt-5.4-mini_search_r12_de6cc82256_gpt-4o.json"   # 23425 tok, 7 gate calls

# --- the gpt-4o-mini side of every Arm B cell, re-read from cache at zero cost ---
$PY score_cid.py --cid e3b9969979 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r1_e3b9969979_gpt-4o-mini.json"
$PY score_cid.py --cid 72b7f29be1 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r2_72b7f29be1_gpt-4o-mini.json"
$PY score_cid.py --cid 4f92a0a713 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r3_4f92a0a713_gpt-4o-mini.json"
$PY score_cid.py --cid de32bbc087 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r4_de32bbc087_gpt-4o-mini.json"
$PY score_cid.py --cid 310a7081b7 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r5_310a7081b7_gpt-4o-mini.json"
$PY score_cid.py --cid 41077f40f4 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r6_41077f40f4_gpt-4o-mini.json"
$PY score_cid.py --cid f89aca1864 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r7_f89aca1864_gpt-4o-mini.json"
$PY score_cid.py --cid f06e4a88cd --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r8_f06e4a88cd_gpt-4o-mini.json"
$PY score_cid.py --cid a87f632db4 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r9_a87f632db4_gpt-4o-mini.json"
$PY score_cid.py --cid 257893bc61 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r10_257893bc61_gpt-4o-mini.json"
$PY score_cid.py --cid ec0ff39fb9 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r11_ec0ff39fb9_gpt-4o-mini.json"
$PY score_cid.py --cid 0dc5a70dbf --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_Hstar_r12_0dc5a70dbf_gpt-4o-mini.json"
$PY score_cid.py --cid 196b62107c --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r1_196b62107c_gpt-4o-mini.json"
$PY score_cid.py --cid 575c31d510 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r2_575c31d510_gpt-4o-mini.json"
$PY score_cid.py --cid 5ddf0ae144 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r3_5ddf0ae144_gpt-4o-mini.json"
$PY score_cid.py --cid 723a666bea --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r4_723a666bea_gpt-4o-mini.json"
$PY score_cid.py --cid 9dfb329edc --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r5_9dfb329edc_gpt-4o-mini.json"
$PY score_cid.py --cid 4bdc9d8204 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r6_4bdc9d8204_gpt-4o-mini.json"
$PY score_cid.py --cid 45efae88e7 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r7_45efae88e7_gpt-4o-mini.json"
$PY score_cid.py --cid 187e5b8676 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r8_187e5b8676_gpt-4o-mini.json"
$PY score_cid.py --cid 4efa950421 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r9_4efa950421_gpt-4o-mini.json"
$PY score_cid.py --cid 6fe7ac04ad --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r10_6fe7ac04ad_gpt-4o-mini.json"
$PY score_cid.py --cid d8c99fc2c0 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r11_d8c99fc2c0_gpt-4o-mini.json"
$PY score_cid.py --cid 4169e064c2 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-3.5-turbo_search_r12_4169e064c2_gpt-4o-mini.json"
$PY score_cid.py --cid a565da6c63 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r13_a565da6c63_gpt-4o-mini.json"
$PY score_cid.py --cid 43d9efc5de --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r14_43d9efc5de_gpt-4o-mini.json"
$PY score_cid.py --cid 88e0bc7ac4 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r15_88e0bc7ac4_gpt-4o-mini.json"
$PY score_cid.py --cid 4a2a5c9cce --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r16_4a2a5c9cce_gpt-4o-mini.json"
$PY score_cid.py --cid 15b8d664b2 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r17_15b8d664b2_gpt-4o-mini.json"
$PY score_cid.py --cid f505019cdb --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r18_f505019cdb_gpt-4o-mini.json"
$PY score_cid.py --cid c47d4ae6b0 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r19_c47d4ae6b0_gpt-4o-mini.json"
$PY score_cid.py --cid b6e1fcddec --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r20_b6e1fcddec_gpt-4o-mini.json"
$PY score_cid.py --cid 5e94f53bb3 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r21_5e94f53bb3_gpt-4o-mini.json"
$PY score_cid.py --cid 33bf678e87 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r22_33bf678e87_gpt-4o-mini.json"
$PY score_cid.py --cid d04d51dc1b --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r23_d04d51dc1b_gpt-4o-mini.json"
$PY score_cid.py --cid 37f91d3a86 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_Hstar_r24_37f91d3a86_gpt-4o-mini.json"
$PY score_cid.py --cid b7ae94f5ad --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r13_b7ae94f5ad_gpt-4o-mini.json"
$PY score_cid.py --cid 56d19932d9 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r14_56d19932d9_gpt-4o-mini.json"
$PY score_cid.py --cid 916b249f3a --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r15_916b249f3a_gpt-4o-mini.json"
$PY score_cid.py --cid 327e1ece5d --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r16_327e1ece5d_gpt-4o-mini.json"
$PY score_cid.py --cid e157e4cc50 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r17_e157e4cc50_gpt-4o-mini.json"
$PY score_cid.py --cid c278ccfd32 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r18_c278ccfd32_gpt-4o-mini.json"
$PY score_cid.py --cid 248a4a615e --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r19_248a4a615e_gpt-4o-mini.json"
$PY score_cid.py --cid f4863c1ce9 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r20_f4863c1ce9_gpt-4o-mini.json"
$PY score_cid.py --cid dbcf8efab1 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r21_dbcf8efab1_gpt-4o-mini.json"
$PY score_cid.py --cid d0e0b014c6 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r22_d0e0b014c6_gpt-4o-mini.json"
$PY score_cid.py --cid 6e85b0bec0 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r23_6e85b0bec0_gpt-4o-mini.json"
$PY score_cid.py --cid 9c475ffbf8 --assessor gpt-4o-mini --json | tee "$OUT/raw/armB_gpt-4o-mini_search_r24_9c475ffbf8_gpt-4o-mini.json"
$PY score_cid.py --cid c4e7c6af6a --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r1_c4e7c6af6a_gpt-4o-mini.json"
$PY score_cid.py --cid f18e036869 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r2_f18e036869_gpt-4o-mini.json"
$PY score_cid.py --cid 8f8724d40f --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r3_8f8724d40f_gpt-4o-mini.json"
$PY score_cid.py --cid 8e1fd6ff5f --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r4_8e1fd6ff5f_gpt-4o-mini.json"
$PY score_cid.py --cid 948a63b6e3 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r5_948a63b6e3_gpt-4o-mini.json"
$PY score_cid.py --cid 928ffa2166 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r6_928ffa2166_gpt-4o-mini.json"
$PY score_cid.py --cid e579475bf2 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r7_e579475bf2_gpt-4o-mini.json"
$PY score_cid.py --cid 7d8a1e69b4 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r8_7d8a1e69b4_gpt-4o-mini.json"
$PY score_cid.py --cid c9f75355d1 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r9_c9f75355d1_gpt-4o-mini.json"
$PY score_cid.py --cid b649da92ac --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r10_b649da92ac_gpt-4o-mini.json"
$PY score_cid.py --cid 1cfab38f11 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r11_1cfab38f11_gpt-4o-mini.json"
$PY score_cid.py --cid ded2393fcc --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_Hstar_r12_ded2393fcc_gpt-4o-mini.json"
$PY score_cid.py --cid 7a655b49b4 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r1_7a655b49b4_gpt-4o-mini.json"
$PY score_cid.py --cid 4a92b81798 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r2_4a92b81798_gpt-4o-mini.json"
$PY score_cid.py --cid 3eca387592 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r3_3eca387592_gpt-4o-mini.json"
$PY score_cid.py --cid 62e49c8571 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r4_62e49c8571_gpt-4o-mini.json"
$PY score_cid.py --cid 1db8ecfece --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r5_1db8ecfece_gpt-4o-mini.json"
$PY score_cid.py --cid c7a32b6137 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r6_c7a32b6137_gpt-4o-mini.json"
$PY score_cid.py --cid 680869655b --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r7_680869655b_gpt-4o-mini.json"
$PY score_cid.py --cid 47e74b4ae7 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r8_47e74b4ae7_gpt-4o-mini.json"
$PY score_cid.py --cid 61aad4b11d --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r9_61aad4b11d_gpt-4o-mini.json"
$PY score_cid.py --cid 4e1c234b1b --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r10_4e1c234b1b_gpt-4o-mini.json"
$PY score_cid.py --cid 287a0f458c --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r11_287a0f458c_gpt-4o-mini.json"
$PY score_cid.py --cid de6cc82256 --assessor gpt-4o-mini --refusal-gate --refused-as neutral --json | tee "$OUT/raw/armB_gpt-5.4-mini_search_r12_de6cc82256_gpt-4o-mini.json"

# --- per-statement agreement, kappa and the directional split, once --tag exists ---
# $PY compare_assessors.py --cid <cid> --a gpt-4o-mini --b gpt-4o [--tag _gate3]
