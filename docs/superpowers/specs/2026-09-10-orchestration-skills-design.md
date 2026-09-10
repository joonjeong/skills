# Orchestration skills: divide-and-conquer, red-team-blue-team, distill-and-structure

**Date**: 2026-09-10
**Status**: Approved design, pending implementation plan
**Scope**: Three new personal skills + a rename of the `do-agent` router to `delegate-agent`

---

## 1. Goal

Add three orchestration skills to the personal `skillshare/skills` repo, in the same
house style as the existing `do-*` family:

| Skill | One line | Quality axis it serves |
|---|---|---|
| `divide-and-conquer` | Decompose a requirement into independent work units, classify each by difficulty and repetition pattern, route each to the cheapest capable executor, run them, integrate. | Throughput / cost |
| `red-team-blue-team` | Harden a work product through an adversarial loop: an aggressive builder (blue) and a conservative critic (red) iterate build/critique/revise to a termination condition. | Correctness / robustness |
| `distill-and-structure` | Diagnose a prose deliverable's legibility and propose a concrete restructuring (revised outline + specific edits) using top-down pyramid and bottom-up synthesis. Reviews and proposes; does not rewrite. | Deliverability / comprehension |

Plus a preliminary rename: `do-agent` -> `delegate-agent` (router only; adapters keep
`do-*` names).

The three skills are **independent**: no skill invokes another. A human composes them.

## 2. Approach

**Chosen: three self-contained skills, no shared infrastructure** (brainstorming
approach A). Each `SKILL.md` stands alone. `divide-and-conquer` and `red-team-blue-team`
each inline their own "Claude subagent tier vs external CLI adapter" dispatch logic
rather than sharing a reference. Volatile information (model slugs) is *referenced*, not
copied, from `delegate-agent/references/model-index.md`.

Rejected:

- **Shared dual-dispatch reference** — creates a cross-skill dependency; the decision
  table is small enough to inline.
- **Thin wrappers over `delegate-agent` / `do-council`** — contradicts the decision
  that `divide-and-conquer` is a standalone skill, not absorbed into the router.

## 3. Common conventions (all three skills)

Follow the existing `do-*` house style:

- **Location**: directories at repo root — `divide-and-conquer/`,
  `red-team-blue-team/`, `distill-and-structure/`.
- **`SKILL.md` frontmatter**: `name` + `description` only. No `metadata` block (matches
  `do-agent`, not `.system/skill-creator`).
- **Body structure**: `# name — one line` -> `## Overview` -> `## When to use` /
  `## When NOT to use` -> numbered `## Step N` -> `## Anti-patterns` -> `## References`.
- **One hop only**: the delegating skills (`divide-and-conquer`, `red-team-blue-team`)
  state this invariant — a delegated agent must not re-delegate; a subagent that lands
  here does the work directly.
- **Integration gate** (delegating skills): never blind-apply external output — review
  it directly, scan for gamed checks (weakened assertions, skipped tests, broadened
  `except`, hard-coded returns, TODO stubs), run the project's verification yourself,
  and on failure do **not** auto-retry — report to the operator.
- **Volatile info**: model slugs are referenced from
  `delegate-agent/references/model-index.md`, never copied.
- **`references/`**: only where warranted — `red-team-blue-team/references/personas.md`
  and `distill-and-structure/references/pyramid.md`. `divide-and-conquer` has none.
- **Scripts**: none needed.
- **`registry.yaml`** is `{}` and **`README.md`** is `# skills` — neither is touched.

## 4. Step 0 — Rename `do-agent` -> `delegate-agent`

The new skills reference the delegation router, so the rename lands first.

| Item | Action |
|---|---|
| `do-agent/` directory | `git mv do-agent delegate-agent` (preserve history) |
| `delegate-agent/SKILL.md` | `name: delegate-agent`; update title, self-references, and `description` |
| `delegate-agent/references/*` | Moved as-is. Update the `# do-agent — ...` heading in `conventions.md` to `# delegate-agent — ...`; leave the `~/.cache/do-agent/` path text unchanged (see below) |
| 5 adapters (`do-codex`, `do-agy`, `do-claude`, `do-copilot`) | Replace prose references that mean *the router skill*: "the `do-agent` router" -> "the `delegate-agent` router"; "`do-agent` family conventions" -> "`delegate-agent` family conventions" |
| **`~/.cache/do-agent/` cache paths** | **Unchanged.** This is a runtime quota-pool cache namespace shared by all five adapters, not the skill. Renaming it invalidates live caches and forces a simultaneous edit of all adapters — out of proportion to a router rename. Keep `~/.cache/do-agent/`. |
| `do-council` | Mechanical find/replace of router references (`Feeds do-agent` in the description, "execute via `do-agent`", "`do-agent` Step-2 route", "`do-agent` Step 5", `plan-schema.md` line 3) -> `delegate-agent`. **Flagged optional** — the user said `do-council` is out of scope; this find/replace only prevents dangling references and can be vetoed at spec review. |
| `README.md`, `registry.yaml` | No change. |

Adapters keep their `do-*` names. `delegate-agent` is "the router over the `do-{tool}`
adapters" and nothing more.

## 5. `divide-and-conquer`

### 5.1 Frontmatter

```yaml
name: divide-and-conquer
description: Use when a requirement is large enough to split into independent work units of differing difficulty — decompose it, classify each unit by difficulty and repetition pattern, route each to the cheapest capable executor (a Claude subagent tier or an external CLI via delegate-agent), run them in parallel where independent, and integrate. No approach debate — for that use do-council.
```

### 5.2 Body

1. **Overview** — the orchestrator owns the result. This skill decomposes, routes, and
   executes. One hop only.
2. **When to use**: the requirement splits into 3+ independent units; units vary in
   difficulty (some mechanical/repetitive, some hard); spreading cost/quota is a win.
   **When NOT**: one indivisible task; the approach itself is uncertain (-> `do-council`);
   tight iterative back-and-forth with the user; trivial.
3. **Step 1 — Decompose**: each unit has one clear purpose, an explicit interface
   (inputs/outputs), and is independently testable. Build a dependency DAG; mark
   independent (parallelizable) vs sequential units. Apply YAGNI — drop units that do
   not serve the goal.
4. **Step 2 — Classify each unit on two axes**:
   - **Difficulty**: `trivial` / `routine` / `hard` / `novel-design`, each with
     concrete recognition signals.
   - **Repetition pattern**: `one-off` / `templated-repeat` (the same transformation
     across N items) / `boilerplate`.
5. **Step 3 — Route** (inline decision table):

   | Unit profile | Cheapest capable executor |
   |---|---|
   | `boilerplate` · `templated-repeat` · `trivial` | Claude Haiku subagent — or `do-agy` flash / `do-codex` luna via `delegate-agent` |
   | `routine` coding | Claude Sonnet subagent — or `do-codex` terra |
   | `hard` · `novel-design` | Claude Opus subagent — or `do-claude` opus / `do-codex` frontier |

   **Subagent vs external CLI**: choose external when (a) Claude quota is tight, (b) you
   want model diversity for a compare, or (c) the job would burn this session's
   context. Otherwise use an in-session subagent (simpler, shares context). Model slugs:
   see `delegate-agent/references/model-index.md`.
6. **Step 4 — Execute**: independent units run in parallel (Agent-tool fan-out, or
   background `do-*` jobs — each file-writing job gets its own worktree/dir). Sequential
   units run in DAG order, feeding outputs forward. Each unit gets a self-contained
   brief: goal, context by path, numbered steps, output shape, DO NOT list, acceptance.
7. **Step 5 — Integrate**: review each unit's output directly; scan for gamed checks;
   run the project's verification yourself; assemble in DAG order and resolve interface
   mismatches. On failure, do not auto-retry — report to the operator with the unit's
   output and the verification failure.
8. **Anti-patterns**:
   - Over-decomposition (10 units for a two-file change).
   - Routing everything to the top tier "to be safe" — defeats the purpose.
   - Decomposing when the approach is unresolved — that is `do-council`'s job.
   - "Parallel" units that actually share state -> merge conflicts.
   - Blind-assembling subagent output.
9. **References**: none — the classification and routing tables are the core value and
   stay inline in `SKILL.md`.

## 6. `red-team-blue-team`

### 6.1 Frontmatter

```yaml
name: red-team-blue-team
description: Use when a work product must be hardened against defects before it ships and one review pass isn't enough — run an adversarial loop of an aggressive builder (blue) and a conservative critic (red), iterating build/critique/revise until the critic raises zero blocking issues or the round cap is hit. Teams default to Claude subagents; scale to external CLIs via delegate-agent for large or high-risk work.
```

### 6.2 Body

1. **Overview** — blue builds, red attacks, the operator owns the loop and the result.
   One hop only.
2. **When to use**: a high-stakes deliverable (a migration, security-sensitive code, a
   spec others depend on); correctness matters more than speed; a single review pass
   historically misses things.
   **When NOT**: low-stakes work; time-critical; the requirement itself is unclear
   (brainstorm first); trivial.
3. **Step 0 — Configure the teams**: default is blue = 1 Claude subagent, red = 1
   Claude subagent, with distinct persona prompts. Scale up (large surface, high risk,
   or model diversity) by making blue and/or red external CLIs via `delegate-agent`
   (e.g. blue = `do-codex`, red = `do-claude`). Multiple blues build independent parts
   in parallel; multiple reds apply different lenses (correctness / security /
   readability).
   - **Blue persona**: bias to action, produce complete drafts, do not sandbag.
   - **Red persona**: conservative, adversarial, assume defects exist, distinguish
     `BLOCKING` from non-blocking, no rubber-stamping, actively hunt for gamed checks.
4. **Step 1 — Blue builds**: self-contained brief -> a complete draft plus a short
   self-assessment of weak spots.
5. **Step 2 — Red critiques**: review against the requirement and its acceptance
   criteria. Each finding tagged `BLOCKING` / `SHOULD` / `NOTE`, each with a concrete
   failure scenario. "Tests pass" is a claim — red asks for or runs verification
   evidence.
6. **Step 3 — Revise**: blue addresses every `BLOCKING` finding — either fixes it or
   argues back with reasoning for the next round's red to adjudicate. The operator
   arbitrates genuine deadlock so the loop cannot spin forever.
7. **Step 4 — Terminate**: stop when red returns zero `BLOCKING` findings **and** no
   new `BLOCKING` was introduced that round; or when the round cap is hit (operator
   sets it, default 3, hard max 6). **Cap hit with `BLOCKING` remaining -> stop, report
   to the operator (remaining findings + blue's last draft + red's last review), do not
   ship.**
8. **Step 5 — Integrate**: the operator reviews the final artifact directly, runs
   verification, and lands it. Attribution if external CLIs were used.
9. **Anti-patterns**:
   - A red that rubber-stamps — defeats the purpose.
   - A red with no `BLOCKING` / non-blocking distinction — everything blocks, the loop
     never terminates.
   - Blue and red on the identical model + prompt — no real adversarial tension; at
     minimum give them distinct personas.
   - An uncapped loop.
   - An operator that forwards messages without arbitrating deadlock.
   - Using this on an unclear requirement — brainstorm first.
   - Shipping on a cap hit with unresolved `BLOCKING`.
10. **References**: `references/personas.md` — the blue and red system prompts.
    (Distinct from `do-council/references/personas.md`, which holds deliberation
    stances.)

## 7. `distill-and-structure`

### 7.1 Frontmatter

```yaml
name: distill-and-structure
description: Use when a prose deliverable (design doc, spec, report, README, PR description, issue) is complete but hard to follow — diagnose its logical structure and style, and propose a concrete restructuring (revised outline + specific edits) using top-down pyramid and bottom-up synthesis. Reviews and proposes; does not rewrite.
```

### 7.2 Body

1. **Overview** — this skill diagnoses and proposes; it does not apply edits. The
   output is a review, not a new draft.
2. **When to use**: a human reader will struggle; the document grew by accretion; it
   buries the lede; the audience is unclear; there are logical jumps.
   **When NOT**: the content itself is wrong (that is review, not restructuring); a
   short document that is already clear; code (out of scope — prose only).
3. **Step 1 — Identify audience and purpose**: who reads this, what decision or action
   it should enable, what they already know. If the document does not state this, flag
   it — most structure problems trace back here.
4. **Step 2 — Bottom-up pass (synthesize)**: list every distinct point the document
   makes, atomically. Group related points; name each group with a one-line claim.
   Derive the single governing message (what all the groups add up to). Spot orphan
   points, duplicated points, and missing links.
5. **Step 3 — Top-down pass (pyramid)**: state the governing message first, then the
   3–5 supporting claims, then the details under each. Each level answers the "why?" or
   "how?" the level above raises. Order groups by what the reader needs first, not by
   how the author discovered them.
6. **Step 4 — Reconcile and produce the proposal**:
   - A revised outline — a heading tree with the one-line claim per section.
   - Specific relocations ("move paragraph 4 under §2 — it answers a question §2
     raises").
   - Style notes scoped to legibility: sentence length, front-loading the subject,
     removing hedges, defining terms on first use, cutting throat-clearing. Defer deep
     prose mechanics to `elements-of-style:writing-clearly-and-concisely` if present —
     do not duplicate it.
   - The strongest 2–3 concrete before/after examples from the actual text.
7. **Output format**: a short review document — Audience/purpose (or the gap),
   Governing message, Proposed outline, Key relocations, Top style fixes with examples.
8. **Anti-patterns**:
   - Rewriting instead of proposing — out of scope; the human or another skill
     rewrites.
   - Line-editing prose while ignoring structure — structure first, style second.
   - Imposing a pyramid on a document type that should not have one (a narrative
     postmortem, a tutorial).
   - Generic advice ("be concise") with no anchor to the actual text.
   - Restructuring without first pinning down the audience.
9. **References**: `references/pyramid.md` — a compact explanation of the Minto pyramid,
   the bottom-up grouping technique, and one worked example.

## 8. How the three compose

Stated in this spec and as a one-line "See also" in each `SKILL.md`:

- `divide-and-conquer` for breadth — many units, varied difficulty.
- `red-team-blue-team` for depth on one risky unit.
- `distill-and-structure` as a finishing pass on a prose deliverable.
- Pipeline example: `divide-and-conquer` splits a project -> one unit is risky ->
  `red-team-blue-team` hardens it -> the final design doc gets a `distill-and-structure`
  pass before it goes to reviewers.
- They stay independent: no skill invokes another (one-hop respected); the human
  composes them.

## 9. Deliverables

- `delegate-agent/` (renamed from `do-agent/`), with inbound references updated across
  the 5 adapters (and `do-council`, flagged optional).
- `divide-and-conquer/SKILL.md`
- `red-team-blue-team/SKILL.md` + `red-team-blue-team/references/personas.md`
- `distill-and-structure/SKILL.md` + `distill-and-structure/references/pyramid.md`
- This design doc.

## 10. Out of scope

- Renaming the `do-*` adapters or the `~/.cache/do-agent/` cache namespace.
- Renaming `do-council`.
- Any change to `registry.yaml` or `README.md`.
- The skills invoking one another or sharing a dispatch reference.
- `distill-and-structure` rewriting text, or covering code.
