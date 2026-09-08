---
name: do-council
description: Use when one substantial requirement has several viable approaches and choosing wrong is expensive — convene a panel of different agent CLIs/models that propose, debate across rounds, and vote to a consensus, then turn that consensus into a division-of-labor plan. Feeds do-agent for execution.
---

# do-council — deliberate to a consensus, then split the work

## Overview

One requirement → several agents each propose an approach → they **debate** across
rounds (concede / hold / revise), converging early where they can → they **vote**
per decision → you record the consensus with every dissent → build a division-of-labor
plan from it → (optionally) name an orchestrator → execute via `do-agent`.

This skill runs the deliberation and the planning. Execution mechanics live in
`do-agent` and the `do-<tool>` adapters. **One hop only** — a council member does not
itself convene a council or delegate.

## When to use

- The requirement has **multiple defensible strategies** and the cost of picking the
  wrong one is high (architecture, migrations, repo/tooling design, irreversible calls).
- You want diversity of judgement, not just parallel throughput.

## When NOT to use

- One obvious approach → skip straight to `do-agent`.
- The task needs this session's context and can't be serialized → not delegatable.
- Trivial or urgent work — the deliberation spends 2-5 delegations before anything ships.

## Phase A — deliberate to consensus

### A0. Convene the council

1. **Ask the operator the council size** (default 3, range 2-5). Autonomous mode: 3.
2. **Build the roster** of usable `(adapter, model)` seats. "Usable" means the adapter's
   **capability probe** passes — not just its quota preflight (a green rate-limit means
   nothing if the CLI/plan can't run a model). See each `do-<tool>` skill's preflight.
   - Fill seats by **model-family diversity first**: one per distinct family
     (Codex/GPT, agy/Gemini, Claude, Copilot).
   - Size exceeds available families → fill remaining seats with the **same adapter on a
     different model** (e.g. agy: `gemini-3.1-pro-high` → `gemini-3.8-flash-high` →
     `claude-opus-4-6-thinking` → `gpt-oss-120b-medium`). Never two seats on the
     identical `(adapter, model)`.
   - Fewer than **2** usable seats → stop and report to the operator. No 1-member council.
3. **Assign each seat a random codename** from a neutral category (birds, trees,
   minerals, rivers), no repeats. All debate, the comparison table, and the consensus
   record refer to members **by codename only** — so you weigh arguments, not vendor
   reputation. Keep the codename → `(adapter, model)` map in an operator-only appendix.
4. **Assign each seat a random persona** from `references/personas.md` (the stance the
   member argues from). Include a devil's-advocate seat when the roster allows. If the
   operator requested specific personas, traits, adapters, or models, honor those seats
   first and fill the rest randomly.

### A1. Write the deliberation brief

Same brief to every seat: the requirement, the verified facts, and a **numbered list of
the decision questions** (Q1, Q2, …) — these become the ballot, so make them concrete
and mutually exclusive. Ask for: a position on each question with a one-clause reason,
the single biggest risk, and which slice the member would own. Output a structured
proposal; **do not modify anything** (read-only). Name the paths members may read and
pass repo access (`--add-dir` etc.) to every adapter that supports it — an ungrounded
proposal is worth less, and the grounded seat is the one that finds the structural flaw.

### A2. Round 1 — proposals

One delegation per seat, in parallel, each prefixed with its codename and persona
("You are <codename>. You argue from this stance: <persona>."). A seat that errors or
returns nothing → "no response from <codename>"; continue if ≥2 seats responded.

### A3. Debate rounds

**A Round-1 tally is never the consensus** — even a unanimous Round 1 gets one
adversarial pass so the devil's-advocate seat can attack it.

Each round: send every seat the others' current positions **by codename**, plus the
sharpest unrebutted objection so far. Each seat returns, per question, one of
**CONCEDE** (adopt X's position), **HOLD** (restate why), **REVISE** (new synthesis),
and answers the objection directly.

- **Lock a question** when ≥ (roster − 1) seats hold the same option *and* no new
  unrebutted objection to it was raised that round. Locked questions drop out of
  further debate.
- **Stop** when every question is locked, or the debate-round cap is hit (operator sets
  it; default 3, hard max 10). Converge early whenever possible.

### A4. Round N+1 — the vote

Per question, one ballot. The synthesizer (you) **does not vote**.

- Locked question → record the held option as the result, with the tally.
- Open question → each seat casts one option + one line; **majority wins**. Tie →
  operator rules (interactive) or strongest aggregate rationale then lower cost
  (autonomous).

### A5. Consensus record

Per question: the decided option, the vote tally, the round it locked, and **every
dissent quoted verbatim** (a seat outvoted on Q1 still gets its reason recorded).
Appendix (operator-only): codename → adapter → model → persona, plus a diversity note —
if most seats were one model family, say so and lower the stated confidence.

**Cost**: N seats × (1 proposal + debate rounds + 1 ballot) delegations. Budget for it.

## Phase B — division-of-labor plan

From the consensus, produce the structured plan object in `references/plan-schema.md`:
independent units, a dependency DAG, a `do-agent` Step-2 route (adapter + model) per
unit, a per-bucket quota preflight, an execution pattern per wave, and an integration
order with verification checkpoints. **Each unit cites the consensus decision it
implements.**

## Orchestrator (optional)

For plans with many waves or long parallel runs, name one orchestrator: the in-session
Claude by default, or a separate `do-claude` process for heavy runs. It owns wave
dispatch, result collection, and watching for re-planning triggers. It does **not** own
landing commits (the human / primary orchestrator does) and does not implement units
itself.

## Re-planning triggers

- A unit returns `quota_exceeded` or fails verification (`do-agent` Step 5) → pause,
  report to the operator, wait for a new instruction. No auto-retry.
- A consensus assumption is proven wrong mid-execution → re-run a **targeted** mini-
  deliberation on just that point, not the whole council.

## Anti-patterns

- **Shipping the Round-1 tally** — a 2:1 lead before anyone has rebutted is not a
  decision. Run the adversarial debate pass; it is where the structural flaw surfaces.
- **Deliberation theatre** — fanning out, then ignoring the proposals or the vote.
- **False consensus** — papering over a real conflict instead of putting it to a vote.
- **Over-polling** — 5 seats for a two-approach question.
- **Homogeneous roster** — 4 seats on near-identical models; note it as low confidence.
- **Orchestrator that also implements** — breaks one-hop and the review gate.

## References

- `references/personas.md` — deliberation stances for seat assignment
- `references/plan-schema.md` — the structured division-of-labor plan object
