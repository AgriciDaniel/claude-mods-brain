"""Shared helpers for the mods-brain renderers: frontmatter and safe text."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

DOMAIN = "Claude Code mods"
DOMAIN_TAG = "#domain/claude-code-mods"


def clean(text: str) -> str:
    """Make text safe for a table cell and free of em or en dashes."""
    text = text.replace("\u2014", ", ").replace("\u2013", "-").replace("|", "\\|")
    return re.sub(r"\s+", " ", text).strip()


def frontmatter(*, type_: str, title: str, date: str, tested_on: str, confidence: str,
                related: list[str], source_urls: list[str], sources: list[str], status: str = "evergreen") -> str:
    lines = [
        "---",
        f'type: "{type_}"',
        f'title: "{title}"',
        f'domain: "{DOMAIN}"',
        f'status: "{status}"',
        f'created: "{date}"',
        f'updated: "{date}"',
        f'tested_on: "{tested_on}"',
        "tags:",
        f'  - "{DOMAIN_TAG}"',
        f'  - "#type/{type_}"',
        f'  - "#confidence/{confidence}"',
        f'confidence: "{confidence}"',
        'generated_by: "scripts"',
        "related:",
        *[f'  - "[[{r}]]"' for r in related],
        "source_urls:",
        *[f'  - "{u}"' for u in source_urls],
        "sources:",
        *[f'  - "{s}"' for s in sources],
        "---",
        "",
    ]
    return "\n".join(lines)


def delink(text: str) -> str:
    """Turn [[Target]] and [[Target|Label]] into plain text, for vaults that lack the linked notes."""
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    return re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)


def plain_footer(text: str, source: str) -> str:
    """Delink and append the input's sha256 so a standalone report still carries provenance."""
    digest = hashlib.sha256(Path(source).read_bytes()).hexdigest()
    return delink(text).rstrip("\n") + f"\n\nInput: `{Path(source).name}`, sha256 `{digest}`.\n"
