---
type: "concept"
title: "Reach Levels"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/concept"
  - "#confidence/practitioner"
confidence: "practitioner"
lane: "security-governance"
related:
  - "[[Mods Trust Model]]"
  - "[[Mod Catalog]]"
  - "[[karanb192 claude-code-mods]]"
  - "[[Mod Directories]]"
  - "[[Plugin Validate]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Usage Cost Surface]]"
  - "[[Mods API Namespaces]]"
  - "[[Tool Events]]"
source_urls:
  - "https://github.com/karanb192/awesome-claude-code-mods (pinned 59a9911a836326338a831b6c8e37a7a855e405f4, retrieved 2026-10-03)"
  - "https://github.com/karanb192/awesome-claude-code-mods/blob/59a9911a836326338a831b6c8e37a7a855e405f4/tools/grade.mjs (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
sources:
  - "secgov-karanb192-awesome-readme"
  - "secgov-karanb192-grade-mjs"
  - "docs-mods-admin"
  - "docs-mods-reference"
  - "secgov-validate-probes"
  - "compass-report"
---

# Reach Levels

Reach levels L0 to L3 are a practitioner taxonomy from karanb192's community scanner, not an Anthropic classification. The scanner runs `claude plugin validate` on each mod, then grades the `$` calls it lists: L0 draws and remembers, L1 reads, L2 writes files, runs processes, or drives Claude, L3 reaches the network (secgov-karanb192-awesome-readme; secgov-karanb192-grade-mjs) (C-SEC-049). It is a fast, reproducible footprint, and the scanner's own README says it is "a footprint, not a verdict". It misses power that lives in hooks rather than calls, so this brain pairs it with two extra flags.

## The levels as the scanner computes them

Source: `tools/grade.mjs` at commit 59a9911 (2026-10-02). The level is the maximum over all calls; a call that matches no rule is labeled `other` and raises the level to at least L1.

| Level | Name in the scanner | Calls that set it |
|---|---|---|
| L3 | network | `$.http.fetch`, `$.mcp.call` |
| L2 | writes or runs | `$.process.run`, `$.fs.write`, `$.env.set`, `$.config.set`, and "drives Claude": `$.model.*`, `$.agent.spawn`, `$.prompt.submit`, `$.tool.call`, `$.command.run`, `$.turn.abort`, `$.session.compact`, `$.tool.register` |
| L1 | reads | `$.fs.read/list/stat/exists/ancestors`, `$.env.get`, `$.settings.read`, `$.session.messages`, `$.session.authorize`, `$.telemetry.*`, `$.prompt.fill/suggest`, and any unmatched call |
| L0 | draws and remembers | `$.ui.*`, `$.store.*`, `$.audio.*`, `$.agent.list`, and the rest of `$.clock`, `$.command`, `$.plugin`, `$.session`, `$.config` |

The scanner also prints a "Sees" list from hooks (for example `tool.call` without a matcher becomes "every tool call", `prompt.submit` becomes "every prompt", `*` becomes "everything") and a "Review UI rewrite" warning when a `ui.render` mod's source holds control-character strings (secgov-karanb192-awesome-readme, "How the scan works").

Snapshot on 2026-10-02 against 2.1.287: 359 mods, of which L0 55, L1 39, L2 186, L3 79; 79 see every tool call and 111 see every prompt (secgov-karanb192-awesome-readme) (C-SEC-051).

## Where the levels under-report

The grader reads only the `calls:` line, and its rules are a regex table. Read against the admin page's risk table (docs-mods-admin, "Review what a mod can do"):

| Gap | Effect | Evidence |
|---|---|---|
| `$.process.spawn` has no rule | Graded L1 `other`, though the admin page groups it with `run` as "Starts programs as the user" | grade.mjs rules; docs-mods-admin (C-SEC-050) |
| `$.session.send` and `$.session.append` match the L0 `session` rule | A mod that messages other sessions or writes transcript rows grades L0 | grade.mjs; docs-mods-admin lists `$.session.send` as a call to look for |
| `$.mcp.connect`, `$.tool.check`, `$.agent.register` unmatched | Graded L1 `other` | grade.mjs; method list in docs-mods-reference |
| Hook-only authority | `tool.check` approvals, `tool.call` rewrites, `ui.render{component=AskUserQuestion}`, `session.append`, `prompt.*` rewrites make no `$` call, so a mod using only these grades L0 | secgov-validate-probes, Probe 1 (C-SEC-011) |
| Settings hooks, `bin/`, `.mcp.json` in the same plugin | Not graded at all; validate does not print them | secgov-validate-probes, Probe 4 (C-SEC-010) |
| Runtime-fetched code | L3 says "network", not what is fetched or run | pluto-function-hooks, Risk 4 |

So L0 is not "safe". A pure-render mod on `AskUserQuestion` grades L0 and can still reword the question a user is approving (docs-mods-interface).

## This brain's extension: Reach plus two flags

Use the scanner level as the first field, then add two flags computed from the `hooks:` line. This is a local convention for [[Mod Catalog]] rows, not a scanner feature.

| Field | Values | Set it when |
|---|---|---|
| Reach | L0 to L3 | Scanner rule table above, but grade `$.process.spawn` as L2 and `$.session.send` as L2 (drives another Claude) |
| Authority | none, rewrites, approves, governs | `rewrites`: any `next({...e})` on `tool.call`, `prompt.*`, `session.append`, `turn.step`, or a `ui.render` on a transcript or dialog site. `approves`: `tool.check` returning `allow`. `governs`: `plugin.register` or `engine.create`, or hooks on another mod's calls such as `fs.write` |
| Cost | none, model calls, turns | `$.model.*` sets model calls; `$.prompt.submit`, `$.agent.spawn`, timers that start turns set turns. See [[Usage Cost Surface]] |

Example rows (illustrative shapes, not specific repos):

| Mod shape | Scanner level | This brain |
|---|---|---|
| Context meter in the band using `$.session.usage` | L0 | L0, none, none |
| PR tracker that runs `gh` every 60 s | L2 | L2, none, none |
| Secret redactor that rewrites tool results | L0 or L1 | L1, rewrites, none |
| Auto-approver for test commands | L0 | L0, approves, none |
| Org policy mod with `plugin.register` and `fs.write` hooks | L0 to L3 | its level, governs, none |

## How to compute it yourself

```bash
claude plugin validate --json ./some-mod > validate.json
jq -r '.contents[].notes[]' validate.json | grep -E 'hooks:|calls:|env (reads|writes):'
```

Then apply the table by hand, or run the scanner's `grade()` on the `calls` list. Always record the Claude Code version you validated on; the scanner's table says "Validates on" per row for this reason.

## Recommendations

- Use the reach level to sort review effort, never to skip review. PRACTITIONER
- Treat L0 mods with rewrite or approve authority as at least as risky as an L2 mod. EVIDENCE-BASED
- Re-grade `$.process.spawn` and `$.session.send` upward until the scanner adds rules for them. PRACTITIONER
- Record level, authority, cost, and the Claude Code version together in every catalog row. PRACTITIONER

> [!contradiction]
> The seed report says the scanner's last snapshot was 2026-09-15 against 2.1.272 and is stale (compass-report, section 4). The README at commit 59a9911 shows a 2026-10-02 scan against 2.1.287 (secgov-karanb192-awesome-readme). The README wins; the seed was outdated within days.

## Caveats

- The taxonomy, rule table, and counts belong to a community project pinned at 59a9911; they can change any night the scanner runs.
- Levels are computed from static validate output on the version the scanner used (2.1.287), which may differ from 2.1.288 for some mods.
- The gaps table was found by reading `grade.mjs`, not by running the scanner.

## Related

The level is one input to [[Mods Trust Model]] and to the [[Mod Security Audit Checklist]]. Catalog rows in [[Mod Catalog]] carry it, and the scanner's author is covered under [[karanb192 claude-code-mods]] and [[Mod Directories]]. The calls being graded are listed in [[Mods API Namespaces]] and read by [[Plugin Validate]]; the hook-side authority comes from [[Tool Events]] and [[Render Sites]]. Cost flags tie to [[Usage Cost Surface]].

## Sources

- secgov-karanb192-awesome-readme: https://github.com/karanb192/awesome-claude-code-mods (pinned 59a9911a836326338a831b6c8e37a7a855e405f4; capture `.raw/captures/lanes-2026-10-03/security-governance/secgov-karanb192-awesome-readme.md`, retrieved 2026-10-03)
- secgov-karanb192-grade-mjs: https://github.com/karanb192/awesome-claude-code-mods/blob/59a9911a836326338a831b6c8e37a7a855e405f4/tools/grade.mjs (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-interface: https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md`
- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md`
