---
type: "meta"
title: "Corpus Scope Policy"
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

# Corpus Scope Policy

Confidence tag: practitioner.

Corpus scope rule: each corpus note states harness, date, source, and non-scope. Each corpus note must state what the corpus proves, what it does not prove, source date, retrieval path, and non-scope boundaries.

## Operating Contract

- The typings corpus (`.raw/captures/types-2.1.288/`) proves names and shapes for Claude Code 2.1.288 only; it does not prove runtime behaviour, and it says nothing about 2.1.287 or later builds.
- The docs corpus (`.raw/captures/docs-2026-10-03/`) proves documented intent "as of v2.1.287"; where it disagrees with the typings, the typings win for the installed build and the note carries a contradiction callout.
- The #91870 capture proves what was asked and said by 2026-10-03; a staff comment is evidence of intent, not of a shipped API, until docs or typings confirm it.
- Community captures prove what a repo said at its pinned SHA; they never prove the mod is safe or works on the current build.
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
