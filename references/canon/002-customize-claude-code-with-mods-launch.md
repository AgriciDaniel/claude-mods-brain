---
title: "Customize Claude Code with mods"
author: "Anthropic"
publisher: "Anthropic (claude.com blog)"
year: "2026"
date: "2026-10-01"
url: "https://claude.com/blog/claude-code-mods"
source_capture: ".raw/captures/web-2026-10-03/blog-mods-launch.txt"
retrieved: "2026-10-03"
confidence: "evidence-based"
tags:
  - "#domain/claude-code-mods"
  - "#type/canon"
  - "#source/official"
  - "#confidence/evidence-based"
---

# "Customize Claude Code with mods" (Anthropic, 2026-10-01)

The launch announcement, filed under Product announcements with a 5 minute reading time. No individual author is named in the capture, so the author is the company. It is short (about 30 lines of body text) and positions mods for three audiences: individual developers, people who want to swap built-in features, and team or enterprise admins.

## Core Thesis

Mods are small TypeScript functions that change how Claude Code works, and they close the gap that settings hooks left open. Hooks could gate and log; mods can also rewrite events, draw new UI, and replace built-in features. Anthropic frames this as making Claude Code "feel like yours" while keeping distribution and governance inside the existing plugin system, and it states the trust cost plainly: mods are unsandboxed code with Claude Code's own access.

## How It Works

The post teaches a one-paragraph model:

- Each time Claude Code does something (call a tool, ask for permission, draw part of the screen), it emits an event.
- A mod is a function hooked into one event. It can run before, after, or instead of the event, or wrap it (code before and after).
- With one function a mod can rewrite a prompt before it reaches the model, block, rewrite, or retry a tool call, approve or deny a permission request, or redact secrets from tool output before Claude reads it.
- A mod can also edit or replace parts of the interface (a tool result, a question from Claude), add buttons and inputs, and other mods can respond to presses.
- Stacking: when several mods hook one event they run in load order, first loaded sees the event first and the result last.
- Claude Code can write a mod for you, install it, and hot reload it in the session.
- Mods ship inside plugins, so install, share, and admin controls are the plugin ones. Today a mod can target the terminal, the desktop app, or both.

## Key Principles

1. Extensibility without waiting for Anthropic: the stated motivation is user control "without waiting for us to ship a feature".
2. Built-ins become replaceable: `/diff` is now a mod you can disable in `/plugin` or replace, and more built-ins will move to mods over time.
3. Onion ordering enables composition across authors.
4. Same trust model as installing any code: only install from sources you trust.
5. Governance reuses plugin controls: marketplace allow and block lists (admin console on Team and Enterprise, managed settings on API and third-party plans).
6. A built-in guard, `sec-default`, loads first on Team and Enterprise plans and any machine with managed settings, and stops user mods from risky things such as overriding permission deny rules.
7. Admins can load their own mods first; if they do, they must add `sec-default` to their list to keep its restrictions.

## Best Practices

- Treat a mod install like installing any program: trusted sources only, read before you install. EVIDENCE-BASED
- When replacing a built-in such as `/diff`, disable the built-in in `/plugin` first, then load yours. EVIDENCE-BASED
- When an org prepends its own mods, list `sec-default@builtin` in the same `prependPlugins` list, or the guard stops loading. EVIDENCE-BASED
- Use a first-loaded org mod for audit logging of every call other mods make. PRACTITIONER
- Good first team mods per the post: a CI/CD status pane, a confirmation guard before commands touch production config, an audit logger. PRACTITIONER
- Distribute a finished mod as a plugin and submit it to the Claude directory rather than sharing loose files. PRACTITIONER

## Verified Quotes

- "Mods run with the same access to your machine as Claude Code itself." (intro, paragraph 2)
- "hooks can't rewrite events, draw new UI, or replace features. Mods can." ("Why we built mods")
- "The first mod to load sees the event first and the result last." ("How mods work")
- "the built-in /diff feature is now a mod" ("Swap built-in features for your own")
- "pare Claude Code down to a small core" ("Swap built-in features for your own")

## Evidence Caveats

- Marketing compression: "they run in the order they load" is a simplification. The docs order mods by tier first (guard and org prepend, user, org append, built-in), then by `dependencies`, then by `on` call order (docs-mods-events). Load order alone is not the rule.
- "Approve or deny a permission request": true, but where the guard loads a user mod cannot approve a call a `deny` rule refuses unless `allowModsToOverrideDenyRules` is set (docs-mods-admin). The post mentions the guard but not this exception's switch.
- "Redact secrets from tool output before Claude reads it" is accurate as a capability, but the #91870 thread notes the redaction hides output from other mods only when the redacting mod sits at the bottom of the chain (org `appendPlugins`), because every mod above it receives the result after it. A user-tier redactor protects Claude, not the mods below it. See 004.
- The post says nothing about where drawing does not appear (VS Code chat panel, `claude -p`, cloud sessions); the docs' "Where mods run" table does.
- Admin console and plan details are product claims; this lane did not verify them against a live admin console.
- No author byline in the capture; page chrome (related posts, newsletter form) was stripped from consideration.

## Brain Hooks

- [[Mods vs Classic Hooks]]: the post's one-line contrast is the canonical framing.
- [[Hook Middleware Chain]]: before, after, instead, wrap.
- [[Hook Ordering and Tiers]]: "first loaded sees first, result last" with the tier correction above.
- [[Built-in diff Mod]] and [[Built-in sec-default Mod]]: the two built-ins the post names.
- [[Mods Trust Model]]: "not sandboxed, install from trusted sources".
- [[Org Mod Controls]] and [[Org Mod Policy Guide]]: plugin controls apply, prepend with `sec-default`.
- [[Marketplaces and Distribution]]: ship inside plugins, submit to the directory.
- [[Ranked Build Ideas]]: CI/CD pane, production safeguard, audit logger as seeded team ideas.
- [[Claude Code Release Channels]]: launch date anchor of 2026-10-01 for v2.1.287.
