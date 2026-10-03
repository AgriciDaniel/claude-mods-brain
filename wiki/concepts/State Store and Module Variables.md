---
type: "concept"
title: "State Store and Module Variables"
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
  - "[[Render Sites]]"
  - "[[UI Elements and JSX]]"
  - "[[Turn and Session Events]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Budgets and Limits]]"
  - "[[Mod Anatomy]]"
  - "[[Plugin Validate]]"
  - "[[Testing Kit]]"
  - "[[Pitfalls Playbook]]"
  - "[[Mods API Cheatsheet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
sources:
  - "docs-mods-interface"
  - "docs-mods-reference"
  - "types-2-1-288"
---

# State Store and Module Variables

A mod has three places to keep a value, chosen by how long it must last: a module-level variable (gone on every reload), `$.state` (reactive, survives reloads, reset by `/clear`, `/resume` and `/branch`), and `$.store` (a JSON file shared by every session on the machine, kept across sessions) (docs-mods-interface L693-703). `$.state` redraws the sites that read it on its own; module variables need `$.ui.invalidate('ui.render')` (C-API-046). Getting the lifetime wrong is the most common source of "my pane shows 0 again" bugs.

## Lifetimes

| Keep it in | Lasts until | Redraws on write? | Shared with | Use for | Evidence |
|---|---|---|---|---|---|
| module variable (`let tab = 'one'`) | the module reloads (every save under `--plugin-dir`) | no, call `$.ui.invalidate('ui.render')` | nothing | caches, UI state you can lose | docs-mods-interface L699 |
| `$.state` | session end, or `/clear`, `/resume`, `/branch` | yes, for sites that read it while drawing | any plugin may read; only the owner writes | values a drawing depends on that must survive reload | docs-mods-interface L700, L705-707; types L3168-3175 |
| `$.store` | your mod deletes it, or nothing touches the store for `cleanupPeriodDays` | no | every session on the machine running the mod | settings, history, counters across restarts | docs-mods-interface L701; types L3136-3142 |

## `$.store`

```ts
const n = Number((await $.store.get('count')) ?? 0)   // unknown, or undefined when unset
await $.store.set('count', n + 1)                       // any JSON value
await $.store.delete('count')
const keys = await $.store.keys()                       // insertion order
```

- Values round-trip through JSON: a `Date` becomes its ISO string, `undefined` fields drop, a `Map` or `Set` becomes `{}`; a function, a cycle, or a store over 4 MiB of JSON in total rejects (types 2.1.288 L3151-3157).
- It is a JSON file of the plugin's own under the user's Claude Code config directory (`~/.claude/plugins/store/` per docs-mods-interface L701).
- `get` then `set` is not atomic across sessions; the second write wins. Give each item its own key, and re-read right before writing (docs-mods-interface L810-831).

## `$.state`

`$.state.get(ref)` resolves `{ value, version }` (never written: `undefined` at version 0); `$.state.set(ref, value, { ifVersion? })` resolves `{ isSet, version }` (C-API-046; types 2.1.288 L3176-3210). Rules:

- A `get` made while a `ui.render` hook draws subscribes that site; a later `set` redraws it at the redraw rate, no invalidate needed.
- `set` is refused inside a `ui.render` hook; write from `onPress`, `onSubmit`, or another event's hook.
- Any plugin reads any value; only the owner writes. To change another plugin's value, hook its `state.set` and rewrite `e.value`.
- `plugin` and `key` must be string literals in source so `claude plugin validate` can list them; only a family member's `id` may be computed.
- Value must be JSON data and never `undefined`.

### Declaring values

```ts
// types/index.d.ts (plugin.json: "types": "./types/index.d.ts")
declare module 'claude-code' {
  interface PluginState {
    'hello-tabs': { tab: 'one' | 'two'; count: number }
  }
}
```

An undeclared value fails validation with `hello-tabs.count is not declared` (docs-mods-interface L762; C-API-047). `PluginState` is an empty interface in the core typings, filled by declaration merging (types 2.1.288 L7325).

### Helpers: `atom`, `read`, `update`, `derive`, `memberOf`

```ts
import type { Register } from 'claude-code'
import { atom, read, update } from 'claude-code'

const count = atom({ plugin: 'hello-tabs', key: 'count' } as const, 0)

export const register: Register = (on) => {
  on('ui.render', { component: 'Pane' }, async ($, e, next) => {
    if (e.requestId !== 'hello-tabs') return next(e)
    const { Box, Text, Button } = $.ui.resolve(e)
    const n = await read($, count)                       // subscribes this pane
    return Box({ flexDirection: 'row', columnGap: 2, children: [
      Button({ key: 'more', label: 'Add one', hotkey: 'a', onPress: async () => {
        const saved = Number((await $.store.get('count')) ?? 0)  // re-read: other sessions write too
        await $.store.set('count', saved + 1)
        await update($, count, () => saved + 1)          // redraws, no invalidate
      } }),
      Text({ children: ['Count: ' + n] }),
    ] })
  })
}
```

Pattern from docs-mods-interface L742-757, L819-829. Helper semantics (types 2.1.288 L537-579, L3521-3542, L5728-5735, L8656-8661, L13611-13618, L13727-13761):

| Helper | Does |
|---|---|
| `atom(ref, initial, { shape }?)` | names a value with a default so `read` never gives `undefined`; `shape` tags a version of the value's meaning |
| `read($, atomOrDerivedOrRef)` | reads through `$.state.get`; subscribes while drawing |
| `update($, atom, fn)` | read, apply `fn`, write with `ifVersion`, retry on a miss |
| `derive(sources, fn)` | computed value cached by source versions |
| `memberOf(family, e)` | per-instance member of a `StateFamily`, keyed by `e.requestId` |

Bump an atom's `shape` when the code's idea of the value changes; a stored value under another tag then reads as absent (types 2.1.288 L569-578, L11138-11149).

## Reseeding after `/clear`, `/resume`, `/branch`

Those commands reset every `$.state` value to its default, and `session.start` does not fire again. `classic.SessionStart` does fire, with `source` `clear`, `resume` or `fork` (C-API-035):

```ts
async function loadCount($: EngineInterface) {   // import type { EngineInterface } from 'claude-code'
  const saved = Number((await $.store.get('count')) ?? 0)
  await update($, count, () => saved)
}
on('session.start', async ($, e, next) => { await loadCount($); return next(e) })
on('classic.SessionStart', { source: ['clear', 'resume', 'fork'] }, async ($, e, next) => { await loadCount($); return next(e) })
```

From docs-mods-interface L784-801. Without the second hook, the pane shows the default after `/clear`, and the next save writes the default over the stored value. `classic.SessionStart` also fires with `source` `startup` and `compact`, which do not reset state (types 2.1.288 L10954-10960); the filter skips those.

## Module variables and reload

Every save under `--plugin-dir` reloads the module: module variables reset, timers from `$.clock` are cancelled, and `session.start` runs again for the reloaded module (docs-mods-interface L685, L699; types 2.1.288 L3214-3217, L4057-4059). Panes stay open across a reload; `$.ui.panes()` is the engine's record, so a reloaded module can find its own open pane (types L2312-2318).

## Recommendations

- Keep anything a drawing reads in `$.state`, and persist it to `$.store` on every change, not at `session.end`. EVIDENCE-BASED
- Always pair a `session.start` loader with a `classic.SessionStart` loader filtered on `clear`, `resume`, `fork`. EVIDENCE-BASED
- One key per item in `$.store` for anything several sessions write. EVIDENCE-BASED
- Never treat `$.store` as private: it is a plain JSON file readable by anything running as the user. PRACTITIONER

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- The `$.state` reset rule and the `classic.SessionStart` reseed are documented on the interface page only (SINGLE-SOURCE, C-API-035).
- `loadCount` takes `EngineInterface` because it uses both `$.store` and `$.state`; the helpers themselves only need `StateDollar`, which is `Pick<CoreEngineInterface, 'state'>` (types L11298-11302). See the static check note below.
- Store cleanup on `cleanupPeriodDays` is docs-only.

## Related

Drawing that reads state: [[Render Sites]], [[UI Elements and JSX]]. Session resets: [[Turn and Session Events]]. Reload behavior: [[Hot Reload and Dev Loop]]. Limits: [[Budgets and Limits]]. Declaring the contract: [[Mod Anatomy]], [[Plugin Validate]]. Testing state after `/clear`: [[Testing Kit]]. Mistakes: [[Pitfalls Playbook]]. Lookup: [[Mods API Cheatsheet]].

## Sources

- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
