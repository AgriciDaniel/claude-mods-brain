---
type: "concept"
title: "Marketplaces and Distribution"
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
lane: "lifecycle"
related:
  - "[[Publish a Mod Flow]]"
  - "[[Version Pin Policy]]"
  - "[[Versioning and API Drift]]"
  - "[[Plugin Validate]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Org Mod Controls]]"
  - "[[Mods Trust Model]]"
  - "[[Mod Directories]]"
  - "[[Usage Cost Surface]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/publish (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/create-marketplace (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/host-marketplace (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/marketplace-reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/loading (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)"
sources:
  - "docs-plugins-publish"
  - "docs-plugins-create-marketplace"
  - "docs-plugins-host-marketplace"
  - "docs-plugins-marketplace-reference"
  - "docs-plugins-loading"
  - "docs-plugins-measure"
  - "claudedev-getting-started"
  - "gh-issue-91870"
---

# Marketplaces and Distribution

A mod is a plugin, so it ships the way any plugin does: as a folder people load with `--plugin-dir`, through a marketplace (a git repo or URL holding `.claude-plugin/marketplace.json`), or through Anthropic's directory (docs-plugins-publish). Publishing to your own marketplace needs no submission: once the file is in the repo, the plugin is installable as `<name>@<marketplace>` (C-LIF-050). Updates reach users only when the computed version changes, and auto-update is off by default for third-party marketplaces (C-LIF-044, C-LIF-046).

## Routes

| Route | Who installs | Needs | Updates |
|---|---|---|---|
| No marketplace | people you send the folder or `.zip` | the folder; they run `claude --plugin-dir` or drop it under `~/.claude/skills/` | none, they reload what you sent |
| Own marketplace | anyone who can reach the repo (private repo, private marketplace) | `.claude-plugin/marketplace.json` listing the plugin | `claude plugin update` or opt-in auto-update |
| Anthropic's directory | claude.ai and Cowork users, synced into Claude Code as `<name>@synced` | GitHub repo plus paid claude.ai plan, developer portal review (C-LIF-053) | yes, after review |

## marketplace.json essentials

```json
{
  "name": "my-mods",
  "owner": { "name": "Your Name" },
  "description": "Personal Claude Code mods",
  "plugins": [
    { "name": "my-guard", "source": "./plugins/my-guard", "description": "Command guard" }
  ]
}
```

- Required: `name`, `owner` (with `name`), `plugins`; each entry needs `name` and `source` (C-LIF-048).
- A relative source is written from the marketplace root, the folder that holds `.claude-plugin/`, and may not contain `..` (C-LIF-048).
- Keep the entry `name` equal to the plugin's own `name`, or installs by the manifest name fail with `Plugin "<name>" not found in marketplace` (C-LIF-049).
- Unknown keys are ignored at load and only warned by validate, so typos load silently (docs-plugins-marketplace-reference).
- Other top-level fields: `metadata.pluginRoot`, `forceRemoveDeletedPlugins`, `allowCrossMarketplaceDependenciesOn`, `renames`.

## Plugin sources

| `source` | Use | Version when none set |
|---|---|---|
| `"./plugins/x"` | inside the marketplace repo | commit SHA of the dir (git-hosted) or `unknown` (plain local dir) |
| `{ "source": "github", "repo", "ref"?, "sha"? }` | own repo | 12-char commit SHA |
| `{ "source": "git-subdir", "url", "path" }` | monorepo folder | SHA plus path hash |
| `url` | any git host | 12-char commit SHA |
| `archive` | HTTPS zip, optional `sha256` | 12-char digest |
| `npm` | npm package | `unknown` |
| `command` | directory a local command prints | always hash of output |

Version precedence: manifest `version`, then entry `version`, then the source column (C-LIF-044). Set it in one place only; both set means `plugin.json` wins and validate warns (C-LIF-045).

## User-side commands

```bash
claude plugin marketplace add your-org/your-marketplace   # or a URL or a path
claude plugin install my-guard@your-marketplace
claude plugin update my-guard@your-marketplace
claude plugin list
claude plugin details my-guard
```

In a session: `/plugin marketplace add`, `/plugin install`, then `/reload-plugins`; restart if the mod still does not appear (claudedev-getting-started). `--scope project` on the add writes `.claude/settings.json` so a whole repo registers the marketplace (docs-plugins-host-marketplace).

## In place versus copied

- `--plugin-dir` and skills-folder plugins load in place and are never copied (docs-plugins-loading).
- Relative-path plugins in a marketplace added from a local directory load in place, so edits apply at the next session or `/reload-plugins` with no bump (C-LIF-051).
- Everything else is copied into `cache/<marketplace>/<plugin>/<version>/`; files above the plugin root are not copied, and component paths escaping the root are rejected (docs-plugins-loading).

> [!contradiction]
> Docs: an in-place local marketplace plugin picks up edits on `/reload-plugins` (docs-plugins-create-marketplace). A #91870 report on Desktop bundling 2.1.286 says Desktop kept the install-time copy and needed uninstall plus install (comment 5943145826). Docs win for the terminal; treat Desktop as contested and develop with `--plugin-dir` (X-LIF-03).

## Updates and channels

- Auto-update is on by default only for Anthropic's official marketplaces and claude.ai-added ones; users toggle it under `/plugin` Marketplaces, or admins set `autoUpdate` in `extraKnownMarketplaces` (docs-plugins-loading).
- The pass runs after a random delay of up to ten minutes after the first message; the session keeps its loaded version until `/reload-plugins` (C-LIF-046).
- Hold users with `ref`/`sha`, `#<ref>` on the add, or `<plugin>--v<version>` tags from `claude plugin tag --push` (C-LIF-047).
- Release channels are two marketplaces with different `name` values pointing at different refs; Claude Code has no channel concept (docs-plugins-host-marketplace).

## Names, renames, reserved names

- Plugin names starting `claude-`, `anthropic-`, `anthropics-` or `cc-plugin-` fail validate (C-LIF-019).
- Marketplace names such as `claude-plugins-official`, `inline`, `builtin`, `skills-dir`, `synced`, `npm`, `github`, and any `claudeai-` prefix are reserved; exact official names pass validate and fail only at `marketplace add` (C-LIF-021).
- Never rename a published plugin; use `renames` (v2.1.193+) and change `displayName` for labels (C-LIF-052).

## Measuring a published mod

`claude plugin details <name>` reports always-on token cost from skill, agent and command descriptions, and lists hooks as harness-only with no model-context cost (C-LIF-054). Authors get no usage telemetry back; only each user's `/plugin`, `/skill-doctor`, `/doctor` and `/usage` show it (docs-plugins-measure). Whether function-hook mods appear in that inventory the same way is not shown in the captured docs.

## Recommendations

- Use one git repo as both code and marketplace, with relative sources. EVIDENCE-BASED
- Run `claude plugin validate .` on the marketplace root and on each plugin before every push. EVIDENCE-BASED
- Install from a local marketplace once before sharing, since validate misses missing source dirs. EVIDENCE-BASED
- Tell users to enable auto-update or give them the `claude plugin update` line in release notes. EVIDENCE-BASED
- Read a third-party mod's source before adding its marketplace. PRACTITIONER

## Caveats

- Directory-portal rules are not in the captured docs (C-LIF-053).
- Desktop in-place reload behavior is contested.
- Fetch errors only surface at install, never in validate.

## Related

The step-by-step release is [[Publish a Mod Flow]], with version choices in [[Version Pin Policy]] and cache drift in [[Versioning and API Drift]]. Pre-push checks are [[Plugin Validate]]; local iteration stays in [[Hot Reload and Dev Loop]]. Admin limits on marketplaces are in [[Org Mod Controls]], and install risk in [[Mods Trust Model]]. Public listings are tracked in [[Mod Directories]] and [[Mod Catalog]], and context cost in [[Usage Cost Surface]].

## Sources

- docs-plugins-publish: https://code.claude.com/docs/en/plugins/publish (retrieved 2026-10-03)
- docs-plugins-create-marketplace: https://code.claude.com/docs/en/plugins/create-marketplace (retrieved 2026-10-03)
- docs-plugins-host-marketplace: https://code.claude.com/docs/en/plugins/host-marketplace (retrieved 2026-10-03)
- docs-plugins-marketplace-reference: https://code.claude.com/docs/en/plugins/marketplace-reference (retrieved 2026-10-03)
- docs-plugins-loading: https://code.claude.com/docs/en/plugins/loading (retrieved 2026-10-03)
- docs-plugins-measure: https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
