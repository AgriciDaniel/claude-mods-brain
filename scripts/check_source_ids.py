#!/usr/bin/env python3
"""Gate: every source id a wiki note cites in frontmatter `sources:` exists in the ledger.

Ids are bare slugs (e.g. `docs-mods-events`); paths (`.raw/...`, `references/...`),
wikilinks, and canon file names are not ids and are skipped. The ledger holds public
sources under `sources` and local evidence under `local_captures`; both count.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
INTERNAL = {"claim-ledger", "source-ledger"}  # the ledgers themselves, cited as provenance
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def cited_ids(text: str) -> list[str]:
    m = FM_RE.match(text)
    if not m:
        return []
    ids, in_sources = [], False
    for line in m.group(1).splitlines():
        if re.match(r"^sources:\s*$", line):
            in_sources = True
            continue
        if in_sources:
            item = re.match(r'^\s+-\s+"?([^"]*)"?\s*$', line)
            if not item:
                in_sources = False
                continue
            value = item.group(1).strip().split()[0] if item.group(1).strip() else ""
            if ID_RE.match(value):
                ids.append(value)
    return ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--wiki", default="wiki")
    args = parser.parse_args(argv)
    ledger = json.loads((ROOT / "references/source-ledger.json").read_text(encoding="utf-8"))
    known = {s["id"] for s in ledger.get("sources", [])} | {s["id"] for s in ledger.get("local_captures", [])}
    missing: dict[str, list[str]] = {}
    for note in sorted((ROOT / args.wiki).rglob("*.md")):
        for sid in cited_ids(note.read_text(encoding="utf-8", errors="replace")):
            if sid not in known and sid not in INTERNAL:
                missing.setdefault(sid, []).append(note.relative_to(ROOT).as_posix())
    for sid, notes in sorted(missing.items()):
        print(f"unknown source id {sid!r} cited by {len(notes)} note(s), e.g. {notes[0]}")
    print("source-ids gate:", "FAIL" if missing else "PASS", f"({len(known)} ledger ids, {len(missing)} unknown)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
