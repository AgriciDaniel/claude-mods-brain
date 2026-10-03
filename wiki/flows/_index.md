---
type: "hub"
title: "Flows Hub"
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
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Build a Pane Flow]]"
  - "[[Build a Slash Command Flow]]"
  - "[[Build a Status Band Flow]]"
  - "[[Build a Tool Call Guard Flow]]"
  - "[[Claim Verification Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
---

# Flows Hub

Runnable procedures, each with Trigger, Prerequisites, Steps, Outputs, Gates, Failure Modes, and Rollback. Build flows create mods; audit and refresh flows keep the owner safe and current.

Parent: [[index|Index]]. Operating contract: [[CONVENTIONS]]. Evidence: [[research-pack-claude-mods|Research Pack]].

## Notes (16)

### lifecycle

- [[Build a Pane Flow]] (developing, evidence-based): A runnable recipe for a pane (a sidebar in a wide fullscreen terminal, a framed region above the prompt otherwise) that lists this session's tool calls, opened by a `/tool-calls` command, with a Clear button, state in `$...
- [[Build a Slash Command Flow]] (developing, evidence-based): A runnable recipe for two slash commands, `/note <text>` and `/notes`, that save and list notes in `$.store` (kept across sessions), with a `userConfig` option for the list length and kit tests that stub the store and pa...
- [[Build a Status Band Flow]] (developing, evidence-based): A runnable recipe for a band above the prompt (the `AbovePrompt` render site) that shows the last turn's duration and tool-call count, keeps its values in `$.state` so a hot reload does not wipe them, and is covered by a...
- [[Publish a Mod Flow]] (developing, evidence-based): A mod is a plugin, so publishing it means listing it in a marketplace: a `.claude-plugin/marketplace.json` in a git repository that people add once and install from by `name@marketplace` (C-LIF-048, C-LIF-050).
- [[Re-verify After Release Flow]] (developing, evidence-based): The mods API is early access and the typings say it "may change between releases without notice" (types L1-10, C-LIF-043).

### patterns-and-ideas

- [[Migrate a Classic Hook Flow]] (developing, evidence-based): Port a settings hook (a `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, or `SessionStart` script) to a mod in two phases: first wrap it with a pass-through `classic.<Event>` hook so nothing changes, then move th...

### rewrite

- [[Claim Verification Flow]] (developing, evidence-based): A mods claim is verified when a rank 1 source (the official docs captures or the 2.1.288 typings, cited by line range) supports it and a second, independent source agrees.
- [[Context Compaction Routine]] (developing, evidence-based): An agent working this brain keeps its context lean by reading in a fixed order: `wiki/hot.md` first, then `wiki/index.md`, then only the notes the task names, and never whole raw captures (the typings file alone is 14,97...
- [[Explore Plan Code Commit]] (developing, evidence-based): Explore, plan, code, commit applied to a mod means: read the generated typings and the docs before writing anything, plan which events the mod hooks and how much of each budget it spends, code it in a folder you own with...
- [[Multi-Agent Fan-Out Research Flow]] (developing, practitioner): This brain was built on 2026-10-03 with parallel research lanes, a merge, automated gates, and a fresh-context critic.
- [[Reporting Workflow]] (developing, practitioner): The brain produces two kinds of report: generated reports that scripts write from JSON (the API surface, one audit per scanned mod, and a capability matrix across the mods you scanned), and hand-written notes that judge ...
- [[Research Refresh Workflow]] (developing, evidence-based): This brain is pinned to Claude Code 2.1.288: the typings capture, the API surface JSON, every note's `tested_on`, and every ledger `refresh_due` of 2026-11-02 assume it.
- [[Source Intake Workflow]] (developing, evidence-based): Every fact in this brain enters through one door: an immutable capture under `.raw/`, a hash row in `.raw/.manifest.json`, a ledger entry in `references/source-ledger.json`, and claim rows in `references/claim-ledger.md`...
- [[Synthesis Workflow]] (developing, practitioner): Synthesis turns three machine inputs into one model of "who uses what": the API surface imported from the typings, a static footprint scan per mod, and an optional curated catalog.

### security-governance

- [[Audit a Third-Party Mod Flow]] (developing, evidence-based): This flow takes a mod someone wants to use and produces a pinned, recorded verdict (adopt, trial, or avoid) without ever loading the mod.
- [[Build a Tool Call Guard Flow]] (developing, evidence-based): A tool call guard is a `tool.call` hook that holds a risky call, asks the user with `$.ui.ask`, and runs it only on an explicit yes.

## Related hubs

[[wiki/concepts/_index|Concepts Hub]] | [[wiki/deliverables/_index|Deliverables Hub]] | [[wiki/entities/_index|Entities Hub]] | [[wiki/platforms/_index|Platforms Hub]] | [[wiki/decisions/_index|Decisions Hub]] | [[wiki/reports/_index|Reports Hub]] | [[wiki/sources/_index|Sources Hub]] | [[wiki/gaps/_index|Gaps Hub]] | [[wiki/questions/_index|Questions Hub]] | [[wiki/experiments/_index|Experiments Hub]] | [[wiki/meta/_index|Meta Hub]] | [[wiki/canvases/_index|Canvases Hub]]
