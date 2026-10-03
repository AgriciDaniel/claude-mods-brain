---
type: "report"
title: "API Surface 2.1.288"
domain: "Claude Code mods"
status: "evergreen"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/report"
  - "#confidence/evidence-based"
confidence: "evidence-based"
generated_by: "scripts"
related:
  - "[[Mods API Cheatsheet]]"
  - "[[Mod Anatomy]]"
  - "[[Hook Middleware Chain]]"
  - "[[Mods API Namespaces]]"
  - "[[Render Sites]]"
  - "[[UI Elements and JSX]]"
  - "[[Tool Events]]"
  - "[[Prompt Events]]"
  - "[[Turn and Session Events]]"
  - "[[Agent and Command Events]]"
  - "[[Versioning and API Drift]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Classic Hook Bridge]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
sources:
  - "types-2-1-288"
  - ".raw/captures/types-2.1.288/claude-code/index.d.ts"
---

# API Surface 2.1.288

Generated from the typings Claude Code 2.1.288 wrote for a mod (`claude-code/index.d.ts`, 14973 lines, sha256 `d0531eb1b9f9a05f...`). It lists 43 engine events, 61 op events, 33 classic events, 21 `$` namespaces, and 439 exported types. Line numbers cite the capture as `types 2.1.288 L<n>`. #confidence/evidence-based

Read [[Mods API Cheatsheet]] for how to use these, [[Hook Middleware Chain]] for the hook shape, and [[Versioning and API Drift]] for why this note is regenerated after every release.

## Engine events

Hook these with `on(event, matcher?, hook)`. See [[Tool Events]], [[Prompt Events]], [[Turn and Session Events]], and [[Agent and Command Events]].

| Event | Line | What the typings say |
|---|---|---|
| `tool.call` | L3741 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `tool.check` | L3753 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `ui.render` | L3765 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `ui.resolve` | L3774 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `ui.press` | L3783 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `ui.input` | L3792 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `ui.select` | L3801 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `ui.message` | L3810 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `ui.scroll` | L3822 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `ui.focus` | L3834 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `agent.offer` | L3845 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `agent.spawn` | L3854 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `prompt.submit` | L3863 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `prompt.fill` | L3875 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `prompt.suggest` | L3887 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `prompt.edit` | L3899 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `prompt.section` | L3911 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `prompt.context` | L3923 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `prompt.compose` | L3932 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `prompt.attachment` | L3944 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `tool.describe` | L3958 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `command.run` | L3970 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `command.describe` | L3982 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `config.set` | L3994 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `config.describe` | L4006 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `telemetry.log` | L4018 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `telemetry.mark` | L4029 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `skill.prompt` | L4040 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `attribution.text` | L4051 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `session.start` | L4063 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `session.receive` | L4075 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `session.append` | L4087 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `session.send` | L4099 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `session.compact` | L4111 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `session.attach` | L4123 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `session.detach` | L4131 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `session.measure` | L4143 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `session.end` | L4155 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `plugin.register` | L4167 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `turn.start` | L4172 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `turn.step` | L4181 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `turn.complete` | L4190 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |
| `engine.create` | L4199 | [docs: events](https://code.claude.com/docs/en/plugins/mods/events) |

## Op events

Every `$` method is also an event of the same name, so an earlier mod can observe or answer a later mod's call (for example `ui.close` or `fs.read`). See [[Mods API Namespaces]].

| Op event | Line | What the typings say |
|---|---|---|
| `model.complete` | L6410 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `model.classify` | L6414 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `model.fork` | L6422 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `audio.play` | L6427 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `audio.speak` | L6435 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `mcp.call` | L6439 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `mcp.connect` | L6447 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.cwd` | L6453 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.root` | L6457 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.model` | L6461 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.turns` | L6465 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.id` | L6469 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.messages` | L6474 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.repo` | L6478 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.surface` | L6484 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.surfaces` | L6488 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.authorize` | L6492 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.usage` | L6496 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `session.version` | L6500 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `turn.abort` | L6504 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `prompt.read` | L6510 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `tool.list` | L6514 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `tool.register` | L6518 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `command.list` | L6522 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `command.register` | L6526 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `config.list` | L6530 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `agent.list` | L6534 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `agent.register` | L6539 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.toast` | L6543 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.status` | L6550 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.log` | L6557 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.notice` | L6564 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.invalidate` | L6571 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.open` | L6578 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.close` | L6583 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.panes` | L6587 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.selection` | L6591 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.copy` | L6596 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `ui.blit` | L6601 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `fs.read` | L6606 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `fs.write` | L6613 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `fs.list` | L6620 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `fs.exists` | L6626 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `fs.stat` | L6633 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `fs.ancestors` | L6640 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `store.get` | L6644 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `store.set` | L6650 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `store.delete` | L6657 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `store.keys` | L6663 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `state.get` | L6668 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `state.set` | L6676 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `clock.now` | L6680 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `clock.sleep` | L6685 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `clock.after` | L6690 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `clock.every` | L6695 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `http.fetch` | L6699 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `process.run` | L6706 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `process.spawn` | L6713 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `settings.read` | L6717 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `env.get` | L6721 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |
| `env.set` | L6728 | [docs: mods API](https://code.claude.com/docs/en/plugins/mods/api) |

## Classic events

Settings hook events a mod can hook as `classic.<Event>`, receiving the same stdin JSON. See [[Classic Hook Bridge]].

`classic.ConfigChange`, `classic.CwdChanged`, `classic.DirectoryAdded`, `classic.Elicitation`, `classic.ElicitationResult`, `classic.FileChanged`, `classic.InstructionsLoaded`, `classic.MessageDisplay`, `classic.Notification`, `classic.PermissionDenied`, `classic.PermissionRequest`, `classic.PostCompact`, `classic.PostModelSwitch`, `classic.PostToolBatch`, `classic.PostToolUse`, `classic.PostToolUseFailure`, `classic.PreCompact`, `classic.PreModelSwitch`, `classic.PreToolUse`, `classic.SessionEnd`, `classic.SessionStart`, `classic.Setup`, `classic.Stop`, `classic.StopFailure`, `classic.SubagentStart`, `classic.SubagentStop`, `classic.TaskCompleted`, `classic.TaskCreated`, `classic.TeammateIdle`, `classic.UserPromptExpansion`, `classic.UserPromptSubmit`, `classic.WorktreeCreate`, `classic.WorktreeRemove`

## Namespaces and members

| Namespace | Line | Members |
|---|---|---|
| `$.plugin` | L2136 | `name` (L2140), `root` (L2144) |
| `$.ui` | L2150 | `notice` (L2163), `invalidate` (L2177), `blit` (L2198), `resolve` (L2214), `log` (L2230), `ask` (L2246), `toast` (L2261), `status` (L2273), `open` (L2296), `close` (L2310), `panes` (L2323), `scroll` (L2338), `focus` (L2354), `copy` (L2368), `selection` (L2382) |
| `$.model` | L2387 | `complete` (L2414), `fork` (L2433), `classify` (L2452) |
| `$.audio` | L2457 | `play` (L2473), `speak` (L2487) |
| `$.mcp` | L2493 | `call` (L2514), `connect` (L2528) |
| `$.session` | L2534 | `messages` (L2567), `cwd` (L2571), `root` (L2579), `model` (L2583), `turns` (L2588), `id` (L2592), `repo` (L2600), `surfaces` (L2612), `surface` (L2620), `usage` (L2642), `version` (L2659), `compact` (L2671), `send` (L2685), `append` (L2697), `authorize` (L2709) |
| `$.turn` | L2714 | `abort` (L2727) |
| `$.prompt` | L2733 | `submit` (L2745), `read` (L2756), `fill` (L2770), `suggest` (L2782), `compose` (L2794) |
| `$.tool` | L2799 | `list` (L2807), `call` (L2819), `check` (L2831), `register` (L2847) |
| `$.command` | L2852 | `list` (L2860), `run` (L2872), `register` (L2887) |
| `$.config` | L2893 | `list` (L2904), `set` (L2918) |
| `$.telemetry` | L2924 | `log` (L2942), `mark` (L2957) |
| `$.agent` | L2962 | `spawn` (L2974), `list` (L2979), `register` (L3005) |
| `$.fs` | L3015 | `read` (L3034), `write` (L3041), `list` (L3055), `exists` (L3060), `stat` (L3113), `ancestors` (L3134) |
| `$.store` | L3143 | `get` (L3150), `set` (L3158), `delete` (L3162), `keys` (L3166) |
| `$.state` | L3176 | `get` (L3192), `set` (L3208) |
| `$.clock` | L3218 | `now` (L3225), `sleep` (L3239), `after` (L3246), `every` (L3256) |
| `$.http` | L3261 | `fetch` (L3282) |
| `$.process` | L3290 | `run` (L3307), `spawn` (L3345) |
| `$.settings` | L3355 | `read` (L3370) |
| `$.env` | L3380 | `get` (L3390), `set` (L3401) |

## Render components

`RenderComponent` (L8712): `AskUserQuestion`, `UserMessage`, `AssistantMessage`, `ToolUse`, `ToolResult`, `ToolGroup`, `ToolProgress`, `CommandOutput`, `Spinner`, `TurnDuration`, `InfoNotice`, `SessionMode`, `PromptHint`, `AbovePrompt`, `Pane`. See [[Render Sites]].

## Elements by surface

Destructure from `$.ui.resolve(e)`; there are no element globals. See [[UI Elements and JSX]].

| Surface | Line | Elements |
|---|---|---|
| terminal | L3595 | Box, Text, Button, Input, Select, Link, Code, Markdown, Client, Raster, Image |
| desktop | L3616 | Box, Text, Button, Input, Select, Svg, Link, Code, Markdown, Client |
| mobile | L3634 | Box, Text, Button, Svg, Link, Code, Markdown |
| vscode | L3650 | Box, Text, Button, Input, Select, Svg, Link, Code, Markdown |

## Caveats

- Generated by `scripts/import_mod_types.py` and `scripts/render_api_cheatsheet.py`; do not edit by hand. Regenerate after a Claude Code update and diff with `scripts/diff_api_surface.py` (see [[Re-verify After Release Flow]]).
- This edition omits the type definitions' own wording and links each row to the official docs page; line numbers refer to the `index.d.ts` that Claude Code writes beside any mod you load.
- The typings header says the surface may change between releases without notice.

## Sources

- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`, written by Claude Code 2.1.288, captured 2026-10-03.
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03).
