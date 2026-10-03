---
type: "decision"
title: "Read Only Audit Decision"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/decision"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "security-governance"
related:
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Mods Trust Model]]"
  - "[[Plugin Validate]]"
  - "[[Mod Catalog]]"
  - "[[Testing Kit]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Corpus Scope Policy]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)"
sources:
  - "docs-mods-overview"
  - "docs-mods-admin"
  - "docs-mods-api"
  - "docs-mods-reference"
  - "docs-plugins-security"
  - "types-2-1-288"
  - "pluto-function-hooks"
  - "secgov-validate-probes"
  - "compass-report"
---

# Read Only Audit Decision

**Decision:** audits of third-party mods in this brain are static and read-only. Agents and contributors read source, run `claude plugin validate`, and grep; they never install, enable, load, hot-reload, or run a third-party mod, including through `--plugin-dir` or `claude plugin test`. A dynamic trial is a separate step that only a named human may approve, in an isolated OS account or VM with no real credentials, and its result is recorded as practitioner evidence. Status: adopted 2026-10-03 for Claude Code 2.1.288.

## Context

- A loaded mod runs with the user's permissions: files anywhere, processes, network, environment variables and settings, every prompt and tool call, and model calls on the user's plan (docs-mods-overview, "What a mod can reach").
- It is not sandboxed, and processes it starts run outside the Bash sandbox (docs-mods-overview) (C-SEC-001, C-SEC-002).
- `$.fs` uses absolute paths as given (types 2.1.288 L3009-3014). A pre-release test read the Claude Code credential file and the full prompt history and posted them out with no prompt (pluto-function-hooks, Risk 1).
- Harm can happen at load: `session.start` fires for each loaded mod before the first prompt (docs-mods-reference, Session), and `plugin.register` and `engine.create` run while loading (types 2.1.288 L4156-4199).
- The official path supports static review: validate lists events and calls "without running it" (docs-mods-overview), and Claude Code refuses to load a mod whose `$` use the scan cannot read (docs-mods-admin).
- This brain's agents run with the owner's credentials in reach; an agent that loads a mod hands that mod the same reach.

## Options considered

| Option | What it means | Upside | Downside |
|---|---|---|---|
| A. Static read-only (chosen) | Source read, validate, greps; no load | No code from the mod runs; reproducible; works in CI | Misses behavior that only shows with live data; cannot confirm runtime UI claims |
| B. Static plus contained dynamic trial | A then, with human approval, load in a throwaway OS user or VM | Observes real behavior and debug log | Setup cost; still exposes whatever the box holds; easy to do badly |
| C. Dynamic in a "disposable project" | Load with `--plugin-dir` in an empty folder on the real machine | Fast | Not isolation: absolute paths, env, and settings stay readable |
| D. Trust the marketplace | Install from official or allowlisted sources without review | Zero effort | A marketplace's name says who publishes the catalog, not what a plugin does (docs-plugins-security) |

> [!contradiction]
> The seed report's audit checklist ends with "Load it once with `--plugin-dir` in a disposable project with no secrets" (compass-report, section 4). The docs say a mod reads files anywhere the user can, plus environment variables and settings (docs-mods-overview), and the typings say absolute paths are used as given (types 2.1.288 L3009-3014). An empty project protects nothing outside itself. The docs win: option C is rejected; dynamic trials need option B's isolation.

## Rationale

1. The static path covers the questions that decide most verdicts: what the mod hooks, what it calls, which env vars it reads, and what its other components run ([[Mod Security Audit Checklist]]).
2. Validate's own limits are known and testable without loading: it does not report rewrites through `next`, settings hooks, or `bin/` (secgov-validate-probes, Probes 1 and 4). The checklist adds source reads for exactly those.
3. Loading is irreversible in the ways that matter: a secret read and sent at `session.start` cannot be recalled, only rotated.
4. Read-only work is easy to repeat after each release ([[Re-verify After Release Flow]]).

## Consequences

- Catalog rows from this brain say "code reviewed: yes" and "tested on: <version> (static)". Runtime claims carry practitioner or unverified confidence ([[Uncertainty Eval Policy]]).
- Runtime-only findings (UI attribution in the band, `AskUserQuestion` label restoration, `plugin details` hook counts) stay unverified until someone runs option B ([[Mods Trust Model]]).
- Writing and testing your own mods is unaffected: authors use the dev loop and `claude plugin test` on their own code ([[Hot Reload and Dev Loop]], [[Testing Kit]]). This decision covers third-party code.
- Agents asked to "just try" a third-party mod decline and route the request to a human with this note.

## Option B, when a human approves it

Minimum isolation for a dynamic trial:
- A separate OS user account or VM, with no Claude credentials beyond a throwaway login, no SSH or cloud keys, no real `~/.claude/history.jsonl`.
- Network egress logged or limited; note that org web-fetch policy covers `$.http.fetch` but not programs from `$.process.run` (docs-mods-admin) (C-SEC-015).
- Start with `claude --debug` and keep the log; record the pinned SHA and version.
- Destroy the account or VM afterward.

## Revisit triggers

- Claude Code ships install-time capability disclosure or a per-mod sandbox (Pluto asked for both; pluto-function-hooks, "A capability you cannot see").
- The static scan starts reporting rewrites, settings hooks, or `bin/`.
- The brain needs runtime claims that only option B can settle.

## Recommendations

- Keep agent work on option A; never run third-party mod code from an agent session. EVIDENCE-BASED
- Run option B only in an isolated account or VM, never in "a disposable project" on a real machine. EVIDENCE-BASED
- Label every verdict with the method (static or dynamic) and the Claude Code version. PRACTITIONER

## Caveats

- Static review cannot prove absence of behavior; it lowers risk and makes it visible.
- The decision is scoped to 2.1.288 behavior; the typings describe the surface as early access (types 2.1.288 L4).

## Related

The decision is applied by [[Audit a Third-Party Mod Flow]] and [[Mod Security Audit Checklist]], grounded in [[Mods Trust Model]] and the scan described in [[Plugin Validate]]. Verdicts land in [[Mod Catalog]]. Own-mod development stays on [[Hot Reload and Dev Loop]] and [[Testing Kit]]. Scope and confidence rules come from [[Corpus Scope Policy]] and [[Uncertainty Eval Policy]].

## Sources

- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-plugins-security: https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md`
- compass-report: `.raw/sources/compass-report-2026-10-02.md`
