---
type: "flow"
title: "Multi-Agent Fan-Out Research Flow"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/flow"
  - "#confidence/practitioner"
confidence: "practitioner"
lane: "rewrite"
related:
  - "[[Source Intake Workflow]]"
  - "[[Claim Verification Flow]]"
  - "[[Context Compaction Routine]]"
  - "[[Read Only Audit Decision]]"
  - "[[Corpus Scope Policy]]"
  - "[[Provenance Trace Policy]]"
  - "[[research-pack-claude-mods|Research Pack]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Mod Catalog]]"
  - "[[Pitfalls Playbook]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Testing Playbook]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)"
  - "https://claude.com/blog/claude-code-mods (retrieved 2026-10-03)"
sources:
  - "docs-mods-overview"
  - "docs-mods-reference"
  - "gh-issue-91870"
  - "blog-mods-launch"
  - "types-2-1-288"
---

# Multi-Agent Fan-Out Research Flow

This brain was built on 2026-10-03 with parallel research lanes, a merge, automated gates, and a fresh-context critic. One lead captures the shared evidence, writes a single contract (the lane brief), fans out five independent lane agents that write only into their own candidates folder, merges the candidates deterministically, runs every deterministic gate, and hands the result to a fresh-context critic that never sees the builders' self-assessment. The five lanes produced 65 notes and 301 claim rows; rewrite passes (this note came from one) then replaced the generic seed notes under the same contract. The recipe below is reusable for any domain; the orchestration files themselves are not shipped in this repo.

## Trigger

- A brain needs broad, source-cited coverage faster than one context can read it (here: ten docs pages, a 14,973-line typings file, a 235-comment thread, ten repos).
- A refresh touches several areas at once, for example a release that moves events, limits and the ecosystem together.

## Prerequisites

- A job description written before any agent starts: goal, audience, the lanes, non-goals (here: no installing or loading mods, no edits to audited repos, no publishing), constraints, protected paths (the raw captures, the confidence tag rules, the lint and audit scripts, `tests/`), the gates, the critic, and the stop condition.
- Shared captures made by the lead first, so lanes cite the same bytes: docs pages, web captures, the generated typings, and pinned official mod source, all in the lead's own `.raw/` ([[Source Intake Workflow]]). The public repo ships none of these; `references/source-ledger.json` cites each by URL.
- The note registry: each title has exactly one owning lane.

## Steps

1. Write the job description and the lane brief. The brief fixes hard rules (no em or en dashes, quotes of 15 words or fewer, no home paths), the evidence ranking, canonical source ids, the shapes of each lane's source list and claim table, the note contract, and the registry.

2. Fan out one agent per lane, in parallel, each with the same brief and its own slice:

| Lane | Owns | Claim prefix | Notes | Claims |
|---|---|---|---|---|
| api-and-events | events, `$`, render sites, budgets | C-API | 14 | 60 |
| lifecycle | dev loop, validate, test, publish, drift | C-LIF | 13 | 60 |
| security-governance | trust, reach, org controls, audits | C-SEC | 10 | 63 |
| ecosystem | built-ins, samples, community repos, channels | C-ECO | 15 | 58 |
| patterns-and-ideas | patterns, pitfalls, build ideas | C-PAT | 13 | 60 |

Each lane writes only inside its own candidates folder (for example `candidates/<lane>/`): a source list in JSON, a claim table, a contradictions list, its captures, `notes/<folder>/<Title>.md`, and a report under 300 words. Nothing a lane writes touches `wiki/` or the ledgers directly.

3. Dry-run the merge, then merge. The merge is a small deterministic script you write once. It copies notes into `wiki/`, applies title renames (for example `#91870` titles become "issue 91870"), unions the lane source lists into `references/source-ledger.json` (dedupe by id, earliest `retrieved`, latest `refresh_due`), keeps evidence with no public URL out of the public `sources` list, appends claim rows to `references/claim-ledger.md`, and reports dead wikilinks. The dry run prints the same report without writing anything.

A rewrite pass is merged the same way, as one more candidates folder.

4. Fix dead links the merge reports, then run the gates. The ones that ship with this repo:

```bash
python3 scripts/lint_vault.py --vault .
python3 scripts/check_no_em_dash.py
python3 scripts/check_source_ids.py
python3 tests/test_adapters.py
```

They cover vault lint (dead links, frontmatter, orphans), no dashes, secrets or home paths, every cited source id present in the ledger, and the adapter tests. After the merge, also regenerate the index hubs with `python3 scripts/build_spine.py --date "$(date +%F)"` and the [[research-pack-claude-mods|Research Pack]] with `python3 scripts/render_research_pack.py --date "$(date +%F)"`; the pack reads #91870 comment dates from a local thread capture under `.raw/`, so capture the thread first (the script looks for `.raw/captures/web-2026-10-03/gh-issue-91870.md`). The original build ran 14 gates in all, adding a capture hash check, an API surface drift check against the baseline, and a structural rubric. Each gate prints pass or fail with a log.

5. Send a fresh critic. Give it the artifacts, the rubric and the corpus; do not give it the lane reports. It answers "what is wrong", not "is this good".

6. Run rewrite passes for anything still generic, each with its own candidates folder and the same contract.

7. Stop when every gate exits 0 and the structural rubric reports zero critical failures (the job's stop condition).

## Outputs

- `wiki/` notes, `references/source-ledger.json` (50 sources on 2026-10-03), `references/claim-ledger.md` (301 rows), lane captures kept in the lead's local `.raw/`, gate logs.

## Gates

- No lane wrote outside its candidates folder (check with `git status` before merge). EVIDENCE-BASED
- The merge dry run reports no source problems such as a source with no claims. PRACTITIONER
- All gates pass. EVIDENCE-BASED
- The critic's findings are resolved or logged as gaps, never argued away by the builder. PRACTITIONER

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Two lanes write the same fact differently | Overlap in the registry | One owner per title; others link |
| Dead links after merge | Lane linked a title outside the registry or a renamed one | Fix in the candidate and re-merge, or add the rename to the merge |
| Seed report claims leak in as facts | Lane trusted rank 7 alone | [[Claim Verification Flow]]; mark SINGLE-SOURCE |
| A lane tries to load a mod to "check" | Brief ignored | Hard rule: static only ([[Read Only Audit Decision]]) |
| Gates fail on lint after merge | Seed notes still generic, reports unlinked | Rewrite pass, link reports from hubs |

## Rollback

Merging is the only step that touches `wiki/` and the ledgers. Before merging, snapshot with git; to undo, `git checkout -- wiki references/source-ledger.json references/claim-ledger.md`. Candidate folders stay as the record of what each lane produced.

## Caveats

- The critic step is defined in the job description; its findings for this build are not recorded in this note.
- Fan-out saves wall time but costs usage per lane; five lanes plus rewrites is the size used here, not a recommendation for every refresh.

## Related

Context discipline for each lane agent is [[Context Compaction Routine]]. Scope and provenance rules: [[Corpus Scope Policy]], [[Provenance Trace Policy]]. Lane outputs include [[Mods API Cheatsheet]], [[Mod Catalog]], [[Mod Security Audit Checklist]], [[Testing Playbook]] and [[Pitfalls Playbook]]; the assembled corpus is the [[research-pack-claude-mods|Research Pack]].

## Sources

- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
- blog-mods-launch: https://claude.com/blog/claude-code-mods (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
