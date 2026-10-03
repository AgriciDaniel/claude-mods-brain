---
type: "flow"
title: "Build a Tool Call Guard Flow"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/flow"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "security-governance"
related:
  - "[[Holding a Tool Call]]"
  - "[[Tool Events]]"
  - "[[Hook Middleware Chain]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Budgets and Limits]]"
  - "[[Testing Kit]]"
  - "[[Org Mod Controls]]"
  - "[[Mods vs Classic Hooks]]"
  - "[[Plugin Validate]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-reference"
  - "docs-mods-test"
  - "docs-mods-admin"
  - "types-2-1-288"
  - "secgov-validate-probes"
  - "gh-issue-91870"
---

# Build a Tool Call Guard Flow

A tool call guard is a `tool.call` hook that holds a risky call, asks the user with `$.ui.ask`, and runs it only on an explicit yes. The official pattern has three parts: the hold waits inside `$.ui.ask` so the wait does not count against the 10 second hook budget, every non-answer resolves to refuse, and a `.catch` handler returns `{ deny }` so a guard that throws or times out fails closed (docs-mods-events, "Hold a tool call until the user decides" and "Handle a hook that fails"). Use it for rules that need a human in the moment; use permission rules or managed hooks for rules that must always hold.

## Trigger

- A class of commands needs a live confirmation that a static `ask` rule cannot express (for example production `kubectl` or `terraform`, or force pushes).
- An org wants a confirmation step it can ship as a policy mod in `prependPlugins` ([[Org Mod Controls]]).

## Prerequisites

- Claude Code 2.1.287 or later (mods on by default; docs-mods-overview). Tested here: static validate on 2.1.288.
- A plugin skeleton: `.claude-plugin/plugin.json`, `hooks/hooks.json` with `"modules": ["./register.js"]`, and the hooks module (docs-mods-reference, Files).
- A written list of what counts as risky, and what the guard should do when nobody can answer (CI, `claude -p`).
- Decide hold versus decide: `tool.call` runs before the permission check and can hold; `tool.check` runs after rules and settings hooks and returns `allow`, `ask`, or `deny` (docs-mods-events).

## Steps

1. **Write the matcher narrowly.** Filter on `{ tool: 'Bash' }` so `e.command` exists, and test the command with a pattern; pass everything else to `next(e)` untouched.
2. **Hold with `$.ui.ask`.** Start from the safe answer, await the question inside `try`, and compare the result to the exact label. `$.ui.ask` resolves to the chosen label or typed text, and rejects on dismiss, **Chat about this**, or a `-p` run (types 2.1.288 L2232-2246).
3. **Refuse without calling `next`.** Return `{ deny: '...' }`. Claude reads the text as the tool result, so write it as an instruction Claude can act on (docs-mods-events).
4. **Attach `.catch` that fails closed.** Without it, a guard that throws or times out is skipped and the held command runs (docs-mods-events). The handler gets `next.error.kind` (`throw` or `timeout`) and has a 1 second limit (docs-mods-reference, Limits).
5. **Validate statically.** `claude plugin validate --strict ./prod-guard`. Expect `hooks: tool.call{tool=Bash}` and `calls: $.ui.ask, $.ui.log` (secgov-validate-probes, Probe 5).
6. **Test without a session.** Write a `.test.ts` that fires `tool.call` and stubs the question; see [[Testing Kit]].
7. **Place it.** For a personal guard, install normally. For an org guard, deploy it as an org mod in `prependPlugins` with `sec-default@builtin` after it ([[Org Mod Policy Guide]]).

The module, following the docs pattern (validated on 2.1.288; not run):

```javascript
// hooks/register.js
const RISKY = /\b(kubectl|terraform)\b[^\n]*\b(prod|production)\b/

async function guard($, e, next) {
  if (!RISKY.test(e.command)) return next(e)
  let answer = 'Refuse'                       // a question nobody answers refuses
  try {
    answer = await $.ui.ask('Run this production command? ' + e.command, ['Run it', 'Refuse'])
  } catch {
    // dismissed, Chat about this, or claude -p: keep 'Refuse'
  }
  if (answer !== 'Run it') {
    return { deny: 'The user declined this production command. Ask before another approach.' }
  }
  $.ui.log('prod-guard approved ' + JSON.stringify(e.command), { to: 'debug' })
  return next(e)                              // the normal permission check still runs
}

export function register(on) {
  on('tool.call', { tool: 'Bash' }, guard).catch(async ($, e, next) => {
    // runs only when guard threw or timed out; must return a result, not undefined
    return { deny: 'prod-guard failed (' + next.error.kind + '), so this command was not run.' }
  })
}
```

A test sketch (shape from docs-mods-test; `$.ui.ask` reaches a stub as an `AskUserQuestion` tool call):

```typescript
import { expect, test } from 'claude-code/testing'

test('refuses a production command when the user picks Refuse', async ($, on) => {
  on('tool.call', ($, e) => e.tool === 'AskUserQuestion'
    ? { result: { answers: { [e.questions[0]?.question ?? '']: 'Refuse' } } }
    : { result: 'ran' })
  const out = await $.tool.call({ tool: 'Bash', command: 'kubectl apply -f x.yaml --context prod' })
  expect(out.deny).toContain('declined')
})
```
> [!contradiction]
> The docs' test examples (docs-mods-test L31, L122) omit fields the 2.1.288 typings require: `origin` and `presentation` on `$.command.run` (types 2.1.288 L1610-1636) and a typed `value` on a `command.register` stub. The snippet above follows the typings and compiles under the generated tsconfig (strict, `noUncheckedIndexedAccess`) with tsc 5.9.3, checked 2026-10-03.

## Outputs

- A plugin directory with the hooks module, `hooks.json`, manifest, and tests.
- Validate output showing only the expected hooks and calls.
- A debug-log audit line per approval (`$.ui.log` with `{ to: 'debug' }`).

## Gates

| Gate | Pass condition |
|---|---|
| Fail-closed | `.catch` present and returns `{ deny }` on every blocking registration |
| Safe default | Every path except the exact approval label returns `{ deny }` |
| Budget | No waiting on your own promises before `next`; only `$` calls (own waits count toward 10 s; docs-mods-events) |
| Footprint | Validate lists only `tool.call{tool=Bash}` and the `$.ui` calls you expect |
| Tests | Refuse path, approve path, and pass-through path covered |

## Failure Modes

- **Fails open on error.** A missing `.catch`, or a `.catch` that returns `undefined`, makes the hook absent and the command runs (types 2.1.288 L994-1002) (C-SEC-033).
- **Timeout from your own awaits.** Awaiting a non-`$` promise counts toward the 10 second budget; a skipped hook lets the call through (docs-mods-events) (C-SEC-036).
- **Pattern bypass.** A command string matcher misses other spellings; the docs' own example "misses other spellings such as `git push -f`" (docs-mods-events). Shell strings can be obfuscated; a thread participant noted structured matching does not reach inside them (gh-issue-91870, @deafsquad, issuecomment-5532269410). Treat the guard as a reminder layer, and protect the real target (branch protection, cloud IAM).
- **No one to ask.** In `claude -p`, `$.ui.ask` rejects, so the guard always refuses; decide whether CI should run these commands at all.
- **Another mod answers first.** `$.ui.ask` runs as an `AskUserQuestion` tool call "through every hook but the calling one" (types 2.1.288 L2235-2236), so a mod earlier in the chain could rewrite or answer it. Place org guards in `prependPlugins`.
- **Not loaded.** Three worker crashes that cannot be traced to one mod (every mod that is not built in unloads, built-ins stay; docs-mods-troubleshoot L136), `--safe-mode`, or `allowManagedModsOnly` without your mod counting as the org's all remove the guard (docs-mods-admin) (C-SEC-034).
- **Subagents.** `tool.call` fires for subagent calls too (docs-mods-events), so questions can appear during background work.

## Rollback

- Disable the plugin in `/plugin`, or set `"disableAllHooks": true` in `~/.claude/settings.json` to stop every installed mod for that user (docs-mods-overview).
- For an org guard, remove its id from managed `prependPlugins` and `enabledPlugins`, keeping `sec-default@builtin` in the list or removing the key (docs-mods-admin).
- Keep the matching permission rule (`ask` or `deny`) in settings while the guard is out, so the rule still holds.

## Caveats

- The module was validated statically on 2.1.288 and not run; the test sketch was not executed.
- The `answers` stub shape comes from docs-mods-test and can change between releases.

## Related

Background on holding is in [[Holding a Tool Call]] and [[Tool Events]]; chain position in [[Hook Middleware Chain]] and [[Hook Ordering and Tiers]]; time limits in [[Budgets and Limits]]. Tests use [[Testing Kit]] and the scan uses [[Plugin Validate]]. Deciding between this and a settings hook is covered in [[Mods vs Classic Hooks]]. Fleet deployment is in [[Org Mod Controls]] and [[Org Mod Policy Guide]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-test: https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md`
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870#issuecomment-5532269410 (retrieved 2026-10-03)
