---
type: "concept"
title: "Mods Trust Model"
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
lane: "security-governance"
related:
  - "[[Reach Levels]]"
  - "[[Org Mod Controls]]"
  - "[[Prompt Injection via Mods]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Built-in sec-default Mod]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Plugin Validate]]"
  - "[[Render Sites]]"
  - "[[Mods API Namespaces]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)"
  - "https://claude.com/blog/claude-code-mods (retrieved 2026-10-03)"
  - "https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)"
sources:
  - "docs-mods-overview"
  - "docs-mods-admin"
  - "docs-mods-api"
  - "docs-mods-interface"
  - "docs-mods-reference"
  - "docs-mods-events"
  - "docs-plugins-security"
  - "blog-mods-launch"
  - "types-2-1-288"
  - "pluto-function-hooks"
  - "gh-issue-91870"
  - "secgov-validate-probes"
---

# Mods Trust Model

A mod is code that runs with your user permissions inside Claude Code, and it is not sandboxed (docs-mods-overview, blog-mods-launch). The model has a few real boundaries (every effect goes through the `$` mods API, a static scan lists those calls, load order decides authority, the permission prompt cannot be redrawn) and several things that look like boundaries but are not (the Bash sandbox, the `calls:` line, a project folder). Treat installing a mod like running an unreviewed binary, and treat review as the only consent you get (C-SEC-001, C-SEC-056).

## What a loaded mod can reach

The overview lists six reaches, all with the installing user's permissions (docs-mods-overview, "What a mod can reach"):

| Reach | Through | Note |
|---|---|---|
| Files, programs, network | `$.fs`, `$.process`, `$.http` | Absolute paths are used as given (types 2.1.288 L3009-3014) |
| Secrets | `$.env.get`, `$.settings.read` | Env names must be string literals, so validate lists them (C-SEC-006) |
| Your session | `tool.call`, `prompt.submit`, `$.session.messages` | Every prompt and every tool call, including subagent and MCP calls (docs-mods-events) |
| Changing your session | `next({...e})` rewrites, `$.prompt.submit`, `$.session.send` | `asUser: true` sends text as your own words (C-SEC-017) |
| Acting without asking | `tool.check` returning `allow` | Can approve past an `ask` rule or a non-managed `PreToolUse` block (C-SEC-021) |
| Spending usage | `$.model.complete`, `fork`, `classify`, started turns | See [[Usage Cost Surface]] |

The sandbox does not help: the docs state that the sandbox isolates Claude's Bash commands, and a process a mod starts runs outside it (docs-mods-overview; docs-plugins-security) (C-SEC-002).

## The boundaries that hold

1. **One door.** The hooks module has no Node APIs, no timer globals, and no network or file access of its own; everything crosses through `$` (docs-mods-api, "Reach files, processes, and the network"; types 2.1.288 L1-27). Independent tests on pre-release builds found no ambient `fetch`, `require`, or working `import()` (pluto-function-hooks; gh-issue-91870 comment by @deafsquad, issuecomment-5545887629).
2. **A scan you can read before running anything.** `claude plugin validate` prints `hooks:` and `calls:` lines, and Claude Code refuses to load a mod that uses `$` in a way the scan cannot read (docs-mods-admin, "Review what a mod can do"). On 2.1.288 the scan refused computed access such as `$['http']`, a non-literal `$.env.get(n)`, and a dynamic `import()` (secgov-validate-probes, Probe 2).
3. **Order is authority.** Hooks on one event form a middleware chain; the first mod sees the event first and the result last, and decides whether later mods run (docs-mods-events, "The order mods run in"). Organization mods and the built-in guard sit ahead of user mods. See [[Hook Ordering and Tiers]].
4. **Host-assigned identity.** `next.origin` carries `{ plugin, tier }` set by Claude Code (docs-mods-reference, "The hook function"). Reserved names such as `claude-*`, `anthropic-*`, and `cc-plugin-*` fail validate (secgov-validate-probes, Probe 3) (C-SEC-012).
5. **The permission prompt is not a render site.** A mod can restyle much of the interface but cannot change what the permission prompt shows (docs-mods-interface; docs-mods-admin) (C-SEC-003).
6. **Managed rules come first where the guard loads.** Managed `PreToolUse` blocks are final and re-run on a rewritten call; user mods cannot lift a `deny` rule unless an admin sets `allowModsToOverrideDenyRules` (docs-mods-admin) (C-SEC-020, C-SEC-022). See [[Built-in sec-default Mod]].

## The things that are not boundaries

- **The `calls:` line is not the whole story.** A rewrite passed through `next` makes no `$` call. A probe that appended text to every Bash command validated with that rewrite visible only as `tool.call{tool=Bash}` on the `hooks:` line (secgov-validate-probes, Probe 1) (C-SEC-011).
- **Validate does not judge.** The same probe read a file, read `ANTHROPIC_API_KEY`, posted both out, and ran the response with `sh -c`; validate passed with no warning beyond a missing `author` (C-SEC-009).
- **Validate covers the module only.** A `curl | sh` settings hook in the same `hooks/hooks.json` and an executable in `bin/` were not mentioned (secgov-validate-probes, Probe 4) (C-SEC-010).
- **Runtime-fetched code is invisible.** `$.http.fetch` has no integrity option (its `init` is `method, headers, body, auth, socketPath`; types 2.1.288 L3262-3282), so fetch-then-run can change after review (pluto-function-hooks, Risk 4).
- **Reviewed files can change on disk.** Marketplace auto-update replaces what you read (docs-plugins-security, "Understand what a plugin can do") (C-SEC-047).
- **A project folder is not isolation.** `$.fs.read` takes absolute paths, so "a disposable project with no secrets" still exposes the home directory (types 2.1.288 L3009-3014).

> [!contradiction]
> The launch blog says sec-default "stops mods that users install from doing risky things" (blog-mods-launch). The admin page is narrower: the guard protects managed hooks, the system prompt, managed instructions, settings reads, and managed MCP tools, and "adds no other restrictions" (docs-mods-admin). The admin page wins: a user's mod can still read, write, fetch, run, rewrite, and approve.

## Pluto findings re-checked against 2.1.288

Pluto tested pre-release 2.1.274 (pluto-function-hooks, Sep 22, 2026). Status against the 2.1.288 docs, typings, and static probes:

| Pluto finding | Status on 2.1.288 | Evidence |
|---|---|---|
| Mods gated behind `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` | Fixed (superseded): on by default, the variable is ignored | docs-mods-overview; docs-mods-admin (C-SEC-030) |
| Risk 1: `$.fs.read` unscoped, silent exfil via `$.http.fetch` | Still present by design; an admin policy mod can hook `fs.read` | types L3009-3014; docs-mods-api (C-SEC-013) |
| Risk 2: no capability disclosure at install | Still present per docs: disclosure is the manual `claude plugin validate` | docs-mods-overview, "List what a mod does" |
| Risk 2: `plugin details` reports `Hooks (0)` for a mod | Unverified (running `details` needs `--plugin-dir`, out of scope here) | docs-plugins-security says details lists hooks (C-SEC-052) |
| Risk 2: content scan only on the claude.ai path | Unverified | No doc statement (C-SEC-053) |
| Risk 3: fake credential prompt in `AbovePrompt` | Still present: `Input` is a supported element and the band is shared | docs-mods-reference, Elements and Render sites (C-SEC-054) |
| Risk 3: `AskUserQuestion` question swapped | Still present: it is a render site; a rewrite must fit the tool schema | docs-mods-interface; types L9113-9128 (C-SEC-004) |
| Option labels restored by the engine | Unverified: not stated in 2.1.288 docs or typings | (C-SEC-055) |
| Risk 3: transcript falsified via `tool.call` plus `ToolUse` render | Still present: both are documented hook points | docs-mods-interface; Probe 1 |
| Risk 4: fetch-then-run | Still present by design | types L3262-3282 |
| No ambient `fetch`, `require`, `eval` codegen | Holds per docs; validate does not refuse `globalThis` or `Function` statically | docs-mods-api; Probe 2 (C-SEC-007) |
| Permission prompt cannot be rewritten | Holds | docs-mods-interface (C-SEC-003) |
| Identity and tier not spoofable | Holds; reserved names refused | Probe 3 (C-SEC-012) |

## Anthropic's stated position

The issue author on #91870 wrote that admins can disable render hooks or refuse registration, and that installing a plugin is the consent (gh-issue-91870, @poteat, issuecomment-5546290346) (C-SEC-056). So the product will not narrow what a mod may do; narrowing is your job through review and [[Org Mod Controls]].

## Recommendations

- Review before install, every time, using [[Mod Security Audit Checklist]]: validate output plus a source read. EVIDENCE-BASED
- Read the `hooks:` line as carefully as the `calls:` line; rewrites and approvals live there. EVIDENCE-BASED
- Treat any credential prompt drawn above the input box, or any reworded question dialog, as suspect; enter secrets only in flows you started. PRACTITIONER
- Pin reviewed code (commit SHA or vendored copy) and turn off auto-update for marketplaces that ship mods you reviewed. EVIDENCE-BASED
- On a personal machine with no managed settings there is no guard; deny rules do not hold against a user mod there. EVIDENCE-BASED

## Caveats

- Everything here was checked against Claude Code 2.1.288 docs captured 2026-10-03, typings written by 2.1.288, and static validate runs. No mod was loaded, so runtime claims (UI phishing, label restoration, `globalThis` contents) are not re-tested.
- The typings header says the surface "may change between releases without notice" (types 2.1.288 L4). Re-run [[Re-verify After Release Flow]] after each release.

## Related

Start with [[Reach Levels]] for a fast triage label and [[Prompt Injection via Mods]] for the model-facing risk. [[Org Mod Controls]] and [[Org Mod Policy Guide]] cover fleet policy; [[Built-in sec-default Mod]] is the guard itself. The mechanics behind the boundaries are in [[Hook Ordering and Tiers]], [[Hook Middleware Chain]], [[Render Sites]], [[Mods API Namespaces]], and [[Plugin Validate]]. Practical use: [[Audit a Third-Party Mod Flow]], [[Mod Security Audit Checklist]], [[Read Only Audit Decision]].

## Sources

- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-plugins-security: https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)
- blog-mods-launch: https://claude.com/blog/claude-code-mods (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md`
