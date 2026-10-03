---
type: "platform"
title: "Claude Code Release Channels"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/platform"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Version Pin Policy]]"
  - "[[Versioning and API Drift]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Marketplaces and Distribution]]"
  - "[[Org Mod Controls]]"
  - "[[Mod Catalog]]"
  - "[[Publish a Mod Flow]]"
  - "[[Testing Playbook]]"
  - "[[Research Refresh Workflow]]"
source_urls:
  - "https://www.npmjs.com/package/@anthropic-ai/claude-code (npm view, retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/setup (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/host-marketplace (retrieved 2026-10-03)"
sources:
  - "eco-npm-dist-tags"
  - "eco-docs-setup"
  - "docs-mods-overview"
  - "docs-plugins-host-marketplace"
  - "types-2-1-288"
  - "eco-gh-playground-mods"
  - "claudedev-getting-started"
---

# Claude Code Release Channels

Claude Code ships on two update channels, `latest` (default) and `stable` (about a week behind, skipping releases with major regressions), selected by `autoUpdatesChannel` (C-ECO-053). On 2026-10-03 npm's dist-tags read `stable: 2.1.285`, `latest: 2.1.288`, `next: 2.1.288` (C-ECO-051). Mods are on by default only from 2.1.287 (docs-mods-overview), so as of this date the stable channel and the default Homebrew cask sit before the mods release (C-ECO-054, inference). Any mod README that says "2.1.287 or later" is implicitly telling stable-channel users to switch.

## Current versions (npm, 2026-10-03)

| dist-tag | Version | Published (UTC) |
|---|---|---|
| `stable` | 2.1.285 | 2026-09-29T17:32:09Z |
| `latest` | 2.1.288 | 2026-10-02T18:30:40Z |
| `next` | 2.1.288 | 2026-10-02T18:30:40Z |

Recent 2.1.28x history (C-ECO-052):

| Version | Published (UTC) | Mods relevance |
|---|---|---|
| 2.1.280 | 2026-09-22T15:44Z | playground samples built and tested here (eco-gh-playground-mods) |
| 2.1.281 | 2026-09-23T17:01Z | |
| 2.1.282 | 2026-09-24T15:56Z | |
| 2.1.283 | 2026-09-25T18:46Z | |
| 2.1.284 | 2026-09-28T17:11Z | cctop's `TESTED_WITH` |
| 2.1.285 | 2026-09-29T17:32Z | current `stable`; playground validates here |
| 2.1.286 | 2026-09-30T17:14Z | |
| 2.1.287 | 2026-10-01T16:59Z | mods on by default; flag ignored (docs-mods-overview) |
| 2.1.288 | 2026-10-02T18:30Z | current `latest` and `next`; typings in `.raw/captures/types-2.1.288/` |

Earlier community claims cluster on 2.1.269 to 2.1.276 (cc-pr-tracker, Arunjay4213, karanb192), all from the early-access period when `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` was required.

## How a user picks a channel

```json
{
  "autoUpdatesChannel": "stable",
  "minimumVersion": "2.1.287"
}
```

- `"latest"` is the default; `"stable"` is "typically about one week old" and skips releases with major regressions (eco-docs-setup).
- Set it in `/config` (Auto-update channel) or `settings.json`; managed settings can enforce it org-wide.
- `minimumVersion` is a floor: auto-updates and `claude update` refuse to install anything below it, so moving to stable does not downgrade a newer build. Switching to stable in `/config` offers to set this floor to the current version.
- Homebrew picks the channel by cask: `claude-code` tracks stable, `claude-code@latest` tracks latest.
- npm installs follow the dist-tag you install (`@anthropic-ai/claude-code@latest`, `@stable`).

## What this means for mods

- **Users on stable.** Until `stable` reaches 2.1.287 or later, mods are not on by default there (inference from C-ECO-051 and docs-mods-overview; not tested on 2.1.285). Pair `autoUpdatesChannel: "stable"` with `minimumVersion: "2.1.287"` to keep mods while taking the slower channel.
- **Authors.** State a tested-on version in the README and re-validate on each `latest`. cctop's CI (install `@latest`, diff the checked-in d.ts, `validate --strict`) is a working template; see [[Re-verify After Release Flow]].
- **Generated types follow the binary.** Each load writes the typings for the running build into the mod's `.claude-plugin/types/` (docs-mods-overview; claudedev-getting-started). A typings file "Written by Claude Code 2.1.288" is the authority for that build only.
- **Plugin versions are separate.** Claude Code has no release-channel concept for plugins; a publisher who wants stable and early tracks runs two marketplaces pointing at different refs (C-ECO-058).

## Recommendations

- Pin `minimumVersion` to 2.1.287 on any machine that depends on mods, whatever the channel. EVIDENCE-BASED
- Record the exact `claude --version` beside every mod verdict; this vault's catalog uses "tested on" per row. EVIDENCE-BASED
- Re-check npm dist-tags at each refresh; `stable` moving past 2.1.287 changes the default-on population. EVIDENCE-BASED
- For a team, enforce the channel and floor in managed settings rather than per-user. EVIDENCE-BASED

## Caveats

- dist-tags are a snapshot from 2026-10-03; `stable` typically moves weekly.
- Whether 2.1.285 loads mods with the old flag set was not tested; the playground's "validate passes on 2.1.285" suggests the API existed there behind early access.
- The `next` tag's semantics are not described in the docs captured here; it equals `latest` today.

## Related

- [[Version Pin Policy]] and [[Versioning and API Drift]] for pinning decisions.
- [[Re-verify After Release Flow]] and [[Testing Playbook]] for per-release checks.
- [[Marketplaces and Distribution]] and [[Publish a Mod Flow]] for plugin-side versioning.
- [[Org Mod Controls]] for managed channel enforcement.
- [[Mod Catalog]] for the tested-on column.
- [[Research Refresh Workflow]] for the 2026-11-02 recheck.

## Sources

- eco-npm-dist-tags: https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03; capture `captures/eco-npm-claude-code-dist-tags.md`)
- eco-docs-setup: https://code.claude.com/docs/en/setup (retrieved 2026-10-03; capture `captures/eco-docs-setup-channels.md`)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-plugins-host-marketplace: https://code.claude.com/docs/en/plugins/host-marketplace (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- eco-gh-playground-mods: https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods (retrieved 2026-10-03, pinned 569c528)
- claudedev-getting-started: https://claude.dev/blog/getting-started-with-claude-code-mods/ (retrieved 2026-10-03)
