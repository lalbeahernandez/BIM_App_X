# Domain Schema Matrix - AUD-004

Date: 2026-08-18

Scope: reconciliation of the current domain model, SQL schema, API schemas, OpenAPI
surface and event contracts. This is a baseline audit, not an implementation of future
bounded-context features.

Status values used here:

- `ALIGNED`: current repository artifacts agree for the implemented surface.
- `PARTIAL`: the current harness is intentionally smaller than the target model.
- `NOT_IMPLEMENTED_YET`: planned concept with no current API/table/workflow.
- `CONFLICT`: repository artifacts disagree in a way that needs correction or tracking.

## Executive Summary

No unresolved P0 remains after AUD-004. The critical BIM identity decision is aligned:
`bim_elements.id` is the database UUID primary key, `(revision_id, global_id)` is unique,
and `element_lineage` is the continuity table across revisions.

One active P0 was found and corrected: `/v1/selection/resolve` accepted arbitrary IDs as
authoritative and could echo or resolve links without first proving that those IDs belong
to the configured organization/project path. The endpoint now validates element, BOQ and
activity inputs through server-side joins to `projects.organization_id` and only resolves
many-to-many links within the same project.

Most remaining gaps are P1/P2 expected from the starter harness: migration framework is
planned for FND-003, audit/outbox events are not yet typed end to end, status vocabularies
are text/check hybrids, schedule calendars and baselines are not implemented, and several
cross-table same-project invariants are currently enforced by service-layer queries rather
than composite database constraints.

## Domain To Data/API/Event Matrix

| Entity | Domain docs | DB table/storage | PK | Tenant/project path | API schema | API endpoint | Event | Historical? | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Organization | Target root tenant | `organizations` | `id uuid` | Root | None | Implicit default org only | None | Created timestamp | PARTIAL | Auth/membership deferred to FND-001/FND-002. |
| Project | `Organization -> Project` | `projects` | `id uuid` | Direct `organization_id` | `ProjectCreate`, `ProjectOut` | `GET/POST /v1/projects` | Audit on create | Created timestamp | ALIGNED | `UNIQUE (organization_id, code)` exists. |
| Model | `Project -> Model` | `models` | `id uuid` | Direct `project_id` | `ModelCreate`, `ModelOut` | `POST /v1/projects/{project_id}/models` | Audit on create | Created timestamp | ALIGNED | `ON DELETE CASCADE` from project is acceptable for starter, retention policy future. |
| ModelRevision | `Model -> ModelRevision` | `model_revisions` + upload artifact path | `id uuid` | Indirect via model -> project -> org | `RevisionOut` | `POST /v1/models/{model_id}/revisions`, listed by work-area | Outbox `model.revision.ingest_requested.v1`, audit upload | Revision rows retained conceptually | PARTIAL | Source file immutable by concept; final object storage adapter deferred. |
| BimElement | Revision-scoped element | `bim_elements` | `id uuid` | Indirect via revision -> model -> project -> org | None | Selection resolver only | None current | Per revision | ALIGNED | `UNIQUE (revision_id, global_id)` confirms revision identity. |
| ElementLineage | Cross-revision continuity | `element_lineage` | `id uuid` | Indirect through from/to elements | None | None | None current | Lineage rows preserve continuity evidence | PARTIAL | Workflow not implemented yet; table has match/provenance fields. |
| ClassificationNode | Classification/rules | `classification_nodes` | `id uuid` | Nullable direct `project_id` | None | None | None | Reference taxonomy | PARTIAL | `project_id` nullable allows global taxonomy; tenant policy must clarify shared vs tenant data. |
| ElementClassification | Element-classification M2M | `element_classifications` | `(element_id, classification_id)` | Indirect via element and optional classification project | None | None | None | Link provenance | PARTIAL | Needs same-project/global taxonomy policy before classification workflow. |
| Quantity | Element/project quantity | `quantities` | `id uuid` | Direct `project_id`, optional element path | None | None | None | Append-like rows by created_at | PARTIAL | Supports name/value/unit/source/rule_id; same-project invariant is service/domain concern today. |
| BoqItem | BOQ/cost line | `boq_items` | `id uuid` | Direct `project_id` | `WorkAreaBoq` read model | `GET /v1/projects/{project_id}/work-area` | None current | Simplified `revision` column | PARTIAL | `UNIQUE(project_id, code, revision)` is consistent for starter; full cost revisions future. |
| ElementBoqLink | Element <-> BOQ | `element_boq_links` | `(element_id, boq_item_id)` | Indirect via element revision and BOQ project | None | `POST /v1/selection/resolve` reads | None current | Link provenance | ALIGNED | First-class M2M with `source`, `rule_id`, `weight`, `created_at`; API now scopes links same-project. |
| Cost/Rate concepts | Cost/rate target model | `boq_items.rate`, `resources.unit_cost` | N/A | Direct through project tables | `WorkAreaBoq.rate/amount` read model | Work-area read | None | Future cost revisions | PARTIAL | Decimal SQL preserved; API exposes floats in demo read model, P1 before 5D writes. |
| WbsNode | Project WBS | `wbs_nodes` | `id uuid` | Direct `project_id` | None | Work-area activity list indirectly | None | Current WBS only | PARTIAL | `UNIQUE(project_id, code)` exists; baselines future. |
| Activity | Schedule activity | `activities` | `id uuid` | Direct `project_id` | `WorkAreaActivity` | `GET /v1/projects/{project_id}/work-area` | None current | Current-state fields + future progress records | PARTIAL | `percent_complete` documented as projection/cache; `calendar_id` has no table yet. |
| ActivityRelation | Logic relation | `activity_relations` | `(predecessor_id, successor_id, relation_type)` | Indirect through activities | None | None | None | Current relation set | PARTIAL | Relation type CHECK exists; no DB constraint that predecessor/successor share project. |
| ElementActivityLink | Element <-> Activity | `element_activity_links` | `(element_id, activity_id, role)` | Indirect via element revision and activity project | None | `POST /v1/selection/resolve` reads | None current | Link provenance | ALIGNED | First-class M2M with `role`, `source`, `created_at`; API now scopes links same-project. |
| Calendar concept | Target planning calendar | None | N/A | Would be project scoped | None | None | None | Future baselines/calendars | NOT_IMPLEMENTED_YET | `activities.calendar_id` is an unbound future field; P1 before scheduling context. |
| Resource | Productivity/cost resource | `resources` | `id uuid` | Direct `project_id` | None | None | None | Current catalog row | PARTIAL | Decimal unit cost and currency preserved. |
| Crew | Productivity crew | `crews` | `id uuid` | Direct `project_id` | None | None | None | Current catalog row | PARTIAL | `UNIQUE(project_id, code)` exists. |
| ProductivityRate | Productivity assumptions | `productivity_rates` | `id uuid` | Direct `project_id` | None | None | None | Effective-from assumptions | PARTIAL | No effective-to/versioning yet; P1 before productivity workflow. |
| ProgressRecord | Progress history | `progress_records` | `id uuid` | Direct `project_id`, optional activity/element | None | None | None | Append-only conceptual source | PARTIAL | SQL cannot enforce append-only alone; service/domain/authorization policy future. |
| Issue | Collaboration/BCF issue | `issues` | `id uuid` | Direct `project_id` | None | None | None | Status lifecycle future | PARTIAL | Status/priority text not constrained yet; BCF workflow future. |
| IssueElement | Issue-element link | `issue_elements` | `(issue_id, element_id)` | Indirect through issue and element | None | None | None | Link evidence | PARTIAL | Needs same-project enforcement before issue APIs. |
| Inspection | QA/QC inspection | `inspections` | `id uuid` | Direct `project_id`, optional activity/element | None | None | None | QA evidence/history future | PARTIAL | Status text not constrained; same-project validation service/domain future. |
| AuditEvent | Audit provenance | `audit_events` | `id uuid` | Direct `organization_id`, optional `project_id` | None | Internal helper only | None | Append-oriented | PARTIAL | No FK to org/project yet; FND-004 will harden actor/correlation/before-after policy. |
| OutboxEvent | Integration event | `outbox_events` | `id uuid` | Direct `organization_id`, optional `project_id` | None | Internal helper only | JSON schema specs exist | Append/retry state | PARTIAL | Actual row splits metadata from payload; event contract validation deferred to FND-005/FND-009. |

## Tenant And Project Resolution Matrix

| Entity | Direct project_id? | Indirect project path | Organization path | Tenant isolation strategy future |
|---|---:|---|---|---|
| Organization | No | N/A | Self | Auth context maps user to organization. |
| Project | No | Self | `projects.organization_id` | Server-side org filter already used for project list/create. |
| Model | Yes | `models.project_id` | `models -> projects.organization_id` | API validates project in default org before create. |
| ModelRevision | No | `model_revisions -> models.project_id` | Through model/project | Upload validates model in default org. |
| BimElement | No | `bim_elements -> model_revisions -> models.project_id` | Through model/project | Selection resolver now validates element IDs through org/project joins. |
| ElementLineage | No | Through both elements | Through both element paths | P1: future lineage service must enforce compatible revision/project paths. |
| ClassificationNode | Nullable | Direct when project scoped | Via project when set | P1: clarify global classification vs tenant-specific taxonomy. |
| ElementClassification | No | Element path plus optional classification project | Element path plus classification policy | P1 before classification writes. |
| Quantity | Yes | Optional element path | Direct project plus optional element path | P1: service/domain must enforce element belongs to same project. |
| BoqItem | Yes | Self | `boq_items -> projects.organization_id` | Work-area filters by project; future writes need auth context. |
| ElementBoqLink | No | Element path and BOQ project | Both paths | API selection reads now enforce same project. |
| WbsNode | Yes | Self | Through project | Future writes need auth context. |
| Activity | Yes | Self | Through project | Work-area filters by project. |
| ActivityRelation | No | Both activities | Through both activity paths | P1: same-project relation validation before schedule writes. |
| ElementActivityLink | No | Element path and activity project | Both paths | API selection reads now enforce same project. |
| Resource/Crew/ProductivityRate | Yes | Self | Through project | Future productivity writes need auth context. |
| ProgressRecord | Yes | Optional activity/element paths | Direct project plus optional paths | P1: service/domain must enforce same-project optional refs. |
| Issue/Inspection | Yes | Optional activity/element paths | Direct project plus optional paths | P1 before collaboration/QA writes. |
| AuditEvent/OutboxEvent | Optional project | Project when set | Direct organization_id | FND-004/FND-005 will add stricter FK/contract policy. |

## Invariant Catalog

| ID | Confirmed invariant | Repository evidence | Status |
|---|---|---|---|
| INV-BIM-001 | BimElement identity within a revision is `revision_id + GlobalId`; `GlobalId` is not a global PK. | `bim_elements.id uuid PRIMARY KEY`; `UNIQUE (revision_id, global_id)`. | ALIGNED |
| INV-BIM-002 | Original ModelRevision source file is immutable conceptually. | `model_revisions` stores file metadata; upload creates a new revision and artifact path. | PARTIAL |
| INV-BIM-003 | Cross-revision continuity uses `element_lineage`. | `element_lineage` table with from/to element, match method, confidence, approval. | ALIGNED |
| INV-LINK-001 | Element to BOQ is many-to-many with provenance. | `element_boq_links` PK `(element_id, boq_item_id)`, `source`, `rule_id`, `weight`. | ALIGNED |
| INV-LINK-002 | Element to Activity is many-to-many with provenance. | `element_activity_links` PK `(element_id, activity_id, role)`, `role`, `source`. | ALIGNED |
| INV-PRG-001 | Progress history is append-only conceptually. | `progress_records` table; `activities.percent_complete` documented as projection/cache. | PARTIAL |
| INV-AUD-001 | Audit records are not ordinary mutable business entities. | `audit_events` append helper inserts rows; no update path found. | PARTIAL |
| INV-TEN-001 | Every project resource must resolve to one authorized tenant/project. | Direct/indirect paths exist; selection resolver fixed for active reads. | PARTIAL |
| INV-COST-001 | Money/cost values preserve decimal precision and currency. | SQL uses `numeric(24,8)` and `currency char(3)`. | PARTIAL |
| INV-TIME-001 | Real event timestamps and project schedule dates have distinct semantics. | `created_at/occurred_at` use `timestamptz`; planning uses `date`; project has `timezone`. | ALIGNED |

## Schema Findings

### P0

| Finding | Evidence | Resolution |
|---|---|---|
| Active selection resolver could echo or resolve unscoped IDs. | `resolve_selection` previously added input IDs directly and queried link tables without org/project joins. | Fixed in `services/api/app/main.py`; added test and static check. |

### P1

| Finding | Evidence | Required before |
|---|---|---|
| Migration framework absent. | Only `db/init/*.sql` exists; FND-003 is planned. | Production schema changes. |
| Event contract drift between outbox row and JSON schemas. | Actual outbox stores metadata columns plus payload; `model-revision-ingest-requested` schema expects event metadata in one object. | FND-005/FND-009/BIM-004. |
| `activities.calendar_id` references no `calendars` table. | Column exists without FK/table. | Scheduling/calendar implementation. |
| Same-project constraints for optional cross-entity refs are service/domain responsibilities today. | `progress_records`, `issue_elements`, `inspections`, `activity_relations`, classifications can reference rows from incompatible projects if future write APIs skip validation. | Before those write APIs ship. |
| API read models expose money/quantities as `float`. | `WorkAreaBoq.quantity/rate/amount` and `WorkAreaActivity.percent_complete` are floats. | Before 5D/progress writes or financial contract stability. |
| Status vocabularies incomplete. | `model_revisions.status` and `activity_relations.relation_type` have CHECKs; `boq_items.status`, `issues.status`, `inspections.status` are text. | Before workflows/state machines. |
| Audit/outbox tables lack FKs to organization/project. | `organization_id uuid NOT NULL`, `project_id uuid` without references. | FND-004/FND-005 hardening. |

### P2

| Finding | Evidence | Notes |
|---|---|---|
| Delete cascades can remove operational history in dev DB. | Project/model cascades reach many business rows; audit/outbox are not cascaded. | Acceptable starter; retention/soft-delete policy later. |
| BOQ revisioning is simplified. | `boq_items.revision` rather than explicit BOQ revision entity. | Documented limit; deeper model belongs to BOQ tasks. |
| Classification taxonomy scope is nullable. | `classification_nodes.project_id` nullable. | Useful for global taxonomies, but needs policy before writes. |

## Nullability, Constraints And Cascades

- PKs are UUIDs across canonical tables.
- `projects` has `UNIQUE (organization_id, code)`.
- `models.project_id`, `model_revisions.model_id`, `bim_elements.revision_id` are NOT NULL FKs.
- `model_revisions` has `UNIQUE (model_id, revision_no)` and status CHECK.
- `bim_elements` has `UNIQUE (revision_id, global_id)`.
- `activity_relations.relation_type` has CHECK `FS/SS/FF/SF`.
- BOQ, quantities, cost and productivity numeric values use `numeric(...)`; no monetary SQL float was found.
- Project deletion cascades to project business data. That is suitable for disposable dev harness data, but production retention policy must prevent accidental historical loss.
- `progress_records.element_id` uses `ON DELETE SET NULL`, preserving the progress record if an element row is removed.
- `audit_events` and `outbox_events` do not cascade from projects and have no FK constraints yet.

## Date, Time And Status Semantics

- Real event timestamps use `timestamptz`: created/occurred/published/performed timestamps.
- Planning fields use `date`: planned/actual start/finish, progress data date, productivity effective date.
- Project timezone exists on `projects.timezone`; calendar semantics are not implemented yet.
- `ModelRevision.status` values are constrained to `QUEUED`, `PROCESSING`, `READY`, `FAILED`.
- BOQ, issue and inspection status values are currently text vocabularies and require value contracts before workflow implementation.

## API Reconciliation

| Operation | Live FastAPI route | OpenAPI | Status | Notes |
|---|---|---|---|---|
| Health | `GET /health` | Present | MATCH | Minimal response schema only. |
| List projects | `GET /v1/projects` | Present | PARTIAL | OpenAPI has description, not component schema. |
| Create project | `POST /v1/projects` | Present | PARTIAL | Pydantic schema richer than OpenAPI. |
| Create model | `POST /v1/projects/{project_id}/models` | Present | PARTIAL | Tenant check in API. |
| Upload revision | `POST /v1/models/{model_id}/revisions` | Present | PARTIAL | Async enqueue and audit/outbox current harness path. |
| Work area | `GET /v1/projects/{project_id}/work-area` | Added in AUD-004 | PARTIAL | Read model only; schemas not expanded in OpenAPI. |
| Selection resolve | `POST /v1/selection/resolve` | Present | PARTIAL | Resolver now scopes IDs server-side. |

Pydantic mapping:

- `ProjectCreate/ProjectOut` -> `projects`.
- `ModelCreate/ModelOut` -> `models`.
- `RevisionOut` -> `model_revisions`.
- `WorkAreaBoq` -> read model from `boq_items`.
- `WorkAreaActivity` -> read model from `activities`.
- `WorkAreaOut` -> read model from BOQ/activity/revision queries.
- `SelectionResolveIn/Out` -> command/read model over `element_boq_links` and `element_activity_links`.

## Event Reconciliation

| Event | Actual producer | DB outbox | JSON schema | Status | Notes |
|---|---|---|---|---|---|
| `model.revision.ingest_requested.v1` | `upload_revision` | `outbox_events.event_type`, `organization_id`, `project_id`, `payload` | `model-revision-ingest-requested.schema.json` | CONFLICT/P1 | Actual payload contains `revision_id`, `model_id`, `file_path`; schema expects event metadata and project_id in the same object. |
| Generic envelope | `enqueue_outbox` helper | Metadata split across columns | `domain-event-envelope.schema.json` | PARTIAL/P1 | Envelope uses `tenant_id`; DB uses `organization_id`. Needs typed publisher in FND-005/FND-009. |

The mismatch is documented as P1 because the current active worker consumes the Redis job,
not the JSON-schema-validated outbox event. It must be fixed before relying on outbox
events as integration contracts.

## Migration State

- migration framework = `NOT_IMPLEMENTED_YET`
- migration dry run = `NOT_APPLICABLE / BLOCKED_BY_PLANNED_FND-003`
- FND-003 dependency = required before claiming production migration up/down support

`db/init/*.sql` remains the clean-database bootstrap source for the starter harness. Editing
init SQL would not migrate an existing database; no AUD-004 init SQL change was required.

## Schema Validation

- schema static check = `scripts/check_domain_schema.py`
- schema smoke = `BLOCKED_EXTERNAL` in the current Windows environment because Docker daemon
  is not accessible
- domain-schema check = static invariant check over SQL/API/OpenAPI/event schema

The static check validates:

- canonical table presence;
- `UNIQUE (revision_id, global_id)`;
- lineage fields;
- element-to-BOQ and element-to-Activity link provenance;
- progress/audit/outbox structures;
- model revision status/revision constraints;
- OpenAPI presence for active routes;
- selection resolver tenant/project scoping.
