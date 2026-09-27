# Task type → adapter (default opinion)

This table is a **default, not a rule**. The caller may override with an explicit tool
or model. Point-in-time judgement, 2026-09. Extend the table as new categories come up.

| Task category | 1st choice (adapter / model) | 2nd choice | Why |
|---|---|---|---|
| Technical-document writing | `do-claude` (`opus`) | `do-agy` (`claude-opus-4-6-thinking`) | prose quality; multi-source synthesis |
| Diagram — ASCII / mermaid | `do-claude` (`sonnet`) | `do-agy` (`gemini-3.8-flash-high`) | ASCII preference; mermaid syntax accuracy |
| Diagram — drawio / structured XML | `do-codex` (`gpt-6-astra` / `gpt-5.6-terra`) | `do-claude` (`sonnet`) | precise structured output |
| Reviewer-facing narrative (impact first → implementation background) | `do-claude` (`opus`) | `do-agy` (`claude-opus-4-6-thinking`) | narrative & readability; offloads Claude quota |
| Simple code refactor | `do-codex` (`gpt-6-luna`) | `do-agy` (`gemini-3.8-flash-medium`) | fast, cheap, saves quota |
| Complex code refactor | `do-codex` (`gpt-6-sol`, effort high) | `do-claude` (`opus`) · `do-agy` (`claude-sonnet-4-6`) | multi-file agentic; subtle logic |
| New feature design | `do-claude` (`opus`) | `do-codex` (`gpt-6-sol` / `gpt-6-astra`, effort ultra) | trade-off judgement |
| Time-series data analysis | `do-codex` (`gpt-6-astra` / `gpt-5.6-terra`, spreadsheets plugin) | `do-agy` (`gemini-3.1-pro-high`) | analysis code + tooling |
| Financial time-series analysis | `do-codex` (`gpt-6-astra` / `gpt-5.6-terra`) | `do-agy` (`gemini-3.1-pro-high`) | as above + `finance-market-monitor` context |
| Stock-market research | `do-codex` (browser plugin) | `do-claude` (WebSearch) | web research |
| Massive-context repo exploration / multi-file trace | `do-agy` (`gemini-3.1-pro-high`) | `do-claude` (`opus`) | multi-million token window; deep cross-file trace |
| Disclosure / filing research | `do-codex` (browser + pdf + spreadsheets) | `do-agy` (`gemini-3.1-pro-high` + `--json-schema`) | filing parsing & structuring |
| Claude reasoning without Claude quota | `do-agy` (`claude-opus-4-6-thinking` / `claude-sonnet-4-6`) | `do-copilot` (Pro+) | spends agy non-Gemini bucket, leaving Claude Max untouched |

Copilot is generally absent here — reserve it for GitHub-native work. Add it as an
alternative (with the Pro+ gate) where a caller specifically wants Copilot.

`do-codex` rows that name a plugin (browser / pdf / spreadsheets / documents / visualize)
assume those Codex plugins are enabled; `do-codex` documents how to check.
