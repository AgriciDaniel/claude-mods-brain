---
type: "source"
title: "Source Manifest Guide"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/source"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "rewrite"
related:
  - "[[Source Intake Workflow]]"
  - "[[Claim Verification Flow]]"
  - "[[Research Refresh Workflow]]"
  - "[[Provenance Trace Policy]]"
  - "[[Corpus Scope Policy]]"
  - "[[research-pack-claude-mods|Research Pack]]"
  - "[[Claude Code plugins and hooks documentation (Anthropic)]]"
  - "[[Mods design thread, anthropics claude-code issue 91870]]"
  - "[[code-modernization Plugin]]"
  - "[[Mod Catalog]]"
  - "[[Evidence Coverage Not Yet Verified]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-plugins-official/tree/d182ca456ca09d31d139f7d3818d1d333b103cce/plugins/code-modernization (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)"
  - "https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)"
sources:
  - "docs-mods-overview"
  - "docs-mods-reference"
  - "code-modernization-1-0-0"
  - "gh-issue-91870"
  - "eco-npm-dist-tags"
  - "types-2-1-288"
---

# Source Manifest Guide

Four records hold this brain's provenance, each answering one question. A capture manifest says which bytes were captured and proves they have not changed (sha256 per file). An upstream manifest says which upstream commit or build those bytes came from. `references/source-ledger.json` says what each source is, how far to trust it, and when to re-check it. `references/claim-ledger.md` says which statements rest on which sources. The two ledgers ship in this repo and cite every source by its public URL; the two manifests describe raw captures, and the public repo ships no `.raw/` captures, so you build those for your own `.raw/`. A claim is traceable when you can walk from its row to a ledger id, from the id to a URL or capture path, and from the path to a matching hash.

## The four records

| Record | Answers | Size on 2026-10-03 | Ships publicly | Checked by |
|---|---|---|---|---|
| Capture manifest (`.raw/.manifest.json`) | Which bytes, unchanged? | 104 files in the maintainer's capture set | no, build your own | a hash check over your `.raw/` |
| Upstream manifest (`.raw/upstream-manifest.json`) | Which commit or build? | 3 pins: code-modernization at `d182ca4`, types 2.1.288, #91870 with 235 comments | no; the pins are repeated in the ledger and notes | `verified` field, re-hash on refresh |
| `references/source-ledger.json` | What is it, how trusted, when stale? | 50 `sources` plus `local_captures` | yes | `scripts/check_source_ids.py` |
| `references/claim-ledger.md` | Which statement, on what evidence? | 301 rows | yes | [[Claim Verification Flow]] |

## Capturing your own sources

Nothing in `.raw/` is published, so a reader who wants to re-verify a claim captures the evidence locally:

- **Docs pages** as `<page>.md`, fetched with `curl` from the docs site's markdown endpoint, into a dated folder:

```bash
D=.raw/captures/docs-$(date +%F); mkdir -p "$D"
for p in overview create reference interface gallery events api test troubleshoot admin; do
  curl -fsSL "https://code.claude.com/docs/en/plugins/mods/$p.md" -o "$D/plugins-mods-$p.md"
done
```

- **Typings** by loading a scratch mod once with `claude --plugin-dir`, which makes Claude Code write `.claude-plugin/types/claude-code/index.d.ts` for your build; copy that folder to `.raw/captures/types-<version>/` ([[Research Refresh Workflow]]). Use a display-only fixture such as `tests/fixtures/mods/clean-band`, never a third-party mod.
- **Threads and repos** through the GitHub API, pinned to a commit ([[Source Intake Workflow]]).

Then hash what you captured, so a later diff can prove the bytes did not move:

```bash
find .raw -type f ! -name SHA256SUMS -exec sha256sum {} + > .raw/SHA256SUMS
sha256sum -c .raw/SHA256SUMS
```

## The capture manifest

In the maintainer's copy, each entry has `path` (repo-relative, starting `.raw/`), `sha256`, `bytes`, `kind`, `retrieved`. `kind` comes from the path prefix (`captures/types-` is `generated-typings`, `captures/docs-` is `official-docs-markdown`, and so on). Captures are immutable: a changed hash on an existing file is an error, and a missing file, a duplicate path, or an absolute or `..` path fails the check. Keep the same rules for your own `.raw/`: save a re-fetch under a new dated folder rather than overwriting.

## The upstream manifest

Schema `mods-brain.upstream-manifest.v1`. Each pin has `id` (matching a ledger id), `repo`, `path` or `issue`, `sha` or `writer`, `commit_date`, `capture`, `verified`, and `cite_as`. Examples: code-modernization pinned at `d182ca456ca09d31d139f7d3818d1d333b103cce` (2026-10-02), with `hooks/register.ts` verified byte-identical upstream and cited as `repo:claude-plugins-official@d182ca4 path:plugins/code-modernization/<file>`; the typings cited as `types 2.1.288 L<start>-<end>`.

Community repo pins (cctop, Arunjay4213, karanb192 and others) live as `pinned_sha` on their ledger entries instead: 15 ledger sources carry one.

## references/source-ledger.json

Top level: `version`, `status`, `domain`, `refresh_cadence` ("researched on every Claude Code release ... monthly sweep of official mods docs, the #91870 design thread, and community directories"), `rules` (two captured sources for fast-moving claims; accepted primary types), `sources`, `local_captures`.

- `sources` (50): evidence with an honest public URL. 25 official, 11 practitioner, 7 primary, 6 market, 1 supporting. Fields: `id`, `title`, `url`, `publisher`, `source_type`, `published`, `retrieved`, `refresh_due`, `confidence`, `claims`, `lanes`, `notes`, plus `pinned_sha` for repos and `capture` and `capture_note` for local copies such as `types-2-1-288`.
- `local_captures`: evidence with no public URL, kept out of `sources` so no fake link is ever cited, for example `compass-report` (the seed, lead list only), `eco-static-scan`, `lif-plugin-authoring-skill`, and `secgov-validate-probes`.

```bash
jq -r '.sources[] | select(.refresh_due <= "2026-11-02") | .id' references/source-ledger.json | wc -l
jq -r '.sources[] | select(.claims | length == 0) | .id' references/source-ledger.json   # should print nothing
python3 scripts/check_source_ids.py                                                    # every cited id is in the ledger
```

## references/claim-ledger.md

One table row per load-bearing claim: `| ID | Claim | Confidence | Source | Second source | Verdict | Tested on |`, ids `C-API`, `C-LIF`, `C-SEC`, `C-ECO`, `C-PAT`. On 2026-10-03: 225 verified, 55 SINGLE-SOURCE, 14 contradicted, 6 unverified.

```bash
grep -c "^| C-" references/claim-ledger.md
grep "^| C-" references/claim-ledger.md | awk -F'|' '{print $7}' | sed 's/(.*//' | sort | uniq -c
```

## Tracing one claim end to end

C-ECO-051 says npm dist-tags were stable 2.1.285, latest and next 2.1.288 on 2026-10-03.

```bash
grep "^| C-ECO-051 " references/claim-ledger.md                       # source: eco-npm-dist-tags
jq '.sources[] | select(.id=="eco-npm-dist-tags") | {url, retrieved, refresh_due, notes}' references/source-ledger.json
npm view @anthropic-ai/claude-code dist-tags --json                    # re-check against the live source
```

Claim row, ledger entry (primary, refresh due 2026-11-02), public URL: the chain holds in the published repo. In the maintainer's copy it continues to a capture path and a matching hash; in yours, it continues to whatever you captured. A broken link at any step makes the claim unverified until fixed.

## Related records

- `references/canon/` holds 6 canon summaries (docs set, launch post, getting-started post, #91870, Pluto, plugins and hooks docs), each with `source_capture` and `retrieved`; they surface in the wiki as notes such as [[Claude Code plugins and hooks documentation (Anthropic)]] and [[Mods design thread, anthropics claude-code issue 91870]].
- `references/data/` holds derived JSON (api-surface, scans, synthesis, drift); it is regenerable and not hashed.
- `scripts/render_research_pack.py` renders the [[research-pack-claude-mods|Research Pack]] from the ledgers, the dated citation index of every source.

## Recommendations

- Hash your captures after every fetch and before every re-verification. EVIDENCE-BASED
- Put anything without a public page in `local_captures`, never in `sources` with a placeholder URL. EVIDENCE-BASED
- Pin repos by full SHA; cite the short SHA in notes. PRACTITIONER

## Caveats

- The upstream manifest has only 3 pins; community repo pins live in the ledger, so a full pin audit reads both.
- Your own captures will differ from the maintainer's if a page changed since 2026-10-03; that difference is a refresh signal, not an error.

## Related

Adding a source: [[Source Intake Workflow]]. Re-dating sources: [[Research Refresh Workflow]]. Rules: [[Provenance Trace Policy]] and [[Corpus Scope Policy]]. The assembled corpus: [[research-pack-claude-mods|Research Pack]]. Repo pins in use: [[Mod Catalog]] and [[code-modernization Plugin]]. Known holes: [[Evidence Coverage Not Yet Verified]].

## Sources

- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- code-modernization-1-0-0: https://github.com/anthropics/claude-plugins-official/tree/d182ca456ca09d31d139f7d3818d1d333b103cce/plugins/code-modernization (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
- eco-npm-dist-tags: https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`, cited against https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
