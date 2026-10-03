---
type: "deliverable"
title: "Ranked Build Ideas"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/deliverable"
  - "#confidence/practitioner"
confidence: "practitioner"
lane: "patterns-and-ideas"
related:
  - "[[Built-in diff Mod]]"
  - "[[Mod Catalog]]"
  - "[[Patterns Playbook]]"
  - "[[Pitfalls Playbook]]"
  - "[[Usage Cost Surface]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Mods API gaps requested in the 91870 thread but not shipped]]"
  - "[[Build a Status Band Flow]]"
  - "[[Build a Tool Call Guard Flow]]"
  - "[[cctop]]"
  - "[[Arunjay4213 claude-mods]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)"
sources:
  - "compass-report"
  - "claudedev-getting-started"
  - "docs-mods-events"
  - "docs-mods-api"
  - "docs-mods-reference"
  - "docs-mods-overview"
  - "pa-gh-91870-mined"
  - "types-2-1-288"
---

# Ranked Build Ideas

The seed report ranked eight ideas by time saved, with post-turn-verify first (compass-report L380-391). Re-ranked on 2026-10-03 against what now exists (the built-in `/diff` pane, the official samples, and the community catalog as the seed report lists it), the top build is still post-turn-verify, followed by a cache-break detector and a git line in a band. Four seed ideas drop to skip because an existing mod, a built-in, or a non-mod feature covers most of the value. Ranks are judgment, not measurement; cost surfaces are from the docs.

## Verdict key

- **build**: worth writing now with documented events only.
- **watch**: blocked by a missing API or not yet worth it; re-check after releases.
- **skip**: covered by an existing mod, built-in, or a non-mod feature.

Cost surface: **none** (reads and drawing only), **local** (`$.process.run`, `$.fs`), **model** (`$.model.*` on the user's usage), **turn** (starts or extends a Claude turn), **cache** (risks prompt cache misses).

## Ranked table

| Rank | Idea | Seed rank | Verdict | Events and calls | Cost surface | What exists now | Why this rank |
|---|---|---|---|---|---|---|---|
| 1 | Post-turn verify: run lint, typecheck, tests on files changed this turn | 1 | build | `tool.call` (Edit, Write after `next`) to collect paths; `turn.complete` runs `$.process.run`; failures as `{ text }`; optional `classic.Stop` `{ block }` to make Claude fix them | local; turn only if fed back | Nothing shipped community-wide per seed | Highest time saved; `classic.Stop` block gives the feedback loop without `$.prompt.submit` |
| 2 | Cache-break detector | 3 | build | `turn.step` generator reads `usage.cache_read_input_tokens` vs `cache_creation_input_tokens`; observe `prompt.section`, `prompt.context`, `tool.describe` answers and hash them to name the section that changed | none | token-ledger shows a ratio and cache-tax handles idle expiry (seed only, not reviewed); docs show the `turn.step` logging example | Cheap, zero tokens, and directly protects spend; attribution by hashing is feasible with documented events |
| 3 | Git line in the band | 2 | build (as a row in an existing band) | `AbovePrompt`; refresh on `turn.complete` and Bash `tool.call` after `next`; `$.process.run(['git','status','--porcelain=v2','--branch'])` | local | Built-in `/diff` pane shows changes, not branch or ahead/behind | Small; adding a row to a band you already run avoids a second band competing for space |
| 4 | Host and infra guard (`rpm-ostree`, `systemctl` power actions, `kubectl` prod, `terraform apply`) | 7 | build only if a dialog is needed | `tool.call` on Bash, `$.ui.ask`, `.catch` fail closed | none | Blast Radius sample and launch-codes (seed); classic settings hooks | Fixed commands are better as permission rules; build only to add an ask dialog or a dry-run report |
| 5 | Long-turn notifier | new (getting-started idea) | watch | `turn.complete` with `e.durationMs`; `$.ui.toast` | none | None known | A toast only shows inside the session, which is where you already are; worth it only if paired with an OS notification via `$.process.run` |
| 6 | Mod auditor via `plugin.register` | 8 | watch | `plugin.register` observing `e.uses` of other mods; needs an outer tier | none | `claude plugin validate` lists `hooks:` and `calls:` statically; modscope (seed) | Static validate already gives the disclosure; runtime auditing needs `prependPlugins` and is a policy-mod job |
| 7 | Parsed-Bash guard (argv, compound segments) | new | watch | `tool.call` on Bash | none | Gap 5 in [[Mods API gaps requested in the 91870 thread but not shipped]] | Blocked: no parsed command on the event; regex guards stay reminders |
| 8 | Subagent context manager (compact or trim a subagent) | new | watch | `session.compact`, `$.session.compact` | model | `SessionCompactArgs` has no `agentId` (types 2.1.288 L10059-10065) | Blocked by the API |
| 9 | Task-files pane plus pre-commit checklist | 4 | skip | `tool.call`, pane | none | Built-in `/diff` pane; Replay Theater sample | Mostly covered; add a checklist row to an existing pane if needed |
| 10 | Unified usage HUD | 6 | skip | `$.session.usage()`, `turn.step` | none | cctop, Arunjay4213 trio (seed, unreviewed); the status line | Install one after an audit instead of building a fourth |
| 11 | Pre-task primer (branch, ticket, conventions) | 5 | skip | `prompt.submit` `context` | cache (low) | CLAUDE.md and skills; [[Prompt Cache Discipline]] shows the gated version | Static conventions belong in CLAUDE.md at zero code; dynamic facts only if a regex gate exists |
| 12 | Files-read map pane | new (getting-started idea) | skip | `tool.call` on Read, Grep, Glob; pane | none | mission-control (seed) and Replay Theater style panes | Low value for daily work |

## Notes on the top three

**Post-turn verify.** Collect edited paths from `tool.call` after `next` and act in `turn.complete`. Run checks with `$.process.run` and a timeout (30 s default, up to 10 minutes) so the hook budget is not touched (docs-mods-reference). To feed failures back, return `{ block: summary }` from `classic.Stop` once per turn, guarded by `stop_hook_active`, rather than `$.prompt.submit`, which waits for idle and starts a new turn (docs-mods-api). Keep the result line short and put the full log in a pane opened by a command. Keep the edited set in `$.state`, not module variables (Pitfalls S1).

**Cache-break detector.** Hash each `prompt.section` and `prompt.context` answer by observing `await next(e)`, store hashes in `$.state`, and on each main-thread `turn.step` compare `cache_creation_input_tokens` with the prior step. When a large write follows a changed hash, log the section name to debug and show one band warning. Costs nothing, because it reads usage the API already returns (docs-mods-events).

**Git line in the band.** Add a git row that refreshes after Bash calls and turns, not on a timer, and yield on `hasSurvey`.

> [!contradiction]
> The seed report ranks the git-state band second and the cache-break detector third. With the built-in `/diff` pane and any band you already run, a standalone git band adds little, while no installed mod attributes cache writes to a cause. This note swaps them. Judgment, not data.

## Recommendations

- Build post-turn verify into a mod you already run that tracks edits, rather than as a new plugin. PRACTITIONER
- Keep all three builds at zero model cost; feed failures back through `classic.Stop` only on failure. PRACTITIONER
- Audit, then install, an existing usage HUD instead of building one. PRACTITIONER
- Revisit every watch row after each Claude Code release. PRACTITIONER

## Caveats

- Community coverage is taken from the seed report and was not re-verified here; the ecosystem lane owns that check.
- Time-saved ordering is judgment; no usage data was collected.
- Row 4 assumes fixed host commands are already covered by permission rules or a settings hook.

## Related

Existing coverage comes from [[Built-in diff Mod]] and the [[Mod Catalog]], including [[cctop]] and [[Arunjay4213 claude-mods]]. Shapes are in [[Patterns Playbook]] and traps in [[Pitfalls Playbook]]. Cost columns follow [[Usage Cost Surface]] and [[Prompt Cache Discipline]]. Blocked rows map to [[Mods API gaps requested in the 91870 thread but not shipped]]. Build procedures: [[Build a Status Band Flow]] and [[Build a Tool Call Guard Flow]].

## Sources

- compass-report: `.raw/sources/compass-report-2026-10-02.md` (secondary, lead list only)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- pa-gh-91870-mined: `.raw/captures/lanes-2026-10-03/patterns-and-ideas/gh-issue-91870-mined.md`
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
