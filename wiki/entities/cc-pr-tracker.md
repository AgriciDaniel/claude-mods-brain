---
type: "entity"
title: "cc-pr-tracker"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.269"
tags:
  - "#domain/claude-code-mods"
  - "#type/entity"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Mod Catalog]]"
  - "[[Prompt Events]]"
  - "[[Tool Events]]"
  - "[[Build a Status Band Flow]]"
  - "[[Prompt Injection via Mods]]"
  - "[[Reach Levels]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Observe Rewrite Answer]]"
source_urls:
  - "https://github.com/sezaakgun/cc-pr-tracker (retrieved 2026-10-03, pinned 514da1edb4877cdb812ae1a25f79aa81fb6aa6db)"
  - "https://github.com/sezaakgun/cc-pr-tracker/releases/tag/v0.2.0 (retrieved 2026-10-03)"
sources:
  - "eco-gh-cc-pr-tracker"
  - "eco-static-scan"
  - "eco-gh-awesome-claude-code-mods"
  - "docs-mods-overview"
  - "compass-report"
---

# cc-pr-tracker

cc-pr-tracker watches GitHub pull requests from inside a session: paste a PR URL and it gets one line above the prompt with merge state, review decision and required checks, refreshed every minute, with a toast, a flash and a sound when something changes (eco-gh-cc-pr-tracker). It is a single 310-line `register.tsx` with a test file, and a clean example of answering `prompt.submit` with `{ drop }` so a pasted URL never costs a model turn (C-ECO-034). Its reach is L2: it runs `gh` and other host processes.

## Identity and pin

| Field | Value |
|---|---|
| Repo | `sezaakgun/cc-pr-tracker`, MIT, 3 stars |
| Pinned commit | `514da1edb4877cdb812ae1a25f79aa81fb6aa6db` (2026-09-29T09:53:32Z) |
| Releases | v0.1.0 (2026-09-13), v0.2.0 (2026-09-29, added mute) (C-ECO-035) |
| Manifest | `cc-pr-tracker` 0.2.0, `userConfig.muteAll` boolean |
| Requirements | "tested on 2.1.269", `gh` logged in; optional macOS `afplay` and `open`, Linux `xdg-open`, optional cmux |
| Install | `claude plugin marketplace add sezaakgun/cc-pr-tracker`, `claude plugin install cc-pr-tracker@cc-pr-tracker` |
| Code reviewed | static read of `hooks/register.tsx`, `hooks.json`, `plugin.json`, README |

## Events and what each does

| Event | Behaviour |
|---|---|
| `session.start` | Sets up runners for gh, sounds, open and cmux; starts the 60 s poll |
| `config.set {key:'cc-pr-tracker.muteAll'}` | Applies the mute toggle at once |
| `prompt.submit` | URLs inside a normal prompt are watched and the prompt continues; a prompt that is only PR URLs toggles them and returns `{ drop: 'watching owner/repo#N' }` |
| `tool.call {tool:'Bash'}` | After `gh pr create` succeeds, watches the URL from stdout |
| `turn.complete` | Watches PR URLs in the main loop's answer (subagents skipped) |
| `ui.render` AbovePrompt and Pane | One line per PR; the pane names failing checks |

## Host processes

```ts
await $.process.run(
  ['gh', 'api', 'graphql', '-f', `query=${QUERY}`,
   '-f', `o=${owner}`, '-f', `r=${repo}`, '-F', `n=${num}`],
  { timeoutMs: 30_000 })
```

One GraphQL call per watched PR per minute (`POLL_MS = 60_000`), plus `afplay` for sounds, `open` with an `xdg-open` fallback, and the cmux binary when inside cmux (C-ECO-034). Arguments are passed as an argv array, not a shell string, and GitHub text has control characters stripped before drawing.

## Reach and cost

- Reach L2: runs processes, reads env vars and files (eco-gh-awesome-claude-code-mods; eco-static-scan).
- It sees every prompt (to find URLs), every Bash call, and every main-loop answer. Nothing leaves the machine except through `gh` to GitHub with your own credentials.
- Usage cost: none; dropped URL prompts save a turn. GitHub API rate use grows with watched PRs.

## Stale instructions

The README's quick start sets `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` in `~/.claude/settings.json` `env`, warns that this "also loads the hooks module of any other installed plugin", and the repo's own `.claude/settings.json` and `hooks.json` description repeat the flag (C-ECO-035). On 2.1.287+ mods load by default and the flag is ignored (docs-mods-overview); skip step 1.

## Recommendations

- Trial it if you track PRs from the terminal; the footprint is narrow for an L2 mod and every process call is argv-based. EVIDENCE-BASED
- Skip the README's step 1 (flag) on 2.1.287+. EVIDENCE-BASED
- Copy the "prompt that is only a URL returns `{ drop }`" pattern for zero-cost commands typed as plain text. PRACTITIONER
- Watch many PRs only if your GitHub GraphQL budget allows one call per PR per minute. EVIDENCE-BASED

## Caveats

- Tested-on claim is 2.1.269 (pre-GA); the scanner records validate passing on 2.1.287, but no author statement covers 2.1.287+.
- The test file (`register.test.ts`) was not run.
- PR titles and check names from GitHub are drawn on screen, not sent to the model, so the prompt-injection surface is limited to what Claude reads from your own `gh` output elsewhere.

## Related

- [[Mod Catalog]] row and verdict.
- [[Prompt Events]] and [[Observe Rewrite Answer]] for `{ drop }`.
- [[Tool Events]] for the post-call `gh pr create` hook.
- [[Build a Status Band Flow]] for the line-per-item band.
- [[Prompt Injection via Mods]] and [[Audit a Third-Party Mod Flow]] for what it sees.
- [[Reach Levels]] for L2.
- [[userConfig and Plugin Options]] for `muteAll` and the `config.set` hook.

## Sources

- eco-gh-cc-pr-tracker: https://github.com/sezaakgun/cc-pr-tracker (retrieved 2026-10-03, pinned 514da1e)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
- eco-gh-awesome-claude-code-mods: https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03, pinned 59a9911)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (lead only)
