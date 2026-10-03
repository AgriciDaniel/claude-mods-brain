---
type: "concept"
title: "Mods design thread, anthropics claude-code issue 91870"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/concept"
  - "#confidence/practitioner"
confidence: "practitioner"
lane: "rewrite"
related:
  - "[[Hook Middleware Chain]]"
  - "[[Observe Rewrite Answer]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Mods Trust Model]]"
  - "[[Classic Hook Bridge]]"
  - "[[Mods vs Classic Hooks]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Holding a Tool Call]]"
  - "[[Versioning and API Drift]]"
  - "[[Mods API gaps requested in the 91870 thread but not shipped]]"
  - "[[How is $.model.classify billed]]"
  - "[[Does claude plugin test support userConfig values yet]]"
source_urls:
  - "https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
sources:
  - "gh-issue-91870"
  - "pa-gh-91870-mined"
  - "docs-mods-events"
  - "docs-mods-overview"
  - "docs-mods-reference"
  - "types-2-1-288"
---

# Mods design thread, anthropics claude-code issue 91870

This note folds canon 004, the public request for comment that became mods, into the vault. Opened by @poteat (Anthropic) on 2026-09-03, it holds 235 comments to 2026-10-02, 34 of them from @poteat, each captured with author, timestamp and comment URL. It is the only canon work that explains why the design looks the way it does (the `$` contract, the onion, configured order, fail-open). Much of it predates launch, so use @poteat's answers as design intent and the docs plus 2.1.288 typings as shipped behaviour.

## What the work teaches

- **Everything through `$`.** No ambient access; admins restrict by hooking `$` events (comment 5530356661). The restriction is on how plugins act, not what they may do.
- **Isolation as a boundary.** A Bun Worker around the plugin realm and a `node:vm` wrapper per plugin; only "no ambients" is contractual (comment 5546290346).
- **Answering a tool call.** Hooking `tool.call` makes you responsible for calling the tool; `{ deny }` is what the model is told; calling `next(e)` twice reruns the chain (same comment).
- **Rewrites and caching.** The model keeps seeing what it asked to write (comment 5531157307).
- **Failure.** A hook is skipped only when it throws, overruns, or returns a wrong shape (comment 5553458185); `on(...).catch(...)` was proposed for fail-closed (comment 5588686533).
- **Tiers.** `prepend`, `user`, `append`, `builtin`, `core`; `next.to(e, tier)` lets prepend mods skip lower tiers; `classic.*` wraps settings hooks one to one (comment 5574036379).
- **Order is configured, never declared** (comment 5738020815).
- **Streaming.** `turn.step` hooks are async generators (comment 5638914414).
- **Measured cost of the chain.** Eight 300 ms function hooks took 2,427 ms in series against 640 ms as parallel command hooks on a pre-release build (@deafsquad, comment 5542444779; capture L2018-2019).

## How its claims map onto vault notes

| Thread claim | Claim IDs | Vault home | Status on 2.1.288 |
|---|---|---|---|
| `next(e)` twice reruns the tool | C-PAT-037 | [[Observe Rewrite Answer]] | verified in docs |
| `await next(e)` then `{ deny }` runs the tool anyway | C-PAT-036 | [[Holding a Tool Call]] | practitioner, consistent with docs |
| Wrong shape from `tool.call` is skipped | C-PAT-035 | [[Pitfalls Playbook]] | practitioner |
| Settings hooks parallel, chain serial | C-PAT-023, C-PAT-024 | [[Mods vs Classic Hooks]] | verified; timing is pre-release |
| `classic.<Event>` mirrors stdin JSON | C-PAT-019 | [[Classic Hook Bridge]] | verified |
| `.catch` instead of `onError` | C-PAT-054 | [[Hook Middleware Chain]] | verified |
| `session.append` instead of one global filter | C-PAT-055 | [[Turn and Session Events]] | verified |
| Installing is consent | C-SEC-056 | [[Mods Trust Model]] | SINGLE-SOURCE |
| `$` to a helper refused at load | C-PAT-060, C-SEC-008 | [[Plugin Validate]] | contradicted: 2.1.288 traces helpers |
| `$.model.complete` 256-token default (2.1.272) | C-PAT-034 | [[How is $.model.classify billed]] | contradicted: now 1024 default |
| `claude plugin test` cannot set userConfig (2.1.282) | C-PAT-029 | [[Does claude plugin test support userConfig values yet]] | contradicted by typings |
| Worktree isolation lost under `tool.call`, fixed in v288 | C-PAT-044 | [[Versioning and API Drift]] | SINGLE-SOURCE (staff word) |

## Agreement and contradiction

> [!contradiction] Uncaught errors. An early answer said an uncaught error re-dispatches as if no plugins were registered (comment 5532500675). Docs now document per-hook skip semantics (docs-mods-events). Docs win; the early answer is superseded.

> [!contradiction] Helpers and static analysis. A pre-release test said passing `$` to a helper refuses the load (comment 5542444779). On 2.1.288 a module calling `go($)` validates and reports `calls: $.http.fetch (via go)` (secgov-validate-probes, C-SEC-008). Current tool output wins.

- **Items once "planned", now shipped per typings:** `next.trace` (types 2.1.288 L6118-6200, C-API-014), a `context` field on `tool.call` results (L12019-12027, C-API-020), `$.ui.selection()` and `$.ui.panes()` (C-PAT-047), `$.session.messages({ agentId })` (C-PAT-048). The canon file lists `next.trace` and `context` as unverified; the typings resolve both as present.
- **Items requested but absent:** subagent compaction (`SessionCompactArgs` holds only `instructions`, C-PAT-045), `WebAssembly` in the module (deliberately absent, C-PAT-046). The full list is in [[Mods API gaps requested in the 91870 thread but not shipped]].
- **Renames:** `fs.readFile` became `fs.read`; `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` gating ended and 2.1.287 ignores the variable (docs-mods-overview L112).
- **Agrees with the docs** on tiers, deterministic order, the unhookable permission prompt, and fail-open. Agrees with Pluto ([[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]]) that consent is given at install, but draws the opposite conclusion: limiting power is the admin's job.

## Verified quotes

Copied from `references/canon/004-mods-design-thread-issue-91870.md`; each re-found verbatim in `.raw/captures/web-2026-10-03/gh-issue-91870.md`.

- "safe through side-effect tracking over a parameterized $ object" (issue body, capture L33)
- "To make the tool not get called, don't call `next(e)`." (@poteat, comment 5546290346, capture L2370)
- "The model sees what it asked to write, for fundamental prompt caching reasons." (@poteat, comment 5531157307, capture L517)
- "mods cannot dictate their own registration order, full-stop." (@poteat, comment 5738020815, capture L4883)

## What it gets wrong or leaves stale

- Hedged pre-contract answers ("I believe", "tbd", "in our internal prototype") read as commitments if quoted out of context.
- Version-pinned bug reports (2.1.260, 2.1.270, 2.1.272, 2.1.282) are mostly stale; C-PAT-029, C-PAT-034, C-PAT-060 are now contradicted.
- The worktree fix (C-PAT-044) rests on one staff comment ("This should be fixed as of today's release on v288", comment 5961758416); no test confirms it.
- Billing of `$.model.*` was asked directly and never answered (C-PAT-057, comment 5540419526).
- Most of the 235 comments are community proposals, not Anthropic commitments; only @poteat comments count as design intent here.

## How much to trust it

Confidence: practitioner. Rank 4 under the lane brief. It is the best evidence of intent and of real-world failure reports, and the worst evidence of current behaviour. Cite a specific comment URL every time.

- Use @poteat comments to explain why a rule exists, never as proof it still holds. PRACTITIONER
- Check any thread claim with a version number against [[API Surface 2.1.288]] before reuse. EVIDENCE-BASED
- Put deadline logic inside your hook with `Promise.race` so an overrun becomes a deny, not a skip. PRACTITIONER
- Place output redactors in org `appendPlugins` if other mods must not see raw results. PRACTITIONER

## Caveats

- The capture ends at 2026-10-02; later comments may revise answers.
- The mined subset (pa-gh-91870-mined) reflects one lane's selection.
- Version sensitivity: high; comments span pre-release builds to v288.

## Related

Mechanics: [[Hook Middleware Chain]], [[Observe Rewrite Answer]], [[Hook Ordering and Tiers]]. Trust: [[Mods Trust Model]]. Bridging settings hooks: [[Classic Hook Bridge]], [[Mods vs Classic Hooks]]. Caching: [[Prompt Cache Discipline]]. Holding: [[Holding a Tool Call]]. Drift: [[Versioning and API Drift]]. Open asks: [[Mods API gaps requested in the 91870 thread but not shipped]], [[How is $.model.classify billed]], [[Does claude plugin test support userConfig values yet]].

## Sources

- Canon file: `references/canon/004-mods-design-thread-issue-91870.md`
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (opened 2026-09-03, retrieved 2026-10-03), capture `.raw/captures/web-2026-10-03/gh-issue-91870.md`
- pa-gh-91870-mined: `.raw/captures/lanes-2026-10-03/patterns-and-ideas/gh-issue-91870-mined.md` (retrieved 2026-10-03)
- docs-mods-events, docs-mods-overview, docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/<page> (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` L6118-6200, L12019-12027
