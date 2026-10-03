---
type: "flow"
title: "Migrate a Classic Hook Flow"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/flow"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "patterns-and-ideas"
related:
  - "[[Mods vs Classic Hooks]]"
  - "[[Classic Hook Bridge]]"
  - "[[Holding a Tool Call]]"
  - "[[Build a Tool Call Guard Flow]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Testing Kit]]"
  - "[[Plugin Validate]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Pitfalls Playbook]]"
  - "[[Re-verify After Release Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-reference"
  - "docs-mods-test"
  - "docs-mods-troubleshoot"
  - "docs-hooks"
  - "docs-hooks-guide"
  - "types-2-1-288"
  - "compass-report"
---

# Migrate a Classic Hook Flow

Port a settings hook (a `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, or `SessionStart` script) to a mod in two phases: first wrap it with a pass-through `classic.<Event>` hook so nothing changes, then move the logic to the native event and delete the script. Migrate only when the mod adds something the script cannot do (state, UI, deterministic ordering, a no-turn command); otherwise keep the script (docs-mods-overview compare table). This flow is the procedural companion to [[Mods vs Classic Hooks]].

## Trigger

- A settings hook needs state across events, a UI, or a slash command.
- Several `PreToolUse` hooks rewrite the same tool's input and race, since the last `updatedInput` to finish wins (docs-hooks-guide L963).
- A shell hook's per-event process cost shows up on every tool call.

## Prerequisites

- Claude Code 2.1.287 or later (`claude --version`); this flow was checked against 2.1.288 docs and typings.
- The script's source, its `settings.json` entry (matcher, `if`, timeout), and the event's stdin fields from docs-hooks.
- A plugin folder with `.claude-plugin/plugin.json` and `hooks/hooks.json` holding `"modules": ["./register.ts"]` (docs-mods-reference Files).
- Generated typings: load once with `--plugin-dir` so `.claude-plugin/types/` is written, then type `register` with `Register` from `claude-code`.

## Steps

1. **Inventory the script's decisions.** For each output, note the classic field: exit 2, `permissionDecision`, `updatedInput`, `additionalContext`, `decision: "block"`, `continue: false` (docs-hooks decision table).
2. **Map each to a native event** using this table (docs-mods-events, docs-mods-reference, types 2.1.288 L1103-1215):

| Classic | Native mod event | Native result | Notes |
|---|---|---|---|
| `PreToolUse` deny or exit 2 | `tool.call` before `next` | `{ deny: reason }` | Also skips non-managed `PreToolUse` scripts |
| `PreToolUse` `updatedInput` | `tool.call` | `next({ ...e, field })` | Trips auto mode's changed-input check |
| `PreToolUse` `allow` or `ask` | `tool.check` | `{ decision }` | Runs after rules and settings hooks |
| `PostToolUse` log | `tool.call` after `await next(e)` | return result unchanged | Check `result.deny` and `result.isError` |
| `PostToolUse` `updatedToolOutput` | `tool.call` after `next` | return a modified copy of the result | |
| `UserPromptSubmit` `additionalContext` | `prompt.submit` | `next({ ...e, context: [...] })` | |
| `UserPromptSubmit` block | `prompt.submit` | `{ drop: reason }` | |
| `Stop` observe | `turn.complete` | `next(e)` or `{ text }` | Cannot re-prompt |
| `Stop` block (keep going) | `classic.Stop` | `{ block: reason }` | No native equivalent |
| `SessionStart` startup | `session.start` | `next(e)` | Not after `/clear`, `/resume`, `/branch` |
| `SessionStart` clear, resume, compact | `classic.SessionStart` | `next(e)` | Branch on `e.source` |
| `SessionEnd` | `session.end` | `next(e)` | 1.5 s total for all hooks |
| `PreCompact` | `session.compact` | `{ skip }` or `next({ ...e, instructions })` | |
| `SubagentStart` model choice | `agent.spawn` | `{ model }` or `{ deny }` | |

3. **Phase one, wrap.** Register a pass-through on `classic.<Event>` that only logs to debug and returns `next(e)`. Leave the script in place. Load with `claude --plugin-dir ./my-mod --debug-file ./mod.log` and confirm the debug line `hooks module ... loaded ... events:` lists the event (docs-mods-troubleshoot).
4. **Phase two, port.** Write the native hook. For any guard, set the safe answer first and attach `.catch` returning `{ deny }` (docs-mods-events). Put slow work after `next` or on a `$.clock.every` timer, never before it.
5. **Write tests.** Fire the native event or `$.classic.<Event>(fields)` from `claude-code/testing`; stub `$` calls with `on(...)` (docs-mods-test). Pass `userConfig` values with `test(name, { options }, body)` (types 2.1.288 TestOptions).
6. **Validate.** `claude plugin validate --strict ./my-mod` and read the `hooks:` and `calls:` lines (docs-mods-troubleshoot).
7. **Switch over.** Remove the script's entry from `settings.json` in the same change that installs the mod, so both never fire for the same decision.
8. **Record** the tested-on version in the mod's README.

## Outputs

- A mod with one native hook per former script, plus `classic.` hooks only where no native event exists.
- Tests covering allow, deny, and the failure path.
- A settings diff removing the migrated entries.

## Gates

- `validate --strict` passes, and its `hooks:` line names every intended event. EVIDENCE-BASED
- `claude plugin test` passes, including a test where the guard throws and the `.catch` denies. EVIDENCE-BASED
- In a scratch session, the debug log shows no `hook skipped` line for the new hooks. EVIDENCE-BASED
- For a guard that used to be managed: do not migrate it to a user mod. Managed `PreToolUse` blocks are final and run before every mod; a user mod is weaker (docs-mods-events). EVIDENCE-BASED

## Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Guard lets calls through | Hook threw or ran over 10 s and was skipped | `.catch` returning `{ deny }`; keep waits inside `$` calls |
| User's other `PreToolUse` scripts stopped running | The mod answered `tool.call` without `next` | Answer only when denying; pass through otherwise |
| Auto mode denies calls with `a hook changed this call's input` | `tool.call` rewrote input after the classifier reviewed it | Deny with instructions instead of rewriting, or handle the deny inside the hook |
| State lost after `/clear` | Logic lived in `session.start` | Move it to `classic.SessionStart` with `e.source` |
| Module fails to load | Two matcher-less `on()` calls for the same event, or top-level code threw | One hook per event per matcher; guard `new RegExp(option)` with try |
| Double action during switchover | Script and mod both active | Remove the settings entry in the same change |

## Rollback

Disable the plugin in `/plugin` or uninstall it, and restore the removed `settings.json` hook entries from version control. Because phase one kept the script running with a pass-through mod, rolling back from phase one needs only the plugin disable. `"disableAllHooks": true` in user settings stops installed mods and settings hooks together and is the emergency stop, though it does not stop built-in or managed mods (docs-mods-overview).

## Caveats

- Mapping table synthesised from docs and typings on 2.1.288; not executed by this lane.
- The seed report's mapping (compass-report L147-155) maps `Stop` to `turn.complete` only; that loses the block-to-continue behaviour, so this flow adds `classic.Stop` for it.
- Whether a mod `classic.Stop` block counts toward the 8-continuation cap is undocumented.

## Related

Background is in [[Mods vs Classic Hooks]] and [[Classic Hook Bridge]]. Guard specifics are in [[Holding a Tool Call]] and [[Build a Tool Call Guard Flow]]. The dev loop is [[Hot Reload and Dev Loop]]; checks are [[Testing Kit]] and [[Plugin Validate]]; chain position is [[Hook Ordering and Tiers]]. Known traps are in [[Pitfalls Playbook]], and the post-release recheck is [[Re-verify After Release Flow]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-test: https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-hooks: https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)
- docs-hooks-guide: https://code.claude.com/docs/en/hooks-guide (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (secondary, lead list only)
