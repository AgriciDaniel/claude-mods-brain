---
type: "entity"
title: "Built-in diff Mod"
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
  - "[[Render Sites]]"
  - "[[Build a Pane Flow]]"
  - "[[Band and Pane Fallback]]"
  - "[[Tool Events]]"
  - "[[Built-in telemetry Mod]]"
  - "[[Playground Sample Mods]]"
  - "[[Testing Kit]]"
  - "[[Reach Levels]]"
source_urls:
  - "https://github.com/anthropics/claude-code/tree/main/mods/diff (retrieved 2026-10-03, pinned 1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://claude.com/blog/claude-code-mods (retrieved 2026-10-03)"
sources:
  - "eco-gh-anthropics-mods"
  - "docs-mods-overview"
  - "blog-mods-launch"
  - "eco-static-scan"
  - "types-2-1-288"
---

# Built-in diff Mod

`/diff` in Claude Code 2.1.287+ is drawn by a built-in mod, listed in `/plugin` as `cc-plugin-diff`. Its source is public in `anthropics/claude-code/mods/diff` and it is the largest official example of a docked pane with buttons, its own scrolling, and a prompt-context hand-off (C-ECO-001, C-ECO-003). Read it before building any pane; do not copy its size, since about 590 source files and 227 test files serve one command (eco-static-scan).

## Identity and pin

| Field | Value |
|---|---|
| Repo path | `anthropics/claude-code/mods/diff` |
| Pinned commit | `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528` (2026-10-02T20:19:38Z) |
| Manifest | `name: "diff"`, `version: "0.1.0"`, author Anthropic, no `userConfig` |
| Module | `hooks/hooks.json` -> `"modules": ["./register.ts"]` |
| Name in `/plugin` | `cc-plugin-diff` (docs-mods-overview) |
| Where it is on | Interactive terminal sessions (docs-mods-overview) |
| Turn off | Disable in `/plugin`; `/diff` then falls back to the engine's own version (C-ECO-005) |
| Code reviewed | static read of `register.ts`, README and manifests |

The launch post says the built-in `/diff` "is now a mod" and that more built-ins will move to mods (blog-mods-launch).

## Events it hooks

From the README table and `register.ts` (C-ECO-003):

| Event and matcher | What it does |
|---|---|
| `session.start` | Binds the engine once, registers `/diff` via `$.command.register`; leaves the plugin idle if another `/diff` holds the name |
| `ui.render {component:'PromptHint'}` | Reads `viewport.columns` and `isFullscreen` to decide auto-open |
| `ui.render {component:'Pane'}` | Draws the pane when `e.requestId` is its pane id |
| `command.run {command:'diff'}` | Pins the git backend, toggles the pane, returns `{ text }` |
| `command.run {command:['clear','resume']}` | Closes or resets state, forgets the pinned repository |
| `ui.close {id}` | Backs out of the dialog detail view with `{ deny: 'back to the file list' }` |
| `ui.focus {plugin}` | Re-centres the five visible rows on the focus ring |
| `ui.scroll {requestId}` | Scrolls hunks or the list itself, returns `{}` |
| `tool.call {tool:[Edit, Write, NotebookEdit, Bash, PowerShell]}` | After the call, refreshes an open pane; first main-loop edit may open it |
| `prompt.submit` | Appends the armed file's hunks to `e.context`, once |

## Calls on `$`

`clock.after`, `clock.every`, `clock.now`, `command.register`, `env.get` (`CLAUDE_CODE_DISABLE_FILE_CHECKPOINTING`), `fs.list`, `fs.read`, `fs.stat`, `process.run` (git, read-only), `session.id`, `session.messages`, `session.usage`, `settings.read`, `store.get`, `store.set`, `telemetry.log`, `telemetry.mark`, `ui.close`, `ui.invalidate`, `ui.log`, `ui.open`, `ui.resolve`, `ui.status` (eco-static-scan, diff README). All exist in the 2.1.288 typings (C-ECO-055).

Reach: L2, because it runs processes (git). The awesome-list scanner grades it the same, with labels runs processes, reads files, reads env vars, reads settings, reads the transcript, telemetry, persists state, draws (eco-gh-awesome-claude-code-mods). Usage cost: none of its own; an armed "ask" adds the file's hunks to the next prompt's context, so that turn is larger.

## Behaviour worth copying

- **Wrap the engine, then react.** Its `tool.call` hook awaits `next(e)` inside `try/finally` and refreshes after the result, so it never blocks or alters an edit (C-ECO-003). This is the safe observe shape from [[Observe Rewrite Answer]].
- **Auto-open gates.** The main loop's first landed edit opens the pane only when the layout docks it, the terminal is 144 columns or more (110 if the person kept it open before), and checkpointing is on; a subagent's edit opens nothing (C-ECO-004).
- **Placement fallback.** If `$.ui.open` answers `isPlaced === false`, it closes the request at once so a later resize cannot seat a stale pane. Compare [[Band and Pane Fallback]].
- **Debounced refresh.** Refreshes are coalesced with `$.clock.after`, and HEAD is polled with `$.clock.every` only while the pane is open.
- **Per-repo memory.** The comparison base is stored with `$.store.set` keyed by repository top level.

```ts
on('tool.call', { tool: ['Edit', 'Write', 'NotebookEdit', 'Bash', 'PowerShell'] },
  async ($, e, next) => {
    let result
    try {
      result = await next(e)
      return result
    } finally {
      if (host) afterTool(host, e, result)
    }
  })
```

(Shape from `register.ts`, trimmed; `host` and `afterTool` are module-scope in the original.)

## Testing pattern

The repo README shows how the built-ins test: `claude plugin test mods/diff`, `tier('builtin')`, `mock.clock(on)`, and inline `on('process.run', ...)` answers for git (eco-gh-anthropics-mods). The example test asserts that `/diff` outside a git repository opens nothing. See [[Testing Kit]].

## Recommendations

- Read `mods/diff/hooks/register.ts` before building a docked pane; copy the `isPlaced` withdraw and the debounced refresh. EVIDENCE-BASED
- Keep it enabled; it costs no model calls and only runs git when a pane needs data. EVIDENCE-BASED
- If you replace `/diff` with your own mod, disable `cc-plugin-diff` first; with it on, your `$.command.register` for `diff` loses the name. PRACTITIONER
- Do not mirror its file count; a single-command mod should be a few hundred lines. PRACTITIONER

> [!contradiction]
> `mods/README.md` at the pinned commit still says hooks modules load only where function hooks are enabled. The 2.1.287 docs say mods are on by default and the flag is ignored. The docs win (C-ECO-002).

## Caveats

- Verified against source at 1c229fc and typings from 2.1.288; behaviour on 2.1.285 (stable channel) was not checked (see [[Claude Code Release Channels]]).
- Line counts and file counts come from a regex scan, not a build.
- Telemetry rows go through [[Built-in telemetry Mod]]; where analytics are off they are dropped.

## Related

- [[Mod Catalog]] lists this mod with its verdict.
- [[Render Sites]] and [[UI Elements and JSX]] cover `Pane` and `PromptHint`.
- [[Build a Pane Flow]] and [[Band and Pane Fallback]] reuse its open and withdraw pattern.
- [[Tool Events]] explains the `tool.call` matcher it uses.
- [[Built-in telemetry Mod]] provides `$.telemetry`.
- [[Playground Sample Mods]] includes replay-theater, a smaller per-turn diff viewer.
- [[Testing Kit]] and [[Reach Levels]] for test shape and footprint grading.

## Sources

- eco-gh-anthropics-mods: https://github.com/anthropics/claude-code/tree/main/mods/diff (retrieved 2026-10-03, pinned 1c229fc)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- blog-mods-launch: https://claude.com/blog/claude-code-mods (retrieved 2026-10-03)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md` (2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
