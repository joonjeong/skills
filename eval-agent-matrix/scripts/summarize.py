#!/usr/bin/env python3
"""Summarize results/runs.jsonl into a markdown matrix (latest run per cell).

usage: python3 summarize.py [runs.jsonl] [--since YYYYMMDD]
Cell: status (wall seconds). Judged cells show score/10 once filled in.
"""
import collections, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [x for x in sys.argv[1:] if not x.startswith("--")]
path = args[0] if args else os.path.join(ROOT, "results", "runs.jsonl")
since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else ""
latest = {}
for line in open(path):
    r = json.loads(line)
    if r["ts"] >= since:
        latest[(r["adapter"], r["model"], r["task"])] = r
tasks = sorted({k[2] for k in latest})
rows = sorted({(k[0], k[1]) for k in latest})
print("| adapter | model | " + " | ".join(tasks) + " |")
print("|---|---|" + "---|" * len(tasks))
for ad, m in rows:
    cells = []
    for t in tasks:
        r = latest.get((ad, m, t))
        if not r: cells.append("—"); continue
        s = r["status"] if r["score"] is None else f'{r["score"]}/10'
        cells.append(f'{s} ({r["wall_s"]}s)')
    print(f"| {ad} | {m} | " + " | ".join(cells) + " |")
pend = [r for r in latest.values() if r["status"] == "needs_judge" and r["score"] is None]
if pend:
    print("\nNeeds judging:")
    for r in pend: print(f'- {r["adapter"]}/{r["model"]}/{r["task"]}: {r["run_dir"]}/work')
