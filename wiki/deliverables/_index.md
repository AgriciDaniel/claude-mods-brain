---
type: "hub"
title: "Deliverables Hub"
domain: "Claude Code mods"
status: "active"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/hub"
  - "#confidence/practitioner"
confidence: "practitioner"
related:
  - "[[index|Index]]"
  - "[[hot|Hot]]"
  - "[[overview|Overview]]"
  - "[[dashboard|Dashboard]]"
  - "[[CONVENTIONS]]"
  - "[[Tag Taxonomy]]"
  - "[[Start Here]]"
  - "[[research-pack-claude-mods|Research Pack]]"
  - "[[Mod Catalog]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Org Mod Policy Guide]]"
  - "[[Patterns Playbook]]"
  - "[[Pitfalls Playbook]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
---

# Deliverables Hub

The outputs people act on: cheatsheet, playbooks, checklist, catalog, policy guide, roadmap, scorecard. Each cites its sources.

Parent: [[index|Index]]. Operating contract: [[CONVENTIONS]]. Evidence: [[research-pack-claude-mods|Research Pack]].

## Notes (8)

### api-and-events

- [[Mods API Cheatsheet]] (developing, evidence-based): One page for writing a Claude Code mod against build 2.1.288: the module skeleton, every event with what a hook may return, every `$` namespace, the render sites, the elements, and the limits.

### ecosystem

- [[Mod Catalog]] (developing, evidence-based): Forty mods from Anthropic (three pinned repos) and seven pinned community repos, each pinned to a commit, read statically, and graded on reach (L0 to L3), usage cost, tested-on version and a verdict.

### lifecycle

- [[Testing Playbook]] (developing, evidence-based): Test a mod in four layers: plain unit tests for pure functions, kit tests that fire events through the hooks with stubs standing for Claude Code, drawing tests that mount a render site on more than one surface, and polic...

### patterns-and-ideas

- [[Patterns Playbook]] (developing, evidence-based): Twenty-five reusable shapes, plus one structure pattern, for Claude Code mods on 2.1.288, each tied to an official example, or Anthropic's own mod code.
- [[Pitfalls Playbook]] (developing, evidence-based): The failure that matters most in mods is silent: a hook that throws, times out, or returns the wrong shape is skipped and the session carries on as if the mod were not there (docs-mods-troubleshoot).
- [[Ranked Build Ideas]] (developing, practitioner): The seed report ranked eight ideas by time saved, with post-turn-verify first (compass-report L380-391).

### security-governance

- [[Mod Security Audit Checklist]] (developing, evidence-based): Run this before any third-party mod is installed, in order.
- [[Org Mod Policy Guide]] (developing, evidence-based): Pick one of four policies, deploy its managed settings, then verify on a test machine with `claude --debug`.

## Related hubs

[[wiki/concepts/_index|Concepts Hub]] | [[wiki/flows/_index|Flows Hub]] | [[wiki/entities/_index|Entities Hub]] | [[wiki/platforms/_index|Platforms Hub]] | [[wiki/decisions/_index|Decisions Hub]] | [[wiki/reports/_index|Reports Hub]] | [[wiki/sources/_index|Sources Hub]] | [[wiki/gaps/_index|Gaps Hub]] | [[wiki/questions/_index|Questions Hub]] | [[wiki/experiments/_index|Experiments Hub]] | [[wiki/meta/_index|Meta Hub]] | [[wiki/canvases/_index|Canvases Hub]]
