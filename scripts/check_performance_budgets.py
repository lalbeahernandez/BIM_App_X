from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BUDGETS_PATH = ROOT / 'config' / 'performance-budgets.json'
REQUIRED_CLASSES = {'TINY', 'SMALL', 'MEDIUM', 'LARGE'}
REQUIRED_HARDWARE = {'DEV', 'CI', 'PRODUCTION_REFERENCE'}
REQUIRED_TOP_LEVEL = {
    'dataset_classes',
    'hardware_profiles',
    'api_latency_budgets',
    'api_throughput_budgets',
    'response_size_budgets',
    'db_query_budgets',
    'ifc_upload_budgets',
    'ifc_ingest_budgets',
    'worker_memory_budgets',
    'viewer_budgets',
    'reliability_slo',
    'ci_tiers',
    'regression_policy',
}


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def require_positive(value: Any, label: str, failures: list[str]) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        fail(f'{label} must be a positive number', failures)


def main() -> int:
    failures: list[str] = []
    try:
        data = json.loads(BUDGETS_PATH.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'PERFORMANCE BUDGET CHECK: FAIL unable to read JSON: {exc}')
        return 1

    missing = sorted(REQUIRED_TOP_LEVEL - set(data))
    if missing:
        fail(f'missing top-level keys: {", ".join(missing)}', failures)

    dataset_classes = data.get('dataset_classes', {})
    missing_classes = sorted(REQUIRED_CLASSES - set(dataset_classes))
    if missing_classes:
        fail(f'missing dataset classes: {", ".join(missing_classes)}', failures)
    for class_name in REQUIRED_CLASSES & set(dataset_classes):
        spec = dataset_classes[class_name]
        for key in [
            'ifc_products_max',
            'storeys_max',
            'psets_max',
            'quantities_max',
            'boq_items_max',
            'activities_max',
            'triangles_max',
            'derived_artifacts_mb_max',
        ]:
            require_positive(spec.get(key), f'{class_name}.{key}', failures)
        if spec.get('availability') not in {'AVAILABLE', 'SPECIFIED_NOT_AVAILABLE'}:
            fail(f'{class_name}.availability has invalid value', failures)

    hardware = data.get('hardware_profiles', {})
    missing_hardware = sorted(REQUIRED_HARDWARE - set(hardware))
    if missing_hardware:
        fail(f'missing hardware profiles: {", ".join(missing_hardware)}', failures)

    for index, budget in enumerate(data.get('api_latency_budgets', [])):
        label = f'api_latency_budgets[{index}]'
        if budget.get('dataset') not in REQUIRED_CLASSES:
            fail(f'{label}.dataset must be one of {sorted(REQUIRED_CLASSES)}', failures)
        for key in ['p50_ms', 'p95_ms', 'p99_ms']:
            require_positive(budget.get(key), f'{label}.{key}', failures)
        if budget.get('p50_ms', 0) > budget.get('p95_ms', 0):
            fail(f'{label} p50_ms must be <= p95_ms', failures)
        if budget.get('p95_ms', 0) > budget.get('p99_ms', 0):
            fail(f'{label} p95_ms must be <= p99_ms', failures)

    for section in ['ifc_upload_budgets', 'ifc_ingest_budgets', 'worker_memory_budgets', 'viewer_budgets']:
        section_data = data.get(section, {})
        missing_section_classes = sorted(REQUIRED_CLASSES - set(section_data))
        if missing_section_classes:
            fail(f'{section} missing classes: {", ".join(missing_section_classes)}', failures)

    ci_tiers = data.get('ci_tiers', {})
    for tier in ['PR_GATE', 'NIGHTLY', 'RELEASE_CERTIFICATION']:
        entries = ci_tiers.get(tier)
        if not isinstance(entries, list) or not entries:
            fail(f'ci_tiers.{tier} must be a non-empty list', failures)

    if failures:
        print('PERFORMANCE BUDGET CHECK: FAIL')
        for failure in failures:
            print(f'- {failure}')
        return 1

    print('PERFORMANCE BUDGET CHECK: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
