#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "fixtures" / "manifest.json"
SUPPORTED_SCHEMA_VERSION = 1

REQUIRED_FIELDS = {
    "id",
    "category",
    "path",
    "description",
    "format",
    "version",
    "source",
    "provenance",
    "license",
    "redistribution_allowed",
    "sha256",
    "size_bytes",
    "synthetic",
    "contains_customer_data",
    "contains_personal_data",
    "contains_secrets",
    "deterministic",
    "intended_tests",
    "status",
}
ALLOWED_CATEGORIES = {
    "IFC",
    "BOQ",
    "SCHEDULE",
    "BCF",
    "PROGRESS",
    "SECURITY",
    "DOMAIN_SCHEMA",
    "API",
    "PERFORMANCE",
    "GOLDEN_OUTPUT",
}
ALLOWED_STATUSES = {
    "ACTIVE_FIXTURE",
    "GOLDEN_OUTPUT",
    "EXAMPLE",
    "PLACEHOLDER",
    "GENERATED",
    "UNKNOWN",
}
ALLOWED_PROVENANCE = {
    "SYNTHETIC",
    "GENERATED_IN_REPOSITORY",
    "PUBLIC_OPEN_DATA",
    "PUBLIC_STANDARD_EXAMPLE",
    "THIRD_PARTY_LICENSED",
    "QUARANTINED",
}
ALLOWED_DATASET_AVAILABILITY = {"AVAILABLE", "SPECIFIED_NOT_AVAILABLE", "PLANNED"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class FixtureValidationError(Exception):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FixtureValidationError(f"invalid manifest JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise FixtureValidationError("manifest root must be an object")
    return data


def resolve_repo_path(root: Path, raw_path: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path:
        raise FixtureValidationError("fixture path must be a non-empty string")
    path = Path(raw_path)
    if path.is_absolute() or ".." in path.parts:
        raise FixtureValidationError(f"fixture path escapes repository: {raw_path}")
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise FixtureValidationError(f"fixture path escapes repository: {raw_path}") from exc
    return resolved


def validate_fixture(fixture: dict[str, Any], *, root: Path, known_ids: set[str]) -> None:
    missing = sorted(REQUIRED_FIELDS - fixture.keys())
    if missing:
        raise FixtureValidationError(f"{fixture.get('id', '<missing id>')} missing fields: {missing}")

    fixture_id = fixture["id"]
    if not isinstance(fixture_id, str) or not fixture_id:
        raise FixtureValidationError("fixture id must be a non-empty string")
    if fixture["category"] not in ALLOWED_CATEGORIES:
        raise FixtureValidationError(f"{fixture_id} invalid category: {fixture['category']}")
    if fixture["status"] not in ALLOWED_STATUSES:
        raise FixtureValidationError(f"{fixture_id} invalid status: {fixture['status']}")
    if fixture["provenance"] not in ALLOWED_PROVENANCE:
        raise FixtureValidationError(f"{fixture_id} invalid provenance: {fixture['provenance']}")
    if fixture["provenance"] == "UNKNOWN" and fixture["status"] != "QUARANTINED":
        raise FixtureValidationError(f"{fixture_id} uses UNKNOWN provenance without quarantine")

    for text_field in ["description", "format", "version", "source", "license"]:
        if not isinstance(fixture[text_field], str) or not fixture[text_field].strip():
            raise FixtureValidationError(f"{fixture_id} has empty {text_field}")

    for bool_field in [
        "redistribution_allowed",
        "synthetic",
        "contains_customer_data",
        "contains_personal_data",
        "contains_secrets",
        "deterministic",
    ]:
        if not isinstance(fixture[bool_field], bool):
            raise FixtureValidationError(f"{fixture_id} {bool_field} must be boolean")

    if fixture["contains_customer_data"] or fixture["contains_personal_data"] or fixture["contains_secrets"]:
        raise FixtureValidationError(f"{fixture_id} is not allowed as a versioned fixture due to sensitive-data flags")
    if not fixture["redistribution_allowed"]:
        raise FixtureValidationError(f"{fixture_id} is not redistributable")

    intended_tests = fixture["intended_tests"]
    if not isinstance(intended_tests, list) or not intended_tests or not all(isinstance(v, str) and v for v in intended_tests):
        raise FixtureValidationError(f"{fixture_id} intended_tests must be a non-empty string list")

    path = resolve_repo_path(root, fixture["path"])
    if not path.is_file():
        raise FixtureValidationError(f"{fixture_id} file does not exist: {fixture['path']}")
    if fixture["size_bytes"] != path.stat().st_size:
        raise FixtureValidationError(f"{fixture_id} size mismatch for {fixture['path']}")
    if not isinstance(fixture["sha256"], str) or not SHA256_RE.match(fixture["sha256"]):
        raise FixtureValidationError(f"{fixture_id} sha256 must be lowercase hex SHA-256")
    actual_hash = sha256_file(path)
    if fixture["sha256"] != actual_hash:
        raise FixtureValidationError(f"{fixture_id} checksum mismatch for {fixture['path']}")

    source_id = fixture.get("source_fixture_id")
    if fixture["category"] == "GOLDEN_OUTPUT" and not source_id:
        raise FixtureValidationError(f"{fixture_id} golden output must declare source_fixture_id")
    if source_id and source_id not in known_ids:
        raise FixtureValidationError(f"{fixture_id} references unknown source_fixture_id: {source_id}")


def validate_domain_schema_golden(manifest: dict[str, Any], *, root: Path) -> None:
    fixtures = {fixture["id"]: fixture for fixture in manifest["fixtures"]}
    golden = fixtures.get("GOLDEN-DOMAIN-001")
    if not golden:
        return
    source = fixtures.get(golden.get("source_fixture_id"))
    if not source:
        raise FixtureValidationError("GOLDEN-DOMAIN-001 source fixture is missing")
    source_text = resolve_repo_path(root, source["path"]).read_text(encoding="utf-8")
    golden_data = json.loads(resolve_repo_path(root, golden["path"]).read_text(encoding="utf-8"))
    expected = golden_data.get("expected", {})
    table_count = len(re.findall(r"^CREATE TABLE IF NOT EXISTS", source_text, flags=re.MULTILINE))
    index_count = len(re.findall(r"^CREATE INDEX IF NOT EXISTS", source_text, flags=re.MULTILINE))
    if expected.get("table_count") != table_count:
        raise FixtureValidationError("GOLDEN-DOMAIN-001 table_count mismatch")
    if expected.get("index_count") != index_count:
        raise FixtureValidationError("GOLDEN-DOMAIN-001 index_count mismatch")
    for table in expected.get("required_tables", []):
        create_table = f"CREATE TABLE IF NOT EXISTS {table}"
        if create_table not in source_text:
            raise FixtureValidationError(f"GOLDEN-DOMAIN-001 missing table in source: {table}")
    for invariant in expected.get("required_invariants", []):
        if invariant not in source_text:
            raise FixtureValidationError(f"GOLDEN-DOMAIN-001 missing invariant in source: {invariant}")


def validate_manifest_path(path: Path = MANIFEST_PATH, *, root: Path = ROOT) -> dict[str, Any]:
    manifest = load_manifest(path)
    if manifest.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise FixtureValidationError(f"unsupported schema_version: {manifest.get('schema_version')}")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise FixtureValidationError("manifest fixtures must be a non-empty list")

    ids: list[str] = []
    paths: list[str] = []
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            raise FixtureValidationError("each fixture must be an object")
        ids.append(fixture.get("id", ""))
        paths.append(fixture.get("path", ""))

    duplicate_ids = sorted({fixture_id for fixture_id in ids if ids.count(fixture_id) > 1})
    if duplicate_ids:
        raise FixtureValidationError(f"duplicate fixture ids: {duplicate_ids}")
    duplicate_paths = sorted({fixture_path for fixture_path in paths if paths.count(fixture_path) > 1})
    if duplicate_paths:
        raise FixtureValidationError(f"duplicate fixture paths: {duplicate_paths}")

    known_ids = set(ids)
    for fixture in fixtures:
        validate_fixture(fixture, root=root, known_ids=known_ids)

    availability = manifest.get("dataset_availability", {})
    if not isinstance(availability, dict):
        raise FixtureValidationError("dataset_availability must be an object")
    for dataset_class in ["TINY", "SMALL", "MEDIUM", "LARGE"]:
        item = availability.get(dataset_class)
        if not isinstance(item, dict):
            raise FixtureValidationError(f"dataset_availability missing {dataset_class}")
        if item.get("status") not in ALLOWED_DATASET_AVAILABILITY:
            raise FixtureValidationError(f"{dataset_class} has invalid availability status")
        for fixture_id in item.get("fixture_ids", []):
            if fixture_id not in known_ids:
                raise FixtureValidationError(f"{dataset_class} references unknown fixture id: {fixture_id}")

    validate_domain_schema_golden(manifest, root=root)
    return manifest


def print_checksums(manifest: dict[str, Any], *, root: Path) -> None:
    for fixture in manifest["fixtures"]:
        path = resolve_repo_path(root, fixture["path"])
        print(f"{fixture['id']} {fixture['path']} {path.stat().st_size} {sha256_file(path)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate fixture catalog manifest and physical artifact checksums.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--print-checksums", action="store_true")
    args = parser.parse_args()

    try:
        manifest = validate_manifest_path(args.manifest, root=ROOT)
    except FixtureValidationError as exc:
        print(f"FIXTURE CHECK: FAIL {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if args.print_checksums:
        print_checksums(manifest, root=ROOT)
    print(f"FIXTURE CHECK: OK ({len(manifest['fixtures'])} fixtures)")


if __name__ == "__main__":
    main()
