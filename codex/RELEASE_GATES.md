# Release gates

Roadmap V1 detail lives in `docs/TECHNICAL_ROADMAP_V1.md`. This file is the compact
release-gate index; do not duplicate the full roadmap here.

## Gate 0 - Harness green

AUD-001..AUD-008 completed. Architecture V1, frozen invariants, NFRs, threat model,
fixtures/golden datasets, critical path and debt policy are defined. `codex/tasks.yaml`
remains the canonical 140-task graph.

## Gate 1 - Foundation

FND-001..FND-016. Tenant isolation, RBAC, migrations, audit/outbox, object storage,
jobs, OpenAPI, observability, readiness, CI, bootstrap and multi-tenant negative tests
are operational.

## Gate 2 - BIM vertical slice

BIM-001..BIM-017 + VWR-001..VWR-009. Upload IFC -> object storage -> async parse ->
element index -> geometry artifact -> viewer -> click -> property panel. HTTP upload
acceptance is not complete IFC processing.

## Gate 3 - MVP 4D/5D

BOQ-001..BOQ-016 + SCH-001..SCH-016 + D4-001..D4-005. Viewer/BOQ/Gantt synchronized,
QTO/cost provenance, CPM/baseline and usable 4D simulation.

## Gate 4 - Beta Project Controls

BIM-018, VWR-013/014, D4-006..008, PRG-001..012, COL-001..008. Planned vs actual,
productivity, EVM, BCF/QA/IDS and benchmarks with cataloged fixtures/goldens.

## Gate 5 - Advanced

ADV-001..ADV-008 as commercially needed: diff, lineage, clash, GIS, search and read-only
grounded copilot. AI is not a structural dependency of core workflows.

## Gate 6 - Enterprise pilot

ENT-001..ENT-016. SSO, security, DR, integrations, load certification and runbooks ready
for enterprise pilot, with Pilot Ready distinguished from Full Enterprise Complete in
`docs/TECHNICAL_ROADMAP_V1.md`.
