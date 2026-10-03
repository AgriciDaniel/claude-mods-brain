#!/usr/bin/env python3
"""Import a generated Claude Code mods typings capture into an API surface JSON.

Input: a directory holding `claude-code/index.d.ts` (and optionally
`claude-code-tools/index.d.ts`), as Claude Code writes beside a mod under
`.claude-plugin/types/`. Output: `mods-brain.api-surface.v1` JSON listing the
writing Claude Code version, events (engine, op, classic) with their payload
declarations, the `$` namespaces and their members with signatures, render
components, elements by surface, every exported type name, and every line that
states a limit (unit-bearing numbers and numeric constants such as
`ms: 10_000`), each with a source line number for citation.

Read-only: the script reads the capture and writes one JSON file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = "mods-brain.api-surface.v1"
VERSION_RE = re.compile(r"^//\s*Written by Claude Code\s+([0-9]+\.[0-9]+\.[0-9]+[^\s.]*)")
KEY_RE = re.compile(r"^(?P<indent>\s*)(?:'(?P<q>[^']+)'|(?P<b>[A-Za-z_$][\w$]*))\??\s*:")
EXPORT_RE = re.compile(r"^\s*export\s+(?:declare\s+)?(?:type|interface)\s+([A-Za-z_]\w*)")
UNION_LITERAL_RE = re.compile(r"'([^']+)'")
LIMIT_TEXT_RE = re.compile(r"\b[0-9][0-9_,.]*\s?(ms|milliseconds|seconds?|minutes?|MiB|KiB|characters|tokens|entries)\b")
NUMERIC_CONST_RE = re.compile(r"^\s*(?:readonly\s+)?[A-Za-z_$][\w$]*\??:\s*[0-9][0-9_]*\s*;")


class ImportErrorBadInput(Exception):
    """Raised when the capture is not a mods typings file."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_block(lines: list[str], header: re.Pattern[str]) -> tuple[int, int] | None:
    """Return (start, end) 0-based line indexes of the `{ ... }` block opened on a header line."""
    for i, line in enumerate(lines):
        if header.search(line) and line.rstrip().endswith("{"):
            depth = 0
            for j in range(i, len(lines)):
                depth += lines[j].count("{") - lines[j].count("}")
                if depth <= 0 and j > i:
                    return i, j
            return None
    return None


def doc_summary(lines: list[str], idx: int) -> str:
    """First sentence of the JSDoc comment that ends just above line idx."""
    j = idx - 1
    if j < 0 or not lines[j].strip().endswith("*/"):
        return ""
    buf: list[str] = []
    while j >= 0:
        text = lines[j].strip()
        buf.append(text)
        if text.startswith("/**"):
            break
        j -= 1
    buf.reverse()
    body: list[str] = []
    for text in buf:
        text = text.removeprefix("/**").removesuffix("*/").strip().lstrip("*").strip()
        if text.startswith("@"):
            break
        if text:
            body.append(text)
    joined = " ".join(body)
    match = re.match(r"(.+?\.)(\s|$)", joined)
    return (match.group(1) if match else joined)[:240]


def signature(lines: list[str], idx: int, max_lines: int = 6) -> str:
    """The declaration text of the key on line idx, through its terminating semicolon (whitespace normalized)."""
    parts = []
    for j in range(idx, min(idx + max_lines, len(lines))):
        parts.append(lines[j].strip())
        if lines[j].rstrip().endswith((";", "{")):
            break
    return re.sub(r"\s+", " ", " ".join(parts))[:400]


def parse_limits(lines: list[str]) -> list[dict]:
    """Every line that states a limit: unit-bearing numbers in comments and numeric constant declarations."""
    out = []
    for i, line in enumerate(lines):
        text = line.strip().lstrip("*/ ").strip()
        if NUMERIC_CONST_RE.match(line) or LIMIT_TEXT_RE.search(line):
            out.append({"line": i + 1, "text": re.sub(r"\s+", " ", text)})
    return out


def keys_at_depth(lines: list[str], start: int, end: int) -> list[dict]:
    """Keys one level inside the block [start, end], with line numbers and summaries."""
    out: list[dict] = []
    depth = 0
    for i in range(start, end + 1):
        line = lines[i]
        if depth == 1 and not line.strip().startswith(("*", "/*", "//")):
            m = KEY_RE.match(line)
            if m:
                out.append({"name": m.group("q") or m.group("b"), "line": i + 1, "summary": doc_summary(lines, i),
                            "signature": signature(lines, i)})
        depth += line.count("{") - line.count("}")
    return out


def parse_namespaces(lines: list[str]) -> list[dict]:
    block = find_block(lines, re.compile(r"export interface CoreEngineInterface\b"))
    if not block:
        raise ImportErrorBadInput("CoreEngineInterface not found")
    start, end = block
    namespaces = []
    for key in keys_at_depth(lines, start, end):
        i = key["line"] - 1
        members: list[dict] = []
        if lines[i].rstrip().endswith("{"):
            depth = 0
            for j in range(i, end + 1):
                if depth == 1 and j > i and not lines[j].strip().startswith(("*", "/*", "//")):
                    m = KEY_RE.match(lines[j])
                    if m:
                        members.append({"name": m.group("q") or m.group("b"), "line": j + 1, "summary": doc_summary(lines, j),
                                        "signature": signature(lines, j)})
                depth += lines[j].count("{") - lines[j].count("}")
                if depth <= 0 and j > i:
                    break
        namespaces.append({**key, "members": members})
    return namespaces


def parse_union(lines: list[str], name: str) -> dict:
    pat = re.compile(rf"export type {re.escape(name)}\s*=")
    for i, line in enumerate(lines):
        if pat.search(line):
            text = line
            j = i
            while not text.rstrip().endswith(";") and j + 1 < len(lines):
                j += 1
                text += lines[j]
            return {"line": i + 1, "values": UNION_LITERAL_RE.findall(text.split("=", 1)[1])}
    return {"line": None, "values": []}


def parse_elements(lines: list[str]) -> dict:
    block = find_block(lines, re.compile(r"export type Elements\s*=\s*\{"))
    if not block:
        return {}
    start, end = block
    surfaces: dict[str, dict] = {}
    for key in keys_at_depth(lines, start, end):
        i = key["line"] - 1
        elems: list[str] = []
        depth = 0
        for j in range(i, end + 1):
            if depth == 1 and j > i:
                m = KEY_RE.match(lines[j])
                if m and not lines[j].strip().startswith("*"):
                    elems.append(m.group("q") or m.group("b"))
            depth += lines[j].count("{") - lines[j].count("}")
            if depth <= 0 and j > i:
                break
        surfaces[key["name"]] = {"line": key["line"], "elements": elems}
    return surfaces


def parse_events(lines: list[str], type_name: str) -> list[dict]:
    block = find_block(lines, re.compile(rf"export type {re.escape(type_name)}\s*=\s*\{{"))
    if not block:
        return []
    return [k for k in keys_at_depth(lines, *block) if "." in k["name"]]


def classic_events(texts: list[str]) -> list[str]:
    names: set[str] = set()
    for text in texts:
        names.update(re.findall(r"hook_event_name:\s*'([A-Za-z]+)'", text))
    return sorted(names)


def import_capture(capture: Path) -> dict:
    main = capture / "claude-code" / "index.d.ts"
    if not main.is_file():
        raise ImportErrorBadInput(f"missing claude-code/index.d.ts under {capture.name}")
    text = main.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    version_match = VERSION_RE.match(lines[0]) if lines else None
    if not version_match or "declare module 'claude-code'" not in text:
        raise ImportErrorBadInput("not a Claude Code mods typings file (no version header or module declaration)")
    texts = [text]
    tools = capture / "claude-code-tools" / "index.d.ts"
    if tools.is_file():
        texts.append(tools.read_text(encoding="utf-8", errors="replace"))
    engine = parse_events(lines, "EngineEventOf")
    ops = parse_events(lines, "OpEventOf")
    classic = classic_events(texts)
    exports = sorted({m.group(1) for line in lines if (m := EXPORT_RE.match(line))})
    return {
        "schema": SCHEMA,
        "claude_code_version": version_match.group(1),
        "source_file": "claude-code/index.d.ts",
        "source_sha256": sha256_file(main),
        "line_count": len(lines),
        "events": {
            "engine": engine,
            "op": ops,
            "classic": [f"classic.{n}" for n in classic],
        },
        "namespaces": parse_namespaces(lines),
        "render_components": parse_union(lines, "RenderComponent"),
        "elements": parse_elements(lines),
        "exported_types": exports,
        "limits": parse_limits(lines),
        "counts": {
            "engine_events": len(engine),
            "op_events": len(ops),
            "classic_events": len(classic),
            "exported_types": len(exports),
            "limit_lines": len(parse_limits(lines)),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--capture", required=True, help="directory holding claude-code/index.d.ts")
    parser.add_argument("--out", required=True, help="output api-surface JSON path")
    args = parser.parse_args(argv)
    try:
        surface = import_capture(Path(args.capture))
    except ImportErrorBadInput as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(surface, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    counts = surface["counts"]
    print(json.dumps({"version": surface["claude_code_version"], "namespaces": len(surface["namespaces"]), **counts}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
