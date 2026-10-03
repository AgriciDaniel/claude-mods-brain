---
type: "concept"
title: "Versioning and API Drift"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/concept"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "lifecycle"
related:
  - "[[Version Pin Policy]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Plugin Validate]]"
  - "[[Testing Kit]]"
  - "[[Mods API Namespaces]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Claude Code Release Channels]]"
  - "[[code-modernization Plugin]]"
  - "[[Marketplaces and Distribution]]"
  - "[[Mods API gaps requested in the 91870 thread but not shipped]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/loading (retrieved 2026-10-03)"
sources:
  - "types-2-1-288"
  - "docs-mods-create"
  - "docs-mods-reference"
  - "docs-plugins-loading"
  - "docs-plugins-manifest-reference"
  - "code-modernization-1-0-0"
  - "lif-plugin-authoring-skill"
---

# Versioning and API Drift

The mods API is early access and moves between Claude Code releases, so the only authority for a given build is the declaration file that build writes beside the mod, not the docs and not the GitHub copy (C-LIF-043). Drift shows up on two axes: the engine's API under a mod changes per release, and the mod's own copies on users' machines are cached by computed version (C-LIF-044). Manage both by regenerating and diffing typings per release and by bumping the mod's version on every change.

## Where the truth lives, ranked

| Rank | Source | Freshness |
|---|---|---|
| 1 | `<mod>/.claude-plugin/types/claude-code/index.d.ts`, written at each load | exactly the installed build (C-LIF-042) |
| 2 | the `plugin-authoring` skill's `types/claude-code.d.ts` | written per process when the skill loads (C-LIF-060) |
| 3 | code.claude.com mods pages | written "as of v2.1.287" (docs-mods-reference) |
| 4 | `mods/types/claude-code.d.ts` on GitHub | can be older than the installed build (docs-mods-reference) |

The file's first line names the writer, for example `// Written by Claude Code 2.1.288.`, and its header says Paraphrase: early access, may change between releases without notice; regenerate after an update rather than edit (types 2.1.288 L1-10). The docs say the same: trust these files over any page when they disagree (docs-mods-create).

## Drift already visible on 2.1.288

- Anthropic's code-modernization 1.0.0 `tsconfig.json` includes `.claude/types`, while 2.1.288 lays types in `.claude-plugin/types` (C-LIF-059).
- Its `tests/mount.test.ts` reaches `$.ui.mount` through a cast: "`$.ui.mount` is newer than the declarations `tsc` reads" (code-modernization-1-0-0).
- Its `register.test.ts` keeps a case labeled "As 2.1.273 draws it", testing an older viewport shape on purpose.
- `claude plugin test` did not exist on 2.1.270 per a #91870 report, and userConfig-in-tests appeared after 2.1.282 (C-LIF-029). Features arrive release by release.

## Manifest features with their own floors

| Feature | Minimum | Effect on older builds |
|---|---|---|
| Mods at all | 2.1.287 (C-LIF-001) | module not loaded |
| `userConfig` `options` picker | 2.1.271 (C-LIF-038) | plugin cannot load |
| `/config` rows for options | 2.1.269 (docs-plugins-manifest-reference) | no rows |
| directory listing fields accepted by validate | 2.1.281 | `--strict` fails on `Unknown field` |
| marketplace `renames` | 2.1.193 (C-LIF-052) | not migrated |

## How to diff typings between builds

The engine rewrites the types on every load, so keep a committed snapshot and diff after an update:

```bash
# once per release, from the mod folder, after a session has loaded it
head -1 .claude-plugin/types/claude-code/index.d.ts        # names the build
cp .claude-plugin/types/claude-code/index.d.ts \
   contracts/claude-code-$(claude --version | cut -d' ' -f1).d.ts
diff -u contracts/claude-code-2.1.288.d.ts \
        contracts/claude-code-2.1.289.d.ts | grep '^[-+] ' | less
tsc -p .                                                   # does the mod still type-check
```

Focus the diff on what the mod uses: grep for each line of the `validate` inventory (`hooks:` events and `calls:` methods) in the removed (`-`) lines. The `.claude-plugin/types/` folder ships a `.gitignore`, so the engine expects you not to commit it in place; copy it to your own path instead (observed in a personal mod reviewed for this vault).

## What the drift check sees, and what it does not

`scripts/diff_api_surface.py` compares two typings captures on four levels: names (engine, op, and classic events, `$` members, render components, elements by surface, exported types), declaration signatures of every event and `$` member, every limit-bearing line (unit-bearing numbers in the doc comments and numeric constants such as `ms: 10_000`, 27 such lines in 2.1.288), and the file hash. A changed budget or a new optional parameter is therefore drift, and `--wiki wiki` maps it to the notes that mention the member or the number (for a limit, in any of its written forms: `10_000`, `10000`, `10,000`). If the hash changed but none of those did, the report sets `manual_review_required`: the change sits in prose or inside a nested payload type the importer does not index, so diff the two `index.d.ts` files by hand. The baseline is [[API Drift 2.1.288 to 2.1.288]] (zero changes). EVIDENCE-BASED

## Cache by version on the user side

An installed plugin is copied to `cache/<marketplace>/<plugin>/<version>/` and loaded from there (docs-plugins-loading). The computed version is the manifest `version`, else the entry `version`, else the source SHA or digest (C-LIF-044). Consequences:

- A pinned version that is not bumped never reaches users, however many commits land. EVIDENCE-BASED
- A running session keeps the version it loaded until `/reload-plugins` or a relaunch (C-LIF-046). EVIDENCE-BASED
- Previous version folders get an `.orphaned_at` marker and are removed 14 days later (docs-plugins-loading). EVIDENCE-BASED
- An in-place local-directory plugin ignores `version` entirely (C-LIF-051). EVIDENCE-BASED

## Recommendations

- Treat the typings file as a contract: snapshot it per release and diff it before you touch code. PRACTITIONER
- Type-check with `tsc -p` and run `claude plugin validate --strict` and `claude plugin test` after every Claude Code update. EVIDENCE-BASED
- Never edit the generated types; regenerate by loading the mod. EVIDENCE-BASED
- Record tested-on build and feature floors in the README. EVIDENCE-BASED
- Avoid casts like `as any` on kit inputs except where the typings lag, and leave a comment naming the build. PRACTITIONER

## Caveats

- Line numbers cited as `types 2.1.288 L..` shift with every build; re-anchor on refresh.
- Feature floors come from docs pages that may not list every gate; mixed-version `hooks.json` behavior is unresolved (X-LIF-06).
- This lane did not hold two builds side by side, so the diff recipe is untested here.

## Related

The policy built on this is [[Version Pin Policy]], executed by [[Re-verify After Release Flow]]. Static and runtime checks are [[Plugin Validate]] and [[Testing Kit]]. The surfaces that drift are listed in [[Mods API Namespaces]] and [[Mods API Cheatsheet]]. Build channels are in [[Claude Code Release Channels]], official drift evidence in [[code-modernization Plugin]], cache mechanics in [[Marketplaces and Distribution]], and pending API changes in [[Mods API gaps requested in the 91870 thread but not shipped]].

## Sources

- types-2-1-288: local .raw/captures/types-2.1.288/claude-code/index.d.ts (retrieved 2026-10-03)
- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-plugins-loading: https://code.claude.com/docs/en/plugins/loading (retrieved 2026-10-03)
- docs-plugins-manifest-reference: https://code.claude.com/docs/en/plugins/manifest-reference (retrieved 2026-10-03)
- code-modernization-1-0-0: local .raw/captures/official-mods/code-modernization-1.0.0/ (retrieved 2026-10-03)
- lif-plugin-authoring-skill: local captures/plugin-authoring-skill-2-1-288.md (retrieved 2026-10-03)
