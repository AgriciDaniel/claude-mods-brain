---
type: "concept"
title: "Org Mod Controls"
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
  - "[[Org Mod Policy Guide]]"
  - "[[Built-in sec-default Mod]]"
  - "[[Mods Trust Model]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Marketplaces and Distribution]]"
  - "[[Claude Code Release Channels]]"
  - "[[Mods vs Classic Hooks]]"
  - "[[Version Pin Policy]]"
  - "[[Build a Tool Call Guard Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/org (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)"
sources:
  - "docs-mods-admin"
  - "docs-plugins-org"
  - "docs-mods-reference"
  - "docs-mods-troubleshoot"
  - "docs-mods-overview"
  - "docs-plugins-security"
  - "docs-plugins-measure"
  - "blog-mods-launch"
  - "types-2-1-288"
  - "gh-issue-91870"
  - "pluto-function-hooks"
---

# Org Mod Controls

Administrators control mods through managed settings in three layers: the built-in guard `sec-default` and its two options, the plugin-loading keys that already govern every plugin, and an optional policy mod of your own that runs first. None of them sandboxes a mod: "A mod you allow runs as the user" (docs-mods-admin, "Know which controls still apply"). This note explains each control and its limits; [[Org Mod Policy Guide]] turns them into ready policies.

## Layer 1: the built-in guard

`sec-default@builtin` (listed as `cc-plugin-sec-default`) loads ahead of every user mod when the machine has managed settings or the user signs in with a Team or Enterprise plan. API key, Bedrock, Google Cloud Agent Platform, and Microsoft Foundry users get it only on machines with managed settings (docs-mods-admin, "Know what happens by default") (C-SEC-018).

What it does by default (C-SEC-019, C-SEC-020):
- Protects managed hooks' inputs and decisions, the system prompt, managed `CLAUDE.md` and instructions, what mods read as settings, and managed MCP servers' tools and descriptions from user mods.
- Keeps a user mod's `tool.check` from approving a call a `deny` rule refuses, from any settings file. The refusal message contains `tried to lift a deny rule in your settings` (docs-mods-troubleshoot).
- Fails closed: if it cannot read managed settings it refuses every user mod; if it cannot check deny rules for an approved call it refuses the call (docs-mods-admin).

What it does not do: limit `$.fs` or `$.process` calls (a mod can read a file `Read(.env)` denies), or limit anything else a user mod does (docs-mods-admin).

### Guard options (managed `pluginConfigs` only)

| Option | Unset | `true` |
|---|---|---|
| `allowManagedModsOnly` | Users' own mods load | Only org mods and built-in mods load; refused mods include installed, `--plugin-dir`, and session-written ones |
| `allowModsToOverrideDenyRules` | Deny rules beat users' mods | A user mod's approval can override a `deny` rule |

Rules (docs-mods-admin, "Set options on the built-in guard") (C-SEC-023, C-SEC-024):
- The key is exactly `cc-plugin-sec-default@builtin` under `pluginConfigs`; `sec-default@builtin` is accepted only in `prependPlugins`.
- Only managed settings count; user, project, local, and `--settings` files neither set nor loosen an option.
- If you set `prependPlugins`, you must list `sec-default@builtin` in it or the guard does not load, and neither option applies (C-SEC-025).

## Layer 2: plugin-loading keys

| Key | Effect on mods | What it misses |
|---|---|---|
| `allowManagedHooksOnly` | Blocks installed mods that are not the org's, and hooks in users' settings files | Wider than mods; read its settings reference before use |
| `disableAllHooks` (managed) | No mod or hook from any installed plugin runs, the org's included; managed `PreToolUse` stops blocking; status lines and `/goal` stop | Built-in mods keep running |
| `disableSideloadFlags` | Rejects `--plugin-dir`, `--plugin-url`, `--agents`, the SDK `plugins` option, non-SDK `--mcp-config`, and `CLAUDE_CODE_PLUGIN_DIRS` folders; stops session-written mods | Does not restrict `.mcp.json` or `claude mcp add` (docs-plugins-org) |
| `strictKnownMarketplaces` / `blockedMarketplaces` | Decide which marketplace sources any plugin, and so any mod, may come from | Do not block `--plugin-dir`; do not filter plugins inside an allowed marketplace |
| managed `enabledPlugins: false` | Blocks one plugin at every scope and hides it | Needs one entry per plugin |
| `syncClaudeAiPlugins: false` | Stops plugins synced from members' claude.ai accounts | Users can also set it themselves |
| managed `autoUpdate` per marketplace, `DISABLE_AUTOUPDATER` | Freezes reviewed code on disk | `DISABLE_AUTOUPDATER` does not cover `command` sources |
| `pluginTrustMessage` | Appends your text to the install trust warning | Does not change the warning |

Sources: docs-mods-admin, "Choose how much to allow"; docs-plugins-org, control matrix and "Set update policy"; docs-mods-reference, settings table (C-SEC-027, C-SEC-028, C-SEC-047).

The decision table from the admin page, with the plugin controls you already have:

| Your plugin controls | What a user can load as a mod |
|---|---|
| None | Any marketplace, any `--plugin-dir`, or a mod Claude writes in session |
| Marketplace allowlist | Allowed marketplaces, any `--plugin-dir`; session-written mods only if the allowlist includes `skills-dir` |
| Allowlist plus `disableSideloadFlags` | Allowed marketplaces only |

## Layer 3: your own policy mod

An org mod counts as yours only when all three hold: managed `enabledPlugins` sets it `true`; managed settings name its marketplace as a directory by absolute path; the marketplace lists it by relative path so it loads in place. A plugin copied from GitHub, git, URL, or npm counts as a user's even when managed settings enable it (docs-mods-admin) (C-SEC-026). Make that directory writable only by administrators; anyone who can write there can rewrite your mod.

Placement:
- `prependPlugins`: sees every event before users' mods and every result after; can change, refuse, or skip them with `next.to(e, 'append')`.
- `appendPlugins`: runs after users' mods and sees only what they pass on.

What a policy mod can do: refuse other mods at load with `plugin.register` using `e.tier` and `e.uses.calls`; hook any mods API call by name (`fs.write`, `http.fetch`, `process.run`) to log or `{ deny }` it; withhold or add namespaces with `engine.create` (docs-mods-admin; docs-mods-reference, "Other mods"; types 2.1.288 L4156-4199) (C-SEC-031). Withholding a namespace constrains plugins, not Claude's own tools, per a pre-release test (gh-issue-91870, @deafsquad, issuecomment-5542444779) (C-SEC-057).

## Controls that still apply without any mod setting

- Managed `PreToolUse` hooks run before any mod and their block is final, including on a rewritten call (C-SEC-022).
- Network policy covers `$.http.fetch` but not a program started with `$.process.run` (docs-mods-admin) (C-SEC-015).
- No mod loads in an untrusted directory until the trust prompt is answered (docs-mods-admin) (C-SEC-035).
- The permission prompt cannot be redrawn (C-SEC-003).

## Ways a session runs without your controls

- The hooks worker crashing three times unloads every non-built-in mod, yours included, until `/reload-plugins` or a new session (C-SEC-034).
- `--safe-mode` runs without installed mods, yours included.
- A policy check that throws or times out fails open unless its `.catch` returns a refusal (C-SEC-032, C-SEC-033).
- `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=0` does nothing on 2.1.287 and later (C-SEC-030).

## Recommendations

- Use `allowManagedModsOnly` rather than `disableAllHooks` when the goal is "no user mods"; it keeps managed hooks and users' settings hooks working. EVIDENCE-BASED
- Always pair a marketplace allowlist with `disableSideloadFlags`; the allowlist alone leaves `--plugin-dir` open. EVIDENCE-BASED
- Whenever you set `prependPlugins`, list `sec-default@builtin` in it. EVIDENCE-BASED
- Give every policy mod a fail-closed `.catch` on `plugin.register` and on any blocking hook. EVIDENCE-BASED
- Do not rely on a policy mod as the only control for crash or `--safe-mode` sessions; keep managed `PreToolUse` hooks and deny rules for must-hold rules. PRACTITIONER

> [!contradiction]
> Pluto advised admins to use `disableAllHooks` or `allowManagedHooksOnly`, saying mods are off unless an environment variable enables them (pluto-function-hooks, "If you administer Claude Code"). On 2.1.287 and later mods are on by default, the variable is ignored, and `allowManagedModsOnly` is the targeted control (docs-mods-admin). The docs win; Pluto's advice predates the guard options.

## Caveats

- Per-group policy has no key: server-managed settings deliver one configuration per organization (docs-plugins-org, "Plan for what managed settings can't enforce").
- sec-default behavior is from the admin page; the guard's source was not read in this lane.
- Server-managed delivery of `allowManagedModsOnly` has platform limits the admin page links but does not restate.

## Related

Ready-to-deploy policies live in [[Org Mod Policy Guide]]. The guard is profiled in [[Built-in sec-default Mod]], and chain order in [[Hook Ordering and Tiers]]. Distribution controls connect to [[Marketplaces and Distribution]], [[Claude Code Release Channels]], and [[Version Pin Policy]]. How mods sit beside settings hooks is in [[Mods vs Classic Hooks]]. Writing the guard mod itself follows [[Build a Tool Call Guard Flow]]. The threat picture is [[Mods Trust Model]].

## Sources

- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-plugins-org: https://code.claude.com/docs/en/plugins/org (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-plugins-security: https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)
- blog-mods-launch: https://claude.com/blog/claude-code-mods (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870#issuecomment-5542444779 (retrieved 2026-10-03)
- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)
