---
type: "concept"
title: "Prompt Events"
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
lane: "api-and-events"
related:
  - "[[Observe Rewrite Answer]]"
  - "[[Hook Middleware Chain]]"
  - "[[Turn and Session Events]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Prompt Injection via Mods]]"
  - "[[Usage Cost Surface]]"
  - "[[Classic Hook Bridge]]"
  - "[[Mods API Namespaces]]"
  - "[[Patterns Playbook]]"
  - "[[Mods API Cheatsheet]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
sources:
  - "docs-mods-events"
  - "docs-mods-reference"
  - "docs-mods-api"
  - "types-2-1-288"
---

# Prompt Events

Ten events cover everything Claude reads as text: what the user submits (`prompt.submit`), what lands in or near the prompt box (`prompt.fill`, `prompt.suggest`, `prompt.edit`), and what Claude Code writes for Claude on its own (`prompt.compose`, `prompt.section`, `prompt.context`, `prompt.attachment`, `skill.prompt`, `attribution.text`) (docs-mods-reference L60-74). They are the most powerful and the most cache-sensitive events: a changed system prompt section or context block invalidates the prompt cache on every request (C-API-027).

## Event table

| Event | Fires | Rewrite / answer | Cached? | Evidence |
|---|---|---|---|---|
| `prompt.submit` | prompt submitted, before the turn | `next({ ...e, text })`, `next({ ...e, context })`, `{ drop }` | no | types 2.1.288 L3855-3863, L8425-8516 |
| `prompt.fill` | text about to go into the box as a draft (`$.prompt.fill`) | rewrite `text`/`mode`; `{ isFilled: false }` | no | types L3865-3875, L8139-8238 |
| `prompt.suggest` | text proposed as the dim Tab suggestion | rewrite `text`; `{ isShown: false }` | no | types L3877-3887, L8518-8580 |
| `prompt.edit` | user edits the box (key or paste) | rewrite `inputText` down or box up; `{ text, cursor }` consumes | no | types L3889-3899, L7999-8079 |
| `prompt.compose` | system prompt rendered | `{ sections }` list of `{ id, text, scope }` | per request | types L3925-3932, L7782-7905 |
| `prompt.section` | once per named system section | `{ text }` or `{ text: null }` | until `$.ui.invalidate('prompt.section')` | types L3901-3911, L8360-8379 |
| `prompt.context` | once per conversation, first-message context | `{ blocks, instructionFiles? }` | until invalidate, compaction or `/clear` | types L3913-3923, L7906-7980 |
| `prompt.attachment` | each engine-injected message (reminders, mode notes, mentioned files) | `{ text }` or `{ text: null }` | per attachment per process | types L3934-3944, L7672-7765 |
| `skill.prompt` | a skill's text expanded (`/name`, Skill tool, preload) | `{ text }` | no | types L4030-4040, L11195-11216 |
| `attribution.text` | commit or PR attribution composed; `kind` `commit`, `pr`, `exemption`, `remedy` | `{ text }` | no | types L4042-4051, L580-608 |

## `prompt.submit`

`e` fields (C-API-026):

- `text`: the prompt as it will reach the model, pastes expanded
- `attachments?`: `{ type: 'image' or 'audio' or 'document', mediaType?, filename? }`, never bytes
- `context?`: strings the model reads after the prompt, user never sees
- `turnId?`: set when typed while a turn ran
- `wait`: true when the user queued it with `chat:queueSubmit` (`ctrl+x enter` by default)
- `origin`: pinned `PromptOrigin` (types 2.1.288 L8239-8358): `composer`, `bridge`, `sdk`, `task-notification`, `scheduled-trigger`, `peer`, `peer-send-message`, `projects-relay`, `channel` (with `server`), `coordinator`, `observer`, `observer-activity`, `auto-continuation`, `unclassified`, `slack-ping`, `plugin` (with `name`, `asUser?`)

| To do this | Return | Who sees it |
|---|---|---|
| Rewrite the prompt | `next({ ...e, text: newText })` | the transcript shows the new text |
| Add hidden context | `next({ ...e, context: [...(e.context ?? []), extra] })` | Claude only |
| Stop it | `{ drop: 'reason' }` | the user sees the reason |

Source: docs-mods-events L206-210. Context added after `next` resolved is not attached, and is logged (types 2.1.288 L8486-8494).

```ts
import type { Register } from 'claude-code'

export const register: Register = (on) => {
  on('prompt.submit', async ($, e, next) => {
    if (e.origin.kind !== 'composer') return next(e)          // only the user's own typing
    if (!/\bPR\b|pull request/i.test(e.text)) return next(e)
    const git = await $.process.run(['git', 'branch', '--show-current'])
    if (git.exitCode !== 0) return next(e)
    return next({ ...e, context: [...(e.context ?? []), 'Current branch: ' + git.stdout.trim()] })
  })
}
```

Filtering on `origin.kind` keeps the hook off peer messages, scheduled triggers and other mods' prompts. A mod's own `$.prompt.submit({ text })` arrives with `origin: { kind: 'plugin', name }` and Claude reads it framed as sent by that plugin, unless `asUser: true` (types 2.1.288 L8387-8402; docs-mods-reference L172).

## System prompt: `prompt.compose` and `prompt.section`

- `prompt.compose` input: `model`, `promptModel`, `surfaces`, `tools`, `outputStyle`, `traits` (types 2.1.288 L7788-7826). Traits: `bare`, `lean`, `sdk-preset`, `teammate`, `analysis`, `print`, `skills`, `send-user-message` (L7900).
- Sections are `{ id, text, scope }`; every `shared` section must precede every `session` one, and a list breaking that order skips the hook (L3925-3932, L7828-7898).
- Engine ids: the full prompt opens `intro`, `system`, `doing_tasks`, `actions`, `tools`, `tone`; the lean prompt opens `lean_body`; `--bare` has one section `bare`; later sections include `communication`, `pronouns`, `memory`, `env_info_simple` (L7860-7898, L8362). A plugin's own section id is `<plugin>:<name>`.
- Paraphrase (L7840-7848): the API may cache `shared` text across organizations, so only text stable for the build and model belongs there.

```ts
on('prompt.compose', async ($, e, next) => {
  const { sections } = await next(e)
  return { sections: [...sections, { id: 'my-mod:policy', text: 'Never edit generated files under dist/.', scope: 'session' }] }
})
on('prompt.section', { name: 'memory' }, () => ({ text: null }))   // drop one engine section
```

## First-message context: `prompt.context`

Blocks from core: `claudeMd`, `userEmail`, `attachedProject`, `currentDate`, each only when present; `instructionFiles` lists the files behind `claudeMd`, and becomes `undefined` once a hook above rewrote that text (types 2.1.288 L7906-7980). `on('prompt.context', () => ({ blocks: [] }))` sends none.

## Engine-injected messages: `prompt.attachment`

`e.type` names the kind (for example `todo_reminder`, `plan_mode`); declared kinds carry `e.detail` (`plan_mode`, `plan_mode_reentry`, `plan_mode_exit`); `e.origin.kind` is `engine`, `hook` (with the settings `event`) or `plugin` (types 2.1.288 L7672-7753). `{ text: null }` omits it; the transcript keeps the engine's record (L3934-3944).

## Prompt box helpers

| Call | Event | Result |
|---|---|---|
| `$.prompt.read()` | `prompt.read` | `{ text, cursor }`, empty where no box |
| `$.prompt.fill({ text, mode?, decorations? })` | `prompt.fill` | `{ isFilled }`; mode `replace` (default), `append`, `insert` |
| `$.prompt.suggest({ text })` | `prompt.suggest` | `{ isShown }`, false while the box holds text or a turn runs |
| `$.prompt.submit({ text, asUser? })` | `prompt.submit` | resolves when that turn starts; waits for idle |

Evidence: types 2.1.288 L2733-2794. Do not `await $.prompt.submit` inside a hook that runs while Claude works (docs-mods-api L132).

## Recommendations

- Put dynamic facts in `prompt.submit` `context`, not in `prompt.section` or `prompt.compose`, so the system prompt stays cacheable. EVIDENCE-BASED
- Add your own system text as a `session`-scope section at the end; never put varying text in `shared`. EVIDENCE-BASED
- Gate prompt rewrites on `e.origin.kind`, so peers and triggers are not rewritten by accident. PRACTITIONER
- Treat any third-party mod that hooks `prompt.*` or `skill.prompt` as able to rewrite what Claude believes; audit it like code. EVIDENCE-BASED

## Caveats

- The TypeScript snippets here type-check with TypeScript 5.9.3 against the 2.1.288 typings under the strict tsconfig Claude Code recommends (static check only; nothing was loaded or run; see [[Contradictions Register#Static check of this lane's snippets]]).
- Section ids beyond the opening six are named as examples in the typings; the full list varies by model and traits, so read ids off `next(e)` rather than hard-coding many.
- `attribution.text` `kind` values `exemption` and `remedy` are typings-only.

## Related

Moves and answer shapes: [[Observe Rewrite Answer]], [[Hook Middleware Chain]]. What happens after submit: [[Turn and Session Events]]. Cache cost: [[Prompt Cache Discipline]] and [[Usage Cost Surface]]. Risk: [[Prompt Injection via Mods]]. Porting `UserPromptSubmit` hooks: [[Classic Hook Bridge]]. Reusable shapes in [[Patterns Playbook]]; lookup in [[Mods API Namespaces]] and [[Mods API Cheatsheet]].

## Sources

- docs-mods-events: https://code.claude.com/docs/en/plugins/mods/events (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
