---
type: "concept"
title: "Usage Cost Surface"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/concept"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "security-governance"
related:
  - "[[How is $.model.classify billed]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Reach Levels]]"
  - "[[Mods Trust Model]]"
  - "[[Turn and Session Events]]"
  - "[[Agent and Command Events]]"
  - "[[Mods API Namespaces]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Mod Catalog]]"
  - "[[Budgets and Limits]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)"
  - "https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)"
sources:
  - "docs-mods-api"
  - "docs-mods-overview"
  - "docs-mods-admin"
  - "docs-mods-reference"
  - "docs-plugins-measure"
  - "types-2-1-288"
  - "claudedev-getting-started"
  - "code-modernization-1-0-0"
  - "compass-report"
---

# Usage Cost Surface

A mod spends your usage only through a short list of mechanisms: model calls through `$.model.*`, turns it starts, subagents it starts or reroutes, and text it adds to what Claude reads. The docs state plainly that `$.model.complete` and `$.model.fork` "use the user's plan or API key" (docs-mods-api) and list "Spend your usage" among what a mod can reach (docs-mods-overview) (C-SEC-038). Everything beyond that list below is marked as documented or inferred; Anthropic's pages do not publish a per-mod billing rule.

## Documented versus inferred

| Mechanism | What is documented | What is inference | Evidence |
|---|---|---|---|
| `$.model.complete` | Uses the user's plan or API key; result carries `usage` (`input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`) | Billed at the chosen model's normal rates | docs-mods-api; types 2.1.288 L2386-2414, L5857-5877, L6006-6027 (C-SEC-040) |
| `$.model.fork` | Same billing statement; reuses the main thread's prefix from the prompt cache, and the prefix is "billed afresh once the entry lapsed or after `/model`" | Cost tracks main-thread cache health | docs-mods-api; types L2416-2433 (C-SEC-041) |
| `$.model.classify` | One completion over `$.model.complete` with a fixed classifier prompt; default model is the engine's small fast model | Billed like `complete` on that model | types L2434-2452; listed in docs-mods-reference (C-SEC-039); see [[How is $.model.classify billed]] |
| `$.prompt.submit` | Starts a new turn once the session is idle | A full turn at the session model's cost, plus any tools it triggers | docs-mods-api, "Start a turn from a background job" |
| `$.agent.spawn`, `agent.spawn` hook | A mod can start a subagent, or change a spawn's `model` | Subagent runs cost like any subagent | docs-mods-reference, Subagents |
| `turn.step` rewrite | `next({ ...e, model })` or `effort` sends a request to another model or effort | Can raise or lower every request's cost | docs-mods-reference, Turns; types L4170-4181 (C-SEC-045) |
| `prompt.context`, `prompt.section`, `prompt.attachment`, `tool.describe`, `skill.prompt` | A mod can add or change text Claude reads | More input tokens per request; unstable text breaks prompt caching | docs-mods-reference, Prompts; see [[Prompt Cache Discipline]] |
| `$.tool.register` | Registers a tool Claude can call | Its description joins tool context every request | docs-mods-api; docs-plugins-measure notes MCP tool schemas are not counted by `plugin details` |
| `$.session.usage()` | "The plain call costs nothing"; a `"full"` breakdown counts with the token-count API | None needed | types L2620-2642; claudedev-getting-started (C-SEC-042) |
| `$.http.fetch` to another vendor | Network call through the host | Billed by that vendor, invisible to Claude usage views | types L3262-3282 |
| Hooks that only observe, draw, or store | No model call | Zero usage | docs-plugins-measure shows hooks as "harness-only" for a classic hook (C-SEC-043) |

The seed report claimed `classify` is undocumented (compass-report, section 4). The typings document its mechanism and the reference lists it, so that claim is contradicted; only the billing line is inference.

## Where cost shows up

- **Per call, in the mod.** `r.usage` on each `complete` or `fork` result; a mod can sum `output_tokens` (types L5857-5877).
- **Per session, for the user.** `/usage` on Pro, Max, Team, or Enterprise attributes recent usage to skills, subagents, plugins, and MCP servers as a share (docs-plugins-measure). Whether a mod's own `$.model.complete` calls are attributed to its plugin there is not stated; unverified (C-SEC-044).
- **Across a fleet.** The OpenTelemetry cost counter carries `plugin.name` "when the active skill or subagent belongs to a plugin" (docs-plugins-measure). A mod's direct model call is neither a skill nor a subagent, so attribution is unverified. Third-party names are redacted to `third-party` unless `OTEL_LOG_TOOL_DETAILS=1` (C-SEC-046).
- **Before install.** `claude plugin details` projects always-on tokens for skills, agents, and commands only; the **Context cost** pane appears only for official-marketplace plugins (docs-plugins-measure). Neither covers a mod's model calls.

## Cost patterns to look for in source

| Pattern | Why it costs | Grep |
|---|---|---|
| Model call inside `tool.call`, `prompt.submit`, or `turn.step` with no matcher | Runs on every tool call or prompt | `rg -n '\$\.model\.(complete\|fork\|classify)'` then read the enclosing `on(...)` |
| Model call or `$.prompt.submit` inside `$.clock.every` | Spends while idle, between turns | `rg -n '\$\.clock\.(every\|after)'` |
| `turn.step` that sets `model` | Reroutes every request | `rg -n "on\(['\"]turn\.step"` |
| `agent.spawn` returning `{ model }` | Changes subagent model | `rg -n "on\(['\"]agent\.spawn"` |
| Large or time-varying `prompt.section` or `prompt.context` text | Input tokens and cache misses every request | `rg -n "prompt\.(section\|context\|attachment\|compose)"` |
| `maxTokens` near 64,000 | Default is 1024; the cap is 64,000 or the model limit | `rg -n maxTokens` (limit from docs-mods-reference, Limits) |

## Real examples

- Anthropic's `code-modernization` README warns that some steps start many agents and to "expect real usage on a large system" (code-modernization-1-0-0, README).
- The built-in `cc-plugin-you-should-know` runs a side agent while Claude works and is off by default (docs-mods-overview, built-in table). Running a side agent implies usage; the docs do not quantify it.
- Display-only meters that call `$.session.usage()` without a breakdown cost nothing, per the typings and Anthropic's guide (claudedev-getting-started).

## Recommendations

- Classify every mod as cost none, model calls, or turns before install, and record it in [[Mod Catalog]]. EVIDENCE-BASED
- Require a matcher or a cheap pre-filter in front of any per-event model call. PRACTITIONER
- Prefer `$.model.classify` or `complete` on a small model with a low `maxTokens` for judgments; prefer `fork` only when the main thread's cache is warm. EVIDENCE-BASED
- Keep injected prompt text byte-stable across requests; see [[Prompt Cache Discipline]]. PRACTITIONER
- Do not rely on `/usage` or the OTel cost counter to catch a mod's direct model calls until attribution is confirmed. CONTESTED

## Caveats

- No Anthropic page states how a mod's model calls appear in billing or rate-limit windows beyond "the user's plan or API key". Plan-limit effects are inferred.
- Typings line numbers refer to the 2.1.288 capture; the surface is early access.
- `classify`'s default "small fast model" is not named; it can change between releases.

## Related

Cost is one of the three fields this brain adds to [[Reach Levels]] and a step in the [[Mod Security Audit Checklist]]. The events that carry cost are in [[Turn and Session Events]] and [[Agent and Command Events]]; the methods in [[Mods API Namespaces]]; caps in [[Budgets and Limits]]. Open billing questions live in [[How is $.model.classify billed]]. Cache behavior is in [[Prompt Cache Discipline]]. The wider trust picture is [[Mods Trust Model]].

## Sources

- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-plugins-measure: https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/README.md`
- compass-report: `.raw/sources/compass-report-2026-10-02.md`
