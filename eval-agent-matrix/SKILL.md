---
name: eval-agent-matrix
description: Use when deciding or re-checking which coding-agent CLI and model (agy, codex, claude, copilot × subscription tier) can do which kind of task and how well — before changing delegate-agent routing tables, after a CLI or model-catalog update, or when a route keeps failing.
---

# eval-agent-matrix — measure (adapter × model × task) before routing

Routing tables in `delegate-agent/references/` are opinions until measured. This skill
runs a fixed task suite headlessly through each adapter/model pair and records
pass/fail, wall time, and failure class, so routing changes cite evidence.

A cell's result depends on **three** things — record all of them:
the subscription (which models the plan exposes), the CLI agent (its tools, edit and
permission mechanics, version), and the model. The same model can pass on one CLI and
fail on another.

## Task suite (`tasks/`)

| Task | Category (maps to task-routing rows) | Scoring |
|---|---|---|
| `bugfix` | simple code fix | auto: unit tests pass, test file untouched |
| `multi-file-rename` | multi-file refactor | auto: tests pass, no leftover name |
| `json-extract` | structured extraction | auto: exact JSON match (corrections, duplicates, currency) |
| `long-context-trace` | large-context repo trace | auto: 300-module generated maze with decoys; exact answer |
| `pr-narrative` | reviewer-facing prose | judge: `rubric.md`, 0–10, blind |

Each task dir: `prompt.md`, `fixture/`, `check.sh <workdir> <taskdir> <hidden-answer>`,
`meta.json`. Add a task by copying that shape; verify `check.sh` **fails** on the
untouched fixture and **passes** on a hand-made correct answer before using it.

## Run

1. **Confirm budget with the operator first.** Every cell spends real quota. State the
   cells (adapters × models × tasks) and ask. Default plan: the models currently named in
   `delegate-agent/references/model-index.md`, all tasks.
2. Preflight each adapter (its `do-<tool>` skill's auth/quota section). Skip
   `quota_exceeded` adapters; don't burn retries.
3. Run cells — independent, so run them as parallel background jobs:
   ```bash
   python3 scripts/run.py <agy|codex|claude|copilot> <model> <task> [--timeout 900]
   ```
   Each call copies the fixture to a temp dir, runs the CLI's headless edit mode, runs
   the checker, and appends one JSON line to `results/runs.jsonl`.
4. Judge `needs_judge` cells yourself or via a different-family model: read
   `<run_dir>/work/PR.md` without the adapter name, score with `rubric.md`, and write
   `score` into that row.
5. `python3 scripts/summarize.py --since <YYYYMMDD>` → markdown matrix. Save it as
   `results/<date>-matrix.md` with the CLI versions and the plan tier of each subscription.

## Reading results

| Status | Meaning | Routing implication |
|---|---|---|
| `pass` / `fail` | checker verdict | capability + quality signal |
| `timeout` | exceeded `--timeout` | too slow for this category, or hung on a prompt |
| `quota_exceeded` / `auth_error` | not a quality signal | exclude cell; rerun later |
| `error` | CLI missing / broken | adapter unavailable on this machine |

- **One run is one sample.** Run 3 reps per cell before demoting a route; flaky = mixed results.
- **Ceiling effect:** if every cell passes a task, it no longer discriminates — add a
  harder variant instead of concluding "all equal".
- Compare wall time only within a category.

## Feeding routing

Propose `task-routing.md` / `model-index.md` diffs citing the matrix file
(`evidence: results/<date>-matrix.md`). Apply only with operator approval — usually via
`refresh-agent-routing`.

## Common mistakes

- Treating `quota_exceeded` as a failure of the model.
- Changing a route from a single run.
- Letting the agent see the expected answer (hidden answers live outside the workdir).
- Comparing cells run on different CLI versions without noting it.
