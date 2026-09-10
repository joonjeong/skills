---
name: distill-and-structure
description: Use when a prose deliverable (design doc, spec, report, README, PR description, issue) is complete but hard to follow — diagnose how its content is organized and expressed, and propose a concrete restructuring (revised outline + specific edits) using top-down pyramid and bottom-up synthesis. Reviews and proposes; does not rewrite.
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

First check the document *should* be a pyramid — a narrative postmortem, a tutorial,
or a reference table should not be forced into one (see Anti-patterns). If a pyramid
fits, rebuild the document as one:

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
