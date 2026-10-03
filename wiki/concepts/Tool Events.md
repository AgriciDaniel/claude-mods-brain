---
type: "concept"
title: "Tool Events"
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
  - "[[Observe Rewrite Answer]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Build a Tool Call Guard Flow]]"
  - "[[Holding a Tool Call]]"
  - "[[Classic Hook Bridge]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Mods API Namespaces]]"
  - "[[Org Mod Controls]]"
  - "[[Mods API Cheatsheet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-reference"
  - "docs-mods-api"
  - "types-2-1-288"
---

# Tool Events

Three events cover every tool Claude uses: `tool.call` fires when a tool is about to run and can refuse, rewrite, answer or wrap it; `tool.check` fires when Claude Code decides whether the call may run and can flip the decision; `tool.describe` fires once per tool to change the description Claude reads (docs-mods-reference L50-58). They cover built-in tools, MCP tools, a mod's own registered tools, and calls made inside subagents (docs-mods-events L100).

## Event summary

| Event | Fires | `e` | A hook returns | Evidence |
|---|---|---|---|---|
| `tool.call` | tool about to run; `next(e)` runs permission check, dialog, then the tool | `{ tool, tool_use_id, ...args, agentId? }` | `next(e)`, `{ deny }`, `{ result, context? }` | types 2.1.288 L3733-3741, L11952-11961 |
| `tool.check` | after `tool.call` and `PreToolUse` hooks, before the mode settles an `ask` | `{ tool, input: unknown, tool_use_id? }` | `{ decision: 'allow' or 'ask' or 'deny', reason?, rule? }` | types L3742-3753, L12088-12156 |
| `tool.describe` | once per tool per session, when its schema is first rendered | `{ tool, description, isDeferred?, provider }` | `{ description, isDeferred? }` | types L3946-3958, L12164-12207 |

## `tool.call` in detail

- `e.tool` is the model-facing name: `Bash`, `Read`, `mcp__server__tool`, or `mcp__<plugin>__<name>` for a mod's tool (types 2.1.288 L12209-12222).
- Arguments are spread on `e`: `e.command` for Bash, `e.file_path` for Edit, Write and Read. With the build's `claude-code-tools` types, `e.tool === 'Bash'` (or a `{ tool: 'Bash' }` matcher) narrows them (types L860-869).
- `tool`, `tool_use_id` and `agentId` are reserved; a rewrite of them is refused (C-API-018).
- A reserved `consent` key carries the user's own words when a button press raised the call (types L11971-11984).

Result union (C-API-019, types 2.1.288 L11986-12085):

| Arm | Fields | Who produces it |
|---|---|---|
| refused | `{ deny: string }` | a hook, a managed `PreToolUse`, or the permission flow |
| answered | `{ result, context?, ref?, text?, isReadOnly? }` | core (all fields) or a hook (`result`, `context`) |
| errored | `{ isError: true, result, text?, ref?, context? }` | core, when the tool threw, was interrupted, or answered an error |

`context` is a list of strings the model reads after the result and the user never sees, like a `PostToolUse` reminder; past 100,000 characters (200,000 together) the model reads a head plus a path (C-API-020). After `e.tool` narrows, `result` is typed from `BuiltinToolResults` (types L877-890, L12307).

```ts
import type { Register } from 'claude-code'

export const register: Register = (on) => {
  // Post-edit check: append a reminder Claude reads, user does not
  on('tool.call', { tool: ['Edit', 'Write'] }, async ($, e, next) => {
    const r = await next(e)
    if (r.deny !== undefined || r.isError === true) return r
    if (!e.file_path.endsWith('.ts')) return r
    const tsc = await $.process.run(['npx', 'tsc', '--noEmit', '-p', '.'], { timeoutMs: 60_000 })
    if (tsc.exitCode === 0) return r
    return { ...r, context: [...(r.context ?? []), 'tsc failed:\n' + tsc.stdout.slice(0, 4000)] }
  }).catch(async ($, e, next) => {
    // Fail open on purpose: this hook only annotates. next(e) is replay safe here.
    $.ui.log('tsc check skipped: ' + next.error.kind, { to: 'debug' })
    return next(e)
  })
}
```

Inside `.catch`, `next(e)` is replay safe: if the hook had already called it (`next.called`), the settled result comes back without running the tool again (types 2.1.288 L1005-1011).

## Holding a call

A `tool.call` hook can `await` before calling `next`; the tool call stays pending. Keep the wait inside a `$` call such as `$.ui.ask`, because only your own code time counts against the 10 s budget; a hook that times out is skipped and the held command would run (docs-mods-events L138-175). Full pattern in [[Holding a Tool Call]].

```ts
on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
  if (!/\brm\s+-rf?\b/.test(e.command)) return next(e)
  let answer = 'Refuse'
  try { answer = await $.ui.ask('Run this command? ' + e.command, ['Run it', 'Refuse']) } catch {}
  return answer === 'Run it' ? next(e) : { deny: 'The user declined this command.' }
})
```

`$.ui.ask` takes 2 to 4 labels, resolves to the label or typed text, and rejects when dismissed or in `claude -p` (C-API-057).

## `tool.check`: the permission decision

`next(e)` resolves to what the rules, the permission mode, the tool's own check and `PreToolUse` decided; your hook returns that or another verdict in either direction (C-API-021). Use it for decisions that depend on live state; use a permission rule such as `Bash(npm test)` for fixed ones (docs-mods-events L181).

```ts
on('tool.check', { tool: 'Bash' }, async ($, e, next) => {
  const decided = await next(e)
  const input = e.input as { command?: unknown }
  const command = typeof input.command === 'string' ? input.command : ''
  if (!command.includes('git push')) return decided
  const branch = await $.process.run(['git', 'branch', '--show-current'])
  return branch.stdout.trim() === 'main'
    ? { decision: 'deny', reason: 'Push from a branch other than main.' }
    : decided
})
```

> [!contradiction] `e.input` type
> The docs example reads `e.input.command` directly (docs-mods-events L189). In the 2.1.288 typings `input` is `unknown` (types L12110-12115), so strict TypeScript needs the narrowing above. TypeScript 5.9.3 against the 2.1.288 typings rejects the docs form with TS18046 and accepts the narrowed form. Runtime behavior is the same; typings win for `.ts` mods ([[Contradictions Register#API and events]] X6).

`$.tool.check({ tool, input })` asks the same chain without running anything and without a `tool_use_id` (types L2822-2831).

## Where settings hooks sit

| Hook | Position | Can a mod override it? |
|---|---|---|
| Managed-settings `PreToolUse` | before the first mod's `tool.call`; block is final | no |
| Other `PreToolUse` (user, project, plugin `hooks.json`) | after the last mod calls `next`, inside core | a `tool.check` hook can approve what it blocked |
| `tool.check` | after both, before an `ask` is shown | it is the last word up the chain |

Evidence: docs-mods-events L296-303; C-API-017. Org options `allowModsToOverrideDenyRules` and `allowManagedModsOnly` change what a user mod may approve (docs-mods-reference L269-270); see [[Org Mod Controls]].

## `tool.describe` and the prompt cache

Answers are cached for the session until `$.ui.invalidate('tool.describe')`; an unstable description "spends the model's prompt cache" every time (types 2.1.288 L3946-3958). `isDeferred: true` moves a tool behind ToolSearch, `false` puts its schema in the prompt list. See [[Prompt Cache Discipline]].

## Adding your own tool

```ts
on('session.start', async ($, e, next) => {
  await $.tool.register({
    name: 'ticket',
    description: 'Look up a ticket by id; returns title and status.',
    inputSchema: { type: 'object', properties: { id: { type: 'string' } }, required: ['id'] },
  })
  return next(e)
})
on('tool.call', { tool: 'mcp__my-mod__ticket' }, async ($, e) => {
  const id = String((e as { id?: unknown }).id ?? '')
  const r = await $.http.fetch('https://tickets.example.com/api/' + encodeURIComponent(id))
  return { result: r.ok ? r.text : 'Lookup failed with status ' + r.status }
})
```

Full name is `mcp__<plugin>__<name>`; names are 1 to 64 of letters, digits, `_`, `-`; a call no hook answers fails; `register` rejects until the session binds at `session.start` (C-API-023; docs-mods-api L41-66). The cast is needed because a mod tool's arguments are not in the generated MCP types.

## Recommendations

- Guard with `tool.call` plus `.catch` returning `{ deny }`, so the guard fails closed. EVIDENCE-BASED
- Decide permission in `tool.check`, not by answering `tool.call`, when you want the normal dialog and settings hooks to keep working. EVIDENCE-BASED
- Treat text-pattern guards as reminders; protect real invariants (branch protection) on the server. EVIDENCE-BASED
- Keep `tool.describe` answers stable for the session. EVIDENCE-BASED

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- `consent`, `isReadOnly`, and the `context` cap are typings-only in 2.1.288.
- `tool.call` for a mod's own `$.tool.call` runs every hook except the calling one (types L2810-2813).

## Related

Chain mechanics: [[Hook Middleware Chain]], [[Observe Rewrite Answer]], [[Hook Ordering and Tiers]]. Build steps: [[Build a Tool Call Guard Flow]], [[Holding a Tool Call]]. Bridging old hooks: [[Classic Hook Bridge]]. Cache effects: [[Prompt Cache Discipline]]. Org policy: [[Org Mod Controls]]. API surface: [[Mods API Namespaces]], [[Mods API Cheatsheet]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
