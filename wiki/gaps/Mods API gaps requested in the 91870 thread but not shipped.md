---
type: "gap"
title: "Mods API gaps requested in the 91870 thread but not shipped"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/gap"
  - "#confidence/practitioner"
confidence: "practitioner"
lane: "patterns-and-ideas"
related:
  - "[[Mods design thread, anthropics claude-code issue 91870]]"
  - "[[Mods API Namespaces]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Ranked Build Ideas]]"
  - "[[Pitfalls Playbook]]"
  - "[[Versioning and API Drift]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Testing Kit]]"
  - "[[Agent and Command Events]]"
  - "[[Render Sites]]"
source_urls:
  - "https://github.com/anthropics/claude-code/issues/91870 (capture retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
sources:
  - "gh-issue-91870"
  - "pa-gh-91870-mined"
  - "types-2-1-288"
  - "docs-mods-reference"
  - "docs-mods-events"
  - "compass-report"
---

# Mods API gaps requested in the 91870 thread but not shipped

The #91870 design thread (opened 2026-09-03, 235 comments, launch announced 2026-10-01) holds about 25 groups of API requests; @poteat is the only Anthropic staff commenter (pa-gh-91870-mined). Checked against the 2.1.288 typings, many early asks have shipped (`.catch`, `$.ui.ask`, `$.clock`, `$.session.usage`, `prompt.edit` with decorations, `ui.selection`, `$.ui.panes()`, `session.append`, `classic.*`, `userConfig` in tests, `$.model.complete` effort and timeouts). This note lists what is still missing on 2.1.288, so builders stop hacking around it, and records what shipped so stale asks are not repeated. "Not shipped" means absent from `.raw/captures/types-2.1.288/` and the docs captures.

## Still missing on 2.1.288

| # | Gap | Askers (approx.) | Staff position | Evidence it is absent |
|---|---|---|---|---|
| 1 | First-party `hook.error` or health event, fire counts, flag-off notice | about 12 (e.g. [comment 5532848503](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5532848503)) | `next.trace` offered instead | No `hook.error` in typings |
| 2 | A guaranteed `agent.complete` event; `agentId` on `tool.check`; teammate id mapping | about 14 ([5961512212](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5961512212), 2026-10-02) | Partly planned ([5734700291](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5734700291)) | No `agent.complete` in typings |
| 3 | Compact a subagent, compact mid-turn, on-demand microcompact | 4 ([5793658650](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5793658650)) | Unanswered | `SessionCompactArgs` has only `instructions` (types 2.1.288 L10059-10065) |
| 4 | Turn-end gate with `decision: block` parity on a native event | 4 ([5551796570](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5551796570)) | Unanswered | `turn.complete` returns `next(e)` or `{ text }` only (docs-mods-reference); `classic.Stop` `{ block }` is the workaround |
| 5 | Parsed or resolved Bash (argv, compound segments) on `tool.call` | 5 ([5530182390](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5530182390)) | Unanswered | Guards still regex `e.command` (docs-mods-events) |
| 6 | Auto mode classifier verdict as an event or field; `decidedBy` for an `ask` | 5 ([5594210625](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5594210625)) | Unanswered | Not in `tool.check` docs |
| 7 | A threshold push event for rate limits and cache expiry | about 9 | Unanswered | `session.measure` fires after each turn and on percent change, but no cache expiry field (docs-mods-reference) |
| 8 | `$.store` compare-and-set, locks | 5 to 7 | Unanswered | `ifVersion` exists on `$.state.set`, not on `$.store` (types 2.1.288 L3203-3208; docs-mods-interface says store get-then-set races) |
| 9 | Registered tools reaching subagents with a `tools:` allowlist | 1 ([5848066352](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5848066352), 2.1.283) | Unanswered | Not addressed in docs |
| 10 | One hook on the full outgoing request instead of ten events | 3+ ([5827373997](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5827373997)) | Declined for performance; `session.append` added ([5840819337](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5840819337)) | `turn.step` rewrites only `model` and `effort` |
| 11 | Hooks on system-reminder attachments for every kind | about 6 | Partly: `prompt.attachment` exists | Declared kinds only (docs-mods-reference) |
| 12 | Hookable permission dialog | 1+ | Declined by design ([5546290346](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5546290346)) | Docs: permission prompt is not a render site |
| 13 | Cloud session drawing | 1 ([5901341470](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5901341470)) | Planned "asap" ([5942362421](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5942362421)) | Overview: cloud sessions draw nothing |
| 14 | WebAssembly in the hooks module | 2 | Floated as planned in thread | Typings say no `WebAssembly` "deliberately" (types 2.1.288 L13762-13770) |
| 15 | Keybinding registration (`$.keybinding.register`) | 1 | Unanswered | Only `Button.action` binds to existing actions (docs-mods-reference) |
| 16 | Composer pills (`$.prompt.attach`) | 1 | Unanswered | No such method |
| 17 | Declared, queryable budgets for every limit | about 5 | `next.budget` exists | Limits table documents most; `session.end` budget handling acknowledged ([5734700291](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5734700291)) |
| 18 | Validate catching unknown nouns, wrong return shapes, plugin under a marketplace with `--strict` | 3+ ([5953998781](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5953998781)) | Acknowledged as possible | Not documented as fixed |
| 19 | Module 512-file link limit removal | 1 ([5774188428](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5774188428)) | "will be removed" ([5795711511](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5795711511)) | Not stated in 2.1.288 docs; unverified either way |
| 20 | Contract version field, signing, install-time capability disclosure | 3+ | Signing unchanged from plugins | Not in docs |
| 21 | A billing statement for `$.model.*` | 1 ([5540419526](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5540419526)) | Unanswered in thread; docs now say plan or API key | See [[How is $.model.classify billed]] |

## Asked in the thread, now shipped (do not re-request)

| Ask | Shipped as | Evidence |
|---|---|---|
| Declarative fail policy (about 20 askers) | `on(...).catch(handler)` | docs-mods-events; declarative JSON flag declined |
| A way to ask the user ([5553458185](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5553458185)) | `$.ui.ask` | docs-mods-events |
| `$.model.complete` effort, timeout, usage, larger cap ([5676619802](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5676619802), on 2.1.272 default 256) | `effort`, `timeoutMs`, `usage`, default 1024, up to 64,000 | types 2.1.288 L5792-5877 |
| `userConfig` values in tests ([5827373997](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5827373997)) | `test(name, { options }, body)` | types 2.1.288 TestOptions; see [[Does claude plugin test support userConfig values yet]] |
| Subagent transcripts ([5725437710](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5725437710)) | `$.session.messages({ agentId })` | types 2.1.288 L10121-10122 |
| Draft decorations ([5671976322](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5671976322)) | `decorations` on `prompt.edit` results | types 2.1.288 L8062-8073 |
| `ui.selection`, list panes | `$.ui.selection()`, `$.ui.panes()` | types 2.1.288 L2382, L2323 |
| realpath, bytes | `$.fs.stat(path, { resolve })` with `realPath`; `$.fs.read(path, { as: 'bytes' })` | types 2.1.288 L3070, L4656-4673 |
| Terminal `Image` element | `Image` (terminal only) | docs-mods-reference Elements |
| Classic hooks wrapper ([5574036379](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5574036379)) | `classic.<Event>` | docs-mods-events |
| Desktop drawing | Supported at launch ([5942362421](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5942362421)) | docs-mods-overview |
| Worktree isolation loss in subagents ([5949411806](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5949411806)) | Fixed in 2.1.288 per staff ([5961758416](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5961758416)) | Staff comment only; SINGLE-SOURCE |

> [!contradiction]
> The seed report's gap list (compass-report L368-376) includes `ui.selection`, draft decorations in `prompt.edit`, and `$.session.compact({agentId})`. On 2.1.288 the first two exist in the typings; only the subagent compact is still missing. Typings win; the seed list was built from pre-launch comments.

## Recommendations

- Before building a workaround, grep the current typings for the method; half the thread's asks shipped within four weeks. EVIDENCE-BASED
- For gap 4, use `classic.Stop` returning `{ block }`, with a loop guard. EVIDENCE-BASED
- For gap 5, treat command-text guards as reminders and keep hard blocks in permission rules. EVIDENCE-BASED
- For gap 8, give each session its own `$.store` key. EVIDENCE-BASED
- Re-run this table after each Claude Code release through [[Re-verify After Release Flow]]. PRACTITIONER

## Caveats

- Asker counts are approximate, from a subagent read of all 235 comments, spot-checked for 19 comment ids.
- "Absent from typings" can miss a capability spelled differently; each row names what was searched.
- Staff fix claims (2.1.285 double render, 2.1.288 worktree and diff element) are not independently tested.

## Related

The thread itself is summarised in [[Mods design thread, anthropics claude-code issue 91870]]. The current surface is in [[Mods API Namespaces]], [[Mods API Cheatsheet]], [[Agent and Command Events]], and [[Render Sites]]. Ideas blocked by these gaps are marked watch in [[Ranked Build Ideas]]; reported traps are in [[Pitfalls Playbook]]; drift handling is in [[Versioning and API Drift]] and [[Testing Kit]].

## Sources

- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (capture retrieved 2026-10-03)
- pa-gh-91870-mined: `.raw/captures/lanes-2026-10-03/patterns-and-ideas/gh-issue-91870-mined.md` (2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (secondary, lead list only)
