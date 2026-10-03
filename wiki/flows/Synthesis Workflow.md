---
type: "flow"
title: "Synthesis Workflow"
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
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Reach Levels]]"
  - "[[Usage Cost Surface]]"
  - "[[Mod Catalog]]"
  - "[[Ranked Build Ideas]]"
  - "[[Reporting Workflow]]"
  - "[[Plugin Validate]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-plugins-official/tree/d182ca456ca09d31d139f7d3818d1d333b103cce/plugins/code-modernization (retrieved 2026-10-03)"
sources:
  - "types-2-1-288"
  - "docs-mods-reference"
  - "docs-mods-admin"
  - "docs-mods-create"
  - "code-modernization-1-0-0"
---

# Synthesis Workflow

Synthesis turns three machine inputs into one model of "who uses what": the API surface imported from the typings, a static footprint scan per mod, and an optional curated catalog. `scripts/synthesize_mods.py` joins them into `references/data/mods-synthesis.json`, which the renderers turn into a capability matrix and per-mod audit reports. On 2026-10-03 it covered 6 scanned mods (five personal mods reviewed for this brain plus code-modernization) against 43 engine events, of which 9 are used and 34 are not. Everything here is static: no mod is loaded or run.

## Trigger

- A new mod enters scope: a mod you own, an official sample, or a community repo pinned for [[Mod Catalog]].
- The API surface changed after a release ([[Research Refresh Workflow]]).
- A mod you own gets a new commit; scans of an older commit go stale silently.

## Prerequisites

- `references/data/api-surface-2.1.288.json` (schema `mods-brain.api-surface.v1`, 43 engine events, 61 op events, 33 classic events, 21 `$` namespaces, 439 exported types).
- A read-only copy of each mod's plugin directory. For third-party code, a pinned capture; for your own mods, read in place, never edited by the scan.
- Optional: the JSON `claude plugin validate --json <dir>` printed, saved to a file (static, allowed).

## Steps

1. Import the surface (once per Claude Code version). The public repo ships the resulting JSON but no `.raw/` captures; to re-import, point `--capture` at your own typings capture ([[Research Refresh Workflow]]):

```bash
python3 scripts/import_mod_types.py --capture .raw/captures/types-2.1.288 \
  --out references/data/api-surface-2.1.288.json
```

2. Validate each mod statically and keep the JSON. Run it on each plugin folder, not a marketplace root (Pitfalls L6):

```bash
claude plugin validate --json <mod-dir> > .gate-logs/validate-<name>.json; echo "exit=$?"
```

3. Scan each mod. The scanner reads `plugin.json`, `hooks/hooks.json` and every module file, and emits events with matchers, `$` calls, classic hooks, a reach level (L0 draws, L1 reads, L2 writes, runs or drives Claude, L3 network), the cost surface, and red flags:

```bash
python3 scripts/scan_mod.py --plugin <mod-dir> --out references/data/scans/<name>.json \
  --validate-json .gate-logs/validate-<name>.json
```

4. Synthesize. The verdict rule is a suggestion only: any critical flag gives avoid; any high or medium flag, L3 reach, or classic settings hooks shipped beside the mod gives trial; otherwise adopt-candidate.

```bash
python3 scripts/synthesize_mods.py --surface references/data/api-surface-2.1.288.json \
  --scans references/data/scans --out references/data/mods-synthesis.json
```

Add `--catalog <file>` with a `mods-brain.catalog.v1` JSON to merge community rows by name.

5. Render. Each renderer writes one wiki note with `generated_by: "scripts"`:

```bash
python3 scripts/render_mod_audit.py --scan references/data/scans/code-modernization.json \
  --out "wiki/reports/Mod Audit code-modernization.md" --date 2026-10-03 --tested-on 2.1.288 \
  --origin "claude-plugins-official@d182ca4 plugins/code-modernization"
python3 scripts/render_capability_matrix.py --synthesis references/data/mods-synthesis.json \
  --out "wiki/reports/Capability Matrix.md" --date 2026-10-03
```

6. Turn outputs into notes by hand. Generated reports enumerate; hand-written notes judge. For each scan:
   - Read every `event-rewrite` flag in source (the scanner cannot judge a `next({ ...e })`), as the [[Audit a Third-Party Mod Flow]] requires.
   - Move the verdict into [[Mod Catalog]] (third-party) or your own health notes (owned), naming the method (static) and version.
   - Add new traps to [[Pitfalls Playbook]] and unused-event opportunities to [[Ranked Build Ideas]].
   - Record any new fact as a claim row ([[Claim Verification Flow]]).

7. Compare the scan with the source before citing it, and record the commit scanned. On 2026-10-03 the stored scans of the personal mods were written at 00:38, six minutes before the commit later audited (00:44); one mod's scan lists five events, while its committed source also hooks `session.end` to reset state after `/clear`, `/resume` and `/branch`. Re-scan at each new commit and pass `--origin <repo>@<sha>` to the renderer.

## Outputs

- `references/data/scans/<name>.json` (`mods-brain.mod-scan.v1`), one per mod.
- `references/data/mods-synthesis.json` (`mods-brain.synthesis.v1`): `event_matrix` (43), `namespace_matrix` (21), `unused_events` (34), `op_event_hooks`, `unknown_events` (0), per-mod suggestions.
- `wiki/reports/Mod Audit <name>.md` and a rendered capability matrix note.

## Gates

- `unknown_events` is empty; a hooked event missing from the surface means drift or a typo. EVIDENCE-BASED
- Every scan path is relative to the plugin directory; no absolute paths reach the JSON or notes (`check_no_em_dash.py` enforces). EVIDENCE-BASED
- A verdict in a note names who read the source; a synthesis suggestion alone never becomes adopt. PRACTITIONER
- `python3 tests/test_adapters.py` passes (fixtures for importer, scanner, synthesis, renderers, malformed input). EVIDENCE-BASED

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| A `$` call missing from the scan | Aliased `$`, call split across lines, dynamic name | Grep the source by hand; cctop's `prompt.fill` was found that way |
| Scan shows fewer events than source | Source changed after the scan, or regex miss | Re-scan; diff `hooks:` from validate JSON against the scan |
| Reach under-graded | `process.spawn` or `session.send` not mapped to L2 | Check the admin risk table (docs-mods-admin) by hand |
| Matrix says an event is unused but a mod uses it | Event hooked through a classic settings hook | Read `hooks.json` `hooks` key; classic hooks are listed separately |

## Rollback

Scans and synthesis are derived data: delete the JSON and the rendered notes and re-run steps 1 to 5. Hand-written verdicts change only through a normal note edit with git history.

## Caveats

- The scanner is regex over source; it lowers risk but proves nothing absent ([[Read Only Audit Decision]]).
- Synthesis has no runtime data: "unused" means no scanned mod hooks the event, not that it is useless.

## Related

Inputs come from [[API Surface 2.1.288]] and [[Plugin Validate]]; grading scales from [[Reach Levels]] and [[Usage Cost Surface]]; the human checklist from [[Mod Security Audit Checklist]]. Example output: [[Mod Audit code-modernization]]. Rendering and publishing of the outputs is [[Reporting Workflow]].

## Sources

- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- code-modernization-1-0-0: https://github.com/anthropics/claude-plugins-official/tree/d182ca456ca09d31d139f7d3818d1d333b103cce/plugins/code-modernization (retrieved 2026-10-03)
