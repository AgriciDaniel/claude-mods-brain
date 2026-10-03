---
type: "deliverable"
title: "Pitfalls Playbook"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/deliverable"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "patterns-and-ideas"
related:
  - "[[Patterns Playbook]]"
  - "[[Holding a Tool Call]]"
  - "[[Band and Pane Fallback]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Classic Hook Bridge]]"
  - "[[Mods API gaps requested in the 91870 thread but not shipped]]"
  - "[[Budgets and Limits]]"
  - "[[State Store and Module Variables]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Plugin Validate]]"
  - "[[Testing Playbook]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code/issues/91870 (capture retrieved 2026-10-03)"
sources:
  - "docs-mods-troubleshoot"
  - "docs-mods-events"
  - "docs-mods-interface"
  - "docs-mods-api"
  - "docs-mods-reference"
  - "docs-mods-overview"
  - "gh-issue-91870"
  - "pa-gh-91870-mined"
  - "types-2-1-288"
  - "docs-mods-admin"
  - "claudedev-getting-started"
---

# Pitfalls Playbook

The failure that matters most in mods is silent: a hook that throws, times out, or returns the wrong shape is skipped and the session carries on as if the mod were not there (docs-mods-troubleshoot). Most pitfalls below are variants of that, plus state that resets when you do not expect it and UI that does not show where you expect it. Each row gives the symptom, the fix, the evidence, and its status on 2.1.288. Thread rows cite #91870 comments as `c<id>` (full URL: `https://github.com/anthropics/claude-code/issues/91870#issuecomment-<id>`).

## Failure semantics

| # | Pitfall | Symptom | Fix | Evidence | Status 2.1.288 |
|---|---|---|---|---|---|
| F1 | Hook throws or runs over 10 s | Hook skipped, guarded call runs | `.catch` returning `{ deny }` | docs-mods-events; c5540419526, c5560997612 | By design |
| F2 | Waiting with `$.clock.sleep` or your own promise | Budget spent, hook skipped, held command runs | Wait inside `$.ui.ask` or other `$` calls | docs-mods-reference Limits | By design |
| F3 | Returning `{}`, `undefined`, `{ text }` or `{ error }` from `tool.call` | Logged as wrong shape, tool runs, model told it succeeded | Return `next(e)`, `{ deny }` or `{ result }` only | c5555855461, c5716583564; docs-mods-reference | By design |
| F4 | `await next(e)` then `return { deny }` | Tool already ran; file on disk; model told it was refused | Decide before `next` | c5546290346 (staff), c5561779552 | By design |
| F5 | Calling `next(e)` twice | Tool runs twice | Only for deliberate retry | docs-mods-events; c5546290346 | By design |
| F6 | Forgetting `await` on a `$` read | Promise is truthy, check never fails | Always await `$` calls | c5533230310 | Unanswered |
| F7 | A `.catch` handler doing slow work | It has only 1 s | Return a fixed `{ deny }` | docs-mods-reference Limits | By design |
| F8 | Blocking the worker (loop that never awaits) | `was unloaded: it crashed the hooks worker` when the crash traces to one mod; after three crashes that cannot be traced to one mod, every mod that is not built in is unloaded, built-ins stay (docs-mods-troubleshoot L136) | Await in loops; move CPU work to `$.process.run` | docs-mods-troubleshoot | By design |

## Loading and validation

| # | Pitfall | Symptom | Fix | Evidence | Status |
|---|---|---|---|---|---|
| L1 | Two matcher-less `on()` for one event | Module fails: `registered twice without a matcher` | One hook per event per matcher | docs-mods-events | By design |
| L2 | Computed access `$[expr]`, spreading `$` | Load refused | Write each call in full, `$.noun.method()` | c5539280904 (staff); docs-mods-reference; docs-mods-admin | By design. Passing `$` to a named helper was refused on 2.1.260 (c5542444779) but 2.1.288 validate traces it (`calls: ... (via run)` in an observed run) |
| L3 | Top-level code throws (e.g. `new RegExp(badOption)`) | `hooks module did not load` | try/catch around option parsing | docs-mods-troubleshoot | By design |
| L4 | `"hooks": "./hooks/hooks.json"` in plugin.json | Whole hook load dropped, only in debug log | Omit the key; hooks.json is found by convention | c5716583564 (2.1.274) | Unverified on 2.1.288 |
| L5 | `validate` passes nonexistent `$` methods and unknown event names | Runtime throw, hook skipped | Type-check against generated typings (`tsc -p .`) | c5559557492, c5583080783 | Acknowledged |
| L6 | `validate --strict .` at a repo root that is also a marketplace | Validates the marketplace only | Validate each plugin directory | c5953998781 (2.1.287) | Unanswered |
| L7 | Missing `modules` key | Validate lists no `hooks` line | `"modules": ["./register.ts"]` | docs-mods-troubleshoot | Documented |
| L8 | `userConfig` value fails its type | `options do not fit plugin.json userConfig` | Fix `pluginConfigs` value | docs-mods-troubleshoot | Documented |
| L9 | Old `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` in instructions | Setting `0` does not disable mods | Remove it; use `/plugin` or `disableAllHooks` | docs-mods-overview | Documented |
| L10 | Gateway (`ANTHROPIC_BASE_URL`) users | Mods off; cached rollout key | Report; check `claude plugin test` message | c5950552972 (2.1.287) | Unanswered |
| L11 | Module linking more than 512 files | Whole module dropped | Bundle | c5774188428; staff c5795711511 "will be removed" | Unverified |

## Commands and names

| # | Pitfall | Symptom | Fix | Evidence | Status |
|---|---|---|---|---|---|
| N1 | Registering a taken command name | Throws; rest of `session.start` hook skipped | Register last, inside try/catch | docs-mods-api | Documented |
| N2 | Expecting your `/diff` to replace the built-in | Built-in answers; no warning | Pick a new name | c5842961190, c5774188428 | Unanswered |
| N3 | Typing a mod command in the first seconds of a session | Built-in answers; `command.run` not dispatched | None; large modules load late | c5774188428 (2.1.278) | Unanswered |
| N4 | `$.prompt.submit('/x')` | Refused | `$.command.run({ command: 'x' })` | c5607792448 (staff) | Workaround |
| N5 | `$.command.register` without `immediate: true` | Command waits for the turn to end | Add `immediate: true` | docs-mods-api | Documented |

## State and reload

| # | Pitfall | Symptom | Fix | Evidence | Status |
|---|---|---|---|---|---|
| S1 | Data in module variables | Lost on every hot reload | `$.state` for drawn values, `$.store` for durable ones | docs-mods-interface | By design |
| S2 | Relying on `session.start` after `/clear`, `/resume`, `/branch` | Stale ids, empty `$.state` | `classic.SessionStart` with `e.source` | docs-mods-troubleshoot | By design |
| S3 | `$.store` get then set from two sessions | Second write wins | One key per item; re-read right before write | docs-mods-interface | By design |
| S4 | Editing an installed copy | Edits ignored | Develop with `--plugin-dir` | docs-mods-troubleshoot; c5670161416 | Documented |
| S5 | Desktop, local marketplace install | Old copy keeps drawing after `/reload-plugins` | Uninstall and reinstall | c5943145826 | Unanswered |
| S6 | Slow `session.end` work | Cut at 1.5 s for all mods together | Prebuild, write once | docs-mods-reference | By design |
| S7 | Reading Claude Code's internal files (session JSON) | Breaks silently on a release | Prefer `$.session.*` or `$.agent.list()`; pin tested-on | observed in personal mods reviewed for this vault | Practitioner |

## Tool calls and permissions

| # | Pitfall | Symptom | Fix | Evidence | Status |
|---|---|---|---|---|---|
| T1 | Rewriting tool input in auto mode | `a hook changed this call's input after the model wrote it` | Deny with instructions, or handle the deny | docs-mods-troubleshoot | By design |
| T2 | Silent rewrites | Model believes it wrote the original text | Add `context` telling Claude what changed | staff c5531157307; c5531286741 | Acknowledged |
| T3 | Answering `tool.call` without `next` | User's `PreToolUse` scripts never run | Answer only to deny | docs-mods-events | By design |
| T4 | Guard matching command text | `$(...)`, aliases, scripts bypass | Permission rules for hard blocks | docs-mods-events; claudedev-getting-started | By design |
| T5 | `tool.check` returning `allow` on a managed machine | `tried to lift a deny rule`; call stays denied | Do not try; admin sets `allowModsToOverrideDenyRules` | docs-mods-troubleshoot | Documented |
| T6 | Registered tools and subagents with a `tools:` allowlist | Tool never offered | None known | c5848066352 (2.1.283) | Unanswered |
| T7 | Reading `result` fields in a subagent's `tool.call` | `result` undefined, hook throws, skipped | Guard with optional chaining | c5739299765; staff c5739358814 | Acknowledged |
| T8 | `tool.call` hooks in isolated-worktree subagents | Lost isolation, wrong cwd | No verified fix; test worktree isolation with your `tool.call` hooks on your build before relying on it | c5949411806; staff c5961758416 | Reportedly fixed in 2.1.288 (staff: should be fixed), unverified |

## Drawing

| # | Pitfall | Symptom | Fix | Evidence | Status |
|---|---|---|---|---|---|
| D1 | Invalid tree | Claude Code draws its own content; message only with `--plugin-dir` or debug | Read `ui.render (...) refused:` | docs-mods-troubleshoot | Documented |
| D2 | `focus: false`, `closeOnEscape: false`, `holdToasts: false`, `autoFocus: false` | Throws | Omit the prop | docs-mods-interface, docs-mods-reference | Documented |
| D3 | Self-opened pane in a narrow terminal | Nothing shows | Check `isPlaced`; fall back to the band | docs-mods-interface | Documented |
| D4 | Band tree without `await next(e)` | Hides other mods' bands | Compose | docs-mods-interface | Documented |
| D5 | Ignoring `hasSurvey` | Survey hidden | Return `next(e)` | claudedev-getting-started | By design |
| D6 | Terminal-only sites or elements on Desktop | Missing drawing | Check render sites table | docs-mods-reference | Documented |
| D7 | Redrawing an `Input` from keystroke state | IME composition cancelled (Desktop) | Do not redraw on each keystroke | c5945622881 | Unanswered |
| D8 | `$.ui.invalidate('ui.render')` | Re-runs other plugins' visible panes too | Invalidate only on change | c5855273487 | Unanswered |
| D9 | Emoji in bands | Columns misalign | Single-width glyphs | claudedev-getting-started | Practitioner |

## Cost and cache

| # | Pitfall | Fix | Evidence |
|---|---|---|---|
| C1 | Volatile `prompt.section`, `prompt.context`, `tool.describe`, `skill.prompt` text | Keep stable; volatile facts in `prompt.submit` `context` | docs-mods-events; types 2.1.288 L3899-3952 |
| C2 | `$.model.classify` and `$.model.fork` missing from audits | Add both next to `complete` | docs-mods-admin; [[How is $.model.classify billed]] |
| C3 | Summing `turn.complete` usage for context size | Use `$.session.usage().context.tokens` | c5715941633 |
| C4 | `$.prompt.submit` from a command or timer | Starts a full turn on the user's usage | docs-mods-api |

## Recommendations

- Attach `.catch` to every guard and default every hold to refuse. EVIDENCE-BASED
- Run `tsc -p .` against the generated typings in CI, because validate does not check method existence. PRACTITIONER
- Keep state you draw in `$.state` and re-seed it in `classic.SessionStart`. EVIDENCE-BASED
- Develop with `--plugin-dir` and `--debug-file`, so skipped hooks are visible. EVIDENCE-BASED
- Re-check every "Unanswered" row after each release. PRACTITIONER

## Caveats

- Thread rows come from pre-release builds (2.1.259 to 2.1.287) unless marked; several may already be fixed.
- No pitfall was reproduced live by this lane; docs rows are evidence-based, thread rows are practitioner unless staff confirmed.

## Related

The positive counterparts are in [[Patterns Playbook]]; deep dives in [[Holding a Tool Call]], [[Band and Pane Fallback]], [[Prompt Cache Discipline]], and [[Classic Hook Bridge]]. Missing APIs behind some rows are in [[Mods API gaps requested in the 91870 thread but not shipped]]. Limits are in [[Budgets and Limits]], state lifetimes in [[State Store and Module Variables]], the dev loop in [[Hot Reload and Dev Loop]], and checks in [[Plugin Validate]] and [[Testing Playbook]].

## Sources

- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (capture retrieved 2026-10-03)
- pa-gh-91870-mined: `.raw/captures/lanes-2026-10-03/patterns-and-ideas/gh-issue-91870-mined.md`
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
