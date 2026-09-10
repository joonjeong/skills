---
name: do-claude
description: Use when delegating a task to a separate Claude Code process (claude -p) headlessly — to run on a different Claude account or quota, or to fan out background work without spending the current session's context. Runs a quota/cost preflight first.
---

# do-claude — delegate to a separate Claude Code process

Interface adapter for `claude -p`. Use this when you want Claude's strengths (writing,
design, nuanced refactor) but on a **different quota** than the session you are in, or
as a parallel worker. Self-contained: the cache and return-contract shapes below are the
Claude-specific realization of the `delegate-agent` family conventions.

For same-session parallel subtasks that share context, use the `Agent` tool directly —
not this skill.

## 1. Invocation

```bash
claude -p "<brief>"
claude -p "<brief>" --add-dir <path> --model sonnet
claude -p "<brief>" --permission-mode plan          # design-only, no edits
claude -p "<brief>" -c                               # continue most recent
claude -p "<brief>" --resume <session-id>
```

Run under a different login by pointing `CLAUDE_CONFIG_DIR` (or the relevant auth env)
at a separate profile before the call — that is the whole point of routing here.

## 2. Model catalog + quota bucket

Bucket: **a Claude subscription** (Max / API), whichever profile the call runs under.

- Aliases: `opus`, `sonnet`, `haiku`. Full slugs (2026-09): `claude-opus-5`,
  `claude-sonnet-5` (default), `claude-haiku-4-5-20251001`, `claude-fable-5`.
- Verify: `/model` in an interactive session, or the claude-api skill.
- `--model <alias|slug>`, `--fallback-model <model>` for auto-downgrade on overload.

## 3. Structured output

```bash
claude -p "<brief>" --output-format json          # single result object with usage + cost
claude -p "<brief>" --output-format stream-json    # NDJSON events
claude -p "<brief>" --output-format json | jq '.result, .total_cost_usd, .usage'
```

## 4. Sandbox / permissions

```bash
claude -p "<brief>" --permission-mode plan                       # no writes
claude -p "<brief>" --allowedTools 'Read' 'Grep' 'Glob'          # read-only analysis
claude -p "<brief>" --permission-mode acceptEdits --add-dir <dir> # allow edits in dir
```

Never pass `--dangerously-skip-permissions` from a delegation.

## 5. Session resume

`claude -p -c` (most recent) or `claude -p --resume <session-id>`; `--from-pr` to
resume a PR-linked session.

## 6. Quota preflight (MANDATORY)

Claude Code exposes no headless rate-limit readout. Cache-first + cost + error
classification:

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
  - Result / stderr shows a usage-limit / "rate limit" / 429 / "Claude usage limit
    reached" message → `available:false`; parse the reset time from the message
    ("resets at 3pm" / an ISO time); if absent use `now + 18000` (5h window).
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

**Cache-first rule:** if `available == false` and `resets_at` is in the future and
`checked_at` is within the last 30 min → return `quota_exceeded` without probing. No
usage percentage — Claude Code gives none headlessly. `resets_at` is parsed from the
limit message ("resets at 3pm" / ISO time) or a `now + 18000` (5h) estimate.
`session_cost_usd` accumulates from each run's `total_cost_usd` for spend awareness.

## 7. Auth check (no secret exposure)

```bash
command -v claude >/dev/null || echo "claude not installed"
claude -p 'ok' --output-format json >/dev/null 2>&1 || echo "claude not authenticated / over limit"
```

Never read `~/.claude/.credentials.json` or other auth files.

## 8. Normalized return contract

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
- `cost_usd` is real, from the JSON result's `total_cost_usd`; `usage` from `usage`.
- `session_id` from the result's `session_id` for `--resume`.
- `files_changed`: `git diff` in the target dir after an `acceptEdits` run.

## 9. Guardrails

- `--permission-mode plan` or a read-only `--allowedTools` set unless edits are required.
- No `commit` / `push` / PR from the delegated process — you integrate and attribute.
- Parallel writing runs each get their own directory / worktree.
- Keep this off the *current* session's quota: always run under a separate profile, or
  it defeats the purpose.
