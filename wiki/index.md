---
type: "index"
title: "Index"
domain: "Claude Code mods"
status: "active"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/index"
  - "#confidence/practitioner"
confidence: "practitioner"
related:
  - "[[hot|Hot]]"
  - "[[overview|Overview]]"
  - "[[log|Log]]"
  - "[[Start Here]]"
  - "[[CONVENTIONS]]"
  - "[[dashboard|Dashboard]]"
  - "[[Tag Taxonomy]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Mod Catalog]]"
  - "[[research-pack-claude-mods|Research Pack]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
---

# Index

Last updated: 2026-10-03 | Total pages: 101 | Ledger sources: 50 | Tested on: Claude Code 2.1.288

Read [[hot|Hot]] first, then this index, then one folder hub. New here: [[Start Here]]. The shape of the domain: [[overview|Overview]]. History: [[log|Log]].

Hubs: [[wiki/concepts/_index|Concepts Hub]] | [[wiki/flows/_index|Flows Hub]] | [[wiki/deliverables/_index|Deliverables Hub]] | [[wiki/entities/_index|Entities Hub]] | [[wiki/platforms/_index|Platforms Hub]] | [[wiki/reports/_index|Reports Hub]] | [[wiki/decisions/_index|Decisions Hub]] | [[wiki/sources/_index|Sources Hub]] | [[wiki/gaps/_index|Gaps Hub]] | [[wiki/questions/_index|Questions Hub]] | [[wiki/experiments/_index|Experiments Hub]] | [[wiki/meta/_index|Meta Hub]] | [[wiki/canvases/_index|Canvases Hub]]

## Concepts (36)

- [[Agent and Command Events]] (developing, evidence-based): This note covers the events that govern who and what runs: subagents (`agent.offer`, `agent.spawn`), slash commands (`command.run`, `command.describe`), `/config` rows (`config.set`, `config.describe`), other mods (`plug...
- [[Band and Pane Fallback]] (developing, evidence-based): A mod has three places to put a view, in falling order of room: a pane, the band above the prompt (`AbovePrompt`), and plain text (a `$.ui.status` line, a toast, a transcript log, or a command reply).
- [[Best Practices Kernel]] (developing, evidence-based): The fifteen rules that prevent most mod failures on Claude Code 2.1.288, distilled from the Pitfalls Playbook, the Patterns Playbook and the official docs.
- [[Budgets and Limits]] (developing, evidence-based): Mods run under time budgets and size caps that Claude Code enforces per hook and per call: a hook gets 10 seconds of its own execution time per event, a `.catch` handler 1 second, and all `session.end` hooks together 1.5...
- [[Classic Hook Bridge]] (developing, evidence-based): Every settings hook event (`Stop`, `SessionStart`, `PostToolUse`, and the rest) is also a mod event named `classic.` plus the event name, and `e` is the same JSON a settings hook reads on stdin, including `transcript_pat...
- [[Claude Code mods documentation set (Anthropic)]] (developing, evidence-based): This note folds canon 001, the ten official mods pages on code.claude.com captured on 2026-10-03, into the vault.
- [[Claude Code plugins and hooks documentation (Anthropic)]] (developing, evidence-based): This note folds canon 006, the thirteen non-mods plugin and settings-hook pages captured on 2026-10-03, into the vault.
- [[Customize Claude Code with mods (Anthropic blog)]] (developing, evidence-based): This note folds canon 002, Anthropic's launch post of 2026-10-01, into the vault.
- [[Getting started with Claude Code mods (claude.dev)]] (developing, practitioner): This note folds canon 003, Addy Osmani's tutorial on claude.dev (2026-10-01, 11 minute read), into the vault.
- [[Holding a Tool Call]] (developing, evidence-based): A `tool.call` hook can pause a tool call by awaiting before it calls `next(e)` or returns; the call stays pending until the hook settles (docs-mods-events).
- [[Hook Middleware Chain]] (developing, evidence-based): Every hook for one event joins a single middleware chain, Koa style: each hook receives `($, e, next)`, and `next(e)` runs the hooks after it and finally Claude Code's own behavior, resolving to the event's result (C-API...
- [[Hook Ordering and Tiers]] (developing, evidence-based): Hooks for one event nest in a fixed order of five tiers, outermost first: `prepend` (managed mods an admin lists first), `user` (everything a person installs), `append` (managed mods listed last), `builtin` (mods bundled...
- [[Hot Reload and Dev Loop]] (developing, evidence-based): A mod is developed against a folder Claude Code watches, so a save reloads the hooks module in the running session without a restart.
- [[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]] (developing, contested): This note folds canon 005, Ehud Melzer's Pluto Security article of 2026-09-22, into the vault.
- [[Marketplaces and Distribution]] (developing, evidence-based): A mod is a plugin, so it ships the way any plugin does: as a folder people load with `--plugin-dir`, through a marketplace (a git repo or URL holding `.claude-plugin/marketplace.json`), or through Anthropic's directory (...
- [[Mod Anatomy]] (developing, evidence-based): A mod is an ordinary Claude Code plugin with one extra file: `hooks/hooks.json` names a single hooks module whose `register(on, options)` function registers event handlers (C-API-001).
- [[Mods API Namespaces]] (developing, evidence-based): `$`, the first argument of every hook, is the only way a mod acts: 21 namespaces of methods, from drawing (`$.ui`) and model calls (`$.model`) to files, processes and the network (`$.fs`, `$.process`, `$.http`) (C-API-04...
- [[Mods Trust Model]] (developing, evidence-based): A mod is code that runs with your user permissions inside Claude Code, and it is not sandboxed (docs-mods-overview, blog-mods-launch).
- [[Mods design thread, anthropics claude-code issue 91870]] (developing, practitioner): This note folds canon 004, the public request for comment that became mods, into the vault.
- [[Mods vs Classic Hooks]] (developing, evidence-based): Classic hooks (the docs now call them "settings hooks") are commands, HTTP calls, MCP tool calls, prompts, or agents that Claude Code launches per event from a settings file or a plugin's `hooks/hooks.json`; mods are Jav...
- [[Observe Rewrite Answer]] (developing, evidence-based): Every mod hook does one of three things with an event, and what it does with `next` decides which (C-API-007).
- [[Org Mod Controls]] (developing, evidence-based): Administrators control mods through managed settings in three layers: the built-in guard `sec-default` and its two options, the plugin-loading keys that already govern every plugin, and an optional policy mod of your own...
- [[Plugin Validate]] (developing, evidence-based): `claude plugin validate <path>` reads a plugin's manifest and runs the same static analysis on the hooks module's source that Claude Code runs when it loads a mod, without executing any code or starting a session (C-LIF-...
- [[Prompt Cache Discipline]] (developing, evidence-based): A mod that changes what Claude reads can silently make every request a cache miss.
- [[Prompt Events]] (developing, evidence-based): Ten events cover everything Claude reads as text: what the user submits (`prompt.submit`), what lands in or near the prompt box (`prompt.fill`, `prompt.suggest`, `prompt.edit`), and what Claude Code writes for Claude on ...
- [[Prompt Injection via Mods]] (developing, evidence-based): Mods touch prompt injection in two directions.
- [[Reach Levels]] (developing, practitioner): Reach levels L0 to L3 are a practitioner taxonomy from karanb192's community scanner, not an Anthropic classification.
- [[Render Sites]] (developing, evidence-based): A render site is a named place in Claude Code's interface where a `ui.render` hook may draw: two empty sites a mod fills (`Pane`, `AbovePrompt`), and thirteen sites Claude Code already draws that a mod can restyle, wrap ...
- [[State Store and Module Variables]] (developing, evidence-based): A mod has three places to keep a value, chosen by how long it must last: a module-level variable (gone on every reload), `$.state` (reactive, survives reloads, reset by `/clear`, `/resume` and `/branch`), and `$.store` (...
- [[Testing Kit]] (developing, evidence-based): The testing kit is the module `claude-code/testing`, which `claude plugin test [dir]` loads for every `*.test.ts` and `*.test.tsx` under a mod's folder, each file in a child of the Claude Code binary, with no session, si...
- [[Tool Events]] (developing, evidence-based): Three events cover every tool Claude uses: `tool.call` fires when a tool is about to run and can refuse, rewrite, answer or wrap it; `tool.check` fires when Claude Code decides whether the call may run and can flip the d...
- [[Turn and Session Events]] (developing, evidence-based): Turn events follow one answer: `turn.start` when it begins, `turn.step` for every model request inside it (several when tools run), and `turn.complete` when it ends (docs-mods-reference L87-95).
- [[UI Elements and JSX]] (developing, evidence-based): A `ui.render` hook returns a plain-data element tree built from constructors that `$.ui.resolve(e)` hands out for the surface being drawn; elements are never globals (C-API-050; docs-mods-interface L345).
- [[Usage Cost Surface]] (developing, evidence-based): A mod spends your usage only through a short list of mechanisms: model calls through `$.model.*`, turns it starts, subagents it starts or reroutes, and text it adds to what Claude reads.
- [[Versioning and API Drift]] (developing, evidence-based): The mods API is early access and moves between Claude Code releases, so the only authority for a given build is the declaration file that build writes beside the mod, not the docs and not the GitHub copy (C-LIF-043).
- [[userConfig and Plugin Options]] (developing, evidence-based): A mod is configured through the ordinary plugin `userConfig` block in `plugin.json`, and its hooks module receives the resolved values as the second argument of `register(on, options)`, defaults filled in (C-LIF-039).

## Flows (16)

- [[Audit a Third-Party Mod Flow]] (developing, evidence-based): This flow takes a mod someone wants to use and produces a pinned, recorded verdict (adopt, trial, or avoid) without ever loading the mod.
- [[Build a Pane Flow]] (developing, evidence-based): A runnable recipe for a pane (a sidebar in a wide fullscreen terminal, a framed region above the prompt otherwise) that lists this session's tool calls, opened by a `/tool-calls` command, with a Clear button, state in `$...
- [[Build a Slash Command Flow]] (developing, evidence-based): A runnable recipe for two slash commands, `/note <text>` and `/notes`, that save and list notes in `$.store` (kept across sessions), with a `userConfig` option for the list length and kit tests that stub the store and pa...
- [[Build a Status Band Flow]] (developing, evidence-based): A runnable recipe for a band above the prompt (the `AbovePrompt` render site) that shows the last turn's duration and tool-call count, keeps its values in `$.state` so a hot reload does not wipe them, and is covered by a...
- [[Build a Tool Call Guard Flow]] (developing, evidence-based): A tool call guard is a `tool.call` hook that holds a risky call, asks the user with `$.ui.ask`, and runs it only on an explicit yes.
- [[Claim Verification Flow]] (developing, evidence-based): A mods claim is verified when a rank 1 source (the official docs captures or the 2.1.288 typings, cited by line range) supports it and a second, independent source agrees.
- [[Context Compaction Routine]] (developing, evidence-based): An agent working this brain keeps its context lean by reading in a fixed order: `wiki/hot.md` first, then `wiki/index.md`, then only the notes the task names, and never whole raw captures (the typings file alone is 14,97...
- [[Explore Plan Code Commit]] (developing, evidence-based): Explore, plan, code, commit applied to a mod means: read the generated typings and the docs before writing anything, plan which events the mod hooks and how much of each budget it spends, code it in a folder you own with...
- [[Migrate a Classic Hook Flow]] (developing, evidence-based): Port a settings hook (a `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, or `SessionStart` script) to a mod in two phases: first wrap it with a pass-through `classic.<Event>` hook so nothing changes, then move th...
- [[Multi-Agent Fan-Out Research Flow]] (developing, practitioner): This brain was built on 2026-10-03 with parallel research lanes, a merge, automated gates, and a fresh-context critic.
- [[Publish a Mod Flow]] (developing, evidence-based): A mod is a plugin, so publishing it means listing it in a marketplace: a `.claude-plugin/marketplace.json` in a git repository that people add once and install from by `name@marketplace` (C-LIF-048, C-LIF-050).
- [[Re-verify After Release Flow]] (developing, evidence-based): The mods API is early access and the typings say it "may change between releases without notice" (types L1-10, C-LIF-043).
- [[Reporting Workflow]] (developing, practitioner): The brain produces two kinds of report: generated reports that scripts write from JSON (the API surface, one audit per scanned mod, and a capability matrix across the mods you scanned), and hand-written notes that judge ...
- [[Research Refresh Workflow]] (developing, evidence-based): This brain is pinned to Claude Code 2.1.288: the typings capture, the API surface JSON, every note's `tested_on`, and every ledger `refresh_due` of 2026-11-02 assume it.
- [[Source Intake Workflow]] (developing, evidence-based): Every fact in this brain enters through one door: an immutable capture under `.raw/`, a hash row in `.raw/.manifest.json`, a ledger entry in `references/source-ledger.json`, and claim rows in `references/claim-ledger.md`...
- [[Synthesis Workflow]] (developing, practitioner): Synthesis turns three machine inputs into one model of "who uses what": the API surface imported from the typings, a static footprint scan per mod, and an optional curated catalog.

## Deliverables (8)

- [[Mod Catalog]] (developing, evidence-based): Forty mods from Anthropic (three pinned repos) and seven pinned community repos, each pinned to a commit, read statically, and graded on reach (L0 to L3), usage cost, tested-on version and a verdict.
- [[Mod Security Audit Checklist]] (developing, evidence-based): Run this before any third-party mod is installed, in order.
- [[Mods API Cheatsheet]] (developing, evidence-based): One page for writing a Claude Code mod against build 2.1.288: the module skeleton, every event with what a hook may return, every `$` namespace, the render sites, the elements, and the limits.
- [[Org Mod Policy Guide]] (developing, evidence-based): Pick one of four policies, deploy its managed settings, then verify on a test machine with `claude --debug`.
- [[Patterns Playbook]] (developing, evidence-based): Twenty-five reusable shapes, plus one structure pattern, for Claude Code mods on 2.1.288, each tied to an official example, or Anthropic's own mod code.
- [[Pitfalls Playbook]] (developing, evidence-based): The failure that matters most in mods is silent: a hook that throws, times out, or returns the wrong shape is skipped and the session carries on as if the mod were not there (docs-mods-troubleshoot).
- [[Ranked Build Ideas]] (developing, practitioner): The seed report ranked eight ideas by time saved, with post-turn-verify first (compass-report L380-391).
- [[Testing Playbook]] (developing, evidence-based): Test a mod in four layers: plain unit tests for pure functions, kit tests that fire events through the hooks with stubs standing for Claude Code, drawing tests that mount a render site on more than one surface, and polic...

## Entities (13)

- [[Arunjay4213 claude-mods]] (developing, evidence-based): Arunjay4213/claude-mods is a marketplace of four small session trackers built as mods: context-lens, quota-meter, token-ledger and budget-guard (C-ECO-031).
- [[Built-in agents-md Mod]] (developing, evidence-based): Claude Code reads `AGENTS.md` through a built-in mod, `cc-plugin-agents-md`, configured by one option, `instructionFiles` (C-ECO-006).
- [[Built-in diff Mod]] (developing, evidence-based): `/diff` in Claude Code 2.1.287+ is drawn by a built-in mod, listed in `/plugin` as `cc-plugin-diff`.
- [[Built-in sec-default Mod]] (developing, evidence-based): sec-default is the built-in guard Claude Code seats first in the prepend tier on machines with managed settings or for Team and Enterprise organizations.
- [[Built-in telemetry Mod]] (developing, evidence-based): The telemetry mod (`cc-plugin-telemetry`) implements `$.telemetry.log` and `$.telemetry.mark` for Claude Code and its built-in mods, adding the noun in the `engine.create` fold and sending batched first-party analytics r...
- [[Mod Directories]] (developing, evidence-based): Five public lists catalogue community mods.
- [[OneWave claude-code-mods]] (developing, evidence-based): OneWave-AI/claude-code-mods is ten mods "built in one night" by OneWave AI, MIT licensed, with tests for each and a "mix of useful and ridiculous" tone (C-ECO-043).
- [[Playground Sample Mods]] (developing, evidence-based): Anthropic's DevRel team publishes three unsupported sample mods in `anthropics/claude-code-playground/claude-code/mods`: token-weather (a band), blast-radius (a tool-call hold with a pane) and replay-theater (a slash com...
- [[cc-pr-tracker]] (developing, evidence-based): cc-pr-tracker watches GitHub pull requests from inside a session: paste a PR URL and it gets one line above the prompt with merge state, review decision and required checks, refreshed every minute, with a toast, a flash ...
- [[cctop]] (developing, evidence-based): cctop is a btop-style dashboard for a running Claude Code session: context fill and time to autocompact, tokens and cost with cache-hit ratio, rate limits with an exhaustion forecast, per-tool latency, subagents, touched...
- [[code-modernization Plugin]] (developing, evidence-based): code-modernization 1.0.0 is Anthropic's legacy-modernization plugin in the official marketplace (`claude-plugins-official`).
- [[hamzafer claude-code-mods]] (developing, evidence-based): hamzafer/claude-code-mods is a personal collection of 13 mods (bands, guards, panes and two games) published as one marketplace (C-ECO-040).
- [[karanb192 claude-code-mods]] (developing, evidence-based): karanb192/claude-code-mods is a marketplace with one skill and two mods: `mod-builder` (a skill that plans a mod's "capability budget", validates it, and writes a five-line threat model), `fable-pin` (a 36-line mod that ...

## Platforms (1)

- [[Claude Code Release Channels]] (developing, evidence-based): Claude Code ships on two update channels, `latest` (default) and `stable` (about a week behind, skipping releases with major regressions), selected by `autoUpdatesChannel` (C-ECO-053).

## Reports (3)

- [[API Drift 2.1.288 to 2.1.288]] (evergreen, evidence-based): Generated by `scripts/diff_api_surface.py` on 2026-10-03: names (events, `$` members, render components, elements, exported types), declaration signatures, and every limit-bearing line of the generated typings, compared ...
- [[API Surface 2.1.288]] (evergreen, evidence-based): Generated from the typings Claude Code 2.1.288 wrote for a mod (`claude-code/index.d.ts`, 14973 lines, sha256 `d0531eb1b9f9a05f...`).
- [[Mod Audit code-modernization]] (evergreen, practitioner): Static footprint of `code-modernization` 1.0.0 (claude-plugins-official@d182ca4 plugins/code-modernization).

## Decisions (2)

- [[Read Only Audit Decision]] (developing, evidence-based): **Decision:** audits of third-party mods in this brain are static and read-only.
- [[Version Pin Policy]] (developing, evidence-based): Decision: every published mod pins a semver `version` in `plugin.json` only (never also in the marketplace entry), bumps it on every release, records the Claude Code build it was tested on in its README and CHANGELOG, an...

## Sources (3)

- [[Contradictions Register]] (evergreen, evidence-based): Every place where two sources disagree, with the evidence on each side and which one wins, as recorded by the five research lanes on 2026-10-03.
- [[Source Manifest Guide]] (developing, evidence-based): Four records hold this brain's provenance, each answering one question.
- [[research-pack-claude-mods|Research Pack: Claude Code Mods]] (evergreen, evidence-based): The dated citation index for this brain, generated on 2026-10-03 from `references/source-ledger.json` (50 public sources), the local captures list (4), and every #91870 comment the vault cites (36).

## Gaps (3)

- [[Evidence Coverage Not Yet Verified]] (developing, evidence-based): On 2026-10-03 the claim ledger holds 301 claims across five lanes.
- [[Mods API gaps requested in the 91870 thread but not shipped]] (developing, practitioner): The #91870 design thread (opened 2026-09-03, 235 comments, launch announced 2026-10-01) holds about 25 groups of API requests; @poteat is the only Anthropic staff commenter (pa-gh-91870-mined).
- [[Unverified pre-release security findings on current builds]] (developing, contested): Pluto Security tested mods on pre-release Claude Code 2.1.274 (published 2026-09-22).

## Questions (3)

- [[Does claude plugin test support userConfig values yet]] (developing, evidence-based): Yes, on 2.1.288 according to the generated typings: `test` takes an options object before the body, and its `options` field holds "the plugin under test's `userConfig` values, standing as the ones stored in settings" (ty...
- [[How is $.model.classify billed]] (developing, practitioner): Short answer: `$.model.classify` is one `$.model.complete` call in disguise, so it is billed exactly like `$.model.complete`: to the user's own plan or API key through the session's own API client, on the engine's small ...
- [[What Current Official Source Resolves The Highest Risk Claim]] (developing, evidence-based): Answer: there is no single source.

## Experiments (2)

- [[Diff generated typings across two Claude Code versions]] (developing, evidence-based): The experiment detects mods API drift between Claude Code releases by importing the typings each version writes beside a mod and diffing the two surfaces.
- [[Source To Claim Spot Check Probe]] (developing, evidence-based): This probe asks whether ledger claims actually trace to the captures they cite.

## Meta (9)

- [[Answer Engine Citability Policy]] (seed, practitioner): Confidence tag: practitioner.
- [[CONVENTIONS]] (evergreen, practitioner): This is the master vault operating contract.
- [[Corpus Scope Policy]] (seed, practitioner): Confidence tag: practitioner.
- [[Memory Governance Policy]] (seed, practitioner): Confidence tag: practitioner.
- [[Provenance Trace Policy]] (seed, practitioner): Confidence tag: practitioner.
- [[Start Here]] (active, practitioner): This vault is a source-cited brain for Claude Code mods, tested on Claude Code 2.1.288.
- [[Tag Taxonomy]] (evergreen, practitioner): Lowercase hierarchical tags govern graph colors, Dataview filters, and note maintenance.
- [[Uncertainty Eval Policy]] (seed, practitioner): Confidence tag: practitioner.
- [[dashboard|Dashboard]] (evergreen, practitioner): Dataview views over the vault require the Dataview community plugin.

## Canvases (2)

- [Event Flow Map](canvases/Event%20Flow%20Map.canvas) (active, practitioner): Obsidian canvas.
- [Mod Lifecycle Map](canvases/Mod%20Lifecycle%20Map.canvas) (active, practitioner): Obsidian canvas.
