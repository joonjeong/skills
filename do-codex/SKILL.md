---
name: do-codex
description: Use when delegating a task to the Codex CLI (codex exec) headlessly — precise code generation, multi-file refactor, code review, test authoring, or research using Codex's browser/pdf/spreadsheet plugins. Runs a capability + ChatGPT-quota preflight first.
---

# do-codex — delegate to Codex CLI

Interface adapter for `codex exec`. This skill is the interface only — deciding whether
to delegate and what Codex is good at belongs to the caller or the `do-agent` router.
Self-contained: the cache and return-contract shapes below are the Codex-specific
realization of the `do-agent` family conventions.

## 1. Invocation

```bash
codex exec "<brief>"                    # prompt as arg
printf '%s' "<brief>" | codex exec -    # prompt on stdin
codex exec --skip-git-repo-check -C <dir> "<brief>"
codex exec review --uncommitted "<review instructions>"   # dedicated code review
```

- Working dir: `-C <dir>` (or run from the dir). `--skip-git-repo-check` for non-repos.
- Resume: `codex exec resume --last` or `codex exec resume <session-id>`.

## 2. Model catalog + quota bucket

Bucket: **ChatGPT subscription** (single pool, `limit_id: "codex"`), primary window
plus a possible secondary window.

Current slugs (2026-09): `gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`,
`gpt-5.6-luna` (default here), `gpt-5.3-codex-spark` (coding preview). `--oss` switches
to a local open-source provider (no ChatGPT quota).

- No list command. Verify current models: <https://learn.chatgpt.com/docs/models> or
  `/model` in the interactive TUI.
- Select: `-m <slug>` or `-c model="<slug>"`.
- Reasoning effort: `-c model_reasoning_effort="low|medium|high"` (also extra-high /
  max / ultra in newer builds).

**A slug from the docs is not guaranteed to run on *this* install.** Two gates:
- **CLI version** — a stale `codex` 400s newer slugs with *"requires a newer version of
  Codex"* (e.g. 0.142.5 cannot run `gpt-5.6-*`). `codex --version` vs the docs.
- **ChatGPT plan** — older slugs 400 with *"not supported when using Codex with a
  ChatGPT account"*; the free tier is the most restricted. There may be **no** working
  headless model on a stale CLI + free plan — in that case `do-codex` is unavailable,
  route elsewhere.

The only reliable check is the capability probe in §6.

## 3. Structured output

```bash
codex exec --json "<brief>"                       # JSONL events on stdout
codex exec -o /tmp/last.txt "<brief>"             # final message to a file
codex exec --output-schema schema.json "<brief>"  # enforce final-response shape
```

Parse the last `item_completed` / `AgentMessage` event from `--json` for the final text,
and `token_count` events for `usage` + `rate_limits`.

## 4. Sandbox / permissions

Default is sandboxed. Be explicit:

```bash
codex exec -s read-only "<brief>"        # analysis / review — safest
codex exec -s workspace-write "<brief>"  # allow edits in the workspace
codex exec -s danger-full-access ...     # avoid
```

Never pass `--dangerously-bypass-approvals-and-sandbox` from a delegation.

## 5. Session resume

`codex exec resume --last` continues the most recent session. Capture the session id
from the run for a targeted resume.

## 6. Preflight (MANDATORY)

Two checks, in order: **capability** (can it run at all?) then **quota** (does it have
headroom?).

### 6a. Capability probe

A green rate-limit snapshot is meaningless if the CLI/plan can't run a model. Probe the
exact model you intend to delegate with:

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

- `OK` → capable, continue to 6b.
- `INCAPABLE` → **not a quota problem.** Return `status: "error"`, `reason` = the
  message; route elsewhere. Write `available:false`, `reason`, and a far-future
  `resets_at` (`now + 604800`) to the cache so the router stops re-probing a dead CLI —
  clear it only after `codex update` / a plan change.
- `ERROR` → some other 400; report it, don't retry blindly.
- Try each candidate model once; if none is capable, `do-codex` is unavailable.

(Ignore unrelated stderr noise such as `codex_models_manager::cache: ... missing field`
— match only the signatures above.)

### 6b. Quota probe

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
    # newer builds: resets_at (epoch). older builds: resets_in_seconds (relative).
    resets = w.get("resets_at")
    if resets is None and w.get("resets_in_seconds") is not None:
        resets = int(time.time()) + int(w["resets_in_seconds"])
    return used, resets

pu, pr = win(snap.get("primary"))
su, sr = win(snap.get("secondary"))
reached = snap.get("rate_limit_reached_type")
spend = snap.get("spend_control_reached")
worst = max([x for x in (pu, su) if x is not None], default=None)
# soonest reset among windows that are actually near/over the limit
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

Check **both** windows — `primary` is the short rolling window (5h on Plus/Pro, ~30d on
free), `secondary` is the longer/weekly one. A weekly-limit hit shows only in `secondary`.

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

**Cache-first rule:** read the cache; if `available == false` and `resets_at` is in the
future and `checked_at` is within the last 30 min → return `quota_exceeded` without
probing. Otherwise probe (the snippet above), then overwrite the cache. Also update the
cache after every run: on success record `last_used_percent`; on a rate-limit hit set
`available:false` + `resets_at`. Codex fills all fields because the rollout snapshot
carries `used_percent`, `resets_at`, and `plan_type`.

- The snapshot is only as fresh as your last Codex call. If `reason`'s `snap=` timestamp
  is more than a few hours old, do a **minimal fresh probe** (costs one tiny request,
  not the real task) and read the `rate_limits` from its first `token_count` event:

  ```bash
  codex exec --json --skip-git-repo-check -C /tmp "reply with the word ok" 2>/dev/null \
    | python3 -c "import json,sys;[print(json.dumps(json.loads(l)['payload']['rate_limits'])) for l in sys.stdin if '\"rate_limits\"' in l][-1:]"
  ```

- During the real run, the first `token_count` in `--json` also carries current limits —
  abort and record `quota_exceeded` if it shows ≥100% or `rate_limit_reached_type`.
- `blocked` → return `status: "quota_exceeded"` with `resets_at`, do **not** delegate.

## 7. Auth check (no secret exposure)

```bash
command -v codex >/dev/null || echo "codex not installed"
codex login status  # expect "Logged in using ChatGPT"; summary only — never cat auth.json
```

Fallback if `login status` is unavailable in this build: `test -f ~/.codex/auth.json`.

## 8. Normalized return contract

Print one JSON object as the **last line of stdout** (everything before it is Codex's
own streamed output, kept for logs):

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
- `quota_exceeded` → set `resets_at` from the rate-limit snapshot; `text` explains.
- `error` → capability probe (§6a) failed: stale CLI or plan can't run any model.
  `text` = the 400 message. Route elsewhere; don't retry until `codex update`.
- `auth_error` → `codex login status` not logged in; don't retry.
- `cost_usd` is `null` — ChatGPT-subscription usage is not billed per call.
- Fill `usage` from the final `token_count.total_token_usage`.
- `files_changed`: `git diff` in the target dir after a `workspace-write` run.

## 9. Guardrails

- `-s read-only` unless the brief explicitly needs edits.
- Delegated Codex must not `commit`, `push`, or open PRs — you integrate.
- When you stage the result, use **explicit paths** (`git add <path>...`), never
  `git add -A` / `git add .` — the target tree may already carry unrelated untracked
  files that must not be swept into your commit.
- Parallel Codex runs that write must each get their own directory / worktree.
- Research plugins (browser, pdf, spreadsheets, documents, visualize) must be enabled:
  check `~/.codex/config.toml` `[plugins.*]` blocks. If a routed task needs one and it
  is off, tell the caller rather than silently degrading.
