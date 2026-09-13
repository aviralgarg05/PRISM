import glob, json, re, os, collections
REFU = re.compile(r"\b(cannot|can't|can not|won't|will not|unable to|am not able to|must decline to|refuse to)\b[^.]{0,40}\b(fulfil|fulfill|comply|write|create|produce|generate|provide|argue|adopt|take on|role-?play|pretend)", re.I)
DISC = re.compile(r"\b(do not|don't|does not|doesn't)\s+(have|hold|possess)\s+(personal|my own|any personal)", re.I)
def cat_of(txt):
    head = txt[:400]
    if REFU.search(head): return "refuse_then_essay" if len(txt) >= 900 else "pure_refusal"
    if DISC.search(head): return "disclaimer_then_essay"
    return None
out = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
ex = {}
for p in glob.glob("out/essays/pc*_ollama_*.txt"):
    m = re.match(r"pc(\d+)_ollama_(.+?)_(.+)_([0-9a-f]{10})\.txt$", os.path.basename(p))
    if not m: continue
    q, model, role, cid = m.groups()
    cache = "out/ratings/cache_%s_gpt-4o-mini.json" % cid
    if not os.path.exists(cache): continue
    try: lab = json.load(open(cache)).get(q, {}).get("stance")
    except Exception: continue
    if lab is None: continue
    txt = open(p, errors="ignore").read()
    c = cat_of(txt)
    if not c: continue
    out[model][c][lab] += 1
    ex.setdefault((model, c), txt[:150].replace("\n", " "))
for model in sorted(out):
    print(model)
    for c in ("pure_refusal", "refuse_then_essay", "disclaimer_then_essay"):
        k = out[model][c]
        if not k: continue
        strong = k["Strongly agree"] + k["Strongly disagree"]
        print("  %-22s n=%4d  scored as strong stance %4d  Refused %4d  %s" % (c, sum(k.values()), strong, k["Refused"], dict(k)))
        print("     e.g. %r" % ex[(model, c)])

# per-persona contamination in the gemma3 enumeration, for recomputing rank correlations
per = {}
for f in glob.glob("results/m4_gemma_*.json"):
    for r in json.load(open(f))["runs"]:
        cid = r["config_id"]; n_ref = 0; n_strong_ref = 0
        cache = json.load(open("out/ratings/cache_%s_gpt-4o-mini.json" % cid))
        for p in glob.glob("out/essays/pc*_%s.txt" % cid):
            q = re.match(r"pc(\d+)_", os.path.basename(p)).group(1)
            c = cat_of(open(p, errors="ignore").read())
            if c in ("pure_refusal", "refuse_then_essay"):
                n_ref += 1
                if cache.get(q, {}).get("stance") in ("Strongly agree", "Strongly disagree"):
                    n_strong_ref += 1
        per[r["persona"]] = {"social": r["social"], "refusals": n_ref, "refusal_scored_strong": n_strong_ref}
json.dump(per, open("results/m4_gemma_refusal_per_persona.json", "w"), indent=1)
top = sorted(per.items(), key=lambda kv: -kv[1]["refusals"])[:12]
print("\ngemma3 enumeration, personas with most refusals (of 62):")
for k, v in top:
    print("  %-18s refusals %2d  scored-strong %2d  social %+.2f" % (k, v["refusals"], v["refusal_scored_strong"], v["social"]))
print("personas with >=10 refusals: %d of %d" % (sum(1 for v in per.values() if v["refusals"] >= 10), len(per)))
