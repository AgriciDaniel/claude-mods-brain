---
type: "decision"
title: "Version Pin Policy"
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
lane: "lifecycle"
related:
  - "[[Versioning and API Drift]]"
  - "[[Marketplaces and Distribution]]"
  - "[[Publish a Mod Flow]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Plugin Validate]]"
  - "[[Testing Playbook]]"
  - "[[Claude Code Release Channels]]"
  - "[[Mod Catalog]]"
  - "[[Research Refresh Workflow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/loading (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/host-marketplace (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/publish (retrieved 2026-10-03)"
sources:
  - "docs-plugins-loading"
  - "docs-plugins-host-marketplace"
  - "docs-plugins-publish"
  - "docs-mods-create"
  - "types-2-1-288"
  - "code-modernization-1-0-0"
---

# Version Pin Policy

Decision: every published mod pins a semver `version` in `plugin.json` only (never also in the marketplace entry), bumps it on every release, records the Claude Code build it was tested on in its README and CHANGELOG, and checks `$.session.version()` at `session.start` to warn below its tested minimum. Bumping is the only thing that moves users off a cached copy (C-LIF-044), and the mods API changes between releases without notice (C-LIF-043), so the two version axes (the mod's and Claude Code's) are tracked separately and explicitly.

## Context

There are two versions to manage:

| Axis | Who controls it | What enforces it |
|---|---|---|
| The mod's own version | author, via `plugin.json` `version` or source SHA | Claude Code's update check compares computed versions (C-LIF-044) |
| The Claude Code build the mod was written against | user's install | nothing in the manifest: the captured docs describe no engine-version field for mods |

The docs say the README is the place to say which Claude Code version you tested with (docs-mods-create, Share your mod). The typings carry `EARLY ACCESS: this surface may change between releases without notice` (types 2.1.288 L1-10), and even Anthropic's code-modernization 1.0.0 trails its build (C-LIF-059).

## Options considered

### A. Pin `version` in plugin.json and bump each release

- Users stay on the cached copy until the string changes; `claude plugin update` then installs the new one (C-LIF-044, C-LIF-046).
- Risk: forgetting to bump means `<name> is already at the latest version` and nobody gets the fix (docs-plugins-publish).
- Works with `validate --strict`, which warns on a missing `version` (C-LIF-020).

### B. Omit `version` and track the commit SHA

- Version becomes the 12-character commit SHA for git sources, so every push is an update (C-LIF-044).
- Must drop `--strict` in CI, since a missing version is a warning (docs-plugins-publish).
- No human-readable release line; CHANGELOG entries cannot name a version.

### C. Pin `ref` / `sha` on the marketplace entry

- Holds every user on one commit or tag of a git source (C-LIF-047).
- Good for a stable channel beside a latest channel; Claude Code has no channel concept, so channels are two marketplaces (docs-plugins-host-marketplace).
- Does not replace a version string: updates are still detected by computed version.

### D. Tested-on Claude Code version in README

- Zero cost, documented by Anthropic as the place for it (docs-mods-create).
- Advisory only: nothing stops a user on an older or newer build.

### E. Runtime minimum-version guard

`$.session.version()` resolves `{ version, base?, builtAt? }` (C-LIF-058). A guard can warn rather than fail:

```ts
import type { Register } from 'claude-code'

const TESTED_ON = [2, 1, 288] as const

const parse = (v: string) => v.split(/[.-]/).slice(0, 3).map(Number)

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const { version } = await $.session.version()
    const [a = 0, b = 0, c = 0] = parse(version)
    const [x, y, z] = TESTED_ON
    if (a * 1e6 + b * 1e3 + c < x * 1e6 + y * 1e3 + z) {
      $.ui.toast(`${$.plugin.name} was tested on 2.1.288; you run ${version}`)
    }
    return next(e)
  })
}
```

- Catches the "works on my build" case at the person's screen. Adds one `$.session.version` and one `$.ui.toast` to the validate inventory.

## Decision

Adopt A + D + E together; use C only when a stable channel is needed. Reject B for published mods.

1. `plugin.json` holds `"version": "MAJOR.MINOR.PATCH"`; the marketplace entry holds no `version` (setting both makes `plugin.json` win silently and validate warns, C-LIF-045).
2. Every release bumps the version and adds a CHANGELOG line, as code-modernization's CHANGELOG states is the only way users are offered an update.
3. README carries a "Tested on Claude Code 2.1.x (date)" line, updated by the re-verify flow.
4. `session.start` warns below the tested minimum; it never refuses to load.
5. A major bump marks a change a user must act on (new userConfig field, new required option, removed command).

## Rationale

- Explicit versions keep CI on `--strict` and make "which build has the fix" answerable. EVIDENCE-BASED
- A runtime warning is the only Claude Code version signal a user actually sees. PRACTITIONER
- The engine axis cannot be enforced in the manifest per the captured docs, so README plus guard is the ceiling. EVIDENCE-BASED
- Local-directory marketplaces ignore `version` and load in place (C-LIF-051), so the policy matters only for git, URL and archive hosted mods. EVIDENCE-BASED

## Consequences

- Each release costs one bump commit and optionally a `claude plugin tag` (C-LIF-047).
- Users without auto-update need `claude plugin update`; third-party marketplaces default auto-update off (C-LIF-046).
- A userConfig field with `options` raises the effective minimum to 2.1.271 (C-LIF-038); record that in the README too.

## Re-verify trigger

Run [[Re-verify After Release Flow]] when any of these happen: a new Claude Code release reaches the machine (`claude --version` changes), the first line of `.claude-plugin/types/claude-code/index.d.ts` names a new build, or a user reports a skipped hook. Refresh by 2026-11-02 regardless.

## Caveats

- The guard compares only the numeric core; a dev build string such as `2.1.280-dev...` parses to its base.
- Whether a future manifest adds an engine-version field is unknown; check `manifest-reference` on refresh.
- Desktop may hold stale in-place copies (X-LIF-03), outside this policy's reach.

## Related

The drift this guards against is described in [[Versioning and API Drift]], and the hosting mechanics in [[Marketplaces and Distribution]]. Apply it in [[Publish a Mod Flow]] and refresh it through [[Re-verify After Release Flow]] and [[Research Refresh Workflow]]. CI gates come from [[Plugin Validate]] and [[Testing Playbook]]. Build channels are in [[Claude Code Release Channels]]. The policy feeds the tested-on column of [[Mod Catalog]].

## Sources

- docs-plugins-loading: https://code.claude.com/docs/en/plugins/loading (retrieved 2026-10-03)
- docs-plugins-host-marketplace: https://code.claude.com/docs/en/plugins/host-marketplace (retrieved 2026-10-03)
- docs-plugins-publish: https://code.claude.com/docs/en/plugins/publish (retrieved 2026-10-03)
- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- types-2-1-288: local .raw/captures/types-2.1.288/claude-code/index.d.ts (retrieved 2026-10-03)
- code-modernization-1-0-0: local .raw/captures/official-mods/code-modernization-1.0.0/ (retrieved 2026-10-03)
