---
title: "Getting started with Claude Code mods"
author: "Addy Osmani"
publisher: "claude.dev Blog"
year: "2026"
date: "2026-10-01"
url: "https://claude.dev/blog/getting-started-with-claude-code-mods/"
source_capture: ".raw/captures/web-2026-10-03/claudedev-getting-started.txt"
retrieved: "2026-10-03"
confidence: "practitioner"
tags:
  - "#domain/claude-code-mods"
  - "#type/canon"
  - "#source/official"
  - "#confidence/practitioner"
---

# "Getting started with Claude Code mods" (Addy Osmani, claude.dev, 2026-10-01)

Byline and date are in the capture header (author Addy Osmani, published Oct 01, 2026, 11 min read). It is the tutorial the launch post links to. It builds one mod, Token Weather, from an empty folder, then tours two larger samples, Blast Radius and Replay Theater, which match the three sample mods in the `claude-code-playground` repository named in docs-mods-overview.

## Core Thesis

You do not need to learn the API to get a mod: describe it to Claude and allow hot reload. But a mod worth keeping follows a small set of habits: let the generated types be the reference, read layout from `e.props`, keep anything that must survive a save in `$.state`, and read the debug log when a drawing does not show. The tutorial teaches the observe, rewrite, answer model through real code rather than prose.

## How It Works

- **Shortcut path**: paste a descriptive prompt ("Make me a Claude Code mod called token-weather ..."), accept hot reload once, iterate by asking for tweaks. The mod lives only in that session's folder and is cleaned up later, so copy it out to keep it.
- **Manual path, six steps**:
  1. Folder: `plugin.json`, `hooks/hooks.json` with one module, `types/index.d.ts`, `tests/`.
  2. Draw: hook `ui.render` on `{ component: "AbovePrompt" }`, get `Box` and `Text` from `$.ui.resolve(e)` (elements are per surface, not globals; JSX works with `h`).
  3. Read numbers: `$.session.usage()` gives `context.tokens`, `context.window`, `context.percent`. Observe on `session.start` and `turn.complete` (skip `e.agentId` subagent turns). Store history in `$.state`, declared in `interface PluginState` and pointed to by the manifest `types` field.
  4. Draw the forecast: about 80 lines, sized to `e.props.bodyColumns`, yielding to surveys via `e.props.hasSurvey`.
  5. Validate and test: `claude plugin validate` prints `types`, `hooks`, `calls (via helper)`, `state reads/writes`; `claude plugin test` stubs `session.usage` and mounts `AbovePrompt` with `$.ui.mount`.
  6. Share: a folder with `.claude-plugin/marketplace.json`, then `claude plugin marketplace add` and `claude plugin install ... --scope user`.
- **Blast Radius**: `tool.call` on Bash classifies risky commands, runs dry-run commands (`git status --porcelain`, `git clean -n`) through `$.process.run` with argv arrays, opens a pane with Proceed and Cancel hotkeys, and falls back to the band when `$.ui.open` returns `isPlaced: false`. It waits by looping on short `sleep` processes until a button sets the decision or `next.signal` aborts.
- **Replay Theater**: pure observation. Records Edit and Write diffs (reads old file content with `$.fs.read` before the write), brackets them with `turn.start` and `turn.complete`, and registers `/replay`.

## Key Principles

1. Types written into `.claude-plugin/types/` are the authority for your build.
2. Layout props live on `e.props`; only `component`, `surface`, `requestId`, `viewport` sit on `e`.
3. Return `next(e)` when you have nothing to draw, giving the site back to Claude Code and other mods.
4. A hot reload is a fresh load: `register` and `session.start` run again and module variables reset.
5. `$.state` reads inside a render hook subscribe the drawing, so `$.state.set` redraws without `$.ui.invalidate`.
6. Time inside `$` calls does not count against a hook's 10 seconds, which is what makes holding a call possible.
7. A text-matching guard is a safety net, not a permission system.

## Best Practices

- Start from a prompt that describes the output, not the API; let the built-in `plugin-authoring` skill handle the how. PRACTITIONER
- Declare every `$.state` key in `types/index.d.ts`, or validate fails with an error naming the fix. EVIDENCE-BASED
- Use single-width symbols, not emoji, so bands line up in every terminal font. PRACTITIONER
- Pass `argv` arrays to `$.process.run` so paths are never run as shell code. EVIDENCE-BASED
- Degrade from pane to band when `isPlaced` is false; let the surface decide dock versus inline placement. EVIDENCE-BASED
- Filter out `e.agentId` when you only want main-loop turns. EVIDENCE-BASED
- Use permission rules for hard blocks; text guards miss `$(...)`, aliases, and scripts. PRACTITIONER
- When a drawing fails, run `claude --debug` and search for "does not validate". EVIDENCE-BASED

## Verified Quotes

- "It's a safety net, not a permission system." (Blast Radius section)
- "keep data in $.state, not in module variables" ("Four habits worth keeping")
- "Use single-width symbols, not emoji." (Step 4, details worth copying)
- "Pass when you have nothing to draw." (Step 4, details worth copying)
- "The module runs in a sandbox of its own, with no DOM and no Node" ("How a mod works")

## Evidence Caveats

- **Contested wording on sandboxing.** The tutorial says the module "runs in a sandbox of its own". The docs say "Mods aren't sandboxed" (docs-mods-overview). Both are true at different layers: the module has no ambient Node, DOM, or network (an isolation boundary, confirmed by @poteat on #91870), but every `$` call runs with the user's full permissions. Readers who take "sandbox" as OS isolation will be misled. Docs win for the trust claim.
- **Busy-wait pattern.** Blast Radius polls `$.process.run(["sleep", "0.25"])` rather than `$.clock.sleep`, because the docs count `$.clock.sleep` against the budget (docs-mods-reference#limits). It spawns a process four times a second while held; `$.ui.ask` is the documented cheaper hold.
- The test uses `describe`, `$.ui.mount`, and `as any` casts. `$.ui.mount` is documented (docs-mods-test, "Test a drawing"), but `describe` does not appear in docs-mods-test; confirm it in the 2.1.288 typings before copying.
- `$.session.usage()` is described as free unless a breakdown is requested; this lane did not find that statement in the docs.
- "Install takes three commands" then "If it doesn't show up, restart Claude Code" is anecdotal guidance, not documented behavior.

## Brain Hooks

- [[Build a Status Band Flow]]: Token Weather is the reference build.
- [[Holding a Tool Call]] and [[Build a Tool Call Guard Flow]]: Blast Radius hold loop and its limits.
- [[Band and Pane Fallback]]: `isPlaced` false leads to the band.
- [[State Store and Module Variables]]: the reload trap and `$.state` declaration.
- [[Hot Reload and Dev Loop]]: shortcut path and `--plugin-dir` watch.
- [[Plugin Validate]] and [[Testing Kit]]: sample validate output and the mount test.
- [[Render Sites]] and [[UI Elements and JSX]]: `AbovePrompt`, `$.ui.resolve`, `h`.
- [[Playground Sample Mods]]: token-weather, blast-radius, replay-theater.
- [[Patterns Playbook]] and [[Pitfalls Playbook]]: the four habits and the text-guard limit.
- [[Ranked Build Ideas]]: the five starter ideas at the end.
