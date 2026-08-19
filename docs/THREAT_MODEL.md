# Threat Model - AUD-006

Date: 2026-08-18

Scope: initial threat model for the current harness around tenancy, IFC uploads, object
storage, BIM jobs and HTTP APIs. This document describes implemented controls and
known gaps; it does not introduce product features.

## System Summary

The current system is a modular-monolith FastAPI service, a Next.js web client, PostgreSQL
as system of record, Redis for the `bim:ingest` queue, a BIM worker that runs IfcOpenShell,
and a declared but not yet wired S3-compatible object storage adapter.

Primary assets:

| Asset | Sensitivity | Current owner |
|---|---|---|
| Organization and project membership boundaries | Critical | Foundation |
| IFC source artifacts | Critical | Storage / BIM platform |
| Normalized BIM elements and properties | High | BIM platform / Data platform |
| BOQ, activity, progress and QA/QC project data | High | Domain owners |
| Audit and outbox records | High | Foundation / Integrations |
| Redis job payloads | Medium | Platform / Workers |
| Web Work Area state | Medium | Frontend / Work Area |

## Trust Boundaries

| Boundary | Entry point | Trusted side | Untrusted side | Current status |
|---|---|---|---|---|
| Browser to API | `apps/web` -> FastAPI | API server | Browser/user input | PARTIAL, no auth context yet |
| API to PostgreSQL | SQLAlchemy connection | API/data platform | Request payloads | FUNCTIONAL, server-side project filters exist |
| API to upload artifact path | `UploadFile` -> local volume | API filesystem | User-provided IFC bytes/name | PARTIAL, dev storage path only |
| API to queue | Redis `bim:ingest` push | API/worker contract | Queue transport/payload replay | PARTIAL, direct Redis dependency |
| Worker to IFC parser | IfcOpenShell | Worker sandbox target | Untrusted IFC content | PARTIAL, isolated from HTTP but not sandboxed |
| Worker to database | psycopg writes | DB | Job payload/file parser output | PARTIAL, state machine hardening pending |
| API to outbox/audit | DB transaction | Foundation records | Caller-provided metadata | PARTIAL, typed event contracts pending |
| Viewer adapter | `ViewerAdapter` contract | App/domain identity | Vendor renderer internals | STUB, no production viewer selected |

## Data Flows

```text
Browser
  -> FastAPI /v1/projects, /v1/models, /v1/selection/resolve
  -> PostgreSQL with organization/project filters

Browser
  -> FastAPI /v1/models/{model_id}/revisions
  -> local upload volume using server-generated revision_id path
  -> PostgreSQL model_revisions + audit_events + outbox_events
  -> Redis bim:ingest
  -> BIM worker
  -> IfcOpenShell parses IFC asynchronously
  -> PostgreSQL bim_elements by (revision_id, GlobalId)
```

## Current Controls

| Control ID | Surface | Control | Evidence | Status |
|---|---|---|---|---|
| AUD006-TEN-001 | Tenant isolation | Project/model/work-area reads and writes validate `projects.organization_id` on the server. | `services/api/app/main.py` queries with `organization_id=:org`. | FUNCTIONAL for implemented endpoints |
| AUD006-TEN-002 | Selection resolver | Input IDs are not echoed as authority; IDs are resolved through tenant/project joins. | `services/api/tests/test_selection_scope.py`; `/v1/selection/resolve` joins through project/org. | FUNCTIONAL |
| AUD006-UPL-001 | IFC upload acceptance | Upload endpoint accepts only `.ifc` filenames for the MVP path. | `upload_revision` checks `file.filename.lower().endswith('.ifc')`. | FUNCTIONAL, weak content validation |
| AUD006-UPL-002 | Upload size | Upload endpoint rejects files above the 1 GiB development limit. | `upload_revision` checks `len(data) > 1024 * 1024 * 1024`. | FUNCTIONAL, non-streaming |
| AUD006-UPL-003 | Path traversal | Stored artifact path uses server-generated `revision_id` and ignores user path segments. | `file_path = upload_dir / f'{revision_id}.ifc'`. | FUNCTIONAL |
| AUD006-UPL-004 | Provenance | Revision upload writes audit and outbox records before queueing the worker job. | `record_audit`, `enqueue_outbox`, `redis_client.lpush`. | FUNCTIONAL, event typing pending |
| AUD006-JOB-001 | Heavy BIM work | IFC parsing runs in `services/bim-worker`, not inside the HTTP request. | API enqueues Redis job; worker imports `ifcopenshell`. | FUNCTIONAL |
| AUD006-JOB-002 | Worker failure state | Worker marks revision `FAILED` and stores bounded error text on exceptions. | `services/bim-worker/worker.py` updates status and truncates error. | FUNCTIONAL, state machine pending |
| AUD006-BIM-001 | BIM identity | Elements keep revision-scoped identity through `(revision_id, global_id)`. | `UNIQUE (revision_id, global_id)` in SQL schema. | FUNCTIONAL |
| AUD006-BIM-002 | Lineage | Cross-revision logical identity has a dedicated `element_lineage` table. | `db/init/010_schema.sql`. | STUB workflow, schema present |
| AUD006-AUD-001 | Audit/outbox | Critical implemented writes create audit/outbox records where applicable. | Project/model audit; revision upload audit + outbox. | PARTIAL |
| AUD006-API-001 | Input bounds | Selection resolver limits request IDs to 1..1000 via Pydantic. | `SelectionResolveIn.ids = Field(min_length=1, max_length=1000)`. | FUNCTIONAL |

## Top Risks

| Risk ID | Severity | Threat | Impact | Current mitigation | Required next mitigation | Owner | Verification |
|---|---|---|---|---|---|---|---|
| AUD006-R1 | P1 | Missing real auth/RBAC lets the harness rely on `default_org_id`. | Cross-tenant access once more tenants/users exist. | Server-side org filters exist for implemented endpoints. | FND-001/FND-002: authenticated tenant context, memberships and RBAC checks on every route. | Foundation | `python scripts/dev.py security-checklist`; future authorization matrix tests |
| AUD006-R2 | P1 | Malicious IFC exploits parser or exhausts memory/CPU. | Worker compromise, denial of service, poisoned ingest state. | Parsing is async in worker, not HTTP; upload size limit exists. | BIM-002/BIM-014/ENT-006: streaming upload, content sniffing, sandboxed worker, AV/malware scanning, resource limits and retry policy. | BIM platform / Security | Security checklist now; future malicious private corpus |
| AUD006-R3 | P1 | Object storage path is a shared dev volume, not immutable content-addressed storage. | Artifact tampering, weak retention/lifecycle, hard-to-audit provenance. | Server-generated revision path and SHA-256 recorded. | FND-006/BIM-003: storage adapter, immutable object keys, checksum verification and lifecycle policy. | Storage / Data platform | `AUD006-UPL-003`, `AUD006-UPL-004`; future storage adapter tests |
| AUD006-R4 | P1 | Redis job payload can be replayed or malformed because queue contract is direct and untyped. | Duplicate ingest, wrong file processing, inconsistent revision state. | Outbox row id is used as job id; worker failure state exists. | FND-007/BIM-005: typed queue port, idempotency keys, state transition guards and dead-letter policy. | Foundation / Workers | `AUD006-JOB-001`, `AUD006-JOB-002`; future worker idempotency tests |
| AUD006-R5 | P1 | Audit/outbox rows are free-form and not schema-validated end to end. | Broken integration contracts, weak forensic evidence. | Audit/outbox are inserted in the caller transaction for implemented writes. | FND-004/FND-005/FND-009: typed event publisher, correlation IDs, event schema validation and actor policy. | Foundation / Integrations | `AUD006-UPL-004`, `AUD006-AUD-001`; future event contract tests |
| AUD006-R6 | P2 | Viewer/property text could carry XSS payloads when a real renderer/property panel arrives. | Session/data compromise through UI rendering. | Current viewer is placeholder; no vendor SDK selected. | VWR/FND: escape property text, CSP/security headers, no dangerous HTML rendering, viewer adapter contract review. | Frontend / Viewer | Future UI security tests and CSP checks |
| AUD006-R7 | P2 | Bulk or cross-selection APIs can leak cross-project relationships if future writes bypass same-project checks. | Cross-project data disclosure or corrupted 4D/5D links. | Active selection resolver now scopes all source IDs and M2M links through project/org joins. | FND-016 plus write-service same-project invariant tests for each new write API. | API platform / Domain | `services/api/tests/test_selection_scope.py`; future auth matrix |
| AUD006-R8 | P2 | Dev CORS/default settings may be copied to production. | Browser-origin abuse or weak environment isolation. | CORS is limited to local dev origin in current harness. | ENT-006: environment-specific CORS/security headers/rate limiting checklist. | Platform / Security | Future config tests |

No P0 was found in AUD-006. P1 risks are accepted only as baseline debt because the current
repository is a harness and the roadmap already has FND/BIM/ENT tasks for hardening.

## STRIDE Summary

| Surface | Spoofing | Tampering | Repudiation | Information disclosure | Denial of service | Elevation of privilege |
|---|---|---|---|---|---|---|
| Tenancy/auth | Real auth absent | Tenant context can be miswired later | Actor is static `dev-user` | Cross-tenant reads if filters omitted | N/A | Missing RBAC |
| IFC upload | Model ID guessing | Malicious or swapped artifact | Audit exists but actor weak | Filename may expose user naming | Large files/parser cost | Parser exploit |
| Object storage | Future signed URL misuse | Dev volume mutable | SHA recorded but no immutable object proof | Artifact URI policy missing | Storage exhaustion | Adapter credential misuse |
| Jobs/Redis | Job producer not authenticated at queue boundary | Payload replay/edit | Outbox exists, queue contract untyped | Job payload includes file path | Queue flood/retries | Worker trust of payload |
| APIs | No user auth yet | Future writes may skip invariants | Audit partial | Error/detail leakage future | Large/bulk payloads | Missing permission checks |
| Viewer | N/A now | Vendor/plugin script risk future | N/A | Property data leakage | Heavy model render | XSS/session abuse |

## Security Checklist

The executable AUD-006 checklist is:

```bash
python scripts/dev.py security-checklist
```

It verifies that this threat model and `tests/security/README.md` contain the required
AUD-006 control/risk IDs and that the current code still exposes the baseline controls
documented above.

## ADR Impact

No ADR was created for AUD-006. This task documents the current threat model and known
security debt without changing a boundary, public contract or architectural decision.

Future ADRs are expected when selecting:

- the production object storage adapter and immutable key strategy;
- the queue abstraction and worker retry/dead-letter semantics;
- authentication/RBAC/ABAC model;
- production viewer engine and security constraints.
