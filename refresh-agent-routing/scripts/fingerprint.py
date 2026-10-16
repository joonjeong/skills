#!/usr/bin/env python3
"""Detect coding-agent CLI / model-catalog changes since the last acknowledged state.

usage:
  fingerprint.py check [--hook]   print changes (exit 0 always); --hook: throttle to 1/day, silent if none
  fingerprint.py ack              record the current state as acknowledged
State: ~/.cache/do-agent/agent-fingerprint.json (acked), ~/.cache/do-agent/agent-fingerprint.last (hook throttle)
"""
import json, os, subprocess, sys, time

CACHE = os.path.expanduser("~/.cache/do-agent")
ACKED = os.path.join(CACHE, "agent-fingerprint.json")
STAMP = os.path.join(CACHE, "agent-fingerprint.last")
PROBES = {
    "agy.version": ["agy", "--version"],
    "agy.models": ["agy", "models"],
    "codex.version": ["codex", "--version"],
    "claude.version": ["claude", "--version"],
    "copilot.version": ["copilot", "--version"],
}


def probe(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=15, stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        return "<not installed>"
    except subprocess.TimeoutExpired:
        return None  # unknown; never report as a change
    lines = [l.split("\t")[0].strip() for l in p.stdout.splitlines()
             if l.strip() and not l.startswith(("Fetching", "Run '"))]
    return sorted(lines) if len(lines) > 1 else (lines[0] if lines else None)


def current():
    return {k: probe(v) for k, v in PROBES.items()}


def diff(old, new):
    out = []
    for k, v in new.items():
        if v is None or old.get(k) == v:
            continue
        o = old.get(k)
        if isinstance(v, list) and isinstance(o, list):
            add, rm = sorted(set(v) - set(o)), sorted(set(o) - set(v))
            out.append(f"{k}: +{add} -{rm}")
        else:
            out.append(f"{k}: {o!r} -> {v!r}")
    return out


def main():
    os.makedirs(CACHE, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    hook = "--hook" in sys.argv
    if mode == "ack":
        json.dump({"acked_at": int(time.time()), "state": current()}, open(ACKED, "w"), indent=1)
        print("acknowledged current agent CLI state"); return
    if hook:
        try:
            if time.time() - os.path.getmtime(STAMP) < 86400:
                return
        except OSError:
            pass
        open(STAMP, "w").write(str(int(time.time())))
    try:
        old = json.load(open(ACKED))["state"]
    except Exception:
        old = None
    new = current()
    if old is None:
        if hook:
            print("[refresh-agent-routing] No acknowledged agent-CLI baseline yet. "
                  "Ask the user whether to run the refresh-agent-routing skill to set one.")
        else:
            print(json.dumps(new, indent=1))
        return
    changes = diff(old, new)
    if changes:
        print("[refresh-agent-routing] Coding-agent CLI / model changes since last routing review:")
        for c in changes: print("  - " + c)
        if hook:
            print("Before other work, ask the user whether to review model routing now "
                  "(refresh-agent-routing skill). If they decline, run "
                  "`python3 ~/.config/skillshare/skills/refresh-agent-routing/scripts/fingerprint.py ack`.")
    elif not hook:
        print("no changes")


if __name__ == "__main__":
    main()
