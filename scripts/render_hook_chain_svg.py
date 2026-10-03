#!/usr/bin/env python3
"""Render _attachments/mods-hook-chain.svg: the five hook tiers around core, and the three moves.

Facts drawn (Claude Code 2.1.288): hooks for one event nest outermost first as
prepend, user, append, builtin, core (types 2.1.288 L11897-11907; docs-mods-events);
a hook observes (await next, return the result), rewrites (next with a copy), or
answers (return without calling next). Styled to match the README hero: warm dark
ground, serif headings, mono labels, clay accent. A clay pulse travels in through the
tiers to the core and back out (SVG animation; a still diagram where unsupported).
Deterministic output, no dashes.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_attachments" / "mods-hook-chain.svg"

W, H = 1280, 690
BG, SURF, LINE = "#191917", "#22211f", "#3a3833"
TEXT, MUTED, DIM = "#FAF9F5", "#a6a39a", "#7a766c"
CLAY = "#D97757"
SERIF = "'Source Serif 4', Georgia, 'Times New Roman', serif"
SANS = "'IBM Plex Sans', 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'IBM Plex Mono', ui-monospace, Menlo, Consolas, monospace"

# tier name, note, accent, fill
TIERS = [
    ("prepend", "org mods: sec-default, prependPlugins", "#D97757", "#1e1d1b"),
    ("user", "mods a person installs", "#C9A35A", "#22211e"),
    ("append", "org mods: appendPlugins", "#8FB3E0", "#262522"),
    ("builtin", "mods bundled in Claude Code", "#7FB58A", "#2a2926"),
]
MOVES = [
    ("Observe", "r = await next(e); return r"),
    ("Rewrite", "return next({ ...e, field })"),
    ("Answer", "return { deny } or { result }"),
]
X0, Y0, BW, BH, INSET = 64, 160, 700, 460, 40
IN_X, OUT_X = 530, 572  # inside the core's x range, right of every tier note


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x: float, y: float, s: str, *, family: str = SANS, size: int = 15, fill: str = TEXT, weight: int = 400,
      anchor: str = "start") -> str:
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}">{esc(s)}</text>')


def render() -> str:
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-labelledby="hc-t hc-d">',
        '<title id="hc-t">How one event runs through mods</title>',
        '<desc id="hc-d">Five nested tiers, outermost first: prepend, user, append, builtin, then core. An event enters at '
        'the outer tier and the result returns outward. Each hook can observe, rewrite, or answer.</desc>',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        t(64, 86, "How one event runs through mods", family=SERIF, size=36, weight=600),
        t(64, 122, "Claude Code 2.1.288. Outer tiers see the event first and the result last; "
                   "an inner hook cannot hide anything from an outer one.", size=15, fill=MUTED),
    ]
    for i, (name, note, accent, fill) in enumerate(TIERS):
        x, y = X0 + i * INSET, Y0 + i * INSET
        w, h = BW - 2 * i * INSET, BH - 2 * i * INSET
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{accent}" stroke-opacity="0.55" stroke-width="1.4"/>')
        out.append(t(x + 18, y + 26, name, family=MONO, size=14, fill=accent, weight=500))
        out.append(t(x + 98, y + 26, note, size=13, fill=MUTED))
    cx, cy = X0 + 4 * INSET, Y0 + 4 * INSET
    cw, ch = BW - 8 * INSET, BH - 8 * INSET
    out.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" fill="{TEXT}"/>')
    out.append(t(cx + cw / 2, cy + 70, "core", family=SERIF, size=28, fill=BG, weight=600, anchor="middle"))
    out.append(t(cx + cw / 2, cy + 98, "the permission prompt, then the tool itself", size=13, fill="#4a4740", anchor="middle"))
    top, bottom = Y0 - 12, cy - 4
    out.append(f'<line x1="{IN_X}" y1="{top}" x2="{IN_X}" y2="{bottom - 10}" stroke="{CLAY}" stroke-width="2"/>')
    out.append(f'<path d="M{IN_X - 6} {bottom - 12} L{IN_X} {bottom} L{IN_X + 6} {bottom - 12} Z" fill="{CLAY}"/>')
    out.append(f'<line x1="{OUT_X}" y1="{bottom}" x2="{OUT_X}" y2="{top + 10}" stroke="{TEXT}" stroke-opacity="0.7" stroke-width="2"/>')
    out.append(f'<path d="M{OUT_X - 6} {top + 12} L{OUT_X} {top} L{OUT_X + 6} {top + 12} Z" fill="{TEXT}" fill-opacity="0.7"/>')
    out.append(f'<path id="hc-loop" d="M{IN_X} {top} L{IN_X} {bottom} L{OUT_X} {bottom} L{OUT_X} {top}" fill="none" stroke="none"/>')
    out.append(f'<g><circle r="11" fill="{CLAY}" fill-opacity="0.22"/><circle r="5" fill="{CLAY}"/>'
               f'<animateMotion dur="4.5s" repeatCount="indefinite" calcMode="linear"><mpath href="#hc-loop" xlink:href="#hc-loop"/></animateMotion></g>')
    ly = Y0 + BH + 40
    out.append(f'<circle cx="{X0 + 6}" cy="{ly - 5}" r="5" fill="{CLAY}"/>')
    out.append(t(X0 + 20, ly, "event in", family=MONO, size=13, fill=MUTED))
    out.append(f'<circle cx="{X0 + 120}" cy="{ly - 5}" r="5" fill="{TEXT}" fill-opacity="0.7"/>')
    out.append(t(X0 + 134, ly, "result out", family=MONO, size=13, fill=MUTED))
    rx = 820
    out.append(t(rx, 192, "Three moves per hook", family=SERIF, size=24, weight=600))
    for i, (move, code) in enumerate(MOVES):
        y = 216 + i * 108
        out.append(f'<rect x="{rx}" y="{y}" width="396" height="92" rx="12" fill="{SURF}" stroke="{LINE}"/>')
        out.append(t(rx + 20, y + 36, move, size=17, weight=600))
        out.append(t(rx + 20, y + 66, code, family=MONO, size=14, fill="#e8a88e"))
    out.append(t(rx, 568, "A guard needs a .catch that fails closed:", size=14, fill=MUTED))
    out.append(t(rx, 590, "a hook that times out is skipped.", size=14, fill=MUTED))
    out.append(t(rx, ly, "Source: types 2.1.288 L11897-11907, docs-mods-events", family=MONO, size=12, fill=DIM))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
