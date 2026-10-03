---
type: "flow"
title: "Publish a Mod Flow"
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
lane: "lifecycle"
related:
  - "[[Marketplaces and Distribution]]"
  - "[[Plugin Validate]]"
  - "[[Versioning and API Drift]]"
  - "[[Version Pin Policy]]"
  - "[[Testing Playbook]]"
  - "[[Mods Trust Model]]"
  - "[[Org Mod Controls]]"
  - "[[code-modernization Plugin]]"
  - "[[Re-verify After Release Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/publish (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/create-marketplace (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/host-marketplace (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/loading (retrieved 2026-10-03)"
sources:
  - "docs-plugins-publish"
  - "docs-plugins-create-marketplace"
  - "docs-plugins-host-marketplace"
  - "docs-plugins-loading"
  - "docs-plugins-manifest-reference"
  - "docs-plugins-marketplace-reference"
  - "docs-mods-create"
---

# Publish a Mod Flow

A mod is a plugin, so publishing it means listing it in a marketplace: a `.claude-plugin/marketplace.json` in a git repository that people add once and install from by `name@marketplace` (C-LIF-048, C-LIF-050). This recipe takes a working mod folder to a GitHub-hosted marketplace with a strict validation gate, a local install test, a version decision, a tag, and user instructions.

## Trigger

A mod works under `--plugin-dir`, has passing tests, and someone else (or another machine of yours) should install it and receive updates.

## Prerequisites

- The mod passes `claude plugin validate` and `claude plugin test` (see [[Testing Playbook]]).
- A permanent kebab-case `name` that validate does not reserve: no `claude-`, `anthropic-`, `anthropics-` or `cc-plugin-` prefix, not `claude-mods` or `claude-code` (C-LIF-019).
- A git repository and `git` on users' machines; a private repo makes a private marketplace (docs-plugins-publish).

## Steps

1. Fill in the metadata users see in `.claude-plugin/plugin.json`. `homepage` must parse as a URL or the plugin fails to load (docs-plugins-manifest-reference).

```json
{
  "name": "turn-band",
  "displayName": "Turn band",
  "version": "1.0.0",
  "description": "Shows the last turn's duration and tool calls above the prompt",
  "author": { "name": "Your Name" },
  "homepage": "https://github.com/your-org/turn-band",
  "repository": "https://github.com/your-org/turn-band",
  "license": "MIT",
  "keywords": ["mod", "band"],
  "types": "./types/index.d.ts"
}
```

2. Decide versioning now (C-LIF-044). Either bump `version` on every release (users stay on the cached copy until the string changes), or omit `version` in both the manifest and the entry so the 12-character commit SHA becomes the version. Never set it in both places: `plugin.json` wins silently and validate warns `Entry declares version` (C-LIF-045). See [[Version Pin Policy]].

3. Add a README with a tested-on line, because the API can change between releases and the docs name the README as the place to say so (docs-mods-create):

```markdown
### Compatibility
Tested on Claude Code 2.1.288 (typings header: "Written by Claude Code 2.1.288."). Re-verified 2026-10-03.
Requires Claude Code 2.1.287 or later.
```

4. Add the marketplace file beside `plugin.json` so the repository is its own marketplace, with `source` `"./"` and the entry `name` equal to the manifest `name` (C-LIF-049):

```bash
cd ~/mods/turn-band
cat > .claude-plugin/marketplace.json <<'JSON'
{
  "name": "your-mods",
  "description": "Mods by Your Name",
  "owner": { "name": "Your Name" },
  "plugins": [
    { "name": "turn-band", "source": "./", "description": "Last-turn band above the prompt" }
  ]
}
JSON
```

For several mods in one repo, put each under `plugins/<name>/` and use `"source": "./plugins/<name>"`, written from the folder that holds `.claude-plugin/`, never with `..` (C-LIF-048).

5. Validate strictly, as CI would. `--strict` turns warnings (unknown field, missing version or author) into exit 1 (C-LIF-020). Drop `--strict` only if you chose to omit `version`.

```bash
claude plugin validate --strict ~/mods/turn-band
claude plugin validate --strict --json ~/mods/turn-band | jq -e '.success'
cd ~/mods/turn-band && claude plugin test
```

6. Install from a local marketplace to catch what validate cannot: a missing source directory, a name mismatch, a reserved marketplace name (C-LIF-021).

```bash
claude plugin marketplace add ~/mods/turn-band
claude plugin install turn-band@your-mods
claude plugin list
claude plugin details turn-band
```

Start a session and confirm the `/plugin` line `1 mod active · turn-band` (docs-mods-overview). `plugin details` also prints the always-on token cost (C-LIF-054). Then remove the test install: `claude plugin marketplace remove your-mods` (it uninstalls its plugins).

7. Commit, tag, and push. A tag matters when other plugins declare a version range on yours; `claude plugin tag` creates `{name}--v{version}` and `--push` sends it to `origin` (C-LIF-047).

```bash
cd ~/mods/turn-band
git add -A && git commit -m "turn-band 1.0.0"
git push origin main
claude plugin tag --push
```

8. Tell users how to install (C-LIF-050):

```bash
claude plugin marketplace add your-org/turn-band
claude plugin install turn-band@your-mods
```

Or in a session: `/plugin marketplace add your-org/turn-band`, `/plugin install turn-band@your-mods`, then `/reload-plugins`; if it still does not show, restart Claude Code (claudedev-getting-started). Tell them auto-update is off by default for your marketplace and how to turn it on under `/plugin` Marketplaces (C-LIF-046).

9. Ship a later release: change code, bump `version` (or just push, if versionless), re-run steps 5 and 6, update the README tested-on line, tag. Users get it on `claude plugin update turn-band@your-mods` or auto-update.

## Outputs

- A repository that is both the plugin and its marketplace, a git tag `turn-band--v1.0.0`, and a README with a tested-on line.
- A verified local install path matching what users will run.

## Gates

- `claude plugin validate --strict` exits 0 for the plugin and the marketplace. EVIDENCE-BASED
- A local `marketplace add` plus `install` succeeds and the mod appears in the `mods active` line. EVIDENCE-BASED
- README states the Claude Code version you tested on. EVIDENCE-BASED
- For an Anthropic directory listing, a clean local validate is necessary but not sufficient: the portal adds its own rules and needs a paid plan (C-LIF-053). EVIDENCE-BASED

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `Plugin name "claude-x" is reserved` | Reserved prefix | Rename before first release (C-LIF-019) |
| `Plugin "<name>" not found in marketplace` | Entry name differs from manifest name | Make them equal (C-LIF-049) |
| `Source path does not exist: <path>` at install | Relative source points at a missing folder | Fix the path; validate passes this (C-LIF-021) |
| `<name> is already at the latest version (1.0.0).` | Pushed commits without a version bump | Bump `version` or omit it (C-LIF-044) |
| Users on an old copy after your push | Auto-update off, or session still running the loaded version | `claude plugin update`, `/reload-plugins` (C-LIF-046) |
| Installed users lost the plugin after a rename | Installs are recorded by name | Use the `renames` map; relabel with `displayName` (C-LIF-052) |

> [!contradiction]
> Docs say a relative-path plugin in a marketplace added from a local directory loads in place, so edits apply at the next session or `/reload-plugins` without a version bump (docs-plugins-create-marketplace, docs-plugins-loading). A Desktop user on 2.1.286 needed uninstall plus install each time (gh-issue-91870 comment 5943145826). Docs win for the terminal; treat Desktop as contested and develop with `--plugin-dir` (C-LIF-051, X-LIF-03).

## Rollback

- Bad release: revert the commit and publish a higher `version` (users only move forward on a changed version string), or point the entry's `ref`/`sha` at the last good commit to hold users there (C-LIF-047).
- Withdraw a plugin: remove its entry; set `forceRemoveDeletedPlugins: true` or map it to `null` in `renames` so installs are cleaned up (docs-plugins-marketplace-reference).
- Your own machine: `claude plugin marketplace remove your-mods`.

## Caveats

- Mods run with the user's permissions; say in the README what the mod hooks and calls (paste the validate inventory) so reviewers can audit it ([[Mods Trust Model]]).
- Organizations can block your marketplace or allow only managed mods (`allowManagedModsOnly`); see [[Org Mod Controls]].
- Steps 6 and 7 were not executed by this lane (no installs allowed); commands are from the official docs.

## Related

Distribution routes and hosting are in [[Marketplaces and Distribution]]; the version decision is [[Version Pin Policy]] and its background [[Versioning and API Drift]]. Gates use [[Plugin Validate]] and [[Testing Playbook]]; after each Claude Code release follow [[Re-verify After Release Flow]]. Trust and policy context: [[Mods Trust Model]], [[Org Mod Controls]]. For a published mod that ships from a marketplace repository, compare the [[code-modernization Plugin]] in Anthropic's official plugins repo.

## Sources

- docs-plugins-publish: https://code.claude.com/docs/en/plugins/publish (retrieved 2026-10-03)
- docs-plugins-create-marketplace: https://code.claude.com/docs/en/plugins/create-marketplace (retrieved 2026-10-03)
- docs-plugins-host-marketplace: https://code.claude.com/docs/en/plugins/host-marketplace (retrieved 2026-10-03)
- docs-plugins-loading: https://code.claude.com/docs/en/plugins/loading (retrieved 2026-10-03)
- docs-plugins-manifest-reference: https://code.claude.com/docs/en/plugins/manifest-reference (retrieved 2026-10-03)
- docs-plugins-marketplace-reference: https://code.claude.com/docs/en/plugins/marketplace-reference (retrieved 2026-10-03)
- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
