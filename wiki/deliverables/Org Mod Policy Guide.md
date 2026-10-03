---
type: "deliverable"
title: "Org Mod Policy Guide"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/deliverable"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "security-governance"
related:
  - "[[Org Mod Controls]]"
  - "[[Built-in sec-default Mod]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Build a Tool Call Guard Flow]]"
  - "[[Marketplaces and Distribution]]"
  - "[[Claude Code Release Channels]]"
  - "[[Version Pin Policy]]"
  - "[[Mod Catalog]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/org (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)"
sources:
  - "docs-mods-admin"
  - "docs-plugins-org"
  - "docs-mods-troubleshoot"
  - "docs-mods-reference"
  - "docs-plugins-measure"
  - "types-2-1-288"
  - "secgov-validate-probes"
---

# Org Mod Policy Guide

Pick one of four policies, deploy its managed settings, then verify on a test machine with `claude --debug`. The default for most organizations is **Policy B, only our mods**: users' own mods are refused by the built-in guard's `allowManagedModsOnly`, side-loading is off, and any mod you want is vendored into a directory marketplace you control after it passes the [[Audit a Third-Party Mod Flow]]. Every key name below is spelled exactly as the admin and org pages spell it (docs-mods-admin; docs-plugins-org). Background on each control is in [[Org Mod Controls]].

## Choose a policy

| Policy | Who it fits | Users' own mods | Org mods | Keys |
|---|---|---|---|---|
| A. No installed mods | Regulated or not ready to review | Refused | None | `pluginConfigs` guard option, `disableSideloadFlags` |
| B. Only our mods (default) | Most orgs | Refused | Yes, first | A plus `extraKnownMarketplaces` (directory), `enabledPlugins`, `prependPlugins` |
| C. Reviewed marketplaces, guarded | Orgs with a review pipeline | Allowed from allowlisted, pinned marketplaces, checked by your policy mod | Yes, first | allowlist, `disableSideloadFlags`, `autoUpdate: false`, `prependPlugins` |
| D. Everything off | Incident response | Refused | Refused | `disableAllHooks` (also stops managed hooks) |

Do not use D as a steady state: in managed settings it stops your own managed `PreToolUse` hooks from blocking anything (docs-mods-admin, "Choose how much to allow").

## Policy A: no installed mods

```json
{
  "pluginConfigs": {
    "cc-plugin-sec-default@builtin": { "options": { "allowManagedModsOnly": true } }
  },
  "disableSideloadFlags": true
}
```

Users keep their settings hooks, status lines, and `/goal`; built-in mods keep running (docs-mods-admin). Add your marketplace allowlist if you also want to limit non-mod plugins.

## Policy B: only our mods

The admin page's complete example, with the guard kept second (docs-mods-admin, "Allow only your organization's mods"):

```json
{
  "extraKnownMarketplaces": {
    "acme-tools": { "source": { "source": "directory", "path": "/opt/acme/claude-plugins" } }
  },
  "enabledPlugins": { "acme-guard@acme-tools": true },
  "prependPlugins": ["acme-guard@acme-tools", "sec-default@builtin"],
  "pluginConfigs": {
    "cc-plugin-sec-default@builtin": { "options": { "allowManagedModsOnly": true } }
  },
  "disableSideloadFlags": true
}
```

Requirements for a mod to count as yours: managed `enabledPlugins` true, the marketplace named by absolute directory path in managed settings, and the plugin listed by relative path so it loads in place. MDM must copy the directory to the same path on every machine, writable only by administrators. A plugin from GitHub, git, URL, or npm counts as a user's even when you enable it (docs-mods-admin) (C-SEC-026).

## Policy C: reviewed marketplaces, guarded

Users may install mods only from marketplaces you allowlist; your policy mod refuses any user-tier mod whose provenance and version are not on the reviewed list.

```json
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "anthropics/claude-plugins-official" },
    { "source": "github", "repo": "acme/approved-mods" },
    { "source": "directory", "path": "/opt/acme/claude-plugins" }
  ],
  "extraKnownMarketplaces": {
    "acme-tools": { "source": { "source": "directory", "path": "/opt/acme/claude-plugins" } },
    "acme-approved": { "source": { "source": "github", "repo": "acme/approved-mods" }, "autoUpdate": false }
  },
  "enabledPlugins": { "acme-guard@acme-tools": true },
  "prependPlugins": ["acme-guard@acme-tools", "sec-default@builtin"],
  "disableSideloadFlags": true
}
```

Allowlist entry syntax and the `autoUpdate` field come from docs-plugins-org ("Allowlist with strictKnownMarketplaces", "Set update policy"). A `github` entry without `ref` does not cover a source with a `ref` (docs-plugins-org, "How entries match").

The policy mod (`/opt/acme/claude-plugins/plugins/acme-guard/hooks/register.js`), validated statically on 2.1.288 with `hooks: plugin.register, http.fetch, process.run` and `calls: $.ui.log`:

```javascript
// Reviewed user mods: provenance (name@marketplace) -> audited version
const REVIEWED = { 'token-meter@acme-approved': '1.2.0', 'pr-tracker@acme-approved': '0.2.0' }

async function checkMod($, e, next) {
  if (e.tier !== 'user') return next(e)
  if (REVIEWED[e.provenance] && REVIEWED[e.provenance] === e.version) return next(e)
  return { refuse: 'Acme policy: ' + e.provenance + ' ' + (e.version ?? '?') + ' is not on the reviewed list' }
}

export function register(on) {
  on('plugin.register', checkMod).catch(async ($, e, next) => {
    if (e.tier !== 'user') return next(e)
    return { refuse: 'Acme policy check failed, so this mod was not loaded' }  // fail closed
  })
  on('http.fetch', async ($, e, next) => {   // audit every later mod's network call
    $.ui.log('audit http.fetch by ' + next.origin.plugin + ' ' + JSON.stringify(e.url), { to: 'debug' })
    return next(e)
  })
  on('process.run', async ($, e, next) => {  // and every program it starts
    $.ui.log('audit process.run by ' + next.origin.plugin + ' ' + JSON.stringify(e.argv), { to: 'debug' })
    return next(e)
  })
}
```

Fields used: `e.tier`, `e.provenance` (`<name>@<marketplace>`), `e.version` (types 2.1.288 L7207-7234); `next.origin.plugin` (docs-mods-reference). Pinning by manifest `version` trusts the author to bump it; for stronger pinning, vendor reviewed mods into the directory marketplace (Policy B). The fail-closed `.catch` is the documented pattern (docs-mods-admin, "Refuse mods when your check fails").

## Verify on a test machine

| Check | Expected | Source |
|---|---|---|
| `/status` | `Enterprise managed settings` in `Setting sources` | docs-plugins-org, "Troubleshoot policy" |
| `claude --debug`, your mod | `hooks module acme-guard@acme-tools loaded` with `tier prepend` | docs-mods-admin |
| Same, if misconfigured | `tier user` plus `prependPlugins names ... skipped` | docs-mods-admin |
| A user mod under A or B | Line containing `refused by cc-plugin-sec-default: mods are limited to your organization's by policy (allowManagedModsOnly)` | docs-mods-admin; docs-mods-troubleshoot |
| `claude --plugin-dir ./any-mod` | Exits with `--plugin-dir is disabled by your organization's managed settings (disableSideloadFlags)` | docs-mods-admin |
| A user mod approving a denied call | Call stays denied; message contains `tried to lift a deny rule in your settings` | docs-mods-troubleshoot |

## Rollout

1. Pilot group first. Server-managed settings apply one configuration per organization, so use endpoint-managed settings or gateway policy for a pilot (docs-plugins-org, "Plan for what managed settings can't enforce").
2. Announce what changes: users' own mods stop loading under A and B; their settings hooks keep working.
3. Publish the review path: requests go through [[Audit a Third-Party Mod Flow]]; adopted mods land in [[Mod Catalog]] and the directory marketplace.
4. Watch adoption with `claude_code.plugin_loaded` and the Analytics API; third-party names are `third-party` unless `OTEL_LOG_TOOL_DETAILS=1` (docs-plugins-measure) (C-SEC-046).
5. Re-verify after each Claude Code release; the mods surface is early access (types 2.1.288 L4).

## Recommendations

- Start with Policy B even if you have no mods yet; adding one later is a directory copy and two managed entries. PRACTITIONER
- Never set `prependPlugins` without `sec-default@builtin` in it. EVIDENCE-BASED
- Leave `allowModsToOverrideDenyRules` unset. EVIDENCE-BASED
- Keep must-hold rules in managed `PreToolUse` hooks and deny rules, not only in a policy mod; a crashed worker or `--safe-mode` removes mods. EVIDENCE-BASED
- Make the marketplace directory and every parent writable only by administrators. EVIDENCE-BASED

## Caveats

- Keys and messages are from docs captured 2026-10-03 for 2.1.288; nothing here was deployed. The policy mod and guard were validated statically only.
- Delivery of the guard option from the claude.ai admin console has platform limits the admin page links but does not restate.
- `e.version` is self-declared by the plugin's manifest.

## Related

Control-by-control detail: [[Org Mod Controls]] and [[Built-in sec-default Mod]]. Review pipeline: [[Audit a Third-Party Mod Flow]], [[Mod Security Audit Checklist]], [[Mod Catalog]]. Writing your own guard: [[Build a Tool Call Guard Flow]]. Distribution and pinning: [[Marketplaces and Distribution]], [[Version Pin Policy]], [[Claude Code Release Channels]].

## Sources

- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-plugins-org: https://code.claude.com/docs/en/plugins/org (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-plugins-measure: https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md`
