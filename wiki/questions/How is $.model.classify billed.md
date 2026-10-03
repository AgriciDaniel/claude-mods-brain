---
type: "question"
title: "How is $.model.classify billed"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/question"
  - "#confidence/practitioner"
confidence: "practitioner"
lane: "patterns-and-ideas"
related:
  - "[[Usage Cost Surface]]"
  - "[[Mods API Namespaces]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Mod Security Audit Checklist]]"
  - "[[Prompt Cache Discipline]]"
  - "[[Plugin Validate]]"
  - "[[Ranked Build Ideas]]"
  - "[[Pitfalls Playbook]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
sources:
  - "types-2-1-288"
  - "docs-mods-api"
  - "docs-mods-admin"
  - "docs-mods-reference"
  - "docs-mods-overview"
  - "gh-issue-91870"
  - "pa-gh-91870-mined"
  - "compass-report"
---

# How is $.model.classify billed

Short answer: `$.model.classify` is one `$.model.complete` call in disguise, so it is billed exactly like `$.model.complete`: to the user's own plan or API key through the session's own API client, on the engine's small fast model unless the mod names another (types 2.1.288 L2436-2452, L1218-1226; docs-mods-api). That is an inference from the typings plus the docs' blanket statement that `$.model` calls "use the user's plan or API key" (docs-mods-api). No docs page describes `classify` itself, it returns no usage figures to the mod, and nothing documents which model "small fast" resolves to. Confidence stays practitioner until an experiment confirms the per-call cost.

## What the evidence says

| Fact | Evidence | Grade |
|---|---|---|
| `$.model` has `complete`, `fork`, `classify` | docs-mods-reference mods API table (L171) | official |
| Paraphrase: classify picks one of `labels` for `text` with a single `$.model.complete` completion and a fixed classifier prompt | types 2.1.288 L2436-2452 | primary |
| Default model is "the engine's small fast model"; `options.model` takes an alias or id | types 2.1.288 L1218-1226, L2444-2446 | primary |
| `$.model` is "Completions through the session's own client and credentials" (paraphrase of the namespace comment) | types 2.1.288 L2385 | primary |
| "These calls use the user's plan or API key." (quote, 9 words) | docs-mods-api L97, after the `complete` and `fork` examples | official |
| Overview lists "Spend your usage: call a model on your plan or API key" | docs-mods-overview | official |
| Result is `string or undefined` only, no `usage` | types 2.1.288 OpValueOf L6746, signature L2452 | primary |
| Classify fires its own interceptable event `model.classify` with `{ text, labels, options }` | types 2.1.288 OpEventOf L6412-6418 | primary |
| `$.model.complete` returns `usage` (ModelUsage) per call, `maxTokens` default 1024 | types 2.1.288 L5857-5877, L5811-5819 | primary |
| On #91870 the direct question of which quota a plugin's model call hits went unanswered by staff | [comment 5540419526](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5540419526), 2026-09-04 | primary (unanswered) |
| A commenter notes `$.model.complete` runs on the session's own client, so users need no key of their own (paraphrase) | [comment 5835788532](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5835788532), 2026-09-25 | practitioner |
| Admin review table names `$.model.complete` as the usage-spending call; it does not list `classify` or `fork` | docs-mods-admin review table | official |

## What follows

1. **Who pays**: the person running the session. On a subscription plan that means plan usage; on an API key it means API spend. The docs do not distinguish further. EVIDENCE-BASED
2. **Model**: default "small fast" model. Its identity is not documented; on classic hooks, prompt and agent hooks also default to "the model Claude Code uses for background functionality" without naming it (docs-hooks). Pass `{ model: 'haiku' }` to make the choice explicit and reviewable. PRACTITIONER
3. **Size**: one request with the text, the label list and a fixed classifier prompt, answered with one label. The fixed prompt's length and the `maxTokens` used are not exposed. Per-call cost is small but not zero, and it scales with `text` length. PRACTITIONER
4. **No cache reuse**: unlike `$.model.fork`, a complete (and so a classify) carries no conversation, so it does not ride the main thread's prompt cache (types 2.1.288 L2415-2421). Calling it on every `tool.call` or `prompt.submit` multiplies small requests. PRACTITIONER
5. **Visibility**: because classify returns no usage, a mod cannot meter its own classify spend directly. An earlier mod can observe the `model.classify` event, and possibly the underlying `model.complete`, through the chain (docs-mods-api: every `$` call is an event). Whether the inner complete is raised as a separate event is not documented. Unverified.

> [!contradiction]
> The seed report says `classify` "is undocumented, and its billing is my inference" (compass-report L304). On 2.1.288 the generated typings do document its mechanics (one completion over `$.model.complete`), which upgrades the billing claim from guess to strong inference; the docs pages still do not describe it. Typings win on mechanics; the docs' general `$.model` statement covers billing.

> [!gap]
> The admin page's review table lists only `$.model.complete` as a usage-spending call. A reviewer scanning the `calls:` line of `claude plugin validate` for that string will miss `$.model.classify` and `$.model.fork`. Add both to any audit checklist.

## Experiment that would settle the open parts

Run by the owner, in a disposable folder, because this lane may not load mods:

1. Write a scratch mod with a `/classify-bench` command that calls `$.model.classify(sample, ['bug', 'feature'])` 20 times, then reads `(await $.session.usage()).cost` before and after.
2. In the same mod, hook `model.complete` and `model.classify` and `$.ui.log` each event with `next.origin`, to see whether classify raises an inner `model.complete` and what `usage` it reports.
3. Repeat with `{ model: 'haiku' }` and with no model, and compare the reported `model` field in `usage` from step 2.
4. Record the per-call input and output tokens, the default model id, and whether `cost` moved, then update this note and C-PAT-030.

Expected result if the inference holds: cost rises on the user's plan or key, the inner request uses the small fast model, and tokens per call are a few hundred input and a handful of output.

## Recommendations

- Treat `$.model.classify` as a model call on the user's usage, and disclose it in the plugin description. EVIDENCE-BASED
- Pin `options.model` explicitly so reviewers and users know which model is paid for. PRACTITIONER
- Never call classify on every tool call or prompt without a cheap prefilter (regex or matcher) in front of it. PRACTITIONER
- Guard with try/catch: classify rejects on a failed request, an abort, or an empty reply, unlike complete which resolves with a reason (types 2.1.288 L2436-2452). EVIDENCE-BASED

## Caveats

- No live test was run; billing is inferred from typings and docs on 2.1.288.
- The identity of the small fast model is undocumented and can change between releases.
- #91870 has no staff statement on `$.model.*` billing or on `classify` at all (pa-gh-91870-mined section 3b); a 2.1.272 report of a 256 token default and no usage field is superseded by the 2.1.288 typings.

## Related

The full cost picture is in [[Usage Cost Surface]]; the method list in [[Mods API Namespaces]] and [[Mods API Cheatsheet]]. Reviewers should add classify to [[Mod Security Audit Checklist]] and read [[Plugin Validate]] output with it in mind. Why fork is cheaper for context-heavy questions is in [[Prompt Cache Discipline]]. Ideas that would call it are costed in [[Ranked Build Ideas]], the trap is listed in [[Pitfalls Playbook]], and the confidence handling follows [[Uncertainty Eval Policy]].

## Sources

- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- docs-mods-api: https://code.claude.com/docs/en/plugins/mods/api (retrieved 2026-10-03)
- docs-mods-admin: https://code.claude.com/docs/en/plugins/mods/admin (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-overview: https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)
- docs-hooks: https://code.claude.com/docs/en/hooks (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (capture retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (secondary, lead list only)
