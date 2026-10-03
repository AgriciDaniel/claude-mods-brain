---
type: "source"
title: "Contradictions Register"
domain: "Claude Code mods"
status: "evergreen"
created: "2026-10-03"
updated: "2026-10-03"
tested_on: "2.1.288"
tags:
  - "#domain/claude-code-mods"
  - "#type/source"
  - "#confidence/evidence-based"
confidence: "evidence-based"
related:
  - "[[Claim Verification Flow]]"
  - "[[research-pack-claude-mods|Research Pack]]"
  - "[[Mods API Cheatsheet]]"
  - "[[Render Sites]]"
  - "[[UI Elements and JSX]]"
  - "[[Mods Trust Model]]"
  - "[[Mod Catalog]]"
  - "[[Testing Kit]]"
  - "[[Versioning and API Drift]]"
  - "[[Inside Claude Code Function Hooks The Trust Problem (Pluto Security)]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
sources:
  - "types-2-1-288"
  - "docs-mods-reference"
  - "compass-report"
---

# Contradictions Register

Every place where two sources disagree, with the evidence on each side and which one wins, as recorded by the five research lanes on 2026-10-03. The ranking rule: the typings Claude Code 2.1.288 wrote for this build win on names and shapes; the docs (written "as of v2.1.287") win on intent; the design thread, independent research, community repos, and the seed report follow, in that order. Each entry names the claim-ledger row it settles. #confidence/evidence-based

How a new contradiction enters: [[Claim Verification Flow]]. Sources: [[research-pack-claude-mods|Research Pack]].

## API and events

Ranking rule applied: the generated typings for the installed build (types-2-1-288, written by Claude Code 2.1.288) win over the docs pages, which describe v2.1.287 and say so themselves. Paraphrase of docs-mods-reference L11-13: when the GitHub copy of the types and your build disagree, trust the copy Claude Code writes for your version. The seed report (compass-report) loses to both.

### X1. Which surfaces a render hook can see (docs vs typings)

- Docs: docs-mods-reference L190 says `e.surface` is `terminal` or `desktop`, and the elements table has only Terminal and Desktop columns (L222-235).
- Typings: `RenderSurface = 'terminal' | 'desktop' | 'mobile' | 'vscode'` (types 2.1.288 L9695). `Elements` declares four tables (L3586-3660), and `$.session.surfaces()` lists "a terminal and two phones" as possible at once (L2600-2612).
- Winner: typings. A hook that branches only on `terminal` vs `desktop` must also handle `mobile` and `vscode`.
- Claim: C-API-049 (contradicted).

### X2. Where `Svg` draws (docs and seed vs typings)

- Docs: docs-mods-reference L232 marks `Svg` Desktop only; docs-mods-interface L424 says "Desktop". Seed: compass-report section 1 says "Desktop-only elements: `Svg`".
- Typings: types 2.1.288 L3588-3592 says every remote surface carries `Svg`; the `desktop`, `mobile` and `vscode` tables all declare it (L3618-3660). The terminal table has none.
- Winner: typings. The docs and seed are correct about the terminal (no `Svg`), wrong to call it desktop only.
- Claim: C-API-050 (contradicted).

### X3. Cost of `$.session.usage()` (seed vs typings)

- Seed: compass-report section 1 says `usage()` "is free unless you ask for a `breakdown`".
- Typings: types 2.1.288 L2626-2630: the plain call costs nothing; `breakdown: "full"` counts each category with the token-count API as `/context` does; `"summary"` estimates locally. So a `summary` breakdown is also free of API calls.
- Winner: typings. Seed is imprecise rather than wrong.
- Claim: C-API-058.

### X4. What a reload re-runs (seed vs typings)

- Seed: compass-report says "Every reload re-runs `register` and `session.start` and wipes module variables."
- Typings: types 2.1.288 L4057-4059: a later `session.start` "runs its hooks alone", for an enable, a worker respawn, or a reload of "changed modules only; all if one hooks `engine.create`/`plugin.register`". Docs (docs-mods-reference L105) say it fires again "after a reload of that mod".
- Winner: typings plus docs. A reload re-runs the changed mod only, unless some loaded mod hooks `engine.create` or `plugin.register`.
- Claim: C-API-033.

### X5. Streaming hooks and `yield*` (seed vs typings)

- Seed: compass-report says hooks on `turn.step` and `process.spawn` "must be async generators that use `yield* next(e)`".
- Typings: the generator part is right (types 2.1.288 L11454-11477). `yield*` is one option: a transforming hook iterates `for await (const chunk of next(e))` and yields rewritten chunks (example at L3338-3344); returning nothing lets the last `next(e)` result stand (L11457).
- Winner: typings. Treat `yield* next(e)` as the pass-through form, not a requirement.

### X6. `tool.check` input type (docs example vs typings)

- Docs: docs-mods-events L189 reads `e.input.command.includes('git push')` directly.
- Typings: `ToolCheckInput.input` is `unknown` (types 2.1.288 L12110-12115), and a `{ tool: 'Bash' }` matcher does not narrow it. Under the strict tsconfig the engine supplies (L66-77), the docs line does not type-check in a `.ts` module; it works in plain `.js`.
- Static check (2026-10-03, TypeScript 5.9.3 against the 2.1.288 typings, scratch project, nothing loaded or run): the docs line fails with `TS18046: 'e.input' is of type 'unknown'`.
- Winner: both are right at run time; for TypeScript, narrow first, for example `const command = typeof (e.input as { command?: unknown }).command === 'string' ? (e.input as { command: string }).command : ''`.

### X7. Undocumented members present in the 2.1.288 typings (docs gaps, not conflicts)

| Surface | Docs say | Typings add | Evidence |
|---|---|---|---|
| `$.ui` methods | 14 listed (docs-mods-reference L167) | `selection()` | types L2368-2382 |
| `$.session` methods | 14 listed (L174) | `surface()` (deprecated in favour of `surfaces()`) | types L2613-2620 |
| `next` members | signal, origin, budget, to, error, called (L37-42) | `is`, `event`, `trace` | types L6144-6182 |
| Hook budgets | 10 s and 1 s (L245-246) | `lingerMs: 5_000` after an abort | types L4820-4828 |
| `Button` props | key, label, onPress, hotkey, plain, dimColor, autoFocus, action (L226) | `variant` (`primary`/`secondary`), `role: 'dismiss'`, `hover` | types L900-1000 |
| `Text` `wrap` values | wrap, truncate, truncate-start, truncate-middle, truncate-end (interface L420) | `end`, `middle` | types L11885 |
| `ToolProgress` props | `kind` (L201) | `kind: 'background_hint'`, `hint` | types L9405-9424 |
| `$.fs.list` entries | `{ name, kind, size, isLink }` (api L186) | `mtimeMs` | types L4619-4653 |
| `$.ui.blit` rate | not stated | up to 120 a second taken, about 60 shown | types L2183-2184 |
| `context` cap | not stated | past 100,000 chars (200,000 together) the model reads head + path | types L8440, L12025 |

Treat each as "present in 2.1.288, undocumented": usable, but recheck at every release (see C-API notes' Caveats).

### X8. Element string limit for `Text` (docs only)

- Docs: docs-mods-reference L251 caps one string child of a `Text` at 10,000 characters.
- Typings: no `Text` cap stated; caps exist for `Code` (L1458) and `Markdown` (L5395) at 10,000. Not a conflict, but the `Text` figure is docs-only (SINGLE-SOURCE).

### X9. Destructuring surface-specific elements (docs examples vs typings)

- Docs: the interface examples destructure `Input` (and the gallery `Select`, `Raster`, `Svg`) straight from `$.ui.resolve(e)` without checking `e.surface` (docs-mods-interface L560; docs-mods-gallery starter module).
- Typings: unnarrowed, `resolve` returns the union of the four surface tables, and "shared names type-check" only (types 2.1.288 L2199-2214); mobile has no `Input` or `Select`. The same static check reports `TS2339: Property 'Input' does not exist` on the union.
- Winner: typings for `.ts`/`.tsx` mods. At run time the handed-out table is completed with every element name, and an omitted one draws a fragment (types 2.1.288 L3578-3580), so in plain JavaScript the control silently does not appear on that surface. Narrow `e.surface` first and draw a fallback (UI Elements and JSX note).

### Static check of this lane's snippets

All TypeScript and TSX snippets in this lane's notes were assembled into seven modules and checked with TypeScript 5.9.3 (`strict`, `noUncheckedIndexedAccess`, `jsxFactory: h`) against `.raw/captures/types-2.1.288/` with zero errors. A negative control (docs-style `e.input.command`, unnarrowed `Input`, a non-generator `turn.step` hook, assigning to `e.cwd`) produced the four expected errors (TS18046, TS2339, TS2322, TS2540). Type-checks only; no mod was installed, loaded or run.

## Lifecycle

Seed report (`compass-report`) and community claims checked against the official docs captures, the 2.1.288 typings, the bundled `plugin-authoring` skill, and a read-only CLI run. Ranked by how much each changes what an author should do.

### X-LIF-01: Can `claude plugin test` set userConfig values?

- Seed / community side: compass-report "Testing, Known gaps" says Paraphrase: `claude plugin test` cannot set `userConfig` values, citing lperezmo on #91870. The comment (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5827373997, 2026-09-25, built on 2.1.282) says: "`claude plugin test` can't set userConfig values."
- Official side: types 2.1.288 L14924-14945 declare `TestOptions.options?: PluginOptions`, "The plugin under test's `userConfig` values, standing as the ones stored in settings", with the example `test('greets', { options: { greeting: 'yo' } }, body)`. The bundled skill's reference.md says the same: a test gives the plugin its values with `test(name, { options }, body)`.
- The docs test page (docs-mods-test) is silent: it documents `plugins` and `tier` but not `options`.
- Verdict: typings win for 2.1.288 (rank 1 source, written by the installed build). The community claim was true for 2.1.282 at most and is stale now. Not executed by this lane (we did not run `claude plugin test`), so mark the capability "declared, not run". Claims: C-LIF-029. Affects the patterns lane question note "Does claude plugin test support userConfig values yet".

### X-LIF-02: Does a plugin in `~/.claude/skills/` hot-reload?

- Community side: lperezmo (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5670161416, 2026-09-14, 2.1.270): Paraphrase: a user-level mod in `~/.claude/skills/` kept serving the old module until a restart, while `claude -p` loaded fresh, so headless checks passed against new code the interactive session never ran.
- Official side: the 2.1.288 skill reference.md says an interactive session watches the folder, "as is a plugin auto-loaded from a skills folder (`~/.claude/skills/<name>`, the project's `.claude/skills/<name>`)".
- Verdict: the skill (bundled with 2.1.288) wins for current builds, but only one official source says it and nobody has re-tested on 2.1.287 or later. Keep it SINGLE-SOURCE (C-LIF-013) and develop with `--plugin-dir`, which both sides agree reloads. The `-p` versus interactive split lperezmo hit is still real: `-p` always loads fresh (C-LIF-012).

### X-LIF-03: Do edits to a locally added marketplace plugin apply on `/reload-plugins`?

- Official side: docs-plugins-create-marketplace ("Test an edit to a plugin") and docs-plugins-loading ("In-place and copied plugins"): a relative-path plugin in a marketplace added from a local directory loads in place, and edits take effect at the next session start or `/reload-plugins` with no version change.
- Community side: shivam-dhaka (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5943145826, 2026-10-02, Desktop bundling 2.1.286): Paraphrase: Desktop kept drawing the install-time copy after source edits; `/reload-plugins` alone did not pick it up, and only uninstall plus install did.
- Verdict: docs win for the terminal; the Desktop report is a plausible surface-specific bug on an older bundled build. Mark C-LIF-051 contested for Desktop and keep `--plugin-dir` as the dev loop on every surface.

### X-LIF-04: Seed report's install sequence ends in `/reload-plugins`; is a restart ever needed?

- Seed / claude.dev side: compass-report "Publishing" and claudedev-getting-started give `/plugin marketplace add`, `/plugin install`, `/reload-plugins`, and claude.dev adds "If it doesn't show up, restart Claude Code."
- Official side: docs-plugins-loading: an auto-updated copy needs `/reload-plugins` to switch hooks, MCP and LSP servers, and monitors need a session restart; a command-source reload that would invalidate the prompt cache asks for `/reload-plugins --force`.
- Verdict: consistent, not a conflict in substance, but the seed omits the restart fallback and the cache caveat. Flows in this lane include both.

### X-LIF-05: Official example code lags the build it ships for

- docs-mods-create says the engine lays types at `.claude-plugin/types/` and adds a root `tsconfig.json` that extends it. code-modernization 1.0.0 `tsconfig.json` includes `.claude/types`, an older location, and `tests/mount.test.ts` reaches `$.ui.mount` through a cast with the comment "`$.ui.mount` is newer than the declarations `tsc` reads".
- Verdict: not a contradiction of fact but evidence that even Anthropic's shipped plugin trails the typings by a release or more. Supports the Version Pin Policy (C-LIF-059). The capture is also incomplete: its tests import `./fixtures/*` and `../hooks/reader/*` files that are not in `.raw/captures/official-mods/code-modernization-1.0.0/`, so those tests cannot be run from the capture.

### X-LIF-06: Seed report says hooks.json with unknown keys may be dropped by older versions

- Seed side: compass-report: "older Claude Code versions 'can drop an entire hooks.json that contains keys they do not recognise' (vanja.io)", flagged by the seed itself as unverified on 2.1.287.
- Official side: no docs capture addresses mixed-version `hooks.json`. The #91870 thread has requests that an unknown `modules` key be skipped, not drop the file (sidhartha1s, https://github.com/anthropics/claude-code/issues/91870#issuecomment-5536927938, 2026-09-04).
- Verdict: unresolved. Out of this lane's verification reach (needs an old binary). Recorded as an open gap, no claim made.

## Security and governance

Each entry names both sides, the evidence, and which source wins under the brief's evidence ranking (official docs and 2.1.288 typings first, independent research fifth, seed report last). Local static probes are cited as `secgov-validate-probes` (tool output from 2.1.288 itself).

### 1. Are mods on by default? (Pluto vs docs)

- **Side A:** Pluto says function hooks are "currently gated behind CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1" and that the feature "is currently off unless its environment-variable gate is enabled" (pluto-function-hooks, "Current Status" and "If you administer Claude Code"; tested pre-release 2.1.274).
- **Side B:** Mods require 2.1.287 or later "and they're on by default"; 2.1.287 and later ignore the variable, so setting it to `0` does not keep mods off (docs-mods-overview, "Turn mods on or off"; docs-mods-admin).
- **Winner:** docs (rank 1). Pluto described a pre-release state. Practical impact: an admin who followed Pluto's or early-access advice and set the variable to `0` has mods on. Claims: C-SEC-030, C-SEC-063.

### 2. Is `$.model.classify` documented? (seed vs reference and typings)

- **Side A:** "`classify` is undocumented, and its billing is my inference" (compass-report, section 4).
- **Side B:** The reference lists `classify` in the `$.model` row (docs-mods-reference, "Mods API methods"); the typings document it as one completion over `$.model.complete` with a fixed classifier prompt (types 2.1.288 L2434-2452).
- **Winner:** reference and typings. Only the billing statement remains inference (by construction it is a `complete` call, which the docs say uses the user's plan or API key). Claims: C-SEC-039, C-SEC-061.

### 3. Does a "disposable project" isolate a dynamic trial? (seed vs docs)

- **Side A:** Audit step 9: "Load it once with `--plugin-dir` in a disposable project with no secrets" (compass-report, section 4).
- **Side B:** A mod reads and writes files "anywhere your user account can" and reads environment variables and settings (docs-mods-overview, "What a mod can reach"); absolute paths are used as given (types 2.1.288 L3009-3014); a pre-release test read the Claude Code credential file and full prompt history (pluto-function-hooks, Risk 1).
- **Winner:** docs. A project folder bounds nothing. Resolved in [[Read Only Audit Decision]]: dynamic trials need a separate OS account or VM. Claim: C-SEC-062.

### 4. What does sec-default restrict? (launch blog vs admin page)

- **Side A:** sec-default "stops mods that users install from doing risky things, like overriding your permission deny rules" (blog-mods-launch).
- **Side B:** The guard protects managed hooks, the system prompt, managed instructions, settings reads, and managed MCP tools, and deny rules; otherwise "Everything else is allowed. The guard adds no other restrictions" (docs-mods-admin, "Know what happens by default").
- **Winner:** admin page (more specific, same publisher). Readers of the blog may over-trust the guard; a user mod can still read, write, fetch, run, rewrite prompts, and approve calls an `ask` rule would prompt for. Claim: C-SEC-019.

### 5. Can `$` be passed to a helper? (#91870 pre-release test vs 2.1.288 validate)

- **Side A:** "passing `$` to a helper ... refuse the load" (gh-issue-91870, @deafsquad, issuecomment-5542444779, pre-release build).
- **Side B:** On 2.1.288, a module calling `go($)` where `go` calls `api.http.fetch` validated and reported `calls: $.http.fetch (via go)` (secgov-validate-probes, Probe 2).
- **Winner:** the 2.1.288 tool output (current version; the thread comment predates release). The scanner now follows `$` into helpers. Claim: C-SEC-008 (SINGLE-SOURCE: one local test).

### 6. Is the reach-level scan stale? (seed vs scanner README)

- **Side A:** karanb192's "last snapshot I saw was 2026-09-15 against 2.1.272, so it is stale" (compass-report, section 4).
- **Side B:** README at commit 59a9911 (2026-10-02): "As of 2026-10-02, scanned against Claude Code 2.1.287: 359 mods" (secgov-karanb192-awesome-readme).
- **Winner:** README (pinned primary). Claim: C-SEC-051.

### 7. Does the reach level reflect `process.spawn` and `session.send`? (scanner rules vs admin risk table)

- **Side A:** `tools/grade.mjs` has no rule for `$.process.spawn` (falls to L1 `other`) and grades `$.session.send` and `$.session.append` at L0 through its catch-all `session` rule (secgov-karanb192-grade-mjs).
- **Side B:** The admin page lists `$.process.run, $.process.spawn` together as "Starts programs as the user" and lists `$.session.send` as a call to look for (docs-mods-admin, "Review what a mod can do").
- **Winner:** admin page for risk meaning. The scanner's level under-reports these calls; this brain re-grades both as L2 ([[Reach Levels]]). Claim: C-SEC-050.

### 8. Does `claude plugin details` show a mod's hooks? (Pluto vs plugin security page) UNRESOLVED

- **Side A:** On 2.1.274, `plugin details` reported a mod hooking four events as "Hooks (0)" and "~0 tokens" (pluto-function-hooks, Risk 2).
- **Side B:** The plugin security page says `plugin details` prints a `Component inventory` listing "hooks with each hook's event" (docs-plugins-security, "Review a plugin before you install"). It does not say whether function hooks are included; the mods pages point reviewers to `claude plugin validate` instead (docs-mods-overview; docs-mods-admin).
- **Status:** unverified on 2.1.288. Running `details` on an uninstalled mod needs `--plugin-dir`, which this lane does not run. Until checked, rely on validate. Claim: C-SEC-052.

### 9. Are `AskUserQuestion` option labels protected? (Pluto vs 2.1.288 docs and typings) UNRESOLVED

- **Side A:** Pluto observed the engine restoring the model's original option labels after a mod rewrite, while question text and option descriptions stayed editable (pluto-function-hooks, Risk 3).
- **Side B:** The 2.1.288 typings say only that a rewrite of `questions` "must still fit the tool's schema or the original is drawn" (types 2.1.288 L9113-9128); the interface page says a mod can change the dialog (docs-mods-interface). Neither mentions label restoration. The seed report repeats Pluto's point as confirmed (compass-report, section 4).
- **Status:** unverified on 2.1.288. Treat question wording as mod-controllable and do not rely on labels. Claim: C-SEC-055.

### 10. Which admin control should stop user mods? (Pluto vs admin page) SUPERSEDED

- **Side A:** Pluto recommends `disableAllHooks` or `allowManagedHooksOnly` (pluto-function-hooks, "If you administer Claude Code").
- **Side B:** The admin page adds `allowManagedModsOnly` as the targeted control and warns that managed `disableAllHooks` also stops managed `PreToolUse` hooks from blocking (docs-mods-admin, "Choose how much to allow").
- **Winner:** admin page. Pluto's controls still work but are wider than needed. Claims: C-SEC-023, C-SEC-028.

## Ecosystem

Seed report (compass-report) and community claims checked against official docs, the 2.1.288 typings and source at pinned SHAs. Retrieved 2026-10-03.

### 1. Seed: the official mods directory could not be fetched, descriptions came from search snippets

- Seed: "GitHub blocks automated fetching of this directory" (compass-report section 2).
- Evidence: `gh api repos/anthropics/claude-code/contents/mods` returned the README, four mod folders, `tsconfig.json` and `types/` at SHA 1c229fc (2026-10-02). All four mods were read statically (eco-gh-anthropics-mods).
- Winner: eco-gh-anthropics-mods. The seed's four one-line descriptions hold up (C-ECO-006, C-ECO-010, C-ECO-015).

### 2. Official mods README vs official docs on whether mods are on by default

- `mods/README.md`: "Early access: hooks modules load only where function hooks are enabled" (eco-gh-anthropics-mods).
- docs-mods-overview L97, L112: mods need v2.1.287+, are on by default, and the flag is ignored.
- Winner: docs-mods-overview (rank 1). The repo README is stale text (C-ECO-002).

### 3. Seed: the awesome list is stale and nothing re-scans on 2.1.287

- Seed: "31 mods in 92 repos as of 2026-09-15" and "None of these lists re-scans on 2.1.287 yet".
- Evidence: awesome-claude-code-mods README at 59a9911: "As of 2026-10-02, scanned against Claude Code 2.1.287: 359 mods in 373 candidate repos"; `data/mods.json` has `claudeVersion: "2.1.287"`, generated 2026-10-02T02:16Z.
- Winner: eco-gh-awesome-claude-code-mods (C-ECO-047). Note: `data/mods.json` holds 437 mod rows while the README says 359; the README count appears to dedupe (catalogue copies), unverified.

### 4. Seed: Arunjay4213 is a "trio"

- Seed: "context-lens / quota-meter / token-ledger".
- Evidence: the tree at d4fffd7 has a fourth plugin, budget-guard, which refuses tool calls and can `$.turn.abort` (C-ECO-031, C-ECO-032). GitHub reports no license; the README says MIT.
- Winner: eco-gh-arunjay4213.

### 5. Seed: hamzafer ships 11 mods

- Seed: "hamzafer/claude-code-mods (11 mods)".
- Evidence: README at 543abfa says 13 mods; 13 `hooks.json` files exist (C-ECO-040).
- Winner: eco-gh-hamzafer.

### 6. Seed: use "Blast Radius pattern with `$.ui.ask`"

- Seed (ideas table rank 7): stack guards via "Blast Radius pattern with `$.ui.ask` and `.catch` fail-closed".
- Evidence: the official blast-radius holds the call with a Pane, Proceed and Cancel buttons and a `$.process.run(["sleep", "0.25"])` loop; it never calls `$.ui.ask` and has no `.catch` hook (eco-gh-playground-mods, C-ECO-021). docs-mods-events L175 does recommend waiting inside `$.ui.ask`.
- Winner: both patterns are valid; the seed misattributes `$.ui.ask` to Blast Radius. The sleep loop exists because `$.clock.sleep` counts against the 10 s hook budget (docs-mods-reference L245).

### 7. Getting-started advice vs the published token-weather sample

- claudedev-getting-started L448: keep data in `$.state`, not in module variables.
- The playground's `token-weather.mjs` at 569c528 keeps `let readings = []` at module level; blast-radius keeps `let held = null`.
- Winner: neither is wrong for these samples (state loss on reload is cosmetic), but the post and the sample disagree; follow the post and docs-mods-interface L699 for anything you build (C-ECO-022).

### 8. Community install instructions vs 2.1.287 docs (obsolete flag)

- cctop, Arunjay4213, cc-pr-tracker, karanb192/claude-code-mods and cache-tax still tell users to set `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`, three of them in `~/.claude/settings.json` `env`.
- docs-mods-overview L112 and docs-mods-admin L51: 2.1.287+ ignores it at any value.
- Winner: docs. The flag is harmless on 2.1.287+ but a `0` does not turn mods off (C-ECO-056).

### 9. Seed: cctop "Not yet confirmed on 2.1.287"

- Seed: CI contract job on 2.1.284.
- Evidence: `TESTED_WITH = '2.1.284'` in `plugin/hooks/model.ts`; CI installs `@latest` (so it now runs against 2.1.288), and the scanner records cctop as passing validate on 2.1.287 (C-ECO-027, C-ECO-032 row data).
- Status: still no author statement of a 2.1.287+ test; static validation only. Contested, not contradicted.

### 10. Release channel: "2.1.287 or later" vs what the stable channel ships

- Docs and every community README say mods need 2.1.287+.
- npm dist-tags on 2026-10-03: `stable` is 2.1.285 (eco-npm-dist-tags). Homebrew `claude-code` tracks stable (eco-docs-setup).
- Inference (C-ECO-054, unverified): stable-channel and default Homebrew users do not yet have mods on by default. Not a source conflict, but every install line in this lane silently assumes the latest channel.

## Patterns and ideas

Seed report (`compass-report`, `.raw/sources/compass-report-2026-10-02.md`) and pre-release thread reports versus the 2.1.288 docs and typings. The higher-ranked source wins per the lane brief.

| # | Seed or thread says | Official or typings say | Winner | Evidence |
|---|---|---|---|---|
| X1 | "`claude plugin test` can't set `userConfig` values" (compass-report L221, citing @lperezmo on #91870, 2.1.282, c5827373997) | `TestOptions.options` holds the plugin under test's `userConfig` values, with example `test('greets', { options: { greeting: 'yo' } }, body)` (types 2.1.288 L14924-14946). The docs test page does not mention it. | Typings. Gap closed on 2.1.288, runtime not yet run (C-PAT-028, C-PAT-029) | |
| X2 | `$.model.classify` "is undocumented, and its billing is my inference" (compass-report L304, L456) | Typings document it: one completion over `$.model.complete` with a fixed classifier prompt, default small fast model, no usage returned (types 2.1.288 L2436-2452, L1218-1226). Docs: `$.model` calls use the user's plan or API key (docs-mods-api L97) | Typings for mechanics; billing remains an inference, now strong (C-PAT-030, C-PAT-031) | No staff statement in #91870 (c5540419526 unanswered) |
| X3 | Migration table maps classic `Stop` to `turn.complete` (compass-report L154) | `turn.complete` can return only `next(e)` or `{ text }` (docs-mods-reference); a `classic.Stop` hook can return `{ block }` (types 2.1.288 L1103-1108, L1205-1215) | Docs and typings. Use `classic.Stop` when the old hook blocked to keep Claude going (C-PAT-058) | |
| X4 | Gap list includes `ui.selection` and draft decorations in `prompt.edit` (compass-report L372-375) | `$.ui.selection()`, a `ui.selection` event, and `decorations` on `prompt.edit` results exist (types 2.1.288 L2382, L6591, L8062-8073) | Typings. Only subagent compaction of that list is still missing (C-PAT-045, C-PAT-047) | |
| X5 | Holds can use "a loop of short `$.process.run(["sleep","0.25"])` calls as Blast Radius does" as an equal alternative (compass-report L247) | Docs teach `$.ui.ask` for holds and warn that waits on your own promise count against the budget (docs-mods-events) | Docs on the recommended shape; the loop is valid but heavier (C-PAT-050) | |
| X6 | On 2.1.272, `$.model.complete` defaulted to 256 tokens, had no `effort` or `timeoutMs`, and returned a bare string (#91870 c5676619802, c5541527253) | Default 1024, up to 64,000; `effort`, `timeoutMs`, and `usage` present (types 2.1.288 L5792-5877; docs-mods-reference Limits) | Typings (C-PAT-033, C-PAT-034) | Pre-release report superseded |
| X7 | Passing `$` to a helper refuses the load (#91870 c5542444779, 2.1.260) | 2.1.288 validate traces helpers: a probe module calling `go($)` validates and reports `calls: $.http.fetch (via go)` (secgov-validate-probes, C-SEC-008) | Direct 2.1.288 run. Computed `$[expr]` access is still refused per staff c5539280904 (C-PAT-060) | |
| X8 | WebAssembly "is in my plans" (staff @poteat, #91870 c5702935782) | No `WebAssembly`, "deliberately"; compiled code goes through `$.process.run` (types 2.1.288 L13762-13770) | Typings for 2.1.288; staff intent may still change it (C-PAT-046) | |
| X9 | Seed ranks git-state band 2nd and cache-break detector 3rd (compass-report L384-386) | Not a factual conflict: re-ranked in Ranked Build Ideas because the built-in `/diff` pane already covers part of the git band | Judgment, recorded as such | |
| X10 | Cache-miss cost "12.5x a hit" and up to 80x (compass-report L386, secondary blogs) | Docs only state that changing text invalidates the cache | Unresolved: multipliers not verified in this lane | Treat as unverified |

## Caveats

- Lane entries are kept as written on 2026-10-03; later corrections live in the claim ledger and the notes, which cite the entry they supersede.
- A contradiction resolved by the typings holds for Claude Code 2.1.288 only; re-check each on the next release ([[Versioning and API Drift]]).
