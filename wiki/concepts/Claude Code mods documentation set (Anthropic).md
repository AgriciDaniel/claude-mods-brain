---
type: "concept"
title: "Claude Code mods documentation set (Anthropic)"
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
  - "[[Mod Anatomy]]"
  - "[[Hook Middleware Chain]]"
  - "[[Observe Rewrite Answer]]"
  - "[[Hook Ordering and Tiers]]"
  - "[[Budgets and Limits]]"
  - "[[State Store and Module Variables]]"
  - "[[Render Sites]]"
  - "[[Mods API Namespaces]]"
  - "[[Org Mod Controls]]"
  - "[[Plugin Validate]]"
  - "[[Versioning and API Drift]]"
  - "[[API Surface 2.1.288]]"
  - "[[Mods design thread, anthropics claude-code issue 91870]]"
  - "[[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
sources:
  - "docs-mods-overview"
  - "docs-mods-create"
  - "docs-mods-events"
  - "docs-mods-interface"
  - "docs-mods-api"
  - "docs-mods-admin"
  - "docs-mods-reference"
  - "docs-mods-troubleshoot"
  - "docs-mods-test"
  - "docs-mods-gallery"
  - "types-2-1-288"
---

# Claude Code mods documentation set (Anthropic)

This note folds canon 001, the ten official mods pages on code.claude.com captured on 2026-10-03, into the vault. The set is the rank 1 prose source for this brain: it defines a mod as a plugin whose hooks module exports `register(on, options)`, runs unsandboxed inside Claude Code's process, and reaches the world only through `$`. Its own create page says the generated typings win any disagreement, and on 2.1.288 they do disagree in a handful of places. Trust it as authoritative for behavior and governance, and check every signature against [[API Surface 2.1.288]].

## What the work teaches

The ten pages (overview, create, interface, gallery, events, api, test, troubleshoot, admin, reference) teach one model in layers:

| Layer | Page | Core lesson |
|---|---|---|
| Shape | reference#files | `.claude-plugin/plugin.json`, `hooks/hooks.json` with `"modules": ["./register.js"]`, one ES module |
| Hook | reference, events | `on(event, matcher?, async ($, e, next) => ...)`, `e` deeply frozen, `next(e)` runs the rest |
| Moves | events | observe, rewrite, answer; answering skips later mods and core |
| Order | events | guard and org prepend, user, org append, built-in; dependencies; `on` call order |
| Failure | events | throw, timeout, or wrong shape before `next` means skip (fail open); `.catch` fails closed |
| State | interface | module variable, `$.state`, `$.store` (4 MiB, machine-wide) |
| Limits | reference#limits | 10 s own time, 1 s `.catch`, 1.5 s for all `session.end` hooks |
| Reach | overview, admin | unsandboxed, runs as the user, deny rules skip a mod's own `$.fs` and `$.process` |
| Drawing | overview, interface | hooks run in `-p`, SDK, VS Code chat; only terminal and Desktop Code tab draw |
| Governance | admin | `sec-default@builtin`, `allowManagedModsOnly`, `prependPlugins`, `appendPlugins` |

The central design claim is that routing every effect through `$` makes a mod statically inspectable: `claude plugin validate` prints `hooks:`, `calls:`, `env reads:` and `state writes:` without running anything (C-LIF-014).

## How its claims map onto vault notes

| Canon claim | Claim IDs | Vault home |
|---|---|---|
| Mod file layout and `register(on, options)` | C-API-001, C-LIF-002 | [[Mod Anatomy]] |
| Observe, rewrite, answer | C-API-007 | [[Observe Rewrite Answer]], [[Hook Middleware Chain]] |
| Tier order and settings hooks inside the chain | C-SEC-022, C-PAT-007 | [[Hook Ordering and Tiers]] |
| Fail open unless `.catch` | C-PAT-004, C-PAT-005 | [[Holding a Tool Call]], [[Pitfalls Playbook]] |
| Budgets (10 s, 1 s, 1.5 s) | C-API-012, C-PAT-002 | [[Budgets and Limits]] |
| State lifetimes and reset on `/clear` | C-API-035, C-PAT-040 | [[State Store and Module Variables]] |
| Unsandboxed reach, deny rules scope | C-SEC-001, C-SEC-020 | [[Mods Trust Model]], [[Reach Levels]] |
| Guard loading rules and scope | C-SEC-018, C-SEC-019 | [[Built-in sec-default Mod]], [[Org Mod Controls]] |
| On by default from 2.1.287 | C-LIF-001, C-SEC-030 | [[Versioning and API Drift]] |
| Validate as the disclosure tool | C-LIF-014, C-SEC-011 | [[Plugin Validate]] |
| 21 namespaces | C-API-041 | [[Mods API Namespaces]], [[Mods API Cheatsheet]] |
| Render sites and surfaces | C-API-049, C-API-050 | [[Render Sites]], [[UI Elements and JSX]] |

## Agreement and contradiction

**With the 2.1.288 typings.** The docs describe the surface "as of v2.1.287"; the typings were written by 2.1.288 and run 14,973 lines.

> [!contradiction] `e.surface` values. The reference says `e.surface` is `terminal` or `desktop` (docs-mods-reference L190). The typings declare `RenderSurface = 'terminal' | 'desktop' | 'mobile' | 'vscode'` (types 2.1.288 L9695). Typings win by the docs' own rule (C-API-049).

> [!contradiction] Svg availability. The docs and the seed report put `Svg` on desktop only; the typings' element tables give it to every remote surface and keep it off the terminal (types 2.1.288 L3586-3660, C-API-050). Typings win.

- `next` carries `is`, `event` and `trace` in the typings (types 2.1.288 L6118-6200) but the docs' `next` table omits them (C-API-014). The canon caveat "treat `next.trace` as unshipped unless the typings show it" is now resolved: the typings show it.
- The typings add `$.ui.selection()` and deprecate `$.session.surface()` in favour of `surfaces()` (types 2.1.288 L2382, L2617; C-API-041).
- Limits agree exactly: `ms: 10_000`, `catchMs: 1_000`, `lingerMs: 5_000` (types 2.1.288 L4803-4837); `lingerMs` appears only in the typings.

**With the other canon works.** The launch blog compresses ordering to "load order" (canon 002), which this set corrects with tiers. The claude.dev tutorial (canon 003) says the module "runs in a sandbox of its own"; this set says the opposite at the trust layer. The #91870 thread ([[Mods design thread, anthropics claude-code issue 91870]]) supplies the reasons behind the onion and the `$` contract that this set states as rules. Pluto ([[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]]) tested pre-release 2.1.274 and is superseded here on the env gate and admin controls (C-SEC-063). The plugins and hooks set ([[Claude Code plugins and hooks documentation (Anthropic)]]) is the substrate this set builds on.

## Verified quotes

Copied from `references/canon/001-claude-code-mods-docs.md`; each re-found verbatim in `.raw/captures/docs-2026-10-03/`.

- "Mods aren't sandboxed." (docs-mods-overview, capture L79)
- "trust these files over any page, this one included, when they disagree" (docs-mods-create, capture L284)
- "it sees the event before the others and the result after them" (docs-mods-events, capture L285)
- "Without the handler, Claude Code would skip `guard` and run the command." (docs-mods-events, capture L324)
- "so write it as an instruction Claude can act on" (docs-mods-events, capture L116)

## What it gets wrong or leaves stale

- **Incomplete surface list.** Mobile and VS Code surfaces exist in the typings but not in the reference (C-API-049). A mod that branches only on `terminal` versus `desktop` has an unhandled case.
- **Svg placement** is wrong per typings (C-API-050).
- **`next` fields** `is`, `event`, `trace` are missing from the table (C-API-014).
- **No dates.** No page carries a publish or revision date, so drift can only be detected by re-capturing and diffing.
- **Guard coverage is easy to misread.** The admin page is precise ("The guard adds no other restrictions"), but personal API-key users get no guard at all without managed settings (C-SEC-018); nothing on the overview page warns them.
- **Cost attribution is silent.** The admin review table names `$.model.complete` as the usage-spending call but not `classify` or `fork` (C-PAT-032), and nothing says whether a mod's model calls appear per plugin in `/usage` (C-SEC-044).

## How much to trust it

Confidence: evidence-based. It is rank 1 under the lane brief, and 218 of 301 ledger claims carry a plain `verified` verdict, most of them against these pages plus the typings. Use it as the default answer for behavior, ordering, trust, and admin keys. Do not use it alone for exact type shapes, surface lists, or element availability; read [[API Surface 2.1.288]] first.

- Cite docs plus a typings line range for any signature claim. EVIDENCE-BASED
- When docs and typings disagree, follow the typings and record a contradiction callout. EVIDENCE-BASED
- Re-capture all ten pages on each release and diff before trusting old notes. EVIDENCE-BASED

## Caveats

- The capture is of 2026-10-03; the pages are undated and may change silently.
- Gallery and interface pages were read for headings and state rules, not every element prop.
- Version sensitivity: written for 2.1.287, tested here against 2.1.288 typings only, not by running a mod.

## Related

Start from [[Mod Anatomy]] and [[Hook Middleware Chain]], then [[Observe Rewrite Answer]] and [[Hook Ordering and Tiers]]. Limits live in [[Budgets and Limits]], state in [[State Store and Module Variables]], drawing in [[Render Sites]]. Governance is in [[Org Mod Controls]] and inspection in [[Plugin Validate]]. Drift handling is in [[Versioning and API Drift]] and [[Re-verify After Release Flow]]. Overall map: [[overview|Overview]].

## Sources

- Canon file: `references/canon/001-claude-code-mods-docs.md`
- docs-mods-overview, docs-mods-create, docs-mods-events, docs-mods-interface, docs-mods-api, docs-mods-admin, docs-mods-reference, docs-mods-troubleshoot, docs-mods-test, docs-mods-gallery: https://code.claude.com/docs/en/plugins/mods/<page> (retrieved 2026-10-03), captures in `.raw/captures/docs-2026-10-03/plugins-mods-*.md`
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (written by Claude Code 2.1.288, retrieved 2026-10-03)
- Claim ledger rows: `references/claim-ledger.md` (C-API-001, C-API-012, C-API-014, C-API-041, C-API-049, C-API-050, C-SEC-018, C-SEC-019, C-SEC-044, C-PAT-032)
