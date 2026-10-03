---
type: "entity"
title: "Arunjay4213 claude-mods"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.272"
tags:
  - "#domain/claude-code-mods"
  - "#type/entity"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Mod Catalog]]"
  - "[[cctop]]"
  - "[[Build a Status Band Flow]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Usage Cost Surface]]"
  - "[[Reach Levels]]"
  - "[[State Store and Module Variables]]"
  - "[[Versioning and API Drift]]"
  - "[[Turn and Session Events]]"
source_urls:
  - "https://github.com/Arunjay4213/claude-mods (retrieved 2026-10-03, pinned d4fffd7de9204a62b10e7b3604fc893158fa25fd)"
  - "https://github.com/anthropics/claude-code/issues/91870#issuecomment-5669755348 (retrieved 2026-10-03)"
sources:
  - "eco-gh-arunjay4213"
  - "eco-static-scan"
  - "eco-gh-awesome-claude-code-mods"
  - "gh-issue-91870"
  - "docs-mods-overview"
  - "compass-report"
---

# Arunjay4213 claude-mods

Arunjay4213/claude-mods is a marketplace of four small session trackers built as mods: context-lens, quota-meter, token-ledger and budget-guard (C-ECO-031). The first three only read `$.session.usage()`, draw a pinned line and a pane, and persist readings: the smallest footprint of any usage mod in this lane (L0, C-ECO-032). budget-guard is different in kind: it refuses tool calls, aborts turns and gates prompts once a cost or quota limit passes (L2). The repo predates GA (last push 2026-09-15) and its install steps still set the obsolete flag (C-ECO-033).

## Identity and pin

| Field | Value |
|---|---|
| Repo | `Arunjay4213/claude-mods`, 3 stars |
| Pinned commit | `d4fffd7de9204a62b10e7b3604fc893158fa25fd` (2026-09-15T19:01:51Z) |
| License | README and `budget-guard/plugin.json` say MIT; no LICENSE file; GitHub reports none (C-ECO-031) |
| Requirements | "Claude Code 2.1.269 or newer"; checked-in types "Written by Claude Code 2.1.272" |
| Install | `claude plugin marketplace add Arunjay4213/claude-mods`, then `claude plugin install <mod>@claude-mods` |
| Announced | #91870 comment by the author, 2026-09-14 (gh-issue-91870, issuecomment-5669755348) |
| Code reviewed | static read of all four `register.tsx` files (363 to 704 lines each) |

## The four mods

| Mod | Pinned line | Pane | Events | Calls beyond ui.* | Reach |
|---|---|---|---|---|---|
| context-lens | window used, growth per turn, turns left before compaction | `/context-lens` | session.start, turn.complete, session.compact, command.run, ui.render, ui.close | session.usage, command.register | L0 |
| quota-meter | 5-hour and 7-day plan limits, reset countdown, projected exhaustion | `/quota` | session.start, turn.complete, command.run, ui.render, ui.close | session.usage, store.get/set, clock.every/now | L0 |
| token-ledger | session cost, last turn cost, tokens, cache hit ratio | `/ledger` | session.start, turn.complete, command.run, ui.render, ui.close | session.usage, session.id, store.get/set | L0 |
| budget-guard | only near a limit | `/guard` | session.start, turn.start, turn.complete, tool.call, prompt.submit, command.run | turn.abort, config.set, ui.ask, store, clock.after, session.usage | L2 |

(eco-static-scan; the awesome-list scanner gives the same levels and "passed" validate on 2.1.287, eco-gh-awesome-claude-code-mods.) Usage cost: none for all four; budget-guard reduces spend by stopping turns.

## budget-guard behaviour

- `userConfig`: `costLimitUsd` (default 0, off), `fiveHourLimitPercent` (90), `sevenDayLimitPercent` (95), `warnAtPercent` (80).
- At the warn mark it toasts once and pins a line; past a limit in `block` mode it refuses the next tool call (subagents included) and calls `$.turn.abort` on the running turn, because "a model that is refused one tool tries another" (README).
- A new prompt past a limit raises a `$.ui.ask` with "Send anyway" and "Do not send"; the latter drops the prompt.
- `/guard override` allows one turn; limits are changed through `$.config.set`.

## quota-meter caveats from its README

- API-key sessions report no plan limits; the line says so.
- The 7-day projection needs about 8.4 hours of readings before it says anything.
- Readings persist in `$.store`, so a restart inside the window keeps the rate.

## Recommendations

- Trial context-lens, token-ledger and quota-meter as the lowest-reach usage view; they only draw and remember. EVIDENCE-BASED
- Delete the `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` step from its README when installing; 2.1.287+ ignores it. EVIDENCE-BASED
- Trial budget-guard only with explicit limits set; it can stop a running turn mid-task by design. EVIDENCE-BASED
- Do not vendor or fork the code until a LICENSE file exists; a README line is weak license evidence. PRACTITIONER

> [!contradiction]
> The seed report calls this a "trio" of trackers. The pinned tree has four plugins, and the fourth (budget-guard) is L2 with `$.turn.abort` (C-ECO-031, C-ECO-032). The repo wins.

## Caveats

- Not updated since 2026-09-15; written against 2.1.272 types. Static validation on 2.1.287 comes from the scanner, not the author.
- `$.config.set` behaviour was noted by the author as build-specific ("On the Claude Code build this was written against (2.1.272)"); recheck on 2.1.288.
- Footprint from regex scan plus reading; nothing was loaded.

## Related

- [[Mod Catalog]] rows for all four.
- [[cctop]] is the heavier alternative.
- [[Build a Status Band Flow]] for the pinned-line pattern.
- [[userConfig and Plugin Options]] for budget-guard's options.
- [[Usage Cost Surface]] and [[Reach Levels]] for grading.
- [[State Store and Module Variables]] for `$.store` persistence.
- [[Versioning and API Drift]] for the 2.1.272 pin.
- [[Turn and Session Events]] for `turn.complete` sampling.

## Sources

- eco-gh-arunjay4213: https://github.com/Arunjay4213/claude-mods (retrieved 2026-10-03, pinned d4fffd7)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870#issuecomment-5669755348 (retrieved 2026-10-03)
- eco-gh-awesome-claude-code-mods: https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03, pinned 59a9911)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (lead only)
