---
name: do-agy
description: Use when delegating a task to Antigravity (agy) headlessly — large-context repo work, newest Gemini 3 models, or running Claude/OSS models off a separate quota. Antigravity meters Gemini and non-Gemini models on separate quota buckets; runs a preflight first.
---

# do-agy — delegate to Antigravity (agy)

Interface adapter for `agy --print`. This skill is the interface only — deciding whether
to delegate and what Antigravity is good at belongs to the caller or the `delegate-agent`
router. Self-contained: the cache and return-contract shapes below are the agy-specific
realization of the `delegate-agent` family conventions.

## 1. Invocation

```bash
agy -p "<brief>"                              # single non-interactive turn
agy -p "<brief>" --add-dir <path> --add-dir <path2>
agy -p "<brief>" --print-timeout 15m          # default is 5m
agy -c -p "<follow-up>"                        # continue most recent
agy --conversation <id> -p "<follow-up>"      # resume by id
```

## 2. Model catalog + quota buckets

Two **separate** buckets — this is the main reason to route here:

| Bucket | Models (2026-09) |
|---|---|
| **Gemini** | `gemini-3.8-flash-{high,medium,low}`, `gemini-3.7-flash-*`, `gemini-3.6-flash-*`, `gemini-3.1-pro-{high,low}` |
| **non-Gemini** | `claude-sonnet-4-6`, `claude-opus-4-6-thinking`, `gpt-oss-120b-medium` |

- Live list (authoritative): `agy models`.
- Select: `--model <slug>`. Reasoning effort: `--effort low|medium|high` (flash slugs
  also bake the tier into the name).
- Routing a Claude-family or OSS model here spends the **non-Gemini** bucket, leaving
  your Claude Max and ChatGPT quotas untouched.

## 3. Structured output

```bash
agy -p "<brief>" --output-format json                       # single JSON result
agy -p "<brief>" --output-format json --json-schema s.json  # enforce final shape
agy -p "<brief>" --output-format stream-json                # NDJSON events
```

## 4. Sandbox / permissions

```bash
agy -p "<brief>" --sandbox                       # terminal restrictions on — default choice
agy -p "<brief>" --dangerously-skip-permissions  # avoid; only in an externally sandboxed env
```

Default execution mode is fine for read/analysis. For edits, `--mode accept-edits`;
for design-only, `--mode plan`.

## 5. Session resume

`agy -c` (most recent) or `agy --conversation <id>`. Capture the id from the first run.

## 6. Quota preflight (MANDATORY)

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

## 7. Auth check (no secret exposure)

```bash
command -v agy >/dev/null || echo "agy not installed"
agy models >/dev/null 2>&1 || echo "agy not authenticated"   # fails clean if logged out
```

Never read files under `~/.antigravity/`.

## 8. Normalized return contract

Print one JSON object as the **last line of stdout**:

```json
{
  "tool": "agy",
  "model": "gemini-3.1-pro-high",
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
- `quota_bucket` is `"gemini"` or `"non-gemini"` per the model used.
- `cost_usd` is `null` — Antigravity usage is subscription-metered, not per-call billed.
- `usage` from the `--output-format json` result's token fields (omit if absent).
- `files_changed`: `git diff` in the target dir after an `accept-edits` run.

## 9. Guardrails

- `--sandbox` unless the brief needs real edits; `--mode plan` for design-only.
- No `commit` / `push` / PR from the delegated run.
- Parallel writing runs each get their own directory / worktree.
- Never pass `--dangerously-skip-permissions` outside an already-sandboxed host.
