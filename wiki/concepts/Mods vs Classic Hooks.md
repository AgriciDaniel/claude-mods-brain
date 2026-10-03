---
type: "concept"
title: "Mods vs Classic Hooks"
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
lane: "patterns-and-ideas"
related:
  - "[[Classic Hook Bridge]]"
  - "[[Migrate a Classic Hook Flow]]"
  - "[[Mod Anatomy]]"
  - "[[Hook Middleware Chain]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Mods Trust Model]]"
  - "[[Org Mod Controls]]"
  - "[[Budgets and Limits]]"
  - "[[Patterns Playbook]]"
  - "[[Holding a Tool Call]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/hooks-guide (retrieved 2026-10-03)"
sources:
  - "docs-mods-overview"
  - "docs-mods-events"
  - "docs-mods-reference"
  - "docs-hooks"
  - "docs-hooks-guide"
  - "claudedev-getting-started"
  - "gh-issue-91870"
  - "pa-gh-91870-mined"
  - "docs-mods-interface"
  - "docs-mods-api"
  - "docs-mods-troubleshoot"
  - "compass-report"
---

# Mods vs Classic Hooks

Classic hooks (the docs now call them "settings hooks") are commands, HTTP calls, MCP tool calls, prompts, or agents that Claude Code launches per event from a settings file or a plugin's `hooks/hooks.json`; mods are JavaScript or TypeScript functions loaded once into Claude Code's own process (docs-mods-overview, docs-hooks L15). Both keep working side by side: the hooks reference says the hooks "keep working alongside mods" (docs-hooks L15, quote). Pick a settings hook to block, allow, or log with a script you already have; pick a mod for a pane, a band, a command with no turn, a registered tool, or a rewrite of an arbitrary event (docs-mods-overview compare table).

## Side by side

| Dimension | Settings hook | Mod | Source |
|---|---|---|---|
| Where it runs | Separate process per event (or HTTP, MCP, model) | In process, one shared hooks worker for installed mods | docs-hooks L404-410; docs-mods-troubleshoot |
| Language | Any; JSON on stdin, exit code and JSON on stdout | JavaScript or TypeScript ES module exporting `register(on, options)` | docs-hooks; docs-mods-reference |
| Handler types | `command`, `http`, `mcp_tool`, `prompt`, `agent` | function hooks `($, e, next)` | docs-hooks L404-410; docs-mods-events |
| Concurrency | All matching hooks run in parallel; identical handlers in several settings files run once | One sequential middleware chain per event | docs-hooks L412; docs-mods-events |
| Multiple input rewrites | Last `updatedInput` to finish wins, nondeterministic | Each mod passes its copy to `next`; order is deterministic | docs-hooks-guide L963; docs-mods-events |
| Default timeout | 600 s command, http, mcp_tool; 30 s prompt; 60 s agent | 10 s of the hook's own time per event; waits inside `next` and `$` calls do not count | docs-hooks L426; docs-mods-reference |
| On timeout | `PreToolUse` command hook does not block; call continues | Hook skipped; call continues unless `.catch` answers | docs-hooks L841-845; docs-mods-events |
| State between events | None in process (files only) | Module variables, `$.state`, `$.store` | docs-mods-interface |
| Draw UI | No (only `terminalSequence`) | Panes, band, replace built-in rows | docs-mods-overview |
| Register commands or tools | No | `$.command.register`, `$.tool.register` | docs-mods-api |
| Change system prompt, tool descriptions, compaction, subagent model | Limited (`additionalContext`) | `prompt.section`, `tool.describe`, `session.compact`, `agent.spawn` | docs-mods-reference |
| Runs inside subagents | Yes, settings and plugin hooks | `tool.call` fires for subagent calls; `e.agentId` identifies them | docs-hooks L269; docs-mods-events |
| Turned off by | `disableAllHooks` | `disableAllHooks`, disabling the plugin, `--safe-mode`; not built-in mods | docs-mods-overview |
| Where org blocks sit | Managed `PreToolUse` blocks are final, before any mod | Mods cannot lift managed blocks; `tool.check` can lift a non-managed `PreToolUse` block | docs-mods-events; docs-hooks-guide L971 |

## Ordering when both exist

For a tool call the order is: managed-settings `PreToolUse` hooks, then each mod's `tool.call` hook from outermost to innermost, then (inside the last `next`) non-managed `PreToolUse` hooks from settings and plugin `hooks.json` plus the permission rules, then `tool.check` hooks, then the tool (docs-mods-events "Where settings hooks run in the order"). Two consequences:

- A mod that answers `tool.call` without `next` stops your own `PreToolUse` scripts from running at all (docs-mods-events). EVIDENCE-BASED
- A mod on `tool.check` can approve a call your own `PreToolUse` hook blocked, unless that hook is managed (docs-hooks-guide L971). With `sec-default` loaded (managed machines, Team and Enterprise), a mod cannot lift a `deny` rule unless `allowModsToOverrideDenyRules` is set (docs-mods-reference). EVIDENCE-BASED

## What only classic hooks do

Documented capabilities with no direct mod equivalent in the docs (lane subagent summary of docs-hooks, spot-checked):

- `CLAUDE_ENV_FILE` to persist environment variables from `SessionStart`, `Setup`, `CwdChanged`, `FileChanged`.
- `WorktreeCreate` and `WorktreeRemove` replacement of worktree handling.
- Handlers in any language, HTTP endpoints, and `prompt` or `agent` handlers that run a model without code.
- `async: true` background command hooks and `asyncRewake`.
- Survival under `allowManagedHooksOnly` when the hook is managed.

A mod reaches most of these moments through `classic.<Event>` (see [[Classic Hook Bridge]]), but for env files and worktrees, keep the shell hook.

## Overhead

On #91870, @deafsquad ([comment 5542444779](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5542444779), 2.1.260) and @sirmaelstrom ([5617960003](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5617960003), 2026-09-10) measured the chain as strictly serial: eight 300 ms function hooks took 2,427 ms against 640 ms for the same work as parallel command hooks, with about 3 ms host overhead per link. Staff advice ([5618866247](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5618866247)) was to start `next(e)` without awaiting it before slow independent work, and to use `tool.check` for parallel guards. These are pre-release numbers (SINGLE-SOURCE per figure), but the serial shape follows from the docs' single chain. Slow work in a mod hook adds directly to every tool call; move it to a timer or after `next`. PRACTITIONER

The same thread measured the interleave on 2.1.261: settings command hooks run inside `next(e)`, so a mod deny means no classic `PreToolUse` or `PostToolUse` hook runs (@gbrussich52, [5555855461](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5555855461)), which the 2.1.287 docs now state. EVIDENCE-BASED

## Decision rule

| You want | Use |
|---|---|
| Block a fixed command or path | A permission rule, no code (docs-mods-events) |
| Block or log with an existing script | Settings hook |
| Decision depending on live state (branch, recorded value) | Mod `tool.check` or `tool.call` |
| Anything drawn, any slash command with no turn, any registered tool | Mod |
| Persist env vars, replace worktrees | Settings hook |
| Org-wide enforcement | Managed settings hook or a `prependPlugins` policy mod |

## Caveats

- Ordering text is from the 2.1.287 docs as captured on 2026-10-03 against 2.1.288; not observed live.
- Overhead figures are pre-release and secondhand.
- The pre-release warning that older Claude Code builds can drop a whole `hooks.json` with unknown keys is unverified on 2.1.288 (compass-report L164).

## Related

The in-process bridge is [[Classic Hook Bridge]] and the port procedure is [[Migrate a Classic Hook Flow]]. Mod structure is in [[Mod Anatomy]] and the chain in [[Hook Middleware Chain]] and [[Hook Ordering and Tiers]]. Trust and org controls are in [[Mods Trust Model]] and [[Org Mod Controls]]; time limits in [[Budgets and Limits]]. The guard pattern that replaces a `PreToolUse` script is [[Holding a Tool Call]], and shapes are collected in [[Patterns Playbook]].

## Sources

- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-hooks: https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)
- docs-hooks-guide: https://code.claude.com/docs/en/hooks-guide (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (capture retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (secondary, lead list only)
