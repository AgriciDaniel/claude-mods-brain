---
type: "entity"
title: "karanb192 claude-code-mods"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.276"
tags:
  - "#domain/claude-code-mods"
  - "#type/entity"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Mod Catalog]]"
  - "[[Mod Directories]]"
  - "[[Reach Levels]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Usage Cost Surface]]"
  - "[[Agent and Command Events]]"
  - "[[Plugin Validate]]"
  - "[[Classic Hook Bridge]]"
  - "[[Mod Security Audit Checklist]]"
source_urls:
  - "https://github.com/karanb192/claude-code-mods (retrieved 2026-10-03, pinned 9d73de721ed7e53b88ff24618f266c8082bfed76)"
  - "https://github.com/karanb192/cache-tax (retrieved 2026-10-03, pinned 2b51ee46ddac789a58170453439838c3a26e134b)"
  - "https://github.com/anthropics/claude-code/issues/91870#issuecomment-5715941633 (retrieved 2026-10-03)"
sources:
  - "eco-gh-karanb192-mods"
  - "eco-gh-cache-tax"
  - "eco-static-scan"
  - "eco-gh-awesome-claude-code-mods"
  - "gh-issue-91870"
  - "docs-mods-overview"
---

# karanb192 claude-code-mods

karanb192/claude-code-mods is a marketplace with one skill and two mods: `mod-builder` (a skill that plans a mod's "capability budget", validates it, and writes a five-line threat model), `fable-pin` (a 36-line mod that pins every non-fork subagent to the `fable` model), and `cache-tax` (now maintained in `karanb192/cache-tax`, still installed from this marketplace) (C-ECO-036). The same author runs the footprint scanner behind [[Mod Directories]]' best list. The mods are small and well documented; cache-tax is the one with real cost, because its keep-warm pings call the model (C-ECO-039).

## Identity and pins

| Field | claude-code-mods | cache-tax |
|---|---|---|
| Repo | `karanb192/claude-code-mods`, MIT, 33 stars | `karanb192/cache-tax`, MIT, 39 stars |
| Pinned commit | `9d73de721ed7e53b88ff24618f266c8082bfed76` (2026-10-02T09:40:39Z) | `2b51ee46ddac789a58170453439838c3a26e134b` (2026-09-20T11:38:49Z) |
| Release | none tagged | v2.1.3 (2026-09-18) |
| Tested-on claim | templates and hello-mod "validated on 2.1.272" | "Validated on Claude Code 2.1.276" |
| Install | `claude plugin marketplace add karanb192/claude-code-mods`; `claude plugin install <name>@claude-code-mods` | same marketplace |
| Code reviewed | static read: fable-pin `register.ts`, mod-builder `SKILL.md` and scripts | static read: `hooks/register.ts`, README |

## fable-pin

```ts
on('agent.spawn', async ($, e, next) => {
  if (!enabled || e.fork || e.model === TARGET) return next(e)
  return next({ ...e, model: TARGET })
})
```

Events: `session.start`, `command.run {command:'fable-pin'}`, `agent.spawn`. Calls: `command.register`, `store.get`, `store.set`. Reach L0 (persists state) per scanner and scan (C-ECO-037). Usage cost: no calls of its own, but every subagent now runs on the pinned model, which changes spend in whichever direction that model's price goes. Forks are skipped because they inherit the parent's model.

## cache-tax

| Item | Detail |
|---|---|
| Events | `session.start`, `classic.SessionStart`, `command.run` (`keepwarm`, `cache-tax`), `prompt.submit`, `turn.step`, `turn.complete`, `session.compact` |
| Calls | `clock.after`, `clock.now`, `command.list`, `command.register`, `model.fork`, `session.id`, `session.model`, `session.usage`, `store.delete`, `store.get`, `store.set`, `ui.log`, `ui.status` |
| Keep-warm | after 50 idle minutes inside an armed window, one tool-less `$.model.fork` over the transcript; stops if reads are zero or writes reach 10% of reads |
| Guard | drops the first cold send once (for 50k+ token contexts) with an estimated rewrite price; the resend goes through |
| Reach | L2, drives Claude (scanner and README agree) |

Usage cost: model calls. The README states pings "cost tokens, including uncapped output", and that how a cache read counts against subscription limits "is not documented anywhere I could find" (eco-gh-cache-tax). It also hooks `classic.SessionStart` from the module, a live example of [[Classic Hook Bridge]].

## mod-builder

- Modes: build, brainstorm, review, discover, migrate, debug, publish. Build mode shows the planned surface and reach level and waits for a yes before writing files.
- `scripts/footprint.mjs` runs the validator and exits 1 when the printed `calls:` line widens beyond the plan; `scripts/list-mods.mjs` fetches the nightly scan (network).
- `SKILL.md` checks whether the user starred the repo with `gh api` and offers to star it, acting only after an explicit yes; the offer is recorded once in `~/.cache/claude-code-mods/star-invitation.json` (C-ECO-038).
- Its `references/gotchas.md` item 1 says nothing loads without the flag, which is stale on 2.1.287+ (C-ECO-036, docs-mods-overview).

## Recommendations

- Trial mod-builder's footprint script as a CI gate: diffing the validator's `calls:` line against a plan catches silent reach growth. PRACTITIONER
- Avoid cache-tax unless you accept per-ping model spend and run a one-hour main cache; on API keys set `promptCacheTtl` to `"1h"` first, as its README says. EVIDENCE-BASED
- Trial fable-pin only if you mean to move all subagents to one model; it overrides agents that asked for a cheaper one. EVIDENCE-BASED
- When using mod-builder, decline or ignore the star prompt if you do not want `gh` acting on your account. PRACTITIONER

> [!contradiction]
> The repo README and mod-builder's gotchas say "Nothing loads unless `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` is set". The 2.1.287 docs say the flag is ignored and mods load by default (docs-mods-overview). The docs win; the repo text predates GA.

## Caveats

- Validation claims are 2.1.272 (templates) and 2.1.276 (cache-tax); the scanner shows both passing on 2.1.287, not an author re-test.
- cache-tax's dollar figures use list prices from its README; they are not re-verified here.
- The skill's reference files (events, nouns) derive from the architecture paper and cheat sheet, not the generated typings; check against [[Plugin Validate]] output.

## Related

- [[Mod Catalog]] rows for all three.
- [[Mod Directories]]: the same author's awesome list and scanner.
- [[Reach Levels]] and [[Mod Security Audit Checklist]]: the L0 to L3 scale comes from this author's scanner.
- [[Prompt Cache Discipline]] and [[Usage Cost Surface]] for cache-tax.
- [[Agent and Command Events]] for `agent.spawn` rewrites.
- [[Classic Hook Bridge]] for `classic.SessionStart`.

## Sources

- eco-gh-karanb192-mods: https://github.com/karanb192/claude-code-mods (retrieved 2026-10-03, pinned 9d73de7)
- eco-gh-cache-tax: https://github.com/karanb192/cache-tax (retrieved 2026-10-03, pinned 2b51ee4)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870#issuecomment-5715941633 (retrieved 2026-10-03)
- eco-gh-awesome-claude-code-mods: https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03, pinned 59a9911)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- eco-static-scan: `.raw/captures/lanes-2026-10-03/ecosystem/eco-static-scan-2026-10-03.md`
