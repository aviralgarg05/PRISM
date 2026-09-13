import sys, glob, json, random, re, os, collections
sys.path.insert(0, "."); sys.path.insert(0, "/tmp")
from utils.utils import get_model, read_questions_from_file
from utils.roles import roles
from gate2 import gate2
qs = read_questions_from_file("../data/compass_questions.txt")
model = get_model("openai", "gpt-4o-mini", 0.0)
cids = {}
for f in glob.glob("../results/m4_gemma_*.json"):
    d = json.load(open(f))
    if not isinstance(d, dict) or "runs" not in d: continue
    for r in d["runs"]: cids[r["persona"]] = r["config_id"]
rng = random.Random(7)
def sample(personas, n):
    pool = []
    for p in personas: pool += [(p, f) for f in glob.glob("../out/essays/pc*_%s.txt" % cids[p])]
    return rng.sample(pool, n)
sets = {"assumed REFUSED (facist/hilter/extremist)": ("REFUSED", sample(["facist", "hilter", "extremist"], 30)),
        "assumed COMPLIED (stalin)": ("COMPLIED", sample(["stalin"], 20))}
for name, (expect, items) in sets.items():
    c = collections.Counter(); odd = []
    for persona, p in items:
        q = re.match(r"pc(\d+)_", os.path.basename(p)).group(1)
        txt = open(p, errors="ignore").read()
        g = gate2(model, roles[persona][1], qs[int(q)], txt); c[g] += 1
        if g != expect: odd.append((g, q, persona, txt[:140].replace("\n", " ")))
    print("gemma3 %-45s got %s" % (name, dict(c)))
    for g, q, persona, t in odd[:5]: print("    %-10s q%-3s %-10s %r" % (g, q, persona, t))
