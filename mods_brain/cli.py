"""Command-line entry point for the Claude Mods Brain tools.

Every command reads files only: nothing loads a mod, touches the network, or reads credentials.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable


def run_script(script: str, args: list[str]) -> int:
    return subprocess.call([PY, str(REPO / "scripts" / script), *args], cwd=REPO)


def here(path: str) -> str:
    """Resolve a path argument against the caller's cwd, since scripts run with cwd=REPO."""
    return str(Path(path).expanduser().resolve()) if path else path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mods-brain", description="Offline tools for Claude Code mods.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_audit = sub.add_parser("audit-mod", help="statically scan a mod and write its audit note")
    p_audit.add_argument("plugin", help="mod plugin directory (the folder holding .claude-plugin/plugin.json)")
    p_audit.add_argument("--origin", required=True, help="where the mod came from, e.g. owner/repo@abc1234")
    p_audit.add_argument("--tested-on", required=True, help="Claude Code version you checked against")
    p_audit.add_argument("--date", required=True, help="ISO date for the report")
    p_audit.add_argument("--validate-json", default="", help="optional file holding `claude plugin validate --json` output")
    p_audit.add_argument("--out-dir", default="wiki/reports")
    p_surface = sub.add_parser("surface", help="import Claude Code's mod type definitions into an API surface JSON")
    p_surface.add_argument("--capture", required=True, help="directory holding claude-code/index.d.ts")
    p_surface.add_argument("--out", required=True)
    p_drift = sub.add_parser("drift", help="compare two API surfaces; exit 1 when anything changed")
    p_drift.add_argument("--old", required=True)
    p_drift.add_argument("--new", required=True)
    p_drift.add_argument("--out", required=True)
    p_drift.add_argument("--markdown", default="")
    p_lint = sub.add_parser("lint", help="check the vault's links, frontmatter, and structure")
    p_lint.add_argument("--vault", default=".")
    args = parser.parse_args(argv)

    if args.command == "audit-mod":
        plugin = Path(args.plugin).expanduser().resolve()
        scan = REPO / "references" / "data" / "scans" / f"{plugin.name}.json"
        call = ["--plugin", str(plugin), "--out", str(scan)]
        if args.validate_json:
            call += ["--validate-json", here(args.validate_json)]
        code = run_script("scan_mod.py", call)
        if code:
            return code
        out = Path(here(args.out_dir)) if Path(args.out_dir).is_absolute() else REPO / args.out_dir
        return run_script("render_mod_audit.py", ["--scan", str(scan), "--out", str(out / f"Mod Audit {plugin.name}.md"),
                                                  "--date", args.date, "--tested-on", args.tested_on, "--origin", args.origin])
    if args.command == "surface":
        return run_script("import_mod_types.py", ["--capture", here(args.capture), "--out", here(args.out)])
    if args.command == "drift":
        call = ["--old", here(args.old), "--new", here(args.new), "--out", here(args.out), "--wiki", str(REPO / "wiki")]
        if args.markdown:
            call += ["--markdown", here(args.markdown)]
        return run_script("diff_api_surface.py", call)
    if args.command == "lint":
        return run_script("lint_vault.py", ["--vault", here(args.vault)])
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
