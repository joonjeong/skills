# Task type → adapter (default opinion)

This table is a **default, not a rule**. The caller may override with an explicit tool
or model. Point-in-time judgement, 2026-10. **Not benchmarked** — these are qualitative opinions; see `delegate-agent` "Routing policy provenance". Extend the table as new categories come up.

| Task category | 1st choice (adapter / model) | 2nd choice | Why |
|---|---|---|---|
| Technical-document writing | `do-claude` (`opus`) | `do-agy` (`claude-opus-5-5-high`) | prose quality; multi-source synthesis |
| Diagram — ASCII / mermaid | `do-claude` (`sonnet`) | `do-agy` (`gemini-3.8-flash-high`) | ASCII preference; mermaid syntax accuracy |
| Diagram — drawio / structured XML | `do-codex` (`gpt-6-astra` / `gpt-5.6-terra`) | `do-claude` (`sonnet`) | precise structured output |
| Reviewer-facing narrative (impact first → implementation background) | `do-claude` (`opus`) | `do-agy` (`claude-opus-5-5-high`) | narrative & readability; offloads Claude quota |
| Simple code refactor | `do-codex` (`gpt-6-luna`) | `do-agy` (`gemini-3.8-flash-medium`) | fast, cheap, saves quota |
| Complex code refactor | `do-codex` (`gpt-6-sol`, effort high) | `do-claude` (`opus`) · `do-agy` (`claude-sonnet-5-5-medium`) | multi-file agentic; subtle logic |
| New feature design | `do-claude` (`opus`) | `do-codex` (`gpt-6-sol` / `gpt-6-astra`, effort ultra) | trade-off judgement |
| Time-series data analysis | `do-codex` (`gpt-6-astra` / `gpt-5.6-terra`, spreadsheets plugin) | `do-agy` (`gemini-4-argon-high`) | analysis code + tooling |
| Financial time-series analysis | `do-codex` (`gpt-6-astra` / `gpt-5.6-terra`) | `do-agy` (`gemini-4-argon-high`) | as above + `finance-market-monitor` context |
| Stock-market research | `do-codex` (browser plugin) | `do-claude` (WebSearch) | web research |
| Massive-context repo exploration / multi-file trace | `do-agy` (`gemini-4-argon-high`) | `do-claude` (`opus`) | multi-million token window; deep cross-file trace |
| Disclosure / filing research | `do-codex` (browser + pdf + spreadsheets) | `do-agy` (`gemini-4-argon-high` + `--json-schema`) | filing parsing & structuring |
| Claude reasoning without Claude quota | `do-agy` (`claude-opus-5-5-high` / `claude-sonnet-5-5-medium`) | `do-copilot` (Pro+) | spends agy non-Gemini bucket, leaving Claude Max untouched |

Copilot is generally absent here — reserve it for GitHub-native work. Add it as an
alternative (with the Pro+ gate) where a caller specifically wants Copilot.

`do-codex` rows that name a plugin (browser / pdf / spreadsheets / documents / visualize)
assume those Codex plugins are enabled; `do-codex` documents how to check.

## Starting tier + escalation (cost policy)

Tiers are defined in `model-index.md` → "Cost tier ladder". Start at the listed tier
on the 1st-choice adapter; escalate **one tier per retry** only on a trigger.

| Task category | Start | Escalate when | Evidence (eval-agent-matrix, 2026-10-17, n=1, provisional) |
|---|---|---|---|
| Simple refactor / multi-file rename | T0 | checker/test fail, timeout | rename: all T1/T2 + copilot auto pass; luna pass |
| Bugfix (small, test-guarded) | T0 (not `haiku`) → T1 | test still fails, diagnosis ambiguous | bugfix: `haiku` **fail**; flash-low, luna, terra, sonnet pass |
| Structured extraction (JSON / XML / drawio) | T0 | schema validation fails | json-extract: luna, sonnet, copilot auto pass |
| Long-context trace / repo exploration | T1 (T2 `gemini-4-argon-high` if >200k tokens) | missed references, incomplete trace | long-context-trace: `haiku` and luna pass |
| Diagram — ASCII / mermaid | T1 | syntax render fails | not benchmarked |
| Data / financial analysis | T1 | numbers fail cross-check | not benchmarked |
| Complex refactor | T1 | checker fail, subtle-logic regression | not benchmarked |
| Reviewer-facing prose / narrative, tech docs | **T2** (start high) | — | pr-narrative (blind judge, 0–10): T2 opus / gpt-6-astra / gpt-6-sol = 10; T0–T1 gpt-6-luna / copilot auto = 7 (dropped key numbers and risk callouts). Sonnet unscored (artifact lost) |
| New feature design / architecture | **T2** | — | not benchmarked |
| High-stakes / irreversible (migrations, deletes, prod config, security) | **T2** | — | policy, not eval-derived |

General triggers for any row: checker fail · timeout · ambiguous / underspecified
brief the worker could not resolve · stakes discovered to be high mid-task. Not
triggers: `quota_exceeded` (route to another bucket at the same tier), `auth_error`.
The ceiling effect (almost every cell passed) means these results support
"T0/T1 is adequate for mechanical tasks", not a fine-grained ranking.
