#!/usr/bin/env python3
"""Render _attachments/mods-hook-chain.svg: the five hook tiers around core, and the three moves.

Facts drawn (Claude Code 2.1.288): hooks for one event nest outermost first as
prepend, user, append, builtin, core (types 2.1.288 L11897-11907; docs-mods-events);
a hook observes (await next, return the result), rewrites (next with a copy), or
answers (return without calling next). Deterministic output, no dashes.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_attachments" / "mods-hook-chain.svg"
TIERS = [
    ("prepend", "org mods: sec-default, prependPlugins", "#D3E3FD", "#0B57D0"),
    ("user", "mods a person installs", "#CEEAD6", "#137333"),
    ("append", "org mods: appendPlugins", "#FEEFC3", "#976800"),
    ("builtin", "mods bundled in Claude Code", "#FAD2CF", "#C5221F"),
]
MOVES = [
    ("Observe", "r = await next(e); return r"),
    ("Rewrite", "return next({ ...e, field })"),
    ("Answer", "return { deny } or { result }"),
]


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render() -> str:
    w, h = 960, 560
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t d">',
        '<title id="t">Claude Code mods hook chain</title>',
        '<desc id="d">Five nested tiers, outermost first: prepend, user, append, builtin, then core. An event enters at the outer tier and the result returns outward.</desc>',
        f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>',
        '<text x="32" y="44" font-family="Helvetica, Arial, sans-serif" font-size="24" font-weight="700" fill="#202124">How one event runs through mods</text>',
        '<text x="32" y="70" font-family="Helvetica, Arial, sans-serif" font-size="14" fill="#5F6368">Claude Code 2.1.288. Outer tiers see the event first and the result last; an inner hook cannot hide anything from an outer one.</text>',
    ]
    x0, y0, bw, bh = 32, 100, 600, 400
    for i, (name, note, fill, ink) in enumerate(TIERS):
        inset = i * 34
        out.append(f'<rect x="{x0 + inset}" y="{y0 + inset}" width="{bw - 2 * inset}" height="{bh - 2 * inset}" rx="14" fill="{fill}" stroke="{ink}" stroke-width="2"/>')
        out.append(f'<text x="{x0 + inset + 14}" y="{y0 + inset + 22}" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="{ink}">{esc(name)}</text>')
        out.append(f'<text x="{x0 + inset + 90}" y="{y0 + inset + 22}" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#202124">{esc(note)}</text>')
    inset = len(TIERS) * 34
    out.append(f'<rect x="{x0 + inset}" y="{y0 + inset}" width="{bw - 2 * inset}" height="{bh - 2 * inset}" rx="14" fill="#202124"/>')
    out.append(f'<text x="{x0 + bw / 2}" y="{y0 + bh / 2 - 6}" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="18" font-weight="700" fill="#FFFFFF">core</text>')
    out.append(f'<text x="{x0 + bw / 2}" y="{y0 + bh / 2 + 16}" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#D3E3FD">permission prompt, the tool itself</text>')
    ax_in, ax_out = x0 + bw - 150, x0 + bw - 100
    out.append(f'<path d="M {ax_in} {y0 + 8} L {ax_in} {y0 + inset - 10}" stroke="#0B57D0" stroke-width="3" marker-end="url(#a)"/>')
    out.append(f'<path d="M {ax_out} {y0 + inset - 4} L {ax_out} {y0 + 14}" stroke="#137333" stroke-width="3" marker-end="url(#b)"/>')
    out.append(f'<text x="{ax_in - 8}" y="{y0 + 22}" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="11" font-weight="700" fill="#0B57D0">event in</text>')
    out.append(f'<text x="{ax_out + 18}" y="{y0 + 22}" font-family="Helvetica, Arial, sans-serif" font-size="11" font-weight="700" fill="#137333">result out</text>')
    out.insert(4, '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#0B57D0"/></marker>'
                  '<marker id="b" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#137333"/></marker></defs>')
    out.append('<text x="680" y="120" font-family="Helvetica, Arial, sans-serif" font-size="16" font-weight="700" fill="#202124">Three moves per hook</text>')
    for i, (move, code) in enumerate(MOVES):
        y = 150 + i * 92
        out.append(f'<rect x="680" y="{y}" width="248" height="76" rx="10" fill="#F8F9FA" stroke="#DADCE0"/>')
        out.append(f'<text x="696" y="{y + 28}" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="700" fill="#202124">{esc(move)}</text>')
        out.append(f'<text x="696" y="{y + 54}" font-family="Menlo, Consolas, monospace" font-size="12" fill="#3C4043">{esc(code)}</text>')
    out.append('<text x="680" y="440" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#5F6368">A guard needs .catch failing closed:</text>')
    out.append('<text x="680" y="460" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#5F6368">a hook that times out is skipped.</text>')
    out.append('<text x="680" y="500" font-family="Helvetica, Arial, sans-serif" font-size="11" fill="#5F6368">Source: types 2.1.288 L11897-11907; docs-mods-events</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
