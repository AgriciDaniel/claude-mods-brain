---
type: "concept"
title: "Classic Hook Bridge"
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
  - "[[Mods vs Classic Hooks]]"
  - "[[Migrate a Classic Hook Flow]]"
  - "[[Turn and Session Events]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[State Store and Module Variables]]"
  - "[[Testing Kit]]"
  - "[[Patterns Playbook]]"
  - "[[Pitfalls Playbook]]"
  - "[[Tool Events]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-troubleshoot"
  - "docs-mods-test"
  - "docs-mods-reference"
  - "docs-hooks"
  - "types-2-1-288"
  - "code-modernization-1-0-0"
---

# Classic Hook Bridge

Every settings hook event (`Stop`, `SessionStart`, `PostToolUse`, and the rest) is also a mod event named `classic.` plus the event name, and `e` is the same JSON a settings hook reads on stdin, including `transcript_path` (docs-mods-events). A mod can observe these events, answer them with the same results a command hook would print, or use them to reach lifecycle moments that native mod events skip. `'classic.*'` matches all of them (docs-mods-events). The one exception is `PreToolUse`, which rides on `tool.call` rather than firing as its own `classic.` event in the testing kit (types 2.1.288 `claude-code/testing`, ClassicEvent comment).

## Three uses of the bridge

| Use | Example | Why not a native event |
|---|---|---|
| Observe a classic-only moment | `classic.Stop` to log `e.transcript_path` | No native event carries the transcript path |
| Re-seed state after `/clear`, `/resume`, `/branch` | `classic.SessionStart` with `e.source === 'clear'` loads `$.store` back into `$.state` | `session.start` does not fire again after those commands (docs-mods-reference, docs-mods-troubleshoot) |
| Answer as an in-process settings hook | return `{ block: 'reason' }` from `classic.Stop` to keep Claude going | `turn.complete` can only observe or add a line; it cannot re-prompt |

## Result shapes

A `classic.<Event>` hook returns the `ClassicResult` subset that event allows (types 2.1.288 L1103-1186, L1205-1215):

| Field | Classic JSON equivalent |
|---|---|
| `block` | `decision: "block"` with `reason`, or exit code 2 |
| `preventContinuation` | `continue: false` |
| `stopReason` | `stopReason` |
| `additionalContext` (array) | `hookSpecificOutput.additionalContext` |
| `sessionTitle`, `initialUserMessage`, `watchPaths`, `reloadSkills` | SessionStart and UserPromptSubmit specific fields |
| `updatedToolOutput`, `updatedMCPToolOutput` | PostToolUse specific fields |
| `retry`, `displayContent`, `worktreePath`, ... | PermissionDenied, MessageDisplay, WorktreeCreate fields |

`classic.PreToolUse` keeps its own `allow`, `ask`, or `deny` result type (types 2.1.288 L1205-1215).

## The pass-through rule

Return `next(e)` (or `await next(e)` and return it) so the settings hooks configured for that event still run (docs-mods-events). Answering without `next` replaces them for that event: the user's own `Stop` script, for example, never runs. For `tool.call`, a mod that answers without `next` also keeps non-managed `PreToolUse` hooks from running (docs-mods-events).

```typescript
on('classic.SessionStart', async ($, e, next) => {
  const result = await next(e)       // user's SessionStart scripts still run
  if (e.source === 'clear' || e.source === 'resume') {
    const saved = await $.store.get('count')
    if (typeof saved === 'number') await $.state.set(COUNT, saved)
  }
  return result
})
```

This is the documented shape for reloading a value after `/clear` (docs-mods-troubleshoot points to it; docs-mods-test shows the test with `source: 'clear'`). `COUNT` stands for your declared state reference.

## Alternative for /clear: hook the command

The official code-modernization plugin resets its in-memory activity with `on('command.run', { command: ['clear', 'resume'] }, ...)`, awaiting `next(e)` first (code-modernization-1-0-0 `hooks/register.ts` L1058-1068). That works for user-typed commands but not for a resume from the CLI flag, so `classic.SessionStart` with `source` is the broader hook. PRACTITIONER

## Settings hook facts that matter when bridging

- Classic matching hooks run in parallel and identical handlers in several settings files run once (docs-hooks L412). A `classic.` mod hook is in-process and sequential in the mod chain, so ordering assumptions do not carry over.
- A timed-out classic `PreToolUse` command hook does not block the call (docs-hooks L841-845). A timed-out mod hook is skipped too, unless it has a fail-closed `.catch` (docs-mods-events).
- Classic `SessionEnd` hooks share a 1.5 second budget (docs-hooks), the same figure the mods reference gives for all `session.end` hooks together (docs-mods-reference). Do not assume the two budgets are separate pools; that is unverified.
- `hooks/hooks.json` can hold both `modules` (the mod) and `hooks` (settings hooks) in one plugin (docs-mods-reference Files table).

## Recommendations

- Use `classic.SessionStart` to restore `$.state` after `/clear`, `/resume`, and `/branch`. EVIDENCE-BASED
- Always pass through with `next(e)` unless replacing the user's settings hooks is the point. EVIDENCE-BASED
- Use `classic.Stop` `{ block }` only with a loop guard; classic Stop blocks are capped at 8 consecutive continuations by default (docs-hooks, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`). Whether the same cap applies to a mod's block is undocumented. CONTESTED
- Prefer native events (`tool.call`, `prompt.submit`) over their `classic.` twins when you need to rewrite; native events take typed rewrites, classic ones mirror the stdin JSON. PRACTITIONER

## Caveats

- Whether `classic.<Event>` fires when no settings hook is configured for that event is implied by the docs' `/clear` advice but not stated directly.
- Ordering between a mod's `classic.Stop` hook and the settings `Stop` hooks it wraps is "inside `next`"; parallelism among those settings hooks is preserved by the engine, per docs-hooks, not tested here.
- The Stop continuation cap for mod blocks is unverified.

## Related

The comparison is [[Mods vs Classic Hooks]] and the procedure is [[Migrate a Classic Hook Flow]]. Native lifecycle events are in [[Turn and Session Events]] and [[Tool Events]]; chain position in [[Hook Ordering and Tiers]]; state lifetimes in [[State Store and Module Variables]]; firing classic events from tests in [[Testing Kit]]. Shapes and traps are collected in [[Patterns Playbook]] and [[Pitfalls Playbook]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- docs-mods-test: https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-hooks: https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/` (retrieved 2026-10-03)
