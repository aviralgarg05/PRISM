import sys, glob, random, re, os, collections
sys.path.insert(0, "."); sys.path.insert(0, sys.argv[1])
from utils.utils import get_model, read_questions_from_file
from utils.roles import roles
from gate2 import gate2
qs = read_questions_from_file("../data/compass_questions.txt")
model = get_model("openai", "gpt-4o-mini", 0.0)
REFU = re.compile(r"\b(cannot|can't|can not|won't|will not|unable to|am not able to|must decline to|refuse to)\b[^.]{0,40}\b(fulfil|fulfill|comply|write|create|produce|generate|provide|argue|adopt|take on|role-?play|pretend)", re.I)
DISC = re.compile(r"\b(do not|don't|does not|doesn't)\s+(have|hold|possess)\s+(personal|my own|any personal)", re.I)
QUOTA = {"regex refuse_then_essay": 15, "regex pure_refusal": 3, "disclaimer_then_essay": 20, "ordinary essay": 20}
EXPECT = {"regex pure_refusal": "REFUSED", "regex refuse_then_essay": "COMPLIED (in-persona voice, from earlier read)",
          "disclaimer_then_essay": "debatable", "ordinary essay": "COMPLIED"}
rng = random.Random(11)
buckets = collections.defaultdict(list)
files = glob.glob("../out/essays/pc*_openai_gpt-3.5-turbo_*.txt"); rng.shuffle(files)
for p in files:
    txt = open(p, errors="ignore").read(); head = txt[:400]
    b = ("regex refuse_then_essay" if REFU.search(head) and len(txt) >= 900 else "regex pure_refusal" if REFU.search(head)
         else "disclaimer_then_essay" if DISC.search(head) else "ordinary essay")
    if len(buckets[b]) < QUOTA[b]: buckets[b].append(p)
    if all(len(buckets[k]) >= v for k, v in QUOTA.items()): break
for name in ("regex pure_refusal", "regex refuse_then_essay", "disclaimer_then_essay", "ordinary essay"):
    c = collections.Counter(); flagged = []
    for p in buckets[name]:
        m = re.match(r"pc(\d+)_openai_gpt-3\.5-turbo_(.+)_([0-9a-f]{10})\.txt$", os.path.basename(p))
        q, role = m.group(1), m.group(2)
        persona = roles[role][1] if role in roles and roles[role][1] else role
        txt = open(p, errors="ignore").read()
        g = gate2(model, persona, qs[int(q)], txt); c[g] += 1
        if g != "COMPLIED": flagged.append((g, q, role, txt[:110].replace("\n", " ")))
    print("gpt-3.5-turbo %-24s n=%2d expect %-45s got %s" % (name, len(buckets[name]), EXPECT[name], dict(c)))
    if name in ("regex refuse_then_essay", "ordinary essay"):
        for g, q, role, t in flagged: print("    %-10s q%-3s %-14s %r" % (g, q, role, t))
