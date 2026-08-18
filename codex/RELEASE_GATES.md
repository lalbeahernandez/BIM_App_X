# Release gates

## Gate 0 — Harness green
AUD-001..AUD-008 completadas. Local y CI reproducibles. NFRs, threat model y golden datasets definidos.

## Gate 1 — Foundation
FND-001..FND-016. Tenant isolation, RBAC, migrations, audit/outbox, object storage, jobs, OpenAPI y observabilidad operativos.

## Gate 2 — BIM vertical slice
BIM-001..BIM-017 + VWR-001..VWR-009. Upload IFC → object storage → async parse → element index → geometry artifact → viewer → click → property panel.

## Gate 3 — MVP 4D/5D
BOQ-001..BOQ-016 + SCH-001..SCH-016 + D4-001..D4-005. Viewer/BOQ/Gantt sincronizados, QTO/cost y CPM/baseline con simulación 4D.

## Gate 4 — Beta Project Controls
BIM-018, VWR-013/014, D4-006..008, PRG-001..012, COL-001..008. Planned vs actual, productividad, EVM, BCF/QA/IDS y benchmarks.

## Gate 5 — Advanced
ADV-001..ADV-008 según necesidad comercial: diff/lineage/clash/GIS/search/copilot read-only.

## Gate 6 — Enterprise pilot
ENT-001..ENT-016. SSO/security/DR/integrations/load certification/runbooks listos para piloto enterprise.
