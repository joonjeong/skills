#!/bin/sh
python3 -I - "$1/answer.json" "$2/expected.json" <<'P'
import json, sys
try: got = json.load(open(sys.argv[1]))
except Exception as e: print("bad json:", e); sys.exit(1)
exp = json.load(open(sys.argv[2]))
if got == exp: print("exact match"); sys.exit(0)
print("mismatch:", json.dumps(got)[:300]); sys.exit(1)
P
