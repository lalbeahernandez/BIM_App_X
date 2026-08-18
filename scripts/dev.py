#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "services" / "api"
WEB_DIR = ROOT / "apps" / "web"
NPM = "npm.cmd" if os.name == "nt" else "npm"


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print(f"+ {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=cwd)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def verify() -> None:
    run([sys.executable, "scripts/verify_harness.py"])


def codex_tasks() -> None:
    run([sys.executable, "scripts/validate_codex_tasks.py"])


def lint_api() -> None:
    run([sys.executable, "-m", "ruff", "check", "app", "tests"], cwd=API_DIR)


def lint_web() -> None:
    run([NPM, "run", "lint"], cwd=WEB_DIR)


def lint() -> None:
    lint_api()
    lint_web()


def typecheck_api() -> None:
    run([sys.executable, "-m", "mypy", "app"], cwd=API_DIR)


def typecheck_web() -> None:
    run([NPM, "run", "typecheck"], cwd=WEB_DIR)


def typecheck() -> None:
    typecheck_api()
    typecheck_web()


def test() -> None:
    run([sys.executable, "-m", "pytest", "-q"], cwd=API_DIR)


def smoke() -> None:
    run([sys.executable, "scripts/smoke_http.py"])


def performance_budgets() -> None:
    run([sys.executable, "scripts/check_performance_budgets.py"])


COMMANDS = {
    "verify": verify,
    "codex-tasks": codex_tasks,
    "performance-budgets": performance_budgets,
    "lint": lint,
    "lint-api": lint_api,
    "lint-web": lint_web,
    "typecheck": typecheck,
    "typecheck-api": typecheck_api,
    "typecheck-web": typecheck_web,
    "test": test,
    "smoke": smoke,
}


def all_gates() -> None:
    for name in ["verify", "codex-tasks", "lint", "typecheck", "test", "smoke"]:
        COMMANDS[name]()


COMMANDS["all"] = all_gates


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        names = ", ".join(sorted(COMMANDS))
        raise SystemExit(f"Usage: python scripts/dev.py <command>\nCommands: {names}")
    COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    main()
