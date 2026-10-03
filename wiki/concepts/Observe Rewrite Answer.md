---
type: "concept"
title: "Observe Rewrite Answer"
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
  - "[[Hook Middleware Chain]]"
  - "[[Tool Events]]"
  - "[[Prompt Events]]"
  - "[[Turn and Session Events]]"
  - "[[Render Sites]]"
  - "[[Holding a Tool Call]]"
  - "[[Prompt Injection via Mods]]"
  - "[[Patterns Playbook]]"
  - "[[Pitfalls Playbook]]"
  - "[[Mods API Cheatsheet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-reference"
  - "types-2-1-288"
  - "claudedev-getting-started"
---

# Observe Rewrite Answer

Every mod hook does one of three things with an event, and what it does with `next` decides which (C-API-007). Observe: let the event through and look at it (or at its result). Rewrite: call `next` with a changed copy, or change the result on the way back up. Answer: return a result without calling `next`, so later mods and Claude Code's own behavior never run (docs-mods-events L13-71; claudedev-getting-started L35-38).

## The three moves side by side

| Move | Code shape | Effect on later hooks and core | Typical use |
|---|---|---|---|
| Observe before | `doWork(); return next(e)` | Run unchanged | Logging, counters, a status band |
| Observe after | `const r = await next(e); look(r); return r` | Run unchanged; you see the result | Post-tool checks, cache stats |
| Rewrite down | `return next({ ...e, text: e.text.trim() })` | Run on your copy, never see the original | Prompt cleanup, model routing, arg fixes |
| Rewrite up | `const r = await next(e); return { ...r, text: newText }` | Ran on the original; hooks above see your result | Redacting tool output, relabeling |
| Answer | `return { deny: 'reason' }` (no `next`) | Do not run | Guards, mocks, custom tools and commands |
| Retry | `let r = await next(e); if (r.isError) r = await next(e); return r` | Run twice | Flaky tools (docs-mods-events L134) |

Each call to `next` runs everything beneath again (types 2.1.288 L6106-6111), so retry is literally a second `next(e)`.

## Worked TypeScript, one event, three moves

```ts
import type { Register } from 'claude-code'

export const register: Register = (on) => {
  // Observe after: log failed Edit/Write calls, change nothing
  on('tool.call', { tool: ['Edit', 'Write'] }, async ($, e, next) => {
    const result = await next(e)
    if (result.isError === true) $.ui.log('failed: ' + e.file_path)
    return result
  })

  // Rewrite down: force a timeout on every Bash call
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    return next({ ...e, timeout: Math.min(e.timeout ?? 120_000, 120_000) })
  })

  // Answer: refuse force pushes without running anything beneath
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    if (/git push .*--force/.test(e.command)) {
      return { deny: 'Force push blocked. Push to a new branch instead.' }
    }
    return next(e)
  })
}
```

Two `on('tool.call', { tool: 'Bash' }, ...)` registrations are fine because each has a matcher; the no-matcher duplicate rule applies only to identical bare registrations (docs-mods-events L92).

## What "answer" means per event

The answer shape is event specific. A wrong shape counts as a failure and the hook is skipped (C-API-011).

| Event | Answer without `next` | Evidence |
|---|---|---|
| `tool.call` | `{ deny }` or `{ result, context? }` | types 2.1.288 L11986-12085 |
| `tool.check` | `{ decision, reason?, rule? }` | types L12133-12156 |
| `prompt.submit` | `{ drop: reason }` | types L8478-8516 |
| `prompt.section`, `prompt.attachment` | `{ text }` or `{ text: null }` to omit | types L8376-8379, L7755-7758 |
| `command.run` | `{ text }`, `{}`, `{ text, exitCode }` | types L1655-1698 |
| `turn.step` | a generator that yields its own chunks and returns a `TurnStepResult`; no request is sent | types L4174-4181 |
| `turn.complete` | `{ text }` shown beneath the answer | types L4183-4190 |
| `session.compact` | `{ skip: reason }` or `{ messages }` | types L4101-4111 |
| `session.receive` | `{ consumed: reason }` | types L10750-10774 |
| `session.send` | `{ isDelivered: false, reason }` | types L10932-10954 |
| `agent.offer` | `{ isOffered: false }` | types L3836-3845 |
| `agent.spawn` | `{ model }` or `{ deny }` | types L3847-3854 |
| `ui.render` | an element tree | types L3755-3765 |
| `plugin.register` | `{ refuse: reason }` | types L4159-4167 |
| any `$` call event | `{ value }` or `{ deny }` | docs-mods-reference L158 |

## Pinned fields: what a rewrite cannot change

Several inputs carry identity fields the engine refuses or ignores when rewritten:

| Event | Pinned | Rewritable | Evidence |
|---|---|---|---|
| `tool.call` | `tool`, `tool_use_id`, `agentId` | the tool's own arguments | types 2.1.288 L11952-11961 |
| `tool.check` | `tool`, `input`, `tool_use_id` (decide, do not change) | none; answer a decision | types L12103-12107 |
| `prompt.submit` | `origin` (may put back, never set another) | `text`, `context` | types L8462-8470 |
| `turn.step` | `turnId`, `index`, `messageCount`, `agentId` | `model`, `effort` | types L12628-12671 |
| `command.run` | `command`, `presentation` | `args` | types L1610-1653 |
| `telemetry.log` | `to` | record contents | types L4008-4018 |

## Answering is powerful, and invisible

Paraphrase (docs-mods-events L134): when a `tool.call` hook answers `{ result }`, no permission prompt appears, the tool does not run, and your result is all Claude learns. Claude reads `deny` text as the tool result, so write it as an instruction Claude can act on (docs-mods-events L116). The same power makes a hostile mod dangerous: a `prompt.submit` or `session.append` rewrite changes what the model reads with no visible trace; see [[Prompt Injection via Mods]] and [[Mods Trust Model]].

> [!note] Rewrites that the user still sees
> A `prompt.submit` rewrite changes the user message on screen (types 2.1.288 L3858-3862), while `context` added there is model-only. A `turn.complete` `{ text }` adds a line but never rewrites the transcript record (L4183-4190). Choose the move by who should see the change.

## Recommendations

- Default to observe; reach for rewrite or answer only when the mod's purpose requires it, and say so in the README. PRACTITIONER
- When answering a tool call, phrase `deny` as a next step ("Push to a new branch instead"). EVIDENCE-BASED
- Rewrite on the way down with spread copies (`{ ...e, field }`); never try to mutate `e`, it throws. EVIDENCE-BASED
- When you rewrite up, keep `ref` by spreading the object you got, so core can reuse its messages verbatim (types 2.1.288 L12027-12033). EVIDENCE-BASED

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- The per-event answer table is drawn from the 2.1.288 typings; a few shapes (`command.run` `exitCode`, `session.compact` `{ messages }`) are not on the docs pages.
- No hook here was executed; shapes are from declarations and docs examples.

## Related

The chain mechanics are in [[Hook Middleware Chain]]. Per-family detail: [[Tool Events]], [[Prompt Events]], [[Turn and Session Events]], [[Render Sites]]. Holding before answering is in [[Holding a Tool Call]]. Reusable shapes live in [[Patterns Playbook]]; failure modes in [[Pitfalls Playbook]]; one page in [[Mods API Cheatsheet]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
