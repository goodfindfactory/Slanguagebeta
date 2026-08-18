#!/usr/bin/env python3
"""Verify all SlanguageOS entry points run through unified bootstrap."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable
SLANGUAGE_BIN = Path("/Library/Frameworks/Python.framework/Versions/3.13/bin/slanguage")


class Check:
    def __init__(self, name: str, ok: bool, detail: str = ""):
        self.name = name
        self.ok = ok
        self.detail = detail


def run_cmd(name: str, cmd: list[str], *, expect_code: int = 0, expect_in: str | None = None) -> Check:
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "") + (result.stderr or "")
    ok = result.returncode == expect_code
    if expect_in and expect_in not in output:
        ok = False
    detail = output.strip().splitlines()[-1] if output.strip() else f"exit {result.returncode}"
    if not ok and output.strip():
        detail = output.strip()[-400:]
    return Check(name, ok, detail)


def main() -> int:
    checks: list[Check] = []

    checks.append(run_cmd("tests", [PYTHON, "run_tests.py"], expect_in="OK"))
    checks.append(
        run_cmd(
            "terrain mapper",
            [
                PYTHON,
                "-c",
                "from slanguage.terrain import TerrainMapperAgent, render_map, run_command; "
                "a=TerrainMapperAgent(); r=run_command(a, ['goto','37.7','-122.4']); "
                "assert r['status']=='ARRIVED'; assert '@' in render_map(a); print('terrain ok')",
            ],
            expect_in="terrain ok",
        )
    )
    checks.append(run_cmd("demo", [PYTHON, "examples/demo.py"], expect_in="SlanguageOS smoke demo"))
    checks.append(
        run_cmd(
            "run.py --once",
            [PYTHON, "run.py", "--once", "spy status"],
            expect_in="[terse]",
        )
    )
    checks.append(
        run_cmd(
            "run.py guest lock",
            [PYTHON, "run.py", "--once", "hello", "--entity", "guest"],
            expect_in="[OMNI-LOCK]",
        )
    )
    checks.append(
        run_cmd(
            "module -m slanguage.cli.main",
            [PYTHON, "-m", "slanguage.cli.main", "--once", "ponder why"],
            expect_in="[reflective]",
        )
    )
    checks.append(
        run_cmd(
            "bootstrap import",
            [
                PYTHON,
                "-c",
                "from slanguage.bootstrap import build, get_categories, get_constructs; "
                "rt=build(); assert get_constructs(rt); assert get_categories(); print('bootstrap ok')",
            ],
            expect_in="bootstrap ok",
        )
    )
    checks.append(
        run_cmd(
            "gui import",
            [
                PYTHON,
                "-c",
                "from slanguage.gui.app import SlanguageGUI; "
                "g=SlanguageGUI(); g.root.update(); g.root.destroy(); print('gui ok')",
            ],
            expect_in="gui ok",
        )
    )

    if SLANGUAGE_BIN.exists():
        checks.append(
            run_cmd(
                "slanguage entry point",
                [str(SLANGUAGE_BIN), "--once", "diva hey"],
                expect_in="[playful]",
            )
        )

    print("SlanguageOS unified verification\n" + "=" * 40)
    failed = 0
    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        print(f"[{status}] {check.name}")
        if check.detail:
            print(f"       {check.detail}")
        if not check.ok:
            failed += 1

    print("=" * 40)
    print(f"{len(checks) - failed}/{len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
