---
type: "concept"
title: "Plugin Validate"
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
  - "[[Testing Kit]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Mod Anatomy]]"
  - "[[Mods API Namespaces]]"
  - "[[State Store and Module Variables]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Publish a Mod Flow]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Reach Levels]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/manifest-reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/marketplace-reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/create-marketplace (retrieved 2026-10-03)"
sources:
  - "docs-mods-create"
  - "docs-plugins-manifest-reference"
  - "docs-plugins-marketplace-reference"
  - "docs-plugins-create-marketplace"
  - "a local `claude plugin validate --json` run"
  - "lif-plugin-authoring-skill"
  - "claudedev-getting-started"
---

# Plugin Validate

`claude plugin validate <path>` reads a plugin's manifest and runs the same static analysis on the hooks module's source that Claude Code runs when it loads a mod, without executing any code or starting a session (C-LIF-014). It prints what the module hooks, which `$` methods it calls, which environment variables and `$.state` keys it touches, and every error the engine would refuse at load. It is the cheapest check in the lifecycle, so run it after every edit, in CI with `--strict --json`, and on any third-party mod before you load it.

## What it reads and reports

On a plugin folder, validate checks `plugin.json`, then each component file, including `hooks/hooks.json` and the module it names (C-LIF-014, C-LIF-015). For a mod the text output ends with an inventory, as in the docs tutorial:

```text
  ❯ ./register.js hooks: session.start, tool.call, command.run{command=tally}, ui.render{component=Spinner}
  ❯ ./register.js calls: $.command.register, $.ui.invalidate

✔ Validation passed
```

A module that uses state or the environment gets more lines. The claude.dev Token Weather example shows the full set (claudedev-getting-started):

| Line | Meaning |
|---|---|
| `types ./types/index.d.ts declares state: <plugin>.<key>` | The `$.state` contract the manifest names |
| `<module> hooks: ...` | Every `on(...)` with its matcher in braces |
| `<module> calls: ...` | Every `$.noun.verb`, with `(via helper)` when `$` was passed to a top-level function |
| `<module> env reads:` / `env writes:` | `$.env.get` / `$.env.set` names |
| `<module> state reads:` / `state writes:` | `$.state` keys read and written |

On a marketplace root (or the `marketplace.json` file) it validates the catalog instead: JSON syntax, required `name`/`owner`/`plugins`, entry names, `..` in sources, unknown fields as warnings, and each relative-path plugin's own `plugin.json` as `plugins[N] plugin.json → <field>: <message>` (docs-plugins-create-marketplace).

## Flags and exit codes on 2.1.288

Observed with `claude plugin validate --help` on 2.1.288 (C-LIF-016): only `--json` ("Output the validation report as JSON (same exit codes)") and `--strict` ("Treat warnings as errors (exit 1)").

| Result line | Exit | When |
|---|---|---|
| `Validation passed` | 0 | Loads cleanly |
| `Validation passed with warnings` | 0, or 1 under `--strict` | Unknown top-level field, non-kebab name, missing `version`/`description`/`author`, whole-word `claude` in a name |
| `Validation failed` | 1 | Type mismatch, missing or escaping path, unknown key inside `userConfig`/`channels`/`lspServers`/`monitors`, static-analysis errors |

Sources: C-LIF-020, docs-plugins-manifest-reference.

## The JSON report shape

Observed on 2.1.288 against a local mod (C-LIF-015, home paths redacted):

```json
{
  "success": true,
  "strict": false,
  "target": "<mod>/.claude-plugin/plugin.json",
  "manifest": { "file": "<mod>/.claude-plugin/plugin.json", "type": "plugin",
                "errors": [], "warnings": [], "notes": [] },
  "contents": [
    { "file": "<mod>/hooks/hooks.json", "type": "hooks", "errors": [], "warnings": [],
      "notes": [
        "./register.ts hooks: tool.call{tool=Write|Edit}, tool.call{tool=NotebookEdit}, tool.call{tool=Bash}, tool.call{tool=SendMessage}",
        "./register.ts calls: $.ui.log"
      ] }
  ]
}
```

The inventory is not structured: it arrives as strings in `contents[].notes`. A CI job or an audit script parses those strings:

```bash
claude plugin validate --strict --json ./my-mod > validate.json
jq -e '.success' validate.json >/dev/null || { jq '.manifest.errors, .contents[].errors' validate.json; exit 1; }
jq -r '.contents[].notes[]' validate.json | grep -E ' (hooks|calls|env reads|env writes|state reads|state writes):'
```

## Static analysis rules the module must follow

The inventory is only complete if the source is written so the analyzer can read it (C-LIF-017, docs-mods-create):

| Rule | Error when broken |
|---|---|
| Write each call in full: `$.store.get(...)` | `$.ui is used as a value` for `const ui = $.ui` |
| Pass `$` only to functions declared at the top level of the same file (or the `read`/`update` state helpers) | Fails validation for methods, inner functions, imported helpers |
| Event names are string literals | `the event name passed to on() is not a string literal` |
| No second `on` inside `register` | `"on" is declared again (shadowed)` |
| Import only plugin-relative files and `claude-code` | Fails validation (exact message not captured) |
| No dynamic `import()` | `a dynamic import(); a hooks module imports its own files with an import declaration` |
| Real event names | `"tool.calls" is not an event` |
| Every `$.state` key declared in the `types` contract | `<plugin>.<key> is not declared` (C-LIF-018) |
| A `telemetry.*` hook in an installed mod has `{ to: 'collector' }` | Fails validate (docs-mods-reference) |

## Name checks

validate is one of only three commands (with `plugin init` and `plugin tag`) that check whether a plugin name passes as Anthropic's own (C-LIF-019): an error for names starting `claude-`, `anthropic-`, `anthropics-`, `cc-plugin-`, or equal to `claude`, `claude-code`, `claude-mods` and kin, a warning for `claude` as a whole word elsewhere. Install and load still accept such names, so the check is advisory for users but blocking for a clean `--strict` release.

## What validate does not catch

- A relative marketplace `source` to a directory that does not exist: passes, then install fails with `Source path does not exist` (C-LIF-021).
- Fetch errors for `github`, `git-subdir`, `url`, `archive` sources, and an entry `hooks` written as a path (C-LIF-021).
- An exact reserved official marketplace name: refused only at `marketplace add` (C-LIF-021).
- Runtime behavior: a hook that throws, exceeds 10 s, or returns a wrong shape; a tree a surface refuses. Those need [[Testing Kit]] tests or a debug-log session.
- What a hook does with `next()`: a mod can rewrite events with zero `$` calls, so an empty `calls:` line is not proof of harmlessness (see [[Audit a Third-Party Mod Flow]]).

## Recommendations

- Run validate after every save during development; an event missing from `hooks:` means the engine will not call that hook either. EVIDENCE-BASED
- Gate CI and releases on `claude plugin validate --strict --json`, and fail on non-empty `errors` arrays. EVIDENCE-BASED
- Record the `hooks:`, `calls:`, `env` and `state` lines in the README or audit record; they are the mod's declared reach (see [[Reach Levels]]). PRACTITIONER
- Diff the inventory lines between releases of a third-party mod before updating it. PRACTITIONER
- If you omit `version` to track git SHAs, drop `--strict` or accept the missing-version warning, as the publish docs advise. EVIDENCE-BASED

## Caveats

- The JSON shape was observed on one passing mod on 2.1.288; the shape of a failing report (error record fields) was not observed and may differ.
- Field-level docs of the JSON format were not found in the captured pages; treat key names as observed, not contracted.
- validate inspects source statically; it cannot see behavior hidden behind data (a URL from `$.store`, a command string from config).

## Related

validate is the first gate of the [[Hot Reload and Dev Loop]] and of [[Testing Playbook]], followed by the [[Testing Kit]]. Its inventory maps to [[Mods API Namespaces]] and the declared state contract in [[State Store and Module Variables]]; the files it reads are described in [[Mod Anatomy]]. Security reviews use it in [[Audit a Third-Party Mod Flow]] and [[Mod Security Audit Checklist]], scored by [[Reach Levels]]. Release work uses `--strict` in [[Publish a Mod Flow]] and after an update in [[Re-verify After Release Flow]].

## Sources

- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- docs-plugins-manifest-reference: https://code.claude.com/docs/en/plugins/manifest-reference (retrieved 2026-10-03)
- docs-plugins-marketplace-reference: https://code.claude.com/docs/en/plugins/marketplace-reference (retrieved 2026-10-03)
- docs-plugins-create-marketplace: https://code.claude.com/docs/en/plugins/create-marketplace (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- A local `claude plugin validate --json` run on Claude Code 2.1.288 (retrieved 2026-10-03; output not redistributed)
- lif-plugin-authoring-skill: `.raw/captures/lanes-2026-10-03/lifecycle/plugin-authoring-skill-2-1-288.md` (retrieved 2026-10-03)
