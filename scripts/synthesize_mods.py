#!/usr/bin/env python3
"""Synthesize the mods API surface, mod scans, and the catalog into one model.

Inputs:
  --surface   a `mods-brain.api-surface.v1` JSON (import_mod_types.py)
  --scans     a directory of `mods-brain.mod-scan.v1` JSON files (scan_mod.py)
  --catalog   optional `mods-brain.catalog.v1` JSON (community mods, curated)
Output: `mods-brain.synthesis.v1` JSON with
  - capability matrix: every engine event and `$` namespace, and which scanned
    mods use it; op events (a `$` method hooked as an event, such as
    `ui.close`) listed separately; events unknown to the surface flag drift
  - per-mod verdict suggestions derived from reach, red flags, and cost
  - catalog rows merged with scan evidence when names match

Verdict rule (suggestion only; a human read decides, see the audit flow):
  any critical red flag -> avoid; any high or medium red flag (for example a
  fail-open guard or reads of Claude Code internals), L3 reach, or classic
  settings hooks shipped beside the mod (shell commands outside the mod
  surface) -> trial; otherwise -> adopt-candidate.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCHEMA = "mods-brain.synthesis.v1"


def load(path: Path, schema: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path.name}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema") != schema:
        raise ValueError(f"{path.name} is not a {schema} file")
    return data


def verdict(scan: dict) -> tuple[str, str]:
    severities = {f["severity"] for f in scan.get("red_flags", [])}
    codes = [f["code"] for f in scan.get("red_flags", []) if f["severity"] in {"critical", "high"}]
    if "critical" in severities:
        return "avoid", "critical red flag: " + ", ".join(codes)
    if severities & {"high", "medium"}:
        flagged = [f["code"] for f in scan.get("red_flags", []) if f["severity"] in {"high", "medium"}]
        return "trial", "needs a human read for: " + ", ".join(flagged)
    if scan.get("classic_hooks"):
        return "trial", "ships classic settings hooks (" + ", ".join(scan["classic_hooks"]) + ") that run shell commands outside the mod surface"
    if scan.get("reach") == "L3":
        return "trial", "network reach (L3): check what leaves the machine"
    return "adopt-candidate", f"reach {scan.get('reach')}, no medium-or-higher static flags"


def synthesize(surface: dict, scans: list[dict], catalog: dict | None) -> dict:
    engine_events = [e["name"] for e in surface["events"]["engine"]]
    op_events = {e["name"] for e in surface["events"]["op"]}
    known_events = set(engine_events) | op_events | set(surface["events"]["classic"])
    namespaces = [ns["name"] for ns in surface["namespaces"]]

    event_matrix = {e: [] for e in engine_events}
    namespace_matrix = {n: [] for n in namespaces}
    unknown_events: dict[str, list[str]] = {}
    op_hooks: dict[str, list[str]] = {}
    mods = []
    for scan in sorted(scans, key=lambda s: s["plugin"]["name"] or ""):
        name = scan["plugin"]["name"]
        for event in scan["events"]:
            if event in event_matrix:
                event_matrix[event].append(name)
            elif event in op_events:
                op_hooks.setdefault(event, []).append(name)
            elif event not in known_events and event != "*":
                unknown_events.setdefault(event, []).append(name)
        used_ns = sorted({call.split(".")[0] for call in scan["calls"]})
        for ns in used_ns:
            if ns in namespace_matrix:
                namespace_matrix[ns].append(name)
        v, why = verdict(scan)
        mods.append({
            "name": name,
            "version": scan["plugin"].get("version"),
            "reach": scan["reach"],
            "events": sorted(scan["events"]),
            "namespaces": used_ns,
            "control_events": scan.get("control_events", []),
            "cost_surface": scan.get("cost_surface", []),
            "red_flags": [{"code": f["code"], "severity": f["severity"]} for f in scan.get("red_flags", [])],
            "verdict_suggestion": v,
            "verdict_reason": why,
        })

    catalog_rows = []
    scanned = {m["name"]: m for m in mods}
    if catalog:
        for row in catalog.get("mods", []):
            merged = dict(row)
            evidence = scanned.get(row.get("name"))
            if evidence:
                merged["scan_reach"] = evidence["reach"]
                merged["scan_verdict"] = evidence["verdict_suggestion"]
            catalog_rows.append(merged)

    return {
        "schema": SCHEMA,
        "claude_code_version": surface["claude_code_version"],
        "mods_scanned": len(mods),
        "event_matrix": event_matrix,
        "namespace_matrix": namespace_matrix,
        "unused_events": sorted(e for e, users in event_matrix.items() if not users),
        "op_event_hooks": op_hooks,
        "unknown_events": unknown_events,
        "mods": mods,
        "catalog": catalog_rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--surface", required=True)
    parser.add_argument("--scans", required=True)
    parser.add_argument("--catalog")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        surface = load(Path(args.surface), "mods-brain.api-surface.v1")
        scans = [load(p, "mods-brain.mod-scan.v1") for p in sorted(Path(args.scans).glob("*.json"))]
        catalog = load(Path(args.catalog), "mods-brain.catalog.v1") if args.catalog else None
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not scans:
        print("ERROR: no scan files found", file=sys.stderr)
        return 2
    result = synthesize(surface, scans, catalog)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mods": result["mods_scanned"], "unused_events": len(result["unused_events"]), "unknown_events": len(result["unknown_events"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
