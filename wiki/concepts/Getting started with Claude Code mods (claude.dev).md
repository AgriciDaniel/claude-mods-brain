---
type: "concept"
title: "Getting started with Claude Code mods (claude.dev)"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/concept"
  - "#confidence/practitioner"
confidence: "practitioner"
lane: "rewrite"
related:
  - "[[Build a Status Band Flow]]"
  - "[[Holding a Tool Call]]"
  - "[[Build a Tool Call Guard Flow]]"
  - "[[Band and Pane Fallback]]"
  - "[[State Store and Module Variables]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Plugin Validate]]"
  - "[[Testing Kit]]"
  - "[[Render Sites]]"
  - "[[Playground Sample Mods]]"
  - "[[Pitfalls Playbook]]"
  - "[[Mods Trust Model]]"
source_urls:
  - "https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods (retrieved 2026-10-03)"
sources:
  - "claudedev-getting-started"
  - "docs-mods-overview"
  - "docs-mods-reference"
  - "docs-mods-interface"
  - "docs-mods-test"
  - "eco-gh-playground-mods"
  - "types-2-1-288"
---

# Getting started with Claude Code mods (claude.dev)

This note folds canon 003, Addy Osmani's tutorial on claude.dev (2026-10-01, 11 minute read), into the vault. It builds Token Weather, a band above the prompt, from an empty folder, then tours Blast Radius (a held Bash guard) and Replay Theater (pure observation), which match the three playground samples. It is the best worked example in the canon, and its habits are mostly right, but it calls the module sandboxed and its Blast Radius hold loop is a costly pattern; route both through the docs.

## What the work teaches

**Two paths.** A shortcut (describe the mod to Claude, allow hot reload) and a six-step manual build:

1. Folder: `plugin.json`, `hooks/hooks.json` with one module, `types/index.d.ts`, `tests/`.
2. Draw: hook `ui.render` on `{ component: "AbovePrompt" }`, get `Box` and `Text` from `$.ui.resolve(e)`.
3. Read numbers: `$.session.usage()` for `context.tokens`, `context.window`, `context.percent`; observe `session.start` and `turn.complete`, skip turns with `e.agentId`.
4. Draw the forecast: size to `e.props.bodyColumns`, yield when `e.props.hasSurvey`.
5. Validate and test: `claude plugin validate`, then `claude plugin test` with `$.ui.mount`.
6. Share: `.claude-plugin/marketplace.json`, `claude plugin marketplace add`, `claude plugin install ... --scope user`.

**Four habits** it names: generated types are the authority; layout is on `e.props`; keep data in `$.state`; read `claude --debug` for "does not validate" when nothing draws.

**Two larger samples.** Blast Radius hooks `tool.call` on Bash, runs dry runs through `$.process.run` with argv arrays, opens a pane with Proceed and Cancel hotkeys, falls back to the band when `isPlaced` is false. Replay Theater reads old file content with `$.fs.read` before Edit and Write, brackets turns, and registers `/replay`.

## How its claims map onto vault notes

| Tutorial claim | Claim IDs | Vault home | Status |
|---|---|---|---|
| Observe, rewrite, answer | C-API-007 | [[Observe Rewrite Answer]] | verified |
| 10 s own time, `$` time excluded | C-API-012, C-PAT-002 | [[Budgets and Limits]] | verified (types 2.1.288 L4803-4837) |
| Reload is a fresh load, module vars reset | C-LIF-007, C-PAT-040 | [[Hot Reload and Dev Loop]], [[State Store and Module Variables]] | verified |
| Every `$.state` key must be declared | C-LIF-018 | [[Plugin Validate]] | verified |
| Session-written mods are temporary | C-LIF-005 | [[Hot Reload and Dev Loop]] | verified |
| `$.session.usage()` with no breakdown is free | C-SEC-042, C-API-058 | [[Usage Cost Surface]] | verified in typings |
| Yield to surveys via `hasSurvey` | C-PAT-013 | [[Band and Pane Fallback]] | verified |
| Hold a call while a `$` call is pending | C-PAT-001 | [[Holding a Tool Call]] | verified |
| Blast Radius sleep loop | C-PAT-050 | [[Build a Tool Call Guard Flow]] | SINGLE-SOURCE |
| Install with marketplace add and install | C-LIF-050 | [[Marketplaces and Distribution]] | verified |

## Agreement and contradiction

> [!contradiction] Is the module sandboxed? The tutorial says the module "runs in a sandbox of its own, with no DOM and no Node". The overview says "Mods aren't sandboxed" (docs-mods-overview L79). Both describe real layers: the module has no ambient Node, DOM, timers, or network (types 2.1.288 L18-24, C-API-003), but every `$` call runs with the user's full permissions (C-SEC-001). For any trust decision the docs win; see [[Mods Trust Model]].

> [!contradiction] State habit versus the sample it describes. The tutorial says keep data in `$.state`; the published token-weather sample in the playground keeps readings in a module-level `let` (C-ECO-022, eco-gh-playground-mods). The habit is right per docs-mods-interface; the sample is the outlier. See [[Playground Sample Mods]].

- **`describe` in tests.** The canon caveat questioned `describe`, which docs-mods-test does not mention. The 2.1.288 testing typings export it: `export const describe: (name: string, body: () => void) => void` (types 2.1.288 L13986). Resolved: usable.
- **`$.session.usage()` cost.** The canon could not find the "free unless breakdown" statement in docs; the typings carry it (types 2.1.288 L2620-2642, C-SEC-042). Resolved in favour of the tutorial.
- **Hold loop.** Blast Radius polls `$.process.run(["sleep", "0.25"])`, because `$.clock.sleep` counts against the 10 s budget (docs-mods-reference limits). The design thread ([[Mods design thread, anthropics claude-code issue 91870]]) and docs point to `$.ui.ask`, which holds inside one `$` call without spawning a process four times a second.
- **Agrees with Pluto** that text-matching guards are weak: the tutorial itself calls Blast Radius a safety net ([[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]]).

## Verified quotes

Copied from `references/canon/003-getting-started-with-claude-code-mods.md`; each re-found verbatim in `.raw/captures/web-2026-10-03/claudedev-getting-started.txt`.

- "It's a safety net, not a permission system." (capture L401)
- "keep data in $.state, not in module variables" (capture L448)
- "Pass when you have nothing to draw." (capture L276)
- "The module runs in a sandbox of its own, with no DOM and no Node" (capture L39)

## What it gets wrong or leaves stale

- **"Sandbox" wording** invites a false sense of isolation, as above.
- **Busy-wait hold.** Spawning `sleep` four times a second is a workaround, not the documented hold. Prefer `$.ui.ask` or a `$` call that resolves on the decision ([[Holding a Tool Call]]).
- **Two surfaces only.** The `$.ui.mount` loop it shows names terminal and desktop; the 2.1.288 typings add `mobile` and `vscode` (C-API-049), and the testing header says the test names "terminal, desktop, vscode or mobile".
- **"Restart Claude Code if it doesn't show up"** is anecdotal, not documented behaviour.
- **`/clear` blind spot.** It teaches `$.state` but not that `/clear`, `/resume` and `/branch` reset it and skip `session.start`, so state must be reseeded on `classic.SessionStart` (C-API-035, SINGLE-SOURCE).

## How much to trust it

Confidence: practitioner. It is official (claude.dev, rank 3) and its code tracks the docs, but it is a tutorial written at launch against 2.1.287. Copy its structure and habits; verify every API call against [[API Surface 2.1.288]].

- Use Token Weather as the reference build for [[Build a Status Band Flow]]. PRACTITIONER
- Declare every `$.state` key in `types/index.d.ts` before validating. EVIDENCE-BASED
- Pass argv arrays to `$.process.run`, never a shell string. EVIDENCE-BASED
- Use permission rules for hard blocks; text guards miss `$(...)`, aliases, and scripts. PRACTITIONER
- Replace the sleep loop with `$.ui.ask` in any guard you ship. PRACTITIONER

## Caveats

- Byline and date come from the capture header; not independently confirmed.
- Code samples were read, not executed; the brain never loads a mod.
- Version sensitivity: written for 2.1.287; checked against 2.1.288 typings.

## Related

Build flows: [[Build a Status Band Flow]], [[Build a Tool Call Guard Flow]]. Patterns: [[Holding a Tool Call]], [[Band and Pane Fallback]]. State and reload: [[State Store and Module Variables]], [[Hot Reload and Dev Loop]]. Tooling: [[Plugin Validate]], [[Testing Kit]]. Drawing: [[Render Sites]]. Samples: [[Playground Sample Mods]]. Traps: [[Pitfalls Playbook]].

## Sources

- Canon file: `references/canon/003-getting-started-with-claude-code-mods.md`
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (published 2026-10-01, retrieved 2026-10-03), capture `.raw/captures/web-2026-10-03/claudedev-getting-started.txt`
- docs-mods-overview, docs-mods-reference, docs-mods-interface, docs-mods-test: https://code.claude.com/docs/en/plugins/mods/<page> (retrieved 2026-10-03)
- eco-gh-playground-mods: https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` L18-24, L2620-2642, L9695, L13986
