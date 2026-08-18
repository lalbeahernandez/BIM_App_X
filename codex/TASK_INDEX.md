# Índice de tareas Codex

Este pack contiene **140 tareas** ordenadas por dependencia para convertir el harness en un producto BIM 4D/5D enterprise.

La columna **Target** indica el primer release en el que conviene exigir la tarea. No significa que todas las tareas del mismo target deban ejecutarse en paralelo.

## 0 Discovery & Baseline

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [AUD-001](tasks/AUD-001.md) | MUST | MVP | Auditar y poner verde el harness | — |
| [AUD-002](tasks/AUD-002.md) | MUST | MVP | Inventariar boundaries y ownership | AUD-001 |
| [AUD-003](tasks/AUD-003.md) | MUST | MVP | Fijar toolchain y dependencias | AUD-001 |
| [AUD-004](tasks/AUD-004.md) | MUST | MVP | Reconciliar schema SQL y modelo de dominio | AUD-002 |
| [AUD-005](tasks/AUD-005.md) | MUST | MVP | Definir NFR y presupuestos de rendimiento | AUD-001 |
| [AUD-006](tasks/AUD-006.md) | MUST | MVP | Threat model inicial | AUD-002 |
| [AUD-007](tasks/AUD-007.md) | MUST | MVP | Catálogo de fixtures y golden datasets | AUD-001 |
| [AUD-008](tasks/AUD-008.md) | MUST | MVP | Congelar roadmap técnico v1 | AUD-003, AUD-004, AUD-005, AUD-006, AUD-007 |

## 1 Foundation

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [FND-001](tasks/FND-001.md) | MUST | MVP | Propagar tenant context | AUD-008 |
| [FND-002](tasks/FND-002.md) | MUST | MVP | RBAC mínimo | FND-001 |
| [FND-003](tasks/FND-003.md) | MUST | MVP | Framework de migrations | AUD-004 |
| [FND-004](tasks/FND-004.md) | MUST | MVP | Auditoría transaccional | FND-001, FND-003 |
| [FND-005](tasks/FND-005.md) | MUST | MVP | Transactional outbox | FND-003, FND-004 |
| [FND-006](tasks/FND-006.md) | MUST | MVP | ObjectStorage adapter | FND-003 |
| [FND-007](tasks/FND-007.md) | MUST | MVP | Job queue abstraction | FND-005 |
| [FND-008](tasks/FND-008.md) | MUST | MVP | Error envelope y correlation IDs | FND-001 |
| [FND-009](tasks/FND-009.md) | MUST | MVP | OpenAPI como contrato verificado | FND-008 |
| [FND-010](tasks/FND-010.md) | MUST | MVP | Session/auth boundary frontend | FND-001, FND-002 |
| [FND-011](tasks/FND-011.md) | SHOULD | MVP | Feature flags | FND-001 |
| [FND-012](tasks/FND-012.md) | MUST | MVP | Observabilidad baseline | FND-008 |
| [FND-013](tasks/FND-013.md) | MUST | MVP | Health/readiness/dependency checks | FND-006, FND-007, FND-012 |
| [FND-014](tasks/FND-014.md) | MUST | MVP | CI quality gates | AUD-003, FND-003, FND-009 |
| [FND-015](tasks/FND-015.md) | MUST | MVP | Bootstrap reproducible de desarrollo | FND-003, FND-006, FND-007, FND-013 |
| [FND-016](tasks/FND-016.md) | MUST | MVP | Suite de aislamiento multi-tenant | FND-001, FND-002, FND-014 |

## 2 BIM Ingestion

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [BIM-001](tasks/BIM-001.md) | MUST | MVP | Dominio Model y ModelRevision | FND-003, FND-004 |
| [BIM-002](tasks/BIM-002.md) | MUST | MVP | Upload IFC streaming | BIM-001, FND-006, FND-008 |
| [BIM-003](tasks/BIM-003.md) | MUST | MVP | Checksum y almacenamiento inmutable | BIM-002 |
| [BIM-004](tasks/BIM-004.md) | MUST | MVP | Encolar ingest request | BIM-003, FND-005, FND-007 |
| [BIM-005](tasks/BIM-005.md) | MUST | MVP | State machine idempotente del worker | BIM-004 |
| [BIM-006](tasks/BIM-006.md) | MUST | MVP | Detección IFC schema | BIM-005 |
| [BIM-007](tasks/BIM-007.md) | MUST | MVP | Índice básico de IfcProduct | BIM-006 |
| [BIM-008](tasks/BIM-008.md) | MUST | MVP | Jerarquía espacial y storeys | BIM-007 |
| [BIM-009](tasks/BIM-009.md) | MUST | MVP | Property sets normalizados | BIM-007 |
| [BIM-010](tasks/BIM-010.md) | MUST | MVP | Base quantities y QTO IFC | BIM-007 |
| [BIM-011](tasks/BIM-011.md) | SHOULD | MVP | Clasificaciones IFC | BIM-007 |
| [BIM-012](tasks/BIM-012.md) | MUST | MVP | Normalización de unidades | BIM-006, BIM-010 |
| [BIM-013](tasks/BIM-013.md) | SHOULD | MVP | Metadata geométrica | BIM-007 |
| [BIM-014](tasks/BIM-014.md) | MUST | MVP | Errores y retry de ingestión | BIM-005, BIM-006 |
| [BIM-015](tasks/BIM-015.md) | MUST | MVP | Element query API | BIM-008, BIM-009, BIM-010, BIM-011, FND-009 |
| [BIM-016](tasks/BIM-016.md) | SHOULD | MVP | Revision summary y métricas | BIM-014, BIM-015 |
| [BIM-017](tasks/BIM-017.md) | MUST | MVP | Golden IFC regression suite | BIM-012, BIM-015, AUD-007 |
| [BIM-018](tasks/BIM-018.md) | SHOULD | Beta | Benchmark de ingestión grande | BIM-017, AUD-005 |

## 3 Viewer & Work Area

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [VWR-001](tasks/VWR-001.md) | MUST | MVP | Benchmark y ADR de viewer | BIM-017, AUD-005 |
| [VWR-002](tasks/VWR-002.md) | MUST | MVP | Implementar ViewerAdapter de producción | VWR-001 |
| [VWR-003](tasks/VWR-003.md) | MUST | MVP | Contrato de geometry artifacts | VWR-001, BIM-013 |
| [VWR-004](tasks/VWR-004.md) | MUST | MVP | Pipeline worker de geometría | VWR-003, FND-006, FND-007 |
| [VWR-005](tasks/VWR-005.md) | MUST | MVP | Artifact manifest API | VWR-004, FND-009 |
| [VWR-006](tasks/VWR-006.md) | MUST | MVP | Carga de un modelo real | VWR-002, VWR-005 |
| [VWR-007](tasks/VWR-007.md) | MUST | MVP | Selección con identidad BIM estable | VWR-006, BIM-015 |
| [VWR-008](tasks/VWR-008.md) | MUST | MVP | Hide/isolate/show | VWR-007 |
| [VWR-009](tasks/VWR-009.md) | MUST | MVP | Property panel BIM | VWR-007, BIM-009, BIM-010, BIM-011 |
| [VWR-010](tasks/VWR-010.md) | SHOULD | MVP | Clipping y measurement tools | VWR-006, BIM-012 |
| [VWR-011](tasks/VWR-011.md) | MUST | MVP | Federación multi-modelo | VWR-007 |
| [VWR-012](tasks/VWR-012.md) | MUST | MVP | Cross-selection Viewer↔BOQ↔Gantt | VWR-007, VWR-011 |
| [VWR-013](tasks/VWR-013.md) | SHOULD | Beta | Progressive loading/performance | VWR-011, BIM-018 |
| [VWR-014](tasks/VWR-014.md) | MUST | MVP | Visual regression y E2E del Work Area | VWR-012, VWR-013 |

## 4 BOQ / QTO / 5D

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [BOQ-001](tasks/BOQ-001.md) | MUST | MVP | BOQ hierarchy y revisions | BIM-015, FND-003 |
| [BOQ-002](tasks/BOQ-002.md) | MUST | MVP | CRUD de BOQ items | BOQ-001, FND-009 |
| [BOQ-003](tasks/BOQ-003.md) | MUST | MVP | Links manuales elemento↔BOQ | BOQ-002, BIM-015 |
| [BOQ-004](tasks/BOQ-004.md) | MUST | MVP | DSL/modelo de mapping rules | BOQ-003 |
| [BOQ-005](tasks/BOQ-005.md) | MUST | MVP | Ejecución asíncrona de mapping rules | BOQ-004, FND-007 |
| [BOQ-006](tasks/BOQ-006.md) | MUST | MVP | Modelo de quantity rules | BOQ-002, BIM-010 |
| [BOQ-007](tasks/BOQ-007.md) | MUST | MVP | Motor QTO reproducible | BOQ-005, BOQ-006, BIM-012 |
| [BOQ-008](tasks/BOQ-008.md) | MUST | MVP | Conversiones de unidad 5D | BOQ-007 |
| [BOQ-009](tasks/BOQ-009.md) | SHOULD | MVP | Cantidades importadas y override | BOQ-007 |
| [BOQ-010](tasks/BOQ-010.md) | MUST | MVP | Rate catalogs | BOQ-002 |
| [BOQ-011](tasks/BOQ-011.md) | MUST | MVP | Cost revisions y budgets | BOQ-001, BOQ-010 |
| [BOQ-012](tasks/BOQ-012.md) | MUST | MVP | Cálculo de importes y rollups | BOQ-008, BOQ-010, BOQ-011 |
| [BOQ-013](tasks/BOQ-013.md) | MUST | MVP | API de trazabilidad 5D | BOQ-003, BOQ-012 |
| [BOQ-014](tasks/BOQ-014.md) | SHOULD | Beta | Import/export CSV/XLSX | BOQ-002, BOQ-010 |
| [BOQ-015](tasks/BOQ-015.md) | MUST | MVP | UI BOQ tree/editor | BOQ-013, VWR-012 |
| [BOQ-016](tasks/BOQ-016.md) | MUST | MVP | Golden suite 5D | BOQ-015, AUD-007 |

## 5 Scheduling

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [SCH-001](tasks/SCH-001.md) | MUST | MVP | WBS hierarchy | FND-003, FND-001 |
| [SCH-002](tasks/SCH-002.md) | MUST | MVP | Activity CRUD | SCH-001, FND-009 |
| [SCH-003](tasks/SCH-003.md) | MUST | MVP | Calendars y working time | SCH-002 |
| [SCH-004](tasks/SCH-004.md) | MUST | MVP | Activity relationships | SCH-002 |
| [SCH-005](tasks/SCH-005.md) | MUST | MVP | CPM forward pass | SCH-003, SCH-004 |
| [SCH-006](tasks/SCH-006.md) | MUST | MVP | CPM backward pass y float | SCH-005 |
| [SCH-007](tasks/SCH-007.md) | MUST | MVP | Constraints y milestones | SCH-006 |
| [SCH-008](tasks/SCH-008.md) | MUST | MVP | Data date y status semantics | SCH-007 |
| [SCH-009](tasks/SCH-009.md) | SHOULD | MVP | Import schedule CSV | SCH-004 |
| [SCH-010](tasks/SCH-010.md) | COULD | Beta | MS Project adapter contract | SCH-009 |
| [SCH-011](tasks/SCH-011.md) | SHOULD | Beta | Primavera P6 adapter contract | SCH-009 |
| [SCH-012](tasks/SCH-012.md) | MUST | MVP | Schedule baselines | SCH-008 |
| [SCH-013](tasks/SCH-013.md) | SHOULD | Beta | What-if scenarios | SCH-012 |
| [SCH-014](tasks/SCH-014.md) | MUST | MVP | Schedule query/Gantt API | SCH-006, SCH-008, SCH-012 |
| [SCH-015](tasks/SCH-015.md) | MUST | MVP | Gantt UI real | SCH-014, VWR-012 |
| [SCH-016](tasks/SCH-016.md) | MUST | MVP | Golden CPM suite | SCH-015, AUD-007 |

## 6 4D Simulation

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [D4-001](tasks/D4-001.md) | MUST | MVP | Links elemento↔actividad | BIM-015, SCH-002, VWR-012 |
| [D4-002](tasks/D4-002.md) | MUST | MVP | Motor de estados 4D | D4-001, SCH-008 |
| [D4-003](tasks/D4-003.md) | MUST | MVP | Timeline controls | D4-002, SCH-015 |
| [D4-004](tasks/D4-004.md) | MUST | MVP | Color/status legend | D4-002, VWR-008 |
| [D4-005](tasks/D4-005.md) | SHOULD | MVP | Incremental 4D updates | D4-003, D4-004 |
| [D4-006](tasks/D4-006.md) | SHOULD | Beta | 4D federado | D4-001, VWR-011, D4-005 |
| [D4-007](tasks/D4-007.md) | SHOULD | Beta | Planned vs actual visual | D4-002, SCH-008 |
| [D4-008](tasks/D4-008.md) | MUST | Beta | 4D E2E y performance gate | D4-006, D4-007 |

## 7 Progress / Productivity / EVM

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [PRG-001](tasks/PRG-001.md) | SHOULD | Beta | ProgressRecord append-only | BOQ-016, SCH-012, FND-004 |
| [PRG-002](tasks/PRG-002.md) | SHOULD | Beta | API de captura de progreso | PRG-001, FND-009 |
| [PRG-003](tasks/PRG-003.md) | SHOULD | Beta | Physical progress por cantidad | PRG-002, BOQ-007, D4-001 |
| [PRG-004](tasks/PRG-004.md) | SHOULD | Beta | Resources y crews | SCH-002 |
| [PRG-005](tasks/PRG-005.md) | SHOULD | Beta | Productivity rates | PRG-004, BOQ-008 |
| [PRG-006](tasks/PRG-006.md) | SHOULD | Beta | Forecast de duración por productividad | PRG-003, PRG-005, SCH-003 |
| [PRG-007](tasks/PRG-007.md) | SHOULD | Beta | Planned Value timephasing | BOQ-011, SCH-012, D4-001 |
| [PRG-008](tasks/PRG-008.md) | SHOULD | Beta | Earned Value | PRG-003, PRG-007 |
| [PRG-009](tasks/PRG-009.md) | SHOULD | Beta | Actual cost/commitments interface | BOQ-011, FND-005 |
| [PRG-010](tasks/PRG-010.md) | SHOULD | Beta | EVM KPIs y forecast | PRG-008, PRG-009 |
| [PRG-011](tasks/PRG-011.md) | SHOULD | Beta | S-curves y dashboard project controls | PRG-010 |
| [PRG-012](tasks/PRG-012.md) | SHOULD | Beta | Golden suite progreso/EVM | PRG-011, AUD-007 |

## 8 Collaboration / QA / IDS

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [COL-001](tasks/COL-001.md) | SHOULD | Beta | Issues y comments | VWR-014, FND-004 |
| [COL-002](tasks/COL-002.md) | SHOULD | Beta | Viewpoints y component selection | COL-001, VWR-007, FND-006 |
| [COL-003](tasks/COL-003.md) | SHOULD | Beta | BCF import/export | COL-002 |
| [COL-004](tasks/COL-004.md) | SHOULD | Beta | QA/QC inspections y checklists | COL-001 |
| [COL-005](tasks/COL-005.md) | SHOULD | Beta | NCR y punch workflows | COL-004 |
| [COL-006](tasks/COL-006.md) | SHOULD | Beta | Evidence attachments | COL-004, FND-006 |
| [COL-007](tasks/COL-007.md) | SHOULD | Beta | IDS validation jobs | BIM-017, FND-007 |
| [COL-008](tasks/COL-008.md) | SHOULD | Beta | Notifications y workflow events | COL-001, COL-005, FND-005 |

## 9 Advanced BIM Intelligence

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [ADV-001](tasks/ADV-001.md) | COULD | Post-Beta | Revision diff por identidad y propiedades | BIM-017 |
| [ADV-002](tasks/ADV-002.md) | COULD | Post-Beta | Lineage candidate matching | ADV-001, BIM-013 |
| [ADV-003](tasks/ADV-003.md) | COULD | Post-Beta | Manual lineage remap | ADV-002, FND-004 |
| [ADV-004](tasks/ADV-004.md) | COULD | Post-Beta | Clash engine adapter/orchestration | VWR-011, FND-007 |
| [ADV-005](tasks/ADV-005.md) | COULD | Post-Beta | CRS y georreferenciación | BIM-008 |
| [ADV-006](tasks/ADV-006.md) | COULD | Post-Beta | Parcel/setback analysis | ADV-005 |
| [ADV-007](tasks/ADV-007.md) | COULD | Post-Beta | Search indexing | BIM-015, FND-005 |
| [ADV-008](tasks/ADV-008.md) | COULD | Post-Beta | AI copilot read-only y grounded | BOQ-016, SCH-016, PRG-012, COL-007 |

## 10 Enterprise Hardening

| ID | Pri | Target | Tarea | Depende de |
|---|---|---|---|---|
| [ENT-001](tasks/ENT-001.md) | MUST | Enterprise | OIDC SSO | FND-010, FND-002 |
| [ENT-002](tasks/ENT-002.md) | SHOULD | Enterprise | SAML enterprise adapter | ENT-001 |
| [ENT-003](tasks/ENT-003.md) | SHOULD | Enterprise | ABAC y permisos por proyecto | ENT-001, FND-016 |
| [ENT-004](tasks/ENT-004.md) | COULD | Enterprise | PostgreSQL RLS defence-in-depth | ENT-003 |
| [ENT-005](tasks/ENT-005.md) | MUST | Enterprise | Secrets y encryption/KMS | ENT-001, FND-006 |
| [ENT-006](tasks/ENT-006.md) | MUST | Enterprise | Rate limiting y security headers | ENT-001, AUD-006 |
| [ENT-007](tasks/ENT-007.md) | MUST | Enterprise | Backups, restore y DR | FND-006, FND-003 |
| [ENT-008](tasks/ENT-008.md) | SHOULD | Enterprise | HA y escalado de workers | BIM-018, D4-008 |
| [ENT-009](tasks/ENT-009.md) | SHOULD | Enterprise | Retention y lifecycle de artifacts | FND-006, COL-006 |
| [ENT-010](tasks/ENT-010.md) | SHOULD | Enterprise | Webhooks firmados | FND-005, FND-009 |
| [ENT-011](tasks/ENT-011.md) | SHOULD | Enterprise | Integration framework | ENT-010 |
| [ENT-012](tasks/ENT-012.md) | COULD | Enterprise | Autodesk/ACC adapter | ENT-011 |
| [ENT-013](tasks/ENT-013.md) | SHOULD | Enterprise | ERP cost connector | ENT-011, PRG-009 |
| [ENT-014](tasks/ENT-014.md) | SHOULD | Enterprise | Compliance export y audit search | FND-004, COL-005, ENT-009 |
| [ENT-015](tasks/ENT-015.md) | MUST | Enterprise | Load/soak/performance certification | ENT-008, PRG-011, VWR-013 |
| [ENT-016](tasks/ENT-016.md) | MUST | Enterprise | Production readiness y piloto | ENT-005, ENT-006, ENT-007, ENT-015 |
