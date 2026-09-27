---
name: do-codex
description: Use when delegating precise code generation, multi-file refactoring, dedicated code review, or plugin-assisted research to the Codex CLI (codex exec) headlessly, or when offloading to ChatGPT subscription quota.
---

# do-codex — delegate to Codex CLI

Interface adapter for `codex exec`. Deciding whether to delegate and what Codex is
good at belongs to the caller or the `delegate-agent` router. Self-contained: the cache
and return-contract shapes below are the Codex-specific realization of the `delegate-agent`
family conventions.

## 1. Invocation

```bash
# Read / Analysis / Review (no file edits, safest)
codex exec -s read-only "<brief>"
codex exec --skip-git-repo-check -C <dir> -s read-only "<brief>"
codex exec review --uncommitted "<review instructions>"   # dedicated code review

# Code Edits / Generation (using managed git worktree or isolated dir)
codex exec --worktree --approve-for-me "<brief>"
codex exec -C <dir> --approve-for-me "<brief>"

# Structured output & schema enforcement
codex exec --json "<brief>"                       # JSONL events on stdout
codex exec --output-schema schema.json "<brief>"  # enforce final-response shape
codex exec -o /tmp/last.txt "<brief>"             # final message to a file

# Session resume (do NOT pass --approve-for-me or -s to resume; see §6)
codex exec resume --last "<follow-up / test failure logs>"
codex exec resume <session-id> "<follow-up>"
```

- Working dir: `-C <dir>` (or run from the dir). `--skip-git-repo-check` for non-repos.
- Managed worktree: `--worktree` runs in an automatic, isolated Git worktree to protect the host workspace.

## 2. Model catalog + quota bucket

Bucket: **ChatGPT subscription** (single pool, `limit_id: "codex"`), primary window
plus a possible secondary window.

Current slugs (2026-09):
- `gpt-6-astra` — Flagship model: state-of-the-art reasoning, multi-step agentic workflows, difficult coding & software engineering.
- `gpt-6-sol` — High-tier reasoning: complex multi-file refactoring and architecture design (effort: `medium|high|ultra`).
- `gpt-6-luna` — High-speed, cost-optimized workhorse: routine code changes, classification, and quick refactoring.
- `gpt-5.6-sol` — Previous generation reasoning model.
- `gpt-5.6-terra` — Balanced quality, latency, and cost for general coding and analysis.
- `gpt-5.6-luna` — Previous generation lightweight model.
- `--oss` — Local open-source provider via Ollama/LM Studio (zero ChatGPT quota).

Note: The family alias is `gpt-6`. Do not invent unverified slugs like `gpt-6-pro` (explicitly unmapped in Codex runtime).

- Discovery & verify: `/model` in interactive TUI or <https://learn.chatgpt.com/docs/models>.
- Select: `-m <slug>` or `-c model="<slug>"`.
- Reasoning effort: `-c model_reasoning_effort="low|medium|high|ultra"`.

**A slug from the docs is not guaranteed to run on *this* install:**
- **CLI version**: Stale `codex` 400s newer slugs with *"requires a newer version of Codex"*. Check `codex --version`.
- **ChatGPT plan**: Older slugs 400 with *"not supported when using Codex with a ChatGPT account"*. Free tier is most restricted.
- The capability probe in §7a is the only authoritative gate.

## 3. Structured output

```bash
codex exec --json "<brief>"                       # JSONL events on stdout
codex exec -o /tmp/last.txt "<brief>"             # final message to a file
codex exec --output-schema schema.json "<brief>"  # enforce final-response shape
```

Parse the last `item_completed` / `AgentMessage` event from `--json` for final text, and `token_count` events for `usage` + `rate_limits`.

## 4. Execution modes & Permission flags (CRITICAL for headless runs)

In headless execution from another agent (such as Antigravity, Claude, or Hermes), stdin is non-interactive:

| Delegation Goal | Recommended Flags | Rationale |
|---|---|---|
| **Read / Analysis / Review** | `-s read-only` | Prevents file writes and unsafe commands. Zero confirmation prompts. |
| **Direct File Editing** | `--worktree --approve-for-me` | `--approve-for-me` already selects the `workspace-write` sandbox and routes approvals automatically. `--worktree` isolates edits. |

### Why commands fail when calling Codex headlessly
- **Mutual Exclusivity of `--sandbox` and `--approve-for-me` (CRITICAL)**:
  `--approve-for-me` internally configures the `workspace-write` sandbox policy. Combining `-s/--sandbox` with `--approve-for-me` causes an immediate CLI error:
  `error: the argument '--sandbox <SANDBOX_MODE>' cannot be used with '--approve-for-me'`.
  **Never combine `-s` and `--approve-for-me`.** Pass `--approve-for-me` by itself.
- **Confirmation Prompts**: Without `--approve-for-me`, workspace writes or command executions request interactive user approval. In headless mode stdin is closed, causing execution to hang or abort.
- **Dangerous Bypass**: Never use `--dangerously-bypass-approvals-and-sandbox` unless the outer host is an already-isolated ephemeral container. Use `--worktree --approve-for-me` instead.

## 5. Delegation Strategy: Command Separation Principle

To maximize work delegation to Codex while eliminating environment-related tool failures, separate **Reasoning/Generation** from **Command Execution**:

### What to delegate maximally to Codex
1. **Precise code generation & complex algorithms**: Pure algorithmic functions, edge-case heavy logic, math/data structures.
2. **Multi-file refactoring**: Translating interfaces, updating deprecations across multiple files (`--worktree -s workspace-write --approve-for-me`).
3. **Dedicated code review**: `codex exec review --uncommitted` for rigorous line-level correctness checks.
4. **Structured JSON extraction**: Schema-constrained output using `--output-schema`.
5. **Research with plugins**: Browsing, PDF reading, spreadsheet analysis via enabled Codex plugins.

### What to retain for the Host orchestrator (DO NOT delegate to Codex)
- **Running test suites** (`pytest`, `npm test`, `cargo test`)
- **Compiling / building** (`make`, `cargo build`, `npm run build`)
- **Package installation & network operations** (`pip`, `npm install`, `curl`)
- **Git operations** (`git commit`, `git push`, PR creation)

### The Delegate-Verify-Resume Loop
1. **Host writes brief** instructing Codex to edit code or output diff, explicitly forbidding shell commands:
   ```
   DO NOT: run shell commands, package managers, test suites, or git commands.
   TASK: Implement the specified changes in the target files.
         The orchestrator will execute tests and verify.
   ```
2. **Codex executes** code modifications under `--worktree --approve-for-me`.
3. **Host verifies**: Host orchestrator runs tests and linters in the worktree.
4. **If tests fail**: Host feeds compiler/test error output back into Codex via resume:
   `codex exec resume --last "Verification failed with errors: <paste output>. Fix the code without running commands."`
   *(Note: If `resume` stalls on approvals, do not repeatedly retry; use a fresh session with `--worktree --approve-for-me`)*.
5. **Codex fixes code** -> Host re-verifies.

## 6. Session resume & Continuation

```bash
codex exec resume --last "<follow-up prompt>"
codex exec resume <session-id> "<follow-up prompt>"
```

**CRITICAL limitations of `codex exec resume`:**
- **No `--approve-for-me` or `-s/--sandbox` in `resume`**: The `resume` subcommand does not accept `--approve-for-me` or `--sandbox`. Passing them will fail with an unknown option error and result in empty/failed runs.
- **Approval behavior on resume**: `resume` inherits the previous session's sandbox mode, but if interactive approval is triggered in headless mode, execution will hang or fail.
- **Recommended Fallback (Fresh Session)**: If `resume` fails or cannot proceed non-interactively, start a fresh session with context instead:
  ```bash
  codex exec --worktree --approve-for-me "Previous verification failed with: <error output>. Inspect the files and fix the issues."
  ```

## 7. Preflight (MANDATORY)

Two checks, in order: **capability** (can it run at all?) then **quota** (does it have headroom?).

### 7a. Capability probe

A green rate-limit snapshot is meaningless if the CLI/plan can't run a model. Probe the exact model you intend to delegate with:

```bash
out=$(codex exec --skip-git-repo-check -C /tmp -s read-only -m "<model>" "reply with: ok" 2>&1)
if printf '%s' "$out" | grep -qiE 'requires a newer version of Codex|not supported when using Codex with a ChatGPT account'; then
  echo "INCAPABLE: $(printf '%s' "$out" | grep -oE '"message":"[^"]*"' | head -1)"
elif printf '%s' "$out" | grep -qE 'invalid_request_error|"status":4[0-9][0-9]'; then
  echo "ERROR: $(printf '%s' "$out" | grep -oE '"message":"[^"]*"' | head -1)"
else
  echo "OK"
fi
```

- `OK` → capable, continue to 7b.
- `INCAPABLE` → **not a quota problem.** Return `status: "error"`, `reason` = the message; route elsewhere. Write `available:false`, `reason`, and a far-future `resets_at` (`now + 604800`) to the cache so the router stops re-probing a dead CLI — clear it only after `codex update` / a plan change.
- `ERROR` → some other 400; report it, don't retry blindly.
- Try each candidate model once; if none is capable, `do-codex` is unavailable.

### 7b. Quota probe

Codex persists a rate-limit snapshot in every session rollout file. Read the newest one:

```bash
mkdir -p ~/.cache/do-agent
f=$(find ~/.codex/sessions -name 'rollout-*.jsonl' -type f 2>/dev/null | sort | tail -1)
python3 - "$f" <<'EOF'
import json, sys, time
f = sys.argv[1] if len(sys.argv) > 1 else ""
snap = snap_ts = None
try:
    for line in open(f):
        try: o = json.loads(line)
        except: continue
        p = o.get("payload", {})
        if p.get("type") == "token_count" and p.get("rate_limits"):
            snap = p["rate_limits"]; snap_ts = o.get("timestamp")
except OSError:
    pass
if not snap:
    print(json.dumps({"available": True, "reason": "no snapshot", "resets_at": None}))
    raise SystemExit

def win(w):
    w = w or {}
    used = w.get("used_percent")
    resets = w.get("resets_at")
    if resets is None and w.get("resets_in_seconds") is not None:
        resets = int(time.time()) + int(w["resets_in_seconds"])
    return used, resets

pu, pr = win(snap.get("primary"))
su, sr = win(snap.get("secondary"))
reached = snap.get("rate_limit_reached_type")
spend = snap.get("spend_control_reached")
worst = max([x for x in (pu, su) if x is not None], default=None)
resets = pr if (pu or 0) >= (su or 0) else sr
blocked = (worst is not None and worst >= 90) or bool(reached) or bool(spend)
print(json.dumps({
    "available": not blocked,
    "reason": f"primary {pu}% / secondary {su}% reached={reached} spend={spend} snap={snap_ts}",
    "resets_at": resets,
    "last_used_percent": worst,
    "plan": snap.get("plan_type"),
}))
EOF
```

Check **both** windows — `primary` is the short rolling window (5h on Plus/Pro, ~30d on free), `secondary` is the longer/weekly one.

### Cooldown cache — `~/.cache/do-agent/codex.json`

```json
{
  "tool": "codex",
  "available": true,
  "reason": "",
  "checked_at": 1789000000,
  "resets_at": 1789086617,
  "last_used_percent": 31.0,
  "plan": "free"
}
```

**Cache-first rule:** if `available == false` and `resets_at` is in future and `checked_at` < 30 min → return `quota_exceeded` without probing. Otherwise probe, then overwrite cache.

## 8. Auth check (no secret exposure)

```bash
command -v codex >/dev/null || echo "codex not installed"
codex login status  # expect "Logged in using ChatGPT"; summary only — never cat auth.json
```

Fallback if `login status` is unavailable in this build: `test -f ~/.codex/auth.json`.

## 9. Normalized return contract

Print one JSON object as the **last line of stdout**:

```json
{
  "tool": "codex",
  "model": "gpt-5.6-terra",
  "quota_bucket": "chatgpt",
  "status": "ok",
  "resets_at": null,
  "text": "<final AgentMessage>",
  "files_changed": "<unified diff, path list, or null>",
  "session_id": "<rollout session id or null>",
  "usage": { "input": 1234, "output": 567, "cost_usd": null },
  "exit_code": 0
}
```

- `status` ∈ `ok | quota_exceeded | auth_error | error`.
- `quota_bucket` is `"chatgpt"`.
- `cost_usd` is `null` — ChatGPT-subscription usage is subscription-metered.
- Fill `usage` from the final `token_count.total_token_usage`.
- `files_changed`: `git diff` in the target dir after a `workspace-write` run.

## 10. Guardrails & Common Failure Modes

### Guardrails
- **Use `--worktree`**: Isolate file modifications in an automatic Git worktree.
- **No Git/PR actions from Codex**: Codex must never commit, push, or open PRs. The host orchestrator reviews and lands changes.
- **Stage with explicit paths**: `git add <path>...`, never `git add -A` or `git add .`.
- **Forbid shell command execution in brief**: Always instruct Codex not to run tests or builds directly.

### Common Failure Modes & Remedies

| Symptom / Failure | Root Cause | Fix |
|---|---|---|
| **`--sandbox cannot be used with --approve-for-me`** | Conflicting flags: `--approve-for-me` already selects the workspace-write sandbox | Remove `-s / --sandbox`. Pass `--approve-for-me` alone (e.g. `--worktree --approve-for-me`) |
| **Empty run / option error on `resume`** | Passed `--approve-for-me` or `-s` to `codex exec resume` (unsupported on resume) | Omit flags from resume command, or start a fresh session with `--worktree --approve-for-me` |
| **Hangs / stalls in headless run** | Approval prompt requested for workspace write without auto-approval | Add `--approve-for-me` (without `-s`), or use `-s read-only` |
| **Command fails in subshell** | Tool execution restricted or blocked by Codex sandbox policy | Enforce Command Separation: host runs tests; Codex only produces code edits |
| **Working tree collision / dirty tree** | Parallel writing runs overwriting same directory | Pass `--worktree` to automatically run in a new managed Git worktree |
| **Model 400 error (Incapable)** | Stale Codex CLI or ChatGPT plan restriction | Run capability probe (§7a); route to supported model or update CLI |
| **Plugin missing error** | Task routed for browser/pdf/spreadsheet but plugin disabled in config | Check `~/.codex/config.toml` `[plugins.*]` before routing |
