---
type: "question"
title: "What Current Official Source Resolves The Highest Risk Claim"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/question"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "rewrite"
related:
  - "[[Mods Trust Model]]"
  - "[[Built-in sec-default Mod]]"
  - "[[Org Mod Controls]]"
  - "[[Plugin Validate]]"
  - "[[Usage Cost Surface]]"
  - "[[How is $.model.classify billed]]"
  - "[[Versioning and API Drift]]"
  - "[[Claude Code Release Channels]]"
  - "[[API Surface 2.1.288]]"
  - "[[Evidence Coverage Not Yet Verified]]"
  - "[[Unverified pre-release security findings on current builds]]"
  - "[[Re-verify After Release Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/setup (retrieved 2026-10-03)"
sources:
  - "docs-mods-overview"
  - "docs-mods-admin"
  - "docs-mods-api"
  - "docs-mods-create"
  - "docs-plugins-security"
  - "docs-plugins-measure"
  - "eco-docs-setup"
  - "eco-npm-dist-tags"
  - "types-2-1-288"
---

# What Current Official Source Resolves The Highest Risk Claim

Answer: there is no single source. Of the five highest-risk claims in this brain, three are resolved by a named official page as of 2026-10-03 (unsandboxed reach, guard scope, on-by-default), one is resolved only by the 2.1.288 typings with no docs line (model call cost), and one has no official resolution at all (whether `plugin details` discloses a mod's hooks). The pages to watch are code.claude.com `plugins/mods/admin`, `plugins/mods/overview`, `plugins/security`, and `plugins/measure`, plus the typings Claude Code writes beside each mod.

## How "highest risk" was chosen

A claim ranks high when being wrong about it would lead a user or admin to install, approve, or pay for something they otherwise would not. Ranking used three axes from the ledger: security impact, cost impact, and version drift (claims that silently change between releases). Candidates came from the SEC lane, the cost rows (C-SEC-038 to C-SEC-044, C-PAT-031, C-PAT-032, C-PAT-057), and the version rows (C-LIF-001, C-SEC-030, C-ECO-053, C-ECO-054).

## The five claims

| # | Axis | Claim | Resolving official source | Status |
|---|---|---|---|---|
| 1 | Security | A mod is unsandboxed: it reads and writes files anywhere the user can, and deny rules do not cover its own `$.fs` or `$.process` calls (C-SEC-001, C-SEC-020) | docs-mods-overview "What a mod can reach"; docs-mods-admin | resolved, verified |
| 2 | Security | `sec-default` protects only managed hooks, system prompt, managed instructions, settings reads, managed MCP tools and deny rules, and loads only with managed settings or a Team or Enterprise sign-in (C-SEC-018, C-SEC-019) | docs-mods-admin "Know what happens by default" | resolved, verified; blog wording is looser |
| 3 | Security | `claude plugin details` shows what hooks a mod registers (C-SEC-052) | docs-plugins-security L104 (inventory lists "hooks with each hook's event") | unresolved: page is silent on function hooks; Pluto saw "Hooks (0)" on 2.1.274 |
| 4 | Cost | A mod's `$.model.complete`, `fork` and `classify` spend the user's plan or API key, and that spend is attributable (C-SEC-038, C-PAT-031, C-SEC-044) | docs-mods-api and docs-mods-admin (complete and fork use the plan); types 2.1.288 L2434-2452 (classify is one `complete` call) | partly resolved: spend yes, attribution in `/usage` or OTel undocumented |
| 5 | Version drift | Mods are on by default from 2.1.287 and `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` is ignored, so `0` does not turn them off (C-LIF-001, C-SEC-030, C-ECO-056) | docs-mods-overview L97, L112; docs-mods-admin | resolved, verified; stable-channel timing is inference (C-ECO-054) |

## Detail per claim

### 1. Unsandboxed reach

The overview says "Mods aren't sandboxed" (docs-mods-overview L79) and lists files, processes, network, environment, settings, every prompt and tool call, approvals, and usage. The admin page adds that with `Read(.env)` denied a mod can still read `.env`, and that network policy covers `$.http.fetch` but not a program started by `$.process.run`. This is the fact the claude.dev tutorial blurs with "a sandbox of its own". Status: verified, no open question. Home: [[Mods Trust Model]].

### 2. Guard scope and coverage

The admin page is the only source precise enough to act on. It lists what the guard protects and says "The guard adds no other restrictions" (docs-mods-admin L65). It also says API-key, Bedrock, Agent Platform and Foundry users get the guard only on a machine with managed settings (docs-mods-admin L63). The launch blog's "stops mods ... overriding your permission deny rules" is accurate but invites over-trust. Status: verified. Home: [[Built-in sec-default Mod]], [[Org Mod Controls]].

### 3. Pre-install disclosure

docs-plugins-security tells reviewers to run `claude --plugin-dir <dir> plugin details <name>` and read the `Component inventory`. It does not say whether function hooks are counted. The mods pages instead send reviewers to `claude plugin validate`, which this brain verified lists events and `$` calls on 2.1.288 but shows `next` rewrites only as the hooked event (C-SEC-011). Status: unresolved by any official source; needs either a docs line or the trial in [[Unverified pre-release security findings on current builds]]. Until then, [[Plugin Validate]] is the disclosure tool of record.

### 4. Model call cost

docs-mods-api and docs-mods-admin say `$.model.complete` uses the user's plan or API key; C-SEC-041 adds that `$.model.fork` reuses the cached prefix but re-bills it after the cache lapses. The admin review table names `complete` but not `classify` or `fork` (C-PAT-032). The typings resolve `classify` as one `complete` call over the engine's small fast model (types 2.1.288 L2434-2452). Nothing official says whether a mod's spend shows per plugin in `/usage` or the OTel cost counter (C-SEC-044); docs-plugins-measure ties the counter to skills and subagents. A direct billing question on #91870 went unanswered (C-PAT-057). Status: spend resolved, attribution open. Home: [[Usage Cost Surface]], [[How is $.model.classify billed]].

### 5. On by default, and the version that carries it

docs-mods-overview: "Mods require Claude Code v2.1.287 or later, and they're on by default" (L97), and 2.1.287 and later ignores the early-access variable (L112). npm dist-tags on 2026-10-03 show `latest` 2.1.288 and `stable` 2.1.285 (eco-npm-dist-tags), and the setup page says stable is about a week behind (C-ECO-053). So stable users get mods on by default when stable reaches 2.1.287, with no opt-in step. Status: verified for the rule; the stable-channel consequence is inference (C-ECO-054). Drift sub-risk: docs describe "as of v2.1.287" and already disagree with 2.1.288 typings on surfaces and Svg (C-API-049, C-API-050); docs-mods-create says to trust the typings. Home: [[Versioning and API Drift]], [[Claude Code Release Channels]], [[API Surface 2.1.288]].

## Recommendations

- Cite docs-mods-admin, never the launch blog, for any guard decision. EVIDENCE-BASED
- Treat `plugin details` as non-authoritative for mods until claim 3 resolves. CONTESTED
- Budget any mod that calls `$.model.*` as spending the user's plan, including `classify`. EVIDENCE-BASED
- Re-capture the five resolving pages on every release via [[Re-verify After Release Flow]]. EVIDENCE-BASED

## Caveats

- Ranking is this pass's judgement; the five could change after runtime trials.
- All sources captured 2026-10-03; refresh due 2026-11-02.

## Related

Open evidence work: [[Evidence Coverage Not Yet Verified]], [[Unverified pre-release security findings on current builds]]. Security homes: [[Mods Trust Model]], [[Built-in sec-default Mod]], [[Org Mod Controls]], [[Plugin Validate]]. Cost homes: [[Usage Cost Surface]], [[How is $.model.classify billed]]. Version homes: [[Versioning and API Drift]], [[Claude Code Release Channels]], [[API Surface 2.1.288]].

## Sources

- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03), capture L79, L97, L112
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03), capture L58-65, L126-129
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- docs-plugins-security: https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03), capture L104
- docs-plugins-measure: https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)
- eco-docs-setup: https://code.claude.com/docs/en/setup (retrieved 2026-10-03)
- eco-npm-dist-tags: https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` L2434-2452, L9695
