---
type: "concept"
title: "Turn and Session Events"
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
lane: "api-and-events"
related:
  - "[[Prompt Events]]"
  - "[[Agent and Command Events]]"
  - "[[Budgets and Limits]]"
  - "[[State Store and Module Variables]]"
  - "[[Classic Hook Bridge]]"
  - "[[Usage Cost Surface]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Build a Status Band Flow]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Mods API Cheatsheet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-reference"
  - "docs-mods-api"
  - "docs-mods-interface"
  - "types-2-1-288"
---

# Turn and Session Events

Turn events follow one answer: `turn.start` when it begins, `turn.step` for every model request inside it (several when tools run), and `turn.complete` when it ends (docs-mods-reference L87-95). Session events bracket the whole session and its plumbing: start and end, compaction, cross-session messages, every stored transcript row, remote surfaces attaching, and usage measurements (L97-111). `turn.step` is one of only two streaming events, so its hook must be an async generator (C-API-029). Settings-hook events also arrive here as `classic.<Event>`.

## Turn events

| Event | `e` | Result / answer | Evidence |
|---|---|---|---|
| `turn.start` | `{ text, turnId }` | `{ turnId }` echoed; observe only | types 2.1.288 L4168-4172, L12572-12595 |
| `turn.step` | `{ turnId, index, model, effort?, messageCount, agentId? }` | streams `TurnStepChunk`s, returns `TurnStepResult`; rewrite `model`/`effort` | types L4174-4181, L12601-12812 |
| `turn.complete` | `{ answer, durationMs, isAborted, turnId, agentId?, usage?, reason, refusal? }` | `{ text, usage? }`; a different `text` shows beneath the answer | types L4183-4190, L12478-12560 |

- `effort` is `'low' | 'medium' | 'high' | 'xhigh' | 'max' | number` (types 2.1.288 L12645-12650).
- `reason` is `answer`, `aborted`, `refusal` (with `refusal: { category, explanation }`) or `error` (L12528-12569).
- A subagent's run fires no `turn.start`, but its steps and `turn.complete` carry `agentId` (L12495-12509).
- Usage fields: `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, plus `model` (C-API-031).

### Streaming `turn.step`

Chunks: `text` (`index`, `text`), `thinking`, `tool` (`index`, `id`, `name`), `input` (partial JSON for a tool's arguments), `stop` (`stopReason`, `usage`), and opaque `engine` chunks to pass on (types 2.1.288 L12601-12782). Stop reasons: `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`, `pause_turn`, `compaction`, `refusal`, `model_context_window_exceeded`, or `null` (L12797).

```ts
import type { Register } from 'claude-code'

export const register: Register = (on) => {
  // Cache meter: pass the stream through, read the result
  on('turn.step', async function* ($, e, next) {
    const result = yield* next(e)
    if (e.agentId === undefined && result.usage) {
      const u = result.usage
      $.ui.status('cache ' + u.cache_read_input_tokens + ' read, ' + u.cache_creation_input_tokens + ' written')
    }
    return result
  })

  // Route subagent requests to a cheaper model
  on('turn.step', async function* ($, e, next) {
    if (e.agentId === undefined) return yield* next(e)
    return yield* next({ ...e, model: 'haiku' })
  })
}
```

Paraphrase (types 2.1.288 L11454-11460): a plain function on a streaming event is a type error even when it returns `next(e)`, because the hook is the generator. The budget counts only your own code, never time at a `yield` or inside the stream (L4815-4820). A hook that calls `next(e)` twice sends two model requests (L11481-11486).

> [!warning] Rewriting text chunks rewrites the record
> The text the user watches and the transcript records are both the concatenation of `text` chunks; a hook that rewrites them rewrites both, and dropping a `tool` chunk means no tool call is recorded or run (types 2.1.288 L12735-12779).

## Session events

| Event | Fires | Key fields | Answer | Evidence |
|---|---|---|---|---|
| `session.start` | once per loaded mod before the first prompt (awaited), again on reload | `cwd`, `surface`, `isInteractive` | `{ cwd }` echoed | types L4053-4063, L10982-11008 |
| `session.end` | exit, `/clear`, resume, logout, signal, `-p` done | `reason`, `sessionId`, `resume` | `{ sessionId }` echoed | types L4145-4155, L10356-10404 |
| `session.compact` | before compaction | `trigger`, `instructions?`, `messages`, `agentId?` | `{ skip }` or `{ messages }` | types L4101-4111, L10110-10168 |
| `session.receive` | inbound message before it is queued | `origin`, `text`, `event?`, `agentId?` | `{ consumed: reason }` | types L4065-4075, L10618-10774 |
| `session.send` | outbound message (SendMessage or `$.session.send`) | `to`, `text`, `origin` (`model` or `plugin`), `agentId?` | `{ isDelivered: false, reason }` | types L4089-4099, L10824-10954 |
| `session.append` | every row before it is stored | `message`, `door`, `origin`, `uuid`, `agentId?` | `next({ ...e, message })` | types L4077-4087, L9848-10016 |
| `session.attach` / `session.detach` | remote client joins or leaves | `surface`, `clientId`, `viewport?` / `reason` | observe | types L4113-4131, L10018-10349 |
| `session.measure` | after each main-thread turn; rate-limit moves a whole point | `context`, `rateLimits`, `cost?`, `changed` | observe | types L4133-4143, L10410-10447 |

Value sets: `session.end` reason `clear`, `resume`, `logout`, `prompt_input_exit`, `other` (`/branch` reports `resume`) (C-API-034). Compaction `trigger`: `manual`, `auto`, `plugin`, `precompute` (C-API-036). Append `door`: `prompt`, `command`, `response`, `tool-result`, `tool-message`, `delivery`, `attachment`, `hook-context`, `note`, `compaction`, `notice` (types L9871).

### Session lifecycle rules

- `session.start` is the place to register commands, tools and timers; the first is awaited, so a `$.tool.register` is listed in turn one (C-API-033). A later one runs on enable, worker respawn or reload of changed modules only (types L4057-4059).
- `/clear`, `/resume` and `/branch` do not fire `session.start`. They fire `classic.SessionStart` with `source` `clear`, `resume` or `fork`, and they reset `$.state` (C-API-035). Reseed there.
- All `session.end` hooks share one 1.5 s wall-clock bound that keeps running through `$` waits (C-API-013). Save with `next.budget` in mind.

```ts
on('session.end', async ($, e, next) => {
  if (next.budget.remainingMs > 200) await $.store.set('lastEnd', { reason: e.reason, at: await $.clock.now() })
  return next(e)
})
```

### Usage without polling

```ts
on('session.measure', async ($, e, next) => {
  const hot = e.rateLimits.find(r => r.percentUsed >= 90)
  if (hot && e.changed.includes('rateLimits')) $.ui.toast(hot.kind + ' at ' + hot.percentUsed + '%')
  return next(e)
})
```

`$.session.usage()` returns the same figures on demand; a plain call is free, `breakdown: 'full'` uses the token-count API (C-API-058). See [[Usage Cost Surface]].

## Settings hook events (`classic.*`)

Each settings hook event is also `classic.<Event>`, with `e` equal to the stdin JSON a command hook would read (docs-mods-events L260-277). The 2.1.288 typings list 33: ConfigChange, CwdChanged, DirectoryAdded, Elicitation, ElicitationResult, FileChanged, InstructionsLoaded, MessageDisplay, Notification, PermissionDenied, PermissionRequest, PostCompact, PostModelSwitch, PostToolBatch, PostToolUse, PostToolUseFailure, PreCompact, PreModelSwitch, PreToolUse, SessionEnd, SessionStart, Setup, Stop, StopFailure, SubagentStart, SubagentStop, TaskCompleted, TaskCreated, TeammateIdle, UserPromptExpansion, UserPromptSubmit, WorktreeCreate, WorktreeRemove (types 2.1.288 `hook_event_name` literals). Each fires wherever the engine runs that classic hook, whether or not any settings hook is configured (types L1060-1068). Return `next(e)` so settings hooks still run. See [[Classic Hook Bridge]].

## Recommendations

- Register everything in one `session.start` hook and register commands last, since a throw skips the rest (docs-mods-api L39). EVIDENCE-BASED
- Check `e.agentId === undefined` in `turn.step` and `turn.complete` hooks meant for the main conversation only. EVIDENCE-BASED
- Prefer `session.measure` to polling `$.session.usage()` on a timer. EVIDENCE-BASED
- Never block in `session.end`; write small and fast, or persist continuously during the session. EVIDENCE-BASED

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- `session.append`, `session.attach`/`detach` and `session.measure` shapes are documented only by name and one line on the docs pages; detail here is from the 2.1.288 typings.
- The classic event count (33) is read from the 2.1.288 typings and will drift with the settings hooks docs.

## Related

Prompt side: [[Prompt Events]]. Subagents and commands: [[Agent and Command Events]]. Limits: [[Budgets and Limits]]. State reset rules: [[State Store and Module Variables]]. Old hooks: [[Classic Hook Bridge]]. Cost: [[Usage Cost Surface]], [[Prompt Cache Discipline]]. A status band built on these: [[Build a Status Band Flow]]. Reload behavior: [[Hot Reload and Dev Loop]]. Lookup: [[Mods API Cheatsheet]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
