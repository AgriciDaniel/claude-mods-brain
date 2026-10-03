---
type: "concept"
title: "Budgets and Limits"
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
  - "[[Holding a Tool Call]]"
  - "[[Turn and Session Events]]"
  - "[[State Store and Module Variables]]"
  - "[[UI Elements and JSX]]"
  - "[[Mods API Namespaces]]"
  - "[[Usage Cost Surface]]"
  - "[[Testing Kit]]"
  - "[[Versioning and API Drift]]"
  - "[[Mods API Cheatsheet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
sources:
  - "docs-mods-reference"
  - "docs-mods-events"
  - "docs-mods-api"
  - "types-2-1-288"
  - "claudedev-getting-started"
---

# Budgets and Limits

Mods run under time budgets and size caps that Claude Code enforces per hook and per call: a hook gets 10 seconds of its own execution time per event, a `.catch` handler 1 second, and all `session.end` hooks together 1.5 seconds; a hook over budget is skipped and a call over a size cap is rejected (docs-mods-reference L239-258; C-API-012, C-API-013). The key subtlety is what the clock counts: it stops while your hook waits on `next` or on any `$` call, except "a `$.clock` wait" (types 2.1.288 L4797). That wording is wider than `$.clock.sleep` alone and may cover other `$.clock` waits; this brain has only confirmed `sleep` (types 2.1.288 L4803-4812).

## Time budgets

| Budget | Value | What counts | If exceeded | Evidence |
|---|---|---|---|---|
| Hook, per dispatch (`HookBudget.ms`) | 10,000 ms | own code only; clock stops in `next` and `$` calls, not in "a `$.clock` wait" (L4797), which is wider than `$.clock.sleep` | skipped (or `.catch` runs); if it had called `next`, that result stands | types L4812-4820; docs-mods-reference L245 |
| Streaming hook (`turn.step`, `process.spawn`) | 10,000 ms | own code only; never at a `yield` or reading the stream; `turn.step` sums over the response, `process.spawn` resets per piece | as above | types L4815-4820 |
| `.catch` handler (`catchMs`) | 1,000 ms | fresh from the moment it is called, same stopping clock | hook treated as absent | types L4821-4827; docs-mods-reference L246 |
| Linger after abort (`lingerMs`) | 5,000 ms | time a hook keeps running after `next.signal` aborted | reported as lingering; dispatch already moved on | types L4828-4836 |
| All `session.end` hooks together | 1.5 s (default) | wall clock, does not stop for `$` waits | `next.signal` aborts; `$` calls in flight abort | types L10356-10362; docs-mods-reference L247 |
| `engine.create` | none | | a failing step unloads its plugin | types L4825-4827, L4191-4199 |
| `$.process.run` | 30 s default, 10 min max (`timeoutMs`) | wall clock | rejects | types L3300-3307; docs-mods-reference L248 |
| `$.model.complete` `timeoutMs` | none by default; up to 2,147,483,647 ms | wall clock | resolves `isAnswered: false`, `reason: 'aborted'` | types L5834-5846 |
| One `claude plugin test` test | 5 s unless `timeoutMs` | | test fails | docs-mods-reference L258 |

Read the live budget with `next.budget.ms` and `next.budget.remainingMs`; `remainingMs` stands still while a `next` or `$` call is in flight, except under the `session.end` cut (types 2.1.288 L6197-6225).

```ts
import type { Register } from 'claude-code'

export const register: Register = (on) => {
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    // A $.ui.ask wait is free; a promise of your own is not
    const answer = await $.ui.ask('Run ' + e.command + '?', ['Run', 'Skip']).catch(() => 'Skip')
    if (answer !== 'Run') return { deny: 'User skipped it.' }
    if (next.budget.remainingMs > 1_000) $.ui.log('approved: ' + e.command)  // optional work only with time to spare
    return next(e)
  }).catch(async () => ({ deny: 'Guard failed; command not run.' }))
}
```

> [!warning] A timed-out guard fails open
> "Claude Code skips a hook that times out, so the held command would run." (docs-mods-events L175) Hold a tool call inside a `$` call (`$.ui.ask`, `$.process.run`), never in a busy loop or a bare `new Promise`, and add `.catch` returning `{ deny }`. See [[Holding a Tool Call]].

## Size and count caps

| Item | Cap | Evidence |
|---|---|---|
| `$.fs.read`, `$.fs.write` | 4 MiB per file | types L3010-3013; docs-mods-reference L250 |
| `$.store` | 4 MiB of JSON text in total | types L3151-3157; docs-mods-reference L252 |
| `$.process.run` stdout, stderr | 4,194,304 bytes each, rest dropped with `isStdoutTruncated`/`isStderrTruncated` | types L3302-3306, L7565-7590 |
| `$.process.spawn` unread buffer | 1,048,576 characters waiting unread (nothing dropped) | types L7610-7614 |
| `$.model.complete` `maxTokens` | default 1024; max is the lower of 64,000 and the model's output limit | types L5808-5820; docs-mods-reference L249 |
| `$.session.messages()` | newest 4,096 entries | types L2545-2549; docs-mods-reference L253 |
| `context` strings (tool.call, prompt.submit) | past 100,000 chars (200,000 together) the model reads head plus path | types L8440, L12025 |
| One `Text` string child | 10,000 characters | docs-mods-reference L251 |
| `Code` source, `Markdown` text | 10,000 characters | types L1458, L5395 |
| `Svg` source | 131,072 characters | types L11580; docs-mods-reference L232 |
| `Raster` | 512 columns by 256 rows | types L8624-8629; docs-mods-reference L234 |
| `Image` | 2 MiB decoded; 1 to 255 columns and rows | types L5011-5030 |
| `Client` posts | 20,000 values, 32 deep, 100,000 characters | types L1429 |
| `$.audio.speak` text | 4,096 characters | types L11248 |
| Command, tool, subagent type, pane names | letters, digits, `_`, `-`; up to 64 | docs-mods-reference L257; types L12341 |
| `$.ui.ask` options | 2 to 4 labels; header chip 12 characters | types L2240-2241, L521 |

## Rate limits

| Thing | Limit | Evidence |
|---|---|---|
| `$.ui.invalidate('ui.render')` redraws | 10 a second; 30 in the terminal for the visible pane, expanded band and prompt hint; sooner calls coalesce | docs-mods-reference L254; types L2167-2170 |
| `$.ui.blit` | up to 120 a second accepted, about 60 shown | types L2181-2184 |
| `$.clock.every` | period at least 1 ms | types L3248-3250 |
| `session.measure` | one at a time; a burst folds into one more | types L4133-4143 |
| `$.ui.toast` | 4,000 ms on screen unless `timeoutMs` | types L11928-11940; docs-mods-reference L255 |

## Placement thresholds

A pane opened without a user action is placed only from 144 terminal columns, or 110 once the user opened that id; a pane opened by a command or press appears at any width (C-API-054).

## Recommendations

- Do slow work through `$` (process, model, http) so it does not burn the 10 s budget; never spin. EVIDENCE-BASED
- Guards: `.catch` returning `{ deny }` plus a check of `next.budget.remainingMs` before optional work. EVIDENCE-BASED
- In `session.end`, write only small values; persist continuously instead. EVIDENCE-BASED
- Re-read this table after every Claude Code release; limits are constants in the generated types and can move. PRACTITIONER

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- `lingerMs`, spawn buffer, blit rate and the `context` cap are typings-only (2.1.288).
- Docs and typings agree on every value both state. claudedev-getting-started L394 corroborates the 10 s own-time rule.
- No limit was measured empirically in this lane.

## Related

Chain behavior on failure: [[Hook Middleware Chain]]. Holding calls safely: [[Holding a Tool Call]]. Exit timing: [[Turn and Session Events]]. Store and state caps: [[State Store and Module Variables]]. Element caps: [[UI Elements and JSX]]. Method detail: [[Mods API Namespaces]]. Token cost: [[Usage Cost Surface]]. Test timeouts: [[Testing Kit]]. Drift: [[Versioning and API Drift]]. Lookup: [[Mods API Cheatsheet]].

## Sources

- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
