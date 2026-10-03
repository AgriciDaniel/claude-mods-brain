---
type: "dashboard"
title: "Dashboard"
domain: "Claude Code mods"
status: "evergreen"
created: "2026-10-03"
updated: "2026-10-03"
tags:
  - "#domain/claude-code-mods"
  - "#type/dashboard"
  - "#confidence/practitioner"
confidence: "practitioner"
related:
  - "[[Start Here]]"
  - "[[CONVENTIONS]]"
  - "[[Tag Taxonomy]]"
  - "[[index|Index]]"
  - "[[overview|Overview]]"
  - "[[hot|Hot]]"
  - "[[log|Log]]"
  - "[[Mods API gaps requested in the 91870 thread but not shipped]]"
  - "[[Does claude plugin test support userConfig values yet]]"
  - "[[Diff generated typings across two Claude Code versions]]"
  - "[[dashboard|Dashboard]]"
  - "[[Source Intake Workflow]]"
  - "[[Research Refresh Workflow]]"
  - "[[Claim Verification Flow]]"
  - "[[Synthesis Workflow]]"
  - "[[Reporting Workflow]]"
  - "[[Source Manifest Guide]]"
  - "[[Best Practices Kernel]]"
  - "[[wiki/flows/_index|Flows Hub]]"
  - "[[wiki/sources/_index|Sources Hub]]"
  - "[[wiki/concepts/_index|Concepts Hub]]"
  - "[[wiki/decisions/_index|Decisions Hub]]"
  - "[[wiki/deliverables/_index|Deliverables Hub]]"
  - "[[wiki/reports/_index|Reports Hub]]"
  - "[[wiki/questions/_index|Questions Hub]]"
  - "[[wiki/gaps/_index|Gaps Hub]]"
  - "[[wiki/experiments/_index|Experiments Hub]]"
source_urls: []
---

# Dashboard

Dataview views over the vault require the Dataview community plugin. Without Dataview, use the linked seed lists and run `python3 scripts/audit_brain.py --json` for the same gate signals.

## Visual Map

![brain relationship map](../../_attachments/brain-relationship-map.svg)

## Brain at a glance (2026-10-03)

| Signal | Value |
|---|---|
| Tested on | Claude Code 2.1.288 (npm `latest`); `stable` is 2.1.285 |
| Ledger | 50 public sources, 7 local captures, 301 claims |
| Canon | 6 works, folded into concepts |
| Adapters | typings importer, drift, scanner, synthesis, 3 renderers, research pack |
| Next refresh | next Claude Code release, or 2026-11-02 at the latest |

Current state and next action: [[hot|Hot]]. Release watch: Weekly Report. Pending owner decisions: Approval Queue.

## Freshness: notes by tested_on

```dataview
TABLE tested_on, confidence, updated
FROM "wiki"
WHERE tested_on
SORT tested_on ASC, file.name ASC
```

## Notes by lane

```dataview
TABLE length(rows) AS notes
FROM "wiki"
WHERE lane
GROUP BY lane
```

## Notes by status

```dataview
TABLE status, domain, confidence, updated
FROM "wiki"
WHERE type != "meta"
SORT status ASC, updated DESC
```

## Seeds needing substance

```dataview
LIST
FROM "wiki"
WHERE status = "seed"
SORT file.name ASC
```

## Contested and low-confidence claims

```dataview
LIST
FROM "wiki"
WHERE confidence = "contested" OR contains(tags, "#confidence/contested") OR contains(tags, "#confidence/folklore")
SORT updated DESC
```

## Recently updated

```dataview
TABLE updated, status, confidence
FROM "wiki"
SORT updated DESC
LIMIT 15
```

## Seed Evidence Queue

### Gaps

- [[Mods API gaps requested in the 91870 thread but not shipped]]
- [[Unverified pre-release security findings on current builds]]
- [[Evidence Coverage Not Yet Verified]]

### Questions

- [[Does claude plugin test support userConfig values yet]]
- [[How is $.model.classify billed]]
- [[What Current Official Source Resolves The Highest Risk Claim]]

### Experiments

- [[Diff generated typings across two Claude Code versions]]
- Scan owned mods with the footprint scanner
- [[Source To Claim Spot Check Probe]]

Watch for `> [!gap]`, `> [!question]`, `> [!contradiction]`, `> [!stale]`, and `> [!done]` callouts in seed notes.

## Operating Links

- [[Source Intake Workflow]]
- [[Research Refresh Workflow]]
- [[Claim Verification Flow]]
- [[Explore Plan Code Commit]]
- [[Multi-Agent Fan-Out Research Flow]]
- [[Context Compaction Routine]]
- [[Synthesis Workflow]]
- [[Reporting Workflow]]
- Approval Queue
- Health Scorecard
- Action Roadmap
