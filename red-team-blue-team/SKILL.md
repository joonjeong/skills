---
name: red-team-blue-team
description: Use when a work product must be hardened against defects before it ships and one review pass isn't enough — run an adversarial loop of an aggressive builder (blue) and a conservative critic (red), iterating build/critique/revise until the critic raises zero blocking issues or the round cap is hit. Teams default to Claude subagents; scale to external CLIs via delegate-agent for large or high-risk work.
---

# red-team-blue-team — adversarial build-and-critique loop

## Overview

Blue builds. Red attacks. You (the operator) own the loop and the result. Blue produces
complete drafts with a bias to action; red reviews conservatively, assuming defects
exist. They iterate build → critique → revise until red has no blocking findings, or a
round cap stops the loop.

**One hop only.** A blue or red team member does not itself run a red-team-blue-team
loop or delegate further. If you were dispatched as blue or red, do that job directly.

## When to use

- A **high-stakes deliverable** — a migration, security-sensitive code, or a spec other
  people will depend on.
- **Correctness matters more than speed** on this piece.
- A single review pass has historically let defects through.

## When NOT to use

- Low-stakes work — the loop's cost is not repaid.
- Time-critical work.
- The requirement itself is unclear — brainstorm it first.
- Trivial changes.

## Step 0 — Configure the teams

Default: **blue = one Claude subagent, red = one Claude subagent**, each with a distinct
persona prompt from `references/personas.md`.

Scale up when the surface is large, the risk is high, or you want model diversity: make
blue and/or red **external CLIs via `delegate-agent`** (e.g. blue = `do-codex`, red =
`do-claude`). Use **multiple blues** to build independent parts in parallel, **multiple
reds** to apply different lenses (correctness, security, readability). Model slugs come
from `delegate-agent/references/model-index.md`.

- **Blue** — bias to action, produce a complete draft, do not sandbag.
- **Red** — conservative, adversarial, assume defects exist, separate `BLOCKING` from
  the rest, never rubber-stamp, actively hunt for gamed checks.

## Step 1 — Blue builds

Hand blue a self-contained brief (goal, context by path, task steps, output shape, DO
NOT list, acceptance criteria). Blue returns a **complete draft** plus a short
**self-assessment** naming its own weak spots.

## Step 2 — Red critiques

Red reviews the draft — and blue's self-assessment, treating the named weak spots as
leads, not absolution — against the requirement and its acceptance criteria. Every
finding is tagged and carries a concrete failure scenario:

| Tag | Meaning |
|---|---|
| `BLOCKING` | Ships a defect. Must be resolved before the loop can terminate. |
| `SHOULD` | Real weakness, not a blocker. Fix if cheap. |
| `NOTE` | Observation or nitpick. |

"Tests pass" is a claim — red runs the verification, or asks for the evidence.

## Step 3 — Revise

Blue addresses **every `BLOCKING` finding** — either fixes it, or argues back with
reasoning for the next round's red to adjudicate. You arbitrate genuine deadlock (blue
and red both holding, with reasons) so the loop cannot spin forever.

## Step 4 — Terminate

One round = one red critique plus blue's revision; blue's initial build is round 0.

Stop when **either**:

- Red returns **zero open `BLOCKING` findings** — a finding the operator has arbitrated
  in blue's favour is closed; record the dismissal — **or**
- The **round cap** is hit. The operator sets it; default **3**, hard max **6**.

If the cap is hit with `BLOCKING` findings still open: **stop and report to the
operator** — the remaining findings, blue's last draft, and red's last review. **Do not
ship.**

## Step 5 — Integrate

You review the final artifact yourself, run the project's verification, and land it. If
external CLIs were used, attribute them (`Assisted-by: <tool> (<model>)` in the commit
body). Team members have no commit/push/PR rights.

## Anti-patterns

- **A red that rubber-stamps** — the loop then proves nothing.
- **A red with no `BLOCKING` / non-blocking distinction** — everything blocks, the loop
  never terminates.
- **Blue and red on the identical model and prompt** — no real adversarial tension. At
  minimum give them distinct personas.
- **An uncapped loop.**
- **An operator that only forwards messages** — someone has to arbitrate deadlock.
- **Running this on an unclear requirement** — brainstorm first.
- **Shipping on a cap hit** with unresolved `BLOCKING` findings.

## See also

`divide-and-conquer` to split a large requirement into units first;
`distill-and-structure` for a legibility pass on the final prose.

## References

- `references/personas.md` — the blue and red system prompts.
