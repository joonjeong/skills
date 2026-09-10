# delegate-agent — union return contract

Each `do-<tool>` adapter is self-contained: its SKILL.md carries its own "Quota
preflight" cooldown-cache shape and its own return-contract example, specialized to what
that CLI actually exposes. This file is the router's reference for the **union** of
fields, so it can parse any adapter's output uniformly.

## Cooldown caches

All under `~/.cache/do-agent/`. One file per quota pool:

| Adapter | Cache file(s) | Notes |
|---|---|---|
| `do-codex` | `codex.json` | has `last_used_percent`, `plan`, real `resets_at` (from rollout snapshot) |
| `do-agy` | `agy-gemini.json`, `agy-nongemini.json` | per bucket; no usage percent |
| `do-copilot` | `copilot.json` | has `plan`, `credits_remaining` (from `copilot billing`) |
| `do-claude` | `claude-<profile>.json` | per profile; `session_cost_usd`; no usage percent |

Common fields: `tool`, `available` (bool), `reason`, `checked_at` (unix s),
`resets_at` (unix s or null).

**Cache-first rule (every preflight):** if `available == false` and `resets_at` is in
the future and `checked_at` is within the last 30 min → treat as `quota_exceeded`
without probing. Otherwise probe, then overwrite the cache. Update the cache after every
run (success and failure).

## Normalized return contract

The adapter prints one JSON object as the **last line of stdout**; earlier lines are the
tool's own streamed output (kept for logs).

```json
{
  "tool": "<codex|agy|copilot|claude>",
  "model": "<model id or 'auto'>",
  "quota_bucket": "<chatgpt | gemini | non-gemini | copilot | claude:<profile>>",
  "status": "<ok | quota_exceeded | auth_error | error>",
  "resets_at": "<unix seconds when quota_exceeded, else null>",
  "text": "<final assistant message>",
  "files_changed": "<unified diff, path list, or null>",
  "session_id": "<resume handle or null>",
  "usage": {
    "input": 0,
    "output": 0,
    "cost_usd": "<number for claude; null for codex/agy>",
    "credits_used": "<number for copilot only>",
    "plan": "<string for copilot only>"
  },
  "exit_code": 0
}
```

- `quota_exceeded` → `resets_at` set when known; `text` explains; router falls back or
  reports the reset time to the caller.
- `auth_error` → tool not logged in; do not retry, tell the user.
- `error` → tool ran but failed; `text` carries the message, `exit_code` non-zero.
