---
type: "meta"
title: "Provenance Trace Policy"
domain: "Claude Code mods"
status: "seed"
created: "2026-10-03"
updated: "2026-10-03"
tags:
  - "#domain/claude-code-mods"
  - "#type/meta"
  - "#confidence/practitioner"
confidence: "practitioner"
related:
  - "[[CONVENTIONS]]"
  - "[[index|Index]]"
  - "[[dashboard|Dashboard]]"
  - "[[Tag Taxonomy]]"
  - "[[Source Manifest Guide]]"
  - "[[Claim Verification Flow]]"
  - "[[Research Refresh Workflow]]"
  - "[[Source Intake Workflow]]"
  - "[[Synthesis Workflow]]"
  - "[[Reporting Workflow]]"
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

# Provenance Trace Policy

Confidence tag: practitioner.

Provenance trace rule: source to claim to note to decision to deliverable. Connect source, claim, note, decision, tool output, and deliverable so final answers can be audited.

## Operating Contract

- Trace for an API claim: typings line range or docs page, to a claim-ledger row (C-API, C-LIF, C-SEC, C-ECO, C-PAT), to the note, to the deliverable that uses it.
- Trace for an audit verdict: the mod at a pinned SHA, to `scripts/scan_mod.py` output in `references/data/scans/`, to the rendered `Mod Audit` report, to the human-read checklist result, to the catalog row.
- Every capture in `.raw/` is hashed in `.raw/.manifest.json`; pinned repos are listed in `.raw/upstream-manifest.json`.
- Keep claims advisory until the claim ledger and source ledger support them.
- Cite source notes, raw hashes, or official URLs for domain claims.

## Review Loop

1. Check [[dashboard|Dashboard]] for notes whose status, confidence, or freshness conflicts with this policy.
2. Check [[Tag Taxonomy]] when a note needs a new domain, type, or confidence tag.
3. Check [[Source Intake Workflow]] before turning raw material into a wiki claim.
4. Check [[Claim Verification Flow]] before moving a claim into a deliverable.
5. Check [[Research Refresh Workflow]] before relying on time-sensitive evidence.
6. Update [[log|Log]] when this policy changes a release gate or operator workflow.

## Failure Signals

- A deliverable cites no source note, raw hash, or official URL.
- A confidence value in body text disagrees with frontmatter.
- A note says evidence-based while the source ledger is empty.
- A public-facing page contains copied source text without attribution.
- A workflow asks an agent to mutate an external system in V1.
- A source is old enough to require refresh but no stale callout exists.

## See Also

- [[CONVENTIONS]] for the full vault contract.
- [[Tag Taxonomy]] for graph and Dataview tag rules.
- [[dashboard|Dashboard]] for status and confidence queries.
- [[Source Manifest Guide]] for source note requirements.
- [[Claim Verification Flow]] for evidence promotion.

## Related

- [[CONVENTIONS]]
- [[index|Index]]
- [[dashboard|Dashboard]]
- [[Source Manifest Guide]]
- [[Claim Verification Flow]]
- [[Research Refresh Workflow]]
