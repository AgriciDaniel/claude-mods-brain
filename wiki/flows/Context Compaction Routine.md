---
type: "flow"
title: "Context Compaction Routine"
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
  - "[[Turn and Session Events]]"
  - "[[Mods API Namespaces]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Budgets and Limits]]"
  - "[[State Store and Module Variables]]"
  - "[[Classic Hook Bridge]]"
  - "[[Memory Governance Policy]]"
  - "[[Start Here]]"
  - "[[Multi-Agent Fan-Out Research Flow]]"
  - "[[Mods API gaps requested in the 91870 thread but not shipped]]"
  - "[[Mod Catalog]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)"
sources:
  - "docs-mods-reference"
  - "docs-mods-api"
  - "docs-mods-events"
  - "docs-hooks"
  - "types-2-1-288"
---

# Context Compaction Routine

An agent working this brain keeps its context lean by reading in a fixed order: `wiki/hot.md` first, then `wiki/index.md`, then only the notes the task names, and never whole raw captures (the typings file alone is 14,973 lines, `hooks.md` is about 248 KB). When compaction does happen, it runs through the mods chain: any loaded mod hooking `session.compact` can rewrite what the summarizer is told, swap the messages, or veto it. A personal handoff mod reviewed for this brain, for example, saves a snapshot and appends its preservation rules to every real compaction.

## Trigger

- Starting any task in this vault (the read order applies from the first message).
- The context meter passes about 70 percent, or a long research step is about to begin.
- Claude Code compacts on its own (`trigger: 'auto'`) or the user types `/compact`.

## Prerequisites

- The spine notes exist: `wiki/hot.md`, `wiki/index.md`, [[Start Here]], `wiki/meta/CONVENTIONS.md`.
- `sed -n '/^## Next Action/,/^## /p' wiki/hot.md` prints the `## Next Action` section of `hot.md`, a one-line entry point.

## Steps

1. Orient in three reads, in this order, and stop as soon as the task is clear:

```bash
sed -n '/^## Next Action/,/^## /p' wiki/hot.md
sed -n '1,80p' wiki/hot.md
grep -n "\[\[" wiki/index.md | grep -i "<topic>"
```

2. Open only the named notes. Prefer the section you need: `grep -n "^## " "wiki/concepts/Budgets and Limits.md"`, then `sed -n` that range.

3. Read raw evidence by line range, never whole. The public repo ships no `.raw/` captures; this assumes you captured your own typings into `.raw/` ([[Research Refresh Workflow]]):

```bash
F=.raw/captures/types-2.1.288/claude-code/index.d.ts
grep -n "export type SessionCompactInput" "$F"          # L10110
sed -n '10105,10150p' "$F"
```

4. Delegate wide reads. A sweep over the 235-comment #91870 capture or ten repos goes to a subagent that returns conclusions with citations, the same pattern as [[Multi-Agent Fan-Out Research Flow]].

5. Before compacting, write state to the vault, not to the conversation: a line in `wiki/log.md`, the current step in `wiki/hot.md` (follow [[Memory Governance Policy]]). Then compact with explicit instructions:

```text
/compact keep: task, files touched, claim ids changed, open questions; drop: file dumps
```

6. After compaction, re-read `hot.md` only, then continue.

## When a mod's session.compact hook matters

Compaction is an event, so mods see it. Facts from the 2.1.288 typings and reference:

| Fact | Source |
|---|---|
| Triggers: `manual` (`/compact`), `auto` (threshold or prompt too long), `plugin`, `precompute` | types 2.1.288 L10165-10171 (C-API-036) |
| Rewrite `instructions` with `next({ ...e, instructions })`, or `messages` | types 2.1.288 L10110-10145 |
| Answer `{ skip: reason }` to veto; the conversation stays and one line says why | types 2.1.288 L10150-10159; docs-mods-reference |
| `agentId` is set when a subagent's own transcript compacts | types 2.1.288 L10116-10125 |
| `precompute` installs nothing; its result is kept for the next compaction | types 2.1.288 L10165-10170 |
| A classic `PreCompact` hook that blocks makes core answer `{ skip }` | types 2.1.288 L10153-10155 |
| `$.session.compact({ instructions })` compacts between turns as trigger `plugin`; rejects while a turn runs | types 2.1.288 L2659-2670 |
| `$.session.usage()` gives `context` figures at no cost; the example compacts at 85 percent | types 2.1.288 L2625-2642 |

What this means in practice:
- **Your `/compact` text is not the last word.** A mod can append its own rules after yours on every non-`precompute` main-thread compaction; the handoff mod reviewed for this brain did exactly that with a `PRESERVE` block, and saved a snapshot first. If a summary keeps things you asked it to drop, check which mods hook `session.compact`. EVIDENCE-BASED
- **A veto looks like a failed compaction.** A mod returning `{ skip }`, or a classic `PreCompact` block, leaves the context full with one notice line. Read the notice before retrying. EVIDENCE-BASED
- **Usage meters hook it too.** cctop, Arunjay4213's context-lens and karanb192's cache-tax all list `session.compact` among their events ([[Mod Catalog]]). Observing is harmless; rewriting is what changes your summary. PRACTITIONER
- **Subagent compaction is out of reach for plugins.** The event carries `agentId`, but `SessionCompactArgs` holds only `instructions` (types 2.1.288 L10059-10065, C-PAT-045), so a mod cannot start a subagent's compaction. EVIDENCE-BASED

## Outputs

- A short working set: hot, index, the named notes, and cited line ranges.
- Vault-side state (`hot.md`, `log.md`) that survives compaction.

## Gates

- The agent cites notes and line ranges, not pasted captures. PRACTITIONER
- After compaction, the next action in `hot.md` still matches the task. PRACTITIONER

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Context fills during the first task | Whole captures or whole notes opened | Steps 2 and 3: section and line ranges only |
| Summary ignores your `/compact` focus | A mod rewrote `instructions` or `messages` | `/plugin` to see loaded mods; read their `session.compact` hooks |
| Compaction "does nothing" | A hook answered `{ skip }` or `PreCompact` blocked | Read the notice; disable the mod for the session if needed |
| `$.session.compact` rejects | Called while a turn runs | Call from a command or between turns |

## Rollback

Compaction cannot be undone inside a session; the vault is the recovery path. Re-read `hot.md` and the log, or resume from a handoff file if a handoff mod saved one. To stop a mod rewriting compactions, disable it in `/plugin`.

## Caveats

- Whether `precompute` dispatches are frequent enough to matter was not measured.

## Related

Event details: [[Turn and Session Events]]; the `$.session` calls: [[Mods API Namespaces]]; why tail context beats prefix edits: [[Prompt Cache Discipline]]; the 1.5 s `session.end` bound: [[Budgets and Limits]]; state that survives reloads: [[State Store and Module Variables]]; the `PreCompact` bridge: [[Classic Hook Bridge]]; subagent compaction gap: [[Mods API gaps requested in the 91870 thread but not shipped]].

## Sources

- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-hooks: https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
