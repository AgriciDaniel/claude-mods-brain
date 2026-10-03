---
type: "entity"
title: "cctop"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.284"
tags:
  - "#domain/claude-code-mods"
  - "#type/entity"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Mod Catalog]]"
  - "[[Arunjay4213 claude-mods]]"
  - "[[Build a Pane Flow]]"
  - "[[Versioning and API Drift]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Reach Levels]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Built-in diff Mod]]"
source_urls:
  - "https://github.com/tomstagl/cctop (retrieved 2026-10-03, pinned 6ceafc34a972f4e58d5e53b1c69f80e2a9759d41)"
  - "https://github.com/tomstagl/cctop/releases/tag/v0.9.1 (retrieved 2026-10-03)"
sources:
  - "eco-gh-cctop"
  - "eco-static-scan"
  - "eco-gh-awesome-claude-code-mods"
  - "docs-mods-overview"
  - "compass-report"
---

# cctop

cctop is a btop-style dashboard for a running Claude Code session: context fill and time to autocompact, tokens and cost with cache-hit ratio, rate limits with an exhaustion forecast, per-tool latency, subagents, touched files, and a rule-based "coach" (eco-gh-cctop). It is two things: a Rust binary (`cctop`) that reads Claude Code's local transcripts and draws a terminal UI in a multiplexer split, and a small mod (`plugin/hooks/pane.tsx`) that docks the same view inside Claude Code by polling that binary (C-ECO-028). The mod alone does nothing without the binary.

## Identity and pin

| Field | Value |
|---|---|
| Repo | `tomstagl/cctop`, MIT, 2 stars |
| Pinned commit | `6ceafc34a972f4e58d5e53b1c69f80e2a9759d41` (2026-10-01T18:07:18Z) |
| Releases | v0.8.0 (2026-09-21), v0.9.0 and v0.9.1 (2026-09-29) |
| Install | `brew install tomstagl/tap/cctop` or `cargo install cctop`, then the plugin |
| Mod module | `plugin/hooks/hooks.json` -> `./pane.tsx` (14 source files, about 3400 lines) |
| Tested on | `TESTED_WITH = '2.1.284'` in `plugin/hooks/model.ts`; checked-in types "Written by Claude Code 2.1.284" (C-ECO-027) |
| CI | `ci.yml` installs `@anthropic-ai/claude-code@latest` and runs `scripts/check-contract.sh` |
| Code reviewed | static read of the mod's `pane.tsx`, `poller.ts`, `model.ts`; Cargo manifest and `src/otel.rs` skimmed |

## Mod footprint

| Events | `session.start`, `turn.start`, `turn.complete`, `tool.call`, `skill.prompt`, `session.compact`, `command.run`, `ui.render`, `ui.close` |
|---|---|
| Calls | `clock.after`, `clock.every`, `clock.now`, `command.register`, `env.get`, `fs.write`, `plugin.root`, `process.run`, `prompt.fill`, `session.id`, `session.model`, `session.usage`, `ui.close`, `ui.invalidate`, `ui.log`, `ui.open`, `ui.resolve`, `ui.status`, `ui.toast` |
| Processes | `cctop query --help` and `cctop query <verb> --session <id>` on a timer (`poller.ts`) |
| Files written | a marker at `~/.cctop/pane/<session>.json` |
| Prompt | `$.prompt.fill` from the coach's fill button; never submits |

(eco-static-scan; `prompt.fill` found by hand because the call spans two lines.) Reach: L2 (runs processes, writes files, writes the prompt box). The scanner grades it L2 and passing validate on 2.1.287 (eco-gh-awesome-claude-code-mods). Usage cost: none; the advisor is rule-based ("36 rules today, no model call", README).

## The binary's reach

- Cargo dependencies include `tokio`, `notify`, `ratatui`, `serde_json` and no HTTP client crate (C-ECO-029).
- `src/otel.rs` hosts an optional OTLP/JSON receiver on `127.0.0.1:4318` for Claude Code's OpenTelemetry export: loopback only.
- The coach records every fire in `~/.cctop/<session>.advisor.json` and can A/B rules across sessions (`cctop run --coach auto`).
- It reads `~/.claude/projects` transcripts, so it sees everything your sessions saw. Treat it as a local reader with full transcript access.

## Stale instructions

The README says the panel view "needs `"CLAUDE_CODE_ENABLE_FUNCTION_HOOKS": "1"` in the `env` block of `~/.claude/settings.json`" and `CLAUDE.md` regenerates types with the flag (C-ECO-030). On 2.1.287+ the flag is ignored (docs-mods-overview). Remove it from anything you copy; do not edit shell rc files for it.

## Recommendations

- Trial it if you want the deepest usage view available; install the binary from a release you can verify, then load the plugin. PRACTITIONER
- Before trusting the panel on a new Claude Code release, check that `TESTED_WITH` or a release note names that version; today it names 2.1.284. EVIDENCE-BASED
- If you only need context, cost and quota lines, the L0 trackers in [[Arunjay4213 claude-mods]] reach far less. EVIDENCE-BASED
- Its CI contract job (install latest, diff the d.ts, `validate --strict`) is a model for [[Re-verify After Release Flow]]. PRACTITIONER

> [!contradiction]
> The seed report says cctop's CI contract job ran on 2.1.284 and that 2.1.287 was not yet confirmed. At 6ceafc3 CI installs `@latest` (now 2.1.288) and the scanner validates it on 2.1.287, but `TESTED_WITH` still reads 2.1.284. Static validation on 2.1.287 is confirmed; an author-run live test on 2.1.287+ is not.

## Caveats

- The Rust binary (about 45k lines) was not reviewed beyond dependencies and the OTLP receiver.
- The "panel view" also requires `/tui fullscreen` per README; behaviour in the non-fullscreen layout was not checked.
- Two stars and a single author: bus factor is one.

## Related

- [[Mod Catalog]] row and verdict.
- [[Arunjay4213 claude-mods]] as the low-reach alternative.
- [[Build a Pane Flow]] and [[Built-in diff Mod]]: cctop and `/diff` share one dock.
- [[Versioning and API Drift]] and [[Re-verify After Release Flow]] for the contract job.
- [[Reach Levels]] and [[Audit a Third-Party Mod Flow]] for grading.
- [[Prompt Cache Discipline]]: its cache panel surfaces misses.

## Sources

- eco-gh-cctop: https://github.com/tomstagl/cctop (retrieved 2026-10-03, pinned 6ceafc3)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
- eco-gh-awesome-claude-code-mods: https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03, pinned 59a9911)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (lead only)
