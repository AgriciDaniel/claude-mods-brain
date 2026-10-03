---
type: "hot"
title: "Hot"
domain: "Claude Code mods"
status: "active"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/hot"
  - "#confidence/evidence-based"
confidence: "evidence-based"
related:
  - "[[index|Index]]"
  - "[[overview|Overview]]"
  - "[[log|Log]]"
  - "[[Start Here]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Mod Catalog]]"
  - "[[Patterns Playbook]]"
  - "[[Pitfalls Playbook]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)"
---

# Hot

## Recent Context

Built on 2026-10-03 from parallel research lanes, a merge, automated checks, and two fresh-context review rounds. Tested on **Claude Code 2.1.288**. Mods shipped in 2.1.287 on 2026-10-01 and are on by default from that version; the old `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` flag is ignored. #confidence/evidence-based

## Last Updated

2026-10-03. Typings capture: `.raw/captures/types-2.1.288/` (14,973 lines; 43 engine events, 61 op events, 33 classic events, 21 `$` namespaces). Every `refresh_due` is 2026-11-02.

## Key Recent Facts

- **Check the version first.** If `claude --version` is newer than 2.1.288, run [[Re-verify After Release Flow]] before trusting API notes. npm on 2026-10-03: `stable` 2.1.285 (no mods by default yet), `latest` and `next` 2.1.288 ([[Claude Code Release Channels]]).
- **Typings beat docs for this build.** The 2.1.288 typings list four surfaces (terminal, desktop, mobile, vscode) where the docs say two, put `Svg` on every remote surface, and ship members the docs do not mention (`$.ui.selection`, `next.trace`). See [[Mods API Cheatsheet]] and [[API Surface 2.1.288]].
- **Static validation is not safety.** `claude plugin validate` passes an exfiltration-shaped module without warning on 2.1.288; a disposable project is not isolation because `$.fs` takes absolute paths. Use [[Audit a Third-Party Mod Flow]] and [[Mod Security Audit Checklist]].
- **`claude plugin test` can set userConfig on 2.1.288** (`test(name, { options }, body)` in the typings), contradicting older reports. Declared, not executed: [[Does claude plugin test support userConfig values yet]].
- **Classic `Stop` is not `turn.complete`.** Only `classic.Stop` returning `{ block }` keeps Claude going ([[Migrate a Classic Hook Flow]]).
- **Ecosystem:** 359 mods in 373 repos scanned on 2026-10-02; the catalog grades 40 (5 adopt, 18 trial, 17 avoid) ([[Mod Catalog]]).

## Next Action

On the next Claude Code release, run [[Re-verify After Release Flow]] and the drift check, then update `tested_on` here. Open questions that only a runtime trial in an isolated OS user or VM can settle are listed in [[Unverified pre-release security findings on current builds]].
