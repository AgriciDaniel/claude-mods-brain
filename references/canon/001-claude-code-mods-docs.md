---
title: "Claude Code mods documentation set"
author: "Anthropic"
publisher: "Anthropic (code.claude.com)"
year: "2026"
date: "unknown"
url: "https://code.claude.com/docs/en/plugins/mods/overview"
source_capture: ".raw/captures/docs-2026-10-03/plugins-mods-*.md"
retrieved: "2026-10-03"
confidence: "evidence-based"
tags:
  - "#domain/claude-code-mods"
  - "#type/canon"
  - "#source/official"
  - "#confidence/evidence-based"
---

# Claude Code mods documentation set (Anthropic, 2026)

Ten official pages, captured verbatim on 2026-10-03: overview, create, interface, gallery, events, api, test, troubleshoot, admin, reference. Each is cited as https://code.claude.com/docs/en/plugins/mods/<page>. The reference page describes the surface "as of v2.1.287". No page shows a publish date, so `date` is unknown.

## Core Thesis

A mod is a plugin whose hooks module exports `register(on, options)`. The functions it registers run inside Claude Code's own process, sit in a middleware chain in front of Claude Code's behavior, and reach the outside world only through the `$` mods API. That design makes mods more powerful than settings hooks (they can draw, rewrite events, add commands and tools), and it also makes them statically inspectable: `claude plugin validate` can list every event and every `$` call without running the code. Mods are not sandboxed. They run as the user (overview, admin).

## How It Works

- **Files** (reference#files): `.claude-plugin/plugin.json` (no new required fields), `hooks/hooks.json` with `"modules": ["./register.js"]` (one path; the key is what makes the plugin a mod), and the hooks module as an ES module in `.js/.mjs/.cjs/.jsx/.ts/.mts/.cts/.tsx`. A `types/index.d.ts` named by the manifest `types` field is required when the mod uses `$.state` or adds a namespace.
- **Hook signature** (reference#the-hook-function): `on(event, matcher?, async ($, e, next) => ...)`. `e` is deeply frozen plain data. `next(e)` runs later hooks then Claude Code's behavior. `next` also carries `signal`, `origin` (`{ plugin, tier }`), `budget`, and `to(e, tier)`. `on(...)` returns a registration with `.catch(handler)`.
- **Three moves** (events): Observe (return `next(e)`), Rewrite (call `next` with a changed copy, or change the result), Answer (return a result without calling `next`, which short-circuits later mods and Claude Code).
- **Event families** (reference#events): tools (`tool.call`, `tool.check`, `tool.describe`), prompts (`prompt.submit`, `prompt.section`, `prompt.context`, `prompt.attachment`, `skill.prompt`), commands and config, turns (`turn.start`, `turn.step` as async generator, `turn.complete`), session (`session.start`, `session.end`, `session.append`, `session.send/receive`), subagents, interface (`ui.render`, `ui.press`, etc.), other mods (`plugin.register`, `engine.create`), telemetry, `classic.<Event>` for every settings hook event, and every `$` method as its own event (`fs.read`, `model.complete`).
- **Order** (events#the-order-mods-run-in): built-in guard `sec-default@builtin` plus org `prependPlugins` and other org mods, then user-installed mods, then `appendPlugins`, then other built-in mods. Among user mods, a mod runs before its declared `dependencies`. Within one module, in `on` call order.
- **Settings hooks in the chain**: managed `PreToolUse` hooks run before the first mod and their block is final. Other `PreToolUse` hooks run after the last mod calls `next`. `tool.check` fires after rules and settings hooks decided.
- **Failure** (events#handle-a-hook-that-fails): a hook that throws, times out, or returns a bad shape before calling `next` is skipped (fail open). After `next` resolved, that result stands. `.catch` lets a guard fail closed.
- **Dev loop** (create): `claude --plugin-dir ./mod` hot-reloads on save; each reload reruns `register` and `session.start`. Claude Code writes `.claude-plugin/types/` declarations for the running build. `claude plugin test` runs `*.test.ts` with no session, sign-in, or network.

## Key Principles

1. Everything outside the module goes through `$`. The module has no Node APIs, no timer globals, no ambient file or network access (api#reach-files-processes-and-the-network).
2. Static analysis is a contract. Write `$.ns.method(...)` in full, use string-literal event names, never alias `$`, no dynamic `import()`. Claude Code refuses a module it cannot read (create, admin).
3. The first mod is outermost and controls whether later mods run (events).
4. Generated types beat prose. The docs say the types for your build win when they disagree with any page (create).
5. State has three lifetimes: module variable (until reload), `$.state` (until session end, `/clear`, `/resume`, `/branch`; survives reload; reactive), `$.store` (persistent JSON, 4 MiB total, shared by every session on the machine) (interface#keep-state).
6. Hooks have a 10 s budget for their own execution. Time inside `next` or a `$` call does not count, except `$.clock.sleep` (reference#limits).
7. Drawing is narrower than hooking: hooks run in `claude -p`, the SDK, and VS Code chat, but only the terminal and Desktop Code tab draw (overview#where-mods-run).
8. A mod can approve tool calls and so can bypass `ask` rules and non-managed `PreToolUse` blocks. Where the guard loads, `deny` rules and managed hooks still win (admin).

## Best Practices

- Run `claude plugin validate --strict` before every commit and read the `hooks:`, `calls:`, `env reads:`, and `state writes:` lines. EVIDENCE-BASED
- Put guards on `tool.check` when the decision depends on live state, and use permission rules for fixed commands. EVIDENCE-BASED
- Add `.catch` returning `{ deny }` to every blocking hook so a crash fails closed. EVIDENCE-BASED
- Hold a tool call inside a `$` call such as `$.ui.ask`, never a promise of your own, or the 10 s budget skips the hook and the held command runs. EVIDENCE-BASED
- Register commands last in `session.start`, or wrap `$.command.register` in try/catch: a taken name throws and skips the rest of the hook. EVIDENCE-BASED
- Keep drawing state in `$.state` and cross-session data in `$.store`, not module variables. EVIDENCE-BASED
- Check `e.props.bodyColumns` and `isPlaced` and fall back from pane to band or `$.ui.status` where nothing draws. EVIDENCE-BASED
- Write `deny` text as an instruction Claude can act on, since Claude reads it as the tool result. EVIDENCE-BASED
- State the tested Claude Code version in the README, because events and methods can change between releases. EVIDENCE-BASED

## Verified Quotes

- "Mods aren't sandboxed." (overview, "What a mod can reach"; repeated on admin)
- "A mod can restyle much of Claude Code's interface, but not the permission prompt" (overview, "What a mod can reach")
- "trust these files over any page, this one included, when they disagree" (create, "Get type definitions for your version")
- "it sees the event before the others and the result after them" (events, "The order mods run in")
- "Without the handler, Claude Code would skip `guard` and run the command." (events, "Handle a hook that fails")
- "so write it as an instruction Claude can act on" (events, "Guard or change a tool call")

## Evidence Caveats

- Version sensitivity: the set describes v2.1.287. The lead's installed build is 2.1.288; the docs themselves defer to `.raw/captures/types-2.1.288/`. Re-check every signature against the typings before relying on it.
- The built-in guard only loads on a machine with managed settings or for a Team or Enterprise sign-in. Personal API-key users get no deny-rule protection from mods (admin).
- Deny rules do not cover a mod's own `$.fs` and `$.process` calls. With `Read(.env)` denied, a mod can still read `.env` (admin).
- Network policy covers `$.http.fetch` but not a program started with `$.process.run` (admin).
- Pages do not mention `next.trace`, which the #91870 thread described as planned. Treat it as unshipped unless the typings show it.
- Gallery and interface pages were skimmed for headings and state rules, not read line by line for every element prop.

## Brain Hooks

- [[Mod Anatomy]]: files, `register(on, options)`, the `modules` key.
- [[Hook Middleware Chain]] and [[Observe Rewrite Answer]]: the three moves and `next` semantics.
- [[Hook Ordering and Tiers]]: guard, prepend, user, append, built-in, and where settings hooks sit.
- [[Tool Events]], [[Prompt Events]], [[Turn and Session Events]], [[Agent and Command Events]]: event tables.
- [[Render Sites]] and [[UI Elements and JSX]]: site table, element table, terminal-only elements.
- [[Mods API Namespaces]] and [[Mods API Cheatsheet]]: the 21 namespaces in the reference table.
- [[State Store and Module Variables]] and [[Budgets and Limits]]: lifetimes and the limits table.
- [[Plugin Validate]], [[Testing Kit]], [[Hot Reload and Dev Loop]]: the inspection and test loop.
- [[Org Mod Controls]] and [[Built-in sec-default Mod]]: managed settings and guard options.
- [[Holding a Tool Call]] and [[Band and Pane Fallback]]: documented patterns.
