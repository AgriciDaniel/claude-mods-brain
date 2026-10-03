#!/usr/bin/env python3
"""Diff two mods API surfaces and report drift between Claude Code versions.

Inputs: two `mods-brain.api-surface.v1` JSON files written by
`import_mod_types.py`. Output: a `mods-brain.api-drift.v1` JSON report and,
optionally, a markdown drift note listing added and removed events, `$`
namespaces and members, render components, elements, and exported types, plus
the wiki notes whose `tested_on` must be re-verified. It also compares member
and event declarations (signature changes) and every limit-bearing line, so a
changed budget such as `ms: 10_000` is drift; if the typings hash changed but
nothing named did, the report sets `manual_review_required`. This is the CI contract
job: re-capture the typings after every Claude Code update, diff, and act.

Read-only on inputs; exit code 0 when there is no drift, 1 when drift exists,
2 on bad input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SURFACE_SCHEMA = "mods-brain.api-surface.v1"
DRIFT_SCHEMA = "mods-brain.api-drift.v1"


def load_surface(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read surface {path.name}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema") != SURFACE_SCHEMA:
        raise ValueError(f"{path.name} is not a {SURFACE_SCHEMA} file")
    for key in ("claude_code_version", "events", "namespaces", "render_components", "elements", "exported_types"):
        if key not in data:
            raise ValueError(f"{path.name} missing key {key}")
    return data


def names(items: list) -> set[str]:
    return {i["name"] if isinstance(i, dict) else i for i in items}


def delta(old: set[str], new: set[str]) -> dict:
    return {"added": sorted(new - old), "removed": sorted(old - new)}


def member_names(surface: dict) -> set[str]:
    return {f"$.{ns['name']}.{m['name']}" for ns in surface["namespaces"] for m in ns.get("members", [])}


def element_names(surface: dict) -> set[str]:
    return {f"{surface_name}:{el}" for surface_name, spec in surface["elements"].items() for el in spec.get("elements", [])}


def changed_signatures(old: dict, new: dict) -> list[dict]:
    """Members and events present in both surfaces whose declaration text changed."""
    def sigs(surface: dict) -> dict[str, str]:
        out = {f"event:{e['name']}": e.get("signature", "") for e in surface["events"]["engine"] + surface["events"]["op"]}
        out.update({f"$.{ns['name']}.{m['name']}": m.get("signature", "") for ns in surface["namespaces"] for m in ns.get("members", [])})
        return out
    a, b = sigs(old), sigs(new)
    return [{"name": k, "old": a[k], "new": b[k]} for k in sorted(set(a) & set(b)) if a[k] and b[k] and a[k] != b[k]]


def diff(old: dict, new: dict) -> dict:
    sections = {
        "engine_events": delta(names(old["events"]["engine"]), names(new["events"]["engine"])),
        "op_events": delta(names(old["events"]["op"]), names(new["events"]["op"])),
        "classic_events": delta(set(old["events"]["classic"]), set(new["events"]["classic"])),
        "namespaces": delta(names(old["namespaces"]), names(new["namespaces"])),
        "namespace_members": delta(member_names(old), member_names(new)),
        "render_components": delta(set(old["render_components"]["values"]), set(new["render_components"]["values"])),
        "elements": delta(element_names(old), element_names(new)),
        "exported_types": delta(set(old["exported_types"]), set(new["exported_types"])),
    }
    sig_changes = changed_signatures(old, new)
    limits = delta({l["text"] for l in old.get("limits", [])}, {l["text"] for l in new.get("limits", [])})
    sections["limits"] = limits
    changed = sum(len(v["added"]) + len(v["removed"]) for v in sections.values()) + len(sig_changes)
    identical = old.get("source_sha256") == new.get("source_sha256")
    return {
        "schema": DRIFT_SCHEMA,
        "from_version": old["claude_code_version"],
        "to_version": new["claude_code_version"],
        "from_sha256": old.get("source_sha256"),
        "to_sha256": new.get("source_sha256"),
        "typings_identical": identical,
        "change_count": changed,
        "sections": sections,
        "signatures_changed": sig_changes,
        "manual_review_required": (not identical) and changed == 0,
    }


def affected_notes(report: dict, wiki: Path | None) -> list[str]:
    """Wiki notes that mention any added or removed name and so need re-verification."""
    if wiki is None or not wiki.is_dir():
        return []
    tokens: set[str] = set()
    for key, section in report["sections"].items():
        for name in section["added"] + section["removed"]:
            if key == "limits":
                # A limit line maps to notes by its numbers, in the forms notes write them (10_000, 10,000, 10000).
                # Big numbers stand alone (10_000, 10000, 10,000); small ones only with their unit ("10 seconds").
                for num in re.findall(r"\d[\d_,]*\d|\d", name):
                    digits = num.replace("_", "").replace(",", "")
                    if digits.isdigit() and int(digits) >= 1000:
                        tokens.update({num, digits, f"{int(digits):,}"})
                for num, unit in re.findall(r"(\d[\d_,.]*)\s?(ms|milliseconds|seconds?|minutes?|MiB|KiB|characters|tokens|entries)\b", name):
                    tokens.add(f"{num} {unit}")
                continue
            token = name.split(":")[-1].removeprefix("$.")
            if len(token) >= 4:
                tokens.add(token)
    for change in report.get("signatures_changed", []):
        token = change["name"].split(":")[-1].removeprefix("$.")
        tokens.add(token)
        if "." in token:
            tokens.add(token.split(".")[-1])
    if not tokens:
        return []
    pattern = re.compile("|".join(re.escape(t) for t in sorted(tokens, key=len, reverse=True)))
    hits = []
    for path in sorted(wiki.rglob("*.md")):
        try:
            if pattern.search(path.read_text(encoding="utf-8", errors="replace")):
                hits.append(path.relative_to(wiki).as_posix())
        except OSError:
            continue
    return hits


def render_note(report: dict, date: str) -> str:
    """The drift report as a vault note: frontmatter, the table, and how to act on it."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _render_common import frontmatter
    title = f"API Drift {report['from_version']} to {report['to_version']}"
    fm = frontmatter(
        type_="report", title=title, date=date, tested_on=report["to_version"], confidence="evidence-based",
        related=["Re-verify After Release Flow", "Versioning and API Drift", "Research Refresh Workflow", "API Surface 2.1.288",
                 "Mods API Cheatsheet", "Budgets and Limits", "Version Pin Policy", "Mods API Namespaces"],
        source_urls=[f"https://code.claude.com/docs/en/plugins/mods/reference (retrieved {date})"],
        sources=[f"types-{report['from_version'].replace('.', '-')}", f"types-{report['to_version'].replace('.', '-')}", "scripts/diff_api_surface.py"],
    )
    body = render_markdown(report).split("\n", 1)[1]
    intro = (f"\n# {title}\n\nGenerated by `scripts/diff_api_surface.py` on {date}: names (events, `$` members, render components, "
             "elements, exported types), declaration signatures, and every limit-bearing line of the generated typings, compared "
             "between two Claude Code builds. Act on it with [[Re-verify After Release Flow]]; background in [[Versioning and API Drift]]. "
             "#confidence/evidence-based\n")
    guide = "\n".join([
        "",
        "## Reading this report",
        "",
        "- **Added or removed events and members**: update [[Mods API Cheatsheet]] and the concept note for that family; a removal breaks mods that use it.",
        "- **Changed signatures**: a parameter, option, or return shape moved; re-check every snippet that calls it and re-run the snippet type-check.",
        "- **Limits**: a budget, cap, or size changed; update [[Budgets and Limits]] and any guard that depends on the old value.",
        "- **Typings changed but nothing named did** (`manual_review_required`): diff the two `index.d.ts` files by hand; the change is in prose or a type the importer does not index.",
        "- **Notes to re-verify**: re-read each one against the new capture, then bump its `tested_on`.",
        "",
        "## Caveats",
        "",
        "- Generated; regenerate rather than edit. The importer indexes names, declarations, and limit lines, not every nested type, so a quiet change inside a payload type surfaces only as a hash change.",
        "",
    ])
    return fm + intro + body + guide


def render_markdown(report: dict) -> str:
    lines = [
        f"# API drift {report['from_version']} to {report['to_version']}",
        "",
        f"Typings identical: {'yes' if report['typings_identical'] else 'no'}. Changes: {report['change_count']}.",
        "",
        "| Section | Added | Removed |",
        "|---|---|---|",
    ]
    for key, section in report["sections"].items():
        added = ", ".join(f"`{n}`" for n in section["added"]) or "none"
        removed = ", ".join(f"`{n}`" for n in section["removed"]) or "none"
        lines.append(f"| {key} | {added.replace('|', '/')} | {removed.replace('|', '/')} |")
    if report.get("signatures_changed"):
        lines += ["", "## Changed signatures", ""]
        lines += [f"- `{c['name']}`: `{c['old']}` became `{c['new']}`".replace("|", "/") for c in report["signatures_changed"]]
    if report.get("manual_review_required"):
        lines += ["", "> [!warning] The typings changed but no named element, signature, or limit line did. Diff the two index.d.ts files by hand."]
    notes = report.get("affected_notes", [])
    lines += ["", "## Notes to re-verify", ""]
    lines += [f"- `{n}`" for n in notes] or ["- none"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--out", required=True, help="drift JSON output path")
    parser.add_argument("--markdown", help="optional markdown report path")
    parser.add_argument("--wiki", help="wiki folder to scan for notes affected by drift")
    parser.add_argument("--note", help="write the report as a vault note (needs --date)")
    parser.add_argument("--date", help="ISO date stamped into --note")
    args = parser.parse_args(argv)
    try:
        old = load_surface(Path(args.old))
        new = load_surface(Path(args.new))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    report = diff(old, new)
    report["affected_notes"] = affected_notes(report, Path(args.wiki) if args.wiki else None)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(render_markdown(report), encoding="utf-8")
    if args.note:
        if not args.date:
            print("ERROR: --note needs --date", file=sys.stderr)
            return 2
        Path(args.note).write_text(render_note(report, args.date), encoding="utf-8")
    print(json.dumps({"from": report["from_version"], "to": report["to_version"], "changes": report["change_count"]}))
    return 1 if report["change_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
