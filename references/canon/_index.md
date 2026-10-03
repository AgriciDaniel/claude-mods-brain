# Canon index: Claude Mods Brain

Six canon works, all from local captures retrieved 2026-10-03. Official docs and the 2.1.288 typings outrank everything else here; the #91870 thread records design intent; Pluto is independent and pre-release.

001 | Claude Code mods documentation set | Anthropic | 2026 | evidence-based | Takeaway: A mod is an unsandboxed, statically inspectable middleware chain in front of Claude Code, and the generated types for your build are the final authority.
002 | Customize Claude Code with mods | Anthropic | 2026 | evidence-based | Takeaway: Mods let users rewrite events, draw UI, and replace built-ins such as /diff, governed by plugin controls and the sec-default guard.
003 | Getting started with Claude Code mods | Addy Osmani | 2026 | practitioner | Takeaway: Describe a mod to Claude or build Token Weather by hand, and keep state in $.state, layout in e.props, and hard blocks in permission rules.
004 | Mods - make Claude 10x more extensible (issue 91870) | @poteat and community | 2026 | practitioner | Takeaway: The design thread explains the Koa-style onion, the $ side-effect contract, and the tier order, though several proposals there never reached the docs.
005 | Inside Claude Code Function Hooks: The Trust Problem Behind Claude Mods | Ehud Melzer (Pluto Security) | 2026 | contested | Takeaway: The $ model is sound, but consent is uninformed and next rewrites and fetched code evade the scanner, so treat each mod as an untrusted binary.
006 | Claude Code plugins and hooks documentation | Anthropic | 2026 | evidence-based | Takeaway: Plugins run as the user and are governed at the marketplace and managed-settings layer, while settings hooks merge in parallel rather than as a chain.
