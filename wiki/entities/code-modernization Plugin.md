---
type: "entity"
title: "code-modernization Plugin"
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
  - "[[Classic Hook Bridge]]"
  - "[[Mods vs Classic Hooks]]"
  - "[[Build a Pane Flow]]"
  - "[[Usage Cost Surface]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Prompt Events]]"
  - "[[Marketplaces and Distribution]]"
  - "[[Testing Kit]]"
source_urls:
  - "https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-modernization (retrieved 2026-10-03, repo pinned d182ca456ca09d31d139f7d3818d1d333b103cce)"
sources:
  - "code-modernization-1-0-0"
  - "eco-gh-code-modernization-upstream"
  - "eco-static-scan"
  - "types-2-1-288"
---

# code-modernization Plugin

code-modernization 1.0.0 is Anthropic's legacy-modernization plugin in the official marketplace (`claude-plugins-official`). It is mostly commands, agents and Python scripts; its mod part is an optional, early-access live progress pane (estate map, rule review deck, sign-off dialog, fleet view) in `hooks/register.ts` (code-modernization-1-0-0). For this vault it matters as the only official plugin that ships classic shell hooks and a mods module in the same `hooks/hooks.json` (C-ECO-024).

## Identity and pin

| Field | Value |
|---|---|
| Upstream | `anthropics/claude-plugins-official/plugins/code-modernization` |
| Upstream pin | repo HEAD `d182ca456ca09d31d139f7d3818d1d333b103cce` (2026-10-02); `plugin.json` version `1.0.0` |
| Local capture | `.raw/captures/official-mods/code-modernization-1.0.0/` (hooks, tests, README, CHANGELOG; scripts and commands not captured) |
| License | Apache-2.0 (capture `LICENSE`) |
| Install | `/plugin install code-modernization@claude-plugins-official` |
| userConfig | includes `system` and `track` (upstream `plugin.json`), plus a "Usage counts" option per README |
| Code reviewed | static read of `hooks/hooks.json`, `register.ts` (1298 lines) and README |

## One hooks.json, two hook systems

```json
{
  "hooks": {
    "UserPromptSubmit": [{ "hooks": [{ "type": "command",
      "command": "sh \"${CLAUDE_PLUGIN_ROOT}/scripts/telemetry.sh\" command",
      "timeout": 10, "asyncRewake": true }] }],
    "Stop": [ "...state, run..." ],
    "SessionStart": [ "...health..." ],
    "PostToolUseFailure": [ "...failure..." ],
    "StopFailure": [ "...failure..." ]
  },
  "modules": ["./register.ts"]
}
```

(Abridged from the capture.) The classic hooks run `scripts/telemetry.sh` for usage counts; the `modules` entry loads the pane. See [[Mods vs Classic Hooks]] and [[Classic Hook Bridge]] for how the two coexist.

## The module's footprint

| Events | Detail |
|---|---|
| `session.start` | Binds a host built from literal `$.noun.event(...)` calls |
| `ui.render` | `PromptHint`, `AbovePrompt`, `Pane` |
| `ui.close` | Keeps pane state in step |
| `command.run` | `modernize-panel`, `modernize-review-pane`, `modernize-sign`, and `clear`/`resume` |
| `prompt.submit` | Adds a one-line "Modernization state ... (a status line, not an instruction)" to `context` for composer prompts, only when the line changed |
| `turn.start`, `turn.complete` | Activity and fleet bookkeeping; logs x-ray counts |
| `tool.call` | Tracks touched files and running agents for the map |

Calls: `clock.after`, `clock.every`, `clock.now`, `command.register`, `fs.exists`, `fs.list`, `fs.read`, `fs.stat`, `fs.write`, `prompt.fill`, `store.get`, `store.set`, `turn.abort`, `ui.blit`, `ui.close`, `ui.invalidate`, `ui.log`, `ui.open`, `ui.resolve`, `ui.status`, `ui.toast`; `$.prompt.submit` is wired into the host object but not called anywhere in the captured module (C-ECO-025). Every one exists in the 2.1.288 typings (C-ECO-055).

Reach: L2 (writes files: the review ledger and signed brief under `analysis/<system>/`; drives Claude: `prompt.fill` and `turn.abort`), plus classic hooks that run shell. Usage cost of the mod: none; usage cost of the plugin: high, since `extract-rules` started 50 to 200 agents in the author's runs (C-ECO-026).

## Design details worth copying

- **Literal `$` calls in one binder.** A comment explains each member is spelled `$.noun.event(...)` "so the engine reads what the module calls off its source" (C-ECO-023). Wrap `$` in a host object, but keep the literal calls in one function.
- **Context injection that protects the cache.** The `prompt.submit` hook adds its status line only when it differs from the last one sent, and labels it as data, not instruction. See [[Prompt Cache Discipline]] and [[Prompt Events]].
- **Debounced refresh under load.** `REFRESH_DEBOUNCE_MS = 450` normally, `REFRESH_BUSY_MS = 2500` while a fleet of agents writes.
- **Tests for hostile input.** The capture ships `tests/hostile.test.ts` beside logic, mount, register, stacks and verification tests.

## Recommendations

- Use it for what it is: a modernization workflow; the pane is optional. Pilot on one module first, as its README says. EVIDENCE-BASED
- Read its `register.ts` as an example of a large pane that reads state from disk artifacts, not chat. PRACTITIONER
- Copy the "changed-only" `prompt.submit` context pattern for any status you feed the model. PRACTITIONER
- Expect real token spend on large estates; every fan-out step states its agent count first. EVIDENCE-BASED

> [!contradiction]
> The README says usage counts go "through Claude Code's own telemetry", yet the classic hooks call `scripts/telemetry.sh`, which this capture does not include. How the script reaches Claude Code's telemetry (installed plugins cannot call `$.telemetry`, C-ECO-016) is unverified; the README is the only source.

## Caveats

- The capture lacks `scripts/`, `commands/` and `agents/`, so the classic-hook and workflow halves were not reviewed.
- Tested-on version is not stated in the captured README or CHANGELOG.
- The pane is labelled "early access, terminal" in the CHANGELOG.

## Related

- [[Mod Catalog]] row and verdict.
- [[Mods vs Classic Hooks]] and [[Classic Hook Bridge]] for mixed hooks.json files.
- [[Build a Pane Flow]] for the pane mechanics it uses.
- [[Usage Cost Surface]] for fan-out agent spend.
- [[userConfig and Plugin Options]] for `system` and `track`.
- [[Marketplaces and Distribution]] for the official marketplace.
- [[Testing Kit]] for its test layout.

## Sources

- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/` (retrieved 2026-10-03)
- eco-gh-code-modernization-upstream: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-modernization (retrieved 2026-10-03, pinned d182ca4)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
