---
type: "hub"
title: "Entities Hub"
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
  - "[[Arunjay4213 claude-mods]]"
  - "[[Built-in agents-md Mod]]"
  - "[[Built-in diff Mod]]"
  - "[[Built-in sec-default Mod]]"
  - "[[Built-in telemetry Mod]]"
  - "[[Mod Directories]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
---

# Entities Hub

Specific mods and repos: the built-ins, official examples, community mods pinned by SHA, and directories.

Parent: [[index|Index]]. Operating contract: [[CONVENTIONS]]. Evidence: [[research-pack-claude-mods|Research Pack]].

## Notes (13)

- [[Arunjay4213 claude-mods]] (developing, evidence-based): Arunjay4213/claude-mods is a marketplace of four small session trackers built as mods: context-lens, quota-meter, token-ledger and budget-guard (C-ECO-031).
- [[Built-in agents-md Mod]] (developing, evidence-based): Claude Code reads `AGENTS.md` through a built-in mod, `cc-plugin-agents-md`, configured by one option, `instructionFiles` (C-ECO-006).
- [[Built-in diff Mod]] (developing, evidence-based): `/diff` in Claude Code 2.1.287+ is drawn by a built-in mod, listed in `/plugin` as `cc-plugin-diff`.
- [[Built-in sec-default Mod]] (developing, evidence-based): sec-default is the built-in guard Claude Code seats first in the prepend tier on machines with managed settings or for Team and Enterprise organizations.
- [[Built-in telemetry Mod]] (developing, evidence-based): The telemetry mod (`cc-plugin-telemetry`) implements `$.telemetry.log` and `$.telemetry.mark` for Claude Code and its built-in mods, adding the noun in the `engine.create` fold and sending batched first-party analytics r...
- [[Mod Directories]] (developing, evidence-based): Five public lists catalogue community mods.
- [[OneWave claude-code-mods]] (developing, evidence-based): OneWave-AI/claude-code-mods is ten mods "built in one night" by OneWave AI, MIT licensed, with tests for each and a "mix of useful and ridiculous" tone (C-ECO-043).
- [[Playground Sample Mods]] (developing, evidence-based): Anthropic's DevRel team publishes three unsupported sample mods in `anthropics/claude-code-playground/claude-code/mods`: token-weather (a band), blast-radius (a tool-call hold with a pane) and replay-theater (a slash com...
- [[cc-pr-tracker]] (developing, evidence-based): cc-pr-tracker watches GitHub pull requests from inside a session: paste a PR URL and it gets one line above the prompt with merge state, review decision and required checks, refreshed every minute, with a toast, a flash ...
- [[cctop]] (developing, evidence-based): cctop is a btop-style dashboard for a running Claude Code session: context fill and time to autocompact, tokens and cost with cache-hit ratio, rate limits with an exhaustion forecast, per-tool latency, subagents, touched...
- [[code-modernization Plugin]] (developing, evidence-based): code-modernization 1.0.0 is Anthropic's legacy-modernization plugin in the official marketplace (`claude-plugins-official`).
- [[hamzafer claude-code-mods]] (developing, evidence-based): hamzafer/claude-code-mods is a personal collection of 13 mods (bands, guards, panes and two games) published as one marketplace (C-ECO-040).
- [[karanb192 claude-code-mods]] (developing, evidence-based): karanb192/claude-code-mods is a marketplace with one skill and two mods: `mod-builder` (a skill that plans a mod's "capability budget", validates it, and writes a five-line threat model), `fable-pin` (a 36-line mod that ...

## Related hubs

[[wiki/concepts/_index|Concepts Hub]] | [[wiki/flows/_index|Flows Hub]] | [[wiki/deliverables/_index|Deliverables Hub]] | [[wiki/platforms/_index|Platforms Hub]] | [[wiki/decisions/_index|Decisions Hub]] | [[wiki/reports/_index|Reports Hub]] | [[wiki/sources/_index|Sources Hub]] | [[wiki/gaps/_index|Gaps Hub]] | [[wiki/questions/_index|Questions Hub]] | [[wiki/experiments/_index|Experiments Hub]] | [[wiki/meta/_index|Meta Hub]] | [[wiki/canvases/_index|Canvases Hub]]
