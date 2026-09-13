"""Check gate v3's pre-filter against the hand-read cases it was validated on.

Run from the repository root. Exits non-zero if the implemented check does not
reproduce the recorded result.
"""
import json, pathlib, sys
sys.path.insert(0, "code")
from utils.refusal_gate import has_refusal_language
base = pathlib.Path("results/refusal_gate_validation")
expect = {"v3_labels_gpt54mini.json": (6, 7, 29, 29), "v3_labels_gemma3.json": (1, 1, 7, 7)}
got = {}
for name in expect:
    cases = json.load(open(base / name))["cases"]
    ref = [c for c in cases if c["label"] == "REFUSED"]
    non = [c for c in cases if c["label"] == "NOT_REFUSED"]
    kept = [c for c in ref if has_refusal_language(c["opening"])]
    released = [c for c in non if not has_refusal_language(c["opening"])]
    missed = ["%s q%s" % (c["persona"], c["q"]) for c in ref if c not in kept]
    flagged = ["%s q%s" % (c["persona"], c["q"]) for c in non if c not in released]
    got[name] = (len(kept), len(ref), len(released), len(non))
    print("%s: refusals kept %d/%d (missed %s); non-refusals released %d/%d (still flagged %s)"
          % (name, len(kept), len(ref), missed, len(released), len(non), flagged))
ok = got == expect
print("MATCHES VALIDATED NUMBERS" if ok else "MISMATCH: got %s, expected %s" % (got, expect))
sys.exit(0 if ok else 1)
