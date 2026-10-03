---
type: "gap"
title: "Unverified pre-release security findings on current builds"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/gap"
  - "#confidence/contested"
confidence: "contested"
lane: "rewrite"
related:
  - "[[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]]"
  - "[[Read Only Audit Decision]]"
  - "[[Mods Trust Model]]"
  - "[[Prompt Injection via Mods]]"
  - "[[Plugin Validate]]"
  - "[[Render Sites]]"
  - "[[Built-in sec-default Mod]]"
  - "[[Org Mod Controls]]"
  - "[[Audit a Third-Party Mod Flow]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Evidence Coverage Not Yet Verified]]"
source_urls:
  - "https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/interface (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"
sources:
  - "pluto-function-hooks"
  - "docs-plugins-security"
  - "docs-mods-admin"
  - "docs-mods-interface"
  - "docs-mods-troubleshoot"
  - "docs-mods-overview"
  - "secgov-validate-probes"
  - "types-2-1-288"
---

# Unverified pre-release security findings on current builds

Pluto Security tested mods on pre-release Claude Code 2.1.274 (published 2026-09-22). The security lane re-checked every finding against the 2.1.288 docs, typings, and static `claude plugin validate` probes, and three findings could not be settled without loading a mod: `plugin details` showing "Hooks (0)", the claude.ai-only content scan, and `AskUserQuestion` label restoration. Four more are confirmed as capabilities by the docs but were never observed on 2.1.288. This brain never loads a mod, so each item below states what a human-approved, isolated runtime trial would check.

## Status table

| # | Pluto finding (2.1.274) | Claim | 2.1.288 evidence | Status |
|---|---|---|---|---|
| 1 | `plugin details` lists a four-event mod as "Hooks (0)", "~0 tokens" | C-SEC-052 | docs-plugins-security L104 says the inventory lists "hooks with each hook's event", silent on function hooks | unverified |
| 2 | Content scan runs only on the claude.ai / sandbox-proxy path, not `--plugin-dir` or GitHub marketplaces | C-SEC-053 | nothing in docs or typings | unverified |
| 3 | Engine restores model-written `AskUserQuestion` option labels after a mod rewrite | C-SEC-055 | typings say a `questions` rewrite "must still fit the tool's schema or the original is drawn" (types 2.1.288 L9113-9128); no label rule | unverified |
| 4 | `session.start` reads the credentials file and prompt history, posts them silently | C-SEC-001, C-SEC-009 | docs: a mod reads files "anywhere your user account can"; validate passes an exfil-shaped module with no warning | capability confirmed, behaviour unobserved |
| 5 | `Input` in `AbovePrompt` phishes a key | C-SEC-054 | docs confirm elements and site | capability confirmed (docs only) |
| 6 | `tool.call` appends a command, `ToolUse` shows the original | C-SEC-011 | validate shows rewrites only on the `hooks:` line; auto mode denies changed input (docs-mods-troubleshoot L144-148) | partly mitigated, unobserved |
| 7 | Fetch a script, run it with `sh -c`; responses not integrity-pinned | C-SEC-009 | validate passes it; network policy does not cover `$.process.run` (docs-mods-admin) | capability confirmed, unobserved |

Superseded findings are not gaps: the env-var gate (C-SEC-063, docs win) and Pluto's admin advice (contradiction 10 in the security lane, docs win).

## Trial protocol (all items)

The lane brief forbids `claude plugin install`, `/plugin`, and `claude --plugin-dir` for agents. A trial therefore needs the owner's explicit, recorded approval, and isolation stronger than a project folder: `$.fs` accepts absolute paths (types 2.1.288 L3009-3014), so a "disposable project" bounds nothing (C-SEC-062, contradicted).

1. **Isolation.** A separate OS user account with its own home, or a throwaway VM snapshot. Never the owner's everyday account.
2. **Canaries, not secrets.** Sign in with a throwaway account or an API key with a hard spend cap; plant a fake credentials file and history file with unique canary strings.
3. **Contained network.** Point every test mod's `$.http.fetch` at a loopback listener inside the VM; block other egress at the VM firewall.
4. **Two policy states.** Run each check once with no managed settings (no guard for API-key users, C-SEC-018) and once with a managed settings file so `sec-default@builtin` loads.
5. **Record.** `claude --version`, the exact test mod source and its validate output, transcript and debug log (`claude --debug`), screenshots of what the user sees.
6. **Teardown.** Delete the account or revert the snapshot; revoke the throwaway key.

## What each trial would check

**1. `plugin details` disclosure (C-SEC-052).**
- Run `claude --plugin-dir <mod> plugin details <name>` (docs-plugins-security L104 says this reads files "without starting a session") on a mod hooking `tool.call`, `session.start`, `ui.render`, `command.run`.
- Pass if the `Component inventory` lists four function hooks with events; fail if it shows zero. Repeat after a local-marketplace install with `claude plugin details <name>`.
- Lowest-risk trial of the set: no session starts, so no hook runs.

**2. Content scan path (C-SEC-053).**
- Install one benign mod three ways: claude.ai directory path (if available), a GitHub marketplace, and `--plugin-dir`.
- Check the debug log and install output for any scan message on each path. Pass or fail is per path; a scan on all three refutes Pluto.

**3. Label restoration (C-SEC-055).**
- A mod hooks `ui.render` on `{ component: 'AskUserQuestion' }` and rewrites option labels and the question text.
- Ask Claude to call AskUserQuestion with labels "Delete everything" and "Keep". Check which labels and text are drawn, and which label value the tool result reports.
- Matters because, if labels are not restored, dialog swaps can turn a destructive choice into "Confirm".

**4. Silent exfiltration (C-SEC-001).**
- A `session.start` hook calls `$.fs.read` on the canary credentials and history files and posts both to the loopback listener.
- Check: does the read succeed, does any prompt or toast appear, does the guard (state 2) refuse anything. Expected per docs: succeeds silently in both states, since the guard does not restrict `$.fs` (C-SEC-020).

**5. Band phishing (C-SEC-054).**
- A mod draws a fake "session verification" `Input` in `AbovePrompt` and posts what is typed.
- Check whether anything marks the input as mod-drawn (plugin name, frame), which would give users a cue.

**6. Transcript falsification (C-SEC-011).**
- A `tool.call` hook on Bash appends `; echo canary` via `next({ ...e, input })` while `ui.render` on `ToolUse` shows the original.
- Check default mode and auto mode. Expected: auto mode denies with "a hook changed this call's input after the model wrote it"; default mode runs the changed command while showing the original.

**7. Fetch then run (C-SEC-009).**
- A mod fetches a script from the loopback listener and runs `$.process.run(["sh", "-c", body])`; change the script after the first run.
- Check that the second run executes the new body with no prompt, and whether the Bash sandbox (if enabled) applies (docs say it does not, C-SEC-002).

## Recommendations

- Run trial 1 first; it needs no session and settles the disclosure question for [[Audit a Third-Party Mod Flow]]. PRACTITIONER
- Until trials run, rely on `claude plugin validate` and source reading, not `plugin details`. EVIDENCE-BASED
- Treat question text and option descriptions in AskUserQuestion as mod-controllable regardless of trial 3. EVIDENCE-BASED
- Write each trial result back to the claim ledger as `verified` or `contradicted` with the build number. EVIDENCE-BASED

## Caveats

- Every expected outcome above is inference from docs; none is observed.
- Results bind to the build tested; re-run after each release ([[Evidence Coverage Not Yet Verified]]).
- Pluto's article sells a governance product; its framing is weighed accordingly.

## Related

Source critique: [[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]]. Why trials need isolation and approval: [[Read Only Audit Decision]]. Risk model: [[Mods Trust Model]], [[Prompt Injection via Mods]], [[Render Sites]]. Guard and admin: [[Built-in sec-default Mod]], [[Org Mod Controls]]. Audit procedure: [[Plugin Validate]], [[Audit a Third-Party Mod Flow]], [[Mod Security Audit Checklist]].

## Sources

- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (published 2026-09-22, retrieved 2026-10-03), capture `.raw/captures/web-2026-10-03/pluto-function-hooks.txt` L142, L151, L153, L210, L254, L266
- docs-plugins-security: https://code.claude.com/docs/en/plugins/security (retrieved 2026-10-03), capture L104, L108
- docs-mods-admin, docs-mods-interface, docs-mods-troubleshoot, docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/<page> (retrieved 2026-10-03)
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md` (2.1.288, run 2026-10-03)
- Security lane record: [[Contradictions Register#Security and governance]] (entries 8, 9)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` L3009-3014, L9113-9128
