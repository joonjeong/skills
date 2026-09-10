---
name: divide-and-conquer
description: Use when a requirement is large enough to split into independent work units of differing difficulty — decompose it, classify each unit by difficulty and repetition pattern, route each to the cheapest capable executor (a Claude subagent tier or an external CLI via delegate-agent), run them in parallel where independent, and integrate. No approach debate — for that use do-council.
---

# divide-and-conquer — split a requirement, route by difficulty, execute

## Overview

You (the orchestrator) own the result. This skill turns one requirement into
independent work units, classifies each by how hard and how repetitive it is, routes
each to the cheapest executor that clears the bar, runs them, and integrates the
pieces. It does **not** decide *which approach* to take — if the strategy is genuinely
uncertain, use `do-council` first, then bring its plan here.

**One hop only.** A unit's executor does not itself decompose or re-delegate. If you
were dispatched to run a unit, do the work directly.

## When to use

- The requirement splits into **3 or more independent units**.
- The units **vary in difficulty** — some are mechanical or repetitive, some are hard.
- Spreading the work across cheaper executors (or off the Claude quota) is a win.

## When NOT to use

- One indivisible task — nothing to decompose.
- The approach itself is unresolved → `do-council`.
- The work needs tight iterative back-and-forth with the user.
- It is trivial — orchestration overhead exceeds the benefit.

## Step 1 — Decompose

Break the requirement into units where each one:

- has **one clear purpose**,
- has an **explicit interface** — what it takes in, what it produces,
- is **independently testable**.

Draw the dependency DAG. Mark each edge: which units are independent (can run in
parallel) and which must wait for another's output. Apply YAGNI — drop any unit that
does not serve the stated goal.

## Step 2 — Classify

Rate every unit on two axes.

**Difficulty**

| Level | Signals |
|---|---|
| `trivial` | Mechanical edit, one file, no design choices, obvious correct answer. |
| `routine` | Standard coding against a known pattern already in the repo. |
| `hard` | Non-obvious logic, cross-cutting change, or an unfamiliar subsystem. |
| `novel-design` | The interface or approach has to be invented; getting it wrong is expensive. |

**Repetition pattern**

| Pattern | Meaning |
|---|---|
| `one-off` | A single distinct piece of work. |
| `templated-repeat` | The same transformation applied across N items. |
| `boilerplate` | Scaffolding or wiring with a fixed, well-known shape. |

## Step 3 — Route

Pick the cheapest executor that clears the bar for each unit.

| Unit profile | Cheapest capable executor |
|---|---|
| `boilerplate` · `templated-repeat` · `trivial` | Claude Haiku subagent — or `do-agy` (fast/cheap) / `do-codex` (fast/cheap) via `delegate-agent` |
| `routine` coding | Claude Sonnet subagent — or `do-codex` (balanced) via `delegate-agent` |
| `hard` · `novel-design` | Claude Opus subagent — or `do-claude` / `do-codex` (top tier) via `delegate-agent` |

Concrete model slugs churn monthly — take them from
`delegate-agent/references/model-index.md`, never hard-code them here.

**In-session subagent vs external CLI.** Default to an in-session subagent: it is
simpler and shares this session's context. Reach for an external CLI via
`delegate-agent` only when:

- Claude quota is tight, or
- you want a second model's take for a compare, or
- the unit would burn this session's context (large mechanical job).

## Step 4 — Execute

- **Independent units** run in parallel — an Agent-tool fan-out, or background `do-*`
  jobs. Any unit that writes files gets its **own worktree or directory** so parallel
  writes cannot collide.
- **Sequential units** run in DAG order, each fed the outputs of the units it depends
  on.

Give every unit a self-contained brief:

```
GOAL:       <one sentence>
CONTEXT:    <files to read, by path; conventions to follow>
TASK:       <numbered, concrete steps>
OUTPUT:     <diff | file(s) | report to stdout — state the shape>
DO NOT:     touch .env/secrets, commit, push, open PRs
ACCEPTANCE: <how the result will be checked>
```

## Step 5 — Integrate

1. Review each unit's output **yourself**. Scan for a gamed check — weakened
   assertions, skipped or deleted tests, broadened `except`, hard-coded return values,
   TODO stubs. A unit's "it works" is a claim, not evidence.
2. Run the project's verification (build, tests, linters) **yourself**.
3. Assemble the units in DAG order; resolve interface mismatches at the seams.
4. **On failure** — do not auto-retry, auto-resume, or re-delegate. Report to the
   operator: the unit's output, the exact verification failure, and what you found.
   Keep the failed attempt available so the re-instruction can build on it.

## Anti-patterns

- **Over-decomposition** — ten units for a two-file change. The overhead swamps the
  work.
- **Routing everything to the top tier "to be safe"** — that throws away the entire
  point of classifying.
- **Decomposing an unresolved approach** — that is `do-council`'s job, not this one.
- **"Parallel" units that share state** — they will produce merge conflicts. If they
  touch the same files, they are sequential.
- **Blind-assembling** subagent output without reviewing or verifying it.

## See also

`red-team-blue-team` to harden one risky unit; `distill-and-structure` for a legibility
pass on a prose deliverable.

## References

None — the classification and routing tables above are the skill.
