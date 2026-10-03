---
title: "Claude Code plugins and hooks documentation"
author: "Anthropic"
publisher: "Anthropic (code.claude.com)"
year: "2026"
date: "unknown"
url: "https://code.claude.com/docs/en/plugins/overview"
source_capture: ".raw/captures/docs-2026-10-03/plugins-*.md (non-mods), hooks.md, hooks-guide.md"
retrieved: "2026-10-03"
confidence: "evidence-based"
tags:
  - "#domain/claude-code-mods"
  - "#type/canon"
  - "#source/official"
  - "#confidence/evidence-based"
---

# Claude Code plugins and hooks documentation (Anthropic, 2026)

The substrate mods sit on. Thirteen captured pages: plugins overview, components, manifest-reference, loading, security, publish, create-marketplace, host-marketplace, marketplace-reference, org, measure, plus hooks (reference, 3,838 lines) and hooks-guide. URLs follow https://code.claude.com/docs/en/<path>, for example https://code.claude.com/docs/en/plugins/security and https://code.claude.com/docs/en/hooks. Pages show no publish date.

## Core Thesis

A plugin is one installable, versioned unit of skills, agents, settings hooks, MCP and LSP servers, `bin/` executables, and, since 2.1.287, a hooks module (which makes it a mod). Everything a plugin runs, it runs as the user, outside the Bash sandbox, so trust is decided at the marketplace and install step, and organizations govern it through managed settings. Settings hooks remain first-class: they are separate processes fed JSON on stdin, and mods neither replace nor deprecate them.

## How It Works

**Plugins** (plugins-overview, plugins-loading, plugins-publish):

- A plugin must be present at three layers to work: settings (marketplace added, plugin enabled), disk (`~/.claude/plugins/`), session (loaded at startup or `/reload-plugins`).
- Scopes: user, project (committed `.claude/settings.json`), local.
- Version resolution: manifest `version`, then marketplace entry `version`, then the source (12-char commit SHA for github, url, git-subdir; SHA-256 for archive; `unknown` for npm and non-git local dirs). A pinned `version` keeps users on the cached copy however many commits you push.
- Release checklist: permanent kebab-case `name`, a versioning choice, `claude plugin validate --strict`, install from a local marketplace, metadata and README, optional `claude plugin eval`. Renames break installs unless the marketplace `renames` map migrates them. `claude plugin tag` makes `{name}--v{version}` tags for dependency ranges.
- `userConfig` fields (`string`, `number`, `boolean`, `directory`, `file`) prompt at enable time; `sensitive: true` stores in secure storage; values appear as `/config` rows (v2.1.269+).

**Trust** (plugins-security): marketplace names place a source in official, community, or third-party tiers, and official and community names are accepted only from `github.com/anthropics/`. The community catalog pins commits; archive sources can pin `sha256`. The `/plugin` details pane shows that a hook exists, not what it runs. Auto-update can change files after you reviewed them.

**Org controls** (plugins-org control matrix): `strictKnownMarketplaces`, `blockedMarketplaces`, `enabledPlugins`, `disableSideloadFlags`, `disableCommandPluginSources`, `allowManagedHooksOnly`, `strictPluginOnlyCustomization`, `pluginTrustMessage`, and `allowManagedModsOnly` (a guard option, not a top-level key). The allowlist does not cover `--plugin-dir`; `disableSideloadFlags` does.

**Settings hooks** (hooks, hooks-guide): 33 events in three cadences (session, turn, tool call) plus async standalone events. Five handler types: `command`, `http`, `mcp_tool`, `prompt`, `agent`. All matching hooks run in parallel; for `PreToolUse` the most restrictive decision wins (`deny`, `defer`, `ask`, `allow`). Exit 2 blocks and overrides JSON. Default timeouts: 600 s for command, http, mcp_tool; 30 s prompt; 60 s agent; `SessionEnd` shares 1.5 s. A timed-out `PreToolUse` command hook does not block the call. Interactive sessions hold settings hooks until workspace trust is accepted, but `-p` and SDK sessions treat the folder as trusted.

## Key Principles

1. Plugin code runs as you; permission rules and sandboxing govern Claude's tool calls, not code a plugin runs on its own.
2. Marketplace tier tells you who publishes the catalog, not what a plugin does: review every plugin.
3. Versioning is a delivery switch: pinned version means frozen users, omitted version means track commits.
4. Settings hooks merge in parallel (most restrictive wins); mods compose sequentially (outermost decides). These are different algebras.
5. A stalled settings hook is not a gate.
6. Managed settings lock policy; repository settings never set plugin order or org trust.

## Best Practices

- Run `claude plugin validate --strict` in CI before every release. EVIDENCE-BASED
- Decide versioning up front: increment `version` every release, or omit it in a git-hosted marketplace. EVIDENCE-BASED
- Never rename a published plugin; change `displayName`, or use `renames` if forced. EVIDENCE-BASED
- Before installing, check `claude plugin marketplace list` source, read `hooks/hooks.json`, `.mcp.json`, and `bin/`, then `claude plugin details`. EVIDENCE-BASED
- Before `claude -p` over an untrusted repo, review `.claude/` settings or run with `--bare` or `disableAllHooks`. EVIDENCE-BASED
- Do not use a settings hook timeout as a security gate on `PreToolUse`. EVIDENCE-BASED
- Pair `strictKnownMarketplaces` with `disableSideloadFlags` for a real lockdown. EVIDENCE-BASED
- Use `userConfig` with `sensitive: true` for any token a mod needs, never a plain settings value. PRACTITIONER

## Verified Quotes

- "can execute arbitrary code on your machine with your user privileges" (plugins-security, intro)
- "the files you reviewed can change on disk" (plugins-security, "Understand what a plugin can do", Updates)
- "Never change a published plugin's `name`." (plugins-publish, "Rename or remove a plugin")
- "Command hooks execute shell commands with your full user permissions." (hooks, "Security considerations")
- "Exit 2's block is the one outcome JSON can't override." (hooks, "Hook input and output", exit codes)
- "Claude Code runs all matching hooks in parallel" (hooks-guide, "How hooks work")

## Evidence Caveats

- `plugin details` disclosure for mods: plugins-security says the `Component inventory` lists "hooks with each hook's event", but does not say it lists a mod's function hooks. Pluto (005) reported "Hooks (0)" for a mod on 2.1.274. Unverified on 2.1.288; use `claude plugin validate` for mods.
- Only headings and key sections of hooks.md (3,838 lines) and components were read; per-event input schemas and decision fields were not reviewed line by line.
- Cloud sessions do not load local plugins; what carries over is documented on a page this lane did not capture.
- Version numbers in this set (v2.1.269, v2.1.271, v2.1.273) are minimums stated by the pages, not tested here.

## Brain Hooks

- [[Mods vs Classic Hooks]]: parallel merge versus middleware chain, exit codes, timeouts.
- [[Classic Hook Bridge]] and [[Migrate a Classic Hook Flow]]: settings hook events and their stdin JSON.
- [[Marketplaces and Distribution]] and [[Publish a Mod Flow]]: marketplace files, release checklist, renames.
- [[Versioning and API Drift]] and [[Version Pin Policy]]: version resolution order and cache behavior.
- [[userConfig and Plugin Options]]: field types, `sensitive`, `/config` rows.
- [[Org Mod Controls]] and [[Org Mod Policy Guide]]: control matrix and lockdown pairing.
- [[Mods Trust Model]] and [[Audit a Third-Party Mod Flow]]: marketplace tiers, review steps.
- [[Usage Cost Surface]]: context cost of skills, agents, and MCP tools from enabled plugins.
- [[Mod Directories]]: official, community, and third-party tiers.
