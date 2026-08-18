# Architecture Inventory - AUD-002

Date: 2026-08-18

Scope: static inventory of the current repository against the accepted modular monolith,
async BIM worker, and replaceable adapter architecture. This document describes the
architecture that exists now, not a claim that all future bounded contexts are implemented.

## Executive Summary

The repository is a runnable starter harness. The main production-facing path is:

```text
Browser/PWA
  -> apps/web (Next.js demo)
  -> services/api (FastAPI modular-monolith shell)
  -> PostgreSQL/PostGIS schema and Redis queue
  -> services/bim-worker for IFC ingest
```

No direct vendor imports were found inside `services/api/app/domain`; that directory is
currently documentation-only. Vendor/runtime dependencies are present in API infrastructure
code (`FastAPI`, `SQLAlchemy`, `Redis`) and in the BIM worker (`IfcOpenShell`, `psycopg`,
`Redis`). This is acceptable for the harness, but the API still lacks explicit
application/domain/ports boundaries. The largest architecture risks are concentrated in
`services/api/app/main.py`, where routing, validation, SQL, audit/outbox calls, upload file
handling, and Redis enqueueing are currently combined.

## Component Inventory

| Component | Path | Current responsibility | Future responsibility | Bounded context | Incoming dependencies | Outgoing dependencies | Status | Notes | Recommended owner |
|---|---|---|---|---|---|---|---|---|---|
| Web app | `apps/web` | Next.js Work Area demo, API fetch, demo fallback data, placeholder cross-selection | PWA shell that consumes API contracts and viewer adapter, never domain authority | Work Area / Reporting shell | Browser users | API HTTP, React/Next | FUNCTIONAL | Demo fallback remains temporary. | Frontend / Work Area |
| WorkArea component | `apps/web/components/WorkArea.tsx` | BOQ/Gantt panels and demo selection mapping | UI composition only; selection should be resolved by API | Viewer / BOQ / Scheduling presentation | Web app page | `apps/web/lib/api`, `ViewerPlaceholder` | FUNCTIONAL | Contains demo cross-selection rules that should move behind API selection resolution. | Frontend / Work Area |
| Viewer placeholder | `apps/web/components/ViewerPlaceholder.tsx` | Demo geometry and TODO(PROD) note | Concrete implementation behind `ViewerAdapter` | Viewer presentation | WorkArea | CSS only | STUB | Production viewer engine is intentionally not selected. | Viewer |
| Web API client | `apps/web/lib/api.ts` | Fetch work-area API with static demo fallback | Typed contract client generated or validated from OpenAPI | Frontend integration | WorkArea | API HTTP | FUNCTIONAL | Static fallback data should become explicit dev/demo mode later. | Frontend platform |
| FastAPI service | `services/api` | HTTP routes, DB writes/reads, audit/outbox, Redis enqueue | Modular monolith with thin routers and application/domain services | Multiple MVP contexts | Web, smoke tests | PostgreSQL, Redis, local upload volume | FUNCTIONAL | Harness implementation is runnable; boundary debt is listed in P1 findings. | API platform |
| API router/application shell | `services/api/app/main.py` | Health, projects, models, revision upload, work-area query, selection resolver | Thin orchestration delegating to services and ports | Project/Model, BIM Index, BOQ, Scheduling | FastAPI runtime, tests | `audit`, `db`, schemas, Redis, SQL | FUNCTIONAL | P1 boundary debt; routers currently contain SQL/orchestration. | API platform |
| API schemas | `services/api/app/schemas.py` | Pydantic request/response models | Versioned API contract models aligned with OpenAPI | API contracts | FastAPI routes | Pydantic | FUNCTIONAL | API schemas exist, but contract drift checks are future work. | API platform |
| DB connection | `services/api/app/db.py` | SQLAlchemy engine and transaction context | Database adapter/Unit of Work boundary | Persistence | API code | SQLAlchemy/PostgreSQL driver | FUNCTIONAL | Infrastructure boundary is minimal. | Data platform |
| Audit/outbox helpers | `services/api/app/audit.py` | Insert audit and outbox rows transactionally via caller connection | Application service or infrastructure adapter with typed events | Foundation / Integrations | API routes | SQLAlchemy text, DB schema | FUNCTIONAL | Event typing and contract validation are future work. | Foundation |
| Domain placeholder | `services/api/app/domain` | README only | Domain model/services with no vendor imports | All domain contexts | Future application layer | None now | STUB | No executable domain code yet. | Domain architecture |
| API adapters placeholder | `services/api/app/adapters` | README only | Ports/adapters for storage, search, auth, flags, integrations, events | Foundation / Integrations | Future application layer | Vendor SDKs behind adapters | STUB | Placeholder boundary only. | API platform |
| API jobs placeholder | `services/api/app/jobs` | README only | Queue port and job producer abstractions | Foundation / BIM ingest | Future application layer | Redis or queue adapter | STUB | Placeholder boundary only. | Foundation / Workers |
| BIM worker | `services/bim-worker` | Consume Redis queue, parse IFC, persist elements, update revision status | Idempotent heavy BIM processing pipeline behind queue contract | BIM Index & Revision | Redis queue | IfcOpenShell, psycopg, PostgreSQL | FUNCTIONAL | State machine/idempotency hardening is future work. | BIM platform |
| PostgreSQL/PostGIS schema | `db/init` | System of record schema for tenancy, model revisions, BIM elements, BOQ, schedule, progress, issues, audit, outbox | Versioned migrations and normalized domain record | Data platform / all contexts | API, worker | PostgreSQL/PostGIS | FUNCTIONAL | Migration framework is future work. | Data platform |
| Seed data | `db/seed.sql`, `db/init/020_seed.sql`, `fixtures` | Demo projects, BOQ, schedule, IFC/BCF fixtures | Golden datasets and deterministic fixtures | Test data / all contexts | Harness tests, demos | DB init, files | FUNCTIONAL | Demo and golden data are present. | QA / Data |
| Redis service | `docker-compose.yml` | Queue for BIM ingest | Queue/cache/locks only, not business record | Foundation / Jobs | API, worker | Redis image | FUNCTIONAL | Docker daemon is locally unavailable in the current Windows environment. | Platform |
| Object storage / MinIO | `docker-compose.yml`, `packages/adapters/object-storage` | MinIO service declared; upload currently uses shared volume | Immutable artifact storage via adapter | Foundation / Artifacts | API/worker future | S3-compatible adapter | STUB | MinIO service exists; production storage adapter is not wired yet. | Platform / Storage |
| Viewer adapter contract | `packages/viewer-adapter` | TypeScript interface using `revisionId + globalId` element refs | Boundary for production viewer engines | Viewer | Web future | No vendor SDK | STUB | Vendor-neutral contract only. | Viewer |
| Adapter package placeholders | `packages/adapters/*` | README contracts for search, openbim, scheduling, integrations, storage | Vendor isolation packages | Integrations / platform | Future app/domain ports | Vendor SDKs only here | STUB | Placeholder contracts only. | Integration platform |
| Specs | `specs/openapi.yaml`, `specs/events`, `specs/features` | Feature specs, OpenAPI and event schemas | Versioned contracts and acceptance source | Contracts | API/docs/tests | YAML/JSON schemas | FUNCTIONAL | Contract verification is future work. | API platform / Product |
| Infra | `infra` | Terraform/k8s/observability placeholders | Deploy/observability ownership after hardening | Platform | Operators | Terraform, Kubernetes, OTel | STUB | Deployment/observability assets are placeholders. | Platform |
| API health test | `services/api/tests/test_health.py` | Executable pytest coverage for `/health` | Unit/integration API smoke coverage | QA / API | pytest | FastAPI TestClient | FUNCTIONAL | Executes locally and passed during AUD-002. | QA |
| E2E test harness | `tests/e2e/README.md` | Playwright scenario documented only | Executable browser workflow coverage | QA / E2E | Future CI | Playwright future | STUB | README placeholder; no executable suite yet. | QA |
| Contract test harness | `tests/contracts/README.md` | OpenAPI diff strategy documented only | Executable OpenAPI/event contract checks | QA / Contracts | Future CI | OpenAPI/event schemas future | STUB | README placeholder; no executable suite yet. | QA |
| Security test harness | `tests/security/README.md` | Security testing plan documented only | Authorization matrix, DAST and scan automation | QA / Security | Future CI | Security tools future | STUB | README placeholder; no executable suite yet. | QA / Security |
| Visual regression harness | `tests/visual/README.md` | Visual strategy documented only | Executable visual regression checks | QA / Visual | Future CI | Visual tooling future | STUB | README placeholder; no executable suite yet. | QA / Frontend |
| Performance harness | `tests/performance/k6-smoke.js` | Executable k6 health smoke script | API performance smoke and later budgets | QA / Performance | k6 runner | API HTTP | FUNCTIONAL | Useful executable script exists; runtime still requires API service and k6. | QA / Performance |
| Docker Compose | `docker-compose.yml` | Local stack for db, redis, minio, api, worker, web | Dev/test orchestration | Platform | Developers/CI | Docker images/builds | FUNCTIONAL | Docker daemon is locally unavailable in the current Windows environment. | Platform |
| Codex task pack | `codex/*` | Roadmap, dependency graph, task prompts/status | Delivery control and PR sequencing | Engineering process | Humans/agents | Python validator | FUNCTIONAL | Validator is executable and passed. | Engineering |

## Dependency Map

Current runtime dependencies:

```text
Browser
  -> apps/web
       -> services/api over HTTP
       -> demo fallback data when API is unavailable

services/api
  -> PostgreSQL/PostGIS through SQLAlchemy
  -> Redis through redis-py for `bim:ingest`
  -> shared upload volume for IFC files
  -> audit_events and outbox_events in the same DB transaction

services/bim-worker
  -> Redis `bim:ingest` queue
  -> shared upload volume
  -> IfcOpenShell for heavy IFC parsing
  -> PostgreSQL through psycopg

PostgreSQL/PostGIS
  -> system of record for normalized domain data, audit, and outbox

MinIO/Object Storage
  -> declared in Compose and adapter docs
  -> not wired into first upload path yet

packages/viewer-adapter
  -> contract only; no runtime dependency from domain/core

packages/adapters/*
  -> placeholders for future vendor integrations
```

Target dependency direction to protect:

```text
Web -> API -> Application/Domain -> Ports -> Adapters -> DB/Redis/Storage/Vendors
API -> Queue Port -> BIM Worker -> IfcOpenShell/Geometry/Validation -> DB + Artifacts
```

Observed deviations from the target are documented below as P1/P2 debt. No P0 violation
was found.

## Bounded Context Map

| Bounded context | Current implementation | Status | Notes |
|---|---|---|---|
| Identity & Tenancy | `organizations`, `projects`, `DEFAULT_ORG_ID`, server-side project filters | FUNCTIONAL | Minimal harness implementation; auth/RBAC not implemented. |
| Project / Model Management | Project/model/revision endpoints and schema tables | FUNCTIONAL | Harness implementation exists. |
| BIM Index & Revision | `model_revisions`, `bim_elements`, worker ingest, `element_lineage` table | FUNCTIONAL | Baseline ingest exists; lineage workflow is not implemented yet. |
| Classification & Rules | `classification_nodes`, `element_classifications`, adapter docs | STUB | Schema is present; rules workflow is not implemented yet. |
| Quantity / BOQ / Cost | `boq_items`, `quantities`, `element_boq_links`, demo UI/API query | FUNCTIONAL | Harness/demo implementation exists; full 5D rules are future work. |
| Scheduling / 4D | WBS/activity/activity relation tables, `element_activity_links`, demo Gantt | FUNCTIONAL | Harness/demo implementation exists; CPM and full 4D are future work. |
| Progress / Productivity / EVM | `progress_records`, resource/crew/productivity tables | STUB | Schema is present; workflows are not implemented yet. |
| Issues / BCF / QA-QC | issues, issue_elements, inspections, fixtures/docs | STUB | Schema/fixtures are present; workflows are not implemented yet. |
| GIS | PostGIS extension and geometry column | STUB | Spatial foundation exists; GIS workflows are not implemented yet. |
| Integrations | outbox table and adapter placeholders | STUB | Outbox foundation exists; external integrations are not implemented yet. |
| Reporting / Analytics | Work Area read endpoint and frontend panels | FUNCTIONAL | Harness reporting surface exists; analytics are future work. |

## Ownership Recommendations

| Owner | Owns |
|---|---|
| API platform | FastAPI app shell, API contracts, error envelope, routing, request orchestration |
| Domain architecture | `services/api/app/domain`, domain services, invariants, bounded-context boundaries |
| Data platform | DB schema/migrations, query conventions, SQL review, projections |
| Foundation | tenancy, RBAC, audit, outbox, job queue abstraction, observability |
| BIM platform | model revision ingest, worker idempotency, IFC parsing/indexing, lineage |
| Viewer | `ViewerAdapter`, geometry artifact contracts, web viewer integration |
| Frontend / Work Area | Next.js shell, Work Area composition, API clients, UX state |
| Integration platform | storage/search/scheduling/ERP/CDE adapters and outbox publishers |
| QA / Release | test strategy, smoke/e2e/contract/perf/security harnesses |
| Platform / DevEx | Docker Compose, infra placeholders, local bootstrap, CI gates |

## Static Architecture Checks

Commands executed for this inventory:

```bash
rg -n "ifcopenshell|redis|boto3?|minio|s3|autodesk|primavera|openai|anthropic|psycopg|sqlalchemy|viewer" services/api/app/domain services/api/app -g "*.py" -g "*.md"
rg -n "^import |^from " services packages tests scripts -g "*.py" -g "!**/__pycache__/**" -g "!**/.mypy_cache/**" -g "!**/.pytest_cache/**" -g "!**/.ruff_cache/**"
rg -n "import .* from |^import " apps packages tests -g "*.ts" -g "*.tsx" -g "*.mjs" -g "!**/node_modules/**" -g "!**/.next/**"
```

Results:

- `services/api/app/domain` has no executable code and no direct vendor imports.
- `services/api/app/main.py` imports `Redis` and `SQLAlchemy text`; this is outside domain/core
  but should move behind queue/query/application boundaries.
- `services/api/app/db.py` and `services/api/app/audit.py` import SQLAlchemy; acceptable as
  infrastructure code, but the boundary is not yet explicit.
- `services/bim-worker/worker.py` imports `IfcOpenShell`, `Redis`, and `psycopg`; acceptable
  for the worker boundary because heavy BIM work belongs there.
- No frontend-to-database coupling was found.
- No viewer SDK import was found in domain/core or web; current viewer is a placeholder.

## Findings

### P0 - Blocks architecture or security

None found in the current static inspection.

### P1 - Must resolve before expanding bounded contexts

| Finding | Evidence | Impact | Recommended action |
|---|---|---|---|
| Routers contain application logic and SQL | `services/api/app/main.py` mixes route handlers, SQL, tenant filters, revision upload, audit/outbox, and selection resolver logic | Bounded contexts will become hard to protect as features grow | Introduce application services/repositories per context before adding FND/BIM/BOQ/SCH features |
| API directly depends on Redis client | `services/api/app/main.py` imports `Redis` and pushes to `bim:ingest` | Queue vendor choice leaks into API orchestration | Add a job queue port/adapter in FND-007; keep Redis implementation in adapter |
| API uses shared volume as storage adapter | `upload_revision` writes directly to `settings.upload_dir` | Object storage boundary is implicit and not content-addressable | Implement object storage port in FND-006 before production uploads |
| Audit/outbox helpers are untyped SQL helpers | `services/api/app/audit.py` writes raw event rows with free-form payload | Event contracts can drift from `specs/events` | Add typed event publisher/outbox adapter and contract validation in FND-005/FND-009 |
| Worker status updates are not yet idempotent/state-machine guarded | `services/bim-worker/worker.py` directly sets `PROCESSING`, `READY`, `FAILED` | Retries and duplicate jobs can produce ambiguous state | Address in BIM-005/BIM-014 before production ingest |

### P2 - Acceptable temporary debt

| Finding | Evidence | Impact | Recommended action |
|---|---|---|---|
| Domain package is README-only | `services/api/app/domain/README.md` | No actual domain boundary to enforce yet | Build domain services as FND/BIM tasks start |
| Adapter packages are README-only | `packages/adapters/*/README.md` | Contracts are named but not executable | Replace with typed ports/adapters when each feature lands |
| Frontend contains demo cross-selection rules | `apps/web/components/WorkArea.tsx` maps BOQ/activity IDs locally | Demo can be mistaken for domain authority | Move real selection to `/v1/selection/resolve`; keep demo clearly temporary |
| Work Area client has static fallback data | `apps/web/lib/api.ts` | Offline demo can hide API failures in manual testing | Gate demo fallback behind explicit dev/demo mode later |
| Test layers beyond API health are placeholders | `tests/*/README.md` | Architecture regressions are not automatically guarded | Add static architecture tests and contract tests in AUD/FND tasks |
| `activities.percent_complete` is mutable current state | `db/init/010_schema.sql` also has append-only `progress_records` | Acceptable demo projection, but can be misused as source of truth | Treat as projection or derive from `progress_records` in later progress tasks |

## Vendor Coupling Review

| File | Import/dependency | Classification | Impact |
|---|---|---|---|
| `services/api/app/main.py` | `from redis import Redis` | P1 API-to-queue adapter leak | Redis is queue infrastructure in API code, not domain/core |
| `services/api/app/main.py` | `from sqlalchemy import text` | P1 query boundary debt | SQL is in routers; should move to repositories/services |
| `services/api/app/db.py` | `from sqlalchemy import create_engine` | Acceptable infrastructure | DB adapter is minimal and explicit |
| `services/api/app/audit.py` | `from sqlalchemy import text` | P1 typed outbox/audit debt | Free-form event/audit writes need contract boundary |
| `services/bim-worker/worker.py` | `import ifcopenshell` | Acceptable worker vendor | Heavy IFC parsing is in async worker, not HTTP request |
| `services/bim-worker/worker.py` | `from redis import Redis`, `import psycopg` | Acceptable worker infrastructure | Worker owns queue consumption and persistence |
| `packages/viewer-adapter/src/index.ts` | No vendor import | Good boundary | Viewer remains replaceable |
| `services/api/app/domain` | No vendor import found | Good boundary | Domain/core vendor isolation currently holds |

No direct imports of IfcOpenShell, Redis, boto/S3 SDKs, viewer SDKs, Autodesk, Primavera,
ERP, or AI provider SDKs were found inside domain/core.

## Architectural Deviations and ADR Need

No new ADR was created for AUD-002. The deviations found are implementation debt within
accepted decisions ADR-0001, ADR-0002, and ADR-0003, not new architectural decisions:

- Modular monolith plus async workers remains valid.
- BIM identity remains revision-scoped through `UNIQUE (revision_id, global_id)` and the
  `element_lineage` table.
- Viewer remains behind a vendor-neutral adapter contract.

If future work chooses a concrete queue abstraction, object storage adapter, or viewer engine,
that decision should create or update an ADR.

## Boundaries to Protect Next

1. Create application/domain services before expanding API route behavior.
2. Introduce queue and storage ports before adding more upload/ingest workflows.
3. Keep IfcOpenShell and geometry processing in workers only.
4. Keep `revision_id + GlobalId` as persistent element identity and use `element_lineage`
   for continuity between revisions.
5. Preserve `element_boq_links` and `element_activity_links` as first-class provenance links.
6. Treat `progress_records`, model revisions, schedule baselines, and BOQ revisions as history;
   never replace them with only mutable current fields.
7. Add static architecture tests that fail on vendor imports from `domain/core`.
8. Make frontend selection/display state a consumer of API selection resolution, not authority.
