# Division-of-labor plan object

Phase B freezes the consensus into this object. `delegate-agent` executes it wave by wave.
Discuss it as a table first; emit the object once the operator approves.

```yaml
goal: <the requirement, one sentence>
consensus_ref: <path or id of the Phase A consensus record>

units:
  - id: u1
    task: <concrete deliverable, verifiable on its own>
    implements: <which consensus decision this realizes>
    adapter: do-codex | do-agy | do-copilot | do-claude
    model: <slug, or "auto">
    quota_bucket: chatgpt | gemini | non-gemini | copilot | claude:<profile>
    output: diff | report | json
    depends_on: []              # unit ids
    workdir: <isolated dir/worktree if the unit writes files>
    acceptance: <how the orchestrator verifies this unit>

pattern: parallel | pipeline | mixed
waves:                          # execution order; units in a wave run in parallel
  - [u1]
  - [u2, u3]
integration_order: [u1, u2, u3]

quota_check:                    # one line per distinct bucket, from adapter preflight
  chatgpt: <available | exhausted until <ts>>
  gemini:  <...>

orchestrator: in-session | do-claude:<profile> | none
risks:
  - <what could go wrong, which unit, mitigation>
```

## Rules

- A unit must be **verifiable alone** — if you can't state its `acceptance`, the split
  is wrong.
- No two units in the same wave write the same paths. Writers get isolated `workdir`s.
- `quota_check` must clear for every bucket a wave uses before that wave starts.
- If a unit's adapter becomes unusable at run time, that is a re-planning trigger
  (`do-council` "Re-planning triggers") — do not silently reassign.
- `implements` is required: a unit with no consensus decision behind it is scope creep.
