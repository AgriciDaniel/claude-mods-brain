#!/usr/bin/env python3
"""Regenerate wiki/index.md and every wiki/<folder>/_index.md hub from note frontmatter.

Each entry is `[[Title]] (status, confidence): one-line summary`, where the summary is
the first sentence of the note's answer-first paragraph. Run after adding, renaming,
or rewriting notes; hot.md, overview.md, and log.md stay hand-written.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
SPINE = {"hot.md", "index.md", "overview.md", "log.md", "_index.md"}
FOLDERS = {
    "concepts": ("Concepts Hub", "How Claude Code mods work: the hook chain, events, the `$` API, render sites, state, limits, lifecycle, trust, and the canon folds. Start with [[Mod Anatomy]] and [[Hook Middleware Chain]]."),
    "flows": ("Flows Hub", "Runnable procedures, each with Trigger, Prerequisites, Steps, Outputs, Gates, Failure Modes, and Rollback. Build flows create mods; audit and refresh flows keep the owner safe and current."),
    "deliverables": ("Deliverables Hub", "The outputs people act on: cheatsheet, playbooks, checklist, catalog, policy guide, roadmap, scorecard. Each cites its sources."),
    "entities": ("Entities Hub", "Specific mods and repos: the built-ins, official examples, community mods pinned by SHA, and directories."),
    "platforms": ("Platforms Hub", "The Claude Code distribution surface that decides whether a user has mods at all: release channels and versions."),
    "decisions": ("Decisions Hub", "Recorded decisions and the approval queue: what the brain will and will not do, and what waits for the owner."),
    "reports": ("Reports Hub", "Generated evidence: the API surface per Claude Code build, per-mod audits, the capability matrix, and the weekly release watch. Regenerate, never hand-edit."),
    "sources": ("Sources Hub", "Where evidence lives and how it enters: the research pack (dated citation index) and the manifest guide."),
    "gaps": ("Gaps Hub", "What the brain does not yet know or cannot verify, with what would close each gap."),
    "questions": ("Questions Hub", "Open and answered questions, each with its evidence and the experiment that would settle it."),
    "experiments": ("Experiments Hub", "Probes run or planned against the corpus and the adapters, with results."),
    "meta": ("Meta Hub", "The operating contract: conventions, tag taxonomy, policies, the dashboard, and the start page."),
    "canvases": ("Canvases Hub", "Visual maps of the brain: the mod lifecycle and the event flow."),
}
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def field(fm: str, key: str) -> str:
    m = re.search(rf'(?m)^{key}:\s*"?([^"\n]*)"?\s*$', fm)
    return m.group(1).strip() if m else ""


def summary(body: str) -> str:
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block or block.startswith(("#", "<", "|", "-", ">", "```", "!")):
            continue
        text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", block)
        text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
        text = re.sub(r"#confidence/\S+", "", text).replace("\n", " ")
        m = re.match(r"(.+?[.!?])(\s|$)", text)
        out = (m.group(1) if m else text).strip()
        return out[:220] + ("..." if len(out) > 220 else "")
    return ""


def notes_in(folder: Path) -> list[dict]:
    rows = []
    for path in sorted(folder.glob("*.md")):
        if path.name in SPINE:
            continue
        text = path.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        fm, body = (m.group(1), text[m.end():]) if m else ("", text)
        rows.append({
            "stem": path.stem,
            "title": field(fm, "title") or path.stem,
            "status": field(fm, "status") or "active",
            "confidence": field(fm, "confidence") or "practitioner",
            "lane": field(fm, "lane"),
            "summary": summary(body),
        })
    for path in sorted(folder.glob("*.canvas")):
        rows.append({"stem": path.name, "title": path.stem, "status": "active", "confidence": "practitioner", "lane": "",
                     "summary": "Obsidian canvas.", "href": f"wiki/{folder.name}/{path.name}"})
    return rows


def entry(r: dict, base: str = "wiki") -> str:
    if r["stem"].endswith(".canvas"):
        link = f"[{r['title']}]({quote(os.path.relpath(r['href'], base))})"
    else:
        link = f"[[{r['stem']}]]" if r["stem"] == r["title"] else f"[[{r['stem']}|{r['title']}]]"
    return f"- {link} ({r['status']}, {r['confidence']}): {r['summary']}".rstrip(": ")


def frontmatter(type_: str, title: str, date: str, related: list[str]) -> str:
    rel = "\n".join(f'  - "[[{r}]]"' for r in related)
    return (f'---\ntype: "{type_}"\ntitle: "{title}"\ndomain: "Claude Code mods"\nstatus: "active"\n'
            f'created: "2026-10-03"\nupdated: "{date}"\ntested_on: "2.1.288"\ntags:\n  - "#domain/claude-code-mods"\n'
            f'  - "#type/{type_}"\n  - "#confidence/practitioner"\nconfidence: "practitioner"\nrelated:\n{rel}\n'
            f'source_urls:\n  - "https://code.claude.com/docs/en/plugins/mods/overview (retrieved 2026-10-03)"\n---\n')


def build(date: str) -> dict:
    counts = {}
    all_rows: dict[str, list[dict]] = {}
    for name, (hub_title, purpose) in FOLDERS.items():
        folder = WIKI / name
        if not folder.is_dir():
            continue
        rows = notes_in(folder)
        all_rows[name] = rows
        counts[name] = len(rows)
        related = ["index|Index", "hot|Hot", "overview|Overview", "dashboard|Dashboard", "CONVENTIONS", "Tag Taxonomy",
                   "Start Here", "research-pack-claude-mods|Research Pack"]
        related += [r["stem"] for r in rows[:6] if not r["stem"].endswith(".canvas")]
        lines = [frontmatter("hub", hub_title, date, related), f"# {hub_title}", "", purpose, "",
                 "Parent: [[index|Index]]. Operating contract: [[CONVENTIONS]]. Evidence: [[research-pack-claude-mods|Research Pack]].", "",
                 f"## Notes ({len(rows)})", ""]
        lanes = sorted({r["lane"] for r in rows if r["lane"]})
        if len(lanes) > 1:
            for lane in lanes + [""]:
                group = [r for r in rows if r["lane"] == lane]
                if group:
                    lines += [f"### {lane or 'brain operations'}", "", *[entry(r, f"wiki/{name}") for r in group], ""]
        else:
            lines += [entry(r, f"wiki/{name}") for r in rows] + [""]
        lines += ["## Related hubs", "", " | ".join(f"[[wiki/{n}/_index|{t}]]" for n, (t, _) in FOLDERS.items() if n != name and (WIKI / n).is_dir()), ""]
        (folder / "_index.md").write_text("\n".join(lines), encoding="utf-8")

    ledger = json.loads((ROOT / "references/source-ledger.json").read_text(encoding="utf-8"))
    total = sum(counts.values())
    order = ["concepts", "flows", "deliverables", "entities", "platforms", "reports", "decisions", "sources", "gaps", "questions", "experiments", "meta", "canvases"]
    lines = [frontmatter("index", "Index", date, ["hot|Hot", "overview|Overview", "log|Log", "Start Here", "CONVENTIONS", "dashboard|Dashboard",
                                                  "Tag Taxonomy", "Mods API Cheatsheet", "Mod Catalog", "research-pack-claude-mods|Research Pack"]),
             "# Index", "",
             f"Last updated: {date} | Total pages: {total} | Ledger sources: {len(ledger['sources'])} | Tested on: Claude Code 2.1.288", "",
             "Read [[hot|Hot]] first, then this index, then one folder hub. New here: [[Start Here]]. The shape of the domain: [[overview|Overview]]. History: [[log|Log]].", "",
             "Hubs: " + " | ".join(f"[[wiki/{n}/_index|{FOLDERS[n][0]}]]" for n in order if n in all_rows), ""]
    for name in order:
        rows = all_rows.get(name)
        if not rows:
            continue
        lines += [f"## {FOLDERS[name][0].removesuffix(' Hub')} ({len(rows)})", "", *[entry(r) for r in rows], ""]
    (WIKI / "index.md").write_text("\n".join(lines), encoding="utf-8")
    return {"total": total, **counts}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", required=True)
    args = parser.parse_args(argv)
    print(json.dumps(build(args.date)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
