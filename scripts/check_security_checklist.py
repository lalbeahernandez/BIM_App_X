#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(name: str, text: str, needle: str) -> None:
    if needle not in text:
        raise SystemExit(f"SECURITY CHECKLIST FAILED: {name} missing {needle!r}")


def require_any(name: str, text: str, needles: list[str]) -> None:
    if not any(needle in text for needle in needles):
        raise SystemExit(f"SECURITY CHECKLIST FAILED: {name} missing one of {needles!r}")


def main() -> None:
    threat_model = read("docs/THREAT_MODEL.md")
    checklist = read("tests/security/README.md")
    api = read("services/api/app/main.py")
    schemas = read("services/api/app/schemas.py")
    worker = read("services/bim-worker/worker.py")
    sql = read("db/init/010_schema.sql")

    for section in [
        "# Threat Model - AUD-006",
        "## Trust Boundaries",
        "## Current Controls",
        "## Top Risks",
        "## STRIDE Summary",
        "## Security Checklist",
    ]:
        require("threat model section", threat_model, section)

    for risk_id in [f"AUD006-R{i}" for i in range(1, 9)]:
        require("top risk", threat_model, risk_id)

    for control_id in [
        "AUD006-TEN-001",
        "AUD006-TEN-002",
        "AUD006-UPL-001",
        "AUD006-UPL-002",
        "AUD006-UPL-003",
        "AUD006-UPL-004",
        "AUD006-JOB-001",
        "AUD006-JOB-002",
        "AUD006-BIM-001",
        "AUD006-BIM-002",
        "AUD006-AUD-001",
        "AUD006-API-001",
    ]:
        require("current control", threat_model, control_id)

    for check_id in [
        "SEC-AUD006-TEN-001",
        "SEC-AUD006-UPL-001",
        "SEC-AUD006-JOB-001",
        "SEC-AUD006-AUD-001",
        "SEC-AUD006-BIM-001",
        "SEC-AUD006-API-001",
    ]:
        require("security checklist", checklist, check_id)

    require("tenant org filter", api, "organization_id=:org")
    require("selection no-echo scoping", api, "WHERE e.id = ANY(:ids) AND p.organization_id=:org")
    require("boq same-project join", api, "b.project_id=p.id")
    require("activity same-project join", api, "a.project_id=p.id")

    require("ifc extension check", api, "file.filename.lower().endswith('.ifc')")
    require("upload size guard", api, "1024 * 1024 * 1024")
    require("server generated artifact path", api, "file_path = upload_dir / f'{revision_id}.ifc'")
    require("revision checksum", api, "hashlib.sha256(data).hexdigest()")
    require("upload outbox", api, "enqueue_outbox")
    require("upload audit", api, "record_audit")
    require("worker enqueue", api, "redis_client.lpush")

    require("selection id lower bound", schemas, "min_length=1")
    require("selection id upper bound", schemas, "max_length=1000")

    require("worker consumes queue", worker, "brpop")
    require("worker parses ifc", worker, "ifcopenshell.open")
    require("worker failed status", worker, "status='FAILED'")
    require("worker bounded error", worker, "str(exc)[:4000]")

    require("bim identity revision scoped", sql, "UNIQUE (revision_id, global_id)")
    require("element lineage table", sql, "CREATE TABLE IF NOT EXISTS element_lineage")
    require("audit table", sql, "CREATE TABLE IF NOT EXISTS audit_events")
    require("outbox table", sql, "CREATE TABLE IF NOT EXISTS outbox_events")
    require_any("model revision status", sql, ["CHECK (status IN ('QUEUED','PROCESSING','READY','FAILED'))"])

    print("SECURITY CHECKLIST: OK")


if __name__ == "__main__":
    main()
