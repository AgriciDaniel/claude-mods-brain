---
type: "flow"
title: "Build a Slash Command Flow"
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
  - "[[Agent and Command Events]]"
  - "[[Mods API Namespaces]]"
  - "[[State Store and Module Variables]]"
  - "[[Turn and Session Events]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Testing Kit]]"
  - "[[Plugin Validate]]"
  - "[[Usage Cost Surface]]"
  - "[[Build a Pane Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
sources:
  - "docs-mods-api"
  - "docs-mods-test"
  - "docs-mods-create"
  - "docs-plugins-manifest-reference"
  - "types-2-1-288"
---

# Build a Slash Command Flow

A runnable recipe for two slash commands, `/note <text>` and `/notes`, that save and list notes in `$.store` (kept across sessions), with a `userConfig` option for the list length and kit tests that stub the store and pass options. A command is registered in `session.start` and answered by a `command.run` hook that returns `{ text }` (C-LIF-057, docs-mods-api).

## Trigger

You want something the person types, not something Claude calls. For a capability the model should invoke, register a tool with `$.tool.register` instead (docs-mods-api). Remember that `{ text }` is read by the model too, so a command's output costs context (C-LIF-057; see [[Usage Cost Surface]]).

## Prerequisites

- Claude Code 2.1.287 or later (C-LIF-001); scratch folder `~/mods/quick-notes`.
- A name no built-in uses: type `/` in a session to list them. Names are letters, digits, `_`, `-`, up to 64 characters (C-LIF-055).

## Steps

1. Create the layout (no `types/` file: this mod does not use `$.state`), a manifest with one `userConfig` field (C-LIF-037; a plain number with bounds, since `options` needs v2.1.271 or later, C-LIF-038), and the hooks file.

```bash
mkdir -p ~/mods/quick-notes/{.claude-plugin,hooks,tests} && cd ~/mods/quick-notes
cat > .claude-plugin/plugin.json <<'JSON'
{
  "name": "quick-notes", "version": "0.1.0", "author": { "name": "Your Name" },
  "description": "Adds /note and /notes, kept in the mod's store across sessions",
  "userConfig": {
    "show": { "type": "number", "title": "Notes to list", "description": "How many of the newest notes /notes prints",
              "default": 5, "min": 1, "max": 50 }
  }
}
JSON
echo '{ "modules": ["./register.ts"] }' > hooks/hooks.json
```

2. Write `hooks/register.ts`:

```ts
import type { EngineInterface, Register } from 'claude-code'

async function loadNotes($: EngineInterface): Promise<string[]> {
  const saved = await $.store.get('notes')
  return Array.isArray(saved) ? saved.filter((one): one is string => typeof one === 'string') : []
}

export const register: Register = (on, options) => {
  const show = typeof options.show === 'number' ? options.show : 5
  on('session.start', async ($, e, next) => {
    // A taken name throws and would skip the rest of the hook, so catch each call (C-LIF-055)
    const failed = (error: unknown) => $.ui.log(`quick-notes: ${String(error)}`, { to: 'debug' })
    await $.command.register({ name: 'note', description: 'Save a note', argumentHint: '<text>' }).catch(failed)
    await $.command.register({ name: 'notes', description: 'List the newest notes' }).catch(failed)
    return next(e)
  })
  on('command.run', { command: 'note' }, async ($, e) => {
    const text = e.args.trim()
    if (text === '') return { text: 'Usage: /note <text>' }
    // Read right before writing: $.store is shared by every session on the machine
    const notes = [...(await loadNotes($)), text].slice(-200)
    await $.store.set('notes', notes)
    return { text: `Saved note ${notes.length}.` }
  })
  on('command.run', { command: 'notes' }, async $ => {
    const notes = await loadNotes($)
    if (notes.length === 0) return { text: 'No notes yet.' }
    return { text: notes.slice(-show).map((note, i) => `${i + 1}. ${note}`).join('\n') }
  })
}
```

`loadNotes` takes `$` and is declared at the top level, which static analysis accepts (`$.store.get (via loadNotes)`); passing `$` to a function defined inside a hook or imported from another file fails validation (C-LIF-017). `EngineInterface` is the type of `$`, exported from `claude-code` (types header).

3. Validate (C-LIF-014) with `claude plugin validate ~/mods/quick-notes`. Expect `hooks: session.start, command.run{command=note}, command.run{command=notes}` and `calls: $.command.register, $.store.get (via loadNotes), $.store.set, $.ui.log`.

4. Write `tests/quick-notes.test.ts`. `mock.store` answers `$.store` from memory (C-LIF-026); `test(name, { options }, body)` sets userConfig values on 2.1.288 (C-LIF-029).

```ts
import { expect, mock, test } from 'claude-code/testing'

// $.command.run takes the full CommandRunInput in tests: origin and presentation are required (types 2.1.288 L1610-1636)
const RUN = { origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } } as const

test('/note saves and /notes lists, newest last', async ($, on) => {
  mock.store(on, { notes: ['first'] })
  const one = await $.command.run({ command: 'note', args: 'buy milk', ...RUN })
  expect(one.text).toBe('Saved note 2.')
  const list = await $.command.run({ command: 'notes', args: '', ...RUN })
  expect(list.text).toBe('1. first\n2. buy milk')
})
test('/note with no text prints usage and saves nothing', async ($, on) => {
  mock.store(on)
  expect((await $.command.run({ command: 'note', args: '   ', ...RUN })).text).toBe('Usage: /note <text>')
  expect((await $.command.run({ command: 'notes', args: '', ...RUN })).text).toBe('No notes yet.')
})
test('the show option limits the list', { options: { show: 1 } }, async ($, on) => {
  mock.store(on, { notes: ['a', 'b', 'c'] })
  expect((await $.command.run({ command: 'notes', args: '', ...RUN })).text).toBe('1. c')
})
test('session.start registers both commands', async ($, on) => {
  const names: string[] = []
  on('session.start', () => ({ cwd: '/work' }))
  on('command.register', ($, e) => (names.push(e.name), { value: { command: e.name } }))
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  expect(names).toEqual(['note', 'notes'])
})
```
> [!contradiction]
> The docs' test examples (docs-mods-test L31, L122) omit fields the 2.1.288 typings require: `origin` and `presentation` on `$.command.run` (types 2.1.288 L1610-1636) and a typed `value` on a `command.register` stub. The snippet above follows the typings and compiles under the generated tsconfig (strict, `noUncheckedIndexedAccess`) with tsc 5.9.3, checked 2026-10-03.

5. Run, then check the command headlessly and interactively (docs-mods-create):

```bash
cd ~/mods/quick-notes && claude plugin test
claude -p "/notes" --plugin-dir ~/mods/quick-notes
claude --plugin-dir ~/mods/quick-notes
```

The headless run prints `quick-notes: No notes yet.` or the list, with the plugin name in front. To set the option for a `--plugin-dir` load, use `/config` (a row per non-sensitive field, C-LIF-040) or `pluginConfigs` keyed `quick-notes@inline` (C-LIF-039).

## Outputs

Two commands, persistent storage in the plugin's own store file, one user option, four tests. Each reply is a `CommandOutput` row another hook could redraw as a tree (lif-plugin-authoring-skill).

## Gates

- Validate passes and the `calls:` line shows only `$.command`, `$.store` and `$.ui.log`: no process, fs or network reach. EVIDENCE-BASED
- All four tests pass, including the `options` case. If the `options` test fails to compile or run, your build predates that kit feature (see contradiction below). CONTESTED
- `claude -p "/notes" --plugin-dir ...` prints the expected text. EVIDENCE-BASED

> [!contradiction]
> A community report on 2.1.282 says `claude plugin test` cannot set userConfig values (gh-issue-91870 comment 5827373997). The 2.1.288 typings declare `TestOptions.options` (types L14924-14945) and the bundled skill documents it. Typings win for 2.1.288; not executed by this lane (C-LIF-029, X-LIF-01).

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `"/note" refused: it is the built-in /note` style throw in the debug log | Name taken | Rename; the `.catch` keeps the other command alive (C-LIF-055) |
| `/notes` replies `registered /notes but no command.run hook answered it` | Hook skipped or matcher typo | Look for `hook skipped` naming `command.run` (docs-mods-troubleshoot) |
| Module does not load: `options do not fit plugin.json userConfig` | Stored value above `max` or wrong type | Fix the `pluginConfigs` entry the line names (C-LIF-039) |
| Validate fails `$.store is used as a value` | `$` aliased or destructured | Write every call in full (C-LIF-017) |
| Notes lost between two sessions | Read at start, write later: a race | Read right before each write, as above (docs-mods-interface) |
| Command typed mid-turn waits | Commands wait for the turn by default | Add `immediate: true` at registration (C-LIF-057) |

## Rollback

Quit the session; nothing is installed. To erase stored notes, add a temporary `$.store.delete('notes')` command or delete the plugin's store file under `~/.claude/plugins/store/` (docs-mods-interface). Delete the folder to remove the mod.

## Caveats

- `$.store` holds 4 MiB of JSON in total and is shared by every session on the machine; `get` then `set` is not atomic (docs-mods-reference, docs-mods-interface).
- Command arguments are written into the transcript, so a command cannot take private input (gh-issue-91870 comment 5827373997, SINGLE-SOURCE).
- Not executed by this lane; written against docs and 2.1.288 typings.

## Related

Command events and registration live in [[Agent and Command Events]] and [[Mods API Namespaces]]; storage trade-offs in [[State Store and Module Variables]]. The option is explained in [[userConfig and Plugin Options]]. Checks: [[Plugin Validate]], [[Testing Kit]], [[Testing Playbook]]. For a command that opens UI, continue with [[Build a Pane Flow]]. Output that the model reads has a cost: [[Usage Cost Surface]].

## Sources

- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-test: https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)
- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- docs-plugins-manifest-reference: https://code.claude.com/docs/en/plugins/manifest-reference (retrieved 2026-10-03)
- types-2-1-288: local `.raw/captures/types-2.1.288/claude-code/index.d.ts` (`command.register` L2870-2887, `TestOptions` L14924-14945)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
