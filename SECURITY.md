# Security

This repository contains notes and offline tools. The tools only read files: `scripts/scan_mod.py`
reads a mod's source without running it, and no script loads a mod, calls a network service, or reads
credentials.

## Reporting

If you find a security problem in the tools, or advice in the notes that would put a reader at risk
(for example, a recipe that loads an untrusted mod without isolation), please open a private security
advisory on this repository instead of a public issue.

## A reminder about mods themselves

Claude Code mods are not sandboxed: a mod runs with your user permissions, can read files, run
programs, reach the network, approve tool calls, and spend your usage. A clean static scan or a passing
`claude plugin validate` is not a safety verdict. Use `wiki/flows/Audit a Third-Party Mod Flow.md`
before installing anything.
