---
type: "concept"
title: "Customize Claude Code with mods (Anthropic blog)"
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
  - "[[Mods vs Classic Hooks]]"
  - "[[Hook Middleware Chain]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Built-in diff Mod]]"
  - "[[Built-in sec-default Mod]]"
  - "[[Mods Trust Model]]"
  - "[[Org Mod Controls]]"
  - "[[Org Mod Policy Guide]]"
  - "[[Marketplaces and Distribution]]"
  - "[[Ranked Build Ideas]]"
  - "[[Claude Code Release Channels]]"
  - "[[Mods design thread, anthropics claude-code issue 91870]]"
source_urls:
  - "https://claude.com/blog/claude-code-mods (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
sources:
  - "blog-mods-launch"
  - "docs-mods-admin"
  - "docs-mods-events"
  - "docs-mods-overview"
  - "gh-issue-91870"
  - "types-2-1-288"
---

# Customize Claude Code with mods (Anthropic blog)

This note folds canon 002, Anthropic's launch post of 2026-10-01, into the vault. It is the shortest canon work (about 30 lines of body) and the one most people read first: mods are small TypeScript functions hooked into Claude Code's events that can rewrite, draw, and replace built-ins, distributed and governed as plugins. Its framing is accurate, but two compressions (load order, and what `sec-default` stops) mislead if taken literally, so every operational claim here routes to the docs.

## What the work teaches

- **The gap mods close.** Settings hooks could gate and log; mods also rewrite events, draw UI, and replace features. This is the canonical one-line contrast in [[Mods vs Classic Hooks]].
- **Event model.** Every action (tool call, permission request, drawing part of the screen) emits an event. A mod runs before, after, instead of, or around it. See [[Hook Middleware Chain]].
- **Single-function powers.** Rewrite a prompt before the model sees it; block, rewrite or retry a tool call; approve or deny a permission request; redact secrets from tool output.
- **Replaceable built-ins.** `/diff` is now a mod that can be disabled in `/plugin` and replaced, and more built-ins will move to mods ([[Built-in diff Mod]]).
- **Stacking.** Several mods on one event run in load order, first loaded sees the event first and the result last.
- **Authoring.** Claude Code can write, install, and hot reload a mod for you.
- **Governance.** Mods ship in plugins, so marketplace allow and block lists apply; `sec-default` loads first on Team and Enterprise or with managed settings; an org that prepends its own mods must list `sec-default` too.
- **Trust.** Mods run with Claude Code's own access; only install from trusted sources.

## How its claims map onto vault notes

| Blog claim | Claim IDs | Vault home | Status |
|---|---|---|---|
| Mods are unsandboxed, same access as Claude Code | C-SEC-001 | [[Mods Trust Model]] | verified (docs-mods-overview) |
| `/diff` is a mod; disabling leaves core `/diff` | C-ECO-005 | [[Built-in diff Mod]] | verified |
| Guard loads on Team, Enterprise, managed settings | C-SEC-018 | [[Built-in sec-default Mod]] | verified |
| Guard stops overriding deny rules | C-SEC-019, C-SEC-020 | [[Org Mod Controls]] | verified, but narrower than the wording implies |
| Prepend list must include `sec-default` | C-SEC-025 | [[Org Mod Policy Guide]] | verified |
| First loaded sees first, result last | C-API-007 | [[Hook Ordering and Tiers]] | true within a tier only |
| Ship as plugins, submit to directory | C-LIF-053 | [[Marketplaces and Distribution]] | directory needs paid plan (SINGLE-SOURCE) |
| Team ideas: CI/CD pane, prod guard, audit logger | none | [[Ranked Build Ideas]] | practitioner framing |

## Agreement and contradiction

> [!contradiction] What sec-default restricts. The blog says the guard stops user mods "doing risky things, like overriding your permission deny rules". The admin page lists exactly what it protects (managed hooks, system prompt, managed instructions, settings reads, managed MCP tools, deny rules) and states "The guard adds no other restrictions" (docs-mods-admin L65). The admin page wins: a user mod can still read, write, fetch, run processes, rewrite prompts, and approve calls an `ask` rule would prompt for (C-SEC-019, C-SEC-021).

> [!contradiction] Ordering. "The first mod to load sees the event first" is true inside one tier. The docs order by tier first (guard and org prepend, user, org append, built-in), then by `dependencies`, then by `on` call order (docs-mods-events). The #91870 thread adds that mods cannot set their own order at all (@poteat, comment 5738020815). Docs win.

- **Redaction position.** The blog lists redacting secrets from tool output. The design thread notes that only a redactor at the bottom of the chain (org `appendPlugins`) hides raw output from other mods, because every mod above receives the result after it ([[Mods design thread, anthropics claude-code issue 91870]], comment 5560061162). A user-tier redactor protects Claude, not the mods below it.
- **Where drawing appears.** The post says mods target terminal, desktop, or both. The typings already list `mobile` and `vscode` surfaces (types 2.1.288 L9695, C-API-049), while the docs say nothing draws in the VS Code chat panel (C-PAT-012). The blog predates neither claim but covers neither.
- **Agrees with Pluto** on the trust cost: Pluto's "untrusted binary" advice ([[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]]) is a sharper form of the blog's "trusted sources only".
- **Agrees with the plugins docs** ([[Claude Code plugins and hooks documentation (Anthropic)]]) that distribution and admin controls are the plugin ones.

## Verified quotes

Copied from `references/canon/002-customize-claude-code-with-mods-launch.md`; each re-found verbatim in `.raw/captures/web-2026-10-03/blog-mods-launch.txt`.

- "Mods run with the same access to your machine as Claude Code itself." (capture L9)
- "hooks can't rewrite events, draw new UI, or replace features. Mods can." (capture L13)
- "The first mod to load sees the event first and the result last." (capture L23)
- "the built-in /diff feature is now a mod" (capture L27)

## What it gets wrong or leaves stale

- Over-trust risk on the guard, as above. An admin who reads only the blog may assume the guard blocks exfiltration; it does not.
- No mention that personal API-key users get no guard without managed settings (C-SEC-018).
- No mention of the switch `allowModsToOverrideDenyRules` that loosens the deny-rule protection (C-SEC-020).
- No author byline; the company is the author. No version number in the body; the launch date anchors 2.1.287, published to npm 2026-10-01T16:59Z (eco-npm-dist-tags).
- Admin console and plan details are product claims this brain has not verified in a live console.

## How much to trust it

Confidence: evidence-based for what mods are and that they are unsandboxed; practitioner for the build ideas. It is rank 3 under the lane brief. Quote it for framing and motivation; never cite it alone for ordering, guard scope, or surfaces.

- Use the blog's one-line contrast when explaining mods versus settings hooks. EVIDENCE-BASED
- Cite docs-mods-admin, not the blog, whenever guard behaviour matters to a decision. EVIDENCE-BASED
- When replacing a built-in, disable it in `/plugin` first, then load yours. EVIDENCE-BASED
- Treat the CI/CD pane, production guard, and audit logger as seed ideas for [[Ranked Build Ideas]], not endorsed designs. PRACTITIONER

## Caveats

- Marketing compression is the main hazard; the facts it states are not wrong, only incomplete.
- Captured 2026-10-03 as plain text; page chrome was excluded.
- Version sensitivity: written for 2.1.287; the guard and surface claims were checked against 2.1.288 docs and typings, not by running a mod.

## Related

The contrast with settings hooks lives in [[Mods vs Classic Hooks]]; the mechanics in [[Hook Middleware Chain]] and [[Hook Ordering and Tiers]]. Built-ins: [[Built-in diff Mod]], [[Built-in sec-default Mod]]. Trust and governance: [[Mods Trust Model]], [[Org Mod Controls]], [[Org Mod Policy Guide]]. Distribution: [[Marketplaces and Distribution]]. Version anchor: [[Claude Code Release Channels]].

## Sources

- Canon file: `references/canon/002-customize-claude-code-with-mods-launch.md`
- blog-mods-launch: https://claude.com/blog/claude-code-mods (published 2026-10-01, retrieved 2026-10-03), capture `.raw/captures/web-2026-10-03/blog-mods-launch.txt`
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870#issuecomment-5560061162 and #issuecomment-5738020815 (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` L9695
