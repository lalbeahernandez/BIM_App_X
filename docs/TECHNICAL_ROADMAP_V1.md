# Technical Roadmap V1 - AUD-008

Date: 2026-08-19

## Executive Summary

AUD-008 freezes the executable technical roadmap for BIM Control X before Foundation
starts. The product remains a harness, not a finished product. The roadmap keeps the
existing 140 task graph as canonical and turns AUD-001 through AUD-007 into release gates,
owners and debt deadlines.

V1 builds a modular monolith with async BIM workers and replaceable adapters. It does not
make microservices, Kafka, event sourcing or Kubernetes a V1 requirement. Those may be
future ADR-backed decisions only when scaling, security, ownership or deployment evidence
requires them.

No P0 blocks the start of FND-001. The P1 debt is real, owned by future tasks, and must be
resolved before the release gate where it matters.

## Frozen Architecture

Architecture V1 is frozen as:

```text
Next.js Web
  -> FastAPI API
  -> Application / Domain
  -> Ports
  -> Adapters
  -> PostgreSQL/PostGIS
  -> Redis
  -> Object Storage
  -> External systems
```

Heavy BIM processing is frozen as:

```text
API
  -> Job Queue
  -> BIM Worker
  -> IfcOpenShell / geometry / validation
  -> PostgreSQL + Object Storage
```

Required style:

- Modular monolith for API/application/domain boundaries.
- Async BIM workers for CPU, memory, parser and geometry work.
- Replaceable adapters for storage, queue, viewer, scheduling, search, ERP, CDE and AI.
- PostgreSQL/PostGIS is the business system of record.
- Redis is queue/cache/lock infrastructure, not business state.
- Object storage holds files and immutable artifacts, not normalized domain data.

Not V1 requirements:

- Microservices as a starting architecture.
- Kafka as a required event bus.
- Event sourcing as a required persistence model.
- Kubernetes as a required runtime target.

## Frozen Invariants

These invariants are non-negotiable for V1:

| Invariant | Frozen decision |
|---|---|
| BIM identity | `(revision_id, GlobalId)` is the persistent element identity. |
| Internal DB identity | Internal rows use UUID primary keys. |
| Cross-revision continuity | `element_lineage` preserves logical continuity evidence. |
| Element to BOQ | Many-to-many through `element_boq_links` with provenance. |
| Element to Activity | Many-to-many through `element_activity_links` with provenance. |
| Heavy BIM | Never runs inside the normal synchronous HTTP request lifecycle. |
| Progress | Source progress records are historical/append-oriented. |
| Audit | Audit history is preserved and not treated as ordinary mutable state. |
| Critical writes | Audit/outbox strategy is required where applicable. |
| Tenant/project access | Authorization and scoping are validated server-side. |
| Client IDs | Client-provided IDs are never authorization authority by themselves. |
| Uploads | Uploads are untrusted input. |
| Viewer | Domain/core never depends on viewer SDKs or mesh indexes. |
| Costs and quantities | Persist decimal values, units, currency and source/provenance. |

## What We Are Not Building Yet

Before Foundation, do not implement:

- tenant context code beyond existing harness behavior;
- RBAC/auth provider integration;
- migrations;
- real object storage adapter usage;
- queue abstraction;
- BIM feature expansion;
- production viewer;
- BOQ, CPM, 4D, progress, BCF/QA workflows;
- enterprise SSO, DR, HA or integrations.

AUD-008 is a roadmap freeze. FND-001 is the next implementation task.

## Source Of Truth Map

| Topic | Source of truth |
|---|---|
| Architecture | `docs/ARCHITECTURE.md` plus `docs/adr/*` |
| Roadmap V1 | `docs/TECHNICAL_ROADMAP_V1.md` |
| Release gate summary | `codex/RELEASE_GATES.md` |
| Domain model | `docs/DOMAIN_MODEL.md` |
| Domain/schema mapping | `docs/DOMAIN_SCHEMA_MATRIX.md` |
| Performance | `docs/PERFORMANCE_BUDGETS.md` and `config/performance-budgets.json` |
| Security | `docs/THREAT_MODEL.md` |
| Fixtures | `fixtures/manifest.json` and `docs/FIXTURE_CATALOG.md` |
| Task graph | `codex/tasks.yaml` |
| Task status | `codex/task-status.csv` |
| Human task index | `codex/TASK_INDEX.md` |
| Toolchain | `docs/DEVELOPMENT_ENVIRONMENT.md` |
| Data governance | `docs/DATA_GOVERNANCE.md` |

Do not create competing task lists or alternate status trackers.

## Release Model

| Release | Name | Scope | Entry criteria | Exit criteria | Acceptable debt |
|---|---|---|---|---|---|
| R0 | Audited Harness | AUD-001 through AUD-008 | Harness exists and AUD dependencies pass | AUD phase DONE, roadmap frozen, no P0 before FND-001 | External local smoke/Docker blockers if documented |
| R1 | Foundation | FND-001 through FND-016 | R0 complete | tenant/RBAC/migrations/audit/outbox/storage/jobs/contracts/observability gates pass | P2 UX polish and non-critical adapter depth |
| R2 | BIM Core | BIM-001 through BIM-018 | R1 storage, queue, audit and OpenAPI ready | immutable IFC upload, async ingest, element index, schema/psets/qto/units, golden regressions | large benchmark calibration if documented |
| R3 | BIM Work Area | VWR-001 through VWR-014 | R2 BIM query/golden ready | production viewer adapter, artifacts, real model load, GlobalId selection, cross-selection, visual/perf gates | advanced clipping polish unless required by pilot |
| R4 | 4D/5D Controls | BOQ-001 through BOQ-016, SCH-001 through SCH-016, D4-001 through D4-008 | R2/R3 selection and element APIs ready | BOQ, QTO, cost rollups, CPM, Gantt and 4D simulation usable with golden tests | non-core import/export adapters |
| R5 | Project Controls Beta | PRG-001 through PRG-012 and COL-001 through COL-008 | R4 baselines and links ready | append-only progress, productivity/EVM, issues/BCF/QA/IDS and dashboards | advanced enterprise connectors |
| R6 | Pilot Ready | Minimum enterprise hardening for a controlled pilot | R5 complete and pilot threat/perf risks mitigated | OIDC or controlled auth, rate limits/security headers, backup/restore, observability, runbooks, MEDIUM certification where relevant | full SAML/ABAC/RLS/HA if pilot risk accepts |
| R7 | Full Enterprise | ENT-001 through ENT-016 | Pilot evidence and enterprise requirements | SSO, SAML as needed, ABAC/RLS decision, secrets/KMS, DR, HA, integrations, load/soak certification | only explicitly accepted P2 backlog |

## AUD Phase Closure

| Task | Result frozen by AUD-008 |
|---|---|
| AUD-001 | Harness baseline and component classification exist; local external blockers are documented. |
| AUD-002 | Architecture inventory, bounded contexts, ownership and vendor coupling review are recorded. |
| AUD-003 | Python/Node/Docker/GNU Make expectations and Windows canonical commands are documented. |
| AUD-004 | Domain/schema/API/event matrix exists; selection resolver P0 was fixed; remaining issues are P1/P2. |
| AUD-005 | Performance budgets, dataset classes and gate tiers are defined. |
| AUD-006 | Threat model, current controls and security risk owners are defined. |
| AUD-007 | Fixture manifest, fixture validator and golden policy are defined. |
| AUD-008 | Roadmap V1, release gates, critical path, debt policy and FND-001 authorization are frozen. |

## Critical Path

The minimum critical path to an integrated product is:

```text
AUD
  -> FND
  -> BIM
  -> VWR
  -> BOQ/SCH
  -> D4
  -> PRG
  -> COL
  -> ADV/ENT
```

The real task graph allows controlled parallelism after boundaries are stable:

- FND-001/FND-002 unlock authorization; FND-003 unlocks migrations and many schema tasks.
- FND-004/FND-005/FND-006/FND-007 are the backbone for critical writes, events, storage and jobs.
- BIM-001 through BIM-017 form the core path to stable element identity and query APIs.
- VWR-001 can start only after BIM-017 and AUD-005; viewer selection needs real BIM facts.
- BOQ and Scheduling can proceed in parallel after their dependencies are ready.
- D4 depends on BIM element APIs, scheduling and viewer cross-selection.
- Progress/EVM depends on BOQ, schedule baselines, 4D links and audit.
- Collaboration can start after Work Area/viewer and audit/storage foundations exist.
- Advanced and Enterprise tasks should run only when their dependent vertical slices produce evidence.

## Dependency Policy

- `codex/tasks.yaml` is the only machine-readable dependency graph.
- `codex/task-status.csv` is the only operational status tracker.
- Do not renumber, delete or redesign the 140 tasks during implementation tasks.
- Change dependencies only for a demonstrated contradiction that would create a P0 or invalid release gate.
- Every P0/P1 finding must have an owner task or `UNOWNED_GAP`.
- A task may start only when declared dependencies are DONE.
- A release gate is not complete because tasks are checked off; tests, security, data integrity,
  performance, docs and observability criteria must also pass where applicable.

## Parallelization Policy

Foundation starts mostly sequentially because tenant context, migrations, audit/outbox,
storage, queue and error contracts shape every later boundary.

Safe parallelization windows:

- After FND-001, FND-008/FND-011 can proceed while RBAC continues, if shared error/session contracts are coordinated.
- After FND-003, storage (FND-006) can proceed separately from audit/outbox (FND-004/FND-005).
- After FND-009 and BIM-015, BOQ and Scheduling can split across teams.
- Frontend Work Area can work against stable OpenAPI/adapter contracts while workers continue ingestion tasks.
- Collaboration/QA can start after VWR-014/FND-004/FND-006 without blocking Advanced research.
- Enterprise hardening can prepare policies/runbooks in parallel, but implementation waits for its graph dependencies.

Avoid parallel work that changes the same public API, schema or domain invariant without a lead task and ADR decision.

## Foundation Gate

Foundation complete means FND-001 through FND-016 are DONE and verified:

- tenant context propagated server-side;
- RBAC enforced in API, not only UI;
- migration framework and fresh/bootstrap path exist;
- transactional audit and transactional outbox are reliable;
- ObjectStorage port/adapter replaces shared-volume assumptions for production paths;
- job queue abstraction hides Redis from application orchestration;
- error envelope and correlation IDs are standard;
- OpenAPI contract is verified against implementation;
- frontend auth/session boundary is explicit;
- feature flags have safe defaults;
- observability baseline emits logs/metrics/traces;
- health/readiness separates liveness from dependencies;
- CI gates include harness, lint, typecheck, tests and contract checks;
- bootstrap is reproducible;
- multi-tenant isolation suite covers negative cases.

Foundation cannot be complete if tenant isolation is incomplete, migrations are absent,
critical writes lack audit/outbox strategy, workers depend on HTTP implementation details,
Object Storage is hardcoded, or multi-tenant negative tests do not exist.

## BIM Gate

BIM ingestion complete means BIM-001 through BIM-018 are DONE or intentionally split by target:

- Model and ModelRevision domain are explicit;
- uploads stream and do not parse full IFC synchronously;
- checksum and immutable storage are enforced;
- enqueue happens after commit through outbox/job abstractions;
- worker state machine is idempotent;
- IFC2x3/IFC4/IFC4.3 schema detection is deterministic;
- IfcProduct index preserves `(revision_id, GlobalId)`;
- spatial hierarchy, Psets, QTO, classifications and units are normalized with provenance;
- geometric metadata does not couple to a renderer;
- retry/error handling is safe and observable;
- element query API is paginated and tenant-scoped;
- revision summaries exist;
- golden IFC regression uses cataloged fixtures;
- performance benchmark is recorded for the appropriate dataset tier.

Critical invariant: HTTP upload acceptance is not complete IFC processing.

## Viewer Gate

Viewer/Work Area complete means VWR-001 through VWR-014 are DONE:

- viewer ADR/benchmark selects a production adapter;
- ViewerAdapter remains the boundary;
- geometry artifact contracts and worker pipeline exist;
- artifact manifest API is versioned;
- real model loading works;
- selection is based on revision and GlobalId;
- hide/isolate/show, properties, clipping and measurement are usable;
- federation and cross-selection work across Viewer, BOQ and Gantt;
- progressive loading and performance are measured;
- visual and E2E regression guard the Work Area.

Domain/core must not depend on the viewer SDK.

## BOQ, Schedule And 4D Gates

BOQ/5D complete means BOQ-001 through BOQ-016 are DONE:

- BOQ hierarchy and revisions;
- CRUD, manual links and mapping rules;
- async mapping jobs;
- quantity rules, QTO and unit conversion;
- overrides, rate catalogs, cost revisions and rollups;
- traceability API and UI;
- import/export when target requires it;
- golden 5D regression using cataloged fixtures;
- provenance preserved for mappings, quantities, rates and overrides.

Scheduling complete means SCH-001 through SCH-016 are DONE:

- WBS, activities, calendars and working time;
- FS/SS/FF/SF relationships;
- CPM forward/backward pass, float, constraints, milestones;
- data date semantics, imports, baselines and what-if where target requires;
- schedule query/Gantt API and real Gantt UI;
- golden CPM suite.

4D complete means D4-001 through D4-008 are DONE:

- element-activity links;
- 4D state engine, timeline, colors and status legend;
- incremental updates and federation;
- planned vs actual;
- E2E and performance gate.

## Progress And Collaboration Gates

Progress/EVM complete means PRG-001 through PRG-012 are DONE:

- append-only progress records;
- physical quantities, resources, crews and productivity rates;
- forecast, PV, EV, AC, EVM KPIs and S-curves;
- golden progress/EVM regression.

`activities.percent_complete` may remain a projection/cache, but it is not the definitive
historical source.

Collaboration/QA complete means COL-001 through COL-008 are DONE:

- issues/comments;
- viewpoints and components by GlobalId;
- BCF import/export;
- inspections, NCR, punch and evidence attachments;
- IDS validation jobs;
- notifications/events.

## Advanced Gate

Advanced scope is explicitly after basic workflows:

- revision diff;
- lineage candidate matching and manual remap;
- clash orchestration;
- CRS/georeferencing and parcel/setback analysis;
- search indexing;
- read-only grounded AI copilot.

AI is not a structural dependency of core workflows and must stay behind adapters and
authorized APIs.

## Pilot And Enterprise Criteria

Pilot ready is not the same as full enterprise complete.

Pilot ready requires:

- Foundation complete;
- BIM, viewer and required 4D/5D workflows usable for the pilot scope;
- HIGH/CRITICAL threats applicable to exposed surfaces mitigated;
- OIDC or controlled identity path;
- rate limiting/security headers for exposed endpoints;
- backup/restore and rollback path;
- observable API/worker health;
- signed or disabled external webhooks according to pilot scope;
- release certification for relevant TINY/SMALL/MEDIUM datasets;
- runbooks and known-risk acceptance.

Full enterprise complete adds:

- SAML if required;
- ABAC/project permissions and RLS decision;
- secrets/KMS and key rotation;
- HA and worker scaling;
- retention/lifecycle/legal hold;
- full integration framework and connectors;
- compliance exports;
- load/soak/performance certification;
- production readiness and go-live checklist.

## Performance Gates

AUD-005 defines the budgets. Gate tiers:

| Tier | Required scope |
|---|---|
| PR | static budget config, unit/lint/typecheck, fast harness, health smoke only when API is available |
| Nightly | SMALL API/DB query suite, SMALL ingest, Work Area timings, trend comparison |
| Release certification | MEDIUM/LARGE ingest, geometry, viewer FPS/memory, load/soak, federation, 4D/progress/QA suites |

Do not turn every aspirational LARGE target into a PR blocker. Regressions must compare
the same dataset, hardware profile and warm/cold state.

## Security Gates

AUD-006 defines the threat model. No release exposing a surface may ignore an exploitable
HIGH/CRITICAL threat for that surface.

| Gate | Required security posture |
|---|---|
| Foundation complete | tenant context, RBAC baseline, audit/outbox, error safety, auth/session boundary and multi-tenant negative tests |
| BIM upload pilot | streaming upload, content validation/safe parser handling, immutable storage, job idempotency, retry/dead-letter visibility |
| External integrations | signed webhooks, outbox idempotency, connector isolation, external ID provenance, secret isolation |
| Production | OIDC/SAML as required, ABAC/RLS decision, KMS/secrets, rate limits, security headers, backup/DR, SAST/SCA/container/IaC checks |

## Testing Gates

| Test type | Gate policy |
|---|---|
| Unit | Required as each domain/rule/math service is implemented. |
| Integration | Required when DB, Redis, Object Storage or workers are in scope. |
| Contract | Required by FND-009 and for event/outbox and adapters. |
| E2E | Required for upload -> ingest -> viewer -> link -> Work Area vertical slices. |
| Golden regression | Required for BIM-017, BOQ-016, SCH-016 and PRG-012. |
| Performance | PR health smoke where available; nightly/release for heavier budgets. |
| Security | Threat checklist now; auth matrix and DAST/scans as surfaces appear. |
| Visual | Required by VWR-014 for Work Area and viewer regressions. |

Opaque snapshots must not be the only test for 4D/5D calculation logic.

## Fixture And Golden Policy

AUD-007 is the gate for test data:

- regression tests use cataloged fixtures from `fixtures/manifest.json`;
- no customer data, personal data or secrets in versioned fixtures;
- every fixture has source, provenance, license, size and SHA-256;
- golden outputs are deterministic and tied to `source_fixture_id`;
- failing tests do not silently rewrite goldens;
- SMALL/MEDIUM/LARGE datasets remain specified but unavailable until generated or licensed.

## Consolidated Findings

### P0

No open P0 blocks FND-001.

### P1

| ID | Severity | Source audit | Finding | Owner task | Deadline/gate | Status |
|---|---|---|---|---|---|---|
| F-AUD-001 | P1 | AUD-002 | SQL and orchestration remain concentrated in `services/api/app/main.py`. | FND-001 | R1 Foundation | OPEN |
| F-AUD-002 | P1 | AUD-002/AUD-006 | API depends directly on Redis instead of a queue port. | FND-007 | R1 Foundation | OPEN |
| F-AUD-003 | P1 | AUD-002/AUD-006/AUD-005 | Upload path uses a shared dev volume and non-streaming memory read. | FND-006 | R1 Foundation | OPEN |
| F-AUD-004 | P1 | AUD-004/AUD-006 | Audit/outbox helpers are free-form and event contracts can drift. | FND-005 | R1 Foundation | OPEN |
| F-AUD-005 | P1 | AUD-002/AUD-006 | BIM worker state machine and retry/idempotency are incomplete. | BIM-005 | R2 BIM Core | OPEN |
| F-AUD-006 | P1 | AUD-004 | Migration framework is absent. | FND-003 | R1 Foundation | OPEN |
| F-AUD-007 | P1 | AUD-004 | Same-project constraints for future write APIs depend on service/domain validation. | FND-016 | R1/R2 depending on API surface | OPEN |
| F-AUD-008 | P1 | AUD-004 | API money/quantity read models expose floats in demo paths. | BOQ-002 | R4 5D writes | OPEN |
| F-AUD-009 | P1 | AUD-006 | Real auth/RBAC is absent and harness uses default organization/user assumptions. | FND-001 | R1 Foundation | OPEN |
| F-AUD-010 | P1 | AUD-006 | Malicious IFC handling needs streaming, validation, sandbox/resource controls and retry policy. | BIM-002 | R2 BIM Core | OPEN |
| F-AUD-011 | P1 | AUD-005 | Upload and ingest performance baselines beyond TINY are not measured. | BIM-018 | R2/R6 certification | OPEN |
| F-AUD-012 | P1 | AUD-003/AUD-005 | Docker daemon and local smoke are blocked in the current Windows environment. | FND-015 | R1 bootstrap | OPEN |

### P2

| ID | Severity | Source audit | Finding | Owner task | Deadline/gate | Status |
|---|---|---|---|---|---|---|
| F-AUD-013 | P2 | AUD-002 | Domain and adapter packages are mostly README/stub boundaries. | FND-001 | Progressive by context | OPEN |
| F-AUD-014 | P2 | AUD-002 | Frontend contains demo cross-selection and API fallback data. | VWR-012 | R3 Work Area | OPEN |
| F-AUD-015 | P2 | AUD-004 | `activities.percent_complete` is a mutable projection. | PRG-001 | R5 Project Controls | OPEN |
| F-AUD-016 | P2 | AUD-004 | BOQ revisioning is simplified. | BOQ-001 | R4 5D | OPEN |
| F-AUD-017 | P2 | AUD-004 | Status vocabularies are incomplete for future workflows. | SCH-008 | R4 Scheduling and COL workflows | OPEN |
| F-AUD-018 | P2 | AUD-005/AUD-007 | SMALL/MEDIUM/LARGE datasets are specified but unavailable. | BIM-018 | R2/R6 certification | OPEN |
| F-AUD-019 | P2 | AUD-007 | No active progress or security fixture exists yet. | PRG-012 | R5 Project Controls | OPEN |
| F-AUD-020 | P2 | AUD-006 | Viewer XSS/CSP risks are future-facing until real viewer/property panels ship. | VWR-009 | R3 Work Area | OPEN |
| F-AUD-021 | P2 | AUD-003 | GNU Make is unavailable on the current Windows workstation. | FND-015 | R1 bootstrap | OPEN |
| F-AUD-022 | P2 | AUD-003 | npm dependency security debt requires policy, not force updates. | ENT-005 | R6/R7 hardening | OPEN |

### UNOWNED_GAP

None. Every P0/P1 has an owner task in `codex/tasks.yaml`.

## Technical Debt Policy

Debt can ship only when:

- severity is P2 or an accepted P1 outside the current release scope;
- owner task exists;
- deadline/gate is explicit;
- tests or manual checks guard the current safe behavior;
- user-facing or security impact is documented.

Debt cannot ship when:

- it is P0;
- it breaks a frozen invariant;
- it bypasses tenant/project authorization;
- it removes audit/outbox from critical writes;
- it makes heavy BIM synchronous in HTTP;
- it introduces unlicensed/customer/secret fixture data;
- it changes public API/schema/event contracts without versioning and tests.

P2 means consciously deferred, not ignored.

## Architectural Change Control

After AUD-008, significant changes require a new ADR or an update to an accepted ADR when
they affect:

- BIM identity;
- domain boundary;
- event contract;
- public API;
- revision strategy;
- storage abstraction;
- authorization architecture;
- viewer boundary;
- queue/job semantics;
- production deployment topology.

Trivial implementation details do not need ADRs.

## Known External Environment Blockers

These are environment blockers, not product P0s:

- Docker CLI is installed but Docker Desktop daemon is unavailable in the current Windows environment.
- Port 8000 has been observed occupied by a Windows service, causing local smoke timeout.
- GNU Make is unavailable on the current Windows workstation; `python scripts/dev.py ...` is canonical.

## Start Authorization For FND-001

When AUD-008 is DONE, committed, pushed, merged to `main`, and the FND-001 branch is prepared,
FND-001 is the next authorized implementation task.

FND-001 must remain TODO until its prompt is explicitly provided. Creating the branch does
not authorize implementation.
