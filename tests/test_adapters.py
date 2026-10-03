#!/usr/bin/env python3
"""Tests for the mods-brain domain adapters.

Runs as a plain script (`python tests/test_adapters.py`) or under pytest.
Covers: typings import, API drift, mod scan red flags and reach, synthesis
verdicts, renderers, malformed input, and the no-absolute-path rule.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIX = REPO / "tests" / "fixtures"
PY = sys.executable
sys.path.insert(0, str(REPO / "scripts"))

import diff_api_surface  # noqa: E402
import import_mod_types  # noqa: E402
import scan_mod  # noqa: E402
import synthesize_mods  # noqa: E402


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([PY, *args], cwd=REPO, text=True, capture_output=True, check=False)


def test_import_mini_surface() -> None:
    s = import_mod_types.import_capture(FIX / "types-mini")
    assert s["schema"] == "mods-brain.api-surface.v1"
    assert s["claude_code_version"] == "9.9.1"
    assert [e["name"] for e in s["events"]["engine"]] == ["tool.call", "turn.complete"]
    assert s["events"]["engine"][0]["summary"] == "Fires when the engine is about to run a tool."
    assert [e["name"] for e in s["events"]["op"]] == ["ui.toast", "session.usage"]
    assert s["events"]["classic"] == ["classic.Stop"]
    ns = {n["name"]: [m["name"] for m in n["members"]] for n in s["namespaces"]}
    assert ns == {"ui": ["toast", "resolve"], "session": ["usage"]}
    assert s["render_components"]["values"] == ["AbovePrompt", "Pane"]
    assert s["elements"]["desktop"]["elements"] == ["Box", "Svg"]
    assert all(isinstance(e["line"], int) and e["line"] > 0 for e in s["events"]["engine"])


def test_import_rejects_malformed() -> None:
    try:
        import_mod_types.import_capture(FIX / "types-malformed")
    except import_mod_types.ImportErrorBadInput:
        pass
    else:
        raise AssertionError("malformed typings accepted")
    proc = run("scripts/import_mod_types.py", "--capture", str(FIX / "missing-dir"), "--out", "/dev/null")
    assert proc.returncode == 2 and "ERROR" in proc.stderr


def test_drift_detects_changes() -> None:
    old = import_mod_types.import_capture(FIX / "types-mini")
    new = import_mod_types.import_capture(FIX / "types-mini-next")
    report = diff_api_surface.diff(old, new)
    assert report["from_version"] == "9.9.1" and report["to_version"] == "9.9.2"
    assert report["sections"]["engine_events"]["added"] == ["ui.close"]
    assert report["sections"]["render_components"]["added"] == ["Spinner"]
    assert [c["name"] for c in report["signatures_changed"]] == ["$.ui.toast"]
    limits = report["sections"]["limits"]
    assert any("15_000" in t for t in limits["added"]) and any("10_000" in t for t in limits["removed"])
    assert report["change_count"] == 2 + 1 + len(limits["added"]) + len(limits["removed"])
    assert report["manual_review_required"] is False
    same = diff_api_surface.diff(old, old)
    assert same["change_count"] == 0 and same["typings_identical"]
    with tempfile.TemporaryDirectory() as tmp:
        wiki = Path(tmp)
        (wiki / "Budgets.md").write_text("A hook gets 10,000 ms of its own time.")
        (wiki / "Toast.md").write_text("Call $.ui.toast to show a line.")
        (wiki / "Other.md").write_text("Nothing relevant.")
        assert diff_api_surface.affected_notes(report, wiki) == ["Budgets.md", "Toast.md"]
    md = diff_api_surface.render_markdown({**report, "affected_notes": []})
    assert "`ui.close`" in md and "\u2014" not in md


def test_drift_cli_exit_codes_and_bad_input() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        for name in ("types-mini", "types-mini-next"):
            assert run("scripts/import_mod_types.py", "--capture", str(FIX / name), "--out", str(t / f"{name}.json")).returncode == 0
        same = run("scripts/diff_api_surface.py", "--old", str(t / "types-mini.json"), "--new", str(t / "types-mini.json"), "--out", str(t / "d0.json"))
        assert same.returncode == 0
        drift = run("scripts/diff_api_surface.py", "--old", str(t / "types-mini.json"), "--new", str(t / "types-mini-next.json"), "--out", str(t / "d1.json"))
        assert drift.returncode == 1
        (t / "bad.json").write_text('{"schema": "other"}')
        bad = run("scripts/diff_api_surface.py", "--old", str(t / "bad.json"), "--new", str(t / "types-mini.json"), "--out", str(t / "d2.json"))
        assert bad.returncode == 2


def test_scan_clean_band() -> None:
    r = scan_mod.scan(FIX / "mods" / "clean-band")
    assert r["is_mod"] and r["module"] == "./register.ts"
    assert r["reach"] == "L0"
    assert r["events"] == {"ui.render": ["{ component: 'AbovePrompt' }"]}
    assert r["calls"] == {"session.usage": 1, "ui.resolve": 1}
    assert r["red_flags"] == [] and r["cost_surface"] == []
    assert "module-variable-state" not in {f["code"] for f in r["red_flags"]}


def test_scan_risky_mod_flags() -> None:
    r = scan_mod.scan(FIX / "mods" / "risky-mod")
    codes = {f["code"]: f["severity"] for f in r["red_flags"]}
    assert codes["fetch-then-run"] == "critical"
    assert codes["tool-check-allow"] == "critical"
    assert codes["env-read"] == "high"
    assert codes["submit-as-user"] == "high"
    assert codes["acts-on-other-mods"] == "high"
    assert codes["absolute-fs-path"] == "high"
    assert codes["guard-without-catch"] == "medium"
    assert codes["event-rewrite"] == "review"
    assert codes["module-variable-state"] == "review"
    assert codes["reads-claude-internals"] == "medium"
    assert r["reach"] == "L3"
    assert r["classic_hooks"] == ["Stop"]
    assert r["plugin"]["user_config"] == ["endpoint"]
    assert "absolute-config-default" not in codes
    cost = {c.get("call") or c.get("event") for c in r["cost_surface"]}
    assert {"model.complete", "prompt.submit", "prompt.section"} <= cost


def test_scan_flags_absolute_config_default() -> None:
    import shutil
    with tempfile.TemporaryDirectory() as tmp:
        mod = Path(tmp) / "band"
        shutil.copytree(FIX / "mods" / "clean-band", mod)
        manifest = json.loads((mod / ".claude-plugin" / "plugin.json").read_text())
        manifest["userConfig"] = {"notes": {"type": "string", "default": "~/notes/voice.md"}, "label": {"type": "string", "default": "x"}}
        (mod / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest))
        flags = {f["code"]: f for f in scan_mod.scan(mod)["red_flags"]}
        assert flags["absolute-config-default"]["severity"] == "review"
        assert "notes" in flags["absolute-config-default"]["detail"] and "label" not in flags["absolute-config-default"]["detail"]


def test_scan_rejects_bad_inputs() -> None:
    for name, needle in (("bad-modules", "exactly one"), ("broken-json", "not valid JSON")):
        try:
            scan_mod.scan(FIX / "mods" / name)
        except scan_mod.ScanError as exc:
            assert needle in str(exc), exc
        else:
            raise AssertionError(f"{name} accepted")
    try:
        scan_mod.scan(FIX / "mods" / "does-not-exist")
    except scan_mod.ScanError:
        pass
    else:
        raise AssertionError("missing dir accepted")


def test_synthesis_and_renderers_end_to_end() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        scans = t / "scans"
        scans.mkdir()
        assert run("scripts/import_mod_types.py", "--capture", str(FIX / "types-mini"), "--out", str(t / "s.json")).returncode == 0
        for mod in ("clean-band", "risky-mod"):
            assert run("scripts/scan_mod.py", "--plugin", str(FIX / "mods" / mod), "--out", str(scans / f"{mod}.json")).returncode == 0
        p = run("scripts/synthesize_mods.py", "--surface", str(t / "s.json"), "--scans", str(scans), "--catalog", str(FIX / "catalog-mini.json"), "--out", str(t / "syn.json"))
        assert p.returncode == 0, p.stderr
        syn = json.loads((t / "syn.json").read_text())
        verdicts = {m["name"]: m["verdict_suggestion"] for m in syn["mods"]}
        assert verdicts == {"clean-band": "adopt-candidate", "risky-mod": "avoid"}
        assert syn["catalog"][0]["scan_reach"] == "L0"
        # the mini surface lacks these engine events, so synthesis reports them as drift
        assert set(syn["unknown_events"]) == {"ui.render", "plugin.register", "prompt.section", "session.start", "tool.check"}
        assert syn["event_matrix"]["tool.call"] == ["risky-mod"]
        outputs = {
            "audit.md": run("scripts/render_mod_audit.py", "--scan", str(scans / "risky-mod.json"), "--out", str(t / "audit.md"), "--date", "2026-10-03", "--tested-on", "9.9.1", "--origin", "fixtures/risky-mod"),
            "matrix.md": run("scripts/render_capability_matrix.py", "--synthesis", str(t / "syn.json"), "--out", str(t / "matrix.md"), "--date", "2026-10-03"),
            "api.md": run("scripts/render_api_cheatsheet.py", "--surface", str(t / "s.json"), "--out", str(t / "api.md"), "--date", "2026-10-03"),
        }
        for name, proc in outputs.items():
            assert proc.returncode == 0, proc.stderr
            text = (t / name).read_text()
            assert text.startswith("---\n") and 'domain: "Claude Code mods"' in text
            assert "\u2014" not in text and "\u2013" not in text
            assert "/var/home" not in text and "/home/" not in text
            assert text.count("[[") >= 8, name
        assert "fetch-then-run" in (t / "audit.md").read_text()
        refused = run("scripts/render_mod_audit.py", "--scan", str(scans / "risky-mod.json"), "--out", str(t / "x.md"), "--date", "2026-10-03", "--tested-on", "9.9.1", "--origin", "/abs/path")
        assert refused.returncode == 2


def test_verdict_rule_caps_medium_flags_and_classic_hooks() -> None:
    base = {"reach": "L0", "red_flags": [], "classic_hooks": []}
    assert synthesize_mods.verdict(base)[0] == "adopt-candidate"
    medium = {**base, "red_flags": [{"code": "guard-without-catch", "severity": "medium"}]}
    assert synthesize_mods.verdict(medium) == ("trial", "needs a human read for: guard-without-catch")
    review_only = {**base, "red_flags": [{"code": "event-rewrite", "severity": "review"}]}
    assert synthesize_mods.verdict(review_only)[0] == "adopt-candidate"
    classic = {**base, "classic_hooks": ["Stop"]}
    assert synthesize_mods.verdict(classic)[0] == "trial"
    critical = {**base, "red_flags": [{"code": "fetch-then-run", "severity": "critical"}]}
    assert synthesize_mods.verdict(critical)[0] == "avoid"


def test_synthesis_rejects_wrong_schema() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "scans").mkdir()
        (t / "s.json").write_text('{"schema": "nope"}')
        p = run("scripts/synthesize_mods.py", "--surface", str(t / "s.json"), "--scans", str(t / "scans"), "--out", str(t / "o.json"))
        assert p.returncode == 2


def test_outputs_match_json_schemas() -> None:
    try:
        import jsonschema
    except ImportError:
        print("skip schema validation: jsonschema not installed")
        return
    schemas = REPO / "schemas"
    load = lambda n: json.loads((schemas / n).read_text())  # noqa: E731
    surface = import_mod_types.import_capture(FIX / "types-mini")
    jsonschema.validate(surface, load("api-surface.v1.schema.json"))
    nxt = import_mod_types.import_capture(FIX / "types-mini-next")
    jsonschema.validate(diff_api_surface.diff(surface, nxt), load("api-drift.v1.schema.json"))
    scans = [scan_mod.scan(FIX / "mods" / m) for m in ("clean-band", "risky-mod")]
    for scan in scans:
        jsonschema.validate(scan, load("mod-scan.v1.schema.json"))
    jsonschema.validate(synthesize_mods.synthesize(surface, scans, None), load("synthesis.v1.schema.json"))
    jsonschema.validate(json.loads((FIX / "catalog-mini.json").read_text()), load("catalog.v1.schema.json"))


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
        print(f"ok {test.__name__}")
    print(f"{len(tests)} adapter tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
