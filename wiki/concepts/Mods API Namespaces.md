---
type: "concept"
title: "Mods API Namespaces"
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
  - "[[Mod Anatomy]]"
  - "[[Hook Middleware Chain]]"
  - "[[State Store and Module Variables]]"
  - "[[Budgets and Limits]]"
  - "[[Reach Levels]]"
  - "[[Usage Cost Surface]]"
  - "[[Org Mod Controls]]"
  - "[[How is $.model.classify billed]]"
  - "[[Ranked Build Ideas]]"
  - "[[Mods API Cheatsheet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
sources:
  - "docs-mods-reference"
  - "docs-mods-api"
  - "types-2-1-288"
---

# Mods API Namespaces

`$`, the first argument of every hook, is the only way a mod acts: 21 namespaces of methods, from drawing (`$.ui`) and model calls (`$.model`) to files, processes and the network (`$.fs`, `$.process`, `$.http`) (C-API-041). Every method is also an event named `<namespace>.<method>`, so an earlier mod in the chain can observe, rewrite, refuse (`{ deny }`) or answer (`{ value }`) a later mod's calls; that is how organizations limit what mods reach (C-API-040). Calls run "with the same permissions as the user running Claude Code" (docs-mods-api L170).

## Namespaces and methods (2.1.288)

| Namespace | Methods | Notes | Evidence |
|---|---|---|---|
| `$.plugin` | `name`, `root` (data, not calls) | manifest name; absolute plugin dir | types L2136-2145 |
| `$.ui` | `notice`, `invalidate`, `blit`, `resolve`, `log`, `ask`, `toast`, `status`, `open`, `close`, `panes`, `scroll`, `focus`, `copy`, `selection` | `resolve` is a read, not a dispatch | types L2150-2383 |
| `$.model` | `complete`, `fork`, `classify` | session credentials; user's plan or key | types L2387-2453; docs-mods-api L97 |
| `$.audio` | `play`, `speak` | `afplay` and `say` on macOS; Linux terminal plays nothing | types L2457-2488 |
| `$.mcp` | `call(server, tool, args?)`, `connect(server)` | no permission prompt; `connect` only for servers in your own manifest | types L2493-2529 |
| `$.session` | `messages`, `cwd`, `root`, `model`, `turns`, `id`, `repo`, `surfaces`, `surface` (deprecated), `usage`, `version`, `compact`, `send`, `append`, `authorize` | read as plain data | types L2534-2710 |
| `$.turn` | `abort({ turnId })` | only the running turn's id | types L2714-2728 |
| `$.prompt` | `submit`, `read`, `fill`, `suggest`, `compose` | see [[Prompt Events]] | types L2733-2795 |
| `$.tool` | `list`, `call`, `check`, `register` | `call` runs the full permission flow | types L2799-2848 |
| `$.command` | `list`, `run`, `register` | built-in names refused | types L2852-2888 |
| `$.config` | `list`, `set` | every `/config` row incl. plugin `userConfig` | types L2893-2919 |
| `$.telemetry` | `log`, `mark` | only engine and built-ins reach a destination | types L2924-2958 |
| `$.agent` | `spawn`, `list`, `register` | spawn always background | types L2962-3006 |
| `$.fs` | `read`, `write`, `list`, `exists`, `stat`, `ancestors` | 4 MiB per read/write | types L3015-3135 |
| `$.store` | `get`, `set`, `delete`, `keys` | JSON, 4 MiB total, shared machine-wide | types L3143-3167 |
| `$.state` | `get`, `set` (+ helpers `atom`, `read`, `update`, `derive`, `memberOf`) | reactive, session-lived | types L3168-3211, L13727-13761 |
| `$.clock` | `now`, `sleep`, `after`, `every` | replaces timers; reload cancels | types L3218-3257 |
| `$.http` | `fetch(url, { method, headers, body, auth, socketPath })` | through the host; org web-fetch policy applies | types L3261-3283 |
| `$.process` | `run(argv, init?)`, `spawn({ argv, cwd, env, input })` | no shell; CLI only | types L3290-3346 |
| `$.settings` | `read({ source? })` | sources `user`, `project`, `local`, `flag`, `policy` | types L3355-3371, L11127 |
| `$.env` | `get(name)`, `set(name, value)` | name must be a string literal | types L3380-3402 |

The docs table has the same 21 rows but omits `ui.selection` and `session.surface` (docs-mods-reference L164-186); see [[Contradictions Register#API and events]] X7.

## Signatures worth memorizing

```text
$.ui.open({ id, title?, focus?: true, closeOnEscape?: true, holdToasts?: true, rows?, columns? }): Promise<{ isPlaced: true } | { isPlaced: false; reason: string }>
$.ui.ask(question, ['A', 'B'] | { options, header?, multiSelect?: true }): Promise<string>
$.ui.log(text, { to?: 'transcript' | 'debug' }): void
$.model.complete({ model, prompt, system?, maxTokens?, effort?, timeoutMs? }, { signal? }): Promise<ModelCompleteResult>
$.model.classify(text, labels, { model? }): Promise<string | undefined>
$.process.run(argv, { cwd?, env?, stdin?, timeoutMs? }): Promise<{ exitCode, stdout, stderr, isStdoutTruncated, isStderrTruncated }>
$.http.fetch(url, init?): Promise<{ status, ok, headers, text }>
$.session.usage({ breakdown?, columns? }?): Promise<{ startedAt, context, rateLimits, cost? }>
$.state.set(ref, value, { ifVersion? }): Promise<{ isSet, version }>
```

Sources: types 2.1.288 L2232-2296, L2414-2452, L3307, L3282, L2642, L3208; argument types at L6933-7005, L514-536, L5792-5847, L7538-7604, L4898-4966.

## Model calls

```ts
import type { Register } from 'claude-code'

export const register: Register = (on) => {
  on('command.run', { command: 'triage' }, async ($, e) => {
    const r = await $.model.complete({ model: 'haiku', system: 'Reply with one word: bug, feature, or question.', prompt: e.args, maxTokens: 20, effort: 'low', timeoutMs: 15_000 })
    return { text: 'Label: ' + (r.isAnswered ? r.text.trim() : 'unknown (' + r.reason + ')') }
  })
}
```

- `complete`: no tools, no history, system prompt is the CLI identity block plus `system`; `maxTokens` default 1024, up to the lower of 64,000 and the model's output limit; effort `low`, `medium`, `high`, `xhigh`, `max`; API failures resolve `isAnswered: false` with `reason` `api-error` (with `status`, `error`), `empty-reply` or `aborted`, and only a request Claude Code refuses to send rejects (C-API-042; types L2389-2414, L5792-5949).
- `fork({ prompt })`: one tool-less question over the session's own transcript, same model and system prompt, served mostly from the prompt cache; `nothing-to-fork` before the first response or after `/clear` (types L2415-2433; docs-mods-api L95).
- `classify(text, labels)`: 2 or more labels, default the small fast model, resolves `undefined` if none named, rejects on failure (types L2435-2452). Billing detail: see [[How is $.model.classify billed]].

## Files, processes, network

| Call | Rule | Evidence |
|---|---|---|
| `$.fs.read(path, { as: 'bytes' }?)` | text or `{ base64 }`; rejects missing or over 4 MiB | types L3016-3034 |
| `$.fs.write(path, text)` | creates dirs; not atomic | types L3035-3041; docs-mods-reference L178 |
| `$.fs.list(path?)` | one directory, `{ name, kind, size, mtimeMs, isLink }` | types L3042-3055 |
| `$.fs.stat(path, { resolve: true })` | adds `realPath` for path guards | types L3061-3113 |
| `$.fs.ancestors({ names, of?, below? })` | CLAUDE.md-style walk for any `.md` name | types L3114-3134 |
| `$.process.run` | argv, no shell, 30 s default, 10 min max, 4,194,304 bytes per stream, git with repo hooks off | C-API-043 |
| `$.process.spawn` | streaming; leaving the loop kills the child | types L3308-3345 |
| `$.http.fetch` | `auth` takes a handle from `$.session.authorize()` for first-party hosts only | types L3261-3283, L2698-2709 |

Relative paths resolve against the session's working directory (docs-mods-api L185). A file your plugin ships is under `$.plugin.root` (types L3021-3022).

## Show something without a turn

| Call | Where | Lifetime |
|---|---|---|
| `$.ui.status(text)` | one line under the prompt, prefixed with the mod name | until replaced; `undefined` clears |
| `$.ui.toast(text, { timeoutMs })` | box at top right | 4,000 ms default |
| `$.ui.log(text)` | dim transcript line Claude does not read | permanent row |
| `$.ui.notice(tool_use_id, text)` | line under an open permission dialog | removed when the call resolves |

Evidence: docs-mods-api L120-128; types L2152-2273.

## Recommendations

- Treat each namespace as a reach level when reviewing a mod: `fs.write`, `process.*`, `http.fetch`, `mcp.call` and `env.set` are the high-risk ones; see [[Reach Levels]]. EVIDENCE-BASED
- Bound model calls with `timeoutMs` and pass `next.signal` where offered; `$` time does not count against your hook budget. EVIDENCE-BASED
- Wrap `$.process.run` in `try`/`catch`; it rejects when the program cannot start or times out. EVIDENCE-BASED
- Use `$.store` instead of `$.fs.write` for data several sessions change. EVIDENCE-BASED

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- `ui.selection`, `session.surface`, `session.authorize` detail and `fs.ancestors` options are typings-only in 2.1.288.
- `$.process` is CLI only (types L3290); behavior on remote surfaces was not tested.

## Related

Where `$` comes from: [[Mod Anatomy]], [[Hook Middleware Chain]]. State: [[State Store and Module Variables]]. Limits: [[Budgets and Limits]]. Risk and cost: [[Reach Levels]], [[Usage Cost Surface]], [[Org Mod Controls]]. Open questions: [[How is $.model.classify billed]]; what is missing from `$` is tracked in the patterns lane's gap note on issue 91870 (not linked here because a `#` in a wikilink parses as a heading anchor). Build ideas that use these namespaces: [[Ranked Build Ideas]]. Lookup: [[Mods API Cheatsheet]].

## Sources

- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
