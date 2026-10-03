---
name: mods-brain
description: >
  Answer questions about Claude Code mods (function-hook plugins: register(on, options), the $ mods API,
  events, render sites, limits) from this source-cited vault; help build a band, pane, guard, or command
  mod; migrate settings hooks; audit a third-party mod before install; or re-verify after a Claude Code
  release. Triggers: "claude code mod", "function hooks", "mods api", "audit this mod", "is this mod safe".
---

# Claude Mods Brain

Read `CODEX.md`, `wiki/hot.md`, and `wiki/index.md`, then the note for the task. Act as
`agents/mods-secretary.md`: answer from the notes, cite the note plus the official page or the type
definitions line range, name the Claude Code version the answer holds for, and never install, enable,
or load a mod without the user's approval.

Tools (Python 3.10+, no dependencies):

```bash
python3 -m mods_brain.cli audit-mod <plugin-dir> --origin <owner/repo@sha> --tested-on <version> --date YYYY-MM-DD
python3 -m mods_brain.cli surface --capture <dir-with-claude-code/index.d.ts> --out <surface.json>
python3 -m mods_brain.cli drift --old <old-surface.json> --new <new-surface.json> --out <drift.json>
```
