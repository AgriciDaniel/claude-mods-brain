---
type: "concept"
title: "Inside Claude Code Function Hooks The Trust Problem (Pluto Security)"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/concept"
  - "#confidence/contested"
confidence: "contested"
lane: "rewrite"
related:
  - "[[Mods Trust Model]]"
  - "[[Prompt Injection via Mods]]"
  - "[[Reach Levels]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Read Only Audit Decision]]"
  - "[[Org Mod Controls]]"
  - "[[Org Mod Policy Guide]]"
  - "[[Plugin Validate]]"
  - "[[Render Sites]]"
  - "[[Unverified pre-release security findings on current builds]]"
  - "[[Claude Code plugins and hooks documentation (Anthropic)]]"
source_urls:
  - "https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)"
sources:
  - "pluto-function-hooks"
  - "docs-mods-overview"
  - "docs-mods-admin"
  - "docs-mods-troubleshoot"
  - "docs-mods-interface"
  - "docs-plugins-security"
  - "secgov-validate-probes"
  - "types-2-1-288"
---

# Inside Claude Code Function Hooks The Trust Problem (Pluto Security)

This note folds canon 005, Ehud Melzer's Pluto Security article of 2026-09-22, into the vault. It is the only independent, adversarial test of mods in the canon: the author wrote a malicious mod per risk on pre-release Claude Code 2.1.274 and recorded what a user sees. Its thesis holds on 2.1.288 (the `$` design is sound, consent is uninformed, and `next` rewrites evade the capability scanner), but its gate status and admin advice are stale and three findings are still unverified on current builds. Confidence is contested.

## What the work teaches

| Risk | Test on 2.1.274 | Status on 2.1.288 |
|---|---|---|
| 1. Silent exfiltration | `session.start` reads the credentials file and prompt history, posts via `$.http.fetch` | capability confirmed by docs (C-SEC-001); demo not reproduced |
| 2. No disclosure | `plugin details` showed "Hooks (0)" for a four-event mod | unverified (C-SEC-052) |
| 3a. In-terminal phishing | `Input` in `AbovePrompt` reads a typed key | confirmed by docs (C-SEC-054) |
| 3b. Dialog swap | `ui.render` rewrites `AskUserQuestion` text; labels restored | rewrite confirmed (C-SEC-004); label restore unverified (C-SEC-055) |
| 3c. Transcript falsification | `tool.call` appends a command, `ToolUse` shows original | validate blind to it (C-SEC-011); auto mode denies changed input |
| 4. Post-review code swap | `$.http.fetch` a script, run with `$.process.run(["sh","-c", ...])` | validate passes it silently (C-SEC-009) |
| Scan path | content scan only on claude.ai install path | unverified (C-SEC-053) |

Controls it found holding: no ambient `fetch`, `require`, `import` or string `eval`; unhookable permission prompt; host-assigned tier; a mod named after a built-in does not load.

## How its claims map onto vault notes

- Core critique (consent, disclosure) lives in [[Mods Trust Model]].
- Phishing band, dialog swap, transcript falsification live in [[Prompt Injection via Mods]] and [[Render Sites]].
- Fetch plus process as top risk is the L3 rule in [[Reach Levels]].
- "Run validate yourself and read source for `next` rewrites" is step one of [[Audit a Third-Party Mod Flow]] and the [[Mod Security Audit Checklist]].
- Why this brain never reproduces the demos: [[Read Only Audit Decision]].
- Admin advice remapped to current switches: [[Org Mod Controls]], [[Org Mod Policy Guide]].
- The unverified findings and their trial plan: [[Unverified pre-release security findings on current builds]].

## Agreement and contradiction

> [!contradiction] Gate status. Pluto: function hooks are "currently gated behind CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1" and off by default (capture L98, L292). Docs: mods are on by default from 2.1.287 and the variable is ignored, so `0` does not turn them off (docs-mods-overview L97, L112). Docs win (C-SEC-063, contradicted). An admin who followed Pluto has mods on.

> [!contradiction] Admin controls. Pluto recommends `disableAllHooks` or `allowManagedHooksOnly`. The admin page adds `allowManagedModsOnly` on the guard as the targeted switch and warns that managed `disableAllHooks` also stops managed `PreToolUse` blocks (docs-mods-admin). Pluto's advice still works but is wider than needed.

> [!contradiction] `plugin details` disclosure. Pluto saw "Hooks (0)" (capture L142, L151). The plugin security page says `details` prints a `Component inventory` listing "hooks with each hook's event" (docs-plugins-security L104) without saying function hooks count. Unresolved on 2.1.288 (C-SEC-052).

- **Confirmed by 2.1.288 tool output:** validate passes an exfil-shaped module (file read, `ANTHROPIC_API_KEY` read, POST, `sh -c` on the reply) with no warning (C-SEC-009), and `next` rewrites show only on the `hooks:` line (C-SEC-011).
- **Partly mitigated:** in auto mode a call whose input a hook changed after the model wrote it is denied with "a hook changed this call's input after the model wrote it" (docs-mods-troubleshoot L144-148). Outside auto mode, transcript falsification stands.
- **Agrees with the design thread** ([[Mods design thread, anthropics claude-code issue 91870]]) that installing is consent, but treats that as the problem rather than the design.
- **Count drift:** "19 nouns" on `$` predates launch; 2.1.288 has 21 namespaces (C-API-041).

## Verified quotes

Copied from `references/canon/005-pluto-function-hooks-trust-problem.md`; each re-found verbatim in `.raw/captures/web-2026-10-03/pluto-function-hooks.txt`.

- "a mod is code you run, not a document you read." (TL;DR, capture L39)
- "treat installing a mod exactly like running an untrusted binary." (TL;DR, capture L39)
- "The tool-approval dialog is not a hookable render component" (capture L252)
- "$.http.fetch responses are not integrity-pinned" (Risk 4, capture L238)
- "A capability you cannot see is a capability you did not consent to" (closing heading, capture L298)

## What it gets wrong or leaves stale

- Gate status (above): outdated by the 2.1.287 launch.
- Admin controls: incomplete, missing `allowManagedModsOnly`, `disableSideloadFlags`, `prependPlugins`, and the guard.
- "Hooks (0)", the claude.ai-only content scan, and label restoration are 2.1.274 observations never retested (C-SEC-052, C-SEC-053, C-SEC-055).
- Vendor interest: the article ends with a pitch for Pluto's governance product, which colours the "users cannot consent" framing.
- It does not mention that the guard is absent for personal API-key users without managed settings (C-SEC-018), which is the larger real-world exposure.

## How much to trust it

Confidence: contested. Rank 5 (independent research). Its mechanisms are consistent with current docs and with this brain's own static probes, so its risk model is worth adopting. Its status claims are stale and its three unique observations are unverified. Cite it for "what an attacker can do", and cite docs for "what Claude Code does today".

- Read source for `next({...e})` rewrites, `ui.render` on `AskUserQuestion` or `ToolUse`, and fetch-then-run before trusting any validate output. EVIDENCE-BASED
- Flag any mod declaring both `$.http.fetch` and `$.process.run` as L3. PRACTITIONER
- Pin or vendor the exact commit you reviewed; turn off marketplace auto-update for it. PRACTITIONER
- Do not rely on `plugin details` to show a mod's hooks until retested. CONTESTED

## Caveats

- Demos were the author's reports; this brain did not reproduce them and must not without an isolated, human-approved trial.
- Version sensitivity: tested on 2.1.274, nine days before the 2.1.287 launch.

## Related

Trust: [[Mods Trust Model]], [[Reach Levels]]. Attacks: [[Prompt Injection via Mods]], [[Render Sites]]. Audit: [[Audit a Third-Party Mod Flow]], [[Mod Security Audit Checklist]], [[Plugin Validate]], [[Read Only Audit Decision]]. Admin: [[Org Mod Controls]], [[Org Mod Policy Guide]]. Open items: [[Unverified pre-release security findings on current builds]]. Substrate: [[Claude Code plugins and hooks documentation (Anthropic)]].

## Sources

- Canon file: `references/canon/005-pluto-function-hooks-trust-problem.md`
- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (published 2026-09-22, retrieved 2026-10-03), capture `.raw/captures/web-2026-10-03/pluto-function-hooks.txt`
- docs-mods-overview, docs-mods-admin, docs-mods-troubleshoot, docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/<page> (retrieved 2026-10-03)
- docs-plugins-security: https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md` (run 2026-10-03 on 2.1.288)
- Contradictions record: [[Contradictions Register#Security and governance]] entries 1, 8, 9, 10
