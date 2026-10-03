---
type: "hub"
title: "Concepts Hub"
domain: "Claude Code mods"
status: "active"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/hub"
  - "#confidence/practitioner"
confidence: "practitioner"
related:
  - "[[index|Index]]"
  - "[[hot|Hot]]"
  - "[[overview|Overview]]"
  - "[[dashboard|Dashboard]]"
  - "[[CONVENTIONS]]"
  - "[[Tag Taxonomy]]"
  - "[[Start Here]]"
  - "[[research-pack-claude-mods|Research Pack]]"
  - "[[Agent and Command Events]]"
  - "[[Band and Pane Fallback]]"
  - "[[Best Practices Kernel]]"
  - "[[Budgets and Limits]]"
  - "[[Classic Hook Bridge]]"
  - "[[Claude Code mods documentation set (Anthropic)]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
---

# Concepts Hub

How Claude Code mods work: the hook chain, events, the `$` API, render sites, state, limits, lifecycle, trust, and the canon folds. Start with [[Mod Anatomy]] and [[Hook Middleware Chain]].

Parent: [[index|Index]]. Operating contract: [[CONVENTIONS]]. Evidence: [[research-pack-claude-mods|Research Pack]].

## Notes (36)

### api-and-events

- [[Agent and Command Events]] (developing, evidence-based): This note covers the events that govern who and what runs: subagents (`agent.offer`, `agent.spawn`), slash commands (`command.run`, `command.describe`), `/config` rows (`config.set`, `config.describe`), other mods (`plug...
- [[Budgets and Limits]] (developing, evidence-based): Mods run under time budgets and size caps that Claude Code enforces per hook and per call: a hook gets 10 seconds of its own execution time per event, a `.catch` handler 1 second, and all `session.end` hooks together 1.5...
- [[Hook Middleware Chain]] (developing, evidence-based): Every hook for one event joins a single middleware chain, Koa style: each hook receives `($, e, next)`, and `next(e)` runs the hooks after it and finally Claude Code's own behavior, resolving to the event's result (C-API...
- [[Hook Ordering and Tiers]] (developing, evidence-based): Hooks for one event nest in a fixed order of five tiers, outermost first: `prepend` (managed mods an admin lists first), `user` (everything a person installs), `append` (managed mods listed last), `builtin` (mods bundled...
- [[Mod Anatomy]] (developing, evidence-based): A mod is an ordinary Claude Code plugin with one extra file: `hooks/hooks.json` names a single hooks module whose `register(on, options)` function registers event handlers (C-API-001).
- [[Mods API Namespaces]] (developing, evidence-based): `$`, the first argument of every hook, is the only way a mod acts: 21 namespaces of methods, from drawing (`$.ui`) and model calls (`$.model`) to files, processes and the network (`$.fs`, `$.process`, `$.http`) (C-API-04...
- [[Observe Rewrite Answer]] (developing, evidence-based): Every mod hook does one of three things with an event, and what it does with `next` decides which (C-API-007).
- [[Prompt Events]] (developing, evidence-based): Ten events cover everything Claude reads as text: what the user submits (`prompt.submit`), what lands in or near the prompt box (`prompt.fill`, `prompt.suggest`, `prompt.edit`), and what Claude Code writes for Claude on ...
- [[Render Sites]] (developing, evidence-based): A render site is a named place in Claude Code's interface where a `ui.render` hook may draw: two empty sites a mod fills (`Pane`, `AbovePrompt`), and thirteen sites Claude Code already draws that a mod can restyle, wrap ...
- [[State Store and Module Variables]] (developing, evidence-based): A mod has three places to keep a value, chosen by how long it must last: a module-level variable (gone on every reload), `$.state` (reactive, survives reloads, reset by `/clear`, `/resume` and `/branch`), and `$.store` (...
- [[Tool Events]] (developing, evidence-based): Three events cover every tool Claude uses: `tool.call` fires when a tool is about to run and can refuse, rewrite, answer or wrap it; `tool.check` fires when Claude Code decides whether the call may run and can flip the d...
- [[Turn and Session Events]] (developing, evidence-based): Turn events follow one answer: `turn.start` when it begins, `turn.step` for every model request inside it (several when tools run), and `turn.complete` when it ends (docs-mods-reference L87-95).
- [[UI Elements and JSX]] (developing, evidence-based): A `ui.render` hook returns a plain-data element tree built from constructors that `$.ui.resolve(e)` hands out for the surface being drawn; elements are never globals (C-API-050; docs-mods-interface L345).

### lifecycle

- [[Hot Reload and Dev Loop]] (developing, evidence-based): A mod is developed against a folder Claude Code watches, so a save reloads the hooks module in the running session without a restart.
- [[Marketplaces and Distribution]] (developing, evidence-based): A mod is a plugin, so it ships the way any plugin does: as a folder people load with `--plugin-dir`, through a marketplace (a git repo or URL holding `.claude-plugin/marketplace.json`), or through Anthropic's directory (...
- [[Plugin Validate]] (developing, evidence-based): `claude plugin validate <path>` reads a plugin's manifest and runs the same static analysis on the hooks module's source that Claude Code runs when it loads a mod, without executing any code or starting a session (C-LIF-...
- [[Testing Kit]] (developing, evidence-based): The testing kit is the module `claude-code/testing`, which `claude plugin test [dir]` loads for every `*.test.ts` and `*.test.tsx` under a mod's folder, each file in a child of the Claude Code binary, with no session, si...
- [[Versioning and API Drift]] (developing, evidence-based): The mods API is early access and moves between Claude Code releases, so the only authority for a given build is the declaration file that build writes beside the mod, not the docs and not the GitHub copy (C-LIF-043).
- [[userConfig and Plugin Options]] (developing, evidence-based): A mod is configured through the ordinary plugin `userConfig` block in `plugin.json`, and its hooks module receives the resolved values as the second argument of `register(on, options)`, defaults filled in (C-LIF-039).

### patterns-and-ideas

- [[Band and Pane Fallback]] (developing, evidence-based): A mod has three places to put a view, in falling order of room: a pane, the band above the prompt (`AbovePrompt`), and plain text (a `$.ui.status` line, a toast, a transcript log, or a command reply).
- [[Classic Hook Bridge]] (developing, evidence-based): Every settings hook event (`Stop`, `SessionStart`, `PostToolUse`, and the rest) is also a mod event named `classic.` plus the event name, and `e` is the same JSON a settings hook reads on stdin, including `transcript_pat...
- [[Holding a Tool Call]] (developing, evidence-based): A `tool.call` hook can pause a tool call by awaiting before it calls `next(e)` or returns; the call stays pending until the hook settles (docs-mods-events).
- [[Mods vs Classic Hooks]] (developing, evidence-based): Classic hooks (the docs now call them "settings hooks") are commands, HTTP calls, MCP tool calls, prompts, or agents that Claude Code launches per event from a settings file or a plugin's `hooks/hooks.json`; mods are Jav...
- [[Prompt Cache Discipline]] (developing, evidence-based): A mod that changes what Claude reads can silently make every request a cache miss.

### rewrite

- [[Best Practices Kernel]] (developing, evidence-based): The fifteen rules that prevent most mod failures on Claude Code 2.1.288, distilled from the Pitfalls Playbook, the Patterns Playbook and the official docs.
- [[Claude Code mods documentation set (Anthropic)]] (developing, evidence-based): This note folds canon 001, the ten official mods pages on code.claude.com captured on 2026-10-03, into the vault.
- [[Claude Code plugins and hooks documentation (Anthropic)]] (developing, evidence-based): This note folds canon 006, the thirteen non-mods plugin and settings-hook pages captured on 2026-10-03, into the vault.
- [[Customize Claude Code with mods (Anthropic blog)]] (developing, evidence-based): This note folds canon 002, Anthropic's launch post of 2026-10-01, into the vault.
- [[Getting started with Claude Code mods (claude.dev)]] (developing, practitioner): This note folds canon 003, Addy Osmani's tutorial on claude.dev (2026-10-01, 11 minute read), into the vault.
- [[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]] (developing, contested): This note folds canon 005, Ehud Melzer's Pluto Security article of 2026-09-22, into the vault.
- [[Mods design thread, anthropics claude-code issue 91870]] (developing, practitioner): This note folds canon 004, the public request for comment that became mods, into the vault.

### security-governance

- [[Mods Trust Model]] (developing, evidence-based): A mod is code that runs with your user permissions inside Claude Code, and it is not sandboxed (docs-mods-overview, blog-mods-launch).
- [[Org Mod Controls]] (developing, evidence-based): Administrators control mods through managed settings in three layers: the built-in guard `sec-default` and its two options, the plugin-loading keys that already govern every plugin, and an optional policy mod of your own...
- [[Prompt Injection via Mods]] (developing, evidence-based): Mods touch prompt injection in two directions.
- [[Reach Levels]] (developing, practitioner): Reach levels L0 to L3 are a practitioner taxonomy from karanb192's community scanner, not an Anthropic classification.
- [[Usage Cost Surface]] (developing, evidence-based): A mod spends your usage only through a short list of mechanisms: model calls through `$.model.*`, turns it starts, subagents it starts or reroutes, and text it adds to what Claude reads.

## Related hubs

[[wiki/flows/_index|Flows Hub]] | [[wiki/deliverables/_index|Deliverables Hub]] | [[wiki/entities/_index|Entities Hub]] | [[wiki/platforms/_index|Platforms Hub]] | [[wiki/decisions/_index|Decisions Hub]] | [[wiki/reports/_index|Reports Hub]] | [[wiki/sources/_index|Sources Hub]] | [[wiki/gaps/_index|Gaps Hub]] | [[wiki/questions/_index|Questions Hub]] | [[wiki/experiments/_index|Experiments Hub]] | [[wiki/meta/_index|Meta Hub]] | [[wiki/canvases/_index|Canvases Hub]]
