---
type: "flow"
title: "Source Intake Workflow"
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
  - "[[Source Manifest Guide]]"
  - "[[Claim Verification Flow]]"
  - "[[Research Refresh Workflow]]"
  - "[[Provenance Trace Policy]]"
  - "[[Corpus Scope Policy]]"
  - "[[Uncertainty Eval Policy]]"
  - "[[research-pack-claude-mods|Research Pack]]"
  - "[[Mod Catalog]]"
  - "[[Mods design thread, anthropics claude-code issue 91870]]"
  - "[[Claude Code plugins and hooks documentation (Anthropic)]]"
  - "[[Read Only Audit Decision]]"
source_urls:
  - "https://code.claude.com/docs/llms.txt (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)"
  - "https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)"
sources:
  - "docs-mods-overview"
  - "docs-mods-create"
  - "gh-issue-91870"
  - "eco-npm-dist-tags"
  - "types-2-1-288"
  - "code-modernization-1-0-0"
---

# Source Intake Workflow

Every fact in this brain enters through one door: an immutable capture under `.raw/`, a hash row in `.raw/.manifest.json`, a ledger entry in `references/source-ledger.json`, and claim rows in `references/claim-ledger.md`. Official docs are captured as the `<page>.md` markdown the docs site serves, GitHub material through read-only `gh api` calls with a pinned commit SHA, and the generated typings by copying what Claude Code wrote beside an owned mod. Nothing is ever edited in place: a changed source becomes a new dated capture.

## Trigger

- A new mods source appears: a docs page, a #91870 comment worth citing, a community repo for [[Mod Catalog]], an Anthropic post, or independent research such as the Pluto write-up.
- A lane or rewrite pass needs a fact the 50 ledger sources lack, or [[Research Refresh Workflow]] finds a changed page or typings file.

## Prerequisites

- `curl`, `gh` (read-only), `npm`, `python3`, `jq`, run from the repo root. `.raw/` is append-only: only the person maintaining the vault adds captures there. Lane passes save their own captures under `.research-candidates/<lane>/captures/`, and `merge_candidates.py` rewrites those paths to `.raw/captures/lanes-2026-10-03/<lane>/`.
- The canonical id table in `references/orchestration/LANE_BRIEF.md`. Reuse an id when one exists; new ids take a lane prefix (`eco-`, `lif-`, `secgov-`, `pa-`).

## Steps

1. Pick the capture folder by kind and date. `scripts/build_raw_manifest.py` assigns the `kind` from the path prefix, so the folder name matters:

| Folder | Kind recorded |
|---|---|
| `.raw/captures/types-<version>/` | `generated-typings` |
| `.raw/captures/official-mods/<name>-<version>/` | `official-mod-source` |
| `.raw/captures/docs-<date>/` | `official-docs-markdown` |
| `.raw/captures/web-<date>/` | `web-capture` |
| `.raw/captures/<other>/` | `capture` |
| `.raw/sources/` | `seed-research` |

2. Capture official docs pages as markdown. The docs site serves each page with a `.md` suffix, and the capture keeps the index banner that proves where it came from (the existing captures open with the `llms.txt` pointer).

```bash
D=.raw/captures/docs-$(date +%F); mkdir -p "$D"
for p in overview create reference interface gallery events api test troubleshoot admin; do
  curl -fsSL "https://code.claude.com/docs/en/plugins/mods/$p.md" -o "$D/plugins-mods-$p.md"
done
curl -fsSL https://code.claude.com/docs/llms.txt | grep -i "plugins/mods"   # find new pages
```

3. Capture GitHub issues and threads through the API, never by scraping HTML. The #91870 capture holds the body plus all 235 comments with author, date and comment URL.

```bash
gh api repos/anthropics/claude-code/issues/91870 --jq '.title,.created_at,.user.login'
gh api --paginate repos/anthropics/claude-code/issues/91870/comments \
  --jq '.[] | "### \(.user.login) \(.created_at)\n\(.html_url)\n\n\(.body)\n"' > .raw/captures/web-$(date +%F)/gh-issue-91870.md
```

4. Pin every repository to a commit before reading it, and read through the API so nothing is cloned or executed.

```bash
gh api repos/tomstagl/cctop/commits/HEAD --jq '.sha,.commit.committer.date'
gh api repos/tomstagl/cctop/readme --jq .content | base64 -d > captures/eco-gh-cctop-readme.md   # lane folder
gh api "repos/anthropics/claude-plugins-official/contents/plugins/code-modernization/hooks/register.ts?ref=<sha>" \
  --jq .content | base64 -d | sha256sum
```

Record the pin in `.raw/upstream-manifest.json` (`id`, `repo`, `path`, `sha`, `commit_date`, `capture`, `verified`, `cite_as`), as done for `code-modernization-1-0-0` at `d182ca4`.

5. Capture the typings from an owned mod only. Claude Code writes `.claude-plugin/types/` on each `--plugin-dir` load of a folder you own (docs-mods-create, C-LIF-042). Copy, then check the writer line:

```bash
cp -r <owned-mod>/.claude-plugin/types/. .raw/captures/types-2.1.288/
head -1 .raw/captures/types-2.1.288/claude-code/index.d.ts   # // Written by Claude Code 2.1.288.
```

Loading a third-party mod to obtain typings is out of bounds ([[Read Only Audit Decision]]).

6. Capture registry facts as text with the command in the header, as `eco-npm-claude-code-dist-tags.md` does:

```bash
npm view @anthropic-ai/claude-code dist-tags --json
npm view @anthropic-ai/claude-code time --json
```

7. Put a header on every non-docs capture (URL, retrieved date, title); strip home paths, emails and tokens.

8. Hash the new files. Existing rows keep their kind and date; a changed hash on an existing path exits 1 with `immutable capture changed: <path>`.

```bash
python3 scripts/build_raw_manifest.py      # prints "<n> captures hashed" (104 on 2026-10-03)
```

9. Add the ledger entry to `references/source-ledger.json` under `sources` (public URL) or `local_captures` (no public URL: CLI runs, private repos, the seed report):

```json
{"id": "eco-gh-cctop", "title": "tomstagl/cctop", "url": "https://github.com/tomstagl/cctop",
 "publisher": "tomstagl", "source_type": "practitioner", "published": "2026-10-01",
 "retrieved": "2026-10-03", "refresh_due": "2026-11-02", "confidence": "medium",
 "claims": ["C-ECO-027", "C-ECO-028", "C-ECO-029", "C-ECO-030"], "lanes": ["ecosystem"],
 "pinned_sha": "6ceafc34a972f4e58d5e53b1c69f80e2a9759d41", "notes": "MIT, release v0.9.1 2026-09-29."}
```

`source_type` is one of official, primary, api-docs, vendor, practitioner, supporting, market.

10. Write claim rows in `references/claim-ledger.md`, one load-bearing statement each, then verify them through [[Claim Verification Flow]]:

```
| C-ECO-051 | On 2026-10-03 npm dist-tags are stable 2.1.285, latest 2.1.288, next 2.1.288. | evidence-based | eco-npm-dist-tags | none | verified | n/a |
```

## Outputs

- A dated capture under `.raw/captures/`, a new row in `.raw/.manifest.json`, and a pin in `.raw/upstream-manifest.json` for repos.
- A ledger entry with `retrieved` and `refresh_due` (2026-11-02 for this cycle) and the claim ids it supports.
- Claim rows with a source, a second source or `none`, a verdict, and a tested-on version.

## Gates

- `python3 scripts/build_raw_manifest.py` exits 0. EVIDENCE-BASED
- `python3 scripts/check_no_em_dash.py` reports 0 findings (it also catches tokens and home paths in shipped files). EVIDENCE-BASED
- `bash references/orchestration/run_gates.sh` stays green on `vault-lint-root`, which calls `check_raw_manifest`. EVIDENCE-BASED

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `immutable capture changed` | A capture was edited or re-fetched into the same path | Restore the old file; save the new fetch under a new dated folder |
| `curl: (22)` on a docs page | Page renamed or removed | Check `llms.txt`; record the gap in [[Evidence Coverage Not Yet Verified]] |
| Seed report is the only support | Claim taken from `.raw/sources/compass-report-2026-10-02.md` | Find a rank 1 to 6 source or mark SINGLE-SOURCE |

## Rollback

Captures are append-only, so rollback is removal before merge: delete the new capture folder, re-run `build_raw_manifest.py` (removed paths drop out), and remove the ledger entry and claim rows. After merge, use git on the repo: `git checkout -- references/source-ledger.json references/claim-ledger.md`.

## Caveats

- The `.md` docs endpoint is how the 2026-10-03 captures were made; if the site stops serving it, capture the rendered page and say so in the header.

## Related

Where each record lives is mapped in [[Source Manifest Guide]]. Provenance rules come from [[Provenance Trace Policy]] and scope from [[Corpus Scope Policy]]; confidence labels follow [[Uncertainty Eval Policy]]. The assembled corpus is the [[research-pack-claude-mods|Research Pack]]. Canon summaries include [[Claude Code plugins and hooks documentation (Anthropic)]] and [[Mods design thread, anthropics claude-code issue 91870]]. Repo pins feed [[Mod Catalog]]; refresh timing is in [[Research Refresh Workflow]].

## Sources

- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (retrieved 2026-10-03)
- eco-npm-dist-tags: https://www.npmjs.com/package/@anthropic-ai/claude-code (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- code-modernization-1-0-0: https://github.com/anthropics/claude-plugins-official/tree/d182ca456ca09d31d139f7d3818d1d333b103cce/plugins/code-modernization (retrieved 2026-10-03)
