import asyncio
from contextlib import contextmanager
from dataclasses import FrozenInstanceError
from io import BytesIO
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException, UploadFile

import app.main as main
from app.context import (
    ProjectScopeNotFound,
    TenantContext,
    TenantContextConfigurationError,
    require_model_project_scope,
    require_project_scope,
    resolve_development_tenant_context,
)
from app.schemas import SelectionResolveIn

ORG_A = UUID("11111111-1111-1111-1111-111111111111")
ORG_B = UUID("22222222-2222-2222-2222-222222222222")


class Result:
    def __init__(self, rows=None, first_value=None, scalar_value=None):
        self.rows = rows or []
        self.first_value = first_value
        self.scalar_value = scalar_value

    def first(self):
        return self.first_value

    def all(self):
        return self.rows

    def scalar_one(self):
        return self.scalar_value

    def mappings(self):
        return self

    def one(self):
        return self.rows[0]


class ScopeConnection:
    def __init__(self, project_orgs=None, model_projects=None):
        self.project_orgs = {str(k): str(v) for k, v in (project_orgs or {}).items()}
        self.model_projects = {str(k): str(v) for k, v in (model_projects or {}).items()}

    def execute(self, statement, params=None):
        sql = str(statement).lower()
        params = params or {}
        if "from projects" in sql and "where id=:project_id" in sql:
            project_id = params["project_id"]
            org_id = params["organization_id"]
            first_value = (
                SimpleNamespace(id=project_id)
                if self.project_orgs.get(project_id) == org_id
                else None
            )
            return Result(first_value=first_value)
        if "from models" in sql and "where m.id=:model_id" in sql:
            model_id = params["model_id"]
            org_id = params["organization_id"]
            project_id = self.model_projects.get(model_id)
            if project_id and self.project_orgs.get(project_id) == org_id:
                return Result(rows=[{"project_id": project_id}], first_value={"project_id": project_id})
            return Result()
        return Result()


class WorkAreaConnection(ScopeConnection):
    def execute(self, statement, params=None):
        result = super().execute(statement, params)
        if result.first_value is not None or result.rows:
            return result
        return Result(rows=[])


class SelectionConnection:
    def __init__(self, allowed_org):
        self.allowed_org = str(allowed_org)
        self.calls = 0

    def execute(self, _statement, params=None):
        self.calls += 1
        if not params or params.get("org") != self.allowed_org:
            return Result()
        if self.calls == 1:
            return Result(rows=[SimpleNamespace(id=params["ids"][0])])
        if self.calls == 2:
            return Result(rows=[SimpleNamespace(boq_item_id=str(uuid4()))])
        return Result(rows=[SimpleNamespace(activity_id=str(uuid4()))])


@contextmanager
def fake_connection(conn):
    yield conn


def test_development_tenant_context_normalizes_uuid():
    context = resolve_development_tenant_context(str(ORG_A))

    assert context.organization_id == ORG_A
    assert context.project_id is None


@pytest.mark.parametrize("raw_value", ["", "not-a-uuid"])
def test_development_tenant_context_rejects_invalid_or_missing_uuid(raw_value):
    with pytest.raises(TenantContextConfigurationError):
        resolve_development_tenant_context(raw_value)


def test_tenant_context_is_immutable_value_object():
    context = TenantContext(organization_id=ORG_A)

    with pytest.raises(FrozenInstanceError):
        context.organization_id = ORG_B


def test_require_project_scope_accepts_same_organization_project():
    project_id = uuid4()
    conn = ScopeConnection(project_orgs={project_id: ORG_A})

    scoped = require_project_scope(conn, TenantContext(ORG_A), project_id)

    assert scoped.organization_id == ORG_A
    assert scoped.project_id == project_id


def test_require_project_scope_rejects_other_organization_project():
    project_id = uuid4()
    conn = ScopeConnection(project_orgs={project_id: ORG_B})

    with pytest.raises(ProjectScopeNotFound):
        require_project_scope(conn, TenantContext(ORG_A), project_id)


def test_require_project_scope_rejects_missing_project():
    with pytest.raises(ProjectScopeNotFound):
        require_project_scope(ScopeConnection(), TenantContext(ORG_A), uuid4())


def test_require_model_project_scope_follows_model_to_project_to_organization():
    project_id = uuid4()
    model_id = uuid4()
    conn = ScopeConnection(project_orgs={project_id: ORG_A}, model_projects={model_id: project_id})

    scoped = require_model_project_scope(conn, TenantContext(ORG_A), model_id)

    assert scoped.project_id == project_id


def test_work_area_rejects_cross_tenant_project(monkeypatch):
    project_id = uuid4()
    conn = ScopeConnection(project_orgs={project_id: ORG_B})
    monkeypatch.setattr(main, "connection", lambda: fake_connection(conn))

    with pytest.raises(HTTPException) as exc:
        main.work_area(project_id, tenant_context=TenantContext(ORG_A))

    assert exc.value.status_code == 404


def test_work_area_allows_same_tenant_project(monkeypatch):
    project_id = uuid4()
    conn = WorkAreaConnection(project_orgs={project_id: ORG_A})
    monkeypatch.setattr(main, "connection", lambda: fake_connection(conn))

    result = main.work_area(project_id, tenant_context=TenantContext(ORG_A))

    assert result == {"boq": [], "activities": [], "revisions": []}


def test_selection_resolver_rejects_ids_from_other_tenant(monkeypatch):
    requested_id = uuid4()
    monkeypatch.setattr(main, "connection", lambda: fake_connection(SelectionConnection(allowed_org=ORG_B)))

    result = main.resolve_selection(
        SelectionResolveIn(source_type="element", ids=[requested_id]),
        tenant_context=TenantContext(ORG_A),
    )

    assert result == {"element_ids": [], "boq_item_ids": [], "activity_ids": []}


def test_selection_resolver_allows_same_tenant_ids(monkeypatch):
    requested_id = uuid4()
    monkeypatch.setattr(main, "connection", lambda: fake_connection(SelectionConnection(allowed_org=ORG_A)))

    result = main.resolve_selection(
        SelectionResolveIn(source_type="element", ids=[requested_id]),
        tenant_context=TenantContext(ORG_A),
    )

    assert result["element_ids"] == [str(requested_id)]
    assert result["boq_item_ids"]
    assert result["activity_ids"]


def test_upload_revision_rejects_cross_tenant_model(monkeypatch, tmp_path):
    project_id = uuid4()
    model_id = uuid4()
    conn = ScopeConnection(project_orgs={project_id: ORG_B}, model_projects={model_id: project_id})
    monkeypatch.setattr(main, "connection", lambda: fake_connection(conn))
    monkeypatch.setattr(main.settings, "upload_dir", str(tmp_path))
    upload = UploadFile(filename="demo.ifc", file=BytesIO(b"ISO-10303-21;"))

    with pytest.raises(HTTPException) as exc:
        asyncio.run(main.upload_revision(model_id, upload, tenant_context=TenantContext(ORG_A)))

    assert exc.value.status_code == 404
    assert list(tmp_path.iterdir()) == []
