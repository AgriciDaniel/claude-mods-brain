---
type: "concept"
title: "userConfig and Plugin Options"
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
lane: "lifecycle"
related:
  - "[[Mod Anatomy]]"
  - "[[Testing Kit]]"
  - "[[Plugin Validate]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Versioning and API Drift]]"
  - "[[Agent and Command Events]]"
  - "[[Org Mod Controls]]"
  - "[[Does claude plugin test support userConfig values yet]]"
  - "[[code-modernization Plugin]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/manifest-reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
sources:
  - "docs-plugins-manifest-reference"
  - "docs-mods-reference"
  - "docs-mods-troubleshoot"
  - "types-2-1-288"
  - "lif-plugin-authoring-skill"
  - "code-modernization-1-0-0"
  - "gh-issue-91870"
---

# userConfig and Plugin Options

A mod is configured through the ordinary plugin `userConfig` block in `plugin.json`, and its hooks module receives the resolved values as the second argument of `register(on, options)`, defaults filled in (C-LIF-039). Values live in the user's settings under `pluginConfigs`, sensitive ones in secure storage; each non-secret field becomes a `/config` row, and changing one reloads the module with a new `options` object (C-LIF-040). A value that fails validation stops the module loading, with a message naming the field and its settings entry.

## Declaring fields

`userConfig` keys are identifiers (letters, digits, underscores, not starting with a digit). Each field is a strict object: an unknown key fails validation and the plugin does not load (C-LIF-037, docs-plugins-manifest-reference).

| Field | Required | Notes |
|---|---|---|
| `type` | Yes | `string`, `number`, `boolean`, `directory`, `file` |
| `title` | Yes | Label in the configuration dialog and `/config` |
| `description` | Yes | Help text |
| `required` | No | Dialog refuses an empty value; a missing required value fails the load |
| `default` | No | string, number, boolean, or array of strings |
| `options` | No | `string` only, not `multiple` or `sensitive`; fixed picker; needs v2.1.271+ (C-LIF-038) |
| `multiple` | No | `string` holds an array of strings |
| `sensitive` | No | Masked, kept in secure storage, not a `/config` row |
| `min` / `max` | No | Bounds for `number` |

Anthropic's code-modernization 1.0.0 is a realistic model: seven fields, three of them `string` with `options` (`track`: auto, transform, uplift, reimagine; `panel`: auto, command, off), two `boolean` toggles, and free strings with defaults (code-modernization-1-0-0 `.claude-plugin/plugin.json`).

```json
{
  "name": "turn-band",
  "version": "0.2.0",
  "description": "Shows the last turn's time and tool count above the prompt",
  "types": "./types/index.d.ts",
  "userConfig": {
    "toastAfterSeconds": {
      "type": "number", "title": "Toast after (seconds)",
      "description": "Show a toast when a turn takes longer than this.",
      "default": 120, "min": 10, "max": 3600
    },
    "style": {
      "type": "string", "title": "Band style",
      "description": "How much the band shows.",
      "options": ["compact", "full"], "default": "compact"
    }
  }
}
```

## Reading options in the module

`PluginOptions` is `Readonly<Record<string, string | number | boolean | readonly string[]>>` (types 2.1.288 L7197), so narrow each value before use. The options are fixed for one activation: a change reloads the plugin and `register` runs again (types 2.1.288 L8662-8673).

```ts
import type { Register } from 'claude-code'

export const register: Register = (on, options) => {
  const limit = typeof options.toastAfterSeconds === 'number' ? options.toastAfterSeconds : 120
  const isFull = options.style === 'full'

  on('turn.complete', async ($, e, next) => {
    if (e.durationMs / 1000 > limit) $.ui.toast(`${$.plugin.name}: turn took ${Math.round(e.durationMs / 1000)}s`)
    return next(e)
  })
  // isFull would select the band layout in a ui.render hook
  void isFull
}
```

Hooks close over the `options` object, so there is no need to read settings with `$.settings.read` for your own fields.

## Where values are stored and keyed

| Item | Location |
|---|---|
| Non-sensitive values | `pluginConfigs[<plugin id>].options` in the user's `settings.json` (types 2.1.288 L7185-7197) |
| Sensitive values | Platform secure credential store |
| Key for an installed plugin | Plugin id, such as `acme-guard@acme-tools` (docs-mods-reference) |
| Key for `--plugin-dir` | `<name>` or `<name>@inline`, such as `first-mod@inline` |
| Managed values | `pluginConfigs` is also read from managed settings (docs-mods-reference) |

A string field with `options` treats a stored value outside the list as unset, so its `default` applies (lif-plugin-authoring-skill).

## Failure: options that do not fit

When a stored value breaks the declared type or bounds, or a required field has none, the module does not load. The line reads `<mod>: hooks module did not load: options do not fit plugin.json userConfig:` followed by the reason, and its end names the `pluginConfigs` entry to fix (C-LIF-039, docs-mods-troubleshoot). The rest of the plugin (skills, commands) can still load; only the hooks module is refused.

## Options and other components

`userConfig` predates mods, and other components read the same values differently (docs-plugins-manifest-reference):

- `${user_config.KEY}` substitutes in MCP and LSP configs, exec-form hook `args`, and skill and agent text (sensitive values become placeholders there).
- `CLAUDE_PLUGIN_OPTION_<KEY>` is exported to settings-hook processes.
- Shell-form hook commands, monitor commands and `headersHelper` reject `${user_config.*}`.

A mod that also ships classic hooks (as code-modernization does in `hooks/hooks.json`) therefore reaches the same option two ways: `options` in `register`, and the environment variable in its shell hooks.

## Testing with options

On 2.1.288 the typings let a test pass values: `test(name, { options: { style: 'full' } }, body)`, read as if stored in settings, with defaults filled and validation applied; left out, the manifest defaults apply (C-LIF-029).

```ts
import { expect, mock, test } from 'claude-code/testing'

test('a short limit toasts', { options: { toastAfterSeconds: 10 } }, async ($, on) => {
  mock.clock(on)
  const toasts: string[] = []
  on('ui.toast', ($, e) => { toasts.push(e.text); return { value: undefined } })
  on('turn.complete', () => ({ text: '' }))
  await $.turn.complete({ turnId: 't1', answer: 'ok', durationMs: 30_000, isAborted: false, reason: 'answer' })
  expect(toasts).toEqual(['turn-band: turn took 30s'])
})
```

> [!contradiction]
> lperezmo on #91870 (2.1.282, comment 5827373997) reports `claude plugin test` cannot set userConfig values. The 2.1.288 typings (L14924-14945) and the bundled skill say a test passes them through `options`. The typings win for 2.1.288; the snippet above is written to them and was not executed by this lane (X-LIF-01).

## Recommendations

- Give every field a `default`, so the mod loads before the user configures anything and tests without `options` exercise real defaults. EVIDENCE-BASED
- Use `options` pickers for modes, but only if every target user runs v2.1.271 or later, since declaring `options` blocks older clients from loading the plugin. EVIDENCE-BASED
- Narrow each `options.<key>` with `typeof` in `register`; the type admits four value shapes. EVIDENCE-BASED
- Prefer `/config` over the `/plugin` configure screen for `boolean` fields until the reported text-box bug is confirmed fixed (C-LIF-041). PRACTITIONER
- Never put a credential in a non-sensitive field; mark it `sensitive` and avoid surfacing it in skill text. EVIDENCE-BASED

## Caveats

- The `/plugin` boolean text-box issue is single-source on 2.1.282 (C-LIF-041); not re-tested.
- How managed `pluginConfigs` and user values merge for one field was not found in the captured pages.
- `validate` reported no inventory note for a mod's `userConfig` in the observed run on 2.1.288; it validates fields but does not list them.

## Related

The manifest and module layout is in [[Mod Anatomy]]; validation of the block is in [[Plugin Validate]]. Changing an option reloads the module as described in [[Hot Reload and Dev Loop]]. Tests pass values through the [[Testing Kit]], and whether that works is tracked in [[Does claude plugin test support userConfig values yet]]. The `options` picker's minimum version is a drift concern in [[Versioning and API Drift]]. Commands often read options, see [[Agent and Command Events]]. Organizations can manage values through [[Org Mod Controls]]. A real example is [[code-modernization Plugin]].

## Sources

- docs-plugins-manifest-reference: https://code.claude.com/docs/en/plugins/manifest-reference (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` L7185-7197, L8662-8673, L14924-14945 (retrieved 2026-10-03)
- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/.claude-plugin/plugin.json` (retrieved 2026-10-03)
- lif-plugin-authoring-skill: `.raw/captures/lanes-2026-10-03/lifecycle/plugin-authoring-skill-2-1-288.md` (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870#issuecomment-5827373997 (retrieved 2026-10-03)
