---
type: "question"
title: "Does claude plugin test support userConfig values yet"
domain: "Claude Code mods"
status: "developing"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/question"
  - "#confidence/evidence-based"
confidence: "evidence-based"
lane: "patterns-and-ideas"
related:
  - "[[Testing Kit]]"
  - "[[Testing Playbook]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Mods API gaps requested in the 91870 thread but not shipped]]"
  - "[[Versioning and API Drift]]"
  - "[[Re-verify After Release Flow]]"
  - "[[Pitfalls Playbook]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)"
  - "https://github.com/anthropics/claude-code/issues/91870#issuecomment-5827373997 (capture retrieved 2026-10-03)"
sources:
  - "types-2-1-288"
  - "docs-mods-test"
  - "docs-mods-reference"
  - "docs-mods-troubleshoot"
  - "gh-issue-91870"
  - "compass-report"
---

# Does claude plugin test support userConfig values yet

Yes, on 2.1.288 according to the generated typings: `test` takes an options object before the body, and its `options` field holds "the plugin under test's `userConfig` values, standing as the ones stored in settings" (types 2.1.288 `claude-code/testing`, TestOptions L14924-14946, paraphrase). `register(on, options)` receives them as a real load would: unlisted values unset, defaults filled in, validated, and a bad required field fails the load. Inline plugins get none. The docs page for testing does not mention this field yet, and the last report in #91870 (2.1.282) said it was missing, so the answer rests on the typings, which the brief ranks as primary.

## Evidence

| Source | Date and version | What it says |
|---|---|---|
| @lperezmo on #91870, [comment 5827373997](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5827373997) | 2026-09-25, 2.1.282 | "`claude plugin test` can't set userConfig values." (quote, 7 words) |
| Staff reply [5840819337](https://github.com/anthropics/claude-code/issues/91870#issuecomment-5840819337) | 2026-09-25 | Answers only the single-filter point; userConfig not addressed |
| docs-mods-test, "Test a policy mod" | 2.1.287 docs, captured 2026-10-03 | Documents `plugins` and `tier` on the options object; no `options` field |
| types 2.1.288 TestOptions | Written by 2.1.288 | `plugins?`, `timeoutMs?`, `options?: PluginOptions`, with the example `test('greets', { options: { greeting: 'yo' } }, body)` |
| types 2.1.288 PluginOptions L7186-7198 | 2.1.288 | Values stored in `pluginConfigs[<plugin>].options`, validated against declared `type`; string fields with `options` hold one of them |
| Tests in two personal mods reviewed for this brain | Written against local typings | Both pass option values as `test('...', { options: { ... } }, body)` |

## How to use it

```typescript
import { expect, test } from 'claude-code/testing'

const OPTIONS = { options: { proseExtensions: 'md,txt', ignorePaths: '' } }

test('a markdown Write is rewritten', OPTIONS, async ($, on) => {
  on('tool.call', (_$, e) => ({ result: e.tool === 'Write' ? 'wrote ' + e.content : 'ok' }))
  const out = await $.tool.call({ tool: 'Write', file_path: 'a.md', content: 'x' })
  expect(out).toBeDefined()
})
```
> [!contradiction]
> The docs' test examples (docs-mods-test L31, L122) omit fields the 2.1.288 typings require: `origin` and `presentation` on `$.command.run` (types 2.1.288 L1610-1636) and a typed `value` on a `command.register` stub. The snippet above follows the typings and compiles under the generated tsconfig (strict, `noUncheckedIndexedAccess`) with tsc 5.9.3, checked 2026-10-03.

Leave `options` out to test the manifest defaults. To test the failure path, pass a value that breaks a declared type or omit a required field; the load fails at the first `$` call, as `options do not fit plugin.json userConfig` does in a session (docs-mods-troubleshoot).

## What is still unverified

- Whether `claude plugin test` on 2.1.288 actually honours `options` at runtime. The typings are written by the binary, which makes a mismatch unlikely, but this lane is not allowed to run tests.
- Whether `sensitive` userConfig fields (kept in secure storage in a session) behave the same in tests.
- Which release added it: between 2.1.282 (reported missing) and 2.1.288 (in typings). The 2.1.287 typings were not captured.

## Experiment that would settle it

Run by the owner on a scratch copy, not in this lane:

1. Copy a mod you own that declares a `userConfig` field, and has a test passing it through `options`, to a temp folder.
2. Run `claude plugin test` there; pick a test whose assertion depends on that option value.
3. Change the option value in the test to one that should change the outcome (an empty string, say) and confirm the test now fails.
4. Record the version and result here and in claim C-PAT-028.

> [!contradiction]
> The seed report lists "`claude plugin test` can't set `userConfig` values (lperezmo on #91870)" as a known gap (compass-report L221). That was true of 2.1.282 per the thread, but the 2.1.288 typings declare `TestOptions.options` for exactly this. Typings rank above the thread; the gap is closed pending the runtime experiment. The docs page lags the typings.

## Recommendations

- Pass `userConfig` values with `test(name, { options }, body)` and cover at least defaults, one custom value, and one invalid value. EVIDENCE-BASED
- Keep option parsing in a pure helper and unit test it without the engine too. PRACTITIONER
- Wrap any `new RegExp(option)` in try/catch, since an invalid value would otherwise fail the whole module load in tests and sessions alike. EVIDENCE-BASED
- After each release, regenerate typings and grep `TestOptions` to catch a rename. PRACTITIONER

## Caveats

- Version sensitive: the field may be renamed; the docs do not promise it.
- Evidence is typings plus untested test files from personal mods reviewed for this brain; status stays developing until the experiment runs.

## Related

The kit is described in [[Testing Kit]] and the test plan in [[Testing Playbook]]; options themselves in [[userConfig and Plugin Options]]. The thread's other test-kit asks are tracked in [[Mods API gaps requested in the 91870 thread but not shipped]]. Drift handling is [[Versioning and API Drift]] and [[Re-verify After Release Flow]]; the invalid-regex trap is in [[Pitfalls Playbook]]; the confidence call follows [[Uncertainty Eval Policy]].

## Sources

- types-2-1-288: `.raw/captures/types-2.1.288/claude-code/index.d.ts` (retrieved 2026-10-03)
- docs-mods-test: https://code.claude.com/docs/en/plugins/mods/test (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870 (capture retrieved 2026-10-03)
- compass-report: `.raw/sources/compass-report-2026-10-02.md` (secondary, lead list only)
