---
type: "entity"
title: "Built-in agents-md Mod"
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
  - "[[Prompt Events]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Agent and Command Events]]"
  - "[[Tool Events]]"
  - "[[Built-in telemetry Mod]]"
  - "[[Org Mod Controls]]"
  - "[[Hook Ordering and Tiers]]"
source_urls:
  - "https://github.com/anthropics/claude-code/tree/main/mods/agents-md (retrieved 2026-10-03, pinned 1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528)"
  - "https://code.claude.com/docs/en/memory (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
sources:
  - "eco-gh-anthropics-mods"
  - "eco-docs-memory"
  - "docs-mods-overview"
  - "eco-static-scan"
---

# Built-in agents-md Mod

Claude Code reads `AGENTS.md` through a built-in mod, `cc-plugin-agents-md`, configured by one option, `instructionFiles` (C-ECO-006). It is the reference for a mod that edits the instruction files the engine renders, via `prompt.context`, without touching the system prompt text itself. It runs in every session that can read `AGENTS.md` and is not stopped by `disableAllHooks`, `--bare` or `--safe-mode` (C-ECO-019).

## Identity and pin

| Field | Value |
|---|---|
| Repo path | `anthropics/claude-code/mods/agents-md` |
| Pinned commit | `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528` (2026-10-02) |
| Manifest | `name: "agents-md"`, `version: "0.1.0"`, one `userConfig` key |
| Module | `./register.ts` plus folders `files/`, `frames/`, `modes/`, `names/`, `switches/`, `telemetry/` |
| Name in `/plugin` | `cc-plugin-agents-md` |
| Minimum version | Reading `AGENTS.md` directly needs v2.1.277+ (C-ECO-009) |
| Code reviewed | static read of `register.ts`, README, `plugin.json`, `hooks.json` |

## The option

| `instructionFiles` | Effect |
|---|---|
| `claude-md` | Engine's CLAUDE.md walk alone; the mod adds nothing beyond a usage row |
| `claude-md-or-agents-md` (default) | If no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` exists from root to cwd, every `AGENTS.md` and `.claude/AGENTS.md` on that path joins the instruction files |
| `claude-md-and-agents-md` | `AGENTS.md` loads beside `CLAUDE.md`; a file CLAUDE.md already imports or links to is not loaded twice |
| `managed-only` | Project and personal instruction files are dropped; managed files and memory stay |

Set it in `/config` ("Project instructions") or in settings:

```json
{
  "pluginConfigs": {
    "agents-md@builtin": {
      "options": { "instructionFiles": "claude-md-and-agents-md" }
    }
  }
}
```

The key is `agents-md@builtin` per both the mod README and the memory docs (C-ECO-006). A project's `.claude/settings.json` is not read for plugin options (eco-gh-anthropics-mods, README). A legacy `projectInstructions` key is still honoured for now and logs a one-time rename notice (C-ECO-008).

Note the asymmetry with the guard: sec-default options are read only under `cc-plugin-sec-default@builtin` (C-ECO-011), while agents-md uses `agents-md@builtin`. Copy the id from each mod's own docs.

## Events and calls

| Event | Matcher | Purpose |
|---|---|---|
| `session.start` | none | Logs a usage row through `$.telemetry`; prints the legacy-key notice once |
| `prompt.context` | `{ instructionFiles: { kind: DROPPED_KINDS } }` in managed-only, none otherwise | Filters or extends `e.instructionFiles` and calls `next({...e, instructionFiles})` |
| `agent.spawn` | `{ fork: true }` | Copies the parent's already-sent nested files to the fork |
| `tool.call` | `{ tool: 'Read' }` | After a successful Read, attaches nested `AGENTS.md` files as `context` frames |

Calls: `$.fs.ancestors` (the walk), `$.session.root`, `$.session.cwd`, `$.env.get` (`CLAUDE_CODE_SIMPLE`, `CLAUDE_CODE_DISABLE_ATTACHMENTS`, `HOME`, `USERPROFILE`), `$.telemetry.log`, `$.telemetry.mark`, `$.ui.log` (C-ECO-007). Reach L1 (reads files and env); scanner agrees (eco-gh-awesome-claude-code-mods). Usage cost: the added files enlarge the prompt, which is the point.

## Patterns worth copying

- **Answer the list, not the text.** The engine renders `claudeMd` from the files a `prompt.context` hook hands back, with its own framing and omission rules, so an added file behaves exactly like a project CLAUDE.md (eco-gh-anthropics-mods README). Prefer this over string-editing `prompt.section`.
- **Post-call attachment.** On `Read`, it awaits `next(e)`, skips denied or errored results, then returns `{ ...result, context: [...] }`.
- **Respect run switches at call time.** It re-reads `CLAUDE_CODE_SIMPLE` and `CLAUDE_CODE_DISABLE_ATTACHMENTS` on every Read because a settings `env` block can flip mid-session.
- **Fail soft.** A failed walk yields an empty list, and telemetry calls are wrapped so a missing `$.telemetry` never breaks the hook.

## Recommendations

- Leave the default unless a repo has both files; then pick `claude-md-and-agents-md` explicitly. EVIDENCE-BASED
- Do not add `CLAUDE.local.md` to an AGENTS.md-only repo under the default mode; it switches AGENTS.md off for you (eco-docs-memory). EVIDENCE-BASED
- When writing a mod that changes instruction files, copy the `prompt.context` shape here instead of rewriting `prompt.section`; it keeps the cached prefix stable when your list is stable. PRACTITIONER
- Organizations that need only managed instructions can set `managed-only` in managed settings. EVIDENCE-BASED

## Caveats

- `managed-only` does not stop the engine's own nested `CLAUDE.md` attachments on `Read`, which the README says are not an event yet.
- Source pinned at 1c229fc; the shipped binary may differ by a day. Behaviour on the stable channel (2.1.285) was not checked.
- The `projectInstructions` fallback is marked `COMPAT_BREAK` in source and will be removed.

## Related

- [[Mod Catalog]] row and verdict.
- [[Prompt Events]] for `prompt.context` semantics; [[Prompt Cache Discipline]] for why list stability matters.
- [[userConfig and Plugin Options]] for `pluginConfigs` mechanics.
- [[Agent and Command Events]] and [[Tool Events]] for the `agent.spawn` and `tool.call` matchers.
- [[Built-in telemetry Mod]] provides the usage rows.
- [[Org Mod Controls]] and [[Hook Ordering and Tiers]]: a prepended org plugin on `prompt.context` sits above this one.

## Sources

- eco-gh-anthropics-mods: https://github.com/anthropics/claude-code/tree/main/mods/agents-md (retrieved 2026-10-03, pinned 1c229fc)
- eco-docs-memory: https://code.claude.com/docs/en/memory (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
