# Model family / tier → adapter

Model identifiers churn monthly (e.g. GPT-5.4 retired 2026-08-31). This index keys on
**provider family + capability tier**, not exact slugs. Each adapter's "Model catalog"
section carries the current slugs plus a live-discovery command. Snapshot: 2026-09.

| Want | 1st choice (adapter, example model) | Bucket | Alternative (condition) |
|---|---|---|---|
| Top-tier general reasoning | `do-claude` (`opus`) · `do-codex` (`gpt-6-astra` / `gpt-5.6-sol`) | Claude Max / ChatGPT | `do-copilot` (Opus 5) — **Pro+ or higher** |
| Everyday coding (balanced) | `do-codex` (`gpt-5.6-terra`) · `do-claude` (`sonnet`) | ChatGPT / Claude Max | `do-copilot` (`--model auto`) — Pro OK |
| Fast + cheap | `do-codex` (`gpt-5.6-luna`) · `do-agy` (`gemini-3.8-flash-low`) | ChatGPT / agy:Gemini | `do-copilot` (auto) — Pro OK |
| Newest Gemini (version) | `do-agy` (`gemini-3.8-flash-high`) | agy:Gemini | `do-copilot` (Gemini 3.8 Flash) — Pro OK |
| Gemini Pro tier / long context | `do-agy` (`gemini-3.1-pro-high`) | agy:Gemini | `do-copilot` (Gemini 3 Pro, if offered) |
| Claude-family, off the Claude quota | `do-agy` (`claude-opus-4-6-thinking`, `claude-sonnet-4-6`) | agy:non-Gemini | `do-copilot` (Sonnet 4.6 Pro OK / Opus Pro+) |
| Open-source model | `do-agy` (`gpt-oss-120b-medium`) | agy:non-Gemini | `do-codex --oss` |
| GitHub-native task | `do-copilot` (`--model auto`) | Copilot credits | — |

## Copilot plan gate

| Plan | Models | Monthly credit |
|---|---|---|
| Free / Pro ($10) | `--model auto` only; mid-tier (Haiku 4.5, Sonnet-class, Gemini Flash, GPT-5 / 5-mini / 5.3-Codex). No Opus, no frontier. | $15 |
| Pro+ ($39) | + Claude Opus 4.7/4.8/5, Fable 5/5.1, GPT-5.4–5.6, Grok 4.5/4.6, Kimi K2.7/K3 | $70 |
| Business / Enterprise / Max | Pro+ models + priority + larger pool | 1,900 / 3,900 / 20,000 |

`do-copilot` preflight reports the live `plan`; the router treats frontier rows above
as requiring Pro+ or higher.
