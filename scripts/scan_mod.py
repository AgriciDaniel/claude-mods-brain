#!/usr/bin/env python3
"""Statically scan a Claude Code mod (plugin directory) for its footprint.

Reads `.claude-plugin/plugin.json`, `hooks/hooks.json`, and every hook module
source file (never executes anything) and reports: events hooked with their
matchers, `$` calls, classic settings hooks, a reach level (L0 draws, L1
reads, L2 writes/runs/drives Claude, L3 network), the usage-cost surface, and
red flags from the brain's audit checklist. Optionally folds in the JSON that
`claude plugin validate --json <dir>` printed, supplied as a file.

Output schema: `mods-brain.mod-scan.v1`. Paths in the output are relative to
the plugin directory; no absolute paths are written.

A static scan is a first pass, not a verdict: rewrites passed through
`next({...e})` and UI spoofing need a human read (see the audit flow).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = "mods-brain.mod-scan.v1"
MODULE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts"}
SKIP_DIRS = {"node_modules", "types", ".git", "dist", "tests", "test", "__tests__"}

ON_RE = re.compile(r"""\bon\(\s*(['"`])([\w.*-]+)\1\s*(,\s*(\{[^{}]*\}|\[[^\]]*\]|/[^/]+/))?""")
DOLLAR_RE = re.compile(r"\$\.([a-z]+)\.([a-zA-Z]+)\b")
REACH_L3 = {"http.fetch", "mcp.call", "mcp.connect"}
REACH_L2 = {
    "fs.write", "process.run", "process.spawn", "prompt.submit", "agent.spawn", "agent.register",
    "tool.register", "tool.call", "model.complete", "model.fork", "model.classify", "env.set",
    "session.send", "turn.abort", "command.run", "config.set",
}
REACH_L1 = {
    "fs.read", "fs.list", "fs.exists", "fs.stat", "fs.ancestors", "session.messages", "settings.read",
    "env.get", "prompt.read", "session.repo", "session.cwd", "session.root", "tool.list", "agent.list",
    "command.list", "config.list",
}
COST_CALLS = {
    "model.complete": "model call billed to the user's plan or API key",
    "model.fork": "model call with conversation context, billed",
    "model.classify": "model classification call (billing undocumented)",
    "prompt.submit": "starts a turn",
    "agent.spawn": "starts a subagent",
    "tool.register": "tool description added to every request",
}
ENV_KEY_RE = re.compile(r"""\$\.env\.get\(\s*['"`]([A-Za-z_][A-Za-z0-9_]*)""")
BENIGN_ENV = {"HOME", "USER", "LOGNAME", "PATH", "SHELL", "TERM", "LANG", "PWD", "TMPDIR", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "CLAUDE_CONFIG_DIR"}
DENY_RE = re.compile(r"\{\s*deny\s*:")
TOOL_CALL_REG_RE = re.compile(r"""\bon\(\s*['"`]tool\.call['"`]""")
REG_CATCH_RE = re.compile(r"\}\s*\)\s*\.catch\(")
MODULE_STATE_RE = re.compile(r"(?m)^\s{0,2}let\s+[A-Za-z_$]")
INTERNALS_RE = re.compile(r"\.claude/(sessions|projects|history|todos)|/proc/")
CACHE_EVENTS = {"prompt.section", "prompt.context", "skill.prompt", "prompt.attachment"}
CONTROL_EVENTS = {"tool.call", "tool.check", "prompt.submit", "turn.step", "agent.spawn", "session.compact", "process.spawn"}
POLICY_EVENTS = {"engine.create", "plugin.register"}


class ScanError(Exception):
    """Raised when the directory is not a scannable mod."""


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", text)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ScanError(f"{path.name} is not valid JSON: {exc.msg} at line {exc.lineno}") from exc
    if not isinstance(data, dict):
        raise ScanError(f"{path.name} must be a JSON object")
    return data


def module_files(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts[:-1]):
            continue
        if path.is_file() and path.suffix in MODULE_SUFFIXES and ".test." not in path.name:
            files.append(path)
    return files


def reach_level(calls: set[str]) -> str:
    if calls & REACH_L3:
        return "L3"
    if calls & REACH_L2:
        return "L2"
    if calls & REACH_L1:
        return "L1"
    return "L0"


def scan(root: Path, validate_json: Path | None = None) -> dict:
    if not root.is_dir():
        raise ScanError("plugin directory not found")
    manifest_path = root / ".claude-plugin" / "plugin.json"
    if not manifest_path.is_file():
        raise ScanError("missing .claude-plugin/plugin.json")
    manifest = load_json(manifest_path)
    hooks_path = root / "hooks" / "hooks.json"
    hooks = load_json(hooks_path) if hooks_path.is_file() else {}
    modules = hooks.get("modules", [])
    if modules and (not isinstance(modules, list) or len(modules) != 1):
        raise ScanError("hooks.json modules must be an array holding exactly one path")
    classic = sorted(hooks.get("hooks", {}).keys()) if isinstance(hooks.get("hooks"), dict) else []

    events: dict[str, list[str]] = {}
    calls: dict[str, int] = {}
    flags: list[dict] = []
    files_scanned = []
    sources: dict[str, str] = {}
    for path in module_files(root):
        rel = path.relative_to(root).as_posix()
        text = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        sources[rel] = text
        files_scanned.append({"path": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "lines": text.count("\n") + 1})
        for m in ON_RE.finditer(text):
            matcher = (m.group(4) or "").strip()
            events.setdefault(m.group(2), [])
            if matcher and matcher not in events[m.group(2)]:
                events[m.group(2)].append(matcher)
        for m in DOLLAR_RE.finditer(text):
            key = f"{m.group(1)}.{m.group(2)}"
            calls[key] = calls.get(key, 0) + 1

    all_text = "\n".join(sources.values())
    call_set = set(calls)
    event_set = set(events)

    def flag(code: str, severity: str, detail: str) -> None:
        files = sorted(rel for rel, text in sources.items() if detail_hit(code, text))
        flags.append({"code": code, "severity": severity, "detail": detail, "files": files})

    def detail_hit(code: str, text: str) -> bool:
        probes = {
            "fetch-then-run": r"\$\.http\.fetch|\$\.process\.(run|spawn)",
            "env-read": r"\$\.env\.get",
            "submit-as-user": r"asUser\s*:\s*true",
            "tool-check-allow": r"decision\s*:\s*['\"]allow",
            "acts-on-other-mods": r"on\(\s*['\"`](engine\.create|plugin\.register)",
            "wildcard-hook": r"on\(\s*['\"`]\*",
            "event-rewrite": r"next\(\s*\{\s*\.\.\.e",
            "absolute-fs-path": r"\$\.fs\.(read|write|list)\(\s*['\"`](/|~)",
            "guard-without-catch": DENY_RE.pattern,
            "module-variable-state": MODULE_STATE_RE.pattern,
            "reads-claude-internals": INTERNALS_RE.pattern,
        }
        return bool(re.search(probes.get(code, r"$^"), text))

    if "http.fetch" in call_set and call_set & {"process.run", "process.spawn"}:
        flag("fetch-then-run", "critical", "fetches from the network and runs processes: code can change after review")
    if "env.get" in call_set:
        keys = sorted(set(ENV_KEY_RE.findall(all_text)))
        risky = [k for k in keys if k not in BENIGN_ENV] or (["<dynamic>"] if not keys else [])
        if risky:
            flag("env-read", "high", f"reads environment variables that can hold secrets: {', '.join(risky)}")
        else:
            flag("env-read", "info", f"reads only benign environment variables: {', '.join(keys)}")
    if re.search(r"asUser\s*:\s*true", all_text):
        flag("submit-as-user", "high", "submits prompts as the user")
    if "tool.check" in event_set and re.search(r"decision\s*:\s*['\"]allow", all_text):
        flag("tool-check-allow", "critical", "can approve tool calls before the user is asked")
    if event_set & POLICY_EVENTS:
        flag("acts-on-other-mods", "high", "hooks engine.create or plugin.register and so acts on other mods")
    if "*" in event_set:
        flag("wildcard-hook", "high", "wildcard hook sees every event")
    if re.search(r"next\(\s*\{\s*\.\.\.e", all_text) and event_set & (CONTROL_EVENTS | {"ui.render"}):
        flag("event-rewrite", "review", "rewrites events through next({...e}); read each rewrite by hand, a scan cannot judge it")
    if re.search(r"\$\.fs\.(read|write|list)\(\s*['\"`](/|~)", all_text):
        flag("absolute-fs-path", "high", "touches absolute paths outside the workspace")
    guards = len(TOOL_CALL_REG_RE.findall(all_text))
    if guards and DENY_RE.search(all_text) and len(REG_CATCH_RE.findall(all_text)) < guards:
        flag("guard-without-catch", "medium",
             f"denies tool calls but fewer registration .catch handlers than tool.call hooks ({len(REG_CATCH_RE.findall(all_text))} of {guards}), so a failing or timed-out guard lets the call through")
    if MODULE_STATE_RE.search(all_text):
        flag("module-variable-state", "review", "keeps state in module-level or register-level variables, which every reload wipes; prefer $.state or $.store")
    if INTERNALS_RE.search(all_text):
        flag("reads-claude-internals", "medium", "reads undocumented Claude Code internals (session files under ~/.claude or /proc), which a release can break")

    abs_defaults = sorted(k for k, spec in (manifest.get("userConfig") or {}).items()
                          if isinstance(spec, dict) and isinstance(spec.get("default"), str) and spec["default"].startswith(("/", "~")))
    if abs_defaults:
        flags.append({"code": "absolute-config-default", "severity": "review",
                      "detail": "userConfig defaults point at machine-specific absolute paths: " + ", ".join(abs_defaults),
                      "files": [".claude-plugin/plugin.json"]})

    cost = [{"call": c, "why": COST_CALLS[c]} for c in sorted(call_set & set(COST_CALLS))]
    cost += [{"event": e, "why": "text from this hook enters the prompt; unstable text busts the prompt cache"} for e in sorted(event_set & CACHE_EVENTS)]

    validate = None
    if validate_json is not None:
        data = load_json(validate_json)
        validate = {"keys": sorted(data.keys()), "summary": {k: data[k] for k in ("hooks", "calls", "errors", "warnings") if k in data}}

    return {
        "schema": SCHEMA,
        "plugin": {
            "name": manifest.get("name"),
            "version": manifest.get("version"),
            "description": manifest.get("description", ""),
            "user_config": sorted((manifest.get("userConfig") or {}).keys()),
            "dependencies": manifest.get("dependencies", []),
        },
        "module": modules[0] if modules else None,
        "is_mod": bool(modules),
        "classic_hooks": classic,
        "files": files_scanned,
        "events": {k: events[k] for k in sorted(events)},
        "calls": {k: calls[k] for k in sorted(calls)},
        "reach": reach_level(call_set),
        "control_events": sorted(event_set & CONTROL_EVENTS),
        "cost_surface": cost,
        "red_flags": flags,
        "validate": validate,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plugin", required=True, help="plugin directory holding .claude-plugin/plugin.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--validate-json", help="file holding `claude plugin validate --json` output")
    args = parser.parse_args(argv)
    try:
        report = scan(Path(args.plugin), Path(args.validate_json) if args.validate_json else None)
    except ScanError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"plugin": report["plugin"]["name"], "reach": report["reach"], "events": len(report["events"]), "red_flags": [f["code"] for f in report["red_flags"]]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
