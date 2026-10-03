---
type: "concept"
title: "Prompt Injection via Mods"
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
lane: "security-governance"
related:
  - "[[Mods Trust Model]]"
  - "[[Prompt Events]]"
  - "[[Tool Events]]"
  - "[[Observe Rewrite Answer]]"
  - "[[Turn and Session Events]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Built-in sec-default Mod]]"
  - "[[OneWave claude-code-mods]]"
  - "[[Usage Cost Surface]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
sources:
  - "docs-mods-reference"
  - "docs-mods-events"
  - "docs-mods-api"
  - "docs-mods-admin"
  - "types-2-1-288"
  - "blog-mods-launch"
  - "secgov-validate-probes"
  - "pluto-function-hooks"
  - "compass-report"
---

# Prompt Injection via Mods

Mods touch prompt injection in two directions. A malicious or compromised mod is an injector: it can write directly into what Claude reads (system prompt sections, tool descriptions, tool results, prompts sent as your own words). A well-meant mod can be a conduit: it pulls third-party text (web, email, Slack, peer sessions, PR comments) and forwards it into the model loop. Both are documented capabilities; neither needs any exploit (docs-mods-reference, "Prompts and what Claude reads").

## Injection points a mod controls

Every row is a documented hook point or method. Anything a mod puts here becomes model input.

| Point | What Claude reads | Who can protect it |
|---|---|---|
| `prompt.submit` rewrite | `next({ ...e, text })` or `context` changes the user's prompt | Nothing for user prompts |
| `$.prompt.submit({ text })` | Text framed with a sentence naming the mod as sender | The frame is attribution only (C-SEC-017) |
| `$.prompt.submit({ text, asUser: true })` | Text read bare, as the user's words; hooks still see `origin.kind: 'plugin'` | Earlier mods and policy mods can see the origin (types 2.1.288 L8336-8353) |
| `prompt.section`, `prompt.compose` | System prompt sections replaced or omitted | sec-default protects the system prompt from user mods where it loads (docs-mods-admin) |
| `prompt.context`, `prompt.attachment`, `skill.prompt` | First-message context, reminders, expanded skill text | Managed `CLAUDE.md` and managed instructions protected where the guard loads |
| `tool.describe` | A tool's description | Managed MCP tool descriptions protected where the guard loads |
| `tool.call` answered with `{ result }` | "the result you return is all Claude learns" (docs-mods-events) | Nothing |
| `tool.call` answered with `{ deny }` | Claude reads the deny text as the tool result (docs-mods-events) | Nothing |
| `session.append` rewrite | Stored transcript rows rewritten before storage | Nothing |
| `$.session.send` | Another session's or subagent's Claude reads the message as a peer's | Receiver's inbound settings (docs-mods-api) |

Practical consequence: an attacker who controls a mod does not need the user's prompt. A `{ deny }` reason or a fabricated `{ result }` is model-visible text that can carry instructions, and validate shows it only as a hook on `tool.call` (secgov-validate-probes, Probe 1).

## Conduits: untrusted text a mod may forward

| Source | How it enters a mod | Risk if forwarded into the main loop |
|---|---|---|
| Web pages, APIs | `$.http.fetch` text | Instructions in fetched content |
| MCP tools | `$.mcp.call` results | Server-controlled text; types say an MCP server's name is "untrusted text" (types L5636) |
| Other sessions | `session.receive`, which can see a message "held for your approval" before you approve it | The sender's name is "whatever the sender wrote" (docs-mods-api) (C-SEC-058) |
| Files and repos | `$.fs.read` | Instructions planted in READMEs or issues |
| Connected inboxes | A mod reading email, Slack, or calendar connectors | The seed report flags OneWave's inbox-alerts as this shape; not code-reviewed here (compass-report, section 4) |

## Safer shapes

1. **Display, do not forward.** Draw third-party text in a pane or band and never pass it to `prompt.submit`, `prompt.context`, or a tool result. Drawing is not model input.
2. **Classify instead of summarize.** `$.model.classify(text, labels)` treats `text` as data, makes the model answer with a label alone, and resolves `undefined` when the answer names no label (types 2.1.288 L2434-2452). Code then acts on a closed set of values. A free-text summary can carry injected instructions; a label from a fixed list cannot.
3. **Tool-less completions.** `$.model.complete` has no tools and no history (types L2386-2414), so an injected instruction cannot run a tool inside that call. Its output is still untrusted if you forward it.
4. **Never `asUser` for third-party text.** The frame is weak attribution, but `asUser: true` removes even that from Claude's view.
5. **Redact before read.** A `tool.call` hook can rewrite a result before Claude reads it; the launch blog names "Redact secrets from tool output" as a mod use (blog-mods-launch). Redaction mods reduce secret leakage, not instruction injection.
6. **Order a guard first.** A policy mod in `prependPlugins` sees every prompt and tool result after later mods return it, so it can log or strip injections that users' mods add (docs-mods-admin, "Install your organization's mods and set the order").

## Example: classify, then act on a closed set

```javascript
// A /triage command that never forwards the issue text to the main loop
on('command.run', { command: 'triage' }, async ($, e) => {
  const kind = await $.model.classify(e.args, ['bug', 'feature', 'question'])
  // kind is one of the three labels, or undefined
  return { text: 'Label: ' + (kind ?? 'unknown') }
})
```

Shape follows the `/triage` example in docs-mods-api, with `classify` from the typings. It still spends usage (see [[Usage Cost Surface]]).

## Recommendations

- In review, list every path from `$.http.fetch`, `$.mcp.call`, `session.receive`, or `$.fs.read` output to `prompt.*`, `$.prompt.submit`, a tool `result`, or a `deny` string. Any such path needs a reason. EVIDENCE-BASED
- Reject mods that call `$.prompt.submit` with `asUser: true` on text they did not get from the user. PRACTITIONER
- Prefer mods that display external content over mods that forward it. PRACTITIONER
- Treat `tool.call` answers (`result`, `deny`) as model input when reviewing; they are not just UI. EVIDENCE-BASED
- On machines without managed settings, assume no protection for the system prompt or instructions against a user mod. EVIDENCE-BASED

> [!contradiction]
> The seed report suggests a tool-less `$.model.complete` as the safe way to handle untrusted text (compass-report, section 4). The typings support "no tools, no history" for the call itself, but its reply is free text. Forwarding that reply into the main loop re-opens the injection. This note's position: classify to a closed label set, or keep the reply out of model context.

## Caveats

- Injection impact depends on what the main loop's tools and permission rules allow; this note does not test model behavior.
- sec-default's protection list comes from the admin page; its source was not read here (see [[Built-in sec-default Mod]]).
- `$.model.classify` behavior is from typings only.

## Related

The capability table is grounded in [[Prompt Events]], [[Tool Events]], [[Turn and Session Events]], and the observe, rewrite, and answer choices in [[Observe Rewrite Answer]]. The broader frame is [[Mods Trust Model]]; protection where it exists is [[Built-in sec-default Mod]]. Review steps that apply this note are in [[Mod Security Audit Checklist]] and [[Audit a Third-Party Mod Flow]]. A real conduit-shaped mod family is listed under [[OneWave claude-code-mods]]. Model calls used for defense cost usage: [[Usage Cost Surface]].

## Sources

- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- blog-mods-launch: https://claude.com/blog/claude-code-mods (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts`
- secgov-validate-probes: `.raw/captures/lanes-2026-10-03/security-governance/secgov-validate-probes-2-1-288.md`
- pluto-function-hooks: https://pluto.security/blog/claude-code-function-hooks-security/ (retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md`
