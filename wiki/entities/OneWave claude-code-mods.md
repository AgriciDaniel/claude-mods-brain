---
type: "entity"
title: "OneWave claude-code-mods"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.287"
tags:
  - "#domain/claude-code-mods"
  - "#type/entity"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Mod Catalog]]"
  - "[[Prompt Injection via Mods]]"
  - "[[Usage Cost Surface]]"
  - "[[Holding a Tool Call]]"
  - "[[Mods Trust Model]]"
  - "[[Reach Levels]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[hamzafer claude-code-mods]]"
  - "[[Arunjay4213 claude-mods]]"
source_urls:
  - "https://github.com/OneWave-AI/claude-code-mods (retrieved 2026-10-03, pinned ee519cb3d4d4f6d9a336427fe809d939999fb8c7)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
sources:
  - "eco-gh-onewave"
  - "eco-static-scan"
  - "docs-mods-reference"
  - "types-2-1-288"
  - "compass-report"
---

# OneWave claude-code-mods

OneWave-AI/claude-code-mods is ten mods "built in one night" by OneWave AI, MIT licensed, with tests for each and a "mix of useful and ridiculous" tone (C-ECO-043). Two are practical (burn-meter, launch-codes), five are entertainment, and three deserve caution: inbox-alerts reads your Gmail, Slack and Calendar connectors on a timer and can submit a triage prompt built from other people's text (C-ECO-044), session-wrapped runs `python3` and writes to the user's Desktop folder (C-ECO-045), and three narrator-style mods call the model repeatedly (C-ECO-046).

## Identity and pin

| Field | Value |
|---|---|
| Repo | `OneWave-AI/claude-code-mods`, MIT, 0 stars, `SECURITY.md` present |
| Pinned commit | `ee519cb3d4d4f6d9a336427fe809d939999fb8c7` (2026-10-02T08:54:51Z) |
| Requirements | "Requires Claude Code 2.1.287 or later." |
| Install | `/plugin marketplace add OneWave-AI/claude-code-mods`, then `/plugin install <mod>@claude-code-mods` |
| Persistent load option | `CLAUDE_CODE_PLUGIN_DIRS` in `~/.claude/settings.json` `env`; this is a documented variable (C-ECO-057) |
| Tests | 17 test files; README says `claude plugin test <folder>` for each (not run) |
| Code reviewed | static scan of all ten; targeted reads of inbox-alerts, session-wrapped, agent-race, launch-codes |

## Per-mod footprint

| Mod | Events | Notable calls | Reach | Usage cost |
|---|---|---|---|---|
| burn-meter | session.start, prompt.submit, turn.complete, command.run, ui.render | `session.usage`, store, clock | L0 | none |
| launch-codes | session.start, tool.call, command.run, ui.render | `ui.ask`, `audio.play`, `ui.blit` | L0 (blocks Bash) | none |
| session-wrapped | session.start, session.end, prompt.submit, tool.call, turn.complete, command.run, ui.render | `process.run` (python3, base64), `fs.write`, `env.get` | L2 | none |
| boss-fight | session.start, tool.call, command.run, ui.render | store, `ui.blit`, `ui.panes` | L0 | none |
| code-pet | session.start, prompt.submit, tool.call, turn.complete, command.run, ui.render | store | L0 | none |
| inner-monologue | session.start, prompt.submit, tool.call, command.run, ui.render | `model.complete` (haiku) | L2 | model calls |
| sportscaster | session.start, prompt.submit, tool.call, turn.complete, command.run, ui.render | `model.complete` (haiku), `audio.speak`, `audio.play` | L2 | model calls plus speech |
| agent-narrator | session.start, prompt.submit, tool.call, turn.complete, command.run, ui.render | `model.complete` (haiku) | L2 | model calls |
| agent-race | session.start, tool.call, turn.complete, command.run, ui.render | `fs.write`, `fs.read`, `fs.list` (shared race folder), `audio.speak` | L2 | none of its own |
| inbox-alerts | session.start, command.run, ui.render | `mcp.call` (claude.ai Gmail, Slack, Google Calendar), `prompt.submit` | L3 via connectors, drives Claude | MCP calls every 2 minutes; a full turn on triage |

(eco-static-scan; all calls exist in the 2.1.288 typings, C-ECO-055.)

## inbox-alerts in detail

- Polls the three claude.ai connectors with `$.mcp.call` every `EVERY_MS = 2 * 60 * 1000` and shows toasts, a status count and a pane.
- `/alerts triage` (or the pane's triage button) calls `$.prompt.submit` with a fixed instruction block plus the alerts fenced in `<untrusted-alerts>`, telling Claude not to send, reply or follow instructions inside them.
- Fencing helps but is not a boundary: the text of any email or Slack message reaches the model in a turn you did not type. See [[Prompt Injection via Mods]].
- `ME = { email: '', slackId: '' }` is hard-coded empty; users edit source to get mention filtering.

## launch-codes

Classifies risky Bash (`rm -rf`, force push, `git reset --hard`, `DROP`/`TRUNCATE` through a SQL client, `supabase db reset`, `vercel --prod`, `chmod -R 777`, curl piped to a shell) and requires a one-time code plus a LAUNCH press; anything else returns `{ deny }` with a reason. It is a heavier-UI cousin of the playground's blast-radius; see [[Holding a Tool Call]].

## Recommendations

- Trial burn-meter for a cost band; it only reads usage and draws. EVIDENCE-BASED
- Trial launch-codes if you want a stricter guard than blast-radius; test with `/launch-codes test <command>` first. PRACTITIONER
- Avoid inbox-alerts: periodic connector reads plus a model turn built from third-party text is a standing injection and usage risk. EVIDENCE-BASED
- Avoid session-wrapped unless you accept a mod running Python and writing PNGs to your Desktop folder. EVIDENCE-BASED
- Treat inner-monologue, sportscaster and agent-narrator as paid toys: each calls the model while you work. EVIDENCE-BASED

## Caveats

- Not in the awesome-list scanner data despite being in its seeds (C-ECO-048); grades here come from this lane's scan.
- The seed's "statically validated on 2.1.284" was not reproduced; the README only claims 2.1.287+.
- Model-call frequency per narrator mod was not measured.

## Related

- [[Mod Catalog]] rows for all ten.
- [[Prompt Injection via Mods]] and [[Mods Trust Model]] for inbox-alerts.
- [[Usage Cost Surface]] for the `model.complete` mods.
- [[Holding a Tool Call]] for launch-codes.
- [[Reach Levels]] and [[Audit a Third-Party Mod Flow]] for grading.
- [[hamzafer claude-code-mods]] and [[Arunjay4213 claude-mods]] for comparable collections.

## Sources

- eco-gh-onewave: https://github.com/OneWave-AI/claude-code-mods (retrieved 2026-10-03, pinned ee519cb)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (lead only)
