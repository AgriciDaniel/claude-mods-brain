---
type: "experiment"
title: "Diff generated typings across two Claude Code versions"
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
  - "[[Versioning and API Drift]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Version Pin Policy]]"
  - "[[API Surface 2.1.288]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Mods API Namespaces]]"
  - "[[Render Sites]]"
  - "[[Claude Code Release Channels]]"
  - "[[Hot Reload and Dev Loop]]"
  - "[[Evidence Coverage Not Yet Verified]]"
  - "[[Read Only Audit Decision]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)"
sources:
  - "types-2-1-288"
  - "docs-mods-create"
  - "docs-mods-reference"
  - "eco-npm-dist-tags"
---

# Diff generated typings across two Claude Code versions

The experiment detects mods API drift between Claude Code releases by importing the typings each version writes beside a mod and diffing the two surfaces. On 2026-10-03 only one version's typings exist: the 2.1.288 self-diff returns 0 changes, which proves the pipeline is deterministic but says nothing about drift yet. A 2.1.287 capture was not possible, because a Claude Code build writes its typings only when a session loads a mod, and the binaries embed them compressed. Rerun on the next release.

## Hypothesis

Each Claude Code release can add, remove or rename events, `$` namespace members, render components, and elements. The docs are undated and describe the surface "as of v2.1.287" (docs-mods-reference), while docs-mods-create says to trust the generated types over any page. A mechanical diff of two typings captures should therefore list every name-level change and the vault notes that mention it.

## Why typings, and why only one version

- The typings header says they are "Written by the engine each time it loads a mod" from a folder the person owns, beside the mod as `.claude-plugin/types/claude-code/index.d.ts`, and that the first line names the writing version (types 2.1.288 L1-12).
- So a capture needs a session that loads a mod. The brain's hard rule forbids loading a mod ([[Read Only Audit Decision]]); the 2.1.288 capture in `.raw/captures/types-2.1.288/` was supplied by the lead on 2026-10-03 from typings the installed build had written.
- 2.1.287 (published 2026-10-01T16:59Z) had been replaced by 2.1.288 (2026-10-02T18:30Z) before capture (eco-npm-dist-tags). The installed binary embeds the declarations compressed, so they cannot be read out of an old binary with plain text tools.

## Method

Both scripts are read-only on their inputs and write one JSON file each.

```bash
# 1. Import a typings capture into an API surface (mods-brain.api-surface.v1)
python3 scripts/import_mod_types.py \
  --capture .raw/captures/types-2.1.288 \
  --out references/data/api-surface-2.1.288.json

# 2. Diff two surfaces (mods-brain.api-drift.v1); exit 0 no drift, 1 drift, 2 bad input
python3 scripts/diff_api_surface.py \
  --old references/data/api-surface-2.1.288.json \
  --new references/data/api-surface-<next>.json \
  --out references/data/api-drift-2.1.288-<next>.json \
  --markdown <drift-report>.md \
  --wiki wiki
```

The importer reads `claude-code/index.d.ts`, takes the version from the `// Written by Claude Code` line, and records events (engine, op, classic), the 21 namespaces with members, render components, elements by surface, and exported type names, each with a line number. The differ compares eight sections by name, sets `typings_identical` by comparing sha256, and with `--wiki` lists notes that mention any added or removed name (tokens of 4 or more characters).

The same pair can run as a release check: re-import your current capture and diff it against the stored surface; a non-zero exit means drift.

## Result on 2026-10-03

Rerun by this pass into a scratch folder; output matched the stored files exactly.

| Item | Value |
|---|---|
| Version | 2.1.288 |
| Source | `claude-code/index.d.ts`, 14,973 lines, sha256 `d0531eb1b9f9...` |
| Engine events | 43 |
| Op events | 61 |
| Classic events | 33 |
| `$` namespaces | 21 (81 members) |
| Render components | 15 (`AskUserQuestion` to `Pane`) |
| Element surfaces | terminal, desktop, mobile, vscode |
| Exported types | 439 |
| Self-diff change count | 0, `typings_identical: true`, `affected_notes: []`, exit 0 |

Stored outputs: `references/data/api-surface-2.1.288.json`, `references/data/api-drift-2.1.288-self.json`. Report: [[API Surface 2.1.288]].

## Interpretation

- **Determinism confirmed.** Two imports of the same capture produce identical JSON, so any future non-zero diff is real drift, not noise.
- **No drift measured yet.** One version cannot show change. The docs-versus-typings contradictions already in the ledger (surfaces, Svg, `next.is`, `next.event`, `next.trace`, `$.ui.selection`; C-API-014, C-API-041, C-API-049, C-API-050) are docs lag, not version drift, and this experiment does not detect them.
- **Name-level only (resolved 2026-10-03).** At the time of this probe the differ compared names only; it now also compares member and event signatures and every limit-bearing line, and flags `manual_review_required` when the hash moves with nothing named changing ([[Versioning and API Drift]]). The original finding: the differ compared names. A changed default (for example `$.model.complete` going from 256 to 1,024 default tokens between 2.1.272 and launch, C-PAT-034), a new optional field, or a changed doc comment shows only as `typings_identical: false` with zero named changes. Read the text diff of `index.d.ts` whenever that happens.
- **Line numbers drift even with no API change.** 110 ledger rows cite typings line ranges ([[Evidence Coverage Not Yet Verified]]); any reflow breaks them.

## Trigger to rerun

Rerun on the next Claude Code release (anything after 2.1.288 on `latest`), and again when `stable` passes 2.1.287 ([[Claude Code Release Channels]]).

1. After the update, open a session where the build loads any already-trusted mod so it rewrites `.claude-plugin/types/` (needs the owner's approval under the lane rules).
2. Copy the folder to `.raw/captures/types-<version>/`.
3. Run the two commands above with `--old` 2.1.288 and `--new` the new version.
4. Exit 1: follow [[Re-verify After Release Flow]] for each affected note; exit 0 with `typings_identical: false`: diff the raw file by hand.
5. Update `tested_on` in the affected notes and the [[Version Pin Policy]] tested-on line.

## Recommendations

- Keep every typings capture under `.raw/captures/types-<version>/`; never overwrite one. EVIDENCE-BASED
- Treat a sha change with zero named changes as drift that needs a human read. PRACTITIONER
- Done 2026-10-03: `diff_api_surface.py` diffs signatures and limit lines; tested on fixtures (`tests/test_adapters.py`). PRACTITIONER

## Caveats

- Only one version captured; the experiment has not yet produced its intended result.
- The importer's regexes are tuned to the 2.1.288 file layout; a reformatted file could under-count.

## Related

Drift policy: [[Versioning and API Drift]], [[Version Pin Policy]], [[Re-verify After Release Flow]]. Current surface: [[API Surface 2.1.288]], [[Mods API Cheatsheet]], [[Mods API Namespaces]], [[Render Sites]]. Release timing: [[Claude Code Release Channels]]. Why capture needs a loaded mod: [[Hot Reload and Dev Loop]], [[Read Only Audit Decision]].

## Sources

- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` L1-12 (written by Claude Code 2.1.288, retrieved 2026-10-03)
- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- eco-npm-dist-tags: https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03), capture `.raw/captures/lanes-2026-10-03/ecosystem/eco-npm-claude-code-dist-tags.md`
- Scripts: `scripts/import_mod_types.py`, `scripts/diff_api_surface.py`
- Data: `references/data/api-surface-2.1.288.json`, `references/data/api-drift-2.1.288-self.json`
