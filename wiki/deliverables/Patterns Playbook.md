---
type: "deliverable"
title: "Patterns Playbook"
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
lane: "patterns-and-ideas"
related:
  - "[[Pitfalls Playbook]]"
  - "[[Observe Rewrite Answer]]"
  - "[[Holding a Tool Call]]"
  - "[[Band and Pane Fallback]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Classic Hook Bridge]]"
  - "[[Playground Sample Mods]]"
  - "[[code-modernization Plugin]]"
  - "[[State Store and Module Variables]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Ranked Build Ideas]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-api"
  - "docs-mods-interface"
  - "docs-mods-reference"
  - "docs-mods-admin"
  - "docs-mods-overview"
  - "claudedev-getting-started"
  - "code-modernization-1-0-0"
  - "pa-gh-91870-mined"
  - "types-2-1-288"
---

# Patterns Playbook

Twenty-five reusable shapes, plus one structure pattern, for Claude Code mods on 2.1.288, each tied to an official example, or Anthropic's own mod code. Every pattern is a variation of three moves: observe (`return next(e)` or `await next(e)` then return), rewrite (`next({ ...e, field })`), and answer (return a result without `next`) (docs-mods-events). Pick by the problem column, copy the shape, then check the matching row in [[Pitfalls Playbook]].

## Event patterns

| # | Pattern | Problem | Shape | Reference |
|---|---|---|---|---|
| E1 | Observe after the fact | Record what actually happened | `const r = await next(e); if (!r.deny && !r.isError) record(e); return r` | docs-mods-events |
| E2 | Rewrite with a copy | Normalise input | `return next({ ...e, text: e.text.trim() })` | docs-mods-events |
| E3 | Rewrite plus tell Claude | Avoid the model's stale view of its own input | Add `context` with what changed | staff on #91870 (c5531157307) |
| E4 | Actionable deny | Refuse in a way Claude can recover from | `{ deny: 'X is off here. Use Y instead.' }` | docs-mods-events |
| E5 | Fail-closed guard | Guard must not fail open | `on(...).catch(async () => ({ deny: 'guard failed' }))` | docs-mods-events |
| E6 | Hold for a decision | Ask before a risky call | Await `$.ui.ask`, default refuse | [[Holding a Tool Call]] |
| E7 | Live-state permission | Allow or deny by branch or recorded value | `tool.check`, `const d = await next(e)` then override | docs-mods-events |
| E8 | Retry | Transient tool failure | `let r = await next(e); if (r.isError) r = await next(e); return r` | docs-mods-events |
| E9 | Bracket a turn | Group edits per answer | Reset on `turn.start`, publish on `turn.complete`, skip `e.agentId` | claudedev-getting-started (Replay Theater) |
| E10 | Line under the answer | Report after each turn | `turn.complete` returns `{ ...r, text }`, keeping earlier text | docs-mods-events |
| E11 | Gated context | Add facts only when relevant | Regex and `e.origin.kind` gate, then `next({ ...e, context: [...] })` | docs-mods-events; [[Prompt Cache Discipline]] |
| E12 | Steer compaction | Keep rules through summaries | `session.compact` `next({ ...e, instructions })` | types 2.1.288 L10110-10140 |
| E13 | Prebuilt teardown | Save at exit within 1.5 s | Build on `turn.complete`, only write on `session.end` | docs-mods-reference |
| E14 | Concurrent links | Several independent slow checks | Start `const p = next(e)` before your work, await later | staff on #91870 (c5618866247) |
| E15 | Classic bridge | Moments native events skip | `classic.SessionStart` with `e.source`; `classic.Stop` `{ block }` | [[Classic Hook Bridge]] |

## Interface patterns

| # | Pattern | Problem | Shape | Reference |
|---|---|---|---|---|
| U1 | Command with no turn | Instant user action | `$.command.register({ name, immediate: true })` last in `session.start`, in try/catch; `command.run` returns `{ text }` or `{}` | docs-mods-api |
| U2 | Shared band | Always-visible readout | `AbovePrompt`, yield on `hasSurvey`, compose `await next(e)` | docs-mods-interface; claudedev-getting-started; [[Band and Pane Fallback]] |
| U3 | Pane on demand, band fallback | Rich view without stealing space | Open from a command or button; on `isPlaced: false` draw in the band | [[Band and Pane Fallback]]; code-modernization L779-835 |
| U4 | Reactive state | Redraw without bookkeeping | Values in `$.state` (declared in `types/index.d.ts`); reads subscribe the drawing | docs-mods-interface; claudedev-getting-started |
| U5 | Timer refresh | Data from outside the session | `$.clock.every(ms, () => void refresh($).catch(() => undefined))` started in `session.start` | docs-mods-api |
| U6 | Ask before a destructive button | Buttons that kill or delete | Button `onPress` awaits `$.ui.ask`, default keep | [[Holding a Tool Call]] (worked example) |
| U7 | Text fallback | `-p`, VS Code panel, cloud | Same data through `{ text }` on a command or `turn.complete` | docs-mods-overview |

## API patterns

| # | Pattern | Problem | Shape | Reference |
|---|---|---|---|---|
| A1 | Cheap label | Sort text without the main model | `$.model.complete({ model: 'haiku', system, prompt, maxTokens: 20, timeoutMs: 15000 })`; check `r.isAnswered` | docs-mods-api |
| A2 | Context question | Ask about the conversation cheaply | `$.model.fork({ prompt })`, rides the cache | docs-mods-api; types 2.1.288 L2415-2433 |
| A3 | Tool for Claude | Give Claude a capability | `$.tool.register` in `session.start`; handle `tool.call` on `mcp__<plugin>__<name>` | docs-mods-api |

## Structure pattern

Keep `hooks/register.ts` as the only file that calls `on()`, put logic in `hooks/lib/*.ts` as pure functions, and unit test those without the engine. Validate then lists every hook and call from one file, which keeps review cheap (docs-mods-admin). PRACTITIONER

## Two shapes worth copying in full

Observe-and-report under the answer (E1 plus E10):

```typescript
let edited = new Set<string>()
export const register: Register = (on) => {
  on('tool.call', { tool: ['Edit', 'Write'] }, async ($, e, next) => {
    const r = await next(e)
    if (!('deny' in r && r.deny) && !('isError' in r && r.isError)) edited.add(e.file_path)
    return r
  })
  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    if (e.agentId !== undefined || edited.size === 0) return r
    const line = edited.size + ' files changed'
    edited = new Set()
    return { ...r, text: r.text ? r.text + '\n' + line : line }
  })
}
```

Shared band with survey yield (U2):

```typescript
on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
  const { value: rows = [] } = await $.state.get(ROWS)
  if (e.props.hasSurvey || rows.length === 0) return next(e)
  const { Box, Text } = $.ui.resolve(e)
  const theirs = await next(e)
  const mine = Text({ dimColor: true, children: [rows.join('  ').slice(0, e.props.bodyColumns)] })
  return theirs ? Box({ flexDirection: 'column', children: [mine, theirs] }) : mine
})
```

`ROWS` is a declared `$.state` reference such as `{ plugin: 'my-band', key: 'rows' }` (claudedev-getting-started).

## Recommendations

- Start from the official examples (Token Weather, Blast Radius, Replay Theater, code-modernization) before community repos. EVIDENCE-BASED
- Default to observe; rewrite only with a `context` note; answer only to deny or to serve your own command or tool. PRACTITIONER
- Use `$.state` for anything a drawing reads; use module variables only for values you can lose. EVIDENCE-BASED
- Give every drawing mod a text path for surfaces that do not draw. EVIDENCE-BASED

## Caveats

- Patterns E3 and E14 come from staff comments on pre-release builds, not from the docs.
- Snippets were checked against the 2.1.288 typings by reading, not compiled or run here.

## Related

Each pattern's failure side is in [[Pitfalls Playbook]], and the three moves in [[Observe Rewrite Answer]]. Deep dives: [[Holding a Tool Call]], [[Band and Pane Fallback]], [[Prompt Cache Discipline]], [[Classic Hook Bridge]]. Reference code: [[Playground Sample Mods]], [[code-modernization Plugin]]. Lifetimes are in [[State Store and Module Variables]], signatures in [[Mods API Cheatsheet]], and the ideas these enable in [[Ranked Build Ideas]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/` (retrieved 2026-10-03)
- pa-gh-91870-mined: `.raw/captures/lanes-2026-10-03/patterns-and-ideas/gh-issue-91870-mined.md`
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
