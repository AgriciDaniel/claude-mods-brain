---
type: "hub"
title: "Questions Hub"
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
  - "[[Does claude plugin test support userConfig values yet]]"
  - "[[How is $.model.classify billed]]"
  - "[[What Current Official Source Resolves The Highest Risk Claim]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
---

# Questions Hub

Open and answered questions, each with its evidence and the experiment that would settle it.

Parent: [[index|Index]]. Operating contract: [[CONVENTIONS]]. Evidence: [[research-pack-claude-mods|Research Pack]].

## Notes (3)

### patterns-and-ideas

- [[Does claude plugin test support userConfig values yet]] (developing, evidence-based): Yes, on 2.1.288 according to the generated typings: `test` takes an options object before the body, and its `options` field holds "the plugin under test's `userConfig` values, standing as the ones stored in settings" (ty...
- [[How is $.model.classify billed]] (developing, practitioner): Short answer: `$.model.classify` is one `$.model.complete` call in disguise, so it is billed exactly like `$.model.complete`: to the user's own plan or API key through the session's own API client, on the engine's small ...

### rewrite

- [[What Current Official Source Resolves The Highest Risk Claim]] (developing, evidence-based): Answer: there is no single source.

## Related hubs

[[wiki/concepts/_index|Concepts Hub]] | [[wiki/flows/_index|Flows Hub]] | [[wiki/deliverables/_index|Deliverables Hub]] | [[wiki/entities/_index|Entities Hub]] | [[wiki/platforms/_index|Platforms Hub]] | [[wiki/decisions/_index|Decisions Hub]] | [[wiki/reports/_index|Reports Hub]] | [[wiki/sources/_index|Sources Hub]] | [[wiki/gaps/_index|Gaps Hub]] | [[wiki/experiments/_index|Experiments Hub]] | [[wiki/meta/_index|Meta Hub]] | [[wiki/canvases/_index|Canvases Hub]]
