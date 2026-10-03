---
type: "concept"
title: "Render Sites"
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
  - "[[UI Elements and JSX]]"
  - "[[State Store and Module Variables]]"
  - "[[Budgets and Limits]]"
  - "[[Build a Pane Flow]]"
  - "[[Build a Status Band Flow]]"
  - "[[Band and Pane Fallback]]"
  - "[[Observe Rewrite Answer]]"
  - "[[Testing Kit]]"
  - "[[code-modernization Plugin]]"
  - "[[Mods API Cheatsheet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
sources:
  - "docs-mods-reference"
  - "docs-mods-interface"
  - "types-2-1-288"
  - "code-modernization-1-0-0"
---

# Render Sites

A render site is a named place in Claude Code's interface where a `ui.render` hook may draw: two empty sites a mod fills (`Pane`, `AbovePrompt`), and thirteen sites Claude Code already draws that a mod can restyle, wrap or replace (C-API-048). Each `ui.render` call carries `e.component` (the site), `e.surface` (which app draws), `e.requestId` (which instance), `e.viewport` and `e.props` (types 2.1.288 L9054-9095). The permission prompt is not a render site, so no mod can change it (docs-mods-interface L292).

## The fifteen sites and their props

| Site | `e.props` (2.1.288) | `e.requestId` | Raised on (docs) | Evidence |
|---|---|---|---|---|
| `Pane` | `title`, `isFocused`, `bodyColumns`, `placement: 'dock' or 'inline'`, `scroll`, `view` | pane `id` | Terminal, Desktop | types L9632-9675 |
| `AbovePrompt` (the band) | `hasSurvey`, `isWorking`, `maxRows`, `bodyColumns`, `scroll`, `view` | one instance | Terminal, Desktop | types L9578-9625 |
| `UserMessage` | `text`, `origin`, `isExpanded`, `task?`, `from?`, `onScreen?` | message id | Terminal, Desktop | types L9139-9190 |
| `AssistantMessage` | `text`, `isFirstOfReply`, `onScreen?` | message id | Terminal, Desktop | types L9193-9214 |
| `ToolUse` | `tool`, `input`, `isRunning`, `isErrored`, `isInterrupted`, `output?`, `onScreen?` | tool call id | Terminal, Desktop | types L9219-9270 |
| `ToolResult` | `tool`, `output`, `isErrored`, `onScreen?` | tool call id | Terminal, Desktop | types L9278-9313 |
| `ToolGroup` | `calls: ToolGroupCall[]`, `isActive`, `isExpanded`, `onScreen?` | tool call id | Terminal, Desktop | types L9323-9352 |
| `CommandOutput` | `command`, `args`, `text`, `isErrored`, `onScreen?` | message id | Terminal, Desktop | types L9361-9396 |
| `AskUserQuestion` | `tool`, `questions`, `metadataSource?` | tool call id | Terminal, Desktop | types L9113-9130 |
| `ToolProgress` | `kind: 'background_hint'`, `hint` | tool call id | Terminal | types L9405-9428 |
| `Spinner` | `word`, `message`, `suffix`, `mode` | agent id | Terminal, Desktop | types L9436-9464 |
| `TurnDuration` | `word`, `durationMs`, `onScreen?` | message id | Terminal | types L9469-9490 |
| `InfoNotice` | `text`, `command`, `onScreen?` | message id | Terminal | types L9495-9516 |
| `SessionMode` | `modes` | one instance | Terminal, Desktop | types L9524-9531 |
| `PromptHint` | `isDraft`, `isWorking`, `hint`, `tail?` | one instance | Terminal, Desktop | types L9541-9570 |

`Spinner.mode` is `requesting`, `responding`, `thinking`, `tool-input` or `tool-use` (types L9461). `scroll` is `{ offset, bodyRows }`; `view` is `{ agentId? }`, set while the user views an agent's transcript (types L11159-11193). "Raised on" is from docs-mods-reference L192-206; the typings do not list surfaces per site in this file.

> [!contradiction] How many surfaces exist
> Docs say `e.surface` is `terminal` or `desktop` (docs-mods-reference L190). The 2.1.288 typings declare `'terminal' | 'desktop' | 'mobile' | 'vscode'`: Ink in the terminal, Claude Code Desktop, the Claude mobile app, and Claude Code for VS Code, each remote surface asking over the wire and drawing the tree itself (types L9683-9695). A session may draw on several at once (types L2600-2612). Typings win: never assume a two-way branch (C-API-049; [[Contradictions Register#API and events]] X1).

## Viewport and sizing

`e.viewport` is `{ columns, rows, isFullscreen? }`, absent until measured; `rows` is the whole window, not your site (types 2.1.288 L9705-9735; docs-mods-reference L208). Fit rules (docs-mods-reference L210-216):

- Width of a `Pane` or the band: draw to `e.props.bodyColumns`.
- Docked pane (`placement: 'dock'`): height is `e.props.scroll.bodyRows`.
- Inline pane (`placement: 'inline'`): grows with the tree up to a limit; `$.ui.open({ rows })` asks for another limit.
- A tree taller than the site scrolls as a whole.

Pane placement: opened by a user action, it appears at any width; opened by the mod alone, only from 144 columns, or 110 once the user opened that id (C-API-054). In a narrow terminal the pane sits above the prompt instead of beside the transcript (docs-mods-interface L17).

## Three ways to treat an existing site

```ts
import type { Register } from 'claude-code'

let calls = 0

export const register: Register = (on) => {
  on('tool.call', async ($, e, next) => { calls += 1; $.ui.invalidate('ui.render'); return next(e) })

  // Change a detail: keep Claude Code's spinner, rewrite one prop
  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    if (calls === 0) return next(e)
    return next({ ...e, props: { ...e.props, suffix: ' · tool calls: ' + calls } })
  })

  // Wrap: place the engine's drawing beside your own element
  on('ui.render', { component: 'TurnDuration' }, async ($, e, next) => {
    const { Box, Text } = $.ui.resolve(e)
    const theirs = await next(e)
    return Box({ flexDirection: 'column', children: [theirs, Text({ dimColor: true, children: [calls + ' tool calls'] })] })
  })
}
```

At sites Claude Code draws, `next(e)` returns a reference `{ type: 'engine', ref }` unless a later mod returned its own tree (docs-mods-interface L280). A rewritten `props` object is validated by the component; an invalid one draws the original (types 2.1.288 L9099-9106). For `AskUserQuestion`, a tree must hold the engine reference exactly once with your elements above it, or Claude Code draws its own dialog (docs-mods-interface L292).

## The band and the pane

- The band (`AbovePrompt`) is always present and shared by every mod. Returning a tree replaces what later mods draw; to keep theirs, include `await next(e)` in your `Box` (docs-mods-interface L201-206). Yield to surveys: `if (e.props.hasSurvey) return next(e)`, as the official mod does (code-modernization-1-0-0 `register.ts` L779-800).
- A pane exists only after `$.ui.open({ id })`; filter `{ component: 'Pane' }` and check `e.requestId === id` (docs-mods-interface L194-198).

## Interaction events tied to sites

| Event | `e` | Default (core) | Evidence |
|---|---|---|---|
| `ui.press` | `plugin`, `element` (key), `component`, `requestId`, `surface`, `link?` | runs the Button's `onPress` | types L3775-3783, L13231-13273 |
| `ui.input` | adds `kind: 'change' or 'submit'`, `value` | runs `onInput`/`onSubmit` | types L3785-3792, L13015-13057 |
| `ui.select` | adds `value` | runs `onSelect` | types L3794-3801, L13473-13511 |
| `ui.scroll` | site, offset, `by` | moves to `e.offset` | types L3812-3822 |
| `ui.focus` | site, `element` | lands on `e.element` | types L3824-3834 |
| `ui.close` | `id`, `origin.kind: 'plugin' or 'person' or 'unload'` | closes; answering keeps it open except on unload | types L2298-2310, L6896-6931 |
| `ui.message` | `surface`, `component`, `requestId`, `element`, `module`, `data` | `{}`; only the owning plugin sees it | types L3803-3810, L13096-13135 |

Another mod's `ui.press`/`ui.input` hook runs before your callback and can rewrite or swallow it (docs-mods-interface L486). Key every control.

## When a drawing does not show

A tree with an unknown element, a prop an element does not take, or a child where none goes fails validation; Claude Code draws its own site instead. Under `--plugin-dir` a line such as `ui.render (Pane) refused: Text prop "bogusProp" is not allowed; the engine drew its own` explains it, and the debug log records the same (C-API-051; docs-mods-interface L430-432).

## Recommendations

- Filter every `ui.render` hook with `{ component }` and, for panes, check `requestId`; an unfiltered hook runs for every site. EVIDENCE-BASED
- Branch on `e.surface` and keep a text fallback for surfaces without your element; see [[Band and Pane Fallback]]. EVIDENCE-BASED
- In the band, yield on `hasSurvey` and include `await next(e)` when you only add a line. EVIDENCE-BASED
- Draw to `bodyColumns`, never to `viewport.columns`. EVIDENCE-BASED

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- Per-site surface support is from the docs (two surfaces); behavior on `mobile` and `vscode` was not observed.
- `onScreen`, `view`, `tail`, `isFirstOfReply` are typings-only props in 2.1.288.

## Related

Elements and JSX: [[UI Elements and JSX]]. Redraw and state: [[State Store and Module Variables]], [[Budgets and Limits]]. Build steps: [[Build a Pane Flow]], [[Build a Status Band Flow]], [[Band and Pane Fallback]]. Moves: [[Observe Rewrite Answer]]. Testing drawings: [[Testing Kit]]. A rich real example: [[code-modernization Plugin]]. Lookup: [[Mods API Cheatsheet]].

## Sources

- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/` (retrieved 2026-10-03)
