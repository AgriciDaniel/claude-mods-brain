#!/usr/bin/env python3
"""Deterministic gate: no em or en dash, no credential-looking strings, no local home paths in shipped files."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SELF = "scripts/check_no_em_dash.py"
SKIP = {".git", ".raw", ".research-candidates", ".gate-logs", "dist", "__pycache__", "node_modules", ".venv"}
TEXT = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".txt", ".html", ".css", ".js", ".ts", ".tsx", ".svg", ".canvas", ""}
DASHES = {"em dash": "—", "en dash": "–"}
SECRETS = {
    "github token": re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    "anthropic or openai key": re.compile(r"sk-(?:ant-)?[A-Za-z0-9_-]{30,}"),
    "aws key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "bearer jwt": re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}"),
}
LOCAL_PATH = re.compile(r"/var/home/[A-Za-z0-9_]+|/home/[a-z][a-z0-9_-]+/|/Users/[A-Za-z0-9_]+/|/tmp/claude-\d+")


def main() -> int:
    problems = []
    for path in sorted(REPO.rglob("*")):
        if not path.is_file() or set(path.relative_to(REPO).parts) & SKIP or path.suffix not in TEXT:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(REPO).as_posix()
        if rel == SELF:
            continue
        for name, glyph in DASHES.items():
            if glyph in text:
                problems.append(f"{name} in {rel} (line {text[:text.index(glyph)].count(chr(10)) + 1})")
        for name, pat in SECRETS.items():
            if pat.search(text):
                problems.append(f"possible {name} in {rel}")
        match = LOCAL_PATH.search(text)
        if match:
            problems.append(f"local path {match.group(0)!r} in {rel}")
    for p in problems:
        print(p)
    print("no-dash-no-secrets-no-paths gate:", "FAIL" if problems else "PASS", f"({len(problems)} findings)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
