#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def _parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_inline_list(value: str) -> list[str]:
    value = value.strip()
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item) for item in inner.split(",")]
    return [_parse_scalar(value)] if value else []


def parse_tasks_yaml(path: Path) -> dict[str, dict[str, list[str]]]:
    tasks: dict[str, dict[str, list[str]]] = {}
    current_id: str | None = None
    reading_deps = False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped == "tasks:":
            continue

        if line.startswith("- id:"):
            current_id = _parse_scalar(line.split(":", 1)[1])
            tasks[current_id] = {"depends_on": []}
            reading_deps = False
            continue

        if current_id is None:
            continue

        if stripped.startswith("depends_on:"):
            reading_deps = True
            _, value = stripped.split(":", 1)
            tasks[current_id]["depends_on"] = _parse_inline_list(value)
            continue

        if reading_deps:
            if stripped.startswith("- "):
                tasks[current_id]["depends_on"].append(_parse_scalar(stripped[2:]))
                continue
            reading_deps = False

    return tasks


p = Path(__file__).resolve().parents[1] / "codex" / "tasks.yaml"
tasks = parse_tasks_yaml(p)
missing = []
for tid, t in tasks.items():
    for dep in t.get("depends_on", []):
        if dep not in tasks:
            missing.append((tid, dep))
if missing:
    raise SystemExit(f"Missing dependencies: {missing}")
# cycle detection
seen = set()
active = set()


def dfs(n):
    if n in active:
        raise SystemExit(f"Dependency cycle at {n}")
    if n in seen:
        return
    active.add(n)
    for d in tasks[n].get("depends_on", []):
        dfs(d)
    active.remove(n)
    seen.add(n)


for n in tasks:
    dfs(n)
print(f"OK: {len(tasks)} tasks, dependencies valid, no cycles")
