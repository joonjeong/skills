---
name: interview-local
description: Use when a project checkout has no AGENTS.local.md (or the operator's subscriptions/roles changed) — detect the repo's build/test/module layout, interview the operator, and generate a gitignored AGENTS.local.md plus .agents/roster.yaml that tell the orchestrator which executors (claude, codex, copilot, agy) exist, what each may do, and where parallel work may split. Feeds divide-and-conquer and delegate-agent.
---

# interview-local — build the local orchestration config for this checkout

## Overview

Shared rules live in the committed `AGENTS.md`. **Who is available to do the work**
(subscriptions, roles, risk zones, parallelism cap) is personal and changes over
time, so it must not be committed. This skill interviews the operator once per
checkout and writes that answer to gitignored files:

```
AGENTS.local.md       human-readable rules — the source of truth
.agents/roster.yaml   machine-readable roster the orchestrator parses
CLAUDE.local.md       one line: @AGENTS.local.md   (Claude Code entry point)
GEMINI.local.md       one line: @AGENTS.local.md   (only if agy/gemini is in the roster)
```

Each tool reads a different filename, so the content lives in one file and the rest
only point at it.

**One hop only.** If you were dispatched as a worker, do not run this skill — read
`AGENTS.local.md` and follow it.

## When to use

- `AGENTS.local.md` is missing at the repo root. The committed `AGENTS.md` should say
  so: *"If AGENTS.local.md is absent, run interview-local before starting work."*
- The operator says a subscription was added or dropped, or roles should change.
- A new worktree was created (Step 0 copies the config instead of re-interviewing).

## When NOT to use

- The task is trivial and needs no delegation.
- `AGENTS.local.md` exists and nothing changed — just read it.
- You were dispatched as a subagent.

## Step 0 — existing config

1. If `AGENTS.local.md` exists: show a 5-line summary and ask whether to keep it,
   edit it, or redo it. Never overwrite silently.
2. If this is a **linked worktree** (`git rev-parse --git-common-dir` differs from
   `--git-dir`) and the main checkout has the files: copy them, tell the operator,
   stop.

## Step 1 — detect (do not ask what you can read)

Collect facts from the repo, then present them as defaults to confirm:

| Fact | Where to look |
|---|---|
| Language / build | `Cargo.toml`, `package.json` (+ lockfile → package manager), `pyproject.toml`, `go.mod`, `mise.toml` |
| Test / lint commands | `Makefile`, `justfile`, `mise.toml` tasks, `lefthook.yml`, CI workflow files |
| Split candidates | workspace members (`crates/*`, `apps/*`, `packages/*`), top-level `src/` dirs |
| Existing rules | `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md` — read, do not duplicate |
| Installed executors | `command -v claude codex copilot agy gemini` |

An executor that is installed is only a *candidate*; the operator confirms whether
they actually have a working subscription.

## Step 2 — interview

Use `AskUserQuestion`, at most 4 questions per call, options pre-filled from Step 1.
Keep to the questions below; skip any already answered by the repo.

**Round 1 — executors**
1. Which executors are usable? (multi-select: claude, codex, copilot, agy) and the
   plan tier of each, as free text.
2. Who orchestrates by default, and who takes over if that executor is exhausted?
3. Which executor implements, which reviews? (Rule of thumb offered as default:
   a different executor reviews than the one that implemented.)

**Round 2 — project shape**
4. Confirm build / test / lint commands from Step 1.
5. Confirm the split units — directories that parallel workers may own exclusively.
6. Risk zones workers must not touch or that always need review (e.g. order
   execution, auth, migrations, secrets).
7. Max concurrent workers (default 3).

**Round 3 — conventions**
8. Worktree location and branch naming (default `.worktrees/<unit>`, `wt/<unit>`).
9. Personal hard rules (e.g. "never commit or push without being told").

**Do not ask about quota headroom.** It goes stale within days. `roster.yaml`
records *what exists*; remaining capacity is checked at dispatch time by each
adapter's preflight (`do-codex`, `do-copilot`, `do-agy`, `do-claude`).

## Step 3 — generate

Fill the templates in `references/templates.md`. Rules:

1. Write `.agents/roster.yaml` and `AGENTS.local.md` from the same answers so they
   cannot disagree.
2. Create `CLAUDE.local.md` (and `GEMINI.local.md` if applicable) containing only
   `@AGENTS.local.md`. If such a file already exists with other content, append the
   import line instead of replacing it.
3. Add these lines to `.gitignore` if absent: `AGENTS.local.md`, `CLAUDE.local.md`,
   `GEMINI.local.md`, `.agents/`. Do not reorder or reformat existing entries.
4. Never write secrets, tokens, account emails, or plan prices into any file.

## Step 4 — confirm and verify

1. Print a one-screen summary: active executors and roles, split units, risk zones,
   worker cap, fallback. Ask the operator to approve or correct it. Apply
   corrections and re-print; do not proceed on an unconfirmed roster.
2. Verify the files: `roster.yaml` parses (`python3 -c 'import yaml,sys; yaml.safe_load(open(sys.argv[1]))' .agents/roster.yaml`),
   the gitignore entries are present, and `git status` shows none of the generated
   files as untracked.
3. Do **not** commit anything.

## Consumers

The orchestrator (any executor acting in that role) reads `.agents/roster.yaml`
before decomposing work:

- only executors listed there may receive units;
- `risk_zones` force direct handling or mandatory review;
- `split_units` bound each worker's writable paths, and no two concurrent workers
  may share one;
- `max_workers` caps the fan-out; the rest queue;
- `fallback_orchestrator` takes over when the primary's preflight reports exhaustion.

`divide-and-conquer` and `delegate-agent` do not read this file yet. Until they are
updated, the orchestrator must apply the list above by hand.

## Anti-patterns

- **Interviewing for facts the repo already states** — detect first, confirm second.
- **Recording quota or remaining credits** — stale immediately; use adapter preflight.
- **Committing the local files** — they hold personal subscription and role data.
- **Letting `roster.yaml` and `AGENTS.local.md` drift** — generate both from one pass,
  and on any edit regenerate both.
- **Re-interviewing every worktree** — copy from the main checkout (Step 0).
- **Trusting an unconfirmed roster** — a wrong answer becomes wrong routing everywhere.

## See also

`divide-and-conquer` (decompose and route), `delegate-agent` (dispatch to a CLI),
`do-council` (when the approach itself is unresolved).

## References

- `references/templates.md` — `roster.yaml` and `AGENTS.local.md` templates.
