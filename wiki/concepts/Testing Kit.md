---
type: "concept"
title: "Testing Kit"
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
lane: "lifecycle"
related:
  - "[[Testing Playbook]]"
  - "[[Plugin Validate]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Hook Middleware Chain]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Render Sites]]"
  - "[[code-modernization Plugin]]"
  - "[[Does claude plugin test support userConfig values yet]]"
  - "[[Budgets and Limits]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
sources:
  - "docs-mods-test"
  - "docs-mods-reference"
  - "docs-mods-troubleshoot"
  - "types-2-1-288"
  - "code-modernization-1-0-0"
  - "lif-plugin-authoring-skill"
  - "a local `claude plugin validate --json` run"
  - "gh-issue-91870"
---

# Testing Kit

The testing kit is the module `claude-code/testing`, which `claude plugin test [dir]` loads for every `*.test.ts` and `*.test.tsx` under a mod's folder, each file in a child of the Claude Code binary, with no session, sign-in or network (C-LIF-022). A test gets the engine's own `$` and an `on` whose hooks sit beneath every plugin and stand in for Claude Code, so the test fires real events through the mod and stubs whatever the engine would have answered (C-LIF-024). It exports `test`, `describe`, `expect`, `mock` and `tier` (C-LIF-023), and it checks the tree a hook returns for a named surface, never the paint (C-LIF-031).

## The model in one line

The test's `$` raises events (`$.tool.call`, `$.command.run`, `$.ui.mount`) into the plugins under test; whatever they pass on with `next(e)` or ask of `$` lands on the test's `on(...)` stubs; beneath those, the bottom hook throws `no implementation for <name>`.

Plugins load at the test's first call on `$`, so every stub goes in before that call (types 2.1.288 L14916-14922).

## Exports (types 2.1.288 L13900-14972)

| Export | Signature or shape | Use |
|---|---|---|
| `test` | `test(name, body)` or `test(name, options, body)`; body `($, on) => unknown` | One test; fails on throw, reject, or timeout (5000 ms default) |
| `describe` | `describe(name, body)` | Groups; the name leads each test title |
| `expect` | `expect(received, message?)` with `.not`, `.resolves`, `.rejects`; `expect.any`, `anything`, `stringContaining`, `stringMatching`, `objectContaining`, `arrayContaining` | Assertions |
| `mock` | `mock.clock(on, { now? })`, `mock.store(on, entries?)`, `mock.env(on, vars)` | In-memory namespaces |
| `tier` | `tier('prepend' \| 'user' \| 'append' \| 'builtin')`, once per file | Load the mod under test in another tier |

`TestOptions` holds `plugins` (inline plugins with `name`, optional `tier`, `register`), `timeoutMs`, and on 2.1.288 `options`, the plugin's `userConfig` values (C-LIF-029). Matchers include `toBe`, `toEqual`, `toStrictEqual`, `toMatchObject`, `toContain`, `toContainEqual`, `toHaveLength`, `toHaveProperty`, `toBeDefined`, `toBeUndefined`, `toBeNull`, `toBeTruthy`, `toBeFalsy`, `toBeNaN`, the four numeric comparisons, `toMatch`, `toStartWith`, `toEndWith`, `toBeInstanceOf`, `toThrow` (types 2.1.288 L14273-14440). The docs list only eight; the typings are the authority (C-LIF-043).

## Stubs: what the bottom answers

A stub for a mods API call is named without `$.` and returns `{ value }` or `{ deny }`; a stub for an engine event returns that event's result (C-LIF-025, docs-mods-test):

| The mod calls or passes on | Stub |
|---|---|
| `$.ui.toast`, `$.ui.log`, `$.ui.status`, `$.store.set` | `() => ({ value: undefined })` |
| `$.command.register`, `$.tool.register` | `($, e) => ({ value: { command: e.name } })`, or `{ tool: e.name }` for a tool (types 2.1.288 L6780-6787; `{ value: undefined }` fails tsc) |
| `$.store.get` | `($, e) => ({ value: saved.get(e.key) })` |
| `$.ui.open` | `() => ({ value: { isPlaced: true } })` |
| `$.model.complete` | `() => ({ value: { isAnswered: true, text: '...', usage } })` |
| `$.process.run` | `() => ({ value: { exitCode: 0, stdout: '...', stderr: '' } })` |
| a call that should fail | `() => ({ deny: 'reason' })` |
| `tool.call` (event) | `() => ({ result: '...' })` |
| `session.start` (event) | `() => ({ cwd: '/work' })` |
| `ui.render` (event, when the mod returns `next(e)`) | `() => ({ type: 'Text', props: {}, children: ['...'] })` |

The kit answers `$.ui.invalidate` and `$.state` itself; `$.clock` needs `mock.clock(on)` (C-LIF-026).

## A complete test of a command and a timed toast

The mod under test here is hypothetical: a `standup` mod that registers `/standup` in `session.start`, answers with a summary for `e.args` days, and toasts a reminder a minute later with `$.clock.after`.

```ts
import { expect, mock, test } from 'claude-code/testing'

// $.command.run takes the full CommandRunInput in tests: origin and presentation are required (types 2.1.288 L1610-1636)
const RUN = { origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } } as const

test('/standup registers, answers, and toasts after a delay', async ($, on) => {
  const clock = mock.clock(on)
  const toasts: string[] = []
  on('command.register', ($, e) => ({ value: { command: e.name } }))
  on('ui.toast', ($, e) => { toasts.push(e.text); return { value: undefined } })
  on('session.start', () => ({ cwd: '/work' }))

  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  const answer = await $.command.run({ command: 'standup', args: '3', ...RUN })
  expect(answer.text).toMatch(/3 day/)

  await clock.advance(60_000)
  expect(toasts).toEqual(['standup: time to post'])
})
```
> [!contradiction]
> The docs' test examples (docs-mods-test L31, L122) omit fields the 2.1.288 typings require: `origin` and `presentation` on `$.command.run` (types 2.1.288 L1610-1636) and a typed `value` on a `command.register` stub. The snippet above follows the typings and compiles under the generated tsconfig (strict, `noUncheckedIndexedAccess`) with tsc 5.9.3, checked 2026-10-03.

`session.start` never fires on its own in a test, which is why the test raises it and stubs `command.register` (C-LIF-027).

## Drawing tests

`$.ui.mount({ plugin, surface, component, props, requestId?, viewport? })` draws a render site through the mod and returns a handle typed by that surface: `find`, `findAll`, `drawn`, `press`, `input`, `select`, `redraw`, `unmount`, plus `key`, `pointer`, `post`, `advance`, `resize` where the surface has `Client` (C-LIF-030). `surface` is never defaulted, so loop the body. This test targets the skill's `band.tsx` example (`turn-band`), which returns `next(e)` until a turn has completed, so it stubs `ui.render` for the engine's own band:

```ts
import { expect, mock, test } from 'claude-code/testing'

const BAND = {
  plugin: 'turn-band', component: 'AbovePrompt',
  props: { hasSurvey: false, isWorking: false, maxRows: 6, bodyColumns: 80,
           scroll: { offset: 0, bodyRows: 5 }, view: {} },
} as const

test('the band shows the last turn on every surface, then hides', async ($, on) => {
  mock.clock(on)
  on('ui.render', () => ({ type: 'Text', props: {}, children: ['engine band'] }))
  on('tool.call', () => ({ result: 'ok' }))
  on('turn.complete', () => ({ text: '' }))

  await $.tool.call({ tool: 'Bash', command: 'ls' })
  await $.turn.complete({ turnId: 't1', answer: 'ok', durationMs: 1000, isAborted: false, reason: 'answer' })

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...BAND, surface })
    expect(await ui.find({ type: 'Text', text: /1 tool calls/ })).toBeDefined()
    await ui.unmount()
  }

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
  await ui.press({ key: 'hide' })
  expect(await ui.find({ key: 'hide' })).toBeUndefined()
})
```

Each act resolves only after the chain, the handler and any unawaited work it started have settled, so assert on the next line (lif-plugin-authoring-skill). A mount rejects when the surface refuses the tree, which is how a test catches an element a surface lacks.

## Policy and tier tests

`tier('prepend')` at the top of a file loads the mod under test ahead of user mods, and `test(name, { plugins: [runner] }, body)` loads inline mods for it to judge; a refusal throws at the first `$` call with a message naming the refused mod, the refusing mod, and the reason (C-LIF-032, docs-mods-test). See [[Hook Ordering and Tiers]].

## Errors new authors hit

| Message | Cause | Fix |
|---|---|---|
| `declares no test(): nothing ran` | Test file without `test()` | Add one |
| `on("ui.render") after the test first called $` | Stub registered late | Register all stubs first |
| `no implementation for command.register` | Mod's call has no stub; hook skipped silently | Add the stub; read `the engine reported:` |
| `returned neither { value } nor { deny }` | API stub returned a bare value | Wrap in `{ value }` |
| `no implementation for clock.now` | `$.clock` used without `mock.clock` | Add `mock.clock(on)` |
| `claude plugin test: hooks modules are turned off` | Mods cannot load in that shell | See the probe below |

## The can-mods-load probe

Run `claude plugin test` from a folder with no mod: `no hooks module to load` means mods can load; `hooks modules are turned off here` means a setting blocks them; `hooks modules are turned off in this process` means Anthropic turned installed mods off remotely (C-LIF-033).

## What the kit cannot show

- How a surface paints a tree (C-LIF-031).
- A hook that blocks or crashes the shared hooks worker, since tests run modules on the same thread (C-LIF-035, single-source).
- Live-session interaction; a report says the runner can refuse inside a live session (C-LIF-034, unverified).

## Recommendations

- Write pure logic as plain exported functions and unit test them without the kit, as Anthropic's code-modernization does in `hostile.test.ts` and `logic.test.ts` (C-LIF-036). EVIDENCE-BASED
- Loop every drawing test over at least `terminal` and `desktop`. EVIDENCE-BASED
- Pass userConfig values with `test(name, { options }, body)` on 2.1.288, and keep one test with no options to cover manifest defaults. CONTESTED
- Prefer `mock.store` and `mock.clock` over hand stubs unless you must inspect writes. EVIDENCE-BASED

> [!contradiction]
> A #91870 report on 2.1.282 says `claude plugin test` cannot set userConfig values (comment 5827373997). The 2.1.288 typings declare `TestOptions.options` for exactly that (types 2.1.288 L14924-14945), and the bundled skill agrees. Typings win for 2.1.288; this lane did not execute such a test (X-LIF-01).

## Caveats

- Nothing here was executed by this lane; `claude plugin test` was not run. Signatures come from the 2.1.288 typings and docs.
- The docs test page lags the typings (no `options`, fewer matchers); expect further drift per release.
- Prop objects passed to `$.ui.mount` must satisfy `RenderPropsOf[C]`; the docs example and claude.dev cast with `as any` in places.

## Related

The playbook built on this kit is [[Testing Playbook]]; the static check before it is [[Plugin Validate]], and both run inside the [[Hot Reload and Dev Loop]]. Stubs stand at the bottom of the [[Hook Middleware Chain]], and tier tests exercise [[Hook Ordering and Tiers]]. Drawing tests mount [[Render Sites]]; timeouts mirror [[Budgets and Limits]]. Option tests relate to [[userConfig and Plugin Options]] and the open question [[Does claude plugin test support userConfig values yet]]. The largest official example is the [[code-modernization Plugin]].

## Sources

- docs-mods-test: https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` L13900-14972 (retrieved 2026-10-03)
- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/tests/` (retrieved 2026-10-03)
- lif-plugin-authoring-skill: `.raw/captures/lanes-2026-10-03/lifecycle/plugin-authoring-skill-2-1-288.md` (retrieved 2026-10-03)
- A local `claude plugin validate --json` run on Claude Code 2.1.288 (retrieved 2026-10-03; output not redistributed)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (comments 5827373997, 5949411806, 5950552972; retrieved 2026-10-03)
