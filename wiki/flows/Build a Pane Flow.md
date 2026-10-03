---
type: "flow"
title: "Build a Pane Flow"
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
  - "[[Agent and Command Events]]"
  - "[[Band and Pane Fallback]]"
  - "[[Testing Kit]]"
  - "[[Plugin Validate]]"
  - "[[Budgets and Limits]]"
  - "[[Build a Slash Command Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
sources:
  - "docs-mods-interface"
  - "docs-mods-test"
  - "docs-mods-reference"
  - "types-2-1-288"
  - "lif-plugin-authoring-skill"
---

# Build a Pane Flow

A runnable recipe for a pane (a sidebar in a wide fullscreen terminal, a framed region above the prompt otherwise) that lists this session's tool calls, opened by a `/tool-calls` command, with a Clear button, state in `$.state`, and a kit test on terminal and desktop. It adapts the skill's `pane.tsx` (lif-plugin-authoring-skill) and opens only when asked, which avoids the 144-column rule for unasked panes (C-LIF-056).

## Trigger

You need more than three rows, scrolling, or controls (buttons, inputs, selects). Opening a pane is a two-part contract: `$.ui.open({ id })` says the pane exists, and a `ui.render` hook on `{ component: 'Pane', requestId: id }` draws it (docs-mods-interface).

## Prerequisites

- Claude Code 2.1.287 or later (C-LIF-001); a scratch folder such as `~/mods/tool-calls`.

## Steps

1. Create the layout, manifest (with `types`, because the module uses `$.state`), hooks file and state contract (C-LIF-002, C-LIF-018).

```bash
mkdir -p ~/mods/tool-calls/{.claude-plugin,hooks,types,tests} && cd ~/mods/tool-calls
cat > .claude-plugin/plugin.json <<'JSON'
{ "name": "tool-calls", "version": "0.1.0", "description": "A pane listing this session's tool calls",
  "author": { "name": "Your Name" }, "types": "./types/index.d.ts" }
JSON
echo '{ "modules": ["./register.tsx"] }' > hooks/hooks.json
cat > types/index.d.ts <<'TS'
export type ToolCall = { id: string; tool: string; isDone: boolean }
declare module 'claude-code' {
  interface PluginState { 'tool-calls': { calls: ToolCall[] } }
}
TS
```

2. Write `hooks/register.tsx`. The matcher `requestId: PANE` keeps other mods' panes out of this hook; `String(e.tool)` keeps comparisons valid for tools a build may not register (lif-plugin-authoring-skill); size width to `e.props.bodyColumns`, not `e.viewport.columns` (docs-mods-reference).

```tsx
import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'
import type { ToolCall } from '../types'
const PANE = 'tool-calls'
const calls = atom({ plugin: 'tool-calls', key: 'calls' } as const, [])

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    // A name clash throws and would skip the rest of this hook (C-LIF-055)
    await $.command.register({ name: 'tool-calls', description: 'Show tool calls in a pane' }).catch(error =>
      $.ui.log(`tool-calls: ${String(error)}`, { to: 'debug' }))
    return next(e)
  })
  // A typed command is "asked", so the pane seats at any width; focus and closeOnEscape take only true
  on('command.run', { command: 'tool-calls' }, async $ => {
    const opened = await $.ui.open({ id: PANE, title: 'Tool calls', focus: true, closeOnEscape: true })
    if (!opened.isPlaced) $.ui.toast('tool-calls: the pane is waiting for room')
    return {}
  })
  on('tool.call', async ($, e, next) => {
    const call: ToolCall = { id: e.tool_use_id, tool: String(e.tool), isDone: false }
    await update($, calls, list => [...list, call].slice(-200))
    const ran = await next(e)
    await update($, calls, list => list.map(one => (one.id === call.id ? { ...one, isDone: true } : one)))
    return ran
  })
  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Text } = $.ui.resolve(e)
    const list = await read($, calls)
    const room = Math.max(1, e.props.scroll.bodyRows - 2)
    return (
      <Box flexDirection="column">
        <Box flexDirection="row" columnGap={2}>
          <Text bold>{list.length} calls</Text>
          <Button key="clear" label="Clear" hotkey="c" plain onPress={() => update($, calls, () => [])} />
        </Box>
        {list.length === 0 && <Text dimColor>No tool calls yet.</Text>}
        {list.slice(-room).map(call => (
          <Text dimColor={call.isDone}>{call.isDone ? 'done' : 'runs'} {call.tool}</Text>
        ))}
      </Box>
    )
  })
}
```

3. Validate (C-LIF-014): `claude plugin validate ~/mods/tool-calls`

Expect four hooks (`session.start`, `command.run{command=tool-calls}`, `tool.call`, `ui.render` with its matcher), `calls:` naming `$.command.register`, `$.ui.open`, `$.ui.resolve`, `$.ui.toast`, `$.ui.log`, and state lines for `tool-calls.calls`.

4. Write `tests/tool-calls.test.ts`. Stub every mods API call the mod makes: `command.register`, `ui.open` (`{ value: { isPlaced: true } }`), and the engine's `session.start` and `tool.call` (docs-mods-test stub table, C-LIF-025, C-LIF-027).

```ts
import { expect, test } from 'claude-code/testing'

// $.command.run takes the full CommandRunInput in tests: origin and presentation are required (types 2.1.288 L1610-1636)
const RUN = { origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } } as const
const PANE = { plugin: 'tool-calls', component: 'Pane', requestId: 'tool-calls', viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Tool calls', isFocused: true, bodyColumns: 50, placement: 'dock', scroll: { offset: 0, bodyRows: 30 }, view: {} } } as const

test('/tool-calls opens a pane that lists and clears calls', async ($, on) => {
  const opened: string[] = []
  on('session.start', () => ({ cwd: '/work' }))
  on('command.register', ($, e) => ({ value: { command: e.name } }))
  on('ui.open', ($, e) => (opened.push(e.id), { value: { isPlaced: true } }))
  on('tool.call', () => ({ result: 'ok' }))
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  await $.command.run({ command: 'tool-calls', args: '', ...RUN })
  expect(opened).toEqual(['tool-calls'])
  await $.tool.call({ tool: 'Bash', command: 'ls' })
  await $.tool.call({ tool: 'Read', file_path: 'README.md' })

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ type: 'Text', text: /calls$/ }))?.text).toBe('2 calls')
    expect(await ui.findAll({ type: 'Text', text: /^done / })).toHaveLength(2)
    await ui.unmount()
  }
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  await ui.press({ key: 'clear' })
  expect(await ui.find({ type: 'Text', text: 'No tool calls yet.' })).toBeDefined()
})
```
> [!contradiction]
> The docs' test examples (docs-mods-test L31, L122) omit fields the 2.1.288 typings require: `origin` and `presentation` on `$.command.run` (types 2.1.288 L1610-1636) and a typed `value` on a `command.register` stub. The snippet above follows the typings and compiles under the generated tsconfig (strict, `noUncheckedIndexedAccess`) with tsc 5.9.3, checked 2026-10-03.

5. Run and try it:

```bash
cd ~/mods/tool-calls && claude plugin test
claude --plugin-dir ~/mods/tool-calls
```

Type `/tool-calls`, ask Claude for something that reads files, and watch rows flip from `runs` to `done`. Press `c` while the pane has focus (Ctrl+X then Tab, or a click) to clear; Esc closes it.

## Outputs

A pane mod with a command, a state contract, a two-surface test, and a validate inventory of what it hooks and calls (C-LIF-014).

## Gates

- `claude plugin validate` passes and the inventory lists no `$` call you did not intend. EVIDENCE-BASED
- The mount test passes on `terminal` and `desktop`; mounting proves the tree validates against each surface's element table (C-LIF-030, C-LIF-031). EVIDENCE-BASED
- A live look at narrow and wide terminals, because tests check the tree, not the paint (same layout as [[Build a Status Band Flow]]). PRACTITIONER

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `/tool-calls` replies `registered /tool-calls but no command.run hook answered it` | Matcher names a different command, or the hook was skipped | Check for a `hook skipped` line naming `command.run` (docs-mods-troubleshoot) |
| `$.ui.open` resolves `isPlaced: false` | Opened unasked below 144 columns (110 after first open) | Open from a command or press (C-LIF-056) |
| Hotkey `c` does nothing | Pane lacks keyboard focus | Ctrl+X then Tab, or open with `focus: true` (docs-mods-troubleshoot) |

## Rollback

Close the pane (Esc or `$.ui.close({ id })`), then quit the `--plugin-dir` session. Nothing is installed. Delete the folder to remove the mod.

## Caveats

- Panes opened unasked from `session.start` or a timer wait below 144 columns; this flow deliberately opens only from a command. See [[Band and Pane Fallback]] for a toast or band fallback.
- `$.state` resets on `/clear`, `/resume` and `/branch`, and `session.start` does not fire again (docs-mods-troubleshoot); the call list resetting there is acceptable for this mod.
- Passing `focus: false` throws `ui.open: focus is true or left out`; omit the field. Tests here were written against 2.1.288 typings, not executed.

## Related

The two sites involved are covered in [[Render Sites]] and the elements in [[UI Elements and JSX]]. Command registration and `command.run` are in [[Agent and Command Events]] and the standalone recipe [[Build a Slash Command Flow]]. Persistence choices are in [[State Store and Module Variables]], placement limits in [[Budgets and Limits]] and [[Band and Pane Fallback]]. Checks use [[Plugin Validate]] and [[Testing Kit]]; reload behaviour is in [[Hot Reload and Dev Loop]].

## Sources

- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- docs-mods-test: https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- types-2-1-288: local `.raw/captures/types-2.1.288/claude-code/index.d.ts` (`ui.open` L2275-2296, Pane props L9632-9680, mount L14578-14846)
- lif-plugin-authoring-skill: `.raw/captures/lanes-2026-10-03/lifecycle/plugin-authoring-skill-2-1-288.md` (examples/pane.tsx, retrieved 2026-10-03)
