---
type: "entity"
title: "Built-in telemetry Mod"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/entity"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Mod Catalog]]"
  - "[[Mods API Namespaces]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Hook Middleware Chain]]"
  - "[[Usage Cost Surface]]"
  - "[[Plugin Validate]]"
  - "[[Built-in diff Mod]]"
  - "[[Built-in agents-md Mod]]"
  - "[[Mods Trust Model]]"
source_urls:
  - "https://github.com/anthropics/claude-code/tree/main/mods/telemetry (retrieved 2026-10-03, pinned 1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
sources:
  - "eco-gh-anthropics-mods"
  - "docs-mods-reference"
  - "docs-mods-overview"
  - "eco-gh-awesome-claude-code-mods"
---

# Built-in telemetry Mod

The telemetry mod (`cc-plugin-telemetry`) implements `$.telemetry.log` and `$.telemetry.mark` for Claude Code and its built-in mods, adding the noun in the `engine.create` fold and sending batched first-party analytics rows (C-ECO-015, C-ECO-017). It serves only the `builtin` and `core` tiers and refuses every installed plugin (C-ECO-016). For authors it matters for two reasons: it is the reference for a mod that extends `$` with typed nouns other mods call, and it explains why an installed mod's telemetry hook must name `{ to: 'collector' }`.

## Identity and pin

| Field | Value |
|---|---|
| Repo path | `anthropics/claude-code/mods/telemetry` |
| Pinned commit | `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528` (2026-10-02) |
| Manifest | `name: "telemetry"`, `version: "0.1.0"`, `"types": "./types/index.d.ts"` |
| Module | `./register.ts`, about 210 source files, 62 test files |
| Name in `/plugin` | `cc-plugin-telemetry`; disable in `/plugin` or turn analytics off (docs-mods-overview) |
| Code reviewed | static read of `register.ts`, README, gate and ingest URL |

## Events and calls

| Event | Purpose |
|---|---|
| `telemetry.*` | Gate: a caller outside `SERVED_TIERS = ['builtin', 'core']` is refused; a throwing gate refuses too |
| `telemetry.log` | Queues a `tengu_plugin_<event>` row; passes `to: 'collector'` entries beneath untouched |
| `telemetry.mark` | Queues a `tengu_feature_<kind>` row for `ok`, `sad` or `bad` |
| `engine.create` | Builds the sender over `await next(e)` and returns `{ ...{ telemetry }, ...beneath }` |
| `session.start` | Records interactivity |
| `session.end` | Flushes the queue |

Calls (through the interface `engine.create` hands it): `session.authorize`, `session.id`, `session.model`, `session.surfaces`, `session.cwd`, `session.repo`, `session.version`, `settings.read`, `env.get` (switches and describing variables by literal name), `fs.read`, `fs.list`, `fs.exists`, `process.run` (one `sh -c` of `uname` and `command -v`), `clock.after`, `clock.sleep`, `http.fetch`, `ui.log`. Reach L3: it reaches the network. Destination: `https://api.anthropic.com/api/event_logging/v2/batch` (C-ECO-017).

## The noun-contract pattern

The `engine.create` hook spreads `beneath` last, so an engine that already has `telemetry` keeps its own and this mod only fills a gap (C-ECO-015):

```ts
on('engine.create', async (_$, e, next) => {
  const beneath = await next(e)
  sender = telemetryOf({ /* adapters over beneath.* */ })
  const telemetry: EngineInterface['telemetry'] = sender.telemetry
  return { ...{ telemetry }, ...beneath }
})
```

The noun's types live in `types/index.d.ts`, which declares `$.telemetry` on `EngineInterface`; `mods/tsconfig.json` includes `*/types/**/*.d.ts` so other built-ins (diff, agents-md) type their calls against it (eco-gh-anthropics-mods, mods README). A test of a mod that calls the noun seats an inline provider plugin whose `engine.create` adds it.

## What it sends and when it sends nothing

- Each row carries an event id, device and account ids from the CLI's global config, session id, model, client type and an `env` block (platform, terminal, CI, deployment, VCS); secret-bearing variables are read only for whether they are set (telemetry README).
- Property values are restricted to numbers, booleans, or a "Choice" (a string with its list); free text is refused before queuing.
- It sends nothing under `DISABLE_TELEMETRY`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `DO_NOT_TRACK`, in a test run, on an unmanaged third-party provider, on a cloud gateway, or with a custom OAuth URL; switches are re-read before every batch (C-ECO-017).

## Why installed mods need `{ to: 'collector' }`

The docs say an installed mod's telemetry hook must carry `{ to: 'collector' }` or it fails `claude plugin validate`, and that a record is sent only when Claude Code or a built-in mod makes the call (docs-mods-reference). The scanner shows exactly that failure for this folder when validated as a third-party plugin on 2.1.287 (C-ECO-018).

## Recommendations

- Copy the `engine.create` spread-beneath shape and the single `types/index.d.ts` contract when your mod adds a noun for other mods. EVIDENCE-BASED
- Do not call `$.telemetry` from your own mod expecting data to reach you; installed callers are refused. EVIDENCE-BASED
- To stop analytics, prefer `DISABLE_TELEMETRY` or disabling `cc-plugin-telemetry` in `/plugin`; both are documented. EVIDENCE-BASED
- An org that runs an OpenTelemetry collector should hook `telemetry.log` with `{ to: 'collector' }`, never the bare event. EVIDENCE-BASED

## Caveats

- Verdict "adopt" in [[Mod Catalog]] means adopt as a reference design; whether to keep analytics on is a user choice.
- Row contents are described from the README; the full row builder (about 200 files) was sampled, not read line by line.
- The ingest URL and gate tiers are from source at 1c229fc and can change in any release.

## Related

- [[Mod Catalog]] row.
- [[Mods API Namespaces]] for where `$.telemetry` sits among nouns.
- [[Hook Ordering and Tiers]] and [[Hook Middleware Chain]] for tiers and `engine.create` folding.
- [[Usage Cost Surface]] and [[Mods Trust Model]] for network reach.
- [[Plugin Validate]] for the collector-filter rule.
- [[Built-in diff Mod]] and [[Built-in agents-md Mod]] are its callers.

## Sources

- eco-gh-anthropics-mods: https://github.com/anthropics/claude-code/tree/main/mods/telemetry (retrieved 2026-10-03, pinned 1c229fc)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- eco-gh-awesome-claude-code-mods: https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03, pinned 59a9911)
