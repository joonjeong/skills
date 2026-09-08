---
name: do-agent
description: Use when a coding, writing, analysis, or research task could be handed to a different agent CLI — for parallelism, an independent second opinion, Claude quota relief, or a tool's particular strength. Router over do-codex, do-agy, do-copilot, do-claude.
---

# do-agent — delegate work to another agent CLI

## Overview

You (the orchestrator) keep the conversation and own the result. This skill decides
**whether** to delegate, **which** CLI gets it, and **how** to package and integrate
the handoff. The per-CLI mechanics live in the adapter skills:

| Adapter | CLI | Quota source |
|---|---|---|
| `do-codex` | `codex exec` | ChatGPT subscription |
| `do-agy` | `agy -p` (Antigravity) | Google — Gemini bucket + non-Gemini bucket (separate) |
| `do-copilot` | `copilot -p` | GitHub Copilot credits (plan-tiered) |
| `do-claude` | `claude -p` | a *separate* Claude account/quota |

`opencode`, the standalone Gemini CLI, and Hermes `delegate_task` are intentionally
out of scope.

**One hop only.** A delegated agent must not itself delegate. If you were dispatched to
run a delegation (or you are already a subagent), do the work directly — do not invoke
this skill to hand it off again.

## Delegate only when

- The task splits into **independent chunks** you can run in parallel, OR
- You want an **independent second opinion** on a hard diagnosis / design, OR
- A large mechanical job would **burn this session's context**, OR
- Another tool is **clearly better suited** (see `references/task-routing.md`), OR
- **Claude quota is tight** and the work is routine.

## Do NOT delegate when

- The task needs tight, iterative back-and-forth with the user.
- The context lives only in this session and is expensive to serialize.
- It is trivial — handoff overhead exceeds the benefit.
- It touches secrets. Delegated agents must never read `.env`, keys, tokens, or
  credential files, and must never `commit` / `push` / open PRs.

## Step 1 — write the delegation brief

Delegation is one-shot, not a conversation. Hand the adapter a self-contained brief:

```
GOAL:       <one sentence>
REPO/CWD:   <path>, branch <x>, working tree clean|dirty
CONTEXT:    <files to read, by path; constraints; conventions to follow>
TASK:       <numbered, concrete steps>
OUTPUT:     <unified diff | JSON matching schema | written report to stdout>
DO NOT:     touch .env/secrets, commit, push, open PRs, run destructive commands
ACCEPTANCE: <how you will verify the result>
```

Reference files by path — don't paste large blobs. State the output shape explicitly.

## Step 2 — choose an adapter

Resolve in this order:

1. **Caller named a tool** → use that adapter.
2. **Caller named a model** → `references/model-index.md` maps model family/tier →
   adapter. If no adapter can currently serve that model (e.g. the only adapter that
   offers it is quota-exhausted, or a Copilot frontier model on a Pro plan) → **stop
   and report** to the caller: the model, why each candidate can't serve it, and the
   `resets_at` where relevant. Do not silently substitute a different model.
3. **Caller named only a task type** → `references/task-routing.md` (default opinion,
   caller-overridable) picks a 1st and 2nd choice.
4. **Nothing specified** → you decide from the task; prefer the cheapest adapter that
   clears the quality bar, and spread load off Claude when quota is tight.

If the pick is `do-claude` and you are already running as Claude: still delegate, via
`do-claude` as a **separate process** (that is the point — it keeps this session's
context and quota free). Only skip delegation when the task genuinely needs this
session's context — but then it fails the "Do NOT delegate when" test anyway.

## Step 3 — quota-aware selection

Before delegating, the chosen adapter runs its **preflight** — each `do-<tool>` skill
has a "Preflight" section covering capability (can the CLI/plan run a model at all?) and
quota (does the bucket have headroom?), plus its own cooldown-cache shape. All caches
live under `~/.cache/do-agent/` and are cache-first (a recent `available:false` with a
future `resets_at` short-circuits without probing). `references/conventions.md`
summarizes the union of return fields the router parses.

- Preflight says **available** → proceed.
- Preflight says **quota_exceeded** → don't delegate to it now. Fall back to the 2nd
  choice, or report back to the caller with the `resets_at` and the alternatives.
- Preflight says **error** (capability probe failed — stale CLI, plan can't run a
  model) → treat that adapter as unavailable until fixed; fall back or report.
- **No candidate adapter is available** (all `quota_exceeded` / `error`) → stop and
  report to the caller: which buckets are exhausted, which tools are broken, and each
  `resets_at`. Do not do the work yourself as a fallback and do not sit and wait —
  hand the decision back.

When you have 2+ viable adapters, prefer the one whose bucket has the most headroom —
this is how idle subscription quota gets used.

## Step 4 — execute

| Pattern | Use |
|---|---|
| **One-shot consult** | Second opinion. Capture stdout, do not apply, compare to your own reasoning. |
| **Parallel fan-out** | Independent chunks. Run N adapters as background jobs; if they write files, give **each its own worktree/dir**. Collect, then synthesize. |
| **Redundant / compare** | Risky change. Same brief to 2 adapters, diff the outputs, pick or merge. |
| **Draft → review** | One adapter drafts; you review and integrate. |
| **Background long-runner** | Kick off, poll, resume (each adapter documents its resume flag). |

## Step 5 — integrate the result

Never blind-apply external output.

1. Review the diff / report yourself. Scan for a **gamed check**: weakened assertions,
   removed or `skip`-marked tests, broadened `except`, TODO stubs, hard-coded return
   values. A delegate's "tests pass" is a claim, not evidence.
2. Run the project's verification (build, tests, linters) yourself — evidence before
   claims.
3. **Verification passes** → attribute (`Assisted-by: <tool> (<model>)` in the
   commit/PR body) and **you** land the work. The delegated agent has no
   commit/push/PR rights; stage with explicit paths, never `git add -A`.
4. **Verification fails, or step 1 found a gamed check** → do **not** auto-retry,
   auto-resume, or re-delegate. Report to the operator: the delegate's diff, the exact
   verification output, and what you found. Wait for a new work instruction. Keep the
   failed attempt available (a branch or a saved diff) so the re-instruction can build
   on or discard it.

## Environment split

- **Local Claude Code**: call the CLIs directly. `codex:rescue` / `gemini:rescue`
  plugin skills remain a convenience layer for interactive rescue; this skill is the
  vendor-neutral playbook.
- **Hermes node**: the CLIs are installed per node. Obey the worktree rules
  (`resistance-worktree/{task}`). Results flow operator → synthesis → Discord/Issue,
  never straight to `main`.

## References

- `references/model-index.md` — model family/tier → adapter (model names are volatile)
- `references/task-routing.md` — task type → adapter (default opinion)
- `references/conventions.md` — union return contract the router parses; each
  `do-<tool>` skill carries its own tool-specific cache + contract inline
