---
type: "flow"
title: "Explore Plan Code Commit"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/flow"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "rewrite"
related:
  - "[[Mod Anatomy]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Budgets and Limits]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Plugin Validate]]"
  - "[[Testing Kit]]"
  - "[[Testing Playbook]]"
  - "[[Pitfalls Playbook]]"
  - "[[Ranked Build Ideas]]"
  - "[[State Store and Module Variables]]"
  - "[[Publish a Mod Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)"
sources:
  - "docs-mods-create"
  - "docs-mods-reference"
  - "docs-mods-events"
  - "docs-mods-api"
  - "docs-mods-test"
  - "types-2-1-288"
---

# Explore Plan Code Commit

Explore, plan, code, commit applied to a mod means: read the generated typings and the docs before writing anything, plan which events the mod hooks and how much of each budget it spends, code it in a folder you own with `claude --plugin-dir` only once the owner has approved that load, prove it with `claude plugin validate --strict` and `claude plugin test`, then commit with the tested-on version. The worked example is rank 1 in [[Ranked Build Ideas]], post-turn verify, added to a mod you already own or built as its own small mod.

## Trigger

- A build idea reaches "build" in [[Ranked Build Ideas]].
- You want a new mod or a change to one you own.

## Prerequisites

- Approval from the mod's owner for any change to a mod repo; an agent working from this brain never edits a mod repo unasked.
- Claude Code 2.1.287 or later (mods on by default, docs-mods-overview); this note was written against 2.1.288.
- TypeScript 5.4 or later for `tsc -p .` (typings header).

## Steps

### 1. Explore (read only)

```bash
head -1 <mod>/.claude-plugin/types/claude-code/index.d.ts      # which build wrote these
grep -n "'turn.complete'\|export type TurnCompleteResult" <mod>/.claude-plugin/types/claude-code/index.d.ts
grep -n "process.run" .raw/docs/api.md                          # your own capture of the mods API docs page
```

Facts this example needs, each from rank 1 sources:
- `turn.complete` answers `next(e)` or `{ text }` to show a line under the answer (docs-mods-reference; types 2.1.288 L12546-12549). `e.reason` is `answer`, `aborted`, `refusal` or `error`, and `e.agentId` is set for a subagent's turn.
- `$.process.run(argv, { cwd?, timeoutMs? })` uses no shell, resolves `{ exitCode, stdout, stderr }`, and rejects past its timeout, 30 s by default (docs-mods-api; types 2.1.288 L3307, L7538-7565).
- A hook has 10 s of its own time per dispatch, but the clock stops while a `$` call is in flight, so a long `$.process.run` does not spend it (C-API-012).

### 2. Plan

Write the plan as a table before any code:

| Concern | Decision |
|---|---|
| Events | `tool.call` on Edit and Write (observe after `next`), `turn.complete` (main thread, `reason === 'answer'`) |
| `$` calls | `$.process.run` only; no `$.model.*`, no `$.prompt.submit` (zero usage cost) |
| Budget | Checks run inside `$.process.run` with `timeoutMs: 120000`; hook time stays under 1 s |
| Failure | `try/catch` around the run; on error, return the plain result (fail quiet: this is a report, not a guard) |
| State | Edited paths in `$.state`, not module variables (Pitfalls S1) |
| Feedback to Claude | Optional `classic.Stop` `{ block }` on failure, once per turn |

### 3. Code (after owner approval)

A sketch of the core hook, to be type-checked against the generated typings:

```ts
on('turn.complete', async ($, e, next) => {
  const result = await next(e)
  if (e.agentId || e.reason !== 'answer' || edited.size === 0) return result
  try {
    const r = await $.process.run(['npx', 'tsc', '--noEmit'], { timeoutMs: 120_000 })
    if (r.exitCode === 0) return result
    return { ...result, text: `${result.text}\nverify: tsc failed (${r.stdout.split('\n').length} lines)` }
  } catch {
    return result
  }
})
```

Run the dev loop in the owned folder only. Each save hot-reloads the module and rewrites `.claude-plugin/types/` (docs-mods-create, C-LIF-042):

```bash
claude --plugin-dir <owned-mod> --debug-file ./dev-debug.log
grep -E "loaded|hook skipped|refused" ./dev-debug.log
```

### 4. Prove

```bash
npx -p typescript@5 tsc -p <owned-mod>                          # validate does not check method names (Pitfalls L5)
claude plugin validate --strict --json <owned-mod>; echo "exit=$?"   # warnings are errors
cd <owned-mod> && claude plugin test                             # exit 1 on any failing *.test.ts
```

Add a test that fires `turn.complete` with and without edits; `claude plugin test` runs files ending in `.test.ts` or `.test.tsx` (docs-mods-reference).

### 5. Commit

```bash
git -C <mod-repo> add plugins/<your-mod>
git -C <mod-repo> commit -m "<your-mod>: post-turn verify (tested on Claude Code 2.1.288)"
```

Each fix or build lands as its own commit, and committing stays the owner's call.

## Outputs

- A plan table, a change in an owned mod, passing validate and test output, and a commit naming the tested-on build.

## Gates

- `head -1` of the typings names the running build. EVIDENCE-BASED
- `tsc -p` exits 0, `validate --strict` exits 0, `claude plugin test` exits 0. EVIDENCE-BASED
- The debug log shows a `loaded` line and no `hook skipped`. EVIDENCE-BASED
- No `$.model.*` or `$.prompt.submit` call added without saying so in the README. PRACTITIONER

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Line never appears | Hook skipped: threw or wrong shape | Read the debug log; return `{ text }` only |
| Verify runs on subagent turns | Missing `e.agentId` check | Return early when `agentId` is set |
| Edited set empty after a save | Module variables reset on hot reload | Keep it in `$.state` ([[State Store and Module Variables]]) |
| `hooks module did not load` | Top-level code threw | Move option parsing into try/catch (Pitfalls L3) |

## Rollback

Before commit: `git checkout -- plugins/<your-mod>` in the mod repo, or delete the scratch folder. After commit: `git revert <sha>`. A loaded dev session ends with `/exit`; nothing is installed.

## Caveats

- The snippet omits the `tool.call` collector and `$.state` wiring; it is a sketch, not shipped code.
- `classic.Stop` feedback is described in [[Ranked Build Ideas]] but not tested here.

## Related

Structure: [[Mod Anatomy]]; names and signatures: [[Mods API Cheatsheet]]; limits: [[Budgets and Limits]]; dev loop: [[Hot Reload and Dev Loop]]; checks: [[Plugin Validate]], [[Testing Kit]], [[Testing Playbook]]; traps: [[Pitfalls Playbook]]; release: [[Publish a Mod Flow]].

## Sources

- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-test: https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
