---
type: "concept"
title: "UI Elements and JSX"
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
lane: "api-and-events"
related:
  - "[[Render Sites]]"
  - "[[State Store and Module Variables]]"
  - "[[Budgets and Limits]]"
  - "[[Mod Anatomy]]"
  - "[[Build a Pane Flow]]"
  - "[[Build a Status Band Flow]]"
  - "[[Band and Pane Fallback]]"
  - "[[Testing Kit]]"
  - "[[Pitfalls Playbook]]"
  - "[[Mods API Cheatsheet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/gallery (retrieved 2026-10-03)"
sources:
  - "docs-mods-reference"
  - "docs-mods-interface"
  - "docs-mods-gallery"
  - "types-2-1-288"
---

# UI Elements and JSX

A `ui.render` hook returns a plain-data element tree built from constructors that `$.ui.resolve(e)` hands out for the surface being drawn; elements are never globals (C-API-050; docs-mods-interface L345). Each surface has its own table, so the same tree can be valid in the terminal and invalid on another surface. In a `.tsx` or `.jsx` module the tree can be written as JSX against those constructors, compiled with the `h` and `Fragment` globals (types 2.1.288 L13784-13800).

## Element tables per surface (2.1.288)

| Element | terminal | desktop | mobile | vscode | Main props | Evidence |
|---|:-:|:-:|:-:|:-:|---|---|
| `Box` | yes | yes | yes | yes | flex layout, `gap`/`columnGap`/`rowGap`, `padding*`, `margin*`, `width`, `height`, `min*`, `borderStyle`, `borderColor`, `backgroundColor`, `position`, `overflow`, `display`, `hover`, `key` | types L741-836 |
| `Text` | yes | yes | yes | yes | `color`, `backgroundColor`, `bold`, `italic`, `underline`, `strikethrough`, `dimColor`, `inverse`, `wrap`, `hover` | types L11869-11886 |
| `Button` | yes | yes | yes | yes | `key`, `label`, `onPress` (required), `hotkey`, `action`, `plain`, `dimColor`, `variant`, `role`, `autoFocus` | types L900-1000 |
| `Link` | yes | yes | yes | yes | `href`: an `https:` URL or `http://localhost` only, 2048 printable ASCII; any other scheme (such as `file:`) refuses the whole tree (C-API-061); `label?` | types L5330-5348 |
| `Code` | yes | yes | yes | yes | `source` (10,000 chars), `language?`, `path?`, `startLine?`, `format?: 'diff'`, `wrap?` | types L1453-1505 |
| `Markdown` | yes | yes | yes | yes | `text` (10,000 chars), `key?`, `dimColor?`, `onLinkPress?`, `pressableLinks?` | types L5385-5426 |
| `Input` | yes | yes | no | yes | `key`, `onSubmit` (required), `label`, `placeholder`, `value`, `submitLabel`, `onInput`, `autoFocus` | types L5159-5205 |
| `Select` | yes | yes | no | yes | `key`, `options` (1 or more, unique values), `onSelect` (required), `label`, `value`, `autoFocus` | types L9806-9846 |
| `Svg` | no | yes | yes | yes | `source` (131,072 chars), `alt`, `width?`, `height?`, `isInteractive?` | types L11578-11612 |
| `Client` | yes | yes | no | no | `key`, `module` (string literal path), `props?`, `width?`, `height?`, `flexGrow?` | types L1326-1375 |
| `Raster` | yes | no | no | no | `key`, `columns` 1-512, `rows` 1-256, `cells` (base64) | types L8617-8654 |
| `Image` | yes | no | no | no | `source` (PNG or RGBA base64 up to 2 MiB, or a file or shm name), `columns`/`rows` 1-255, `alt`, `key?` | types L5003-5045 |

Table source: types 2.1.288 L3586-3660 (`Elements`). The docs show only terminal and desktop columns (docs-mods-reference L222-235).

> [!contradiction] Is `Svg` desktop only?
> Docs mark `Svg` desktop only (docs-mods-reference L232; docs-mods-interface L424), and the seed report repeats it. The 2.1.288 typings put `Svg` on every remote surface: desktop, mobile and vscode (types L3588-3592). Typings win; both agree the terminal has none, and a pane that returns only an `Svg` opens empty there (docs-mods-gallery, Svg section). See [[Contradictions Register#API and events]] X2.

## Building a tree in plain TypeScript

```ts
import type { Register } from 'claude-code'

const PANE = 'notes'
let notes: string[] = []

export const register: Register = (on) => {
  on('ui.render', { component: 'Pane' }, async ($, e, next) => {
    if (e.requestId !== PANE) return next(e)
    // Narrow first: unnarrowed, resolve() returns the union of tables and only shared names type-check
    if (e.surface === 'mobile') {
      const { Text } = $.ui.resolve(e)
      return Text({ children: ['Notes need a terminal or desktop.'] })
    }
    const { Box, Text, Button, Input } = $.ui.resolve(e)
    const redraw = () => $.ui.invalidate('ui.render')
    return Box({
      flexDirection: 'column',
      children: [
        Input({
          key: 'new-note', label: 'Note', placeholder: 'Type and press Enter', value: '', submitLabel: 'add', autoFocus: true,
          onSubmit: async (value: string) => {
            if (!value.trim()) return
            notes = [...notes, value.trim()]
            redraw()
            await $.store.set('notes', notes)
          },
        }),
        ...notes.map((note, i) => Box({
          flexDirection: 'row', columnGap: 1,
          children: [
            Button({ key: 'delete-' + i, label: 'x', plain: true, onPress: () => { notes = notes.filter((_, j) => j !== i); redraw() } }),
            Text({ children: [note] }),
          ],
        })),
      ],
    })
  })
}
```

Adapted from docs-mods-interface L553-607. The `e.surface` check matters for types and at run time: `$.ui.resolve(e)` returns exactly one table once `e.surface` is narrowed, and the union otherwise, where only names every table shares type-check (paraphrase, types 2.1.288 L2199-2214). Mobile has no `Input`; at run time a missing element is completed as one that draws a fragment (types L3578-3580), so the plain JavaScript docs example would silently show no field there (see [[Band and Pane Fallback]]). A static check with TypeScript 5.9.3 against the 2.1.288 typings rejects the unnarrowed destructure (TS2339) and accepts the narrowed version above ([[Contradictions Register#API and events]] X9).

## The same tree in JSX

```tsx
// hooks/register.tsx; tsconfig: "jsx": "react", "jsxFactory": "h", "jsxFragmentFactory": "Fragment"
on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
  if (e.props.hasSurvey) return next(e)
  const { Box, Text } = $.ui.resolve(e)
  return <Box flexDirection="row" columnGap={2}><Text bold>build</Text><Text dimColor>green</Text></Box>
})
```

There are no intrinsic string tags; every tag is a constructor from the table (types 2.1.288 L13797-13800). `<>...</>` is a column `Box` (L13793-13796). Children may be strings, numbers, elements, nested arrays, and `false`/`null`/`undefined` (dropped) (L8702-8711). The tsconfig must not include the DOM `lib`, whose `Text` would shadow the element (L84-86).

## Controls, focus and hotkeys

- Callbacks: `Button.onPress(e)` (with `e.surface`), `Input.onSubmit(value)` and `onInput(value)`, `Select.onSelect(value)` (docs-mods-interface L480-486).
- Keyboard reaches controls only while your pane or band has focus, except a digit hotkey on a band button typed into an empty prompt (docs-mods-interface L492; docs-mods-reference L237).
- `hotkey` is one digit or one lowercase letter; two buttons with the same hotkey: the later wins (types 2.1.288 L916, L8744-8748).
- `autoFocus`, and `focus`/`closeOnEscape`/`holdToasts` on `$.ui.open`, accept only `true`; `false` throws (C-API-055).
- Keys while focused: Tab next control, Up/Down move or scroll, Enter press/submit/pick, Esc returns focus to the prompt; a mod cannot rebind Tab or arrows (docs-mods-interface L504-516).
- `action` binds a Claude Code keybinding action's chord to the button (docs-mods-reference L237).
- Terminal shows `[ Add one ]` for a bracketed button and `1: One` with `plain: true` (docs-mods-interface L525-530).

## `Raster`, `Image`, `Client`

Pack `Raster` cells as three 32-bit numbers per cell (code point, foreground, background), `0x01000000` meaning the terminal default; base64 the bytes (docs-mods-interface L436-449). The terminal maps colors to a smaller palette, so `0x2e7d32` draws as `#337733` (docs-mods-gallery, Raster section). Animate with `$.ui.blit({ requestId, key, columns, rows, cells })`, which repaints without re-running the hook, up to 120 a second accepted (C-API-053). `Client` runs a second module of yours for animation and pointer input; it has no `$` and reaches hooks only by posting, which arrives as `ui.message` (docs-mods-interface L425; types L1377-1436).

## Links to local files

A `Link` to `file://...` passes `claude plugin validate` and `tsc` (`href` is typed as `string`) but refuses the whole tree at draw time, so the site falls back to Claude Code's own drawing (types 2.1.288 L5330-5338; C-API-061). To point at a local file, use `Markdown` with a `file:` link, whose links are pressable, or draw the path as `Text`. Found in review of seo-cockpit 0.3.0 (claude-seo), where the pane would have gone blank after its first HTML export.

## Validation

Unknown element, disallowed prop, or a child where none goes: the tree fails as a whole and Claude Code draws its own version (C-API-051). One `Text` string child is capped at 10,000 characters (docs-mods-reference L251).

## Recommendations

- Destructure only the elements you use, and handle `undefined` ones per surface. EVIDENCE-BASED
- Give every control a stable `key`; tests, `ui.press` matchers and `$.ui.focus` all address controls by key. EVIDENCE-BASED
- Name the hotkey in a bracketed button's label, or use `plain: true`, so terminal users see it. EVIDENCE-BASED
- Use one `Raster` instead of a `Box` per cell for grids and sparklines. EVIDENCE-BASED

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- `variant`, `role`, `hover`, `wrap: 'end' | 'middle'` and the mobile and vscode tables are typings-only in 2.1.288 ([[Contradictions Register#API and events]] X7).
- No drawing was rendered in this lane; behavior is from declarations and docs.

## Related

Where trees go: [[Render Sites]]. Reactive redraws: [[State Store and Module Variables]]; throttles in [[Budgets and Limits]]. Setup and tsconfig: [[Mod Anatomy]]. Build flows: [[Build a Pane Flow]], [[Build a Status Band Flow]], [[Band and Pane Fallback]]. Mount and press in tests: [[Testing Kit]]. Common mistakes: [[Pitfalls Playbook]]. Lookup: [[Mods API Cheatsheet]].

## Sources

- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- docs-mods-gallery: https://code.claude.com/docs/en/plugins/mods/gallery (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
