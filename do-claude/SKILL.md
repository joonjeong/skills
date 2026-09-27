---
name: do-claude
description: Use when delegating nuanced code refactoring, system architecture design, or reviewer-facing documentation to a separate Claude Code process (claude -p) headlessly, or when offloading to a separate Claude quota.
---

# do-claude — delegate to a separate Claude Code process

Interface adapter for `claude -p`. Use this when you want Claude's strengths (writing,
design, nuanced refactoring) but on a **different quota** than the session you are in, or
as a parallel worker. Self-contained: the cache and return-contract shapes below are the
Claude-specific realization of the `delegate-agent` family conventions.

For same-session parallel subtasks that share context, use the native `Agent` tool directly —
not this skill.

## 1. Invocation

```bash
# Read / Analysis / Design (no file edits, safest)
claude -p "<brief>" --permission-mode plan
claude -p "<brief>" --tools "Read,Grep,Glob"

# Code Edits / Generation (using managed worktree or isolated dir)
claude -p "<brief>" -w --permission-mode acceptEdits --dangerously-skip-permissions
claude -p "<brief>" --permission-mode acceptEdits --add-dir <dir> --dangerously-skip-permissions

# Targeted model & reasoning effort
claude -p "<brief>" --model sonnet --effort high

# Session resume (e.g. feeding back test failure output from host)
claude -p -c "<follow-up / test failure logs>"          # continue most recent
claude -p -r <session-id> "<follow-up>"                 # resume by id
```

- Run under a different login by pointing `CLAUDE_CONFIG_DIR` (or relevant auth env)
  at a separate profile before the call — that is the primary reason to route here.
- Managed worktree: `-w, --worktree` automatically creates and operates in an isolated Git worktree.

## 2. Model catalog + quota bucket

Bucket: **a Claude subscription** (Max / API), whichever profile the call runs under.

Current slugs & aliases (2026-09):
- `opus` (resolves to `claude-opus-5-5` default in CLI 2.1.280+, or `claude-opus-5`) — Flagship frontier reasoning, 1M native context window, deep architectural trade-offs, reviewer-facing narratives.
- `sonnet` (resolves to `claude-sonnet-5`, or `claude-sonnet-4-6`) — Everyday coding, nuanced multi-file refactoring (default).
- `haiku` (resolves to `claude-haiku-4-5`) — High-speed, lightweight tasks.
- `fable` (resolves to `claude-fable-5-1`) — Creative and structured synthesis.

Specific slugs you can pass directly to `--model`:
- `claude-opus-5-5` (or `opus-5-5`) — 1M context native, top-tier reasoning.
- `claude-opus-5` (or `opus-5`) — Previous generation Opus.
- `claude-sonnet-5` (or `sonnet-5`) — Primary coding workhorse.
- `claude-haiku-4-5` — Fast utility worker.

- Discovery & verify: `/model` in an interactive session.
- Select: `--model <alias|slug>`.
- Reasoning effort: `--effort low|medium|high` (for models with adaptive thinking).
- Fallback: `--fallback-model <model>` for automatic downgrade on high server load.

## 3. Structured output

```bash
claude -p "<brief>" --output-format json          # single result object with usage + cost
claude -p "<brief>" --output-format stream-json    # NDJSON events
claude -p "<brief>" --output-format json | jq '.result, .total_cost_usd, .usage'
```

## 4. Execution modes & Permission flags (CRITICAL for headless runs)

In non-interactive headless delegation (`-p`), stdin is closed and confirmation prompts cannot be answered:

| Delegation Goal | Recommended Flags | Rationale |
|---|---|---|
| **Read / Analysis / Design** | `--permission-mode plan` (or `--tools "Read,Grep,Glob"`) | Read-only tools require no confirmation. Zero risk of hang. |
| **Direct File Editing** | `-w --permission-mode acceptEdits --dangerously-skip-permissions` | `-w` creates a clean Git worktree. `--dangerously-skip-permissions` prevents interactive confirmation prompts from hanging headless execution. |

### Why commands fail when calling Claude headlessly
- **Confirmation Prompts**: If Claude attempts a file write or command execution without permission bypass in `-p` mode, it stalls waiting for stdin and aborts or times out.
- **Remedy**: Always pair file editing with `-w` (worktree isolation) and `--dangerously-skip-permissions`. Never run unisolated writes on a dirty working tree.

## 5. Delegation Strategy: Command Separation Principle

To maximize work delegation to Claude while preventing headless tool failures, separate **Reasoning/Generation** from **Command Execution**:

### What to delegate maximally to Claude
1. **Nuanced multi-file refactoring**: Delicate code transformations requiring semantic preservation and contextual subtlety (`-w --permission-mode acceptEdits --dangerously-skip-permissions`).
2. **Reviewer-facing narratives & docs**: PR descriptions, RFCs, Minto Pyramid architecture docs, technical retrospectives.
3. **Complex trade-off analysis**: New feature design, API boundary critique, architecture ADRs.
4. **Adversarial code review (Red Teaming)**: Identifying subtle logical bugs, security edge cases, or gamed checks in existing PRs.

### What to retain for the Host orchestrator (DO NOT delegate to Claude)
- **Running test suites** (`pytest`, `npm test`, `cargo test`)
- **Compiling / building** (`make`, `cargo build`, `npm run build`)
- **Package management & network calls** (`npm install`, `pip`, `curl`)
- **Git version control** (`git commit`, `git push`, PR creation)

### The Delegate-Verify-Resume Loop
1. **Host writes brief** instructing Claude to edit code or output diff, explicitly forbidding shell commands:
   ```
   DO NOT: run shell commands, package managers, test suites, or git commands.
   TASK: Read relevant files, analyze the requirements, and apply code edits.
         The orchestrator will execute tests and verify.
   ```
2. **Claude executes** code modifications under `-w --permission-mode acceptEdits --dangerously-skip-permissions`.
3. **Host verifies**: Host orchestrator runs tests and linters in the worktree.
4. **If tests fail**: Host feeds compiler/test error output back into Claude via resume:
   `claude -p -r <session-id> "Verification failed with errors: <paste output>. Fix the code without running commands."`
5. **Claude fixes code** -> Host re-verifies.

## 6. Session resume

`claude -p -c` (most recent) or `claude -p -r <session-id>`; `--from-pr` to resume a PR-linked session.

## 7. Quota preflight (MANDATORY)

Claude Code exposes no headless rate-limit readout. Cache-first + cost + error classification:

```bash
mkdir -p ~/.cache/do-agent
cache=~/.cache/do-agent/claude.json
python3 - "$cache" <<'EOF'
import json, sys, time
try: c = json.load(open(sys.argv[1]))
except Exception: c = {}
now = time.time()
if (not c.get("available", True)
        and (c.get("resets_at") or 0) > now
        and now - (c.get("checked_at") or 0) < 1800):
    print("SKIP"); raise SystemExit(3)
print("PROBE")
EOF
```

- On PROBE, run the job with `--output-format json`. Classify:
  - Result / stderr shows a usage-limit / "rate limit" / 429 / "Claude usage limit reached" message → `available:false`; parse the reset time from the message ("resets at 3pm" / an ISO time); if absent use `now + 18000` (5h window).
  - Success → record `checked_at`, `usage`, `total_cost_usd`, clear `reason`.
- Blocked → return `status: "quota_exceeded"` + `resets_at`, do **not** delegate.

### Cooldown cache — one file per profile

Distinct Claude profiles have distinct quotas — key the cache by profile:
`~/.cache/do-agent/claude-<profile>.json`.

```json
{
  "tool": "claude",
  "profile": "worker",
  "available": true,
  "reason": "",
  "checked_at": 1789000000,
  "resets_at": null,
  "session_cost_usd": 0.42
}
```

**Cache-first rule:** if `available == false` and `resets_at` is in future and `checked_at` < 30 min → return `quota_exceeded` without probing. `resets_at` is parsed from the limit message or a `now + 18000` (5h) estimate.

## 8. Auth check (no secret exposure)

```bash
command -v claude >/dev/null || echo "claude not installed"
claude -p 'ok' --output-format json >/dev/null 2>&1 || echo "claude not authenticated / over limit"
```

Never read `~/.claude/.credentials.json` or other auth files.

## 9. Normalized return contract

Print one JSON object as the **last line of stdout**:

```json
{
  "tool": "claude",
  "model": "sonnet",
  "quota_bucket": "claude:worker",
  "status": "ok",
  "resets_at": null,
  "text": "<result field>",
  "files_changed": "<unified diff, path list, or null>",
  "session_id": "<session_id or null>",
  "usage": { "input": 1234, "output": 567, "cost_usd": 0.03 },
  "exit_code": 0
}
```

- `status` ∈ `ok | quota_exceeded | auth_error | error`.
- `quota_bucket` is `claude:<profile>` — always name the profile it ran under.
- `cost_usd` is real, from JSON result's `total_cost_usd`; `usage` from `usage`.
- `session_id` from result's `session_id` for `--resume`.
- `files_changed`: `git diff` in the target dir after an `acceptEdits` run.

## 10. Guardrails & Common Failure Modes

### Guardrails
- **Use `-w, --worktree`**: Isolate file edits in an automatic Git worktree.
- **No Git/PR actions from Claude**: Delegated Claude must not commit, push, or open PRs. The host orchestrator reviews and lands changes.
- **Forbid shell command execution in brief**: Always instruct Claude not to run tests or builds directly.
- **Separate profile quota**: Always run under a designated worker profile (`CLAUDE_CONFIG_DIR`) to avoid burning this session's quota.

### Common Failure Modes & Remedies

| Symptom / Failure | Root Cause | Fix |
|---|---|---|
| **Hangs / stalls in headless run** | Claude prompted for tool permission without interactive stdin | Use `-w --permission-mode acceptEdits --dangerously-skip-permissions` or `--permission-mode plan` |
| **Command fails in subshell** | Claude attempted to run test/build command that failed in restricted environment | Enforce Command Separation: host runs tests; Claude only inspects code and produces fixes |
| **Dirty working tree pollution** | Writes occurred directly in main repository working tree | Pass `-w, --worktree` to automatically run in an isolated Git worktree |
| **Rate limit reached (429)** | Target profile exhausted hourly/daily quota | Parse `resets_at`, set cache `available:false`, fall back to `do-agy` (Claude bucket) or `do-codex` |
