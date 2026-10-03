---
type: "concept"
title: "Holding a Tool Call"
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
  - "[[Tool Events]]"
  - "[[Hook Middleware Chain]]"
  - "[[Budgets and Limits]]"
  - "[[Build a Tool Call Guard Flow]]"
  - "[[Band and Pane Fallback]]"
  - "[[Playground Sample Mods]]"
  - "[[Pitfalls Playbook]]"
  - "[[Patterns Playbook]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Mods vs Classic Hooks]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-reference"
  - "docs-mods-troubleshoot"
  - "claudedev-getting-started"
  - "types-2-1-288"
---

# Holding a Tool Call

A `tool.call` hook can pause a tool call by awaiting before it calls `next(e)` or returns; the call stays pending until the hook settles (docs-mods-events). The documented way to hold is to await `$.ui.ask`, because time spent inside a mods API call does not count against the hook's 10 second budget, while time spent awaiting your own promise does (docs-mods-events, docs-mods-reference). A hold that times out is skipped, which means the held command runs, so every hold needs a fail-closed `.catch` (C-PAT-004).

## The two documented hold shapes

| Shape | Source | How the wait is spent | Notes |
|---|---|---|---|
| `$.ui.ask(question, labels)` | docs-mods-events "Hold a tool call until the user decides" | Inside one `$` call, so off-budget | Resolves to the picked label or typed text; rejects on dismiss, on "Chat about this", and in `claude -p` |
| Pane with buttons plus a polling loop of `$.process.run(['sleep','0.25'])` | claudedev-getting-started (Blast Radius) | Many short `$` calls, each off-budget | Lets the mod draw its own report pane; exits when `next.signal` aborts |

The docs, written for 2.1.287 and current on 2.1.288, show only the `$.ui.ask` shape. The Blast Radius loop predates it as a teaching sample and spawns four processes a second while it waits (claudedev-getting-started). Prefer `$.ui.ask` unless the decision needs a rich custom view. PRACTITIONER

## Minimal correct hold

```typescript
const RISKY = /\brm\s+-rf?\b|\bgit\s+reset\s+--hard\b|\bgit\s+push\b.*--force/

export const register: Register = (on) => {
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    if (!RISKY.test(e.command)) return next(e)
    let answer = 'Refuse'
    try {
      answer = await $.ui.ask('Run this command? ' + e.command, ['Run it', 'Refuse'])
    } catch {
      // dismissed, "Chat about this", or claude -p: keep the safe default
    }
    if (answer !== 'Run it') return { deny: 'The user declined this command.' }
    return next(e)
  }).catch(async () => ({ deny: 'Guard failed, command not run.' }))
}
```

This is the docs example plus the `.catch` from "Handle a hook that fails" (docs-mods-events). The `.catch` handler has its own 1 second limit (docs-mods-reference).

## What the user sees and what happens

- **User picks Run it**: the hook calls `next(e)` and the normal permission check still runs after it (docs-mods-events). A hold is an extra gate, not a replacement for permissions.
- **User picks Refuse**: Claude reads the `deny` text as the tool result, so write it as an instruction Claude can act on (docs-mods-events).
- **User types free text**: `$.ui.ask` resolves to that text; compare against the exact label so anything else refuses (docs-mods-events).
- **Nobody answers**: `$.ui.ask` rejects; the `catch` keeps the safe default (docs-mods-events).
- **`AskOptions`** in the typings also accept `{ options, header, multiSelect }`, with a multi-select answer comma-joined (types 2.1.288 L512-530, L2240-2246).

## Budget arithmetic

| Wait inside | Counts against 10 s hook budget? | Source |
|---|---|---|
| `next(e)` | No | docs-mods-reference Limits |
| Any `$` call except `$.clock.sleep` | No | docs-mods-reference Limits |
| `$.clock.sleep(ms)` | Yes | docs-mods-reference Limits |
| Your own `new Promise(...)`, `setTimeout`-style waits | Yes (and there is no `setTimeout` global) | docs-mods-events, docs-mods-api |

So a loop of `await $.clock.sleep(250)` burns the budget and gets the hook skipped after 10 seconds, and the risky command then runs. This is the most dangerous hold mistake because it fails open silently. EVIDENCE-BASED

`next.budget.ms` and `next.budget.remainingMs` expose the limit at runtime (docs-mods-reference), so a hold that must do heavy local work before asking can check what is left.

## Where the hold sits in the chain

- Managed-settings `PreToolUse` hooks run before any mod's `tool.call`, and their block is final, so a held call may never reach your hook (docs-mods-events).
- Non-managed `PreToolUse` hooks and the permission rules run after the last mod calls `next` (docs-mods-events). A hold that ends in `next(e)` can still be refused later.
- If your mod is outermost (for example in `prependPlugins`), it holds the call before any other mod sees it; a user-tier hold sits behind org mods (docs-mods-events). See [[Hook Ordering and Tiers]].
- `tool.check` is the place to change the final allow, ask, or deny decision without a dialog; it fires after `tool.call` and the settings hooks (docs-mods-reference).

## Auto mode interaction

A hold that only allows or refuses does not rewrite input, so it does not trip the auto mode check `a hook changed this call's input after the model wrote it` (docs-mods-troubleshoot). A hold that edits the command before `next` does trip it. A personal guard mod reviewed for this vault handles this by catching that deny text and returning its own instruction instead. EVIDENCE-BASED

## Recommendations

- Hold with `$.ui.ask`; never with `$.clock.sleep` or a raw promise. EVIDENCE-BASED
- Default the answer to refuse before the `try`, so every failure path denies. EVIDENCE-BASED
- Attach `.catch` returning `{ deny }` to every hook that holds or blocks. EVIDENCE-BASED
- Pass `next.signal` into long work so an Esc interrupt ends the hold (docs-mods-api). EVIDENCE-BASED
- In `claude -p` there is nobody to ask; decide whether a refusal is the right headless default or check `$.session.surfaces()` first. PRACTITIONER
- Treat a text-matching hold as a reminder, not a security boundary: `$(...)`, aliases and scripts bypass it (claudedev-getting-started, docs-mods-events). Use permission rules or the Git host for hard blocks. EVIDENCE-BASED

> [!contradiction]
> The seed report (compass-report) lists "a loop of short `$.process.run(["sleep","0.25"])` calls" as an equal alternative to `$.ui.ask`. The official docs now show only `$.ui.ask` and explain why own-promise waits fail. The sleep loop is valid (each `$` call is off-budget) but heavier; docs-mods-events wins on which shape to teach.

## Worked example: a confirm button

A personal receipt mod reviewed for this vault holds nothing on the tool path, but its pane's Close button awaits `$.ui.ask('Stop ... ?', ['Stop it', 'Keep it'])` before killing a dev server, and defaults to `Keep it` on dismiss. That is the same safe-default shape applied to a button instead of a tool call.

## Caveats

- Tested on 2.1.288 by reading the docs and typings only; no hold was run by this lane (the brief forbids loading mods).
- Whether `$.ui.ask` time is off-budget for a `.catch` handler too is not documented. Unverified.
- Desktop rendering of the ask dialog is documented as the same dialog Claude uses; not checked here.

## Related

The mechanics come from [[Tool Events]] and the [[Hook Middleware Chain]]; the limits are in [[Budgets and Limits]]. The step-by-step build is [[Build a Tool Call Guard Flow]], and the richer pane-based hold uses [[Band and Pane Fallback]] as Blast Radius in [[Playground Sample Mods]] does. Mistakes are collected in [[Pitfalls Playbook]], the shape itself in [[Patterns Playbook]], ordering in [[Hook Ordering and Tiers]], and the classic `PreToolUse` equivalent in [[Mods vs Classic Hooks]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
