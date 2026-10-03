---
type: "entity"
title: "Mod Directories"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.287"
tags:
  - "#domain/claude-code-mods"
  - "#type/entity"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "ecosystem"
related:
  - "[[Mod Catalog]]"
  - "[[karanb192 claude-code-mods]]"
  - "[[Reach Levels]]"
  - "[[Plugin Validate]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Marketplaces and Distribution]]"
  - "[[Read Only Audit Decision]]"
  - "[[Research Refresh Workflow]]"
  - "[[Source Intake Workflow]]"
source_urls:
  - "https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03, pinned 59a9911a836326338a831b6c8e37a7a855e405f4)"
  - "https://mods.aidojo.si/ (retrieved 2026-10-03)"
  - "https://github.com/joeVenner/claude-code-mods (retrieved 2026-10-03, pinned cc67e83713fde68b9ffbe8afcc317ec551cbc767)"
  - "https://github.com/osaki42/awesome-claude-mods (retrieved 2026-10-03, pinned 7ee0986b5827ec7239081b2919962f63d3bab489)"
  - "https://claude-mods.com/ (retrieved 2026-10-03)"
  - "https://claudemods.ai/ (retrieved 2026-10-03)"
sources:
  - "eco-gh-awesome-claude-code-mods"
  - "eco-web-mods-aidojo"
  - "eco-gh-joeventner"
  - "eco-gh-osaki42"
  - "eco-web-claude-mods-com"
  - "eco-web-claudemods-ai"
  - "compass-report"
---

# Mod Directories

Five public lists catalogue community mods. Only one, karanb192's awesome-claude-code-mods, attaches evidence to each row: a nightly scan that runs `claude plugin validate` on every candidate repo and prints the events hooked and `$` calls made, then grades reach L0 to L3 (C-ECO-047). The others are plain indexes or votes. Use the scanner list to discover mods and to pre-screen footprints; never treat any list as a review.

## Comparison

| Directory | Repo or site | Pin or fetch | What it adds | Freshness on 2026-10-03 |
|---|---|---|---|---|
| awesome-claude-code-mods | `karanb192/awesome-claude-code-mods`, CC0, 78 stars; site `mods.aidojo.si` | `59a9911` (2026-10-02) | per-row footprint from `claude plugin validate`, reach level, validate status, stars | "As of 2026-10-02, scanned against Claude Code 2.1.287: 359 mods in 373 candidate repos" |
| claudecodemods.com | `joeVenner/claude-code-mods` | `cc67e83` (2026-09-22) | directory of mods, plugins, skills, agents, hooks, MCP servers; Ideas page | last push 2026-09-22; site text mentions "4 mods" (likely the built-ins; not confirmed) |
| osaki42/awesome-claude-mods | `osaki42/awesome-claude-mods`, CC0 | `7ee0986` (2026-10-02) | "Every entry here was checked by hand"; candidate queue issue | updated 2026-10-02 |
| claude-mods.com | site | fetched 2026-10-03 | "75 mods listed" | page says updated Sep 17, 2026 (C-ECO-049) |
| claudemods.ai | site | fetched 2026-10-03 | "voted catalog" of mods | not determined |

## The scanner in numbers

From the README stats block at 59a9911 (C-ECO-047):

| Measure | Count |
|---|---|
| Mods / candidate repos | 359 / 373 |
| Run host processes | 127 |
| Write files | 95 |
| Read files | 143 |
| Reach the network | 75 |
| See every tool call | 79 |
| See every prompt | 111 |
| Fail to validate on 2.1.287 | 21 |
| L0 / L1 / L2 / L3 | 55 / 39 / 186 / 79 |

`data/mods.json` (generated 2026-10-02T02:16Z, `claudeVersion: "2.1.287"`) holds 437 rows; the README count of 359 appears to exclude catalogue copies (`davila7/claude-code-templates` repackages 38 mods and is named once). That reconciliation is inferred, not documented.

Coverage gaps at the pinned SHA: no rows for hamzafer/claude-code-mods or the playground samples, and OneWave is in `seeds.txt` with no rows (C-ECO-048). The built-in `telemetry` folder shows `failed` because, validated as a third-party plugin, its hooks stand on the stream reserved for built-ins (C-ECO-018).

## What "verified" means on each list

- awesome-claude-code-mods: the footprint is what Claude Code's own validator prints, before any mod code runs. It says nothing about intent or quality.
- claudecodemods.com: "Source verified" means the source URL "returned HTTP 200 on the catalog date"; its spec's security tiers are "a design, not a running scanner" (C-ECO-050).
- osaki42: hand-checked, no stated method.
- claude-mods.com and claudemods.ai: no stated method found.

## Recommendations

- Start discovery from the awesome list or `mods.aidojo.si`, filter by reach, then read source; the footprint line is the cheapest pre-screen available. EVIDENCE-BASED
- Re-run `claude plugin validate` yourself on the version you run; a list's grade is for 2.1.287 and drifts with each release. EVIDENCE-BASED
- Do not rely on claude-mods.com or claudecodemods.com counts for completeness; both lag GA. EVIDENCE-BASED
- Treat star counts as noise this early: most mod repos have under 5 stars. PRACTITIONER

> [!contradiction]
> The seed report lists the awesome list at "31 mods in 92 repos as of 2026-09-15" and says "None of these lists re-scans on 2.1.287 yet". At 59a9911 the list states a 2026-10-02 scan against 2.1.287 covering 359 mods in 373 repos. The repo wins (C-ECO-047).

## Caveats

- Site counts were read from page text on 2026-10-03 and can change daily.
- The reach scale (L0 draws, L1 reads, L2 writes or runs or drives Claude, L3 network) is this author's convention, adopted by this vault in [[Reach Levels]]; it is not an Anthropic standard.
- The awesome list's author also publishes mods reviewed in this lane ([[karanb192 claude-code-mods]]); weigh that when reading rankings.

## Related

- [[Mod Catalog]] uses these lists as leads, then pins and reads each repo.
- [[karanb192 claude-code-mods]] is the scanner author's own marketplace.
- [[Reach Levels]] and [[Plugin Validate]] for what the footprint means.
- [[Audit a Third-Party Mod Flow]] and [[Read Only Audit Decision]] for what to do after discovery.
- [[Marketplaces and Distribution]] for how listed mods install.
- [[Research Refresh Workflow]] and [[Source Intake Workflow]] for re-checking these counts by 2026-11-02.

## Sources

- eco-gh-awesome-claude-code-mods: https://github.com/karanb192/awesome-claude-code-mods (retrieved 2026-10-03, pinned 59a9911)
- eco-web-mods-aidojo: https://mods.aidojo.si/ (retrieved 2026-10-03)
- eco-gh-joeventner: https://github.com/joeVenner/claude-code-mods (retrieved 2026-10-03, pinned cc67e83)
- eco-gh-osaki42: https://github.com/osaki42/awesome-claude-mods (retrieved 2026-10-03, pinned 7ee0986)
- eco-web-claude-mods-com: https://claude-mods.com/ (retrieved 2026-10-03)
- eco-web-claudemods-ai: https://claudemods.ai/ (retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (lead only)
