---
name: do-copilot
description: Use when delegating a task to GitHub Copilot CLI (copilot -p) headlessly — GitHub-native chores, or model routing across the Copilot plan tier. Runs a credit/plan preflight via copilot billing first.
---

# do-copilot — delegate to GitHub Copilot CLI

Interface adapter for `copilot -p`. This skill is the interface only — deciding whether
to delegate and what Copilot is good at belongs to the caller or the `do-agent` router.
Self-contained: the cache and return-contract shapes below are the Copilot-specific
realization of the `do-agent` family conventions.

## 1. Invocation

```bash
copilot -p "<brief>" --allow-all-tools          # non-interactive REQUIRES this (or scoped --allow-tool)
copilot -p "<brief>" -C <dir> --add-dir <path>
copilot -p "<brief>" --allow-tool='shell(git:*)' --deny-tool='shell(git push)'
copilot -p "<brief>" --continue                 # resume most recent
copilot -p "<brief>" --resume <sessionId>
```

`-s/--silent` prints only the final agent response (no progress).

## 2. Model catalog + quota bucket

Bucket: **Copilot AI credits**, plan-tiered. `--model auto` is the safe default; there
is no list command (github/copilot-cli#700).

| Plan | Access | Monthly credits |
|---|---|---|
| Free / Pro ($10) | `--model auto` only; mid-tier models. No Opus / frontier. | $15 |
| Pro+ ($39) | + Opus 4.7/4.8/5, Fable 5/5.1, GPT-5.4–5.6, Grok 4.5/4.6, Kimi K2.7/K3 | $70 |
| Business / Enterprise / Max | Pro+ models + priority | 1,900 / 3,900 / 20,000 |

- Explicit model: `--model <name>` (e.g. `claude-sonnet-4.6`, `gpt-5.6`), only if the
  plan allows it — otherwise the call fails or silently downgrades.
- Verify current names: <https://docs.github.com/copilot/reference/ai-models/supported-models>
- Context window: `--context long_context` for large inputs.

## 3. Structured output

```bash
copilot -p "<brief>" --output-format json          # JSONL, one object per line
copilot -p "<brief>" --usage-output-file usage.json # final usage stats as JSON
```

## 4. Sandbox / permissions

Non-interactive needs broad permission grants — scope them:

```bash
copilot -p "<brief>" \
  --allow-tool='write' --allow-tool='shell(git status)' --allow-tool='shell(git diff)' \
  --deny-tool='shell(git push)' --deny-tool='shell(git commit)'
```

Prefer scoped `--allow-tool` over `--allow-all-tools`. Add `--allow-url` only for the
specific domains the task needs. `--assisted-approval` adds a safety judge.

## 5. Session resume

`copilot -p --continue` (most recent) or `--resume <sessionId>` / `--connect[=id]`.

## 6. Quota preflight (MANDATORY)

```bash
mkdir -p ~/.cache/do-agent
copilot billing 2>/dev/null > /tmp/do-copilot-billing.txt   # plan + AI credit balance
```

- Parse `copilot billing` for the plan tier and remaining credits/pool. If it reports
  the pool exhausted (or very low relative to the task) → `quota_exceeded`.
- If a previous run wrote `usage.json` via `--usage-output-file`, fold it into the
  running estimate.
- Cap each delegated session: `--max-ai-credits <n>`. When the cap is hit the CLI
  blocks the next model call and the run ends — classify that as `quota_exceeded`.
- If `copilot billing` is unavailable non-interactively, fall back to cache-first +
  error classification, and use a `now + 86400` cooldown on a hard credit-exhaustion
  error (the pool resets monthly).

### Cooldown cache — `~/.cache/do-agent/copilot.json`

```json
{
  "tool": "copilot",
  "available": true,
  "reason": "",
  "checked_at": 1789000000,
  "resets_at": null,
  "plan": "pro",
  "credits_remaining": 12.5
}
```

**Cache-first rule:** if `available == false` and `resets_at` is in the future and
`checked_at` is within the last 30 min → return `quota_exceeded` without probing.
Otherwise run `copilot billing`, refresh `plan` + `credits_remaining`, overwrite the
cache. `plan` is required — the `do-agent` router uses it to apply the Pro+ model gate.
`credits_remaining` comes from `copilot billing`; `resets_at` is the monthly reset date
when known.

## 7. Auth check (no secret exposure)

```bash
command -v copilot >/dev/null || echo "copilot not installed"
gh auth status >/dev/null 2>&1 || true      # Copilot rides the gh / device login
copilot billing >/dev/null 2>&1 || echo "copilot not authenticated"
```

Never read files under `~/.copilot/` (contains `settings.json`, session db, tokens).

## 8. Normalized return contract

Print one JSON object as the **last line of stdout**:

```json
{
  "tool": "copilot",
  "model": "auto",
  "quota_bucket": "copilot",
  "status": "ok",
  "resets_at": null,
  "text": "<final agent response>",
  "files_changed": "<unified diff, path list, or null>",
  "session_id": "<sessionId or null>",
  "usage": { "input": 1234, "output": 567, "credits_used": 0.4, "plan": "pro" },
  "exit_code": 0
}
```

- `status` ∈ `ok | quota_exceeded | auth_error | error`.
- `usage.credits_used` from `--usage-output-file`; `usage.plan` from the preflight.
- `model` is `"auto"` unless an explicit `--model` was used (and the plan allowed it).
- `files_changed`: `git diff` in the target dir when `write` was allowed.

## 9. Guardrails

- Scoped `--allow-tool` / `--deny-tool`; never a blanket `--allow-all-urls`.
- Explicitly deny `git commit` / `git push` — you integrate and attribute.
- Parallel writing runs each get their own directory / worktree.
- Don't request a model the current plan can't serve; check the preflight `plan` first.
