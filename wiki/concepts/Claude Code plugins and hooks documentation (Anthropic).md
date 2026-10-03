---
type: "concept"
title: "Claude Code plugins and hooks documentation (Anthropic)"
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
  - "[[Classic Hook Bridge]]"
  - "[[Migrate a Classic Hook Flow]]"
  - "[[Marketplaces and Distribution]]"
  - "[[Publish a Mod Flow]]"
  - "[[Versioning and API Drift]]"
  - "[[Version Pin Policy]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Org Mod Controls]]"
  - "[[Mods Trust Model]]"
  - "[[Usage Cost Surface]]"
  - "[[Mod Directories]]"
  - "[[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/publish (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/org (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/host-marketplace (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/hooks-guide (retrieved 2026-10-03)"
sources:
  - "docs-plugins-security"
  - "docs-plugins-publish"
  - "docs-plugins-org"
  - "docs-plugins-measure"
  - "docs-plugins-loading"
  - "docs-plugins-host-marketplace"
  - "docs-plugins-manifest-reference"
  - "docs-hooks"
  - "docs-hooks-guide"
  - "types-2-1-288"
---

# Claude Code plugins and hooks documentation (Anthropic)

This note folds canon 006, the thirteen non-mods plugin and settings-hook pages captured on 2026-10-03, into the vault. They describe the substrate a mod sits on: a plugin is one versioned, installable unit that runs as the user outside the Bash sandbox, trust is decided at marketplace and install time, and organizations govern it through managed settings. They also define settings hooks, whose parallel, most-restrictive-wins algebra is the opposite of a mod chain. Trust it fully for packaging, versioning and org controls; it says little about mods themselves.

## What the work teaches

**Plugins.** A plugin must exist at three layers to work: settings (marketplace added, plugin enabled), disk (the plugins cache), and session (loaded at startup or `/reload-plugins`). Scopes are user, project and local.

**Versioning.** Version resolves from manifest `version`, then the marketplace entry `version`, then the source (12-character commit SHA for github, url and git-subdir; sha256 for archives; `unknown` for npm and non-git local folders). A pinned `version` keeps users on the cached copy however many commits you push (C-LIF-044).

**Release.** Permanent kebab-case `name`, `claude plugin validate --strict`, install from a local marketplace, `claude plugin tag` for `{name}--v{version}` tags. Renames break installs unless the marketplace `renames` map migrates them (C-LIF-052).

**Trust.** Official and community marketplace names are accepted only from `github.com/anthropics/` (C-SEC-048). Auto-update can change files after review (C-SEC-047).

**Org controls.** `strictKnownMarketplaces`, `blockedMarketplaces`, `enabledPlugins`, `disableSideloadFlags`, `allowManagedHooksOnly`, `strictPluginOnlyCustomization`, `pluginTrustMessage`; `allowManagedModsOnly` is a guard option, not a top-level key (C-SEC-023). The allowlist does not cover `--plugin-dir`; `disableSideloadFlags` does (C-SEC-027).

**Settings hooks.** 33 events, five handler types (`command`, `http`, `mcp_tool`, `prompt`, `agent`). All matching hooks run in parallel; for `PreToolUse` the most restrictive decision wins. Exit 2 blocks. Default timeouts: 600 s command, http, mcp_tool; 30 s prompt; 60 s agent; 1.5 s shared for `SessionEnd`. A timed-out `PreToolUse` command hook does not block (C-PAT-025).

## How its claims map onto vault notes

| Canon claim | Claim IDs | Vault home |
|---|---|---|
| Parallel merge versus serial chain | C-PAT-023 | [[Mods vs Classic Hooks]] |
| Every settings event is `classic.<Event>` | C-PAT-019 | [[Classic Hook Bridge]], [[Migrate a Classic Hook Flow]] |
| Stop hooks capped at 8 continuations | C-PAT-026 | [[Classic Hook Bridge]] |
| Version resolution and cache | C-LIF-010, C-LIF-044, C-LIF-045 | [[Versioning and API Drift]], [[Version Pin Policy]] |
| Marketplace files, install commands | C-LIF-048, C-LIF-050 | [[Marketplaces and Distribution]], [[Publish a Mod Flow]] |
| userConfig fields, `options` needs 2.1.271 | C-LIF-037, C-LIF-038 | [[userConfig and Plugin Options]] |
| Always-on context cost, hooks harness-only | C-LIF-054, C-SEC-043 | [[Usage Cost Surface]] |
| Plugin-level OTel name redaction | C-SEC-046 | [[Usage Cost Surface]] |
| Control matrix and sideload lock | C-SEC-023, C-SEC-027 | [[Org Mod Controls]] |
| Marketplace tiers | C-SEC-048 | [[Mod Directories]], [[Mods Trust Model]] |

## Agreement and contradiction

- **Agrees with the mods set** (canon 001): plugins and mods run as the user and outside the Bash sandbox (C-SEC-002), and the classic event list matches the typings: 33 classic events in the 2.1.288 surface ([[API Surface 2.1.288]]).
- **Two algebras.** This set says settings hooks merge in parallel; canon 001 says mods compose sequentially with the outermost deciding. They coexist: managed `PreToolUse` hooks run before the first mod and are final, and other `PreToolUse` hooks run inside the last mod's `next` (C-PAT-007, C-SEC-022).
- **Release channels.** Claude Code has no plugin release-channel concept; publishers run two marketplaces pointing at different refs (C-ECO-058, SINGLE-SOURCE). See [[Claude Code Release Channels]].

> [!contradiction] Does `plugin details` show a mod's hooks? This set says the `Component inventory` lists "hooks with each hook's event" (docs-plugins-security L104). Pluto reported "Hooks (0)" for a mod on 2.1.274 ([[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]]). The mods pages point reviewers to `claude plugin validate` instead. Unresolved on 2.1.288 (C-SEC-052); rely on validate.

- **Cost attribution gap.** The measure page ties the cost counter to skills and subagents; it does not say whether a mod's own `$.model.*` spend is attributed to its plugin (C-SEC-044, unverified).

## Verified quotes

Copied from `references/canon/006-claude-code-plugins-and-hooks-docs.md`; each re-found verbatim in `.raw/captures/docs-2026-10-03/`.

- "can execute arbitrary code on your machine with your user privileges" (plugins-security, capture L9)
- "the files you reviewed can change on disk" (plugins-security, capture L34)
- "Never change a published plugin's `name`." (plugins-publish, capture L166)
- "Exit 2's block is the one outcome JSON can't override." (hooks, capture L774)
- "Claude Code runs all matching hooks in parallel" (hooks-guide, capture L480)

## What it gets wrong or leaves stale

- **Mod blind spots.** It predates or ignores mods in places: the details inventory, cost measurement, and auto-update review warnings never say how they apply to a hooks module.
- **Version minimums** (v2.1.193 renames, v2.1.269 `/config` rows, v2.1.271 `options`) are stated by the pages and untested here.
- **Coverage.** Only headings and key sections of the 3,838-line hooks reference were read; per-event decision fields were not reviewed line by line.
- **Untrusted folders.** Interactive sessions hold settings hooks until workspace trust is accepted, but `-p` and SDK sessions treat the folder as trusted; for mods, admin docs say no mod loads in an untrusted folder until the prompt is answered (C-SEC-035, interactive only).

## How much to trust it

Confidence: evidence-based. Rank 1 official docs. Use it as the authority for packaging, versioning, marketplace trust, org settings, and settings-hook semantics. Do not use it for anything mod-specific; route that to canon 001 and the typings.

- Decide versioning up front: bump `version` every release, or omit it in a git-hosted marketplace. EVIDENCE-BASED
- Pair `strictKnownMarketplaces` with `disableSideloadFlags` for a real lockdown. EVIDENCE-BASED
- Never use a settings-hook timeout as a security gate on `PreToolUse`. EVIDENCE-BASED
- Store any token a mod needs in a `userConfig` field with `sensitive: true`. PRACTITIONER

## Caveats

- Pages are undated; the capture is of 2026-10-03.
- Cloud session plugin loading is on a page not captured.
- Version sensitivity: low for packaging rules, medium for anything touching mods.

## Related

Settings hooks versus mods: [[Mods vs Classic Hooks]], [[Classic Hook Bridge]], [[Migrate a Classic Hook Flow]]. Packaging: [[Marketplaces and Distribution]], [[Publish a Mod Flow]], [[userConfig and Plugin Options]]. Versions: [[Versioning and API Drift]], [[Version Pin Policy]]. Governance and trust: [[Org Mod Controls]], [[Mods Trust Model]], [[Mod Directories]]. Cost: [[Usage Cost Surface]].

## Sources

- Canon file: `references/canon/006-claude-code-plugins-and-hooks-docs.md`
- docs-plugins-security, docs-plugins-publish, docs-plugins-org, docs-plugins-measure, docs-plugins-loading, docs-plugins-host-marketplace, docs-plugins-manifest-reference: https://code.claude.com/docs/en/plugins/<page> (retrieved 2026-10-03), captures `.raw/captures/docs-2026-10-03/plugins-*.md`
- docs-hooks: https://code.claude.com/docs/en/hooks (retrieved 2026-10-03), capture `.raw/captures/docs-2026-10-03/hooks.md`
- docs-hooks-guide: https://code.claude.com/docs/en/hooks-guide (retrieved 2026-10-03), capture `.raw/captures/docs-2026-10-03/hooks-guide.md`
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (classic event count)
