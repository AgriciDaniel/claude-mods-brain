---
type: "concept"
title: "Best Practices Kernel"
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
lane: "rewrite"
related:
  - "[[Versioning and API Drift]]"
  - "[[Holding a Tool Call]]"
  - "[[Hook Middleware Chain]]"
  - "[[Tool Events]]"
  - "[[Budgets and Limits]]"
  - "[[State Store and Module Variables]]"
  - "[[Classic Hook Bridge]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Band and Pane Fallback]]"
  - "[[Build a Tool Call Guard Flow]]"
  - "[[Usage Cost Surface]]"
  - "[[Testing Playbook]]"
  - "[[Read Only Audit Decision]]"
  - "[[Version Pin Policy]]"
  - "[[Mods API Namespaces]]"
  - "[[Pitfalls Playbook]]"
  - "[[Patterns Playbook]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-reference"
  - "docs-mods-interface"
  - "docs-mods-api"
  - "docs-mods-troubleshoot"
  - "docs-mods-overview"
  - "types-2-1-288"
  - "claudedev-getting-started"
---

# Best Practices Kernel

The fifteen rules that prevent most mod failures on Claude Code 2.1.288, distilled from the [[Pitfalls Playbook]], the [[Patterns Playbook]] and the official docs. Most mod failures are silent: a hook that throws, overruns or returns the wrong shape is skipped and the session carries on (docs-mods-troubleshoot), so most rules are about failing safely and keeping state where it survives. Each rule is one line, then the note that explains it and a confidence tag.

## The kernel

1. Read the typings your own build wrote (`.claude-plugin/types/`) before the docs; where they disagree, the typings win. [[Versioning and API Drift]] EVIDENCE-BASED
2. Decide before you call `next`: a `{ deny }` returned after `await next(e)` arrives after the tool already ran. [[Holding a Tool Call]] EVIDENCE-BASED
3. Chain `.catch(() => ({ deny }))` on every hook that can deny, because an uncaught throw or overrun skips the hook and the call goes through. [[Hook Middleware Chain]] EVIDENCE-BASED
4. Return only the documented result shapes (`next(e)`, `{ deny }`, `{ result }` for `tool.call`); anything else is logged as the wrong shape and ignored. [[Tool Events]] EVIDENCE-BASED
5. Never hold the worker: wait inside `$` calls, run heavy work in `$.process.run` with a `timeoutMs`, and keep a hook's own time far under 10 s. [[Budgets and Limits]] EVIDENCE-BASED
6. Keep what you draw in `$.state` and what must persist in `$.store`; module variables reset on every hot reload. [[State Store and Module Variables]] EVIDENCE-BASED
7. Re-seed per-conversation state from `classic.SessionStart`, since `session.start` does not fire after `/clear`, `/resume` or `/branch`. [[Classic Hook Bridge]] EVIDENCE-BASED
8. Keep `prompt.section`, `prompt.context` and `tool.describe` answers byte-stable; put volatile facts in `prompt.submit` `context`. [[Prompt Cache Discipline]] EVIDENCE-BASED
9. In a band, compose with `await next(e)` and return `next(e)` when `e.props.hasSurvey` is set; check `isPlaced` before trusting a pane. [[Band and Pane Fallback]] EVIDENCE-BASED
10. Use permission rules for hard blocks; a mod that matches command text is a reminder, since `$(...)`, aliases and scripts walk past it. [[Build a Tool Call Guard Flow]] EVIDENCE-BASED
11. Treat every `$.model.*` call and every `$.prompt.submit` as a recurring line on the user's usage, and say so in the README. [[Usage Cost Surface]] EVIDENCE-BASED
12. Prove a change with `tsc -p .`, `claude plugin validate --strict`, `claude plugin test`, then one `--debug-file` load; validate alone does not catch nonexistent `$` methods. [[Testing Playbook]] PRACTITIONER
13. Audit third-party mods statically; run one only in an isolated OS account or VM with owner approval, never in a "disposable project". [[Read Only Audit Decision]] EVIDENCE-BASED
14. Pin `minimumVersion` to 2.1.287 or later and write the tested-on build beside every mod and every verdict. [[Version Pin Policy]] EVIDENCE-BASED
15. Register commands last in `session.start`, inside try/catch, with `immediate: true` unless waiting for the turn is the point. [[Mods API Namespaces]] EVIDENCE-BASED

## Evidence behind each rule

| # | Primary evidence | Pitfall rows | Claim ids |
|---|---|---|---|
| 1 | types 2.1.288 L1-10; docs-mods-create | n/a | C-LIF-042, C-LIF-043 |
| 2 | docs-mods-events; staff comment c5546290346 on #91870 | F4 | C-API-007 |
| 3 | docs-mods-events; types 2.1.288 L8683-8700 | F1, F7 | C-API-010, C-API-011 |
| 4 | docs-mods-reference; types 2.1.288 L11986-12085 | F3 | C-API-019 |
| 5 | types 2.1.288 L4803-4837; docs-mods-reference Limits | F2, F8 | C-API-012 |
| 6 | docs-mods-interface, Keep state | S1, S3 | n/a |
| 7 | docs-mods-reference, Session; docs-mods-troubleshoot | S2 | C-API-034 |
| 8 | docs-mods-events; types 2.1.288 L3899-3952 | C1 | n/a |
| 9 | docs-mods-interface; claudedev-getting-started | D3, D4, D5 | n/a |
| 10 | docs-mods-events; claudedev-getting-started | T4 | n/a |
| 11 | docs-mods-api; docs-mods-admin | C2, C4 | n/a |
| 12 | docs-mods-test; #91870 c5559557492 | L5, L6 | C-LIF-014, C-LIF-022 |
| 13 | docs-mods-overview, What a mod can reach; types 2.1.288 L3009-3014 | n/a | C-SEC-062 |
| 14 | docs-mods-overview (on by default from 2.1.287) | L9 | C-ECO-051, C-ECO-056 |
| 15 | docs-mods-api | N1, N5 | n/a |

## Near misses (true, but not kernel)

- Do not read Claude Code's own `~/.claude/sessions` files; prefer `$.session.*` and `$.agent.list()`. True, but it is a portability rule, covered by rule 14's tested-on line.
- Avoid emoji in bands (column misalignment). PRACTITIONER, cosmetic.
- Do not pass `$` to helpers. Refused on 2.1.260, traced by 2.1.288 validate (C-PAT-060), so no longer a rule.
- Do not call `$.prompt.submit('/x')`; use `$.command.run`. Narrow; lives in [[Pitfalls Playbook]] N4.

## Caveats

- Tested on 2.1.288 by reading docs and typings; no rule was reproduced at runtime.
- Rules 3 and 13 encode a policy choice (fail closed, static first) as much as a fact; the facts behind them are evidence-based.
- Re-check rules 5, 7 and 12 after each release: limits, the session lifecycle and validate's coverage are the parts most likely to move.

## Related

Each rule expands in its linked note; the full trap list is [[Pitfalls Playbook]] and the positive shapes are [[Patterns Playbook]]. The middleware model behind rules 2 to 4 is [[Hook Middleware Chain]]; the `$` surface behind rules 5, 11 and 15 is [[Mods API Namespaces]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
