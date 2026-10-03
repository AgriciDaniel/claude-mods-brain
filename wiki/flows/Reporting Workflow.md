---
type: "flow"
title: "Reporting Workflow"
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
  - "[[API Surface 2.1.288]]"
  - "[[Mod Audit code-modernization]]"
  - "[[Synthesis Workflow]]"
  - "[[Research Refresh Workflow]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Answer Engine Citability Policy]]"
  - "[[Mod Catalog]]"
  - "[[Pitfalls Playbook]]"
  - "[[Source Intake Workflow]]"
  - "[[Claim Verification Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)"
sources:
  - "types-2-1-288"
  - "docs-mods-reference"
  - "docs-mods-admin"
  - "eco-npm-dist-tags"
  - "gh-issue-91870"
---

# Reporting Workflow

The brain produces two kinds of report: generated reports that scripts write from JSON (the API surface, one audit per scanned mod, and a capability matrix across the mods you scanned), and hand-written notes that judge what the generated ones enumerate (catalog verdicts, pitfall rows, build ideas). Generated notes carry `generated_by: "scripts"` and are never hand-edited; if one is wrong, fix the input or the renderer and regenerate. Every report states the Claude Code version it describes, which on 2026-10-03 is 2.1.288.

## Trigger

- After [[Synthesis Workflow]] produced new scans or synthesis.
- After [[Research Refresh Workflow]] imported a new typings version.
- Before any decision (adopt, trial, avoid, build) that cites a report.

## Prerequisites

- `references/data/api-surface-<version>.json`, `references/data/scans/*.json`, `references/data/mods-synthesis.json` current against the source (check file times; see Synthesis step 7).
- `python3` and the repo root as working directory.

## Steps

1. Render the API surface report. It lists every engine, op and classic event, `$` namespace member, render component and element by surface, each with its typings line:

```bash
python3 scripts/render_api_cheatsheet.py --surface references/data/api-surface-2.1.288.json \
  --out "wiki/reports/API Surface 2.1.288.md" --date 2026-10-03
```

For a new version write a new note (`API Surface <new>.md`) rather than overwriting, so older citations keep resolving.

2. Render one audit per scanned mod. `--origin` must be a repo plus pin or a relative label, never an absolute path:

```bash
python3 scripts/render_mod_audit.py --scan references/data/scans/code-modernization.json \
  --out "wiki/reports/Mod Audit code-modernization.md" --date 2026-10-03 --tested-on 2.1.288 \
  --origin "claude-plugins-official@d182ca4 plugins/code-modernization"
python3 scripts/render_mod_audit.py --scan "references/data/scans/<your-mod>.json" \
  --out "wiki/reports/Mod Audit <your-mod>.md" --date "$(date +%F)" --tested-on 2.1.288 \
  --origin "<your-repo>@<sha> plugins/<your-mod>"
```

3. Render the capability matrix for the mods you scanned:

```bash
python3 scripts/render_capability_matrix.py --synthesis references/data/mods-synthesis.json \
  --out "wiki/reports/Capability Matrix.md" --date "$(date +%F)"
```

4. Write the hand-written notes from the generated ones. The pattern: a generated number, then a judgment, then a link.
   - [[Mod Catalog]]: a verdict per third-party mod, naming the method (static) and the version.
   - [[Pitfalls Playbook]]: new traps the audits surfaced.
   - A status note of your own, if you keep one: channels (`npm view @anthropic-ai/claude-code dist-tags --json`), installed version, drift (`jq .change_count` on the drift JSON), ecosystem changes, risks, next actions.

5. Check that the reports hub links every report, so none is orphaned.

6. Run the public gates:

```bash
python3 scripts/lint_vault.py --vault .
python3 scripts/check_no_em_dash.py
python3 scripts/check_source_ids.py
python3 tests/test_adapters.py
```

## Outputs

| Report | Writer | Input | Refresh |
|---|---|---|---|
| [[API Surface 2.1.288]] | `render_api_cheatsheet.py` | api-surface JSON | per release |
| Capability matrix | `render_capability_matrix.py` | synthesis JSON | per scan batch |
| `Mod Audit <name>`, for example [[Mod Audit code-modernization]] | `render_mod_audit.py` | one scan JSON | per source change |
| Catalog verdicts and pitfall rows | hand-written | audits plus a source read | per source change |

## Gates

- Generated notes keep `generated_by: "scripts"` and a `tested_on`; nobody hand-edits them. PRACTITIONER
- No absolute path, token or email in any report (`python3 scripts/check_no_em_dash.py`). EVIDENCE-BASED
- Every number in a hand-written note traces to a JSON field, a ledger claim, or a capture. PRACTITIONER
- `python3 scripts/lint_vault.py --vault .` passes: no dead wikilinks, every report has incoming links. EVIDENCE-BASED

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Audit report contradicts the source | Scan predates source edits | Re-scan, then re-render (Synthesis step 7) |
| Lint warns `zero incoming wiki notes` on reports | Reports not linked from hubs or notes | Link from the reports hub and the hand-written notes |
| Matrix shows `unknown_events` | Surface older than the mods | Re-import the typings ([[Research Refresh Workflow]]) |
| Status numbers disagree with npm | dist-tags moved since capture | Re-capture with the date in the header ([[Source Intake Workflow]]) |

## Rollback

Generated reports are reproducible: `git checkout` the note or re-run the renderer on the previous JSON. Hand-written notes roll back through git.

## Caveats

- `render_mod_audit.py` reports what a regex saw; its "worst flag: none" is not a clean bill. A personal mod reviewed for this brain got "none", yet a hand read of its source found two pitfall failures, one of them pane state kept in module variables.
- Publishing any report outside the vault is the owner's decision.
- Each audit binds to the commit scanned; regenerate it after every later commit.

## Related

The narrative reference behind the generated surface is [[Mods API Cheatsheet]]. Audit example: [[Mod Audit code-modernization]]. Citation and quote rules follow [[Answer Engine Citability Policy]]. Inputs come from [[Synthesis Workflow]]; trap columns come from [[Pitfalls Playbook]]; new claims go through [[Claim Verification Flow]].

## Sources

- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- eco-npm-dist-tags: https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
