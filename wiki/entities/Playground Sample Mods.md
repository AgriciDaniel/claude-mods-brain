---
type: "entity"
title: "Playground Sample Mods"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/entity"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Mod Catalog]]"
  - "[[Holding a Tool Call]]"
  - "[[Build a Status Band Flow]]"
  - "[[Build a Tool Call Guard Flow]]"
  - "[[Band and Pane Fallback]]"
  - "[[State Store and Module Variables]]"
  - "[[Budgets and Limits]]"
  - "[[Built-in diff Mod]]"
  - "[[hamzafer claude-code-mods]]"
source_urls:
  - "https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods (retrieved 2026-10-03, pinned 569c5283d9a0a7ee7938df85bb32e4f48cbb8c86)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)"
sources:
  - "eco-gh-playground-mods"
  - "docs-mods-overview"
  - "docs-mods-reference"
  - "claudedev-getting-started"
  - "eco-static-scan"
---

# Playground Sample Mods

Anthropic's DevRel team publishes three unsupported sample mods in `anthropics/claude-code-playground/claude-code/mods`: token-weather (a band), blast-radius (a tool-call hold with a pane) and replay-theater (a slash command and pane) (C-ECO-020). They are the smallest official, readable examples (122, 528 and 249 lines of plain `.mjs`), and the docs point to them as the place to start (docs-mods-overview). Start new band, guard or pane work by reading the matching sample.

## Identity and pin

| Field | Value |
|---|---|
| Repo | `anthropics/claude-code-playground`, Apache-2.0, 51 stars |
| Pinned commit | `569c5283d9a0a7ee7938df85bb32e4f48cbb8c86` (2026-10-01T16:11:57Z) |
| Marketplace | `claude-code-playground-mods` (owner "Claude Code DevRel"), "Shared as-is" |
| Version claim | each README: needs 2.1.287+, built and tested on 2.1.280, `claude plugin validate` passes on 2.1.285 |
| Code reviewed | static read of all three `.mjs` modules and READMEs |

Try one for a session with `claude --plugin-dir ./token-weather`; to keep one, add the clone's `claude-code/mods` folder as a marketplace. The marketplace points at your clone, so moving the clone breaks the install (docs-mods-overview).

## The three mods

| Mod | Events | `$` calls | Reach | Usage cost |
|---|---|---|---|---|
| token-weather | `session.start`, `turn.complete`, `ui.render {component:'AbovePrompt'}` | `session.usage`, `ui.invalidate`, `ui.resolve` | L0 | none |
| blast-radius | `tool.call {tool:'Bash'}`, `ui.render` Pane and AbovePrompt | `process.run` (git, bash, sleep), `session.cwd`, `clock.now`, `ui.open`, `ui.close`, `ui.invalidate`, `ui.resolve`, `ui.toast` | L2 | none |
| replay-theater | `session.start`, `command.run {command:'replay'}`, `tool.call`, `turn.start`, `turn.complete`, `ui.render` AbovePrompt and Pane, `ui.close` | `command.register`, `fs.read`, `fs.exists`, `session.cwd`, `clock.sleep`, `ui.open`, `ui.close`, `ui.invalidate`, `ui.resolve` | L1 | none |

(eco-static-scan, read by hand.)

## token-weather: the band template

Reads `$.session.usage().context` after each main-loop `turn.complete` (skipping `e.agentId`), keeps the last 12 readings, and draws one line with forecast bands:

| Percent of window | Icon and word |
|---|---|
| under 25 | Clear |
| 25 to 49 | Cloudy |
| 50 to 74 | Showers |
| 75 to 89 | Storm |
| 90 and up | Compact soon |

It yields when `e.hasSurvey` is set and when it has no reading, and only adds the bar chart at 60 columns or more. See [[Build a Status Band Flow]].

## blast-radius: holding a tool call

The hold loop is the reason to read this file (C-ECO-021):

```js
while (mine.decision === null) {
  if (next.signal.aborted) { mine.decision = "interrupted"; break; }
  if ((await $.clock.now()) - startedAt > HOLD_LIMIT_MS) { mine.decision = "timeout"; break; }
  await $.process.run(["sleep", POLL_SECONDS], { timeoutMs: 5000 });
}
```

- Time inside a mods API call does not count against the 10 s hook budget, except `$.clock.sleep`, which does (docs-mods-reference limits row). Hence `process.run(["sleep", "0.25"])`.
- Only one call is held at a time (`held` is claimed with no `await` between check and claim).
- Anything unexpected sets `decision = "error"` and the call is denied with a reason telling Claude not to retry.
- If `$.ui.open` answers `isPlaced: false`, the same report is drawn in the AbovePrompt band ([[Band and Pane Fallback]]).
- README: the classifier and hold-queue fixes were covered by Node tests against a stand-in, "they haven't been re-run in a live session".

See [[Holding a Tool Call]] and [[Build a Tool Call Guard Flow]].

## replay-theater: command plus pane

Registers `/replay` in `session.start` after `next(e)`, records edits in `tool.call` without blocking, swaps pending to replay on main-loop `turn.complete`, and draws a band hint with a `Button` (`hotkey: "r"`). MultiEdit handling and the band fallback are marked untested in its README.

## Recommendations

- Copy blast-radius's sleep-loop hold, `next.signal.aborted` check, 10-minute cap and deny-on-error for any guard. EVIDENCE-BASED
- Copy token-weather's `e.hasSurvey` yield and `agentId` skip for any band. EVIDENCE-BASED
- Keep history in `$.state` rather than module variables when you adapt token-weather, as the getting-started post says. EVIDENCE-BASED
- Prefer these originals over community copies (hamzafer ships its own token-weather, blast-radius and replay-theater with no license). PRACTITIONER

> [!contradiction]
> The getting-started post tells authors to keep data in `$.state`, not module variables (claudedev-getting-started). The published token-weather keeps `let readings = []` and blast-radius keeps `let held = null` at module level (C-ECO-022). For your own mods, follow the post and docs-mods-interface; the samples lose only cosmetic state on reload.

## Caveats

- "Tested on 2.1.280, validates on 2.1.285" is the authors' claim; this lane did not load the mods.
- The playground is "shared as-is, without support"; expect breakage on API changes.
- The seed report's "Blast Radius pattern with `$.ui.ask`" is wrong: the sample never calls `$.ui.ask`.

## Related

- [[Mod Catalog]] rows for all three.
- [[Holding a Tool Call]], [[Build a Tool Call Guard Flow]] for blast-radius.
- [[Build a Status Band Flow]] for token-weather.
- [[Band and Pane Fallback]] for the `isPlaced` fallback.
- [[State Store and Module Variables]] for the state contradiction.
- [[Budgets and Limits]] for the 10 s rule.
- [[Built-in diff Mod]] for a production-scale pane.
- [[hamzafer claude-code-mods]] for derived copies.

## Sources

- eco-gh-playground-mods: https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods (retrieved 2026-10-03, pinned 569c528)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
