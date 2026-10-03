---
type: "flow"
title: "Re-verify After Release Flow"
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
lane: "lifecycle"
related:
  - "[[Versioning and API Drift]]"
  - "[[Version Pin Policy]]"
  - "[[Plugin Validate]]"
  - "[[Testing Kit]]"
  - "[[Testing Playbook]]"
  - "[[Claude Code Release Channels]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Research Refresh Workflow]]"
  - "[[Claim Verification Flow]]"
  - "[[Publish a Mod Flow]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
sources:
  - "docs-mods-create"
  - "docs-mods-reference"
  - "docs-mods-troubleshoot"
  - "types-2-1-288"
  - "code-modernization-1-0-0"
  - "a local `claude plugin validate --json` run"
---

# Re-verify After Release Flow

The mods API is early access and the typings say it "may change between releases without notice" (types L1-10, C-LIF-043). After every Claude Code update, re-run a fixed check sequence against each mod you maintain: regenerate types, diff them against a saved baseline, type-check, validate strictly, run tests, smoke-load, then update the README tested-on line and the vault's claims. Even Anthropic's own code-modernization 1.0.0 already trails 2.1.288 (C-LIF-059), so assume drift until shown otherwise.

## Trigger

- `claude --version` changed (auto-update, manual update, a new Desktop bundle).
- A changelog or #91870 post mentions mods, `claude plugin`, or the typings.
- The monthly vault refresh (`refresh_due` 2026-11-02) arrives ([[Research Refresh Workflow]]).

## Prerequisites

- Each mod keeps a baseline copy of the typings it last passed on, for example `types-baseline/claude-code-<version>.d.ts` committed to the repo (the engine's `.claude-plugin/types/` is regenerated on every load, so it cannot serve as history; C-LIF-042).
- TypeScript 5.4 or newer available, for example via `npx -p typescript@5 tsc` (typings header).
- `jq` for reading `validate --json`.

## Steps

1. Record the new version and compare it with the README line.

```bash
claude --version
grep -n "Tested on Claude Code" ~/mods/turn-band/README.md
```

2. Regenerate the types by loading the mod once. This is a load: do it only for a mod you own, with the owner's explicit approval, and know the rollback (quit the session; nothing installs). Never do this to an audited third-party mod; for the brain's own typings capture, load a scratch copy of `tests/fixtures/mods/clean-band` instead. Any load from a folder you own rewrites `.claude-plugin/types/` (C-LIF-042). Start a session, wait for the prompt, and type `/exit`; for a mod with its own command, a headless `claude -p "/<command>" --plugin-dir <dir>` also loads it (docs-mods-create).

```bash
cd ~/mods/turn-band
claude --plugin-dir ~/mods/turn-band
head -1 .claude-plugin/types/claude-code/index.d.ts
```

The first line must name the new build, as in `// Written by Claude Code 2.1.288.`. If it still names the old one, the module did not load: see Failure Modes.

3. Diff the API surface against the baseline. Full diffs are long (the 2.1.288 file is 14,973 lines), so diff the exported names first, then read the hunks for names you use.

```bash
OLD=types-baseline/claude-code-2.1.288.d.ts
NEW=.claude-plugin/types/claude-code/index.d.ts
diff <(grep -oE "export (type|const|interface) [A-Za-z]+" "$OLD" | sort -u) \
     <(grep -oE "export (type|const|interface) [A-Za-z]+" "$NEW" | sort -u)
diff <(grep -oE "'[a-z]+\.[a-zA-Z]+'" "$OLD" | sort -u) <(grep -oE "'[a-z]+\.[a-zA-Z]+'" "$NEW" | sort -u)
diff -u "$OLD" "$NEW" | grep -nE "^[-+].*(tool\.call|ui\.open|AbovePrompt|Pane: \{|TestOptions|mount)" | head -50
```

The second diff lists event-name literals, a quick signal for added or renamed events. Also diff `claude-code-tools/index.d.ts` if your guards depend on tool input shapes.

4. Type-check against the new declarations. The engine adds a root `tsconfig.json` that extends the generated one when you have none (C-LIF-042).

```bash
npx -p typescript@5 tsc -p ~/mods/turn-band
```

5. Validate strictly and compare the inventory with the one recorded at last release (C-LIF-014, C-LIF-015).

```bash
claude plugin validate --strict --json ~/mods/turn-band > validate-new.json; echo "exit=$?"
jq -r '.success, (.manifest.errors[]?), (.contents[].errors[]?), (.contents[].warnings[]?)' validate-new.json
jq -r '.contents[].notes[]' validate-new.json | sort > inventory-new.txt
diff inventory-baseline.txt inventory-new.txt
```

On 2.1.288 the inventory arrives as strings in `contents[].notes` (a local `claude plugin validate --json` run). A changed `hooks:` or `calls:` line without a code change means the static analyzer changed; investigate before shipping.

6. Run the tests (C-LIF-022). Exit status 1 means a failure; read the `the engine reported:` block for skipped hooks (C-LIF-025).

```bash
cd ~/mods/turn-band && claude plugin test
```

If it prints `hooks modules are turned off`, the run tells you mods cannot load in this shell, not that your mod broke (C-LIF-033).

7. Smoke-load in a real session with a debug log, because tests check trees, not paint (C-LIF-031).

```bash
claude --plugin-dir ~/mods/turn-band --debug-file ./reverify-debug.log
grep -E "turn-band" ./reverify-debug.log | grep -E "loaded|not loaded|hook skipped|refused|does not validate"
```

Expect `hooks module turn-band@inline loaded (...); events: ...` and no `hook skipped` or `refused` lines (C-LIF-009). Exercise each feature once on every surface you support.

8. Record the result.

```bash
cp .claude-plugin/types/claude-code/index.d.ts "types-baseline/claude-code-$(claude --version | cut -d' ' -f1).d.ts"
cp inventory-new.txt inventory-baseline.txt
sed -i "s/^Tested on Claude Code .*/Tested on Claude Code $(claude --version | cut -d' ' -f1). Re-verified $(date +%F)./" README.md
```

Then update the vault: set `tested_on` on affected notes, re-check claims tagged with the old version through [[Claim Verification Flow]], and bump `version` and republish if code changed ([[Publish a Mod Flow]]).

Drift tooling for the brain's own capture: `python3 -m mods_brain.cli surface --capture .raw/captures/types-<new> --out references/data/api-surface-<new>.json`, then `python3 scripts/diff_api_surface.py --old references/data/api-surface-2.1.288.json --new references/data/api-surface-<new>.json --out references/data/api-drift-<new>.json --wiki wiki --note "wiki/reports/API Drift 2.1.288 to <new>.md" --date <today>`. The report covers names, signatures, and limit lines; act on `manual_review_required` by diffing the two files by hand ([[Versioning and API Drift]]).

## Outputs

- A new typings baseline and inventory baseline per mod, a refreshed README tested-on line, and a dated re-verification.
- A short drift log: added, removed or renamed exports and events that touch your mods.

## Gates

- `head -1` of the generated typings names the new version. EVIDENCE-BASED
- `tsc -p` exits 0; `validate --strict --json` reports `success: true` with no errors or warnings. EVIDENCE-BASED
- `claude plugin test` exits 0, and the debug log has a `loaded` line and no `hook skipped` lines. EVIDENCE-BASED
- An export or event you use disappeared or changed shape: stop, fix, re-run from step 4; do not update the tested-on line. EVIDENCE-BASED
- Treat docs as lagging: when docs and typings disagree, typings win (docs-mods-create, C-LIF-043). EVIDENCE-BASED

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Types header still names the old version | Module refused or mods off (`--safe-mode`, `disableAllHooks`, policy) | Read the `not loaded:` reason in stderr or the debug log (docs-mods-troubleshoot) |
| `tsc` errors only in tests on a newer kit call | Kit grew a feature the old declarations lacked | Code-modernization casts `$.ui.mount` for exactly this (C-LIF-059); prefer regenerating over casting |
| Validate now fails a pattern that passed before | Static rules tightened | Rewrite to the rule named in the error (C-LIF-017) |
| Tests pass, session shows `refused:` on a render site | Tree valid for the kit's table, not the live surface | Fix props; tests do not check paint (C-LIF-031) |
| `reload failed, the previous version stays loaded:` | New build rejects the module at reload | Fix the named error; the old version keeps running meanwhile (C-LIF-009) |

## Rollback

If a mod breaks on the new build and cannot be fixed quickly: disable it in `/plugin`, or tell users to; publish a release whose README lists the last working Claude Code version; and, for a broken Claude Code release itself, pin or roll back the Claude Code channel ([[Claude Code Release Channels]]). Restore the previous typings baseline from git to keep comparing.

## Caveats

- The generated `claude-code-mcp/index.d.ts` reflects MCP tools connected at the last reload, so its diff is noisy and machine-specific (docs-mods-create).
- Event-literal grep in step 3 is a heuristic and misses changes to field shapes; read hunks for every type you import.
- Not executed end to end by this lane: only `claude --version` and `validate --json` were run (a local `claude plugin validate --json` run).

## Related

Why drift happens and how to read it: [[Versioning and API Drift]]; what to pin and promise: [[Version Pin Policy]]. Check tools: [[Plugin Validate]], [[Testing Kit]], [[Testing Playbook]]. API lookups for changed names: [[Mods API Cheatsheet]]. Release cadence: [[Claude Code Release Channels]]. Vault upkeep: [[Research Refresh Workflow]] and [[Claim Verification Flow]]. Republishing: [[Publish a Mod Flow]].

## Sources

- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- types-2-1-288: local `.raw/captures/types-2.1.288/claude-code/index.d.ts` (header L1-10)
- code-modernization-1-0-0: local `.raw/captures/official-mods/code-modernization-1.0.0/` (tsconfig.json, tests/mount.test.ts)
- A local `claude plugin validate --json` run on Claude Code 2.1.288 (retrieved 2026-10-03; output not redistributed)
