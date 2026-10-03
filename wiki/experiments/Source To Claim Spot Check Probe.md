---
type: "experiment"
title: "Source To Claim Spot Check Probe"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/experiment"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "rewrite"
related:
  - "[[Claim Verification Flow]]"
  - "[[Provenance Trace Policy]]"
  - "[[Evidence Coverage Not Yet Verified]]"
  - "[[Source Intake Workflow]]"
  - "[[Mod Anatomy]]"
  - "[[Budgets and Limits]]"
  - "[[Render Sites]]"
  - "[[Testing Kit]]"
  - "[[Plugin Validate]]"
  - "[[Mods Trust Model]]"
  - "[[Mod Catalog]]"
  - "[[Arunjay4213 claude-mods]]"
  - "[[How is $.model.classify billed]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)"
  - "https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03)"
  - "https://github.com/Arunjay4213/claude-mods (retrieved 2026-10-03)"
sources:
  - "claim-ledger"
  - "types-2-1-288"
  - "docs-mods-reference"
  - "docs-mods-troubleshoot"
  - "docs-mods-overview"
  - "pluto-function-hooks"
  - "gh-issue-91870"
  - "secgov-validate-probes"
  - "eco-gh-awesome-claude-code-mods"
  - "eco-gh-arunjay4213"
---

# Source To Claim Spot Check Probe

This probe asks whether ledger claims actually trace to the captures they cite. On 2026-10-03 this pass picked 12 evidence-based, load-bearing claims from `references/claim-ledger.md` (2 or 3 per lane) and grepped `.raw/captures/` for each cited source. 11 passed with an exact line. 1 failed in part at the time: C-ECO-031's no-license half had no capture behind it; only the README half was captured. Resolved after the probe on 2026-10-03: the capture `.raw/captures/lanes-2026-10-03/ecosystem/eco-gh-arunjay4213-license-field.md (license field null, license endpoint 404, no license-like path) and eco-gh-arunjay4213-license.md` now backs it, and claim-ledger row 222 is verified.

## Method

1. Choose claims whose verdict others rely on: API shape, limits, security status, ecosystem size, and staff-only statements.
2. For each, grep the cited capture under `.raw/captures/` for the claim's key literal (a value, a quoted phrase, a comment URL).
3. Pass when every material part of the claim is found at the cited source, at or near the cited line. Partial fail when a material part has no capture.
4. Record the exact file and line.

Example commands used:

```bash
T=.raw/captures/types-2.1.288/claude-code/index.d.ts
sed -n 4803,4837p "$T" | grep -n "_000"
grep -n "'terminal' | 'desktop'" "$T"
grep -n "via go" .raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md
grep -n "5961758416\|5949411806" .raw/captures/web-2026-10-03/gh-issue-91870.md
```

## Results

| # | Claim | Lane | Cited source | Capture location found | Result |
|---|---|---|---|---|---|
| 1 | C-API-001: mod = `plugin.json`, `hooks.json` `modules` with one path, module exporting `register(on, options)` | API | docs-mods-reference L15-27; code-modernization hooks.json; types L60-66 | `.raw/captures/docs-2026-10-03/plugins-mods-reference.md` L21-23; `.raw/captures/official-mods/code-modernization-1.0.0/hooks/hooks.json` L71-73 (`"./register.ts"`); `types-2.1.288/claude-code/index.d.ts` L62, L65 | PASS |
| 2 | C-API-012: 10,000 ms own time, 1,000 ms `.catch`, 5,000 ms linger, clock stops in `$` calls except `$.clock.sleep` | API | types L4803-4837; docs-mods-reference L245-246; claudedev L394 | `index.d.ts` L4812 `ms: 10_000`, L4820 `catchMs: 1_000`, L4828 `lingerMs: 5_000`; `plugins-mods-reference.md` L245-246; `web-2026-10-03/claudedev-getting-started.txt` L394 | PASS |
| 3 | C-API-049: `e.surface` is terminal, desktop, mobile, vscode in typings; docs say terminal or desktop | API | types L9695; docs-mods-reference L190 | `index.d.ts` L9695 `RenderSurface = 'terminal' \| 'desktop' \| 'mobile' \| 'vscode'`; `plugins-mods-reference.md` L190 "`e.surface` is `terminal` or `desktop`" | PASS (contradiction confirmed) |
| 4 | C-LIF-009: `reload failed, the previous version stays loaded:`; debug line `hooks module <name>@inline loaded (worker, environment N, tier user)` | LIF | docs-mods-troubleshoot | `docs-2026-10-03/plugins-mods-troubleshoot.md` L228 (reload failed), L223 (`first-mod@inline loaded (worker, environment 2, tier user)`) | PASS |
| 5 | C-LIF-029: `test(name, { options }, body)` passes userConfig values as a load does; left out, manifest defaults; inline plugins get none | LIF | types L14924-14945; skill reference | `index.d.ts` L14924-14946 (L14944 `options?: PluginOptions`); `lanes-2026-10-03/lifecycle/plugin-authoring-skill-2-1-288.md` L131 | PASS |
| 6 | C-SEC-063: Pluto says mods are env-gated and off by default (contradicted) | SEC | pluto-function-hooks; docs-mods-overview | `web-2026-10-03/pluto-function-hooks.txt` L98, L292; `plugins-mods-overview.md` L97 ("on by default"), L112 (variable ignored) | PASS |
| 7 | C-SEC-008: `$` passed to a helper validates as `calls: $.http.fetch (via go)` | SEC | secgov-validate-probes Probe 2 | `lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md` L45 | PASS |
| 8 | C-SEC-016: `$.session.authorize` keeps the credential on the host, handle only for first-party hosts | SEC | types L2697-2709 | `index.d.ts` L2699 ("Holds the session's Anthropic credential on the host"), L2703 ("only for a first-party host"), L2709 `authorize:` | PASS |
| 9 | C-ECO-047: 359 mods in 373 repos against 2.1.287 as of 2026-10-02; L2 186, L3 79 | ECO | eco-gh-awesome-claude-code-mods | `lanes-2026-10-03/ecosystem/eco-gh-awesome-claude-code-mods-readme.md` L18 | PASS |
| 10 | C-ECO-031: four mods (context-lens, quota-meter, token-ledger, budget-guard); GitHub reports no license and no LICENSE file though README says MIT | ECO | eco-gh-arunjay4213 | `lanes-2026-10-03/ecosystem/eco-gh-arunjay4213-readme.md` L17-20 (four mods), L76-78 (`## License` / `MIT`); at probe time, no capture of the GitHub license field or a file listing in `.raw/`. Since: `lanes-2026-10-03/ecosystem/eco-gh-arunjay4213-license.md` (empty license field, no LICENSE among top-level files at d4fffd7, README `## License` / `MIT`) | PASS (resolved 2026-10-03 after the probe; originally PARTIAL FAIL) |
| 11 | C-PAT-044: worktree isolation loss under `tool.call` fixed in 2.1.288 (staff) | PAT | gh-issue-91870 c5961758416, c5949411806 | `web-2026-10-03/gh-issue-91870.md` L5972 (report on 2.1.287), L6128 (@poteat: "should be fixed as of today's release on v288") | PASS (source says "should be"; ledger hedge added 2026-10-03, see below) |
| 12 | C-PAT-031: `$.model.classify` is one `complete` call with a fixed classifier prompt, small fast model default, returns label or `undefined` with no usage | PAT | types L1218-1226, L2436-2452, L6746 | `index.d.ts` L2435-2436, L2444-2445, L2452 (`Promise<string \| undefined>`); L1222-1225 (`ClassifyOptions` default model); L6746 (`'model.classify': string \| undefined`) | PASS |

Score at probe time: 11 pass, 1 partial fail, 0 full fail. After the 2026-10-03 follow-up capture: 12 pass.

## Failure detail: C-ECO-031 (resolved 2026-10-03)

History, kept as found. The ecosystem lane's claim has three parts. Two trace: the four mods (capture L17-20) and the README's MIT line (L76-78). The third, that GitHub's license field is empty and the repo has no LICENSE file, was presumably checked with a live `gh api` call that was not saved; the ecosystem lane's unshipped working ledger noted only author comment URLs for this source. As stored, the claim's "no license" half is uncapturable evidence, and the [[Mod Catalog]] verdict for [[Arunjay4213 claude-mods]] leans on it.

Fix: save `gh api repos/Arunjay4213/claude-mods --jq .license` and `gh api repos/Arunjay4213/claude-mods/contents --jq '.[].name'` at the pinned SHA `d4fffd7d` as a capture, or downgrade the license half to SINGLE-SOURCE.

Resolution (2026-10-03, after the probe): the first option was taken. `.raw/captures/lanes-2026-10-03/ecosystem/eco-gh-arunjay4213-license.md` records an empty license field, a top-level file list with no LICENSE at `d4fffd7`, and the README's `## License` / `MIT` lines. Claim-ledger row 222 now cites it and reads verified.

## Observations beyond pass or fail

- **Hedged staff wording (resolved 2026-10-03).** At probe time C-PAT-044 read "fixed in 2.1.288" while the capture says "This should be fixed". The ledger now records the staff wording as "should be fixed", unconfirmed by a release note or test, with verdict SINGLE-SOURCE.
- **Inferred sub-clauses.** C-PAT-031's "with no usage" is read from the return type, not stated in prose. That is a fair inference but should be labelled.
- **Line drift risk.** Items 2, 3, 5, 8, 12 cite typings lines that will move with the next release ([[Evidence Coverage Not Yet Verified]]).
- **Off-by-two citations.** C-SEC-016 cites L2697-2709; the relevant text starts at L2699 inside that range. Ranges are fine; single-line citations would need care.

## Recommendations

- Require a saved capture for every `gh api` fact before it enters the ledger. EVIDENCE-BASED
- Quote staff hedges verbatim in claim text when the verdict rests on one comment. PRACTITIONER
- Rerun this probe with a fresh random 12 after each ledger regeneration and after every typings re-capture. PRACTITIONER

## Caveats

- 12 of 301 claims (4 percent) is a spot check, not an audit; selection favoured load-bearing rows, so the pass rate is not a population estimate.
- Grep confirms the source says it; it does not confirm the source is right at runtime.

## Related

Process: [[Claim Verification Flow]], [[Provenance Trace Policy]], [[Source Intake Workflow]]. Coverage: [[Evidence Coverage Not Yet Verified]]. Claims probed land in [[Mod Anatomy]], [[Budgets and Limits]], [[Render Sites]], [[Testing Kit]], [[Plugin Validate]], [[Mods Trust Model]], [[Mod Catalog]], [[Arunjay4213 claude-mods]], [[How is $.model.classify billed]].

## Sources

- claim-ledger: `references/claim-ledger.md` (generated 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (written by 2.1.288, retrieved 2026-10-03)
- docs-mods-reference, docs-mods-troubleshoot, docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/<page> (retrieved 2026-10-03)
- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870#issuecomment-5961758416 (retrieved 2026-10-03)
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md`
- eco-gh-awesome-claude-code-mods: https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03)
- eco-gh-arunjay4213: https://github.com/Arunjay4213/claude-mods at d4fffd7d (retrieved 2026-10-03)
