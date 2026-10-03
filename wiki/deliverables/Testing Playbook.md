---
type: "deliverable"
title: "Testing Playbook"
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
lane: "lifecycle"
related:
  - "[[Testing Kit]]"
  - "[[Plugin Validate]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Render Sites]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[State Store and Module Variables]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Pitfalls Playbook]]"
  - "[[Does claude plugin test support userConfig values yet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
sources:
  - "docs-mods-test"
  - "docs-mods-troubleshoot"
  - "docs-mods-reference"
  - "types-2-1-288"
  - "code-modernization-1-0-0"
  - "a local `claude plugin validate --json` run"
  - "gh-issue-91870"
---

# Testing Playbook

Test a mod in four layers: plain unit tests for pure functions, kit tests that fire events through the hooks with stubs standing for Claude Code, drawing tests that mount a render site on more than one surface, and policy tests that load inline plugins at a chosen tier. Gate every change with `claude plugin validate --strict --json` first, then `claude plugin test`, which runs with no session, sign-in or network and exits 1 on failure (C-LIF-022). The kit checks hook behavior and tree validity, never paint, so a real session look is still the last step (C-LIF-031).

## The pyramid

| Layer | What it proves | Kit features | Speed |
|---|---|---|---|
| 1. Pure unit | Parsers, formatters, rules work on hostile input | `test`, `expect` only | fastest |
| 2. Hook (kit) | Hooks observe, rewrite, answer correctly | `on` stubs, `$.tool.call`, `$.command.run`, `mock.*` | fast |
| 3. Drawing | Tree validates per surface, buttons and inputs work | `$.ui.mount`, `press`, `input`, `find` | fast |
| 4. Policy | A prepend mod refuses or admits other mods | `tier`, `{ plugins }` | fast |

Layer 5 is a live `--plugin-dir` session under `--debug-file` (paint, focus, worker isolation). Anthropic's code-modernization 1.0.0 follows this shape: `hostile.test.ts` and `logic.test.ts` are pure, `register.test.ts` and `mount.test.ts` drive the kit (C-LIF-036).

## Layer 1: pure unit tests

A test file may import the mod's own files and run without touching `$` (docs-mods-test). The official mod feeds 100,000-character lines to every parser and fails any that takes over a second, because a backtracking regex would freeze the shared hooks worker (code-modernization-1-0-0 tests/hostile.test.ts).

```ts
import { expect, test } from 'claude-code/testing'
import { stripDashes } from '../hooks/lib/text'
test('stripDashes stays fast on a hostile line', () => {
  const started = Date.now()
  stripDashes('\u2014'.repeat(100_000))
  expect(Date.now() - started).toBeLessThan(1000)
})
```

## Layer 2: hook tests with stubs

The body gets the engine's own `$` and an `on` whose hooks sit beneath every plugin; register all stubs before the first call on `$` (C-LIF-024). A stub for a mods API call returns `{ value }` or `{ deny }`; a stub for an engine event returns that event's result (C-LIF-025).

```ts
import { expect, test } from 'claude-code/testing'
test('the guard denies an Edit of .env', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }))
  on('ui.log', () => ({ value: undefined }))
  const out = await $.tool.call({ tool: 'Edit', file_path: '/work/.env', old_string: 'a', new_string: 'b' })
  expect(out).toMatchObject({ deny: expect.stringContaining('.env') })
})
```

`session.start` never fires by itself: stub it with `() => ({ cwd: '/work' })`, stub `command.register` if the hook registers commands (else the call rejects and the rest of the hook is skipped silently), then `await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })` (C-LIF-027).

### Condensed stub table (docs-mods-test; the kit itself answers `$.ui.invalidate` and `$.state`, C-LIF-026)

| Mod calls or passes on | Stub returns |
|---|---|
| `ui.toast`, `ui.log`, `ui.status`, `store.set` | `{ value: undefined }` |
| `command.register` | `{ value: { command: e.name } }` (types 2.1.288 L6785-6787; `{ value: undefined }` fails tsc) |
| `store.get` | `{ value: saved.get(e.key) }` |
| `ui.open` | `{ value: { isPlaced: true } }` |
| `model.complete` | `{ value: { isAnswered: true, text, usage } }` |
| any call that should fail | `{ deny: 'reason' }` |
| `tool.call` (event) | `{ result }` |
| `ui.render` after `next(e)` | `{ type: 'Text', props: {}, children: ['...'] }` |

## Timers with mock.clock

`mock.clock(on, { now? })` returns a clock with `now`, `advance`, `set`, `settle` and `sleep`; each `advance` resolves after due timers ran (C-LIF-026, types 2.1.288 L14505-14556).

```ts
import { expect, mock, test } from 'claude-code/testing'
// $.command.run takes the full CommandRunInput in tests: origin and presentation are required (types 2.1.288 L1610-1636)
const RUN = { origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } } as const
test('the countdown toasts once at zero', async ($, on) => {
  const clock = mock.clock(on)
  const toasts: string[] = []
  on('ui.toast', ($, e) => { toasts.push(e.text); return { value: undefined } })
  await $.command.run({ command: 'countdown', args: '3', ...RUN })
  await clock.advance(2000)
  expect(toasts).toEqual([])
  await clock.advance(1000)
  expect(toasts).toEqual(['Time is up'])
})
```
> [!contradiction]
> The docs' test examples (docs-mods-test L31, L122) omit fields the 2.1.288 typings require: `origin` and `presentation` on `$.command.run` (types 2.1.288 L1610-1636) and a typed `value` on a `command.register` stub. The snippet above follows the typings and compiles under the generated tsconfig (strict, `noUncheckedIndexedAccess`) with tsc 5.9.3, checked 2026-10-03.

## Layer 3: drawing tests across surfaces

`$.ui.mount` never defaults `surface`, so loop the same body over surfaces to prove independence (C-LIF-030). This adapts the docs' hello-tabs test (docs-mods-test). A site whose hook returns `next(e)` also needs a `ui.render` stub returning a plain `Text` element.

```ts
import { expect, mock, test } from 'claude-code/testing'

const PANE = {
  plugin: 'hello-tabs', component: 'Pane', requestId: 'hello-tabs',
  viewport: { columns: 100, rows: 30 },
  props: { title: 'Hello tabs', isFocused: true, bodyColumns: 60, placement: 'inline',
           scroll: { offset: 0, bodyRows: 10 }, view: {} },
} as const

test('the second tab counts presses on every surface', async ($, on) => {
  mock.store(on, { count: 0 })
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })
    await ui.press({ key: 'tab-two' })
    await ui.press({ key: 'more' })
    expect(await ui.find({ type: 'Text', text: /^Count: \d+$/ })).toBeDefined()
    await ui.unmount()
  }
})
```

If `scroll` or `view` shapes drift, `tsc` fails first; claude.dev's example casts the target `as any` (claudedev-getting-started), which hides drift. To test the reset after `/clear`, fire `$.classic.SessionStart({ source: 'clear' })` instead of `session.start` (docs-mods-test).

## Layer 4: policy tests

`tier('prepend')` at the top of the file loads the mod under test ahead of user mods, and `test(name, { plugins: [...] }, body)` loads inline mods for it to judge; a refusal throws at the first call on `$` (C-LIF-032).

## userConfig values in tests

> [!contradiction]
> A #91870 comment on 2.1.282 says the test command cannot set userConfig values (comment 5827373997), repeated by compass-report. The 2.1.288 typings declare `TestOptions.options` for exactly that (types 2.1.288 L14924-14945), and the bundled skill agrees. Typings win for 2.1.288; this lane did not execute it, so treat it as declared, not run (C-LIF-029). Left out, the manifest defaults apply.

Shape: `test('honors a custom prose list', { options: { proseExtensions: 'md,txt' } }, async ($, on) => { ... })`.

## Common kit errors

| Message | Cause | Fix |
|---|---|---|
| `no implementation for <name>` | call with no stub | add the stub, or `mock.clock` for `clock.now` |
| `returned neither { value } nor { deny }` | stub returned a bare value | wrap in `{ value }` |
| `on("ui.render") after the test first called $` | late stub | register stubs first |
| test passes yet hook did nothing | hook skipped after a rejected call | stub `command.register`; read `the engine reported:` |

## CI recipe

```bash
claude plugin validate --strict --json ./my-mod > validate.json
claude plugin test ./my-mod
```

`validate --json` exits 0 on success and puts the hook and call inventory in `contents[].notes` (C-LIF-015); diff those strings against a committed baseline to catch a lost hook. Before blaming tests, run `claude plugin test` from a folder holding no mod: `no hooks module to load` means mods can load, `turned off here` means a setting blocks them, `turned off in this process` means a remote switch (C-LIF-033).

## Recommendations

- Put parsing and formatting in plain modules and unit test them under hostile input. EVIDENCE-BASED
- Run every drawing test over at least terminal and desktop. EVIDENCE-BASED
- Keep `validate --strict --json` ahead of `plugin test` in CI and diff the notes inventory. PRACTITIONER
- Finish each UI change with a `--plugin-dir` session under `--debug-file`. EVIDENCE-BASED

## Caveats

- The kit runs hooks on the same thread, so it cannot catch a hook that blocks or crashes the shared worker (C-LIF-035, SINGLE-SOURCE).
- A reported need to run `plugin test` with a separate `CLAUDE_CONFIG_DIR` inside a live session is unverified (C-LIF-034).
- Paint, focus feel and Desktop look are out of reach (C-LIF-031).
- The `options` test path is from typings only on 2.1.288; re-check after each release.

## Related

Start from [[Testing Kit]] for the kit's API and [[Plugin Validate]] for the static half. Reload behavior that tests cannot reproduce lives in [[Hot Reload and Dev Loop]]. Option handling is in [[userConfig and Plugin Options]] and the open question [[Does claude plugin test support userConfig values yet]]. Drawing targets come from [[Render Sites]], tiers from [[Hook Ordering and Tiers]], and reload-surviving values from [[State Store and Module Variables]]. Re-run this playbook through [[Re-verify After Release Flow]], and see [[Pitfalls Playbook]] for failure stories.

## Sources

- docs-mods-test: https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- types-2-1-288: local .raw/captures/types-2.1.288/claude-code/index.d.ts (retrieved 2026-10-03)
- code-modernization-1-0-0: local .raw/captures/official-mods/code-modernization-1.0.0/ (retrieved 2026-10-03)
- A local `claude plugin validate --json` run on Claude Code 2.1.288 (retrieved 2026-10-03; output not redistributed)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
