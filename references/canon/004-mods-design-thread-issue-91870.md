---
title: "Mods - make Claude 10x more extensible (design thread)"
author: "@poteat (Anthropic) and community commenters"
publisher: "GitHub, anthropics/claude-code issue 91870"
year: "2026"
date: "2026-09-03"
url: "https://github.com/anthropics/claude-code/issues/91870"
source_capture: ".raw/captures/web-2026-10-03/gh-issue-91870.md"
retrieved: "2026-10-03"
confidence: "practitioner"
tags:
  - "#domain/claude-code-mods"
  - "#type/canon"
  - "#source/primary"
  - "#confidence/practitioner"
---

# Mods design thread, anthropics/claude-code#91870 (opened 2026-09-03 by @poteat)

The public request-for-comment that became mods. The capture holds the issue body (original post of 2026-09-03, community updates of 2026-09-09 and 2026-10-01) and all 235 comments with author, timestamp, and comment URL. @poteat posted 34 of them. It is the best record of why the design looks the way it does, and of which ideas were proposed but may not have shipped.

## Core Thesis

Paraphrase: hooks should be TypeScript functions composed like Express or Koa middleware, with every side effect routed through a parameterized `$` object, so plugins can change Claude Code deeply while admins can audit, allowlist, deny, or log any effect. Ordering is configured, never self-declared, and the first registered plugin "owns" everything beneath it (the "onion model"). The product name "Claude Mods" was adopted on 2026-09-09; "function hook" stays as the implementation term.

## How It Works

The thread teaches the model through @poteat's answers, each citable by comment URL:

- **No ambient access, everything via `$`**: the restriction is not on what plugins may do but on how; admins hook `$` events to restrict (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5530356661).
- **Isolation is a boundary**: a Bun Worker around the plugin realm, a `node:vm` wrapper per plugin; only "no ambients" is contractual (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5546290346).
- **Answering a tool call**: when you hook `tool.call` you are responsible for calling the tool; `{ deny }` is what the model is told, and approval is computed as `result.deny === undefined`. Calling `next(e)` twice reruns the chain (retry) (same comment).
- **Permission prompt not hookable**: a surface declares which product components are wrappable, and the permission request component is not one of them (same comment).
- **Rewrites and caching**: when a `tool.call` hook changes content, the model still sees what it asked to write, for prompt caching reasons (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5531157307).
- **Failure semantics**: the engine skips a hook only when it throws, exceeds its time, or passes or returns a wrong shape (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5553458185). The `on(...).catch(...)` spelling was proposed to make fail-closed easy (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5588686533).
- **Tiers and skipping**: five tiers, `prepend`, `user`, `append`, `builtin`, `core`; `next.to(e, tier)` lets prepend mods skip lower tiers; `classic.*` wraps settings hooks 1:1 (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5574036379).
- **Deterministic order**: org-prepend, user, org-append, built-in; user order is a deterministic merge with dependency topo-sort; no numeric priorities (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5738020815, https://github.com/anthropics/claude-code/issues/91870#issuecomment-5638914414).
- **Concurrency**: start `next(e)` early without awaiting to overlap work; do it on `tool.check`, not `tool.call` (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5618866247).
- **Streaming**: `turn.step` hooks are async generators and the only hooks that yield (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5638914414).
- **Redaction position**: an org-appended mod sits at the bottom, so its redaction of a tool result is what every higher mod receives (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5560061162).

## Key Principles

1. Side effects are data: static analysis of `$` usage feeds `plugin.register`, so admins can refuse mods before they load (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5531699731).
2. Prepend for control, append for defaults (issue body, video 5 caption).
3. Mods cannot set their own order; admins and dependencies do.
4. Fail-closed is the author's job, by try/catch, `Promise.race` with a deadline, or `.catch`.
5. Prefer contractual interfaces over raw files (no transcript path reliance) (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5734700291).
6. Consent is given at install: limiting plugin power is the admin's prerogative, not Anthropic's.
7. `$.prompt.submit` is for text prompts only; run commands with `$.command.run` (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5607792448).

## Best Practices

- Put deadline logic inside your hook with `Promise.race` against `$.clock.sleep(8_000)` so an overrun becomes a denial, not a skip. PRACTITIONER
- Use `.catch` on blocking hooks rather than relying on engine fallback. EVIDENCE-BASED
- Put parallel guards on `tool.check`; keep `tool.call` for actually running or answering the tool. PRACTITIONER
- After rewriting a tool call, tell Claude what changed (the thread suggests extra context), since the model keeps its original view. CONTESTED
- Reach non-TypeScript policy engines through `$.process.run` or a local daemon over `$.http.fetch`. PRACTITIONER
- Place output redactors in org `appendPlugins` if other mods must not see the raw result. PRACTITIONER

## Verified Quotes

- "safe through side-effect tracking over a parameterized $ object" (issue body, original post, AI;DR)
- "everything goes through `$` so that admins can audit, allowlist, deny, log" (@poteat, comment 5530356661)
- "To make the tool not get called, don't call `next(e)`." (@poteat, comment 5546290346)
- "The model sees what it asked to write, for fundamental prompt caching reasons." (@poteat, comment 5531157307)
- "mods cannot dictate their own registration order, full-stop." (@poteat, comment 5738020815)
- "every 'numeric priority' system in the world has failed on this" (@poteat, comment 5738020815)

## Evidence Caveats

- Pre-contract statements. Many answers predate launch and use hedges ("I believe", "tbd", "in our internal prototype"). Shipped behavior is whatever docs-mods-* and the 2.1.288 typings say.
- **Superseded**: the early answer that an uncaught error makes the engine re-dispatch as if no plugins were registered (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5532500675) was replaced by per-hook skip semantics, which docs-mods-events now documents.
- **Superseded**: `fs.readFile` was renamed `fs.read`; `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` gating ended, and 2.1.287 ignores the variable (docs-mods-overview).
- **Unverified as shipped**: `next.trace` (comments 5541093682, 5739358814) is absent from the docs' `next` table; a `context` field on `tool.call` results is not in the reference; removal of a 512-file module link limit (@konsta95, https://github.com/anthropics/claude-code/issues/91870#issuecomment-5790602695, answered in https://github.com/anthropics/claude-code/issues/91870#issuecomment-5795711511). Check the typings.
- **Known regression**: @Und3rf10w reported `tool.call` hooks breaking worktree isolation for subagents on 2.1.287 (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5949411806); @poteat said it is fixed in v288 (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5961758416). Not independently verified.
- Cloud sessions: @poteat called cloud support in scope "asap" on 2026-10-01; docs list hooks running only for plugins that reach the cloud session, with no drawing.
- Most of the 235 comments are community proposals, not Anthropic commitments. Only @poteat comments are used here as design intent.

## Brain Hooks

- [[Hook Middleware Chain]] and [[Observe Rewrite Answer]]: Koa model, `next` twice, deny semantics.
- [[Hook Ordering and Tiers]]: five tiers, `next.to`, deterministic merge, no numeric priority.
- [[Mods Trust Model]] and [[Reach Levels]]: no ambients, consent at install.
- [[Org Mod Controls]] and [[Org Mod Policy Guide]]: `plugin.register` on static analysis, prepend and append roles.
- [[Classic Hook Bridge]] and [[Mods vs Classic Hooks]]: `classic.*` wrapping.
- [[Prompt Cache Discipline]]: model sees its original write.
- [[Holding a Tool Call]] and [[Build a Tool Call Guard Flow]]: `Promise.race` deadline, `.catch`.
- [[Versioning and API Drift]] and [[Re-verify After Release Flow]]: superseded names and the v288 fix.
- [[Turn and Session Events]]: `turn.step` streaming and `session.append` origin.
