---
type: "deliverable"
title: "Mod Catalog"
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
lane: "ecosystem"
related:
  - "[[Mod Directories]]"
  - "[[Reach Levels]]"
  - "[[Usage Cost Surface]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Read Only Audit Decision]]"
  - "[[Claude Code Release Channels]]"
  - "[[Built-in diff Mod]]"
  - "[[Playground Sample Mods]]"
  - "[[cctop]]"
source_urls:
  - "https://github.com/anthropics/claude-code/tree/main/mods (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods (retrieved 2026-10-03)"
  - "https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03)"
sources:
  - "eco-gh-anthropics-mods"
  - "eco-gh-playground-mods"
  - "code-modernization-1-0-0"
  - "eco-gh-cctop"
  - "eco-gh-arunjay4213"
  - "eco-gh-cc-pr-tracker"
  - "eco-gh-karanb192-mods"
  - "eco-gh-cache-tax"
  - "eco-gh-hamzafer"
  - "eco-gh-onewave"
  - "eco-gh-awesome-claude-code-mods"
  - "eco-static-scan"
  - "types-2-1-288"
---

# Mod Catalog

Forty mods from Anthropic (three pinned repos) and seven pinned community repos, each pinned to a commit, read statically, and graded on reach (L0 to L3), usage cost, tested-on version and a verdict. Nothing here was installed or run. The verdicts split 5 adopt, 18 trial (3 official, 15 community) and 17 avoid. Start with the built-ins and the token-weather sample; community trials are mostly low-reach trackers, toys and cc-pr-tracker, and every mod that calls the model on a timer or reads your inbox is "avoid" by default.

## How to read a row

- **Reach** follows [[Reach Levels]]: L0 draws and remembers, L1 reads (files, env, settings, transcript), L2 writes files, runs processes or drives Claude (`model.*`, `prompt.submit`, `turn.abort`, `prompt.fill`), L3 reaches the network (`http.fetch`, MCP connectors).
- **Usage cost**: none, model calls (the mod calls `$.model.*` itself), or turns (it submits prompts).
- **Tested on**: the Claude Code version the author claims. "scan 2.1.287" means only the awesome-list scanner validated it on 2.1.287.
- **Code reviewed**: "static read" means this lane read the source at the pin; nothing was executed.
- **Verdict**: adopt (use or copy now), trial (try with eyes open), avoid (skip unless you accept the stated risk).

## Pins

| Repo | Full SHA | Commit date |
|---|---|---|
| anthropics/claude-code (mods/) | `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528` | 2026-10-02 |
| anthropics/claude-code-playground | `569c5283d9a0a7ee7938df85bb32e4f48cbb8c86` | 2026-10-01 |
| anthropics/claude-plugins-official | `d182ca456ca09d31d139f7d3818d1d333b103cce` | 2026-10-02 |
| tomstagl/cctop | `6ceafc34a972f4e58d5e53b1c69f80e2a9759d41` | 2026-10-01 |
| Arunjay4213/claude-mods | `d4fffd7de9204a62b10e7b3604fc893158fa25fd` | 2026-09-15 |
| sezaakgun/cc-pr-tracker | `514da1edb4877cdb812ae1a25f79aa81fb6aa6db` | 2026-09-29 |
| karanb192/claude-code-mods | `9d73de721ed7e53b88ff24618f266c8082bfed76` | 2026-10-02 |
| karanb192/cache-tax | `2b51ee46ddac789a58170453439838c3a26e134b` | 2026-09-20 |
| hamzafer/claude-code-mods | `543abfa670c2242779c9f93cf2ee414a4709a300` | 2026-10-02 |
| OneWave-AI/claude-code-mods | `ee519cb3d4d4f6d9a336427fe809d939999fb8c7` | 2026-10-02 |

## Official

| Name | Repo | Pin | What it does | Events | Reach | Usage cost | Tested on | Code reviewed | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| diff | anthropics/claude-code mods/diff | 1c229fc | `/diff` pane of uncommitted changes | session.start, ui.render, command.run, ui.close, ui.focus, ui.scroll, tool.call, prompt.submit | L2 | none | built in, 2.1.288 | static read | adopt: built in, git read-only, best pane reference |
| agents-md | anthropics/claude-code mods/agents-md | 1c229fc | loads AGENTS.md like CLAUDE.md, one option | session.start, prompt.context, agent.spawn, tool.call | L1 | none (adds instruction files) | built in, 2.1.288 | static read | adopt: default on, documented option |
| sec-default | anthropics/claude-code mods/sec-default | 1c229fc | keeps org policy out of user mods' reach | classic.*, prompt.*, settings.read, tool.*, agent.*, plugin.register (15) | L1 | none | built in, 2.1.288 | static read | adopt: org guard and policy-mod template |
| telemetry | anthropics/claude-code mods/telemetry | 1c229fc | `$.telemetry` for built-ins, batched analytics | telemetry.*, engine.create, session.start, session.end | L3 | none | built in, 2.1.288 | static read | adopt as reference: noun-contract design; analytics on/off is a user choice |
| token-weather | claude-code-playground | 569c528 | context forecast band | session.start, turn.complete, ui.render | L0 | none | 2.1.280; validate 2.1.285 | static read | adopt: minimal band template |
| blast-radius | claude-code-playground | 569c528 | holds risky Bash, shows impact, Proceed/Cancel | tool.call, ui.render | L2 | none | 2.1.280; validate 2.1.285 | static read | trial: hold fixes not re-run live per README |
| replay-theater | claude-code-playground | 569c528 | `/replay` steps last turn's edits | session.start, command.run, tool.call, turn.start, turn.complete, ui.render, ui.close | L1 | none | 2.1.280; validate 2.1.285 | static read | trial: MultiEdit and band fallback untested per README |
| code-modernization pane | claude-plugins-official | d182ca4 | modernization progress pane plus classic telemetry hooks | session.start, ui.render, ui.close, command.run, prompt.submit, turn.start, turn.complete, tool.call | L2 | plugin: high (50 to 200 agents per extract-rules) | not stated | static read (module only) | trial: only for modernization work; scripts not reviewed |

## Community

| Name | Repo | Pin | What it does | Events | Reach | Usage cost | Tested on | Code reviewed | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| cctop | tomstagl/cctop | 6ceafc3 | btop-style usage dashboard pane over external binary | session.start, turn.*, tool.call, skill.prompt, session.compact, command.run, ui.render, ui.close | L2 | none | 2.1.284 | static read (mod) | trial: deepest view, but external binary and stale flag text |
| context-lens | Arunjay4213/claude-mods | d4fffd7 | context used, turns to compaction | session.start, turn.complete, session.compact, command.run, ui.render, ui.close | L0 | none | 2.1.272 | static read | trial: smallest footprint; no license file |
| quota-meter | Arunjay4213/claude-mods | d4fffd7 | 5h and 7d plan limits with projection | session.start, turn.complete, command.run, ui.render, ui.close | L0 | none | 2.1.272 | static read | trial: L0; subscription only |
| token-ledger | Arunjay4213/claude-mods | d4fffd7 | session and turn cost, cache hit ratio | session.start, turn.complete, command.run, ui.render, ui.close | L0 | none | 2.1.272 | static read | trial: L0; no license file |
| budget-guard | Arunjay4213/claude-mods | d4fffd7 | refuses tools, aborts turns past cost or quota limits | session.start, turn.start, turn.complete, tool.call, prompt.submit, command.run | L2 | none (saves spend) | 2.1.272 | static read | trial: set limits first; aborts turns by design |
| cc-pr-tracker | sezaakgun/cc-pr-tracker | 514da1e | watched PRs above the prompt, alerts on change | session.start, config.set, prompt.submit, tool.call, turn.complete, ui.render | L2 | none | 2.1.269 | static read | trial: argv-only gh calls, `{drop}` saves turns |
| mod-builder | karanb192/claude-code-mods | 9d73de7 | skill: plan reach budget, validate, threat model | none (skill) | n/a (skill; scripts fetch scan) | model use of the skill | 2.1.272 | static read | trial: footprint gate is useful; star prompt uses gh |
| fable-pin | karanb192/claude-code-mods | 9d73de7 | pins non-fork subagents to `fable` | session.start, command.run, agent.spawn | L0 | shifts subagent spend to one model | scan 2.1.287 | static read | trial: only if you want every subagent on that model |
| cache-tax | karanb192/cache-tax | 2b51ee4 | cold-send guard and keep-warm pings | session.start, classic.SessionStart, command.run, prompt.submit, turn.step, turn.complete, session.compact | L2 | model calls (pings) | 2.1.276 | static read | avoid: pings cost tokens, needs 1h cache |
| mission-control | hamzafer/claude-code-mods | 543abfa | live agent and code map pane | session.start, turn.*, tool.call, agent.spawn, command.run, ui.render | L2 | model calls (per turn) | 2.1.287 (author) | static read | avoid: macOS Chrome path, per-turn model call, no license |
| token-weather (copy) | hamzafer/claude-code-mods | 543abfa | context band | session.start, turn.complete, ui.render | L0 | none | 2.1.287 (author) | static read | avoid: use the official sample |
| where-am-i | hamzafer/claude-code-mods | 543abfa | goal and next-step band | session.start, prompt.submit, tool.call, turn.complete, command.run, ui.render | L2 | model calls (per turn) | 2.1.287 (author) | static read | avoid: per-turn Haiku call, no license |
| agent-radar | hamzafer/claude-code-mods | 543abfa | one line per running subagent | session.start, agent.spawn, tool.call, turn.complete, command.run, ui.render | L1 | none | 2.1.287 (author) | static read | trial: L1, no model calls; no license |
| browser-lanes | hamzafer/claude-code-mods | 543abfa | Playwright browser ownership and cleanup | session.start, session.end, agent.spawn, tool.call, turn.complete, command.run, ui.render | L2 | none | 2.1.287 (author) | static read | avoid: kills processes, setup-specific |
| merge-gate | hamzafer/claude-code-mods | 543abfa | holds `gh pr merge` until CI and one Codex review | session.start, tool.call, turn.complete, command.run, ui.render | L2 | none | 2.1.287 (author) | static read | avoid: hard-codes one Codex model |
| oneform-line | hamzafer/claude-code-mods | 543abfa | author's fitness app band | session.start, turn.complete, command.run, ui.render | L3 | none | 2.1.287 (author) | static read | avoid: private app |
| rulebook-guard | hamzafer/claude-code-mods | 543abfa | rewrites em dashes; asks before amend, push, PII | tool.call | L2 | none | 2.1.287 (author) | static read | avoid: silently rewrites Claude's writes |
| blast-radius (copy) | hamzafer/claude-code-mods | 543abfa | risky command hold | tool.call, ui.render | L2 | none | 2.1.287 (author) | static read | avoid: use the official sample |
| session-saver | hamzafer/claude-code-mods | 543abfa | `/park` notes, names sessions | session.start, prompt.submit, turn.complete, command.run, ui.render | L2 | model calls | 2.1.287 (author) | static read | avoid: needs author's `unpause` tool |
| replay-theater (copy) | hamzafer/claude-code-mods | 543abfa | edit replay | session.start, tool.call, turn.*, command.run, ui.render | L1 | none | 2.1.287 (author) | static read | avoid: use the official sample |
| reels | hamzafer/claude-code-mods | 543abfa | YouTube Shorts pane while Claude works | session.start, session.end, turn.*, command.run, ui.render | L3 | none | 2.1.287 (author) | static read | avoid: spawns Playwright, fetches video |
| snake | hamzafer/claude-code-mods | 543abfa | game pane | session.start, turn.*, ui.message, command.run, ui.render | L0 | none | 2.1.287 (author) | static read | trial: harmless toy; no license |
| burn-meter | OneWave-AI/claude-code-mods | ee519cb | spend band with plan bars | session.start, prompt.submit, turn.complete, command.run, ui.render | L0 | none | 2.1.287 (author) | static read | trial: L0, MIT |
| launch-codes | OneWave-AI/claude-code-mods | ee519cb | code-gated risky Bash | session.start, tool.call, command.run, ui.render | L0 | none | 2.1.287 (author) | static read | trial: strict guard, MIT |
| session-wrapped | OneWave-AI/claude-code-mods | ee519cb | session recap PNG | session.*, prompt.submit, tool.call, turn.complete, command.run, ui.render | L2 | none | 2.1.287 (author) | static read | avoid: runs python3, writes to the user's Desktop folder |
| boss-fight | OneWave-AI/claude-code-mods | ee519cb | pixel boss from failing tests | session.start, tool.call, command.run, ui.render | L0 | none | 2.1.287 (author) | static read | trial: toy |
| code-pet | OneWave-AI/claude-code-mods | ee519cb | pixel pet fed by tool calls | session.start, prompt.submit, tool.call, turn.complete, command.run, ui.render | L0 | none | 2.1.287 (author) | static read | trial: toy |
| inner-monologue | OneWave-AI/claude-code-mods | ee519cb | model-written thoughts pane | session.start, prompt.submit, tool.call, command.run, ui.render | L2 | model calls | 2.1.287 (author) | static read | avoid: paid toy |
| sportscaster | OneWave-AI/claude-code-mods | ee519cb | spoken play-by-play | session.start, prompt.submit, tool.call, turn.complete, command.run, ui.render | L2 | model calls | 2.1.287 (author) | static read | avoid: paid toy |
| agent-narrator | OneWave-AI/claude-code-mods | ee519cb | plain-English step narration | session.start, prompt.submit, tool.call, turn.complete, command.run, ui.render | L2 | model calls | 2.1.287 (author) | static read | avoid: model call stream |
| agent-race | OneWave-AI/claude-code-mods | ee519cb | scoreboard across sessions | session.start, tool.call, turn.complete, command.run, ui.render | L2 | none | 2.1.287 (author) | static read | trial: writes a shared race folder |
| inbox-alerts | OneWave-AI/claude-code-mods | ee519cb | Gmail, Slack, Calendar alerts and triage | session.start, command.run, ui.render | L3 | turns (triage) plus connector calls every 2 min | 2.1.287 (author) | static read | avoid: third-party text into a model turn |

## Totals

| Verdict | Count |
|---|---|
| adopt | 5 (4 built-ins, token-weather) |
| trial | 18 |
| avoid | 17 |

## Recommendations

- Adopt the built-ins as-is and read diff, sec-default and the playground samples before any community repo. EVIDENCE-BASED
- For usage visibility, trial Arunjay4213's L0 trackers or burn-meter before cctop; the reach difference is processes versus none. EVIDENCE-BASED
- Treat every `model.complete` or `model.fork` mod as a recurring cost line; avoid unless the value is clear. EVIDENCE-BASED
- Re-run `claude plugin validate` on your version before installing any row; grades are for 2.1.287 and 2.1.288. EVIDENCE-BASED
- Strip `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` and shell rc edits from any copied install steps (cctop, Arunjay4213, cc-pr-tracker, karanb192, cache-tax). EVIDENCE-BASED

## Caveats

- Footprints come from a regex scan plus targeted reading; calls split across lines can be missed (cctop's `prompt.fill` was found by hand).
- "Tested on" is the author's claim; this lane ran nothing.
- hamzafer and OneWave are absent from the awesome-list scanner data, so their reach grades are this lane's alone.
- thieung/claude-mods, konsta95, Sma1lboy and other repos from the seed list are out of this lane's slice and not graded here.

## Related

- [[Mod Directories]] for discovery sources.
- [[Reach Levels]] and [[Usage Cost Surface]] for the grading scales.
- [[Audit a Third-Party Mod Flow]], [[Mod Security Audit Checklist]] and [[Read Only Audit Decision]] before installing a trial row.
- [[Claude Code Release Channels]] for the tested-on column.
- Entity notes: [[Built-in diff Mod]], [[Built-in agents-md Mod]], [[Built-in sec-default Mod]], [[Built-in telemetry Mod]], [[Playground Sample Mods]], [[code-modernization Plugin]], [[cctop]], [[Arunjay4213 claude-mods]], [[cc-pr-tracker]], [[karanb192 claude-code-mods]], [[hamzafer claude-code-mods]], [[OneWave claude-code-mods]].

## Sources

- eco-gh-anthropics-mods: https://github.com/anthropics/claude-code/tree/main/mods (retrieved 2026-10-03, pinned 1c229fc)
- eco-gh-playground-mods: https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods (retrieved 2026-10-03, pinned 569c528)
- code-modernization-1-0-0: `.raw/captures/official-mods/code-modernization-1.0.0/` (retrieved 2026-10-03)
- eco-gh-cctop, eco-gh-arunjay4213, eco-gh-cc-pr-tracker, eco-gh-karanb192-mods, eco-gh-cache-tax, eco-gh-hamzafer, eco-gh-onewave: GitHub repos at the pins above (retrieved 2026-10-03)
- eco-gh-awesome-claude-code-mods: https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03, pinned 59a9911)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
