# Orchestration Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Each skill-authoring task additionally uses **superpowers:writing-skills** to author and pressure-test the skill file.

**Goal:** Add three independent orchestration skills (`divide-and-conquer`, `red-team-blue-team`, `distill-and-structure`) to the personal `skillshare/skills` repo, and rename the `do-agent` router skill to `delegate-agent`.

**Architecture:** Three self-contained `SKILL.md` files at repo root, matching the existing `do-*` house style (name+description frontmatter, `Overview` / `When to use` / `When NOT to use` / numbered `Step N` / `Anti-patterns` / `References`). `divide-and-conquer` and `red-team-blue-team` inline their own "Claude subagent tier vs external CLI via delegate-agent" dispatch logic; model slugs are referenced, not copied, from `delegate-agent/references/model-index.md`. No skill invokes another. The rename touches the `do-agent` directory, its two files, and inbound prose references in five adapters plus `do-council`; the `~/.cache/do-agent/` cache namespace is left unchanged.

**Tech Stack:** Markdown skill files. No code, no build, no runtime. Verification is structural (frontmatter parses, house-style sections present, no dangling references) plus behavioral pressure-testing via `superpowers:writing-skills`.

**Spec:** `docs/superpowers/specs/2026-09-10-orchestration-skills-design.md`

## Global Constraints

- **Skill file location:** each skill is a directory at repo root — `divide-and-conquer/`, `red-team-blue-team/`, `distill-and-structure/`, `delegate-agent/`.
- **Frontmatter:** `name` and `description` only. No `metadata` block. `name` must exactly equal the directory name.
- **Body section order:** `# <name> — <one line>`, then `## Overview`, `## When to use`, `## When NOT to use`, numbered `## Step N — ...`, `## Anti-patterns`, `## References`. A `## See also` line goes at the end of `Overview` or just before `References`.
- **One hop only:** `divide-and-conquer` and `red-team-blue-team` must state that a delegated agent does not re-delegate, and that a subagent that lands in the skill does the work directly.
- **No copied model slugs:** any reference to concrete model names points to `delegate-agent/references/model-index.md`.
- **Cache namespace untouched:** every `~/.cache/do-agent/` path string stays exactly as written. Only references that mean *the router skill* become `delegate-agent`.
- **`registry.yaml` and `README.md` are not modified.**
- **Commit style:** end every commit message body with the two trailer lines:
  ```
  Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01QWJiCgT1wKXPywQZt2gARM
  ```
- **Branch:** work stays on `orchestration-skills` (already created; the spec commit is `53bce96`).

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `delegate-agent/` (from `do-agent/`) | Renamed router directory | 1 |
| `delegate-agent/SKILL.md` | `name:` and heading updated to `delegate-agent` | 1 |
| `delegate-agent/references/conventions.md` | Heading updated to `delegate-agent` | 1 |
| `do-codex/SKILL.md`, `do-agy/SKILL.md`, `do-claude/SKILL.md`, `do-copilot/SKILL.md` | Router prose references updated | 1 |
| `do-council/SKILL.md`, `do-council/references/plan-schema.md` | Router prose references updated (mechanical) | 1 |
| `divide-and-conquer/SKILL.md` | Decompose → classify → route → execute → integrate workflow | 2 |
| `red-team-blue-team/SKILL.md` | Adversarial build/critique/revise loop with termination | 3 |
| `red-team-blue-team/references/personas.md` | Blue and red system prompts | 3 |
| `distill-and-structure/SKILL.md` | Prose-legibility diagnosis + restructuring proposal | 4 |
| `distill-and-structure/references/pyramid.md` | Minto pyramid + bottom-up grouping method + worked example | 4 |

---

## Task 1: Rename `do-agent` → `delegate-agent`

**Files:**
- Rename: `do-agent/` → `delegate-agent/` (via `git mv`)
- Modify: `delegate-agent/SKILL.md:2` (`name:`) and `:6` (heading)
- Modify: `delegate-agent/references/conventions.md:1` (heading)
- Modify: `do-codex/SKILL.md:9,11`
- Modify: `do-agy/SKILL.md:9,11`
- Modify: `do-claude/SKILL.md:11`
- Modify: `do-copilot/SKILL.md:9,11,99`
- Modify: `do-council/SKILL.md:3,13,16,27,108,123`
- Modify: `do-council/references/plan-schema.md:3`
- Test: `docs/superpowers/plans/checks/task1-grep.sh` (throwaway check script, not committed)

**Interfaces:**
- Consumes: nothing.
- Produces: the skill name `delegate-agent` and the directory `delegate-agent/`, referenced by Tasks 2 and 3 as `delegate-agent/references/model-index.md`.

- [ ] **Step 1: Write the verification check**

Create `docs/superpowers/plans/checks/task1-grep.sh` (temporary, gitignored path is fine — do not `git add` it):

```bash
#!/usr/bin/env bash
set -euo pipefail
fail=0

# 1. delegate-agent dir exists, do-agent dir gone
[ -d delegate-agent ] || { echo "FAIL: delegate-agent/ missing"; fail=1; }
[ ! -d do-agent ] || { echo "FAIL: do-agent/ still present"; fail=1; }

# 2. frontmatter name is delegate-agent
grep -q '^name: delegate-agent$' delegate-agent/SKILL.md || { echo "FAIL: frontmatter name"; fail=1; }

# 3. every remaining 'do-agent' occurrence in tracked md is a ~/.cache/ path
stray=$(grep -rn "do-agent" --include="*.md" . | grep -v "/.git/" | grep -v "/.remember/" | grep -v '~/.cache/do-agent/' || true)
if [ -n "$stray" ]; then echo "FAIL: stray router refs:"; echo "$stray"; fail=1; fi

# 4. new router name is referenced by the adapters
grep -q 'delegate-agent' do-codex/SKILL.md || { echo "FAIL: do-codex not updated"; fail=1; }

exit $fail
```

- [ ] **Step 2: Run the check to verify it fails**

Run: `bash docs/superpowers/plans/checks/task1-grep.sh`
Expected: FAIL — `delegate-agent/ missing` (rename not done yet).

- [ ] **Step 3: Rename the directory**

Run: `git mv do-agent delegate-agent`

- [ ] **Step 4: Update `delegate-agent/SKILL.md`**

Change line 2 from `name: do-agent` to `name: delegate-agent`.
Change line 6 from `# do-agent — delegate work to another agent CLI` to `# delegate-agent — delegate work to another agent CLI`.
Leave the `description` line and every `~/.cache/do-agent/` occurrence unchanged.

- [ ] **Step 5: Update `delegate-agent/references/conventions.md`**

Change line 1 from `# do-agent — union return contract` to `# delegate-agent — union return contract`.
Leave line 10 (`All under ~/.cache/do-agent/`) unchanged.

- [ ] **Step 6: Update the four adapters**

In each file, replace the phrase `the \`do-agent\` router` with `the \`delegate-agent\` router`, and `\`do-agent\` family conventions` with `\`delegate-agent\` family conventions`. Leave every `mkdir -p ~/.cache/do-agent` and `~/.cache/do-agent/*.json` line unchanged.

- `do-codex/SKILL.md`: lines 9 and 11.
- `do-agy/SKILL.md`: lines 9 and 11.
- `do-claude/SKILL.md`: line 11.
- `do-copilot/SKILL.md`: lines 9 and 11, plus line 99 (`the \`do-agent\` router uses it to apply the Pro+ model gate` → `the \`delegate-agent\` router uses it to apply the Pro+ model gate`).

- [ ] **Step 7: Update `do-council` (mechanical router-reference find/replace)**

In `do-council/SKILL.md`, replace `do-agent` with `delegate-agent` on these lines only:
- Line 3 (`description:` — `Feeds do-agent for execution.` → `Feeds delegate-agent for execution.`)
- Line 13 (`execute via \`do-agent\`` → `execute via \`delegate-agent\``)
- Line 16 (`\`do-agent\` and the \`do-<tool>\` adapters` → `\`delegate-agent\` and the \`do-<tool>\` adapters`)
- Line 27 (`skip straight to \`do-agent\`` → `skip straight to \`delegate-agent\``)
- Line 108 (`a \`do-agent\` Step-2 route` → `a \`delegate-agent\` Step-2 route`)
- Line 123 (`fails verification (\`do-agent\` Step 5)` → `fails verification (\`delegate-agent\` Step 5)`)

In `do-council/references/plan-schema.md`, line 3: `\`do-agent\` executes it wave by wave.` → `\`delegate-agent\` executes it wave by wave.`

- [ ] **Step 8: Run the check to verify it passes**

Run: `bash docs/superpowers/plans/checks/task1-grep.sh`
Expected: PASS (no output, exit 0).

Also run: `grep -rn "do-agent" --include="*.md" . | grep -v "/.git/" | grep -v "/.remember/"`
Expected: only lines containing `~/.cache/do-agent/`.

- [ ] **Step 9: Commit**

```bash
rm -rf docs/superpowers/plans/checks
git add delegate-agent do-codex do-agy do-claude do-copilot do-council
git status   # confirm do-agent/ shows as renamed, no checks/ dir staged
git commit -m "refactor: rename do-agent router to delegate-agent

Router skill only. Adapters keep do-* names; the ~/.cache/do-agent/
quota-cache namespace is unchanged. Inbound prose references updated
across the five adapters and do-council.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01QWJiCgT1wKXPywQZt2gARM"
```

---

## Task 2: `divide-and-conquer/SKILL.md`

**Files:**
- Create: `divide-and-conquer/SKILL.md`
- Test: behavioral pressure-test via `superpowers:writing-skills` (see Step 4)

**Interfaces:**
- Consumes: `delegate-agent/references/model-index.md` (path reference only — the skill body links to it for model slugs).
- Produces: the skill `divide-and-conquer`, named by `red-team-blue-team` and `distill-and-structure` in their `See also` lines.

- [ ] **Step 1: Write the acceptance checks**

The finished file must satisfy all of:
1. Frontmatter is exactly `name: divide-and-conquer` + a `description` line, nothing else.
2. `description` is one sentence, third person, states the trigger ("Use when a requirement is large enough to split into independent work units of differing difficulty…") and the exclusion ("for approach debate use do-council").
3. Body has, in order: `## Overview`, `## When to use`, `## When NOT to use`, `## Step 1 — Decompose`, `## Step 2 — Classify`, `## Step 3 — Route`, `## Step 4 — Execute`, `## Step 5 — Integrate`, `## Anti-patterns`, `## See also`.
4. `## Overview` contains the string "One hop only".
5. `## Step 3 — Route` contains a markdown table with three rows (boilerplate/templated-repeat/trivial, routine, hard/novel-design) and links to `delegate-agent/references/model-index.md`.
6. `## Step 5 — Integrate` says to review output directly, scan for gamed checks, run verification yourself, and not auto-retry on failure.
7. No concrete model slug (e.g. `gpt-`, `claude-opus-`, `gemini-3`) appears outside a reference to `model-index.md`.

- [ ] **Step 2: Verify no file exists yet**

Run: `test ! -e divide-and-conquer/SKILL.md && echo "absent (expected)"`
Expected: `absent (expected)`.

- [ ] **Step 3: Author the file**

Create `divide-and-conquer/SKILL.md` with exactly this content:

````markdown
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
````

- [ ] **Step 4: Pressure-test with writing-skills**

Invoke `superpowers:writing-skills` and follow its verification section:
- Confirm the `description` triggers on a decompose-and-route scenario and does **not**
  trigger on a "which architecture should we pick" scenario (that is `do-council`).
- Dispatch a subagent with a 5-unit requirement and confirm it follows Steps 1–5,
  produces a DAG, and routes a `boilerplate` unit to a cheap executor.
- Fix any wording the test surfaces.

- [ ] **Step 5: Run the acceptance checks**

Run:
```bash
grep -c '^name: divide-and-conquer$' divide-and-conquer/SKILL.md   # 1
grep -oE '^## [A-Za-z0-9 —-]+' divide-and-conquer/SKILL.md          # sections in order
grep -q 'One hop only' divide-and-conquer/SKILL.md && echo ok
grep -q 'model-index.md' divide-and-conquer/SKILL.md && echo ok
grep -nE 'gpt-[0-9]|claude-opus-|gemini-3' divide-and-conquer/SKILL.md || echo "no hard-coded slugs (expected)"
```
Expected: count `1`; sections in the order from acceptance check 3; two `ok`s; `no hard-coded slugs (expected)`.

- [ ] **Step 6: Commit**

```bash
git add divide-and-conquer/SKILL.md
git commit -m "feat: add divide-and-conquer skill

Decompose a requirement into independent units, classify each by
difficulty and repetition pattern, route to the cheapest capable
executor (Claude subagent tier or external CLI via delegate-agent),
execute, integrate.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01QWJiCgT1wKXPywQZt2gARM"
```

---

## Task 3: `red-team-blue-team/SKILL.md` + `references/personas.md`

**Files:**
- Create: `red-team-blue-team/SKILL.md`
- Create: `red-team-blue-team/references/personas.md`
- Test: behavioral pressure-test via `superpowers:writing-skills` (see Step 5)

**Interfaces:**
- Consumes: `delegate-agent` (named as the scale-up path for team members); `delegate-agent/references/model-index.md` (path reference).
- Produces: the skill `red-team-blue-team`, named by `divide-and-conquer` and `distill-and-structure` in their `See also` lines.

- [ ] **Step 1: Write the acceptance checks**

The finished `SKILL.md` must satisfy:
1. Frontmatter is `name: red-team-blue-team` + one `description` sentence only.
2. `description` states the trigger ("a work product must be hardened … one review pass isn't enough"), the loop ("build/critique/revise"), the termination ("zero blocking issues or the round cap"), and the default (Claude subagents, scale to external CLIs via delegate-agent).
3. Body order: `## Overview`, `## When to use`, `## When NOT to use`, `## Step 0 — Configure the teams`, `## Step 1 — Blue builds`, `## Step 2 — Red critiques`, `## Step 3 — Revise`, `## Step 4 — Terminate`, `## Step 5 — Integrate`, `## Anti-patterns`, `## See also`, `## References`.
4. `## Overview` contains "One hop only".
5. `## Step 4 — Terminate` names the default round cap (3), a hard max (6), and states "do not ship" on a cap hit with `BLOCKING` remaining.
6. `## Step 2 — Red critiques` defines the `BLOCKING` / `SHOULD` / `NOTE` tags.
7. `## References` links `references/personas.md`.
8. `references/personas.md` exists and contains a "Blue" section and a "Red" section, each a usable system prompt.

- [ ] **Step 2: Verify no files exist yet**

Run: `test ! -e red-team-blue-team/SKILL.md && echo "absent (expected)"`
Expected: `absent (expected)`.

- [ ] **Step 3: Author `red-team-blue-team/SKILL.md`**

Create the file with exactly this content:

````markdown
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

Red reviews the draft against the requirement and its acceptance criteria. Every
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

Stop when **either**:

- Red returns **zero `BLOCKING` findings** and introduced no new `BLOCKING` that round,
  **or**
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

`divide-and-conquer`, `distill-and-structure`.

## References

- `references/personas.md` — the blue and red system prompts.
````

- [ ] **Step 4: Author `red-team-blue-team/references/personas.md`**

Create the file with exactly this content:

````markdown
# Blue and red personas

Assign one to each team member at Step 0. Prepend the relevant block to the member's
brief.

## Blue — the builder

> You are Blue. Your job is to produce a complete, working draft of the deliverable,
> fast. Bias to action: make the decisions the brief leaves open, write the whole
> thing, and do not sandbag or leave gaps for someone else to fill. When you finish,
> add a short self-assessment: the three places you are least confident about and why.
> You are not here to critique — you are here to build. Do not weaken tests or
> assertions to make something pass; if something cannot be made to work, say so
> explicitly.

## Red — the critic

> You are Red. Assume the draft in front of you ships a defect and your job is to find
> it. Review conservatively against the requirement and its acceptance criteria. Tag
> every finding `BLOCKING` (ships a defect — must be fixed), `SHOULD` (real weakness,
> not a blocker), or `NOTE` (nitpick). For each `BLOCKING` finding, give a concrete
> failure scenario: the input or state that triggers it and the wrong result. Do not
> rubber-stamp; do not soften findings to be agreeable. Treat "tests pass" as an
> unverified claim — run the verification or demand the evidence. Actively look for
> gamed checks: weakened assertions, skipped or deleted tests, broadened exception
> handlers, hard-coded return values, TODO stubs.
````

- [ ] **Step 5: Pressure-test with writing-skills**

Invoke `superpowers:writing-skills` and follow its verification section:
- Confirm the `description` triggers on "harden this migration script before we run it"
  and does not trigger on a low-stakes one-file tweak.
- Dispatch subagents as blue and red on a small deliverable with a planted defect;
  confirm red tags it `BLOCKING`, blue fixes it, and the loop terminates.
- Confirm a planted unfixable issue plus a low round cap ends in "stop and report, do
  not ship".

- [ ] **Step 6: Run the acceptance checks**

Run:
```bash
grep -c '^name: red-team-blue-team$' red-team-blue-team/SKILL.md      # 1
grep -oE '^## [A-Za-z0-9 —-]+' red-team-blue-team/SKILL.md            # order per check 3
grep -q 'One hop only' red-team-blue-team/SKILL.md && echo ok
grep -qE 'default \*\*3\*\*, hard max \*\*6\*\*' red-team-blue-team/SKILL.md && echo ok
grep -q 'do not ship' red-team-blue-team/SKILL.md && echo ok
grep -q 'references/personas.md' red-team-blue-team/SKILL.md && echo ok
grep -qE '^## Blue' red-team-blue-team/references/personas.md && grep -qE '^## Red' red-team-blue-team/references/personas.md && echo ok
```
Expected: `1`; sections in order; five `ok`s.

- [ ] **Step 7: Commit**

```bash
git add red-team-blue-team/
git commit -m "feat: add red-team-blue-team skill

Adversarial build/critique/revise loop: an aggressive builder (blue)
and a conservative critic (red) iterate to a termination condition
(zero blocking findings, or a round cap). Teams default to Claude
subagents, scale to external CLIs via delegate-agent.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01QWJiCgT1wKXPywQZt2gARM"
```

---

## Task 4: `distill-and-structure/SKILL.md` + `references/pyramid.md`

**Files:**
- Create: `distill-and-structure/SKILL.md`
- Create: `distill-and-structure/references/pyramid.md`
- Test: behavioral pressure-test via `superpowers:writing-skills` (see Step 5); repo-wide sweep (Step 7)

**Interfaces:**
- Consumes: nothing (references `elements-of-style:writing-clearly-and-concisely` by name only, as an optional deferral target).
- Produces: the skill `distill-and-structure`.

- [ ] **Step 1: Write the acceptance checks**

The finished `SKILL.md` must satisfy:
1. Frontmatter is `name: distill-and-structure` + one `description` sentence only.
2. `description` names the input types (design doc, spec, report, README, PR description, issue), the method (top-down pyramid + bottom-up synthesis), and the constraint ("Reviews and proposes; does not rewrite").
3. Body order: `## Overview`, `## When to use`, `## When NOT to use`, `## Step 1 — Identify audience and purpose`, `## Step 2 — Bottom-up pass`, `## Step 3 — Top-down pass`, `## Step 4 — Reconcile and propose`, `## Output format`, `## Anti-patterns`, `## See also`, `## References`.
4. `## Overview` states the skill does not apply edits — output is a review, not a new draft.
5. `## Step 4` defers deep prose mechanics to `elements-of-style:writing-clearly-and-concisely` "if present".
6. `## Anti-patterns` includes "Rewriting instead of proposing" and "Line-editing prose while ignoring structure".
7. `## References` links `references/pyramid.md`.
8. `references/pyramid.md` exists and contains: the Minto pyramid rule, the bottom-up grouping technique, and one worked before/after example.

- [ ] **Step 2: Verify no files exist yet**

Run: `test ! -e distill-and-structure/SKILL.md && echo "absent (expected)"`
Expected: `absent (expected)`.

- [ ] **Step 3: Author `distill-and-structure/SKILL.md`**

Create the file with exactly this content:

````markdown
---
name: distill-and-structure
description: Use when a prose deliverable (design doc, spec, report, README, PR description, issue) is complete but hard to follow — diagnose its logical structure and style, and propose a concrete restructuring (revised outline + specific edits) using top-down pyramid and bottom-up synthesis. Reviews and proposes; does not rewrite.
---

# distill-and-structure — diagnose a document's legibility, propose a restructure

## Overview

A prose deliverable is written but hard to follow. This skill finds out why and
proposes a fix: a revised outline plus specific, located edits. It works the document
from the bottom up (what points does it actually make?) and from the top down (what
should the reader meet first?), then reconciles the two.

This skill **diagnoses and proposes. It does not apply edits.** The output is a review,
not a rewritten document — the human, or a writing skill, does the rewrite.

## When to use

- A human reader will struggle with the document as written.
- It grew by accretion and no longer has a clear spine.
- It buries the lede — the main point arrives late or never.
- The intended audience is unclear.
- There are logical jumps between sections.

## When NOT to use

- The **content** is wrong or incomplete — that is a review, not a restructure.
- A short document that is already clear.
- Code — this skill is for prose only.

## Step 1 — Identify audience and purpose

Name three things:

- **Who reads this** — role, and what they already know.
- **What it should let them do** — the decision or action it enables.
- **What they already believe** — so you know what needs establishing.

If the document itself does not make these clear, **flag it** — most structure problems
trace straight back to an undefined audience.

## Step 2 — Bottom-up pass

- List **every distinct point** the document makes, atomically — one claim per line.
- **Group** related points. Give each group a one-line claim of its own.
- Derive the **governing message** — the single thing all the groups add up to.
- Flag: **orphan points** (belong to no group), **duplicated points**, and **missing
  links** (a group whose claim the document never actually supports).

See `references/pyramid.md` for the grouping technique.

## Step 3 — Top-down pass

Rebuild the document as a pyramid:

- The **governing message** first.
- Then the **3–5 supporting claims** (the group claims from Step 2).
- Then the **details** under each.

Each level answers the question — "why?" or "how?" — that the level above raises. Order
the supporting claims by **what the reader needs first**, not by the order the author
discovered them.

## Step 4 — Reconcile and propose

Produce:

- **A revised outline** — a heading tree, with the one-line claim for each section.
- **Specific relocations** — "move paragraph 4 under §2; it answers a question §2
  raises." Located, not general.
- **Style notes scoped to legibility** — sentence length, front-loading the subject of
  each sentence, removing hedges, defining terms on first use, cutting throat-clearing
  openers. Defer deeper prose mechanics to
  `elements-of-style:writing-clearly-and-concisely` if present — do not duplicate it.
- **2–3 before/after examples** taken from the actual text, showing the highest-value
  fixes.

## Output format

A short review document:

1. **Audience & purpose** — or the gap, if the document does not establish them.
2. **Governing message** — one sentence.
3. **Proposed outline** — the heading tree with per-section claims.
4. **Key relocations** — the located moves.
5. **Top style fixes** — with before/after from the real text.

## Anti-patterns

- **Rewriting instead of proposing** — out of scope. The human or a writing skill
  rewrites.
- **Line-editing prose while ignoring structure** — structure first, style second.
- **Imposing a pyramid on a document that should not have one** — a narrative
  postmortem, a tutorial, a reference table.
- **Generic advice** ("be concise") with no anchor to the actual text.
- **Restructuring before pinning down the audience.**

## See also

`divide-and-conquer`, `red-team-blue-team`.

## References

- `references/pyramid.md` — the Minto pyramid rule, the bottom-up grouping technique,
  and a worked example.
````

- [ ] **Step 4: Author `distill-and-structure/references/pyramid.md`**

Create the file with exactly this content:

````markdown
# The pyramid, and how to build one bottom-up

## The rule (top-down)

A clear document is a pyramid:

- **One governing message at the top** — the single sentence the reader must leave
  with.
- **3–5 supporting claims** below it. Together they must be sufficient to establish the
  governing message (collectively exhaustive) and not overlap (mutually exclusive).
- **Details** under each supporting claim — evidence, steps, data.

The test for any block of text: does it answer the **"why?"** or **"how?"** raised by
the block above it? If it answers a question nobody asked yet, it is in the wrong
place.

Order the supporting claims by **reader need**, not author chronology. The reader does
not care what you discovered first.

## Building it bottom-up

You rarely know the governing message before you have the pieces. So:

1. **Atomize.** Write every distinct point the draft makes as its own line. One claim
   per line. Ignore the current section boundaries.
2. **Cluster.** Put lines that support the same idea together. A cluster of 1 is an
   orphan — either it belongs in another cluster or it does not belong in the document.
3. **Name each cluster** with a one-line claim — not a topic ("caching"), a claim
   ("the cache is the bottleneck under load").
4. **Read the cluster names in sequence.** They should tell a story. The one sentence
   that story adds up to is your **governing message**.
5. **Check coverage.** Does every cluster name actually get supported by its lines? Is
   any cluster doing two jobs (split it)? Do the cluster names overlap (merge or
   re-cut)?

## Worked example

**Before** — a README section, as written:

> ## Setup
> Install the deps with `pnpm i`. You'll need Node 20+. The config lives in
> `config.yaml` but most of it has sane defaults so you can skip it at first. Run
> `pnpm dev` to start. If you see an `EADDRINUSE` error another process is on port
> 3000. The database is SQLite by default and the file is created on first run. For
> Postgres set `database_url`. Tests are `pnpm test`.

Atomized points: (a) install deps, (b) Node 20+ required, (c) config.yaml exists,
(d) config is optional at first, (e) `pnpm dev` starts it, (f) EADDRINUSE means port
3000 is taken, (g) SQLite is the default, (h) db file auto-created, (i) Postgres via
`database_url`, (j) `pnpm test` runs tests.

Clusters: **Prerequisites** {b}, **First run** {a, e, h}, **Configuration you can defer**
{c, d, g, i}, **Troubleshooting** {f}, **Tests** {j}.

Governing message: *"You can be running in three commands; everything else is optional."*

**After** — restructured:

> ## Setup
>
> **You can be running in three commands.** Everything below that is optional.
>
> **Prerequisites:** Node 20 or newer.
>
> **Run it:**
> ```
> pnpm i
> pnpm dev
> ```
> The SQLite database file is created on first run. Open http://localhost:3000.
>
> **Optional configuration** (`config.yaml`, all with sane defaults): switch to
> Postgres by setting `database_url`.
>
> **Tests:** `pnpm test`
>
> **Troubleshooting:** `EADDRINUSE` — another process is already on port 3000.

The governing message now leads. Deferrable detail is labelled as deferrable. The
reader meets things in the order they need them.
````

- [ ] **Step 5: Pressure-test with writing-skills**

Invoke `superpowers:writing-skills` and follow its verification section:
- Confirm the `description` triggers on "this design doc is hard to follow, can you
  restructure it" and does not trigger on "is this design correct".
- Dispatch a subagent with an accreted, lede-burying document; confirm it returns a
  review in the Output format (not a rewritten document) with a governing message and
  located relocations.
- Confirm it does not rewrite the document in place.

- [ ] **Step 6: Run the acceptance checks**

Run:
```bash
grep -c '^name: distill-and-structure$' distill-and-structure/SKILL.md   # 1
grep -oE '^## [A-Za-z0-9 &—-]+' distill-and-structure/SKILL.md           # order per check 3
grep -q 'does not apply edits' distill-and-structure/SKILL.md && echo ok
grep -q 'writing-clearly-and-concisely' distill-and-structure/SKILL.md && echo ok
grep -q 'Rewriting instead of proposing' distill-and-structure/SKILL.md && echo ok
grep -q 'references/pyramid.md' distill-and-structure/SKILL.md && echo ok
grep -q 'Worked example' distill-and-structure/references/pyramid.md && echo ok
```
Expected: `1`; sections in order; five `ok`s.

- [ ] **Step 7: Repo-wide sweep**

Run:
```bash
# every skill dir has a SKILL.md whose name matches the dir
for d in divide-and-conquer red-team-blue-team distill-and-structure delegate-agent; do
  grep -q "^name: $d\$" "$d/SKILL.md" && echo "$d ok" || echo "$d MISMATCH"
done
# no dangling do-agent router references
grep -rn "do-agent" --include="*.md" . | grep -v "/.git/" | grep -v "/.remember/" | grep -v '~/.cache/do-agent/' || echo "no stray router refs (expected)"
# cross-links resolve: every 'See also' name is a real skill dir
grep -rhoE '(divide-and-conquer|red-team-blue-team|distill-and-structure)' */SKILL.md | sort -u
```
Expected: four `ok`s; `no stray router refs (expected)`; the three skill names listed.

- [ ] **Step 8: Commit**

```bash
git add distill-and-structure/
git commit -m "feat: add distill-and-structure skill

Diagnose a prose deliverable's legibility and propose a concrete
restructuring (revised outline + located edits) using top-down pyramid
and bottom-up synthesis. Reviews and proposes; does not rewrite.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01QWJiCgT1wKXPywQZt2gARM"
```

---

## Self-Review

**1. Spec coverage**

| Spec section | Task |
|---|---|
| §3 Common conventions | Global Constraints + each task's acceptance checks |
| §4 Rename `do-agent` → `delegate-agent` (dir, SKILL.md, conventions.md, 5 adapters, do-council, cache path untouched) | Task 1, Steps 3–7 |
| §5 `divide-and-conquer` (frontmatter + 9 body items) | Task 2, Step 3 |
| §6 `red-team-blue-team` (frontmatter + 10 body items + personas.md) | Task 3, Steps 3–4 |
| §7 `distill-and-structure` (frontmatter + 9 body items + pyramid.md) | Task 4, Steps 3–4 |
| §8 How the three compose ("See also" in each SKILL.md) | Task 2 Step 3, Task 3 Step 3, Task 4 Step 3 (each file has a `See also`) |
| §9 Deliverables | Tasks 1–4 |
| §10 Out of scope | Global Constraints (registry/README untouched, cache namespace untouched); no task renames adapters or do-council's name or has a skill invoke another |

No gaps.

**2. Placeholder scan**

All `SKILL.md` and `references/*.md` content is given in full in the plan. No "TBD",
no "similar to Task N", no "add error handling". The check scripts are complete. The
one deliberate "None" is `divide-and-conquer`'s References section, which the spec
specifies.

**3. Type consistency**

- Skill names are used identically everywhere: `divide-and-conquer`, `red-team-blue-team`,
  `distill-and-structure`, `delegate-agent` (matching each directory and `name:` field).
- The `BLOCKING` / `SHOULD` / `NOTE` tags are defined once in `red-team-blue-team`
  Step 2 and used consistently in Steps 3–4, Anti-patterns, and `personas.md`.
- `delegate-agent/references/model-index.md` is the single referenced path for model
  slugs in both Task 2 and Task 3.
- The round cap ("default 3, hard max 6") matches between the spec §6 and Task 3 Step 3
  acceptance check 5 and the file body.

No inconsistencies.
