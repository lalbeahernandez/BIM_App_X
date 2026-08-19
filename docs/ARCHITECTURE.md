# Architecture

## Style

Comenzar como **modular monolith + async workers**. Separar servicios sólo cuando exista presión demostrable de scaling, seguridad, ownership o ciclo de despliegue.

```text
Browser / PWA
  -> Web (Next.js)
  -> API (FastAPI, modular domain)
       -> PostgreSQL/PostGIS (system of record)
       -> Redis (jobs/cache/locks)
       -> Object Storage (IFC, geometry, snapshots, reports)
       -> Outbox -> integrations/webhooks
  -> BIM Workers
       -> IfcOpenShell / validators / geometry / diff / clash
       -> artifacts + normalized data
```

## Bounded contexts

- Identity & Tenancy
- Project/Model Management
- BIM Index & Revision
- Classification & Rules
- Quantity/BOQ/Cost
- Scheduling/4D
- Progress/Productivity/EVM
- Issues/BCF/QAQC
- GIS
- Integrations
- Reporting/Analytics

## Architectural rules

- HTTP APIs are thin orchestration; domain invariants live in services/domain.
- Heavy BIM is asynchronous and idempotent.
- Files/artifacts are immutable and content-addressable in production.
- Data writes emit audit + outbox transactionally.
- Viewer is a replaceable adapter.
- Internal IDs are UUIDs; IFC `GlobalId` is a domain identifier but not the database PK.
- All temporal values stored as UTC instants when they represent events; project schedule uses project timezone/calendar semantics.
- Monetary values store amount + currency; quantities store value + unit + source.

## Tenant context

Foundation starts with a request-scoped `TenantContext` in `services/api/app/context.py`.
It is a small immutable value object that carries the server-resolved `organization_id`
and, when an endpoint is project-scoped, the resolved `project_id`.

Current local development resolution uses `settings.default_org_id` as a transitional
resolver so the harness remains runnable before real authentication exists. This is not
production auth. Future identity adapters should replace only the resolver boundary;
routers and application code should continue consuming `TenantContext`.

Project-scoped requests must call the project scope helper before operating on resources.
Nested resources resolve through trusted server-side paths, for example:

```text
model_revision -> model -> project -> organization
bim_element -> revision -> model -> project -> organization
boq_item/activity -> project -> organization
```

Client-supplied resource IDs are selectors, not authorization proof. Cross-organization
project or nested-resource access returns not found semantics to avoid unnecessary
resource-existence leakage. Authorization policy remains owned by later tasks.

## Scale strategy

Partition large `bim_elements`, `progress_records`, `audit_events` by project/revision/time only after evidence. Introduce read models/materialized views for dashboards. Add search engine only when PostgreSQL FTS/trigram no longer meets SLA.
