---
type: "entity"
title: "hamzafer claude-code-mods"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.287"
tags:
  - "#domain/claude-code-mods"
  - "#type/entity"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Mod Catalog]]"
  - "[[Playground Sample Mods]]"
  - "[[Usage Cost Surface]]"
  - "[[Holding a Tool Call]]"
  - "[[Observe Rewrite Answer]]"
  - "[[Reach Levels]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[How is $.model.classify billed]]"
  - "[[OneWave claude-code-mods]]"
source_urls:
  - "https://github.com/hamzafer/claude-code-mods (retrieved 2026-10-03, pinned 543abfa670c2242779c9f93cf2ee414a4709a300)"
sources:
  - "eco-gh-hamzafer"
  - "eco-static-scan"
  - "types-2-1-288"
  - "compass-report"
---

# hamzafer claude-code-mods

hamzafer/claude-code-mods is a personal collection of 13 mods (bands, guards, panes and two games) published as one marketplace (C-ECO-040). Several are tailored to the author's own tools (OneForm, unpause, a named Codex model, macOS Chrome), three re-implement the playground samples, and three make a model call after every turn (C-ECO-041). The repo has no license file, so its code cannot be reused safely, and the useful ideas are better taken from the official samples or rebuilt.

## Identity and pin

| Field | Value |
|---|---|
| Repo | `hamzafer/claude-code-mods`, 0 stars, no LICENSE file |
| Pinned commit | `543abfa670c2242779c9f93cf2ee414a4709a300` (2026-10-02T19:39:57Z) |
| Requirements | "Needs Claude Code 2.1.287 or later." |
| Install | `claude plugin marketplace add hamzafer/claude-code-mods`; `claude plugin install <mod>@claude-code-mods` |
| Tests | 14 test files across `mods/*/tests/` (not run) |
| Code reviewed | static scan of all 13 modules; targeted reads of where-am-i, rulebook-guard, browser-lanes, oneform-line, reels, mission-control |

## Per-mod footprint

| Mod | What it does | Notable calls | Reach | Usage cost |
|---|---|---|---|---|
| mission-control | turn map of agents and tool calls, plus a Chrome-rendered code map | `process.run` (sh), `fs.write`, `model.complete`, `ui.panes` | L2 | model calls (Haiku after each turn, README) |
| token-weather | context forecast band | `session.usage` | L0 | none |
| where-am-i | goal, current action, next step | `model.complete`, `session.messages` | L2 (drives Claude) | model calls (Haiku after each turn) |
| agent-radar | one line per running subagent | `agent.list`, `session.messages` | L1 | none |
| browser-lanes | Playwright browser ownership; `/browser clean` | `process.run` (ps, lsof, kill, sh), `ui.ask` | L2 | none |
| merge-gate | holds `gh pr merge` until CI is green and one Codex review ran | `process.run` (gh, git), `fs.read`, `ui.ask` | L2 | none of its own |
| oneform-line | author's fitness app day above the prompt | `http.fetch` to a configured `https://` URL | L3 | none |
| rulebook-guard | rewrites em dashes in prose writes and commit text; asks before amend, unformatted push, PII in notes | `process.run` (git, ruff), `ui.ask`; `next({...e, content: undash(...)})` | L2 | none |
| blast-radius | holds `rm -r`, force push, migrations | `process.run` (bash, git, sleep) | L2 | none |
| session-saver | `/park` notes, names untitled sessions | `process.run` (unpause), `model.complete` | L2 | model calls |
| replay-theater | step through last turn's edits | `fs.read` | L1 | none |
| reels | YouTube Shorts pane while Claude works | `process.spawn`, `http.fetch` over a local socket, `ui.blit` | L3 by scanner rules | none, but runs Playwright |
| snake | game pane | store, ui | L0 | none |

(eco-static-scan; every call exists in the 2.1.288 typings, C-ECO-055.)

## Patterns and problems

- **Input rewriting.** rulebook-guard changes `content`, `new_string` and commit `message` before the tool runs. That is the "rewrite" branch of [[Observe Rewrite Answer]] applied to Claude's own writes; it silently alters files. Fine for the author's house style, surprising for anyone else.
- **Opinionated gates.** merge-gate refuses a `codex review` that does not set one specific model, any `codex exec`, and a second review of the same PR (C-ECO-042).
- **Per-turn model calls.** where-am-i and mission-control each call `$.model.complete` after every turn; on a long session that is a steady extra spend (see [[Usage Cost Surface]]).
- **Platform lock.** mission-control hard-codes the macOS Chrome path; on Linux it shows an error line.
- **Process control.** browser-lanes can `kill` browser PIDs after asking.

## Recommendations

- Avoid installing the collection as a whole; pick per mod, and read each module first. EVIDENCE-BASED
- Use the official playground versions of token-weather, blast-radius and replay-theater instead of these copies. PRACTITIONER
- Avoid oneform-line, reels and merge-gate unless you are the author's exact setup; they depend on a private app, Playwright, and a fixed Codex model. EVIDENCE-BASED
- Trial agent-radar if you run many subagents; it is L1 and makes no model calls. PRACTITIONER
- Do not copy code from this repo: there is no license. PRACTITIONER

> [!contradiction]
> The seed report says "11 mods" with "56 tests pass". The pinned README says 13 mods and the tree holds 13 `hooks.json` files; the test count was not checked (C-ECO-040). The repo wins on the mod count; the test claim is unverified.

## Caveats

- Not in the awesome-list scanner data at its pinned SHA (C-ECO-048), so there is no independent footprint grade.
- "Requires 2.1.287" is the author's claim; nothing was loaded here.
- The repo changes daily (last push 2026-10-02); re-pin before acting.

## Related

- [[Mod Catalog]] rows for each mod.
- [[Playground Sample Mods]] for the originals it copies.
- [[Holding a Tool Call]] for the guard mods.
- [[Observe Rewrite Answer]] for rulebook-guard's rewrites.
- [[Usage Cost Surface]] and [[How is $.model.classify billed]] for model-call costs.
- [[Reach Levels]] and [[Audit a Third-Party Mod Flow]] for grading.
- [[OneWave claude-code-mods]], a similar fun-plus-utility collection.

## Sources

- eco-gh-hamzafer: https://github.com/hamzafer/claude-code-mods (retrieved 2026-10-03, pinned 543abfa)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (lead only)
