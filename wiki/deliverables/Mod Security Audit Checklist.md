---
type: "deliverable"
title: "Mod Security Audit Checklist"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/deliverable"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "security-governance"
related:
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Read Only Audit Decision]]"
  - "[[Mods Trust Model]]"
  - "[[Reach Levels]]"
  - "[[Usage Cost Surface]]"
  - "[[Prompt Injection via Mods]]"
  - "[[Plugin Validate]]"
  - "[[Mod Catalog]]"
  - "[[Pitfalls Playbook]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)"
  - "https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)"
sources:
  - "docs-mods-admin"
  - "docs-mods-overview"
  - "docs-mods-events"
  - "docs-mods-reference"
  - "docs-mods-interface"
  - "docs-plugins-security"
  - "types-2-1-288"
  - "secgov-validate-probes"
  - "pluto-function-hooks"
  - "compass-report"
---

# Mod Security Audit Checklist

Run this before any third-party mod is installed, in order. Nothing in it loads or runs the mod: it pins the code, inventories every component, reads the static scan, sweeps the source with the greps below, and ends in an adopt, trial, or avoid verdict for [[Mod Catalog]]. Each step names its pass condition. A failed step marked BLOCK ends the audit as avoid unless the owner signs an exception. Rationale for staying static is in [[Read Only Audit Decision]].

## 0. Set up (read-only)

- [ ] **0.1** Work in a scratch directory outside any repo you care about. Do not run `/plugin install`, `claude plugin install`, `claude --plugin-dir`, or `claude plugin test` on the target.
- [ ] **0.2** Set `MOD=./some-mod` (the directory holding `.claude-plugin/plugin.json`) and record `claude --version`; every result below is version-specific (types 2.1.288 L4).

## 1. Provenance and pin

- [ ] **1.1** Clone and pin a commit; record `git -C "$MOD" rev-parse HEAD` and `git -C "$MOD" log -1 --format=%cI`. BLOCK if the install path is a moving branch you will not pin.
- [ ] **1.2** Name the marketplace and its tier. Official and community names are accepted only from `github.com/anthropics/`; everything else is third-party (docs-plugins-security).
- [ ] **1.3** Check update exposure: is auto-update on for that marketplace? Note that reviewed files can change on disk after an update (docs-plugins-security) (C-SEC-047).
- [ ] **1.4** Read the README's install steps. BLOCK if it asks Claude or you to edit shell rc files, set `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` (ignored since 2.1.287), or pipe a URL into a shell (compass-report, section 4; docs-mods-overview).

## 2. Inventory every component, not just the mod

`claude plugin validate` reports only the hooks module; a settings hook and `bin/` beside it went unreported on 2.1.288 (secgov-validate-probes, Probe 4) (C-SEC-010).

```bash
cat "$MOD/.claude-plugin/plugin.json"           # name, dependencies, userConfig, types
jq '.hooks, .modules' "$MOD/hooks/hooks.json"   # settings hooks AND the module path
ls "$MOD/bin" "$MOD/.mcp.json" "$MOD/.lsp.json" 2>/dev/null
find "$MOD" -type f -perm -u+x -not -path '*/.git/*'
ls "$MOD/skills" "$MOD/commands" "$MOD/agents" 2>/dev/null
```

- [ ] **2.1** Every `hooks` entry in `hooks.json` is a shell command: read each script it runs. BLOCK on unpinned download-and-run.
- [ ] **2.2** Every `.mcp.json` server's command or URL is known, and every `bin/` file is read; `bin/` lands on Claude's Bash `PATH` (docs-plugins-security).
- [ ] **2.3** `dependencies` in the manifest: each dependency is another plugin to audit; a mod runs before the mods it depends on (docs-mods-events).

## 3. Static scan

```bash
claude plugin validate --strict --json "$MOD" > validate.json
jq -r '.contents[].notes[]?' validate.json
jq -r '.manifest.errors[]?, .contents[].errors[]?' validate.json
```

- [ ] **3.1** Validation passes on your version. A refusal means the mod will not load as written; record why (reserved name, computed `$` access, non-literal env name, dynamic `import()`) (secgov-validate-probes, Probes 2 and 3).
- [ ] **3.2** Copy the `hooks:`, `calls:`, `env reads:`, `env writes:` lines into the record, then compute the reach level and the authority and cost flags from [[Reach Levels]]. Grade `$.process.spawn` and `$.session.send` as L2.
- [ ] **3.3** Do not treat a passing scan or `calls: nothing on $` as clean: rewrites, approvals, and fabricated results make no `$` call (C-SEC-011).

## 4. Source sweeps (run all; read every hit in context)

List every file the module imports first; the typings say a hooks module loads the plugin's own files through import declarations and refuses `import()` (types 2.1.288 L19-24), so read all of them.

```bash
rg -n --type-add 'mod:*.{ts,tsx,js,jsx,mjs,cjs,mts,cts}' -t mod "^import " "$MOD"
```

**4.1 Host reach (admin risk table, docs-mods-admin).**

```bash
rg -n '\$\.(fs\.(read|write)|process\.(run|spawn)|http\.fetch|env\.(get|set)|settings\.read|mcp\.(call|connect))' "$MOD"
```

**4.2 Fetch-then-run.** BLOCK unless the fetched content is pinned by hash in code you read (pluto-function-hooks, Risk 4).

```bash
comm -12 <(rg -l '\$\.http\.fetch' "$MOD" | sort) <(rg -l '\$\.process\.(run|spawn)' "$MOD" | sort)
rg -n "\[\s*['\"](sh|bash|zsh|fish|node|deno|bun|python3?|perl|ruby|curl|wget|osascript|powershell|pwsh|cmd)['\"]" "$MOD"
```

**4.3 Secrets and sensitive paths.** BLOCK on any read of credential stores without a stated, necessary purpose.

```bash
rg -n -i "credentials|history\.jsonl|\.ssh|\.aws|\.config/gh|\.netrc|\.npmrc|\.docker/config|id_(rsa|ed25519)|keychain|\.env\b|\.claude/" "$MOD"
rg -n '\$\.env\.get\(.[A-Z0-9_]*(KEY|TOKEN|SECRET|PASS|AUTH)' "$MOD"
rg -n "session\.authorize|auth:|socketPath" "$MOD"
```

`$.session.authorize` is the safer pattern: the credential stays on the host and only first-party hosts accept the handle (types 2.1.288 L2697-2709) (C-SEC-016).

**4.4 Authority hooks.** Each hit needs a written reason.

```bash
rg -n "on\(\s*['\"](\*|tool\.check|plugin\.register|engine\.create|session\.append|session\.receive|session\.send|turn\.step|agent\.spawn|tool\.describe|skill\.prompt|prompt\.(submit|section|compose|context|attachment)|(fs|http|process|model)\.[a-z]+)['\"]" "$MOD"
rg -n "decision:\s*['\"]allow['\"]" "$MOD"
rg -n "asUser" "$MOD"
```

BLOCK on an unconditional `tool.check` allow, or `asUser: true` on text the user did not type.

**4.5 Trust-surface rendering.** BLOCK on a rewrite of `AskUserQuestion` question text, or an `Input` asking for a key, password, token, or "verification" (pluto-function-hooks, Risk 3; docs-mods-interface).

```bash
rg -n "component:\s*['\"](AskUserQuestion|ToolUse|ToolResult|ToolGroup|UserMessage|AssistantMessage|AbovePrompt|PromptHint|SessionMode)['\"]" "$MOD"
rg -n "Input\(|<Input|onSubmit|ui\.input" "$MOD"
rg -n -i "api key|password|passphrase|token|sign in|log in|verify|verification|expired|re-?enter" "$MOD"
rg -n "module:\s*['\"]" "$MOD"     # Client surface modules: read each one
```

**4.6 Rewrites and answers.** Read each: what changes, under which condition, and whether the transcript row tells the truth.

```bash
rg -n "next\(\s*\{\s*\.\.\.e" "$MOD"
rg -n "return\s*\{\s*(result|deny|decision|drop|consumed|refuse|skip|text|isOffered)\b" "$MOD"
```

**4.7 Evasion and obfuscation.** BLOCK on any hit you cannot explain; validate passes `globalThis` and `Function` access (secgov-validate-probes, Probe 2) (C-SEC-007).

```bash
rg -n "globalThis|\bFunction\(|\beval\(|WebAssembly|import\(" "$MOD"
rg -n "atob\(|fromCharCode|\\\\x[0-9a-fA-F]{2}|\\\\u00|TextDecoder|base64" "$MOD"
find "$MOD" -name '*.js' -size +200k     # minified or bundled payloads
```

**4.8 Telemetry and egress.** List every URL and host; anything beyond the mod's stated purpose is a finding.
```bash
rg -n -o "https?://[^'\"\` )]+" "$MOD" | sort -u
rg -n 'telemetry\.(log|mark)|\$\.telemetry' "$MOD"
```

## 5. Cost

```bash
rg -n '\$\.(model\.(complete|fork|classify)|prompt\.submit|agent\.spawn)|\$\.clock\.(every|after)|maxTokens' "$MOD"
```

- [ ] **5.1** Mark cost none, model calls, or turns ([[Usage Cost Surface]]). No model call fires on every event without a matcher or pre-filter; no timer starts turns unattended.

## 6. Data flow and injection

- [ ] **6.1** Trace each `$.http.fetch`, `$.mcp.call`, `session.receive`, and `$.fs.read` result. If it reaches `prompt.*`, `$.prompt.submit`, a tool `result`, or a `deny` string, the mod is a conduit: require a reason or a classify-to-labels step ([[Prompt Injection via Mods]]).
- [ ] **6.2** Anything sent off-machine is named in the README (compare with the URL list from 4.8).

## 7. Failure behavior (for any mod that blocks or holds)

- [ ] **7.1** Blocking hooks have `.catch` that returns `{ deny }` or `{ refuse }`; a handler returning `undefined` counts as the hook absent (types 2.1.288 L994-1002) (C-SEC-033).
- [ ] **7.2** Holds wait inside a `$` call such as `$.ui.ask`, not a raw promise; own-promise waits count against the 10 s budget and a timed-out hook is skipped (docs-mods-events) (C-SEC-036). The `$.ui.ask` `catch` path keeps the safe answer, since it rejects on dismiss and in `claude -p`.

## 8. Verdict and record

| Verdict | When |
|---|---|
| avoid | Any BLOCK unresolved; or unexplained egress; or authority beyond stated purpose |
| trial | No BLOCK; L2 or L3, or any rewrite or approve authority; owner approves a contained trial outside this brain's agents |
| adopt | No BLOCK; purpose matches footprint; pinned; cost understood; failure paths fail closed |

Record: repo, pinned SHA, version validated on, hooks and calls lines, reach plus authority plus cost, findings with file:line, verdict, reviewer, date. Re-run from step 3 after every Claude Code release ([[Re-verify After Release Flow]]) and every mod update.

## Caveats

- Greps find shapes, not intent: a clean sweep does not prove safety, and a hit is not proof of malice. Runtime behaviors (label restoration, UI attribution, what `globalThis` holds) were not tested; see [[Mods Trust Model]]. Patterns were run with ripgrep against a 2.1.288 probe (secgov-validate-probes); with GNU grep use `grep -rnE` and adjust escapes.

## Related

The executable wrapper is [[Audit a Third-Party Mod Flow]]; the reasons for a static-only audit are in [[Read Only Audit Decision]]. Scoring uses [[Reach Levels]] and [[Usage Cost Surface]]; injection tracing uses [[Prompt Injection via Mods]]. The scan itself is described in [[Plugin Validate]]. Results land in [[Mod Catalog]], and recurring mistakes in [[Pitfalls Playbook]].

## Sources

- docs-mods-admin, docs-mods-overview, docs-mods-events, docs-mods-reference, docs-mods-interface, docs-plugins-security: https://code.claude.com/docs/en/plugins/mods/ (admin, overview, events, reference, interface) and https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md`
- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md`
