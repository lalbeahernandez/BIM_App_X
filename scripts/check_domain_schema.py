from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def normalized(path: str) -> str:
    return ' '.join((ROOT / path).read_text(encoding='utf-8').lower().split())


def require(haystack: str, needle: str, label: str, failures: list[str]) -> None:
    if needle.lower() not in haystack:
        failures.append(f'{label}: missing `{needle}`')


def require_all(haystack: str, needles: list[str], label: str, failures: list[str]) -> None:
    for needle in needles:
        require(haystack, needle, label, failures)


def main() -> int:
    schema = normalized('db/init/010_schema.sql')
    api = normalized('services/api/app/main.py')
    openapi = normalized('specs/openapi.yaml')
    event_schema = normalized('specs/events/model-revision-ingest-requested.schema.json')
    failures: list[str] = []

    require_all(
        schema,
        [
            'create table if not exists organizations',
            'create table if not exists projects',
            'create table if not exists models',
            'create table if not exists model_revisions',
            'create table if not exists bim_elements',
            'create table if not exists element_lineage',
            'create table if not exists classification_nodes',
            'create table if not exists element_classifications',
            'create table if not exists quantities',
            'create table if not exists boq_items',
            'create table if not exists element_boq_links',
            'create table if not exists wbs_nodes',
            'create table if not exists activities',
            'create table if not exists activity_relations',
            'create table if not exists element_activity_links',
            'create table if not exists resources',
            'create table if not exists crews',
            'create table if not exists productivity_rates',
            'create table if not exists progress_records',
            'create table if not exists issues',
            'create table if not exists issue_elements',
            'create table if not exists inspections',
            'create table if not exists audit_events',
            'create table if not exists outbox_events',
        ],
        'canonical table set',
        failures,
    )

    require(schema, 'id uuid primary key, revision_id uuid not null references model_revisions(id)', 'BimElement internal PK', failures)
    require(schema, 'unique (revision_id, global_id)', 'BimElement revision-scoped identity', failures)
    require_all(
        schema,
        ['from_element_id uuid not null', 'to_element_id uuid not null', 'match_method text not null', 'confidence numeric(5,4)', 'approved_by text'],
        'ElementLineage continuity/provenance',
        failures,
    )
    require_all(
        schema,
        ['element_boq_links', 'source text not null default', 'rule_id text', 'weight numeric(12,8)', 'primary key (element_id, boq_item_id)'],
        'Element-BOQ many-to-many provenance',
        failures,
    )
    require_all(
        schema,
        ['element_activity_links', 'role text not null default', 'source text not null default', 'primary key (element_id, activity_id, role)'],
        'Element-Activity many-to-many provenance',
        failures,
    )
    require_all(
        schema,
        ['progress_records', 'data_date date not null', 'quantity_complete numeric(24,8)', 'percent_complete numeric(7,4)', 'evidence_uri text'],
        'ProgressRecord history record',
        failures,
    )
    require_all(
        schema,
        ['audit_events', 'before_data jsonb', 'after_data jsonb', 'occurred_at timestamptz not null default now()'],
        'AuditEvent provenance',
        failures,
    )
    require_all(
        schema,
        ['outbox_events', 'event_type text not null', 'payload jsonb not null', 'published_at timestamptz', 'attempts integer not null default 0'],
        'OutboxEvent publish state',
        failures,
    )
    require_all(
        schema,
        ["status text not null default 'queued' check (status in ('queued','processing','ready','failed'))", 'unique (model_id, revision_no)'],
        'ModelRevision state/revision constraints',
        failures,
    )
    require_all(schema, ['numeric(24,8)', 'currency char(3)', 'timestamptz'], 'decimal money and time primitives', failures)

    require(openapi, '/v1/projects/{project_id}/work-area:', 'OpenAPI work-area route', failures)
    require(openapi, '/v1/selection/resolve:', 'OpenAPI selection route', failures)
    require(event_schema, '"model.revision.ingest_requested.v1"', 'ModelRevisionIngestRequested event schema', failures)

    require_all(
        api,
        ['def resolve_selection', 'p.organization_id=:org', 'and b.project_id=p.id', 'and a.project_id=p.id'],
        'selection resolver server-side tenant/project scoping',
        failures,
    )

    if failures:
        print('DOMAIN SCHEMA CHECK: FAIL')
        for failure in failures:
            print(f'- {failure}')
        return 1
    print('DOMAIN SCHEMA CHECK: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
