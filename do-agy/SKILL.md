---
name: do-agy
description: Use when delegating large-context repository analysis, multi-file code editing, architecture design, or review to Antigravity (agy) headlessly, or when offloading to separate Gemini/non-Gemini quota buckets.
---

# do-agy — delegate to Antigravity (agy)

Interface adapter for `agy --print`. Deciding whether to delegate and what Antigravity is
good at belongs to the caller or the `delegate-agent` router. Self-contained: the cache
and return-contract shapes below are the agy-specific realization of the `delegate-agent`
family conventions.

## 1. Invocation

```bash
# Read / Analysis / Planning (no file edits, zero risk)
agy -p "<brief>"
agy -p "<brief>" --print-timeout 15m          # default 0s = wait until the turn completes

# Code Edits / Generation (in an isolated directory/worktree)
agy -p "<brief>" --mode accept-edits --dangerously-skip-permissions

# Targeted model selection (Gemini bucket vs non-Gemini Claude bucket)
agy -p "<brief>" --model gemini-4-argon-high             # Gemini bucket: massive context
agy -p "<brief>" --model gemini-3.8-flash-high           # Gemini bucket: high speed, cheap
agy -p "<brief>" --model claude-sonnet-5-5-medium               # non-Gemini bucket: nuanced coding
agy -p "<brief>" --model claude-opus-5-5-high        # non-Gemini bucket: deep reasoning & prose

# Targeted directory scope
agy -p "<brief>" --add-dir <path> --add-dir <path2>

# Resume session (e.g. feeding back test failure output from host)
agy -c -p "<follow-up / test failure logs>"   # continue most recent
agy --conversation <id> -p "<follow-up>"      # resume by id
```

## 2. Model catalog + quota buckets

Two **completely separate** quota pools — this is a primary reason to route here:

| Bucket | Models (2026-10, agy 1.4.0) | Key Strength |
|---|---|---|
| **Gemini** | `gemini-4-argon-{high,medium,low}`, `gemini-3.8-flash-{high,medium,low}` | Multi-million token context, high-speed repo scan, structured JSON |
| **non-Gemini** | `claude-sonnet-5-5-{high,medium,low}`, `claude-opus-5-5-{high,medium,low}`, `gpt-oss-120b-medium` | Nuanced refactoring, deep thinking, reviewer-facing prose, zero Claude Max quota hit |

- Live list (authoritative): `agy models`.
- Select: `--model <slug>`. Reasoning effort: `--effort low|medium|high|xhigh|max`. Slugs bake the tier into the name; a base name without a tier/`--effort` falls back to the model's default thinking level (agy ≥1.3.4).
- **Quota separation**: Routing `claude-sonnet-5-5-medium` or `claude-opus-5-5-high` through `do-agy` consumes Google's **non-Gemini** quota bucket, leaving your Claude Code (Claude Max / Anthropic API) quotas 100% untouched.

## 3. Structured output

```bash
agy -p "<brief>" --output-format json                       # single JSON result
agy -p "<brief>" --output-format json --json-schema s.json  # enforce final shape
agy -p "<brief>" --output-format stream-json                # NDJSON events
```

## 4. Execution modes & Permission flags (CRITICAL for -p mode)

`agy -p` runs non-interactively. Understanding permission mechanics avoids common silent failures:

| Delegation Goal | Recommended Flags | Rationale |
|---|---|---|
| **Read / Analysis / Design** | `agy -p "<brief>"` (or `--mode plan`) | Read tools need no confirmation. Fully safe. |
| **Edits with guarded autonomy** | `agy -p "<brief>" --mode auto` | Auto mode (agy ≥1.3.5, Linux/macOS) approves edits and safe commands, still blocks irreversible actions and reviews sandbox-escaping commands. Prefer over skip-permissions when available. |
| **Direct File Editing** (agy <1.3.5 or Windows) | `agy -p "<brief>" --mode accept-edits --dangerously-skip-permissions` | `-p` has no interactive stdin. Without skip-permissions, write/tool approvals stall or fail. Always isolate in a dedicated worktree/branch. |

### Why bash/shell commands fail in `-p` mode
- **No interactive prompt**: In non-interactive `-p` mode, if agy attempts a tool call requiring user confirmation (e.g. terminal execution outside auto-approved rules, or sandbox escalation), it fails or aborts because stdin is closed.
- **`--sandbox` restrictions**: Passing `--sandbox` activates terminal isolation (network disabled, outside-workspace filesystem blocked). Commands like `npm`, `pip`, `git fetch`, or network-bound tools fail immediately.
- **Remedy**: Do **not** use `--sandbox` expecting it to "make commands safe" — it breaks command execution. Instead, apply the **Command Separation Principle** below.

## 5. Delegation Strategy: Model Classification & Command Separation

### 5a. Model characteristics (routing lives in `delegate-agent`)

Which task goes to which adapter/model is decided by `delegate-agent`
(`references/task-routing.md`, `references/model-index.md`). Do not route from here.
This section only describes what each agy model family offers:

| Model family | Bucket | Characteristics |
|---|---|---|
| `gemini-4-argon-*` | Gemini | Largest context window; repo-wide scan, multi-file trace, schema-conformant JSON |
| `gemini-3.8-flash-*` | Gemini | Lowest latency/cost; drafts, routine edits |
| `claude-opus-5-5-*` | non-Gemini | Same generation as `do-claude` Opus; deep reasoning, prose, adversarial review — without spending Claude quota |
| `claude-sonnet-5-5-*` | non-Gemini | Balanced coding with nuance preservation, off Claude quota |
| `gpt-oss-120b-medium` | non-Gemini | Open-weight model; cross-family diversity |

#### `do-claude` (Native CLI) vs `do-agy --model claude-*`
- **`do-claude`**: needs Claude Code native features (plugins, `~/.claude` MCP servers, `--permission-mode`). Consumes Claude Max/API quota.
- **`do-agy --model claude-*`**: same model generation, consumes Antigravity non-Gemini quota instead.

### 5b. Command Separation Principle

To maximize work delegation to AGY while eliminating failures, separate **Reasoning/Generation** from **Command Execution**:

#### What to delegate maximally to AGY
1. **Massive-context repository analysis**: Gemini's multi-million token context window excels at analyzing huge codebases, tracing cross-module dependencies, and finding root causes.
2. **Multi-file code generation & refactoring**: Writing implementations, generating components, modifying code files directly (`--mode accept-edits`).
3. **Architecture, design specs & diagrams**: Generating technical RFCs, API designs, Mermaid diagrams.
4. **Structured JSON extraction**: Complex document/code parsing with `--json-schema`.
5. **Independent code review & second opinion**: Reviewing diffs or diagnosing tricky bugs via Claude Thinking models.

#### What to retain for the Host orchestrator (DO NOT delegate to AGY)
- **Running test suites** (`pytest`, `npm test`, `cargo test`)
- **Compiling / building** (`make`, `npm run build`, `cargo build`)
- **Package management & network calls** (`npm install`, `pip`, `curl`)
- **Git version control** (`git commit`, `git push`, PR creation)

### 5c. The Delegate-Verify-Resume Loop
1. **Host writes brief** instructing AGY to edit code or output diff, explicitly forbidding shell commands:
   ```
   DO NOT: run shell commands, package managers, test suites, or git commands.
   TASK: Read relevant files, analyze the issue, and apply the code fixes.
         The orchestrator will execute tests and verify.
   ```
2. **AGY executes** code modifications under `--mode accept-edits --dangerously-skip-permissions` in an isolated branch/worktree.
3. **Host verifies**: Host orchestrator runs tests and linters locally.
4. **If tests fail**: Host feeds compiler/test error output back into AGY via resume:
   `agy -c -p "Verification failed with errors: <paste output>. Fix the code without running commands."`
5. **AGY fixes code** -> Host re-verifies.

## 6. Session resume

`agy -c` (most recent) or `agy --conversation <id>`. Capture the id from the first run.

## 7. Quota preflight (MANDATORY)

`agy` exposes no quota command. Use cache-first + error classification:

```bash
mkdir -p ~/.cache/do-agent
cache=~/.cache/do-agent/agy.json
# 1. cache-first: if unavailable and resets_at in future and checked_at < 30m old -> quota_exceeded
python3 - "$cache" <<'EOF'
import json, sys, time
try: c = json.load(open(sys.argv[1]))
except Exception: c = {}
now = time.time()
if (not c.get("available", True)
        and (c.get("resets_at") or 0) > now
        and now - (c.get("checked_at") or 0) < 1800):
    print("SKIP: quota_exceeded until", c.get("resets_at")); raise SystemExit(3)
print("PROBE")
EOF
```

- If the cache says proceed, run the real job. Classify the result:
  - JSON result contains a quota / rate-limit / "resource exhausted" error, or exit
    code signals it → set `available:false`, `reason`, and `resets_at` (parse from the
    message; if absent, set `now + 3600` as a conservative cooldown).
  - Success → `available:true`, update `checked_at`, clear `reason`.
- Blocked → return `status: "quota_exceeded"` + `resets_at`, do **not** delegate.

### Cooldown cache — one file per bucket

Antigravity meters Gemini and non-Gemini separately, so key the cache by bucket:
`~/.cache/do-agent/agy-gemini.json` and `~/.cache/do-agent/agy-nongemini.json`. A
Gemini exhaustion must not block a non-Gemini route or vice-versa.

```json
{
  "tool": "agy",
  "bucket": "gemini",
  "available": true,
  "reason": "",
  "checked_at": 1789000000,
  "resets_at": null
}
```

No `last_used_percent` — `agy` gives no usage percentage, only pass/fail. `resets_at` is
parsed from the error message when present, else a conservative `now + 3600`.

## 8. Auth check (no secret exposure)

```bash
command -v agy >/dev/null || echo "agy not installed"
agy models >/dev/null 2>&1 || echo "agy not authenticated"   # fails clean if logged out
```

Never read files under `~/.antigravity/`.

## 9. Normalized return contract

Print one JSON object as the **last line of stdout**:

```json
{
  "tool": "agy",
  "model": "gemini-4-argon-high",
  "quota_bucket": "gemini",
  "status": "ok",
  "resets_at": null,
  "text": "<final result text>",
  "files_changed": "<unified diff, path list, or null>",
  "session_id": "<conversation id or null>",
  "usage": { "input": 1234, "output": 567, "cost_usd": null },
  "exit_code": 0
}
```

- `status` ∈ `ok | quota_exceeded | auth_error | error`.
- `quota_bucket` is `"gemini"` or `"non-gemini"` per the model used (`claude-*` models return `"non-gemini"`).
- `cost_usd` is `null` — Antigravity usage is subscription-metered, not per-call billed.
- `usage` from the `--output-format json` result's token fields (omit if absent).
- `files_changed`: `git diff` in the target dir after an `accept-edits` run.

## 10. Guardrails & Common Failure Modes

### Guardrails
- **Isolate file edits**: Always run `--mode accept-edits` in a dedicated worktree or branch, never directly on `main` or a dirty working tree.
- **No Git/PR actions from AGY**: AGY must never commit, push, or open PRs. The host orchestrator reviews and lands changes.
- **No secret access**: AGY must never read `.env`, tokens, or credentials.
- **Forbid shell command execution in brief**: Always instruct AGY not to run verification commands, tests, or builds.

### Common Failure Modes & Remedies

| Symptom / Failure | Root Cause | Fix |
|---|---|---|
| **Stalls / hangs in `-p` mode** | AGY prompted for tool execution permission without interactive stdin | Add `--dangerously-skip-permissions` (in an isolated directory/worktree) or stick to read-only/plan mode |
| **Command fails with network/sandbox error** | `--sandbox` flag enabled terminal sandbox, blocking network or commands | Remove `--sandbox`; do not ask AGY to run network commands or package installs |
| **Tool exit code 1 on test/build** | AGY attempted to run test/build command that failed in restricted subshell | Enforce Command Separation: host runs tests; AGY only inspects code and produces fixes |
| **Timeout exceeded** | Long analysis or large refactor hit default timeout | Pass `--print-timeout 15m` (or higher) |
| **`--agent <name>` exits 1 listing agents** | Unknown agent name (agy ≥1.3.4 no longer silently falls back) | Check `agy agents` and pass an existing name |
| **Question/clarification prompt blocked** | AGY called interactive question tool in headless mode | Ensure brief is fully self-contained and explicit about acceptance criteria |
