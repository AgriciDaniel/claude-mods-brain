---
type: "flow"
title: "Build a Status Band Flow"
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
lane: "lifecycle"
related:
  - "[[Render Sites]]"
  - "[[UI Elements and JSX]]"
  - "[[State Store and Module Variables]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Plugin Validate]]"
  - "[[Testing Kit]]"
  - "[[Band and Pane Fallback]]"
  - "[[Turn and Session Events]]"
  - "[[Testing Playbook]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
sources:
  - "docs-mods-interface"
  - "docs-mods-test"
  - "docs-mods-create"
  - "types-2-1-288"
  - "lif-plugin-authoring-skill"
---

# Build a Status Band Flow

A runnable recipe for a band above the prompt (the `AbovePrompt` render site) that shows the last turn's duration and tool-call count, keeps its values in `$.state` so a hot reload does not wipe them, and is covered by a kit test on two surfaces. The shape follows the bundled skill's `band.tsx` example (lif-plugin-authoring-skill) and the 2.1.288 typings. Total time: about 15 minutes.

## Trigger

You want a persistent, glanceable readout (a row above the prompt) rather than a pane or a status-line string. Use a band when the content is 1 to 3 rows and useful every turn; use `$.ui.status(text)` for a single string and a pane for anything scrollable (see [[Band and Pane Fallback]]).

## Prerequisites

- `claude --version` prints 2.1.287 or later (C-LIF-001).
- A scratch folder you own, such as `~/mods/turn-band`. Do not develop inside an installed plugin: installed copies are cached by version (C-LIF-010).

## Steps

1. Create the folders, the manifest (its `types` field is required because the module uses `$.state`), the hooks file (one module path, relative to it) and the state contract. Every key the module names must be declared or validate fails with `turn-band.<key> is not declared` (C-LIF-002, C-LIF-018).

```bash
mkdir -p ~/mods/turn-band/{.claude-plugin,hooks,types,tests} && cd ~/mods/turn-band
cat > .claude-plugin/plugin.json <<'JSON'
{ "name": "turn-band", "version": "0.1.0", "description": "Shows the last turn's duration and tool calls above the prompt",
  "author": { "name": "Your Name" }, "types": "./types/index.d.ts" }
JSON
echo '{ "modules": ["./register.tsx"] }' > hooks/hooks.json
cat > types/index.d.ts <<'TS'
export type LastTurn = { seconds: number; tools: number }
declare module 'claude-code' {
  interface PluginState {
    'turn-band': { last: LastTurn | null; pending: number; isHidden: boolean }
  }
}
TS
```

2. Write the hooks module `hooks/register.tsx`.

```tsx
import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'
import type { LastTurn } from '../types'

const last = atom({ plugin: 'turn-band', key: 'last' } as const, null)
const pending = atom({ plugin: 'turn-band', key: 'pending' } as const, 0)
const isHidden = atom({ plugin: 'turn-band', key: 'isHidden' } as const, false)
export const register: Register = on => {
  // Count every tool call of the running turn; write from the event, never from a render
  on('tool.call', async ($, e, next) => {
    await update($, pending, n => n + 1)
    return next(e)
  })
  // Close the turn: store its summary and reset the counter
  on('turn.complete', async ($, e, next) => {
    const tools = await read($, pending)
    const turn: LastTurn = { seconds: Math.round(e.durationMs / 1000), tools }
    await update($, last, () => turn)
    await update($, pending, () => 0)
    return next(e)
  })
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const turn = await read($, last)
    // Yield to a survey, show nothing before the first turn, respect Hide
    if (e.props.hasSurvey || turn === null || (await read($, isHidden))) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    return (
      <Box flexDirection="row" columnGap={1}>
        <Text dimColor>Last turn: {turn.seconds}s, {turn.tools} tool calls</Text>
        <Button key="hide" label="Hide" onPress={() => update($, isHidden, () => true)} />
      </Box>
    )
  })
}
```

Why `$.state` and not `let` variables: a reload re-runs `register` and resets module variables, while `$.state` survives (C-LIF-007). A render hook may read state and must not write it; writes go in `onPress` or another event's hook (docs-mods-interface).

3. Validate statically and read the inventory (C-LIF-014, C-LIF-017).

```bash
claude plugin validate ~/mods/turn-band
```

Expect a `hooks:` line naming `tool.call, turn.complete, ui.render{component=AbovePrompt}`, a `calls:` line including `$.ui.resolve`, plus `state reads:` and `state writes:` lines naming `turn-band.last`, `turn-band.pending`, `turn-band.isHidden`, and `Validation passed`.

4. Write `tests/turn-band.test.ts`. Stubs answer in Claude Code's place and must be registered before the first call on `$` (C-LIF-024, C-LIF-025). A `ui.render` stub is required because the hook returns `next(e)` when quiet (docs-mods-test).

```ts
import { expect, test } from 'claude-code/testing'
const BAND = { plugin: 'turn-band', component: 'AbovePrompt', viewport: { columns: 120, rows: 40 },
  props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 120, scroll: { offset: 0, bodyRows: 10 }, view: {} } } as const

test('the band reports the last turn on terminal and desktop', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }))
  on('turn.complete', () => ({ text: '' }))
  on('ui.render', () => ({ type: 'Text', props: {}, children: ['drawn by Claude Code'] }))
  await $.tool.call({ tool: 'Bash', command: 'ls' })
  await $.tool.call({ tool: 'Read', file_path: 'README.md' })
  await $.turn.complete({ turnId: 't1', answer: 'ok', durationMs: 4200, isAborted: false, reason: 'answer' })
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...BAND, surface })
    expect(await ui.find({ type: 'Text', text: /Last turn: 4s, 2 tool calls/ })).toBeDefined()
    await ui.unmount()
  }
})
test('Hide gives the band back to Claude Code', async ($, on) => {
  on('turn.complete', () => ({ text: '' }))
  on('ui.render', () => ({ type: 'Text', props: {}, children: ['drawn by Claude Code'] }))
  await $.turn.complete({ turnId: 't1', answer: 'ok', durationMs: 1000, isAborted: false, reason: 'answer' })
  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
  await ui.press({ key: 'hide' })
  expect(await ui.find({ type: 'Text', text: 'drawn by Claude Code' })).toBeDefined()
})
```

5. Run the tests and load the mod for one session (C-LIF-006, C-LIF-022).

```bash
cd ~/mods/turn-band && claude plugin test
claude --plugin-dir ~/mods/turn-band --debug-file ./turn-band-debug.log
```

Send a prompt that uses a tool. After the turn ends, the band shows `Last turn: Ns, N tool calls [ Hide ]`. Edit the label and save: the transcript prints a reload line and the values survive the reload.

## Outputs

A four-file mod plus a test under `~/mods/turn-band`; `.claude-plugin/types/` written by the engine at load, with a root `tsconfig.json` extending it if you had none (C-LIF-042); a passing test run and a validate inventory for the README.

## Gates

- Validate passes with the state lines present; no `is not declared` error. EVIDENCE-BASED
- Both test cases pass on `terminal` and `desktop`; a mount that rejects means the tree failed that surface's element table. EVIDENCE-BASED
- In a live session, the band appears only after the first completed turn and disappears on Hide. PRACTITIONER

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Band empty, transcript says `ui.render (AbovePrompt) refused:` | A prop or element the surface rejects | Read the reason; check props in the typings (docs-mods-troubleshoot) |
| Counts reset to 0 on every save | Values kept in module `let` variables | Move them into `$.state` atoms (C-LIF-007) |
| Validate: `turn-band.pending is not declared` | Key missing from `types/index.d.ts` or `types` missing from plugin.json | Declare it (C-LIF-018) |
| Test throws `on("ui.render") after the test first called $` | Stub registered after the first `$` call | Register every stub first (C-LIF-024) |
| Test: `no implementation for ui.render` | Quiet branch returned `next(e)` with no stub | Add the `ui.render` stub (C-LIF-025) |

## Rollback

Quit the `--plugin-dir` session: nothing was installed. Mid-session, press Hide or disable it in `/plugin`; delete `~/mods/turn-band` to remove it.

## Caveats

- `e.durationMs` is the engine's turn duration; it differs slightly from wall clock measured with `$.clock.now()` as the skill example does. Unverified which is closer to the spinner's figure.
- The band is shared by every mod; a tree you return replaces what later mods draw. To stack with them, place `await next(e)` inside your `Box` (docs-mods-interface).
- Tested here against the 2.1.288 typings and docs only; this lane did not execute the tests (C-LIF-029 note: kit features are declared, not run).

## Related

The site and its props are in [[Render Sites]] and [[UI Elements and JSX]]; the persistence choice is explained in [[State Store and Module Variables]]. The reload behaviour behind step 5 is [[Hot Reload and Dev Loop]], the static check is [[Plugin Validate]], and the test API is [[Testing Kit]] with patterns in [[Testing Playbook]]. When a band is the wrong container, see [[Band and Pane Fallback]] and [[Build a Pane Flow]]. The events used are described in [[Turn and Session Events]] and [[Tool Events]].

## Sources

- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- docs-mods-test: https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)
- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- types-2-1-288: local `.raw/captures/types-2.1.288/claude-code/index.d.ts` (AbovePrompt props L9578-9620, testing kit L13900-14972)
- lif-plugin-authoring-skill: `.raw/captures/lanes-2026-10-03/lifecycle/plugin-authoring-skill-2-1-288.md` (examples/band.tsx, retrieved 2026-10-03)
