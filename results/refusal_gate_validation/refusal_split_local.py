import glob, json, re, os, collections
REFU = re.compile(r"\b(cannot|can't|can not|won't|will not|unable to|am not able to|must decline to|refuse to)\b[^.]{0,40}\b(fulfil|fulfill|comply|write|create|produce|generate|provide|argue|adopt|take on|role-?play|pretend)", re.I)
DISC = re.compile(r"\b(do not|don't|does not|doesn't)\s+(have|hold|possess)\s+(personal|my own|any personal)", re.I)
out = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
ex = {}
for p in glob.glob("out/essays/pc*_openai_*.txt"):
    m = re.match(r"pc(\d+)_openai_(.+?)_(.+)_([0-9a-f]{10})\.txt$", os.path.basename(p))
    if not m: continue
    q, model, role, cid = m.groups()
    cache = f"out/ratings/cache_{cid}_gpt-4o-mini.json"
    if not os.path.exists(cache): continue
    try: lab = json.load(open(cache)).get(q, {}).get("stance")
    except Exception: continue
    if lab is None: continue
    txt = open(p, errors="ignore").read()
    head = txt[:400]
    if REFU.search(head):
        cat = "refuse_then_essay" if len(txt) >= 900 else "pure_refusal"
    elif DISC.search(head):
        cat = "disclaimer_then_essay"
    else:
        continue
    out[model][cat][lab] += 1
    ex.setdefault((model, cat), head[:150].replace("\n", " "))
for model in sorted(out):
    print(model)
    for cat in ("pure_refusal", "refuse_then_essay", "disclaimer_then_essay"):
        c = out[model][cat]
        if not c: continue
        strong = c["Strongly agree"] + c["Strongly disagree"]
        print(f"  {cat:<22} n={sum(c.values()):>4}  scored as strong stance {strong:>4}  Refused {c['Refused']:>4}  {dict(c)}")
        print(f"     e.g. {ex[(model,cat)]!r}")
