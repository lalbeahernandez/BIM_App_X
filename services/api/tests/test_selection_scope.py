from contextlib import contextmanager
from uuid import UUID, uuid4

import pytest

import app.main as main
from app.context import TenantContext
from app.schemas import SelectionResolveIn

ORG_A = UUID("11111111-1111-1111-1111-111111111111")


class EmptyResult:
    def all(self):
        return []


class EmptyConnection:
    def execute(self, *_args, **_kwargs):
        return EmptyResult()


@contextmanager
def empty_connection():
    yield EmptyConnection()


@pytest.mark.parametrize(
    ('source_type', 'field_name'),
    [
        ('element', 'element_ids'),
        ('boq', 'boq_item_ids'),
        ('activity', 'activity_ids'),
    ],
)
def test_selection_resolver_does_not_echo_unscoped_ids(monkeypatch, source_type, field_name):
    monkeypatch.setattr(main, 'connection', empty_connection)
    requested_id = uuid4()

    resolved = main.resolve_selection(
        SelectionResolveIn(source_type=source_type, ids=[requested_id]),
        tenant_context=TenantContext(organization_id=ORG_A),
    )

    assert resolved[field_name] == []
