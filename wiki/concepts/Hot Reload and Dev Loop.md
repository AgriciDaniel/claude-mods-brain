---
type: "concept"
title: "Hot Reload and Dev Loop"
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
lane: "lifecycle"
related:
  - "[[Plugin Validate]]"
  - "[[Testing Kit]]"
  - "[[State Store and Module Variables]]"
  - "[[Mod Anatomy]]"
  - "[[Versioning and API Drift]]"
  - "[[Build a Status Band Flow]]"
  - "[[Build a Pane Flow]]"
  - "[[Marketplaces and Distribution]]"
  - "[[userConfig and Plugin Options]]"
  - "[[Pitfalls Playbook]]"
source_urls:
  - "https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)"
  - "https://code.claude.com/docs/en/plugins/loading (retrieved 2026-10-03)"
sources:
  - "docs-mods-create"
  - "docs-mods-troubleshoot"
  - "docs-mods-reference"
  - "docs-plugins-loading"
  - "lif-plugin-authoring-skill"
  - "gh-issue-91870"
---

# Hot Reload and Dev Loop

A mod is developed against a folder Claude Code watches, so a save reloads the hooks module in the running session without a restart. There are two watched routes: a folder you pass with `claude --plugin-dir`, and the per-session `~/.claude/dev-mods/<session-id>` folder that the built-in `plugin-authoring` skill writes into after you approve hot reloading (C-LIF-004, C-LIF-006). A reload is a fresh load, so `register` and `session.start` run again and module variables reset, while `$.state` and `$.store` survive (C-LIF-007). Never develop against an installed copy: installs run from a version-keyed cache (C-LIF-010).

## The three ways a mod reaches a session while you build it

| Route | How it starts | Watched? | Lifetime | Source |
|---|---|---|---|---|
| Claude writes it | Ask in a session; the `plugin-authoring` skill writes to `~/.claude/dev-mods/<session-id>/<mod>/` and the engine asks "Enable hot reloading for this session?" | Yes, once you choose `Enable for this session` | That session only; folder deleted after `cleanupPeriodDays` | C-LIF-004, C-LIF-005 |
| `--plugin-dir` | `claude --plugin-dir ~/mods/my-mod` (repeat the flag for several) | Yes, in an interactive session | That session | C-LIF-006 |
| `CLAUDE_CODE_PLUGIN_DIRS` | Env var or `env` in `~/.claude/settings.json`, for hosts that take no flag (Desktop, SDK) | Interactive yes; headless only with `CLAUDE_CODE_PLUGIN_DIR_WATCH=1` | Every session that reads the variable | C-LIF-011 |

A fourth route, a plugin folder auto-loaded from `~/.claude/skills/<name>`, is described as watched by the 2.1.288 skill, but a community report on 2.1.270 says it served the stale module until restart (C-LIF-013).

> [!contradiction]
> The bundled skill (2.1.288) says a skills-folder plugin is watched like a `--plugin-dir` folder. lperezmo on #91870 (2.1.270, comment 5670161416) found it did not reload. The skill wins for current builds as the rank-1 source, but it is single-source and untested since 2.1.287, so use `--plugin-dir` for development (X-LIF-02).

## What a reload does

The skill puts it plainly: "A reload is a fresh load of the module" (lif-plugin-authoring-skill). Concretely (C-LIF-007):

- `register(on, options)` runs again in a fresh environment; hooks are re-registered from scratch.
- `session.start` fires again, so commands and tools are re-registered. That is why registering in `session.start` is safe across reloads.
- Module-level `let` values start over. The tutorial's `/tally` counter resets to 0 on every save (docs-mods-create).
- Timers from `$.clock.every` and `$.clock.after` in the old environment are dropped; the new module starts its own.
- `$.state` (session scoped) and `$.store` (cross-session, on disk) keep their values because the host owns them.

Pick storage by how long a value must live, which [[State Store and Module Variables]] covers in depth:

| Keep it in | Survives a reload | Survives `/clear`, `/resume`, `/branch` | Survives a restart |
|---|---|---|---|
| Module variable | No | No | No |
| `$.state` | Yes | No (reset to defaults; re-seed in `classic.SessionStart`) | No |
| `$.store` | Yes | Yes | Yes |

## When the reload happens

- Saves made by the model during its own turn reload once, when the turn ends, or sooner when a tool or command the plugin registered is about to run, so the turn can try what it wrote (C-LIF-008).
- Saves from your editor reload after the folder goes quiet: a lone save within about a quarter second, a burst of saves once it stops (C-LIF-008, single-source detail).
- `claude -p` always loads fresh, and it cannot show the approval question, so a mod Claude writes under `-p` or `dontAsk` does not load at all (C-LIF-012).
- A reload that fails keeps the last working version running, and the transcript says `reload failed, the previous version stays loaded:` with the reason (C-LIF-009).

## Where the loop reports problems

While a session hot-reloads a folder, the transcript carries one dim line per failure kind naming the plugin, the event and the reason, for example `first-mod: tool.call hook skipped: threw Error: boom` (docs-mods-troubleshoot). A tree that fails validation shows `<plugin>: ui.render (<Component>) refused: <reason>; the engine drew its own`. Outside a hot-reloading session the same lines go only to the debug log (lif-plugin-authoring-skill).

```bash
# Terminal 1: run the session with a debug file
claude --debug-file ./mod-debug.log --plugin-dir ~/mods/first-mod

# Terminal 2: follow only your mod's lines
tail -f ./mod-debug.log | grep first-mod
# A healthy load looks like:
# hooks module first-mod@inline loaded (worker, environment 2, tier user); events: session.start,tool.call,...
```

## The recommended inner loop

1. Keep the source in your own folder (`~/mods/<name>`), never under the cache or a dev-mods folder you want to keep. EVIDENCE-BASED
2. Start `claude --plugin-dir ~/mods/<name>`; the engine writes `.claude-plugin/types/` and a root `tsconfig.json` on that first load (C-LIF-042). EVIDENCE-BASED
3. After each edit, in a second shell run `claude plugin validate ~/mods/<name>` before looking at the session; it is the fastest way to see whether the engine sees the hooks you meant (see [[Plugin Validate]]). EVIDENCE-BASED
4. Type-check with `tsc -p ~/mods/<name>` once the types folder exists. EVIDENCE-BASED
5. Encode the behavior in a `*.test.ts` and run `claude plugin test ~/mods/<name>` (see [[Testing Kit]]). EVIDENCE-BASED
6. Put anything a drawing reads in `$.state`, not a module variable, or every save visibly resets the UI. EVIDENCE-BASED
7. When you are happy, copy a Claude-written mod out of `~/.claude/dev-mods/` before the cleanup period removes it. EVIDENCE-BASED

```bash
mkdir -p ~/mods && cp -r ~/.claude/dev-mods/<session-id>/git-branch ~/mods/git-branch
claude --plugin-dir ~/mods/git-branch
```

## Installed copies do not hot-reload

An installed marketplace plugin is copied into `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` and loaded from there (docs-plugins-loading). Editing your source changes nothing until the computed version changes and the user updates. The one exception is a relative-path plugin in a marketplace added from a local directory, which loads in place and picks up edits at the next session or `/reload-plugins` (C-LIF-051), contested on Desktop (X-LIF-03). Details live in [[Marketplaces and Distribution]].

## Failure modes in the loop

| Symptom | Likely cause | Fix |
|---|---|---|
| Counter resets after every save | Value kept in a module variable | Move it to `$.state` |
| `/mycmd` missing after a save | `$.command.register` threw (name taken) and the rest of `session.start` was skipped (C-LIF-055) | Rename, or register last inside try/catch |
| Edits ignored entirely | Editing the installed copy, or a `-p` run that loaded fresh while the interactive session runs older code | Use `--plugin-dir`; compare with the debug log |
| UI shows engine default | Tree failed validation | Read the `refused:` line |
| Values from `$.state` vanish after `/clear` | `/clear` resets state and `session.start` does not fire | Re-seed in a `classic.SessionStart` hook |

## Caveats

- Debounce timing, early reload before a registered tool runs, and the skills-folder watch come only from the 2.1.288 bundled skill (C-LIF-008, C-LIF-013).
- The approval question can be off for reasons outside your control: an untrusted workspace, `--safe-mode`, `--bare`, `disableAllHooks`, or managed settings (docs-mods-create).
- This lane did not load any mod; reload behavior is documented, not observed here.

## Related

The loop's static check is [[Plugin Validate]] and its automated check is the [[Testing Kit]], combined in the [[Testing Playbook]]. Storage choices come from [[State Store and Module Variables]]; the file layout from [[Mod Anatomy]]. Changing a mod's options reloads it, see [[userConfig and Plugin Options]]. The flows [[Build a Status Band Flow]] and [[Build a Pane Flow]] run this loop end to end, and [[Re-verify After Release Flow]] runs it after an update. Shipping leaves the loop for [[Marketplaces and Distribution]]. Common traps are collected in [[Pitfalls Playbook]], and drift between builds in [[Versioning and API Drift]].

## Sources

- docs-mods-create: https://code.claude.com/docs/en/plugins/mods/create (retrieved 2026-10-03)
- docs-mods-troubleshoot: https://code.claude.com/docs/en/plugins/mods/troubleshoot (retrieved 2026-10-03)
- docs-mods-reference: https://code.claude.com/docs/en/plugins/mods/reference (retrieved 2026-10-03)
- docs-plugins-loading: https://code.claude.com/docs/en/plugins/loading (retrieved 2026-10-03)
- lif-plugin-authoring-skill: `.raw/captures/lanes-2026-10-03/lifecycle/plugin-authoring-skill-2-1-288.md` (retrieved 2026-10-03)
- gh-issue-91870: https://github.com/anthropics/claude-code/issues/91870#issuecomment-5670161416 (retrieved 2026-10-03)
