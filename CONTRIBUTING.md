# Contributing

Corrections and new sources are the most useful contributions. Mods change with every Claude Code
release, so a dated, sourced correction is worth more than a new note.

## Reporting a wrong or stale fact

Open an issue with:

1. The note and the sentence.
2. Your Claude Code version (`claude --version`).
3. The source that shows the correct fact: an official docs URL, a line range in the type definitions
   Claude Code writes beside a mod (`.claude-plugin/types/claude-code/index.d.ts`), or a pinned commit.

## Changing notes

- Keep the note shape in `wiki/meta/CONVENTIONS.md`: frontmatter with `tested_on`, a confidence tag on
  every recommendation, and a Sources section with retrieval dates.
- Cite, don't copy: quotes of 15 words or fewer, with attribution, or a labelled paraphrase.
- Add or update the matching row in `references/claim-ledger.md` and, for a new source, an entry in
  `references/source-ledger.json`.
- No em or en dashes.

## Changing code

```bash
python3 tests/test_adapters.py
python3 scripts/lint_vault.py --vault .
python3 scripts/check_no_em_dash.py
python3 scripts/check_source_ids.py
```

All four must pass; CI runs them on every pull request. Tests use synthetic fixtures only. Never add a
real third-party mod, a credential, or a session transcript to `tests/fixtures/`.

## Safety

Do not submit instructions that install, enable, or load a mod without the reader's explicit choice,
and keep the isolation advice intact: a runtime trial belongs in a separate OS user or a VM.
