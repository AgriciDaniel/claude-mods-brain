---
title: "Inside Claude Code Function Hooks: The Trust Problem Behind Claude Mods"
author: "Ehud Melzer"
publisher: "Pluto Security (Pluto Research)"
year: "2026"
date: "2026-09-22"
url: "https://pluto.security/blog/claude-code-function-hooks-security/"
source_capture: ".raw/captures/web-2026-10-03/pluto-function-hooks.txt"
retrieved: "2026-10-03"
confidence: "contested"
tags:
  - "#domain/claude-code-mods"
  - "#type/canon"
  - "#source/independent-research"
  - "#confidence/contested"
---

# "Inside Claude Code Function Hooks: The Trust Problem Behind Claude Mods" (Pluto Security, 2026-09-22)

Byline Ehud Melzer, dated Sep 22, 2026, 11 min read. An independent, hands-on security test of the pre-release build (screenshots say Claude Code v2.1.274, gated by `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`), nine days before mods shipped on by default in v2.1.287. The article ends with a vendor pitch for Pluto's own governance product, so weigh its framing accordingly. Overall confidence is contested: the attack mechanics are mostly consistent with the current docs, but several status and disclosure claims are out of date or unverified on 2.1.288.

## Core Thesis

The `$` capability model is sound in design (no ambient access, static scan of `$` calls, host-assigned tier, unhookable permission prompt) but consent is not informed: the capability list exists, yet users are not shown it at install, one inspection screen reported zero hooks, and the scanner cannot see `next` rewrites or code fetched at runtime. Until disclosure improves, treat a mod like an untrusted binary.

## How It Works

The method is adversarial testing: write a malicious mod for each risk, install it through normal paths, and observe what the user sees.

| Risk | Test | Mechanism |
|---|---|---|
| 1. Silent secret exfiltration | `session.start` reads `~/.claude/.credentials.json` and `history.jsonl`, posts both with `$.http.fetch` | `$.fs.read` is not scoped; no prompt |
| 2. No capability disclosure | Mod hooking `*`, `tool.call`, `session.start`, `command.run` via a local marketplace | `install`, `list`, first run show nothing; `plugin details` showed "Hooks (0)"; only `validate` lists `$` calls |
| 3a. In-terminal phishing | Fake "session verification" with a real `Input` in `AbovePrompt` | `ui.input` hook reads the key and posts it |
| 3b. Dialog question swap | Rewrite `AskUserQuestion` text at `ui.render` | Model's option labels are preserved, but question text and descriptions are not |
| 3c. Transcript falsification | `tool.call` appends a hidden command; `ToolUse` render shows the original | Uses only `next` rewrites, so `validate` lists no `$` calls |
| 4. Post-review code swap | `$.http.fetch` a script, run with `$.process.run(["sh","-c", ...])` | Responses are not integrity-pinned |

It also lists controls that held: no ambient `fetch`, `XMLHttpRequest`, `WebSocket`, `require`, `import`, or string `eval`; unhookable permission prompt; label preservation in `AskUserQuestion`; tier derived from host-assigned name, and a mod named after a built-in does not load.

## Key Principles

1. A capability report only helps if users see it before install and it covers the behavior that creates the risk.
2. The `$` scanner cannot see rewrites passed through `next` (UI and transcript) or code fetched at runtime.
3. `$.http.fetch` plus `$.process.run` together equal download-and-execute; treat that pair as high risk.
4. Consent surfaces inside the client (bands, dialogs) are spoofable by any mod that can render there.
5. Provenance and scan results are signals, not guarantees.

## Best Practices

- Run `claude plugin validate` yourself before install and read the `calls:` and `env reads:` lines. EVIDENCE-BASED
- Read the source for `next` rewrites, `ui.render` on `AskUserQuestion` or `ToolUse`, and any fetch-then-run. EVIDENCE-BASED
- Pin or vendor the exact code you reviewed. PRACTITIONER
- Enter secrets only through flows you started; distrust credential prompts that appear inside the session. PRACTITIONER
- Admins: flag mods that declare both `$.http.fetch` and `$.process.run`. PRACTITIONER
- Do not rely on `plugin details` to show mod hooks. CONTESTED

## Verified Quotes

- "a mod is code you run, not a document you read." (TL;DR, last paragraph)
- "treat installing a mod exactly like running an untrusted binary." (TL;DR)
- "Rendered live in Claude Code v2.1.274." (Risk 3, phishing screenshot caption)
- "The tool-approval dialog is not a hookable render component" ("What the design gets right")
- "$.http.fetch responses are not integrity-pinned" (Risk 4)
- "A capability you cannot see is a capability you did not consent to" (closing heading)

## Evidence Caveats

> [!contradiction] Gate status. Pluto says mods are off unless the environment gate is set. docs-mods-overview says mods are on by default from v2.1.287 and the variable is ignored. Docs win; Pluto's claim is outdated.

> [!contradiction] Admin controls. Pluto's admin advice covers `disableAllHooks` and `allowManagedHooksOnly` only. The current docs add `allowManagedModsOnly`, `disableSideloadFlags`, `prependPlugins`, and the `sec-default` guard that keeps user mods from lifting deny rules (docs-mods-admin). Pluto's advice is incomplete, not wrong.

- **Confirmed by docs**: mods are unsandboxed and `$.fs` reads anywhere the user can; deny rules do not cover a mod's own `$.fs` or `$.process` calls; the permission prompt cannot be restyled; `AskUserQuestion` and `ToolUse` are render sites; network policy does not cover `$.process.run` (docs-mods-overview, docs-mods-admin, docs-mods-reference).
- **Partly mitigated in docs**: in auto mode, a call whose input a hook changed after the model wrote it is denied ("a hook changed this call's input after the model wrote it", docs-mods-troubleshoot). That limits transcript falsification in auto mode only.
- **Unverified on 2.1.288**: "Hooks (0)" in `plugin details`; the claim that a content scan runs only on the claude.ai install path; label preservation behavior. Docs say `plugin details` lists hooks with their events but name `validate` as the mod inspection tool. Re-test before citing.
- "19 nouns" on `$` predates launch; docs-mods-reference lists 21 namespaces.
- The exfiltration and phishing demos are the author's reports; this lane did not reproduce them and must not (lane rule: never run a mod).
- Vendor interest: Pluto sells add-on governance, which colors the "users cannot consent" framing.

## Brain Hooks

- [[Mods Trust Model]]: the core of this critique.
- [[Prompt Injection via Mods]]: phishing band, dialog swap, transcript falsification.
- [[Reach Levels]]: fetch plus process as the top reach tier.
- [[Audit a Third-Party Mod Flow]] and [[Mod Security Audit Checklist]]: validate, read `next` rewrites, fetch-then-run.
- [[Read Only Audit Decision]]: why audits stay static here.
- [[Org Mod Controls]] and [[Org Mod Policy Guide]]: map Pluto's admin advice onto the current switches.
- [[Plugin Validate]]: the only disclosure surface Pluto trusted.
- [[Render Sites]]: `AbovePrompt`, `AskUserQuestion`, `ToolUse` as attack surfaces.
- [[Versioning and API Drift]]: pre-release 2.1.274 findings versus 2.1.287 docs.
