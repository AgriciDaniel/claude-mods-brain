# Agent instructions

This repository is a source-cited knowledge vault about Claude Code mods, tested on Claude Code 2.1.288.
Agents working here should act as `agents/mods-secretary.md`.

## Read order

1. `CODEX.md`, then `wiki/hot.md`, then `wiki/index.md`.
2. `wiki/meta/CONVENTIONS.md` before editing any note.
3. The note for the task; API questions start at `wiki/deliverables/Mods API Cheatsheet.md`.

## Rules

- Run `claude --version` first. If it is newer than the `tested_on` in `wiki/hot.md`, say that API notes
  may be stale and follow `wiki/flows/Research Refresh Workflow.md`.
- The type definitions Claude Code writes beside a mod outrank the docs for names and shapes on that
  build; the docs outrank everything else for intent.
- Never install, enable, or load a mod, or run `claude --plugin-dir`, without the user's explicit
  approval. A passing `claude plugin validate` or a clean `scripts/scan_mod.py` report is evidence, not
  a safety verdict.
- Every new claim gets a row in `references/claim-ledger.md`; every new source gets an entry in
  `references/source-ledger.json` with retrieval and refresh dates.
- No credentials, session transcripts, or absolute home paths in notes. No em or en dashes.

## Verification

```bash
python3 tests/test_adapters.py
python3 scripts/lint_vault.py --vault .
python3 scripts/check_no_em_dash.py
python3 scripts/check_source_ids.py
```
