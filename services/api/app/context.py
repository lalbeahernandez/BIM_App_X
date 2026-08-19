from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text

from app.config import settings


@dataclass(frozen=True)
class TenantContext:
    organization_id: UUID
    project_id: UUID | None = None

    def with_project(self, project_id: UUID) -> TenantContext:
        return TenantContext(organization_id=self.organization_id, project_id=project_id)


class TenantContextConfigurationError(ValueError):
    pass


class ProjectScopeNotFound(LookupError):
    pass


class ModelScopeNotFound(LookupError):
    pass


def resolve_development_tenant_context(
    default_organization_id: str = settings.default_org_id,
) -> TenantContext:
    try:
        organization_id = UUID(str(default_organization_id))
    except (TypeError, ValueError) as exc:
        raise TenantContextConfigurationError(
            "development default organization id is not a valid UUID",
        ) from exc
    return TenantContext(organization_id=organization_id)


def get_tenant_context() -> TenantContext:
    return resolve_development_tenant_context()


def require_project_scope(conn, tenant_context: TenantContext, project_id: UUID) -> TenantContext:
    row = conn.execute(
        text("""
          SELECT id
          FROM projects
          WHERE id=:project_id AND organization_id=:organization_id
        """),
        {"project_id": str(project_id), "organization_id": str(tenant_context.organization_id)},
    ).first()
    if not row:
        raise ProjectScopeNotFound("Project not found")
    return tenant_context.with_project(project_id)


def require_model_project_scope(conn, tenant_context: TenantContext, model_id: UUID) -> TenantContext:
    row = conn.execute(
        text("""
          SELECT m.project_id
          FROM models m
          JOIN projects p ON p.id=m.project_id
          WHERE m.id=:model_id AND p.organization_id=:organization_id
        """),
        {"model_id": str(model_id), "organization_id": str(tenant_context.organization_id)},
    ).mappings().first()
    if not row:
        raise ModelScopeNotFound("Model not found")
    return tenant_context.with_project(UUID(str(row["project_id"])))
