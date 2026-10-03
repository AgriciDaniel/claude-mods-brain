---
type: "concept"
title: "Agent and Command Events"
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
  - "[[Turn and Session Events]]"
  - "[[Tool Events]]"
  - "[[Mods API Namespaces]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Build a Slash Command Flow]]"
  - "[[Org Mod Controls]]"
  - "[[Built-in sec-default Mod]]"
  - "[[Built-in telemetry Mod]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Mods API Cheatsheet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
sources:
  - "docs-mods-reference"
  - "docs-mods-api"
  - "docs-mods-interface"
  - "types-2-1-288"
  - "code-modernization-1-0-0"
---

# Agent and Command Events

This note covers the events that govern who and what runs: subagents (`agent.offer`, `agent.spawn`), slash commands (`command.run`, `command.describe`), `/config` rows (`config.set`, `config.describe`), other mods (`plugin.register`, `engine.create`) and telemetry (`telemetry.log`, `telemetry.mark`) (docs-mods-reference L76-150). Commands are how a mod gives the user an entry point; `agent.*` lets a mod hide, reroute or refuse subagents; `plugin.register` and `engine.create` are the governance layer organizations use against other mods.

## Subagents

| Event | Fires | `e` (main fields) | Answer | Evidence |
|---|---|---|---|---|
| `agent.offer` | a type is listed for the model, and again at dispatch | `agent`, `description`, `source`, `provider` | `{ isOffered: false }` hides and refuses it | types 2.1.288 L3836-3845, L192-227 |
| `agent.spawn` | the Agent tool is about to start a subagent | `tool_use_id`, `prompt`, `description`, `subagentType`, `provider`, `model?`, `parentModel`, `parentAgentId?`, `permissionMode?`, `background`, `fork`, `name?`, `cwd?` | `{ model }`, `next({ ...e, model })`, `{ deny }` | types L3847-3854, L239-360 |

- Rewritable on `agent.spawn`: `prompt`, `description`, `subagentType` (must name a dispatchable type), `model`, `background`, `cwd`. Pinned: `tool_use_id`, `provider`, `parentModel`, `parentAgentId`, `permissionMode`, `fork`, `name` (types 2.1.288 L239-330).
- `model` is ignored for forks, which always inherit (L281-286).
- A hook that fails on `agent.offer` passes the type through (L3840-3841).

```ts
import type { Register } from 'claude-code'

export const register: Register = (on) => {
  on('agent.offer', { agent: 'Plan' }, () => ({ isOffered: false }))
  on('agent.spawn', async ($, e, next) => {
    if (e.subagentType === 'Explore' && e.model === undefined) return next({ ...e, model: 'haiku' })
    return next(e)
  })
}
```

Mod-side API (types 2.1.288 L2962-3005): `$.agent.spawn({ prompt, description?, subagentType?, model?, name?, cwd? })` resolves `{ model, agentId }` once started (always background) or `{ deny }`; the answer arrives as that agent's `turn.complete`. `$.agent.list()` returns `{ id, description, type, status, parentId?, spawnedBy?, name? }`. `$.agent.register(spec)` defines `<plugin>:<name>` with any agent-file field: `tools`, `disallowedTools`, `model`, `effort`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `initialPrompt`, `memory`, `background`, `omitClaudeMd`, `isolation` (L362-458; C-API-039).

## Commands

| Event | Fires | `e` | Answer | Evidence |
|---|---|---|---|---|
| `command.run` | `/name args` typed, or `$.command.run` | `command`, `args`, `origin`, `presentation: { isFullscreen, columns }` | `{ text?, context?, exitCode? }`; `{}` prints nothing | types L3960-3970, L1599-1698 |
| `command.describe` | once per command for typeahead and `/help` | `command`, `description`, `argumentHint?`, `isHidden`, `immediate`, `provider` | `{ description, argumentHint, isHidden }`, cached | types L3972-3982, L1507-1548 |

```ts
on('session.start', async ($, e, next) => {
  try {
    await $.command.register({ name: 'standup', description: 'Summarize today', argumentHint: '[days]', immediate: true })
  } catch (err) {
    $.ui.log('standup not registered: ' + String(err), { to: 'debug' })
  }
  return next(e)
})
on('command.run', { command: 'standup' }, async ($, e) => {
  const days = Number(e.args || '1')
  return { text: 'Summary for the last ' + days + ' day(s): ...' }
})
```

Rules (C-API-024, C-API-025):

- A built-in name is refused and `register` throws, for example `"/focus" refused: it is the built-in /focus` (docs-mods-api L39). Register last or wrap in `try`.
- `immediate: true` lets the command run while Claude is working; without it a command typed mid-turn waits (docs-mods-interface L330).
- `text` prints in the transcript after the plugin's name and Claude reads it; `context` entries are hidden notes for the model; `exitCode` 0 to 255 sets the exit status of a headless `claude -p "/cmd"` run (types 2.1.288 L1668-1691).
- A registered command has no core behavior, so a run no hook answers says so as its output (L2878-2880).
- `command.run` can also wrap built-ins: the official mod hooks `{ command: ['clear', 'resume'] }` (code-modernization-1-0-0 `register.ts` L1058).

`CommandSource` for `$.command.list()`: `builtin`, `plugin`, `user`, `mcp` (types L1699).

## `/config` rows

| Event | `e` | Answer | Evidence |
|---|---|---|---|
| `config.set` | `key`, `value`, `previous`, `provider`, `origin` | `next({ ...e, value })` to clamp, `{ deny }` to refuse | types L3984-3994, L1852-1904 |
| `config.describe` | `key`, `label`, `description?`, `isHidden`, `provider` | `{ label, description, isHidden }`, cached | types L3996-4006, L1739-1773 |

Row kinds: `boolean`, `choice`, `text`, `number` (types L1775). A row a trusted source owns is core's to refuse. `$.config.list()` and `$.config.set({ key, value })` cover every row, including each enabled plugin's `userConfig` fields (L2893-2918); see [[userConfig and Plugin Options]].

## Other mods: `plugin.register` and `engine.create`

| Event | `e` | Answer | Evidence |
|---|---|---|---|
| `plugin.register` | `name`, `tier`, `root`, `version?`, `provenance`, `uses: { events, calls, env?, state? }` | `{ refuse: reason }`: no hook, noun or tool of it loads | types L4157-4167, L7207-7310 |
| `engine.create` | `plugins` (the modules this fold builds) | the `$` table with nouns added or withheld | types L4191-4199, L3701-3723 |

`e.uses.calls` spells calls without `$.`, such as `fs.read`, exactly as `claude plugin validate` prints them (docs-mods-reference L141). An `engine.create` step may add and withhold nouns but may not replace one another step added; a failing step unloads its plugin, and the hook has no budget (types 2.1.288 L4191-4199, L8690-8694). These are the hooks an org guard such as [[Built-in sec-default Mod]] uses; see [[Org Mod Controls]].

```ts
on('plugin.register', { tier: 'user' }, async ($, e, next) => {
  if (e.uses.calls.includes('process.run')) return { refuse: 'Process access is managed-only here.' }
  return next(e)
})
```

## Telemetry

`telemetry.log` and `telemetry.mark` fire for usage records. In an installed mod a telemetry hook must carry `{ to: 'collector' }`, or `claude plugin validate` fails it; `'*'` never matches these events (C-API-059). `e.to` is pinned; `{ deny }` rejects the caller (types 2.1.288 L4008-4029). A record reaches a destination only when Claude Code or a built-in makes the call (docs-mods-reference L186). See [[Built-in telemetry Mod]].

## Recommendations

- Register commands with `try`/`catch` inside `session.start`, after tools and timers. EVIDENCE-BASED
- Use `agent.spawn` model rewrites for cost routing; leave forks alone, they ignore `model`. EVIDENCE-BASED
- Use `plugin.register` refusals by `tier` and `uses`, never by plugin name strings alone. PRACTITIONER
- Do not write telemetry hooks in personal mods; there is no first-party destination for them. EVIDENCE-BASED

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- `exitCode`, agent spec fields and `plugin.register` input detail are typings-only (2.1.288).
- Org-level behavior (managed tiers) was not exercised; see the security lane notes.

## Related

Turn and session plumbing: [[Turn and Session Events]]. Tool side: [[Tool Events]]. Ordering of org guards: [[Hook Ordering and Tiers]]. Build steps: [[Build a Slash Command Flow]]. Governance: [[Org Mod Controls]], [[Built-in sec-default Mod]], [[Built-in telemetry Mod]]. Options: [[userConfig and Plugin Options]]. API: [[Mods API Namespaces]], [[Mods API Cheatsheet]].

## Sources

- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/` (retrieved 2026-10-03)
