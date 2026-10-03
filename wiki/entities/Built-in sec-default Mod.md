---
type: "entity"
title: "Built-in sec-default Mod"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/entity"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Mod Catalog]]"
  - "[[Org Mod Controls]]"
  - "[[Org Mod Policy Guide]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Hook Middleware Chain]]"
  - "[[Mods Trust Model]]"
  - "[[Build a Tool Call Guard Flow]]"
  - "[[Classic Hook Bridge]]"
  - "[[Budgets and Limits]]"
source_urls:
  - "https://github.com/anthropics/claude-code/tree/main/mods/sec-default (retrieved 2026-10-03, pinned 1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
sources:
  - "eco-gh-anthropics-mods"
  - "docs-mods-admin"
  - "docs-mods-overview"
  - "eco-static-scan"
---

# Built-in sec-default Mod

sec-default is the built-in guard Claude Code seats first in the prepend tier on machines with managed settings or for Team and Enterprise organizations. It keeps what an organization already controls (classic hooks, managed instructions, settings, MCP allowlist, deny rules) out of reach of user-installed mods, and "adds no policy of its own" (eco-gh-anthropics-mods, docs-mods-admin). It is the reference design for any policy mod: three moves, provenance from engine-pinned fields, and fail-closed error handling (C-ECO-010, C-ECO-012).

## Identity and pin

| Field | Value |
|---|---|
| Repo path | `anthropics/claude-code/mods/sec-default` |
| Pinned commit | `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528` (2026-10-02) |
| Manifest | `name: "sec-default"`, `version: "0.1.0"` |
| Module | `./register.ts`, about 52 source files, 61 test files |
| Name in `/plugin` | `cc-plugin-sec-default`; users cannot turn it off (docs-mods-overview) |
| Options key | `pluginConfigs["cc-plugin-sec-default@builtin"]`, managed settings only (C-ECO-011) |
| Code reviewed | static read of `register.ts` and README |

## The three moves

1. **Continue past the user tier**: `next.to(e, 'append')`. The user tier is skipped, so a person's mod cannot rewrite what the organization's tiers answer.
2. **Refuse by name**: `{ deny }` when `next.origin.tier === 'user'`, or `{ refuse }` on `plugin.register` for a user-tier module.
3. **Pass**: `next(e)`.

`next.to` is refused outside a managed tier, so a copy loaded with `--plugin-dir` can only pass (C-ECO-014).

## Event table

| Event | Move |
|---|---|
| `classic.*` | `next.to(e, 'append')`: org settings hooks see the engine's input and their answer stands |
| `prompt.section`, `prompt.context`, `prompt.compose`, `skill.prompt`, `attribution.text` | `next.to(e, 'append')` |
| `settings.read` | `next.to(e, 'append')`: no user hook rewrites settings reads |
| `tool.describe`, `command.describe`, `agent.offer`, `agent.spawn` | `pastUsers`: continue past users only when `e.provider.tier` is prepend or append |
| `tool.register` | Refuse a user-tier caller while managed settings hold `allowedMcpServers` |
| `tool.list` | Restore the org's managed MCP tools as the org tiers listed them |
| `tool.check` | If a user mod loosened a verdict, re-run past users; a rule-named deny wins |
| `plugin.register {tier:'user'}` | `{ refuse }` while `allowManagedModsOnly` is set |
| everything else | passes (`prompt.submit`, `turn.*`, `tool.call`, `ui.*`, `http.fetch`, `process.run`, and more) |

Calls on `$`: `settings.read` (with `{ source: 'policy' }`) and `ui.log`; the scan also finds `$.tool.register` and `$.tool.list` referenced (C-ECO-010, eco-static-scan). Reach L1 (reads settings). Usage cost: none.

## Options

```json
{
  "pluginConfigs": {
    "cc-plugin-sec-default@builtin": {
      "options": {
        "allowManagedModsOnly": true,
        "allowModsToOverrideDenyRules": false
      }
    }
  }
}
```

- `allowManagedModsOnly`: refuses every user-tier hooks module at load, with the line "mods are limited to your organization's by policy". On unless absent or `false`, so a mistyped `"true"` still locks. Settings hooks, status lines and `/goal` are untouched.
- `allowModsToOverrideDenyRules`: off unless the literal `true`.
- Only managed settings are read; the same key in user or project settings does nothing (C-ECO-011).

## Fail-closed design

The `tool.check` and `plugin.register` hooks each carry a `.catch(...)` handler: an unreadable policy, or a throw in the hook, is treated as a policy in force (C-ECO-012). Copy this for any guard you write:

```ts
on('plugin.register', { tier: 'user' }, async ($, e, next) =>
  isManagedModsOnly(await $.settings.read({ source: 'policy' }))
    ? { refuse: refusal(e.name) }
    : next(e),
).catch(($, e, next) => (next.called ? next(e) : { refuse: refusal(e.name) }))
```

(Shape from `register.ts`; helper names shortened.)

## Cost of being seated

The engine raises `tool.check` only when some plugin hooks it, so where sec-default is seated every tool call now runs the `tool.check` chain (C-ECO-013). `prompt.compose` likewise runs on every system-prompt render.

## Recommendations

- Treat this file as the template for org policy mods: provenance from `next.origin.tier` and `e.provider`, never from what a mod says of itself. EVIDENCE-BASED
- When setting `prependPlugins`, list `sec-default@builtin` explicitly or the guard is dropped (docs-mods-admin). EVIDENCE-BASED
- To check the option on a machine, load a test mod with `--plugin-dir` and confirm the refusal line in `claude --debug` output. EVIDENCE-BASED
- Do not try to reuse `next.to` in a user-installed mod; it is refused outside managed tiers. EVIDENCE-BASED

## Caveats

- Behaviour verified from source at 1c229fc and docs dated 2.1.287; not exercised live in this lane.
- The README notes `claude plugin test` runs in its own engine, so the option never affects tests.
- Pre-release security findings in the #91870 thread predate this guard and may not apply.

## Related

- [[Mod Catalog]] row and verdict.
- [[Org Mod Controls]] and [[Org Mod Policy Guide]] for deploying the options.
- [[Hook Ordering and Tiers]] and [[Hook Middleware Chain]] for `next.to` and tiers.
- [[Mods Trust Model]] for why user mods are untrusted relative to org policy.
- [[Build a Tool Call Guard Flow]] reuses the `.catch` fail-closed shape.
- [[Classic Hook Bridge]] covers the `classic.*` events this mod protects.
- [[Budgets and Limits]] for hook time limits that make `.catch` necessary.

## Sources

- eco-gh-anthropics-mods: https://github.com/anthropics/claude-code/tree/main/mods/sec-default (retrieved 2026-10-03, pinned 1c229fc)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
