#!/usr/bin/env python3
"""Run one (adapter, model, task) cell of the eval matrix and append a JSON line.

usage: python3 run.py <adapter> <model> <task> [--timeout 900] [--out results/runs.jsonl]
adapter: agy | codex | claude | copilot
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QUOTA = re.compile(r"quota|rate.?limit|resource.?exhausted|usage limit|429", re.I)
AUTH = re.compile(r"not (logged|signed) in|unauthori[sz]ed|authenticat|login required", re.I)
VERSION = {"agy": ["agy", "--version"], "codex": ["codex", "--version"],
           "claude": ["claude", "--version"], "copilot": ["copilot", "--version"]}


def command(adapter, model, prompt, work):
    if adapter == "agy":
        return ["agy", "-p", prompt, "--model", model, "--mode", "accept-edits",
                "--dangerously-skip-permissions", "--add-dir", work]
    if adapter == "codex":
        return ["codex", "exec", "--skip-git-repo-check", "-C", work, "--approve-for-me",
                "-m", model, prompt]
    if adapter == "claude":
        return ["claude", "-p", prompt, "--model", model, "--permission-mode", "acceptEdits",
                "--dangerously-skip-permissions"]
    if adapter == "copilot":
        return ["copilot", "-p", prompt, "--model", model, "--allow-all-tools", "-s"]
    sys.exit(f"unknown adapter {adapter}")


def cli_version(adapter):
    try:
        out = subprocess.run(VERSION[adapter], capture_output=True, text=True, timeout=20).stdout
        return out.strip().splitlines()[0] if out.strip() else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("adapter"); ap.add_argument("model"); ap.add_argument("task")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "runs.jsonl"))
    a = ap.parse_args()

    tdir = os.path.join(ROOT, "tasks", a.task)
    meta = json.load(open(os.path.join(tdir, "meta.json")))
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    base = tempfile.mkdtemp(prefix=f"eam-{a.adapter}-{a.task}-")
    work = os.path.join(base, "work")
    shutil.copytree(os.path.join(tdir, "fixture"), work)
    hidden = os.path.join(base, "answer.hidden")  # outside the agent's workdir
    if meta.get("generate"):
        subprocess.run([sys.executable, "-I", os.path.join(tdir, meta["generate"]), work, hidden], check=True)
    prompt = open(os.path.join(tdir, "prompt.md")).read()

    t0 = time.time(); status = None
    try:
        p = subprocess.run(command(a.adapter, a.model, prompt, work), cwd=work,
                           capture_output=True, text=True, timeout=a.timeout, stdin=subprocess.DEVNULL)
        rc, log = p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired as e:
        rc, log, status = None, str(e.stdout or "") + str(e.stderr or ""), "timeout"
    except FileNotFoundError:
        rc, log, status = None, "cli not installed", "error"
    wall = round(time.time() - t0, 1)
    open(os.path.join(base, "agent.log"), "w").write(log)

    check_out = ""
    if status is None:
        if rc != 0 and QUOTA.search(log):
            status = "quota_exceeded"
        elif rc != 0 and AUTH.search(log):
            status = "auth_error"
        elif meta["scoring"] == "judge":
            status = "needs_judge"
        else:
            c = subprocess.run(["sh", os.path.join(tdir, "check.sh"), work, tdir, hidden],
                               capture_output=True, text=True, timeout=300)
            check_out = (c.stdout + c.stderr).strip()[-400:]
            status = "pass" if c.returncode == 0 else "fail"

    row = {"ts": stamp, "adapter": a.adapter, "cli_version": cli_version(a.adapter),
           "model": a.model, "task": a.task, "category": meta["category"], "status": status,
           "score": None, "wall_s": wall, "exit_code": rc, "check": check_out,
           "run_dir": base}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
