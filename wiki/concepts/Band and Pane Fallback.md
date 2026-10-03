---
type: "concept"
title: "Band and Pane Fallback"
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
  - "[[Render Sites]]"
  - "[[UI Elements and JSX]]"
  - "[[Build a Pane Flow]]"
  - "[[Build a Status Band Flow]]"
  - "[[code-modernization Plugin]]"
  - "[[Playground Sample Mods]]"
  - "[[Holding a Tool Call]]"
  - "[[Patterns Playbook]]"
  - "[[Pitfalls Playbook]]"
  - "[[Built-in diff Mod]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
sources:
  - "docs-mods-interface"
  - "docs-mods-overview"
  - "docs-mods-reference"
  - "docs-mods-troubleshoot"
  - "claudedev-getting-started"
  - "code-modernization-1-0-0"
---

# Band and Pane Fallback

A mod has three places to put a view, in falling order of room: a pane, the band above the prompt (`AbovePrompt`), and plain text (a `$.ui.status` line, a toast, a transcript log, or a command reply). A pane the mod opens on its own only appears at 144 terminal columns or more (110 after the user has opened it once), and `$.ui.open` tells you with `{ isPlaced: false, reason }` (docs-mods-interface). Drawing does not happen at all in the VS Code chat panel, `claude -p`, the Agent SDK, or cloud sessions, even though hooks run there (docs-mods-overview). A robust mod plans all three tiers.

## The ladder

| Tier | When it is available | How to draw | Source |
|---|---|---|---|
| Pane (dock beside transcript) | Wide fullscreen terminal, Desktop | `$.ui.open({ id })`, then `ui.render` `{ component: 'Pane' }` checking `e.requestId` | docs-mods-interface |
| Pane (inline, framed above prompt) | Narrower terminals when user-opened | Same tree; placement is the surface's job | claudedev-getting-started (Replay Theater) |
| Band | Terminal and Desktop, always present, shared by every mod | `ui.render` `{ component: 'AbovePrompt' }` | docs-mods-interface |
| Status line, toast, log | Any drawing surface | `$.ui.status`, `$.ui.toast`, `$.ui.log` | docs-mods-api |
| Text only | Every session including `-p` | `command.run` returns `{ text }`; `turn.complete` returns `{ text }` | docs-mods-api, docs-mods-events |

Paraphrase: the overview says a drawing mod can detect the app it runs in and fall back to a transcript line or a command's text reply (docs-mods-overview). The check is `e.surface` inside `ui.render`, one of `terminal`, `desktop`, `mobile` or `vscode` (types 2.1.288 L9683-9695), and `$.session.surfaces()` outside it (docs-mods-reference).

## Rule 1: user-initiated opens always place

A pane opened from a command the user ran or a button the user pressed appears at any width; only self-initiated opens (timer, `turn.start`, a `tool.call` hook) wait for 144 columns (docs-mods-interface). So the cheapest fallback is a one-row band with a button that opens the pane. The official code-modernization plugin does exactly this: with the pane hidden it draws a one-line bar with a show button, and pressing it opens the pane, then toasts the reason if it still did not place (code-modernization-1-0-0 `hooks/register.ts` L779-835, L603-613). EVIDENCE-BASED

## Rule 2: check isPlaced, then degrade

```typescript
const opened = await $.ui.open({ id: 'blast-radius', title: 'Blast Radius', focus: true })
if (!opened.isPlaced) held.where = 'band' // draw the same report above the prompt
```

This is Blast Radius's shape (claudedev-getting-started). Its `AbovePrompt` hook draws the held report when `held.where === 'band'`, so a narrow terminal still gets the Proceed and Cancel buttons. Note that `focus: true` is honoured only when the pane places; band buttons are reachable by digit hotkeys typed into an empty prompt (docs-mods-reference, Button rules). EVIDENCE-BASED

## Rule 3: share the band

The band is one strip that every mod shares; a tree you return replaces what mods after you draw (docs-mods-interface). To coexist, put `await next(e)` inside your `Box`:

```typescript
on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
  if (e.props.hasSurvey || !rows.length) return next(e)
  const { Box, Text } = $.ui.resolve(e)
  const theirs = await next(e)
  const mine = Text({ dimColor: true, children: ['fleet: ' + rows.join('  ')] })
  return theirs ? Box({ flexDirection: 'column', children: [mine, theirs] }) : mine
})
```

A personal band mod reviewed for this vault composes this way, but it does not check `hasSurvey`, which the getting-started post and the official plugin both yield to (claudedev-getting-started; code-modernization-1-0-0 L797). EVIDENCE-BASED

## Rule 4: size to the site, not the window

- Draw to `e.props.bodyColumns`, which is narrower than the terminal when a pane is docked (docs-mods-reference, claudedev-getting-started).
- `e.viewport.rows` is the whole window, not your pane (docs-mods-reference).
- A docked pane's height is `e.props.scroll.bodyRows`; an inline pane grows to a limit you can raise with `rows` on `$.ui.open` (docs-mods-reference).
- Use single-width glyphs, not emoji, so columns line up (claudedev-getting-started). PRACTITIONER

## Rule 5: surface differences

| Item | Terminal | Desktop | Source |
|---|---|---|---|
| `Pane`, `AbovePrompt`, `Spinner`, transcript sites | yes | yes | docs-mods-reference |
| `ToolProgress`, `TurnDuration`, `InfoNotice` | yes | no | docs-mods-reference |
| `Svg` element | no | yes | docs-mods-reference |
| `Raster`, `Image` elements | yes | no | docs-mods-reference |
| `/diff` pane from the built-in diff mod | interactive terminal sessions only | not listed | docs-mods-overview |

A drawing that works in the terminal and not in Desktop usually uses a terminal-only site or element (docs-mods-troubleshoot). An invalid tree makes Claude Code draw its own content at that site, silently outside `--plugin-dir` and `--debug` (docs-mods-troubleshoot).

## Recommendations

- Treat the band as the default home and the pane as an upgrade the user asks for. PRACTITIONER
- Always branch on `isPlaced`; never assume `$.ui.open` showed anything. EVIDENCE-BASED
- Yield the band to surveys with `next(e)` when `e.props.hasSurvey` is true. EVIDENCE-BASED
- Compose with `await next(e)` in the band so other mods stay visible. EVIDENCE-BASED
- Give every drawing mod a text path (`/command` reply or `turn.complete` `{ text }`) for `-p`, VS Code and cloud sessions. EVIDENCE-BASED
- Do not pass `focus: false`, `closeOnEscape: false` or `holdToasts: false`; omit them, because `false` throws (docs-mods-interface). EVIDENCE-BASED

## Caveats

- The 144 and 110 column thresholds are from the 2.1.287 docs, unchanged in the 2.1.288 capture; re-check after each release.
- The code-modernization capture in `.raw/` is missing its `hooks/fleet/` directory, so `claude plugin validate` fails on it; the band code read here is unaffected but the plugin could not be validated end to end.
- Desktop behaviour was not observed by this lane.

## Related

Site names and props are in [[Render Sites]] and elements in [[UI Elements and JSX]]. Builds that apply this are [[Build a Pane Flow]] and [[Build a Status Band Flow]]. Reference implementations are [[code-modernization Plugin]] and Blast Radius in [[Playground Sample Mods]]; the hold that needs the fallback is [[Holding a Tool Call]]. Collected in [[Patterns Playbook]] and [[Pitfalls Playbook]]; the built-in pane example is [[Built-in diff Mod]].

## Sources

- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/` (retrieved 2026-10-03)
