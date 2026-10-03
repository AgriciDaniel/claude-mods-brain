---
type: "overview"
title: "Overview"
domain: "Claude Code mods"
status: "active"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/overview"
  - "#confidence/evidence-based"
confidence: "evidence-based"
related:
  - "[[hot|Hot]]"
  - "[[index|Index]]"
  - "[[Mod Anatomy]]"
  - "[[Hook Middleware Chain]]"
  - "[[Mods API Namespaces]]"
  - "[[Render Sites]]"
  - "[[Mods Trust Model]]"
  - "[[Versioning and API Drift]]"
  - "[[Mod Catalog]]"
  - "[[Mods vs Classic Hooks]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://claude.com/blog/claude-code-mods (retrieved 2026-10-03)"
---

# Overview

A Claude Code mod is a plugin whose `hooks/hooks.json` names one hooks module; that module exports `register(on, options)` and runs inside Claude Code's own process for the whole session. Hooks have the shape `($, e, next)`, nest into a middleware chain, and can observe, rewrite, or answer an event; every side effect goes through `$`. Mods are on by default from Claude Code 2.1.287 and are not sandboxed. #confidence/evidence-based

![brain relationship map](../_attachments/brain-relationship-map.svg)

## The domain in five layers

| Layer | The question it answers | Start here |
|---|---|---|
| Anatomy and chain | What is a mod and how does a hook run? | [[Mod Anatomy]], [[Hook Middleware Chain]], [[Observe Rewrite Answer]], [[Hook Ordering and Tiers]] |
| Events | What can a mod see and change? | [[Tool Events]], [[Prompt Events]], [[Turn and Session Events]], [[Agent and Command Events]], [[Classic Hook Bridge]] |
| The `$` API and interface | What can a mod do, and where can it draw? | [[Mods API Namespaces]], [[Render Sites]], [[UI Elements and JSX]], [[State Store and Module Variables]], [[Budgets and Limits]] |
| Lifecycle | How is a mod built, tested, shipped, and kept working? | [[Hot Reload and Dev Loop]], [[Testing Kit]], [[Plugin Validate]], [[Marketplaces and Distribution]], [[Versioning and API Drift]] |
| Trust and governance | What can go wrong, and who controls it? | [[Mods Trust Model]], [[Reach Levels]], [[Usage Cost Surface]], [[Prompt Injection via Mods]], [[Org Mod Controls]] |

## What changed with mods

Settings hooks (now "classic" hooks) launch a command, HTTP call, prompt, or agent per event and talk JSON over stdin. A mod is loaded once, keeps state, gets typed objects, can draw UI, register commands and tools, and rewrite arbitrary events. Anthropic moved `/diff` to a mod and plans to move more built-ins over time (blog-mods-launch). See [[Mods vs Classic Hooks]].

## The three facts that shape every decision

1. **The API moves.** The typings header says the surface may change between releases without notice, so every claim here carries `tested_on`, and [[Re-verify After Release Flow]] runs on each release.
2. **A mod runs as you.** It can read files anywhere, run programs, reach the network, approve tool calls, and spend usage. A static scan and `claude plugin validate` are evidence, not a verdict ([[Audit a Third-Party Mod Flow]]).
3. **The cheapest mods draw.** Display-only mods built on `$.session.usage()` cost no tokens; model calls, started turns, registered tools, and unstable prompt text cost usage or bust the cache ([[Usage Cost Surface]], [[Prompt Cache Discipline]]).

## Ecosystem at a glance

Four built-ins live in `anthropics/claude-code/mods` (diff, agents-md, sec-default, telemetry), Anthropic ships code-modernization as an official mod, and the community had 359 mods in 373 repos by 2026-10-02. [[Mod Catalog]] grades 40 of them; [[Ranked Build Ideas]] lists what is still worth building.

## How this brain is organized

Evidence in `.raw/` (hashed) and `references/` (ledgers, canon); knowledge in `wiki/`; generated reports from `scripts/`; agents in `agents/`. The navigation path is [[hot|Hot]], [[index|Index]], one hub, one note.
