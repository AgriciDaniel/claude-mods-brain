---
type: "concept"
title: "Prompt Cache Discipline"
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
lane: "patterns-and-ideas"
related:
  - "[[Prompt Events]]"
  - "[[Turn and Session Events]]"
  - "[[Usage Cost Surface]]"
  - "[[Mods API Namespaces]]"
  - "[[How is $.model.classify billed]]"
  - "[[Ranked Build Ideas]]"
  - "[[Pitfalls Playbook]]"
  - "[[Patterns Playbook]]"
  - "[[karanb192 claude-code-mods]]"
  - "[[Arunjay4213 claude-mods]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-api"
  - "docs-mods-reference"
  - "types-2-1-288"
  - "docs-hooks"
  - "compass-report"
---

# Prompt Cache Discipline

A mod that changes what Claude reads can silently make every request a cache miss. The docs state that text from `prompt.section`, `prompt.context`, and `skill.prompt` hooks "that changes between requests invalidates the prompt cache" (docs-mods-events), and the 2.1.288 typings add `tool.describe` and the `shared` versus `session` scope of system prompt sections (types 2.1.288 L3899-3908, L3945-3952, L7820-7870). The discipline is: put volatile text where the cache does not cover it (after the last cached block, or in per-prompt `context`), keep anything in the system prompt and tool descriptions stable for the session, and measure with `turn.step` usage.

## Where mod text lands, and what it costs the cache

| Event | Where the text goes | Cached by engine? | Cache risk | Source |
|---|---|---|---|---|
| `prompt.compose` | Whole system prompt list, split into `shared` then `session` sections | Engine places the boundary and markers | Varying text in a `shared` section misses the cross-organization cache for nobody's benefit | types 2.1.288 L7820-7870 |
| `prompt.section` | One named system prompt section | Answer cached until `$.ui.invalidate('prompt.section')` | An unstable answer "spends the prompt cache every call" | types 2.1.288 L3899-3908 |
| `prompt.context` | Context with the first message of a conversation | Cached answer | Changing it re-writes everything after it | docs-mods-reference, docs-mods-events |
| `tool.describe` | A tool's description | Cached for the session until invalidated | Unstable answer spends the cache | types 2.1.288 L3945-3952 |
| `skill.prompt` | A skill's expanded text | Per expansion | Changing text between requests invalidates | docs-mods-events |
| `prompt.submit` `context` | Appended after the newest user prompt | Not part of the earlier prefix | Low: it sits at the tail | docs-mods-events |
| `prompt.attachment` | Reminder messages | Cached answer | Medium: rewrites mid-transcript rows | docs-mods-reference |
| `turn.step` `next({ ...e, model })` | Swaps the model for one request | Caches are per model | The new model starts cold | docs-mods-events; inference |

`$.ui.invalidate` for the cached-answer events drops the cached answer "next turn" (types 2.1.288 L2164-2176). Calling it on a timer for `prompt.section` is the classic way to turn a cache hit into a write every turn. EVIDENCE-BASED

## Safe patterns

1. **Per-prompt facts go in `prompt.submit` context.** Branch names, ticket ids, a voice card: append with `next({ ...e, context: [...(e.context ?? []), text] })`, and only when the prompt matches (docs-mods-events example). A personal voice-card mod reviewed for this vault adds a card of at most 2,600 characters only on writing prompts from the user's own origins (`composer`, `bridge`, `sdk`), and caches the note by `mtimeMs`. EVIDENCE-BASED
2. **System prompt changes must be session-stable.** If a `prompt.section` hook must vary, vary it at most once per session and keep it in a `session`-scope section. EVIDENCE-BASED
3. **Tool descriptions are part of the prefix.** A registered tool's description is read by Claude; keep it constant and short. Registering tools late or changing them mid-session reshapes the tool block. PRACTITIONER
4. **Do not swap models inside a turn for cost** unless the saving exceeds a cold write on the new model. `turn.step` model swaps and `/model` both forfeit the warm cache (types 2.1.288 L2415-2421 for fork; PreModelSwitch input fields L7357-7368 carry `prompt_cache_warm` and `estimated_cache_write_usd`). PRACTITIONER
5. **Fork, do not complete, when you need conversation context.** `$.model.fork` reuses the main thread's cached prefix; `$.model.complete` sends only your prompt. A fork after the cache lapsed or after `/model` pays the whole prefix (types 2.1.288 L2415-2433). EVIDENCE-BASED

## Measuring it

```typescript
on('turn.step', async function* ($, e, next) {
  const result = yield* next(e)
  if (!e.agentId && result.usage) {
    const u = result.usage
    $.ui.log(`cache read ${u.cache_read_input_tokens} wrote ${u.cache_creation_input_tokens}`, { to: 'debug' })
  }
  return result
})
```

The docs example logs to the transcript (docs-mods-events); sending it to the debug log keeps the transcript clean. `result.usage` carries `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, and `model` (docs-mods-events). A steady state has large reads and small writes; a write that is about the size of the whole context after a mod reload or a timer tick points at a volatile section. PRACTITIONER

## Classic hooks have the same trap

Settings hooks that return `additionalContext` on `SessionStart` or `UserPromptSubmit` add text too, and `PreModelSwitch` input exposes `estimated_cache_write_usd` so a hook can warn before a cold switch (docs-hooks, via lane notes on hooks.md L1142 and L3204). A mod is not uniquely risky here; it just has more places to write.

> [!contradiction]
> The seed report prices a cache miss at "12.5x a hit" for 5 minute writes and up to 80x for 1 hour writes, citing secondary blogs (compass-report L386). This lane did not verify those multipliers against Anthropic pricing pages; treat them as unverified. The docs only say that changing text invalidates the cache and link to the prompt caching page.

## Recommendations

- Keep every `prompt.section`, `prompt.context`, and `tool.describe` answer a pure function of session-stable inputs. EVIDENCE-BASED
- Put volatile facts in `prompt.submit` `context`, gated by a regex, so cost lands only on matching prompts. EVIDENCE-BASED
- Never call `$.ui.invalidate('prompt.section')` from a timer. EVIDENCE-BASED
- Add a `turn.step` cache log while developing any mod that touches prompt events, and remove it or route it to debug before publishing. PRACTITIONER
- State the per-prompt token cost in the plugin description, for example "about 600 input tokens, only on matching prompts". PRACTITIONER

## Caveats

- Cache scope rules (`shared` across organizations) are taken from typings comments, not a docs page; treat as SINGLE-SOURCE until the prompt caching docs are captured.
- The cost multipliers are not verified in this lane.
- Whether `prompt.attachment` rewrites shift the cached prefix depends on where the reminder sits; not tested.

## Related

Event details live in [[Prompt Events]] and [[Turn and Session Events]]; namespaces in [[Mods API Namespaces]]. The cost view is [[Usage Cost Surface]] and [[How is $.model.classify billed]]. Build ideas that rely on this, such as a cache-break detector, are ranked in [[Ranked Build Ideas]]; mistakes in [[Pitfalls Playbook]], shapes in [[Patterns Playbook]]. Community meters that read cache ratios are in [[Arunjay4213 claude-mods]] and [[karanb192 claude-code-mods]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-hooks: https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (secondary, lead list only)
