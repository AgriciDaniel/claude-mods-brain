---
type: "flow"
title: "Research Refresh Workflow"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/flow"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "rewrite"
related:
  - "[[Re-verify After Release Flow]]"
  - "[[Versioning and API Drift]]"
  - "[[Version Pin Policy]]"
  - "[[Claude Code Release Channels]]"
  - "[[API Surface 2.1.288]]"
  - "[[Source Intake Workflow]]"
  - "[[Claim Verification Flow]]"
  - "[[Diff generated typings across two Claude Code versions]]"
  - "[[Pitfalls Playbook]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)"
sources:
  - "types-2-1-288"
  - "docs-mods-reference"
  - "docs-mods-create"
  - "docs-mods-overview"
  - "eco-npm-dist-tags"
  - "gh-issue-91870"
---

# Research Refresh Workflow

This brain is pinned to Claude Code 2.1.288: the typings capture, the API surface JSON, every note's `tested_on`, and every ledger `refresh_due` of 2026-11-02 assume it. When `claude --version` prints anything newer, the brain is stale until this flow runs: re-capture the typings and docs, import and diff the API surface, list the notes the drift touches, re-verify their claims, bump `tested_on` and `refresh_due`, and re-run the gates. [[Re-verify After Release Flow]] is the same idea for one mod; this flow is for the vault.

The public repo ships no `.raw/` captures: `references/source-ledger.json` cites each source by its public URL, and the typings line ranges in notes refer to the file Claude Code 2.1.288 writes. To refresh, you capture your own sources into your own `.raw/`: docs pages as `<page>.md` fetched with `curl`, and your own typings by loading a scratch mod once, since a load is what writes them. Everything below assumes that local `.raw/`.

## Trigger

- `claude --version` reports a version above `2.1.288` (the typings say the surface "may change between releases without notice", types 2.1.288 L1-10, C-LIF-043).
- `npm view @anthropic-ai/claude-code dist-tags --json` shows `stable` moving to 2.1.287 or later, which changes who has mods on by default (C-ECO-051, C-ECO-054).
- The monthly sweep date, 2026-11-02, arrives even if the version did not move (`refresh_cadence` in `references/source-ledger.json`).
- A #91870 staff comment announces a mods change.

## Prerequisites

- Owner approval to load one mod with `--plugin-dir`; that load is what writes fresh typings (docs-mods-create, C-LIF-042). Load only a scratch copy of the brain's synthetic display-only fixture (`cp -r tests/fixtures/mods/clean-band <scratch-dir>/clean-band`): it hooks one `ui.render` and calls only `$.session.usage` and `$.ui.resolve`. Never load a personal mod whose hooks run real side effects, or any third-party mod ([[Read Only Audit Decision]]). Rollback: delete the scratch folder.
- `python3`, `curl`, `gh`, `npm`, and `jq` on PATH.
- A clean read of `wiki/hot.md` so the refresh does not collide with work in flight.

## Steps

1. Record the versions and channels.

```bash
NEW=$(claude --version | cut -d' ' -f1); echo "$NEW"
npm view @anthropic-ai/claude-code dist-tags --json
```

2. Capture the typings into a new versioned folder in your `.raw/` (never overwrite an older one).

```bash
claude --plugin-dir <scratch-dir>/clean-band    # owner-approved load: wait for the prompt, type /exit
mkdir -p ".raw/captures/types-$NEW" && cp -r <scratch-dir>/clean-band/.claude-plugin/types/. ".raw/captures/types-$NEW/"
head -1 ".raw/captures/types-$NEW/claude-code/index.d.ts"   # must read: // Written by Claude Code $NEW.
```

3. Capture the ten mods docs pages and the plugin pages into `.raw/captures/docs-<date>/`, each as `<page>.md`, then the #91870 comments since the last capture ([[Source Intake Workflow]]):

```bash
D=.raw/captures/docs-$(date +%F); mkdir -p "$D"
for p in overview create reference interface gallery events api test troubleshoot admin; do
  curl -fsSL "https://code.claude.com/docs/en/plugins/mods/$p.md" -o "$D/plugins-mods-$p.md"
done
```

4. Hash the new captures so later diffs can be trusted: `find .raw -type f ! -name SHA256SUMS -exec sha256sum {} + > .raw/SHA256SUMS`.

5. Import and diff. `diff_api_surface.py` exits 0 for no drift, 1 for drift, 2 for bad input, and `--wiki` lists notes that mention changed names.

```bash
python3 scripts/import_mod_types.py --capture ".raw/captures/types-$NEW" --out "references/data/api-surface-$NEW.json"
python3 scripts/diff_api_surface.py --old references/data/api-surface-2.1.288.json \
  --new "references/data/api-surface-$NEW.json" --out "references/data/api-drift-2.1.288-to-$NEW.json" \
  --markdown ".gate-logs/drift-$NEW.md" --wiki wiki; echo "exit=$?"
```

6. Diff the docs captures against the previous date to catch prose-only changes the typings do not show (limits, render-site tables, admin settings):

```bash
diff -r .raw/captures/docs-<previous-date> ".raw/captures/docs-$(date +%F)" | grep -E "^[<>]" | head -80
```

7. List the affected notes. Start with `affected_notes` from the drift JSON, then add notes whose claims cite a changed line range:

```bash
jq -r '.affected_notes[]' "references/data/api-drift-2.1.288-to-$NEW.json"
grep -rln "types 2.1.288 L" wiki | sort > .gate-logs/notes-citing-typings.txt
```

Notes that always need a look: [[API Surface 2.1.288]] (regenerate as a new note), [[Mods API Cheatsheet]], [[Budgets and Limits]], [[Render Sites]], [[Pitfalls Playbook]] (every "Unanswered" row), [[Claude Code Release Channels]], and [[Mod Catalog]] tested-on cells.

8. Re-verify each touched claim through [[Claim Verification Flow]]: re-cite the new line range, keep or change the verdict, and set the claim's tested-on column to `$NEW`.

9. Regenerate the reports ([[Reporting Workflow]]):

```bash
python3 scripts/render_api_cheatsheet.py --surface "references/data/api-surface-$NEW.json" --out "wiki/reports/API Surface $NEW.md" --date "$(date +%F)"
```

then re-scan and re-synthesize for the capability matrix per [[Synthesis Workflow]].

10. Bump the dates. In each re-verified note set `tested_on: "$NEW"` and `updated`; in `references/source-ledger.json` set `retrieved` and `refresh_due` (30 days out) on every re-fetched source. Use the new surface JSON as the baseline for the next diff.

11. Re-run the public gates:

```bash
python3 scripts/lint_vault.py --vault .
python3 scripts/check_no_em_dash.py
python3 scripts/check_source_ids.py
python3 tests/test_adapters.py
```

12. Log it: one line in `wiki/log.md` and the new state in `wiki/hot.md`.

## Outputs

- Your local `.raw/captures/types-<new>/`, `docs-<date>/`, and their hashes.
- `references/data/api-surface-<new>.json` and a drift JSON (the self-diff baseline is `api-drift-2.1.288-self.json`, `change_count: 0`).
- A new `API Surface <new>` report, a refreshed matrix, re-dated claims and notes, and ledger entries that still cite public URLs.

## Gates

- The typings header names the new version. EVIDENCE-BASED
- Every note in `affected_notes` carries the new `tested_on` or an explicit caveat saying why not. PRACTITIONER
- No claim row cites a typings line range from the old file without a tested-on of the old version. PRACTITIONER
- Every public gate in step 11 exits 0. EVIDENCE-BASED

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Header still says 2.1.288 | The mod did not load (policy, `disableAllHooks`, refused module) | Read the `not loaded:` reason (docs-mods-troubleshoot) and retry with a minimal mod |
| Drift exit 2 | Capture is not a typings file or JSON is malformed | Check `claude-code/index.d.ts` exists in the capture folder |
| Drift exit 1 but no `affected_notes` | Change touches names no note mentions | Read the markdown drift report; it may be a build idea for [[Ranked Build Ideas]] |
| Docs diff shows only banner changes | Docs index text moved | Ignore; keep the new capture for dating |
| Typings changed, docs did not | Docs lag the binary | Typings win (C-LIF-043); note the lag as a contradiction |

## Rollback

All new artifacts sit in new paths, so rollback is deletion of `types-<new>/`, `docs-<date>/`, the new JSON files and the new report, then re-hash and a git checkout of edited notes and ledgers. The 2.1.288 baseline is never touched.

## Caveats

- The flow needs one owner-approved `--plugin-dir` load; an agent must not perform it unasked.
- The GitHub copy `mods/types/claude-code.d.ts` can serve as a cross-check but may trail the installed build (docs-mods-create, C-LIF-043).
- `stable` was 2.1.285 on 2026-10-03, so a refresh can be triggered by the channel without the installed version moving.

## Related

Version policy lives in [[Version Pin Policy]] and [[Versioning and API Drift]]; channel facts in [[Claude Code Release Channels]]. The falsifiable version of step 5 is [[Diff generated typings across two Claude Code versions]]. Intake of the new captures is [[Source Intake Workflow]].

## Sources

- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`, cited against https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- eco-npm-dist-tags: https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
