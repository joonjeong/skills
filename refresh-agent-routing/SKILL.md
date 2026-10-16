---
name: refresh-agent-routing
description: Use when a session-start notice reports coding-agent CLI or model-catalog changes (agy, codex, claude, copilot), when a subscription plan changes, or when the operator asks to re-check model routing for delegate-agent.
---

# refresh-agent-routing — re-tune routing after agent/model changes, with consent

Agent CLIs and model catalogs change monthly. Stale routing sends work to dead or
outdated models. This skill turns a detected change into an **operator decision**, then
into evidence-backed edits to the routing tables.

Detection: `scripts/fingerprint.py check` diffs CLI versions and `agy models` against the
last acknowledged state (`~/.cache/do-agent/agent-fingerprint.json`). A SessionStart hook
runs `fingerprint.py check --hook` at most once a day and prints a notice only on change.

## Steps

1. **Show the change and ask.** Present the diff (run `fingerprint.py check` if you only
   have the hook notice) and ask the operator, with these options:
   - **Review now** — continue to step 2.
   - **Later** — do nothing; the notice reappears next day.
   - **Ignore this change** — run `fingerprint.py ack`; stop.
   Do not edit anything before the operator chooses "Review now".
2. **Classify impact** of each change:

   | Change | Impact |
   |---|---|
   | model removed | **breaking** — every table row naming it is dead |
   | model added | opportunity — candidate for a tier/row |
   | CLI major/minor version | check changelog (`agy changelog`, release notes) for flag, mode, permission changes |
   | CLI patch only | usually none — say so and offer `ack` |

3. **Find stale references** across the adapters and router:
   `grep -rn "<old slug>" ~/.config/skillshare/skills/{delegate-agent,do-*,do-council,divide-and-conquer,red-team-blue-team}`.
4. **Propose, don't apply.** For each affected skill, show the exact edit: adapter
   catalog (`do-<tool>` model section, invocation flags) and router tables
   (`delegate-agent/references/model-index.md`, `task-routing.md`).
   - Breaking slug swaps can be proposed directly.
   - **Re-ranking** a route (new 1st choice, new tier) requires evidence: offer an
     `eval-agent-matrix` run scoped to the changed adapter's models, with its quota cost.
     **REQUIRED SUB-SKILL:** use eval-agent-matrix for that run.
5. **Apply on approval**, then `skillshare sync`, then `fingerprint.py ack`.
   Update snapshot dates in the edited tables and cite the matrix file for re-ranked rows.
6. Report: what changed, what was edited, what was left as-is and why. No commit/push
   unless asked.

## Quick reference

```bash
S=~/.config/skillshare/skills/refresh-agent-routing/scripts/fingerprint.py
python3 $S check      # show diff vs acknowledged state
python3 $S ack        # accept current state (after review or explicit ignore)
```

## Common mistakes

- Editing tables before asking — the operator may be mid-task.
- Re-ranking a route from changelog marketing instead of an eval run.
- Forgetting `ack` → the notice repeats daily.
- Treating `claude.version` bumps (frequent) as routing-relevant without reading what changed.
