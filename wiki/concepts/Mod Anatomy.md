---
type: "concept"
title: "Mod Anatomy"
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
  - "[[Mods API Namespaces]]"
  - "[[State Store and Module Variables]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Plugin Validate]]"
  - "[[Testing Kit]]"
  - "[[Versioning and API Drift]]"
  - "[[code-modernization Plugin]]"
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

# Mod Anatomy

A mod is an ordinary Claude Code plugin with one extra file: `hooks/hooks.json` names a single hooks module whose `register(on, options)` function registers event handlers (C-API-001). The module runs inside Claude Code's own process, in a locked-down JavaScript environment with no DOM, no Node and no timers, and reaches the outside world only through the `$` mods API (C-API-003). Claude Code writes TypeScript declarations for the exact build beside each mod it loads, so the types on disk are the authoritative contract (C-API-004).

## Files

| Path | Required | What it holds | Evidence |
|---|---|---|---|
| `.claude-plugin/plugin.json` | yes | The normal manifest. Mods add no required field. Optional `types` names your own contract file. | docs-mods-reference L21; docs-mods-interface L726-738 |
| `hooks/hooks.json` | yes | `"modules": ["./register.js"]`, one path relative to this file. May also hold settings hooks under `"hooks"`. | docs-mods-reference L22 |
| `hooks/register.{js,mjs,cjs,jsx,ts,mts,cts,tsx}` | yes | The entry point. Exports `register`. Always an ES module. | docs-mods-reference L23; types 2.1.288 L18-24 |
| `types/index.d.ts` | when using `$.state` or adding a `$` namespace | `PluginState` declarations and any noun the mod adds | docs-mods-reference L24 |
| `*.test.ts`, `*.test.tsx` | no | Tests that `claude plugin test` runs | docs-mods-reference L25 |
| `.claude-plugin/types/` | written by Claude Code | `claude-code/index.d.ts`, `claude-code-tools/index.d.ts`, `claude-code-mcp/index.d.ts`, plus one entry per `dependencies` plugin | types 2.1.288 L5-8, L78-83 |

The official `code-modernization` plugin shows both halves living in one `hooks.json`: five settings hooks (`UserPromptSubmit`, `Stop`, `SessionStart`, `PostToolUseFailure`, `StopFailure`) that run a shell script, and `"modules": ["./register.ts"]` (code-modernization-1-0-0 `hooks/hooks.json`). So a mod does not have to give up classic hooks; see [[Mods vs Classic Hooks]].

## The entry point

```ts
// hooks/register.ts
import type { Register } from 'claude-code'

export const register: Register = (on, options) => {
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    $.ui.log('Bash: ' + e.command)
    return next(e)
  })
}
```

- `Register` is `(on: On, options: PluginOptions) => unknown` (types 2.1.288 L8673). The return value is dropped; a returned promise is awaited (L8664-8666).
- `options` holds the manifest's `userConfig` values with defaults filled in (docs-mods-reference L27). The object is fixed for one activation: a change reloads the plugin and `register` runs again (types 2.1.288 L8666-8667). See [[userConfig and Plugin Options]].
- In a `.js` module, type it with a JSDoc tag: `/** @type {import('claude-code').Register} */ export const register = (on, options) => { ... }` (types 2.1.288 L62-64).
- The official example types the parameters directly: `export function register(on: On, raw: PluginOptions)` (code-modernization-1-0-0 `hooks/register.ts` L104).

## The runtime environment

| Available | Not available | Evidence |
|---|---|---|
| `URL`, `URLSearchParams`, `TextEncoder`, `TextDecoder`, `AbortController`, `AbortSignal`, `crypto.subtle`, `atob`, `btoa`, `structuredClone` | DOM, Node built-ins, `require`, `import()` (a module holding it does not load) | types 2.1.288 L13813-13885, L18-24 |
| `h` and `Fragment` globals for JSX | `setTimeout`, `setInterval` (use `$.clock.after`, `$.clock.every`) | types 2.1.288 L13784-13800; docs-mods-api L101, L170 |
| Static `import` of the plugin's own files | `eval`, `new Function` over a string, `WebAssembly` | types 2.1.288 L13763-13768 |

Paraphrase (types 2.1.288 L13765-13767): code that needs compiled code must run it in its own process through `$.process.run`. Everything with a side effect, files, processes, HTTP, model calls, drawing, goes through `$` (see [[Mods API Namespaces]]), and every `$` call is itself an interceptable event (C-API-040). That is the hook point organizations use to restrict mods; see [[Org Mod Controls]] and [[Reach Levels]].

## Types for your build

- Claude Code writes the declarations "each time it loads a mod from a folder the person owns", at `.claude-plugin/types/claude-code/index.d.ts`, and writes them again after an update rather than editing them (types 2.1.288 L5-8). The first line names the version, here `// Written by Claude Code 2.1.288.` (L1).
- TypeScript 5.4 or newer reads them (L8).
- Built-in tool argument types come from `claude-code-tools/index.d.ts`, merged into `BuiltinToolInputs`, so `e.tool === 'Bash'` narrows `e.command` to `string` (types 2.1.288 L860-869; claude-code-tools L1-4). MCP tool inputs come from `claude-code-mcp/index.d.ts`, written at a save with a server connected.
- A mod with no `tsconfig.json` gets one that extends `.claude-plugin/types/tsconfig.json`; the recommended options are `strict`, `noUncheckedIndexedAccess`, `jsx: "react"`, `jsxFactory: "h"`, `jsxFragmentFactory: "Fragment"`, and no DOM `lib`, because DOM's `Text` would shadow the element (types 2.1.288 L66-90).

> [!contradiction] GitHub types vs your build
> Docs point to `mods/types/claude-code.d.ts` on GitHub but warn that copy can be older than your install, and say to trust the copy Claude Code writes for your version (docs-mods-reference L11-13). This brain cites the 2.1.288 copy. Where docs and that copy differ (surfaces, `Svg`, extra members), the typings win; see [[Contradictions Register#API and events]] X1, X2, X7.

## Declaring your own contract

A mod that uses `$.state` declares its values; a mod that adds a `$` namespace through `engine.create` declares the noun:

```ts
// types/index.d.ts, named by "types": "./types/index.d.ts" in plugin.json
export type Topo = { nodes: () => Promise<string[]> }
declare module 'claude-code' {
  interface PluginState { 'my-mod': { count: number; tab: 'one' | 'two' } }
  interface EngineInterface { topo: Topo }
}
```

The contract file exports its own types, has no `import` or reference, and leads exported names with the noun's PascalCase name (types 2.1.288 L91-99). Undeclared state fails validation with a message such as `hello-tabs.count is not declared` (docs-mods-interface L762). See [[State Store and Module Variables]] and [[Plugin Validate]].

## Recommendations

- Start every TypeScript mod with `import type { Register } from 'claude-code'` and `export const register: Register`, so `on`, `$`, `e` and `next` are typed per event. EVIDENCE-BASED
- Keep `hooks.json` to one module path; split code across files with static `import` instead. EVIDENCE-BASED
- Never commit `.claude-plugin/types/`; it is regenerated per build and pins nothing. PRACTITIONER
- Keep classic settings hooks and the module in the same `hooks.json` only when every consumer runs 2.1.287 or later; see [[Versioning and API Drift]]. PRACTITIONER

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- Tested against the 2.1.288 typings; the docs pages describe 2.1.287. The header marks the surface "EARLY ACCESS" and says it "may change between releases without notice" (types 2.1.288 L4-5).
- The value imports `atom`, `read`, `update`, `derive`, `memberOf` are declared as `export const` (types 2.1.288 L13727-13761) while the header says a type import is empty at run time (L14-16). Docs use the value import (docs-mods-interface L745). Runtime behavior of these helpers was not executed in this lane.

## Related

Read [[Hook Middleware Chain]] next for how `on` composes, then [[Mods API Namespaces]] for what `$` offers. Lifecycle details live in [[Hot Reload and Dev Loop]], [[Plugin Validate]] and [[Testing Kit]]. Configuration is in [[userConfig and Plugin Options]]. A full official example is [[code-modernization Plugin]]. The one-page summary is [[Mods API Cheatsheet]]; drift risk is in [[Versioning and API Drift]].

## Sources

- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/` (retrieved 2026-10-03)
