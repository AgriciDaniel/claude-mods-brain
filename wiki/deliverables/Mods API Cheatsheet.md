---
type: "deliverable"
title: "Mods API Cheatsheet"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/deliverable"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "api-and-events"
related:
  - "[[Mod Anatomy]]"
  - "[[Hook Middleware Chain]]"
  - "[[Observe Rewrite Answer]]"
  - "[[Tool Events]]"
  - "[[Prompt Events]]"
  - "[[Turn and Session Events]]"
  - "[[Agent and Command Events]]"
  - "[[Render Sites]]"
  - "[[UI Elements and JSX]]"
  - "[[Mods API Namespaces]]"
  - "[[State Store and Module Variables]]"
  - "[[Budgets and Limits]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Testing Playbook]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
sources:
  - "docs-mods-reference"
  - "docs-mods-events"
  - "docs-mods-api"
  - "docs-mods-interface"
  - "types-2-1-288"
---

# Mods API Cheatsheet

One page for writing a Claude Code mod against build 2.1.288: the module skeleton, every event with what a hook may return, every `$` namespace, the render sites, the elements, and the limits. Each row links to the concept note that has the detail and citations. When this page and the types Claude Code wrote beside your mod disagree, trust the types (docs-mods-reference L11-13).

## Skeleton

```
my-mod/
  .claude-plugin/plugin.json        { "name": "my-mod", "version": "0.1.0", "types": "./types/index.d.ts" }
  hooks/hooks.json                  { "modules": ["./register.ts"] }
  hooks/register.ts                 export const register: Register = (on, options) => { ... }
  types/index.d.ts                  declare module 'claude-code' { interface PluginState { 'my-mod': { ... } } }
  tests/*.test.ts                   claude plugin test
```

```ts
import type { Register } from 'claude-code'

export const register: Register = (on, options) => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'hello', description: 'Say hi' }).catch(() => undefined)
    return next(e)
  })
  on('command.run', { command: 'hello' }, async () => ({ text: 'hi' }))
  on('tool.call', { tool: 'Bash' }, async ($, e, next) =>
    /rm -rf \//.test(e.command) ? { deny: 'Refused.' } : next(e),
  ).catch(async () => ({ deny: 'Guard failed; not run.' }))
  on('turn.step', async function* ($, e, next) { return yield* next(e) })
}
```

Detail: [[Mod Anatomy]], [[Hook Middleware Chain]].

## Hook shape

`on(event, matcher?, ($, e, next) => result)`; returns `{ catch(handler) }`. Matcher fields: value, array, RegExp, partial object. Patterns: name, `'*'` (not telemetry), `'tool.*'`, `'classic.*'`, `'!tool.call'`. `next`: `next(e)`, `.signal`, `.origin {plugin,tier}`, `.budget {ms,remainingMs}`, `.to(e, tier)` (managed only), `.is`, `.event`, `.trace`; in `.catch`: `.error {kind,message?,budget}`, `.called`. Moves: [[Observe Rewrite Answer]].

## Events and answers

| Event | Answer without `next` / rewrite | Note |
|---|---|---|
| `tool.call` | `{ deny }`, `{ result, context? }`; rewrite args | [[Tool Events]] |
| `tool.check` | `{ decision: 'allow'/'ask'/'deny', reason?, rule? }` | `e.input` is `unknown` |
| `tool.describe` | `{ description, isDeferred? }` | cached |
| `prompt.submit` | `{ drop }`; `next({...e, text})`, `next({...e, context})` | [[Prompt Events]] |
| `prompt.fill` / `prompt.suggest` | `{ isFilled: false }` / `{ isShown: false }` | |
| `prompt.edit` | `{ text, cursor }` consumes | |
| `prompt.compose` | `{ sections: [{ id, text, scope }] }`, shared before session | |
| `prompt.section` / `prompt.attachment` | `{ text }` or `{ text: null }` | cached |
| `prompt.context` | `{ blocks, instructionFiles? }` | cached |
| `skill.prompt` / `attribution.text` | `{ text }` | |
| `command.run` | `{ text?, context?, exitCode? }`, `{}` | [[Agent and Command Events]] |
| `command.describe` / `config.describe` | `{ description, argumentHint, isHidden }` / `{ label, description, isHidden }` | cached |
| `config.set` | `{ deny }`; `next({...e, value})` | |
| `turn.start` | observe | [[Turn and Session Events]] |
| `turn.step` (generator) | `yield* next({...e, model / effort})`; own chunks = no request | streams |
| `turn.complete` | `{ text }` shown beneath answer | |
| `session.start` / `session.end` | observe (`end`: 1.5 s total) | |
| `session.compact` | `{ skip }`, `{ messages }` | |
| `session.receive` / `session.send` | `{ consumed }` / `{ isDelivered: false, reason }` | |
| `session.append` | `next({...e, message})` | rewrites stored row |
| `session.attach` / `detach` / `measure` | observe | |
| `agent.offer` / `agent.spawn` | `{ isOffered: false }` / `{ model }`, `{ deny }` | |
| `ui.render` | element tree; `next({...e, props})`; wrap `await next(e)` | [[Render Sites]] |
| `ui.press` / `ui.input` / `ui.select` | `{ element }` takes it; rewrite `value` | |
| `ui.scroll` / `ui.focus` / `ui.close` / `ui.message` | `{}` or `{ deny }` / keep pane open / `{ props }` | |
| `ui.resolve` | element table, restyled or trimmed | |
| `plugin.register` / `engine.create` | `{ refuse }` / `$` with nouns added or withheld | |
| `telemetry.log` / `telemetry.mark` | `{ deny }`; needs `{ to: 'collector' }` in an installed mod | |
| `classic.<Event>` (33 events) | settings hook JSON; return `next(e)` | |
| `<ns>.<method>` (every `$` call) | `{ value }`, `{ deny }` | |

## `$` namespaces

| `$.` | Methods |
|---|---|
| `plugin` | `name`, `root` |
| `ui` | `resolve`, `invalidate`, `open`, `close`, `panes`, `focus`, `scroll`, `toast`, `status`, `log`, `notice`, `ask`, `copy`, `blit`, `selection` |
| `model` | `complete`, `fork`, `classify` |
| `session` | `messages`, `cwd`, `root`, `model`, `turns`, `id`, `repo`, `surfaces`, `surface` (deprecated for `surfaces`, types 2.1.288 L2614-2620), `usage`, `version`, `compact`, `send`, `append`, `authorize` |
| `prompt` / `turn` | `submit`, `read`, `fill`, `suggest`, `compose` / `abort` |
| `tool` / `command` / `agent` | `register`, `call`/`run`/`spawn`, `check` (tool), `list` |
| `config` / `settings` / `env` | `list`, `set` / `read` / `get`, `set` (literal names) |
| `fs` | `read`, `write`, `list`, `exists`, `stat`, `ancestors` |
| `store` / `state` | `get`, `set`, `delete`, `keys` / `get`, `set` + `atom`, `read`, `update`, `derive`, `memberOf` |
| `clock` / `http` / `process` | `now`, `sleep`, `after`, `every` / `fetch` / `run`, `spawn` (generator) |
| `mcp` / `audio` / `telemetry` | `call`, `connect` / `play`, `speak` / `log`, `mark` |

Detail: [[Mods API Namespaces]], [[State Store and Module Variables]].

## Render sites and elements

Sites: `Pane`, `AbovePrompt` (empty until a mod draws), `UserMessage`, `AssistantMessage`, `ToolUse`, `ToolResult`, `ToolGroup`, `CommandOutput`, `AskUserQuestion`, `Spinner`, `SessionMode`, `PromptHint` (terminal and desktop); `ToolProgress`, `TurnDuration`, `InfoNotice` (terminal). Surfaces in 2.1.288: `terminal`, `desktop`, `mobile`, `vscode`.

Elements via `const { Box, Text } = $.ui.resolve(e)`: all surfaces `Box`, `Text`, `Button`, `Link`, `Code`, `Markdown`; not mobile `Input`, `Select`; remote only `Svg`; terminal and desktop `Client`; terminal only `Raster`, `Image`. Narrow `e.surface` before destructuring a non-shared element. Detail: [[UI Elements and JSX]].

## Limits

| Thing | Limit |
|---|---|
| hook own time / `.catch` / linger | 10 s / 1 s / 5 s |
| all `session.end` hooks | 1.5 s wall clock |
| `$.process.run` | 30 s default, 10 min max; 4 MiB per stream |
| `$.model.complete` `maxTokens` | 1024 default, max min(64,000, model limit) |
| `$.fs` read/write; `$.store` total | 4 MiB; 4 MiB JSON |
| `$.session.messages()` | newest 4,096 |
| `Text` child, `Code`, `Markdown` / `Svg` | 10,000 chars / 131,072 chars |
| `Raster` / `Image` | 512 x 256 cells / 2 MiB |
| redraws | 10/s; 30/s terminal for visible pane, band, hint |
| unasked pane placement | 144 columns (110 once opened) |
| names (command, tool, agent, pane) | `[A-Za-z0-9_-]`, 64 chars |
| toast; test | 4 s default; 5 s per test |

Detail: [[Budgets and Limits]].

## Order

Managed `PreToolUse` → `prepend` (sec-default, `prependPlugins`, org mods) → `user` (installed; before their `dependencies`) → `append` (`appendPlugins`) → `builtin` → `core` (incl. other `PreToolUse`, permission check, tool) → `tool.check`. Detail: [[Hook Ordering and Tiers]].

## Ten gotchas

1. Returning `undefined` from a hook is a failure; return `next(e)`.
2. A hook that fails before `next` is skipped: guards fail open without `.catch`.
3. `e` is frozen; spread a copy.
4. `turn.step` and `process.spawn` hooks must be `async function*`.
5. Two bare `on('session.start', ...)` registrations fail the load.
6. `$.command.register` throws on a built-in name; register last or wrap.
7. `focus`, `closeOnEscape`, `holdToasts`, `autoFocus` accept only `true`.
8. `$.state.set` is refused inside `ui.render`; write from callbacks.
9. `/clear`, `/resume`, `/branch` reset `$.state` and skip `session.start`; reseed on `classic.SessionStart`.
10. Varying text in `prompt.section`, `prompt.compose` or `tool.describe` breaks the prompt cache.

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
Built from docs captured 2026-10-03 (describing 2.1.287) and the 2.1.288 typings. Typings-only items: `ui.selection`, `next.is/event/trace`, `lingerMs`, the `mobile`/`vscode` tables, `exitCode`. Regenerate this page after each release with [[Re-verify After Release Flow]] and see [[Versioning and API Drift]]. Testing recipes: [[Testing Playbook]].

## Related

Concepts: [[Mod Anatomy]], [[Hook Middleware Chain]], [[Observe Rewrite Answer]], [[Tool Events]], [[Prompt Events]], [[Turn and Session Events]], [[Agent and Command Events]], [[Render Sites]], [[UI Elements and JSX]], [[Mods API Namespaces]], [[State Store and Module Variables]], [[Budgets and Limits]], [[Hook Ordering and Tiers]]. Practice: [[Patterns Playbook]], [[Pitfalls Playbook]], [[Testing Playbook]].

## Sources

- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
