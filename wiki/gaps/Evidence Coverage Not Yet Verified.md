---
type: "gap"
title: "Evidence Coverage Not Yet Verified"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/gap"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "rewrite"
related:
  - "[[Claim Verification Flow]]"
  - "[[Source To Claim Spot Check Probe]]"
  - "[[Unverified pre-release security findings on current builds]]"
  - "[[What Current Official Source Resolves The Highest Risk Claim]]"
  - "[[How is $.model.classify billed]]"
  - "[[Does claude plugin test support userConfig values yet]]"
  - "[[Usage Cost Surface]]"
  - "[[Plugin Validate]]"
  - "[[Versioning and API Drift]]"
  - "[[Read Only Audit Decision]]"
  - "[[Mod Catalog]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)"
  - "https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)"
sources:
  - "claim-ledger"
  - "docs-mods-admin"
  - "docs-mods-interface"
  - "docs-mods-troubleshoot"
  - "docs-plugins-measure"
  - "docs-plugins-security"
  - "gh-issue-91870"
  - "pluto-function-hooks"
  - "types-2-1-288"
---

# Evidence Coverage Not Yet Verified

On 2026-10-03 the claim ledger holds 301 claims across five lanes. 224 (74 percent) are verified, with 6 of those carrying a scope qualifier; 55 are SINGLE-SOURCE, 14 contradicted, 6 unverified, and 2 split between verified and contested. No claim in the ledger was verified by running a mod: "tested on 2.1.288" means checked against the 2.1.288 docs, typings, or static `claude plugin validate` output. This gap lists the open claims that matter and the cheapest evidence that would close each.

## Coverage map by verdict

Counted from `references/claim-ledger.md` on 2026-10-03 after the critic-round corrections (C-API-035 gained a partial second source; C-ECO-031 gained a license capture; C-PAT-044 now quotes the staff hedge), with escaped pipes handled (one row, C-LIF-032, otherwise mis-parses).

| Verdict | Count | Share |
|---|---|---|
| verified (including qualified and partial second sources) | 228 | 75.7% |
| SINGLE-SOURCE (including "rate" and "contested for older builds") | 54 | 17.9% |
| contradicted (including seed, docs incomplete) | 13 | 4.3% |
| unverified | 6 | 2.0% |
| **Total** | **301** | |

Confidence column: 276 evidence-based, 15 practitioner, 6 contested, 3 anecdotal, 1 inference.

## Coverage map by lane

| Lane | Claims | Verified | Qualified or partial | SINGLE-SOURCE | Contradicted | Unverified | No second source | Not tested on 2.1.288 |
|---|---|---|---|---|---|---|---|---|
| API (api-and-events) | 60 | 48 | 5 | 5 | 2 | 0 | 3 | 0 |
| LIF (lifecycle) | 60 | 49 | 3 | 7 | 0 | 1 | 7 | 11 |
| SEC (security-governance) | 63 | 42 | 0 | 14 | 3 | 4 | 17 | 9 |
| ECO (ecosystem) | 58 | 41 | 0 | 11 | 5 | 1 | 12 | 40 |
| PAT (patterns-and-ideas) | 60 | 38 | 0 | 18 | 4 | 0 | 13 | 6 |

Reading: API is the best covered because the typings give a second source for almost every row. SEC carries the most unresolved weight (4 of 6 unverified claims). PAT has the most SINGLE-SOURCE rows, mostly docs-only behaviours. ECO is weakest on version: 40 of 58 rows are pinned to repo SHAs, author claims, or 2.1.287 scanner runs rather than 2.1.288.

Contradicted rows are resolved, not open: each names the winning source (for example C-SEC-063, Pluto's env gate, loses to docs-mods-overview). They are listed in [[Contradictions Register]] and are not repeated here.

## Open claims that matter most

Ranked by the damage a wrong answer would do to a security, cost, or build decision.

| Rank | Claim | Verdict | Why it matters | What would verify it |
|---|---|---|---|---|
| 1 | C-SEC-052: `claude plugin details` shows a mod as `Hooks (0)` | unverified | if true, the main pre-install review surface hides mods | isolated trial: `claude --plugin-dir <mod> plugin details <name>` on 2.1.288 (docs-plugins-security L104 says this reads files without a session) |
| 2 | C-SEC-053: content scan only on the claude.ai install path | unverified | decides whether GitHub-marketplace mods get any scan | Anthropic statement, or install the same mod both ways in an isolated account and compare logs |
| 3 | C-SEC-055: `AskUserQuestion` labels restored after rewrite | unverified | decides whether dialog-swap phishing is bounded | isolated trial with a mod rewriting option labels |
| 4 | C-SEC-044: mod `$.model.*` spend attributed per plugin | unverified | cost governance for teams | docs-plugins-measure update, or a trial comparing `/usage` before and after one `$.model.complete` |
| 5 | C-PAT-057 and C-PAT-031: `$.model.classify` billing | SINGLE-SOURCE | cheap-looking call that spends usage | typings already say it is one `complete` call; need a docs line or staff answer on #91870 |
| 6 | C-PAT-044: worktree isolation fix in 2.1.288 | SINGLE-SOURCE | a `tool.call` hook could run subagent Bash in the parent checkout | changelog entry for 2.1.288, or isolated trial with `isolation: "worktree"` |
| 7 | C-ECO-054: stable channel (2.1.285) has no mods | unverified (inference) | users on stable may think mods are off; they get them when stable reaches 2.1.287 | `claude --version` on a stable install plus the channel page |
| 8 | C-SEC-016: `$.session.authorize` keeps the credential on the host | SINGLE-SOURCE | underpins "a mod cannot read the API token" | docs-mods-api line, or validate probe showing the handle type |
| 9 | C-API-035: `/clear`, `/resume`, `/branch` reset `$.state` and skip `session.start` | verified (second source partial) | stale state bugs in any mod that keeps per-conversation state | resolved 2026-10-03: docs-mods-reference L105-106 added as a partial second source (it confirms the session events, not the reset itself) |
| 10 | C-LIF-035: `claude plugin test` runs on the same thread | SINGLE-SOURCE (anecdotal) | tests cannot catch a worker crash | docs-mods-test statement or a test that blocks deliberately |
| 11 | C-PAT-043: three untraceable crashes unload every non-built-in mod | SINGLE-SOURCE | one bad mod can silently disable a guard | typings or troubleshoot cross-check; isolated trial |
| 12 | C-SEC-051 and C-ECO-047: 359 mods scanned, L3 79 | SINGLE-SOURCE | sizes the ecosystem risk in [[Mod Catalog]] | rerun karanb192's scanner at a pinned SHA against 2.1.288 |

Items 1 to 3 need a runtime and are planned in [[Unverified pre-release security findings on current builds]]. Items 4 and 5 are the open questions in [[How is $.model.classify billed]] and [[Usage Cost Surface]].

## Structural gaps

- **No runtime evidence.** The brain's hard rule forbids loading a mod ([[Read Only Audit Decision]]). Every behaviour claim is docs plus typings plus static validate. That is strong for API shape and weak for "what the user sees".
- **Typings line numbers are version bound.** 110 rows cite a typings line range (`types L<n>` or `types 2.1.288 L<n>`); one release that reflows the file invalidates every line range even if nothing changed. [[Versioning and API Drift]] covers the re-capture.
- **Second source independence.** 52 rows have no second source at all. Many API rows use docs plus typings from the same publisher, which is a consistency check, not independent corroboration.
- **Scan freshness.** The footprint scans of the personal mods reviewed for this brain were generated at 00:38 on 2026-10-03, before those mods' sources changed at 00:41 to 00:42. A scan binds to the commit it read; re-scan before citing one ([[Synthesis Workflow]]).

## Recommendations

- Close items 1 to 3 in one isolated, human-approved session rather than three. PRACTITIONER
- Ask on #91870 for billing and attribution of `$.model.*` in one comment, quoting C-SEC-044 and C-PAT-057. PRACTITIONER
- Promote a SINGLE-SOURCE typings row to verified only when a docs page or a `claude plugin test` run agrees. EVIDENCE-BASED
- Re-run [[Source To Claim Spot Check Probe]] after every ledger regeneration. EVIDENCE-BASED

## Caveats

- Counts are from the ledger as generated on 2026-10-03 and will change as lanes merge.
- "Not tested on 2.1.288" counts every Tested-on value that does not start with `2.1.288`, including `n/a` rows where version is irrelevant.

## Related

Process: [[Claim Verification Flow]], [[Source To Claim Spot Check Probe]]. Open items: [[Unverified pre-release security findings on current builds]], [[What Current Official Source Resolves The Highest Risk Claim]], [[How is $.model.classify billed]], [[Does claude plugin test support userConfig values yet]]. Context: [[Usage Cost Surface]], [[Plugin Validate]], [[Versioning and API Drift]], [[Read Only Audit Decision]], [[Mod Catalog]].

## Sources

- claim-ledger: `references/claim-ledger.md` (generated 2026-10-03), counted 2026-10-03
- docs-mods-admin, docs-mods-interface, docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/<page> (retrieved 2026-10-03)
- docs-plugins-measure: https://code.claude.com/docs/en/plugins/measure (retrieved 2026-10-03)
- docs-plugins-security: https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
