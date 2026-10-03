#!/usr/bin/env python3
"""Render wiki/sources/research-pack-claude-mods.md from the ledgers and captures.

The research pack is the dated citation index of the brain: every ledger source
with its URL, publisher, published and retrieved dates, refresh due date, lanes,
and the claims it supports; every #91870 comment the vault cites, with its date
from the thread capture; and the local captures that have no public URL.
Regenerate after any ledger change; never edit the output by hand.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMENT_URL = re.compile(r"https://github\.com/anthropics/claude-code/issues/91870#issuecomment-(\d+)")
CAPTURE = ROOT / ".raw/captures/web-2026-10-03/gh-issue-91870.md"
LANE_TITLES = {
    "api-and-events": "API and events",
    "lifecycle": "Lifecycle: build, test, publish, re-verify",
    "security-governance": "Security and governance",
    "ecosystem": "Ecosystem and catalog",
    "patterns-and-ideas": "Patterns and ideas",
}
RELATED = [
    "Source Manifest Guide", "Source Intake Workflow", "Research Refresh Workflow", "Claim Verification Flow",
    "Mods API Cheatsheet", "Mod Catalog", "Mod Security Audit Checklist", "Versioning and API Drift",
    "Claude Code mods documentation set (Anthropic)", "Mods design thread, anthropics claude-code issue 91870",
]


def comment_dates() -> dict[str, tuple[str, str]]:
    """Map comment id to (author, ISO date) from the thread capture."""
    out: dict[str, tuple[str, str]] = {}
    if not CAPTURE.is_file():
        return out
    pattern = re.compile(r"## Comment by @(\S+) at (\d{4}-\d{2}-\d{2})T[^\n]*\n\nURL: https://github\.com/anthropics/claude-code/issues/91870#issuecomment-(\d+)")
    for author, day, cid in pattern.findall(CAPTURE.read_text(encoding="utf-8")):
        out[cid] = (author, day)
    return out


def cited_comments(wiki: Path) -> dict[str, list[str]]:
    cites: dict[str, set[str]] = defaultdict(set)
    for note in wiki.rglob("*.md"):
        if note.name.startswith("research-pack-"):
            continue
        for cid in COMMENT_URL.findall(note.read_text(encoding="utf-8", errors="replace")):
            cites[cid].add(note.stem)
    return {k: sorted(v) for k, v in cites.items()}


def render(date: str, exclude: set[str] | None = None, wiki: Path | None = None) -> str:
    exclude = exclude or set()
    ledger = json.loads((ROOT / "references/source-ledger.json").read_text(encoding="utf-8"))
    sources = ledger["sources"]
    by_lane: dict[str, list[dict]] = defaultdict(list)
    for s in sources:
        lanes = s.get("lanes") or ["unassigned"]
        by_lane[lanes[0]].append(s)
    dates = comment_dates()
    cites = cited_comments(wiki or ROOT / "wiki")
    lines = [
        "---",
        'type: "source"',
        'title: "Research Pack: Claude Code Mods"',
        'domain: "Claude Code mods"',
        'status: "evergreen"',
        f'created: "{date}"',
        f'updated: "{date}"',
        'tested_on: "2.1.288"',
        "tags:",
        '  - "#domain/claude-code-mods"',
        '  - "#type/source"',
        '  - "#confidence/evidence-based"',
        'confidence: "evidence-based"',
        'generated_by: "scripts/render_research_pack.py"',
        "related:",
        *[f'  - "[[{r}]]"' for r in RELATED],
        "source_urls:",
        f'  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved {date})"',
        "sources:",
        '  - "references/source-ledger.json"',
        '  - "references/claim-ledger.md"',
        "---",
        "",
        "# Research Pack: Claude Code Mods",
        "",
        f"The dated citation index for this brain, generated on {date} from `references/source-ledger.json` "
        f"({len(sources)} public sources), the local captures list ({len([c for c in ledger.get('local_captures', []) if c['id'] not in exclude])}), and every "
        f"#91870 comment the vault cites ({len(cites)}). Official docs and the typings written by Claude Code 2.1.288 outrank "
        "everything else; the seed report is a lead list only. #confidence/evidence-based",
        "",
        "How sources enter: [[Source Intake Workflow]]. How they are kept current: [[Research Refresh Workflow]]. "
        "How a claim is checked: [[Claim Verification Flow]]. Manifest mechanics: [[Source Manifest Guide]].",
        "",
    ]
    for lane in [*LANE_TITLES, *sorted(set(by_lane) - set(LANE_TITLES))]:
        rows = sorted(by_lane.get(lane, []), key=lambda s: (s.get("source_type") != "official", s["id"]))
        if not rows:
            continue
        lines += [f"## {LANE_TITLES.get(lane, lane)}", ""]
        for s in rows:
            conf = {"med": "medium"}.get(s.get("confidence"), s.get("confidence"))
            pin = f", pinned `{s['pinned_sha'][:7]}`" if s.get("pinned_sha") else ""
            lines.append(
                f"- **{s.get('title', s['id'])}** ({s.get('publisher', 'unknown')}, {s.get('source_type')}, confidence {conf}{pin}). "
                f"{s['url']} . Published {s.get('published', 'unknown')}; retrieved {s.get('retrieved')}; refresh due {s.get('refresh_due')}. "
                f"Id `{s['id']}`; supports {len(s.get('claims', []))} claims; lanes: {', '.join(s.get('lanes', []))}."
            )
        lines.append("")
    lines += [
        "## Design thread comments cited in the vault",
        "",
        "Each row is a comment on anthropics/claude-code#91870, dated from the full thread capture "
        "(`.raw/captures/web-2026-10-03/gh-issue-91870.md`). Thread comments are practitioner evidence unless an Anthropic "
        "staff member states a shipped behaviour; see [[Mods design thread, anthropics claude-code issue 91870]].",
        "",
        "| Comment | Author | Date | Cited by |",
        "|---|---|---|---|",
    ]
    for cid in sorted(cites, key=lambda c: dates.get(c, ("", "9999"))[1] + c):
        author, day = dates.get(cid, ("unknown", "unknown"))
        notes = ", ".join(f"[[{n}]]" for n in cites[cid][:3])
        lines.append(f"| https://github.com/anthropics/claude-code/issues/91870#issuecomment-{cid} | @{author} | {day} | {notes} |")
    lines += [
        "",
        "## Local captures without a public URL",
        "",
        "Evidence produced on this machine (CLI runs, static scans, and a private seed report; not redistributed). "
        "Cited by id in claims, kept out of the public source list.",
        "",
    ]
    for c in ledger.get("local_captures", []):
        if c["id"] in exclude:
            continue
        lines.append(f"- `{c['id']}`: {c.get('title', '')} ({c.get('source_type')}), retrieved {c.get('retrieved')}; capture `{c.get('capture', '')}`.")
    lines += [
        "",
        "## Caveats",
        "",
        "- Mods are days old (shipped in 2.1.287 on 2026-10-01). Every source is due for refresh on or before its `refresh_due`, and sooner when `claude --version` moves; see [[Versioning and API Drift]].",
        "- Thread and community sources are lower in the evidence order than docs and typings; contradictions are recorded in the notes that use them.",
        "",
        "## Related",
        "",
        "[[Mods API Cheatsheet]], [[Mod Catalog]], [[Mod Security Audit Checklist]], [[Claude Code mods documentation set (Anthropic)]].",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", required=True)
    parser.add_argument("--out", default="wiki/sources/research-pack-claude-mods.md")
    parser.add_argument("--wiki", default=str(ROOT / "wiki"), help="wiki folder whose citations the pack indexes")
    parser.add_argument("--exclude-local", default="", help="comma-separated local capture ids to leave out (public edition)")
    args = parser.parse_args(argv)
    out = ROOT / args.out
    out.write_text(render(args.date, {i for i in args.exclude_local.split(",") if i}, Path(args.wiki)), encoding="utf-8")
    text = out.read_text(encoding="utf-8")
    print(f"{args.out}: {len(re.findall(r'https?://', text))} urls, {len(re.findall(r'20[12][0-9]-[0-9]{2}-[0-9]{2}', text))} dates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
