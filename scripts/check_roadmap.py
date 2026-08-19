#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "docs" / "TECHNICAL_ROADMAP_V1.md"
TASKS = ROOT / "codex" / "tasks.yaml"
STATUS = ROOT / "codex" / "task-status.csv"

REQUIRED_TASK_IDS = [*(f"AUD-{number:03d}" for number in range(1, 9)), "FND-001"]
REQUIRED_RELEASES = {
    "R0": "Audited Harness",
    "R1": "Foundation",
    "R2": "BIM Core",
    "R3": "BIM Work Area",
    "R4": "4D/5D Controls",
    "R5": "Project Controls Beta",
    "R6": "Pilot Ready",
    "R7": "Full Enterprise",
}
REQUIRED_SOURCE_REFS = [
    "docs/ARCHITECTURE.md",
    "docs/adr/*",
    "docs/DOMAIN_MODEL.md",
    "docs/DOMAIN_SCHEMA_MATRIX.md",
    "docs/PERFORMANCE_BUDGETS.md",
    "config/performance-budgets.json",
    "docs/THREAT_MODEL.md",
    "fixtures/manifest.json",
    "docs/FIXTURE_CATALOG.md",
    "codex/tasks.yaml",
    "codex/task-status.csv",
    "codex/RELEASE_GATES.md",
]
TASK_ID_RE = re.compile(r"(?<!F-)\b(?:AUD|FND|BIM|VWR|BOQ|SCH|D4|PRG|COL|ADV|ENT)-\d{3}\b")
FINDING_ROW_RE = re.compile(r"^\| F-[^|]+\| (?P<severity>P[012]) \| [^|]+ \| [^|]+ \| (?P<owner>[^|]+) \|")


def parse_tasks_yaml(path: Path) -> set[str]:
    task_ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- id:"):
            task_ids.add(line.split(":", 1)[1].strip().strip("'\""))
    return task_ids


def parse_status_csv(path: Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            statuses[row["id"]] = row["status"]
    return statuses


def main() -> int:
    failures: list[str] = []
    if not ROADMAP.is_file():
        failures.append("docs/TECHNICAL_ROADMAP_V1.md is missing")
        print_failures(failures)
        return 1

    roadmap = ROADMAP.read_text(encoding="utf-8")
    task_ids = parse_tasks_yaml(TASKS)
    statuses = parse_status_csv(STATUS)

    for task_id in REQUIRED_TASK_IDS:
        if task_id not in task_ids:
            failures.append(f"{task_id} missing from codex/tasks.yaml")
        if task_id not in statuses:
            failures.append(f"{task_id} missing from codex/task-status.csv")

    for release_id, release_name in REQUIRED_RELEASES.items():
        if release_id not in roadmap or release_name not in roadmap:
            failures.append(f"{release_id} {release_name} missing from roadmap")

    for source_ref in REQUIRED_SOURCE_REFS:
        if source_ref not in roadmap:
            failures.append(f"source-of-truth reference missing: {source_ref}")

    unknown_refs = sorted({task_id for task_id in TASK_ID_RE.findall(roadmap) if task_id not in task_ids})
    if unknown_refs:
        failures.append(f"roadmap references unknown task IDs: {unknown_refs}")

    for line in roadmap.splitlines():
        match = FINDING_ROW_RE.match(line)
        if not match:
            continue
        if match.group("severity") not in {"P0", "P1"}:
            continue
        owner_field = match.group("owner").strip()
        owner_ids = TASK_ID_RE.findall(owner_field)
        if not owner_ids and "UNOWNED_GAP" not in owner_field:
            failures.append(f"P0/P1 finding has no owner task or UNOWNED_GAP: {line}")
        for owner_id in owner_ids:
            if owner_id not in task_ids:
                failures.append(f"P0/P1 owner task does not exist: {owner_id}")

    if "No open P0 blocks FND-001." not in roadmap:
        failures.append("roadmap does not explicitly state that no P0 blocks FND-001")

    if failures:
        print_failures(failures)
        return 1
    print("ROADMAP CHECK: OK")
    return 0


def print_failures(failures: list[str]) -> None:
    print("ROADMAP CHECK: FAIL")
    for failure in failures:
        print(f"- {failure}")


if __name__ == "__main__":
    sys.exit(main())
