---
type: "flow"
title: "Audit a Third-Party Mod Flow"
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
lane: "security-governance"
related:
  - "[[Mod Security Audit Checklist]]"
  - "[[Read Only Audit Decision]]"
  - "[[Mods Trust Model]]"
  - "[[Reach Levels]]"
  - "[[Mod Catalog]]"
  - "[[Plugin Validate]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Org Mod Policy Guide]]"
  - "[[Claim Verification Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/org (retrieved 2026-10-03)"
sources:
  - "docs-mods-overview"
  - "docs-mods-admin"
  - "docs-plugins-security"
  - "docs-plugins-org"
  - "secgov-validate-probes"
  - "secgov-karanb192-grade-mjs"
  - "pluto-function-hooks"
  - "docs-mods-reference"
  - "types-2-1-288"
---

# Audit a Third-Party Mod Flow

This flow takes a mod someone wants to use and produces a pinned, recorded verdict (adopt, trial, or avoid) without ever loading the mod. It wraps the [[Mod Security Audit Checklist]] with the surrounding steps: intake, pinning, who decides, where the result is stored, and when to repeat it. The official docs make the static path the intended first step: you can list a mod's events and "what it asks Claude Code to do, without running it" (docs-mods-overview).

## Trigger

- Someone asks to install a plugin whose `hooks/hooks.json` has a `modules` key (that is what makes it a mod; docs-mods-reference, Files).
- A catalog row in [[Mod Catalog]] is new, its pinned SHA moved, or Claude Code shipped a new release since the row's "tested on" version.
- An admin is deciding whether to add a mod's marketplace to an allowlist ([[Org Mod Policy Guide]]).

## Prerequisites

- A shell with `git`, `jq`, ripgrep, and Claude Code installed; record `claude --version`.
- A scratch directory outside any project; no step installs or loads the mod ([[Read Only Audit Decision]]).
- The mod's source location: repo URL plus the marketplace entry that would install it. A marketplace entry with a `command` source produces the plugin by running a command, so get the produced tree, not just the entry (docs-plugins-org, control matrix).
- A named owner who signs the verdict.

## Steps

1. **Intake.** Record requester, purpose in one sentence, repo URL, marketplace name and tier (official, community, or third-party; docs-plugins-security).
2. **Pin.** Clone; record `HEAD` SHA and commit date. If the marketplace pins an `archive` with `sha256` or the community catalog pins a commit, record that too (docs-plugins-security).
3. **Inventory.** Run checklist section 2. List settings hooks, `.mcp.json`, `bin/`, skills, agents, commands, and dependencies. Each extra component gets its own review; validate does not report them (secgov-validate-probes, Probe 4).
4. **Scan.** Run `claude plugin validate --strict --json` (checklist section 3). Save `validate.json` with the audit. Compute reach, authority, and cost ([[Reach Levels]]; scanner rules from secgov-karanb192-grade-mjs).
5. **Sweep.** Run checklist section 4 greps. For every hit, write one line: file:line, what it does, whether the README discloses it.
6. **Read the paths that matter.** Read in full: every hook on `tool.call`, `tool.check`, `prompt.*`, `session.append`, `ui.render` of a transcript or dialog site, `plugin.register`, `engine.create`; every function that calls `$.http.fetch`, `$.process.*`, `$.fs.write`, `$.model.*`, `$.prompt.submit`.
7. **Trace data and cost.** Checklist sections 5 and 6: where third-party text goes, what leaves the machine, what spends usage.
8. **Check failure behavior.** Checklist section 7 for any mod that blocks, holds, or approves.
9. **Decide.** Apply the verdict table (checklist section 8). Any BLOCK means avoid unless the owner writes an exception with an expiry date.
10. **Record and publish.** Write the [[Mod Catalog]] row: name, repo, pinned SHA, what it does, events, reach plus flags, usage cost, tested-on version, code reviewed yes, verdict. Link the findings file.
11. **Install pinned, if adopted.** Install from a marketplace entry pinned to the reviewed commit, with auto-update off for that marketplace or the plugin vendored into a directory marketplace you control (docs-plugins-org, "Set update policy"; docs-mods-admin on directory marketplaces).
12. **Schedule re-audit.** On every Claude Code release run [[Re-verify After Release Flow]] from step 4; on any upstream change, repeat from step 2.

## Outputs

| Artifact | Contents |
|---|---|
| `audit-<mod>-<sha7>.md` | Intake, pin, inventory, validate lines, findings with file:line, verdict, owner, date |
| `validate.json` | Raw `claude plugin validate --json` output with the Claude Code version |
| Catalog row | One row in [[Mod Catalog]] |
| Exception (if any) | BLOCK item, reason, compensating control, expiry |

## Gates

| Gate | Pass condition | Source |
|---|---|---|
| G1 pinned | SHA recorded and install path can be pinned | docs-plugins-security |
| G2 complete inventory | Every non-module component reviewed | Probe 4 |
| G3 scan clean | Validate passes on the current version | docs-mods-admin |
| G4 no BLOCK | All checklist BLOCK items pass or have a signed exception | checklist |
| G5 footprint matches purpose | Every `$` call and authority hook is explained by the stated purpose | docs-mods-admin, "Review what a mod can do" |
| G6 fail-closed | Any blocking or holding hook fails closed | docs-mods-events, "Handle a hook that fails" |

## Failure Modes

- **Trusting the scan line.** A mod whose only power is rewriting through `next` shows `calls: nothing on $` (secgov-validate-probes, Probe 1). Step 6 exists for this.
- **Auditing the wrong tree.** Auto-update or a `command` source replaces what you read; the review then covers nothing (docs-plugins-security).
- **Missing the shell side.** A plugin's `hooks/hooks.json` settings hooks run shell commands outside the sandbox and validate says nothing about them (docs-plugins-security; Probe 4).
- **Fetch-then-run passed as "auto-update".** `$.http.fetch` plus `$.process.run` means the reviewed code is not the code that runs (pluto-function-hooks, Risk 4).
- **Dynamic testing on a real machine.** "A disposable project" is not isolation: `$.fs` takes absolute paths. See [[Read Only Audit Decision]].
- **Stale verdict.** The typings warn the surface can change without notice (types 2.1.288 L4); a verdict without a version is not a verdict.

## Rollback

If an adopted mod is later found unsafe:
1. Disable it now: `/plugin` Installed tab, or for an org, managed `enabledPlugins` set to `false` for that plugin id (docs-plugins-org).
2. If unsure what loaded, start sessions with `--safe-mode` until cleaned up (docs-mods-overview).
3. Uninstall with `claude plugin uninstall <plugin> --scope <scope>`; cached files stay under `~/.claude/plugins/cache/` for 14 days unless removed by hand (docs-plugins-security, "Remove a plugin you no longer trust").
4. Rotate any secret the mod could read (`$.env.get` names, files from the sweep), and review what it could have sent (`$.http.fetch` hosts from checklist 4.8).
5. Mark the catalog row avoid with the reason and date.

## Caveats

- This flow never observes runtime behavior; it can miss behavior that only appears with live data. That trade is deliberate ([[Read Only Audit Decision]]).
- `claude plugin details` is not used: it needs the plugin loaded or `--plugin-dir`, and Pluto reported it under-counted mod hooks on 2.1.274 (unverified on 2.1.288).

## Related

The step-level detail is the [[Mod Security Audit Checklist]]. Risk background: [[Mods Trust Model]] and [[Reach Levels]]. Scan semantics: [[Plugin Validate]]. Output goes to [[Mod Catalog]]; recurring re-checks follow [[Re-verify After Release Flow]]. Fleet use of verdicts is in [[Org Mod Policy Guide]]. Evidence handling follows [[Claim Verification Flow]].

## Sources

- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-plugins-security: https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)
- docs-plugins-org: https://code.claude.com/docs/en/plugins/org (retrieved 2026-10-03)
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md`
- secgov-karanb192-grade-mjs: https://github.com/karanb192/awesome-claude-code-mods/blob/59a9911a836326338a831b6c8e37a7a855e405f4/tools/grade.mjs (retrieved 2026-10-03)
- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
