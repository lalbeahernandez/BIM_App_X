import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("check_fixtures", ROOT / "scripts" / "check_fixtures.py")
check_fixtures = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(check_fixtures)


def write_fixture_manifest(tmp_path, fixtures):
    manifest = {
        "schema_version": 1,
        "dataset_availability": {
            "TINY": {"status": "AVAILABLE", "fixture_ids": []},
            "SMALL": {"status": "SPECIFIED_NOT_AVAILABLE", "fixture_ids": []},
            "MEDIUM": {"status": "SPECIFIED_NOT_AVAILABLE", "fixture_ids": []},
            "LARGE": {"status": "SPECIFIED_NOT_AVAILABLE", "fixture_ids": []},
        },
        "fixtures": fixtures,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def fixture_entry(tmp_path, fixture_id="API-TINY-001", path="data.json", *, sha256=None):
    file_path = tmp_path / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text('{"ok": true}\n', encoding="utf-8")
    data = file_path.read_bytes()
    return {
        "id": fixture_id,
        "category": "API",
        "path": path,
        "description": "Synthetic API fixture for validator tests.",
        "format": "JSON",
        "version": "1.0.0",
        "source": "test",
        "provenance": "SYNTHETIC",
        "license": "Repository-owned synthetic test data",
        "redistribution_allowed": True,
        "sha256": sha256 or hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        "synthetic": True,
        "contains_customer_data": False,
        "contains_personal_data": False,
        "contains_secrets": False,
        "deterministic": True,
        "intended_tests": ["test_fixture_validator.py"],
        "status": "ACTIVE_FIXTURE",
    }


def test_fixture_validator_accepts_valid_manifest(tmp_path):
    manifest_path = write_fixture_manifest(tmp_path, [fixture_entry(tmp_path)])

    manifest = check_fixtures.validate_manifest_path(manifest_path, root=tmp_path)

    assert len(manifest["fixtures"]) == 1


def test_fixture_validator_rejects_duplicate_fixture_id(tmp_path):
    first = fixture_entry(tmp_path, fixture_id="API-TINY-001", path="one.json")
    second = fixture_entry(tmp_path, fixture_id="API-TINY-001", path="two.json")
    manifest_path = write_fixture_manifest(tmp_path, [first, second])

    with pytest.raises(check_fixtures.FixtureValidationError, match="duplicate fixture ids"):
        check_fixtures.validate_manifest_path(manifest_path, root=tmp_path)


def test_fixture_validator_rejects_missing_file(tmp_path):
    entry = fixture_entry(tmp_path)
    (tmp_path / entry["path"]).unlink()
    manifest_path = write_fixture_manifest(tmp_path, [entry])

    with pytest.raises(check_fixtures.FixtureValidationError, match="file does not exist"):
        check_fixtures.validate_manifest_path(manifest_path, root=tmp_path)


def test_fixture_validator_rejects_checksum_mismatch(tmp_path):
    entry = fixture_entry(tmp_path, sha256="0" * 64)
    manifest_path = write_fixture_manifest(tmp_path, [entry])

    with pytest.raises(check_fixtures.FixtureValidationError, match="checksum mismatch"):
        check_fixtures.validate_manifest_path(manifest_path, root=tmp_path)


def test_fixture_validator_rejects_invalid_manifest_json(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("{", encoding="utf-8")

    with pytest.raises(check_fixtures.FixtureValidationError, match="invalid manifest JSON"):
        check_fixtures.validate_manifest_path(manifest_path, root=tmp_path)


def test_fixture_validator_rejects_invalid_golden_source_reference(tmp_path):
    entry = fixture_entry(tmp_path, fixture_id="GOLDEN-API-001")
    entry["category"] = "GOLDEN_OUTPUT"
    entry["status"] = "GOLDEN_OUTPUT"
    entry["source_fixture_id"] = "API-MISSING-001"
    manifest_path = write_fixture_manifest(tmp_path, [entry])

    with pytest.raises(check_fixtures.FixtureValidationError, match="unknown source_fixture_id"):
        check_fixtures.validate_manifest_path(manifest_path, root=tmp_path)
