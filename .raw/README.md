# .raw

Immutable source captures live here on your machine, not in the published repo. The published notes
cite original URLs and dated retrievals in `references/source-ledger.json`.

To capture your own, for example before refreshing the brain after a Claude Code release:

```bash
mkdir -p .raw/captures/docs-$(date +%F)
curl -sfL https://code.claude.com/docs/en/plugins/mods/reference.md -o .raw/captures/docs-$(date +%F)/plugins-mods-reference.md
```

Your own copy of the mod type definitions appears beside any mod you load, in
`.claude-plugin/types/claude-code/index.d.ts`; see `wiki/flows/Research Refresh Workflow.md`.
`.raw/captures/` and `.raw/sources/` are gitignored.
