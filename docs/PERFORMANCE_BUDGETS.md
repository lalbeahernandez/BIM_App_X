# Performance Budgets - AUD-005

Date: 2026-08-18

This document defines initial non-functional requirements, benchmark datasets,
measurement methodology and performance budgets for BIM Control X. The values are
engineering budgets for design, CI and release certification; they are not commercial SLAs.

`config/performance-budgets.json` is the machine-readable subset used by validation scripts.
This document is the human-readable specification and explains status, caveats and future
measurement work.

## 1. Purpose

Convert vague performance goals into measurable contracts:

```text
dataset class + operation + metric + target/limit + environment + measurement method
```

AUD-005 does not optimize the product. If a current component is unmeasured or below target,
the result is documented as `BASELINE NOT YET MEASURED`, `BLOCKED_EXTERNAL` or
`BASELINE BELOW TARGET`, not hidden by changing product behavior.

## 2. Measurement Philosophy

- Measure the production-shaped path, including tenant/project scoping and validation.
- Report `p50`, `p95`, `p99`, `max`, throughput, memory and artifact size where meaningful.
- Do not use averages as the only latency statistic.
- Record cold and warm state separately.
- Record benchmark metadata: git commit, dataset id/version/checksum, OS, CPU, RAM, Python,
  Node, Docker, PostgreSQL, Redis, browser, timestamp, iterations, warm/cold state and tool
  versions.
- Prefer short PR-gate tests for regressions and reserve heavy ingest/viewer/load tests for
  nightly or release certification.

## 3. Hardware Profiles

| Profile | CPU | RAM | Storage | Intended use | Status |
|---|---:|---:|---|---|---|
| DEV | 8 logical cores | 16 GB | SSD | Local smoke, tiny/small developer baselines | REQUIRED reference |
| CI | 4 vCPU | 8 GB | SSD ephemeral | PR gates and static validation | REQUIRED reference |
| PRODUCTION_REFERENCE | 8 vCPU | 32 GB | SSD/NVMe | Pilot release certification for API/worker | TARGET reference |
| VIEWER_REFERENCE | 4 performance cores + discrete or modern integrated GPU | 16 GB | SSD | Browser viewer certification | TARGET reference |

The hardware profiles are comparison baselines, not cloud vendor promises.

## 4. Dataset Classes

| Class | IFC size | IfcProducts | Storeys | Psets | Quantities | BOQ items | WBS nodes | Activities | Element-BOQ links | Element-Activity links | Progress records | Issues | Geometry | Derived artifacts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| TINY | <=1 MB | 1-100 | 1-2 | <=200 | <=200 | 1-20 | 1-10 | 1-20 | <=200 | <=200 | <=100 | <=20 | <=50k triangles | <=10 MB |
| SMALL | 10-75 MB | 5k-25k | 3-12 | 25k-150k | 10k-75k | 100-1k | 50-300 | 200-1k | 10k-75k | 10k-75k | 5k-50k | 100-1k | 0.5-5M triangles | <=250 MB |
| MEDIUM | 150-500 MB | 100k-500k | 10-60 | 0.5M-3M | 0.2M-1.5M | 2k-10k | 500-2k | 2k-10k | 0.2M-1.5M | 0.2M-1.5M | 0.1M-2M | 1k-10k | 5-30M triangles | <=2 GB |
| LARGE | 1-3 GB | 1M-3M | 30-150 | 5M-20M | 2M-10M | 20k-100k | 2k-10k | 10k-50k | 2M-10M | 2M-10M | 5M-50M | 10k-100k | 30-150M triangles federated | <=10 GB |

TINY is a developer fixture class. SMALL/MEDIUM/LARGE are benchmark specifications until
authorized datasets exist.

## 5. Dataset Availability And Provenance

| Dataset | Class | Source | License/Provenance | Deterministic | Available now | Intended use |
|---|---|---|---|---|---|---|
| `fixtures/ifc/tiny.ifc` | TINY | Repository-owned synthetic IFC | Owned harness fixture, no customer data | Yes | AVAILABLE | Harness ingest smoke and parser sanity |
| `fixtures/boq/demo_boq.csv` | TINY | Repository-owned synthetic BOQ | Owned demo data | Yes | AVAILABLE | Work Area demo and BOQ smoke |
| `fixtures/schedules/demo_schedule.csv` | TINY | Repository-owned synthetic schedule | Owned demo data | Yes | AVAILABLE | Work Area schedule smoke |
| `fixtures/bcf/sample.bcfzip` | TINY | Repository-owned minimal BCF zip | Owned harness fixture | Yes | AVAILABLE | BCF package integrity smoke |
| `benchmark-small-synthetic-v1` | SMALL | To be generated from deterministic synthetic model/data generator | Must record generator commit and checksum | Required | SPECIFIED_NOT_AVAILABLE | Nightly API/DB/worker baseline |
| `benchmark-medium-authorized-v1` | MEDIUM | Publicly licensed or internally generated benchmark model | License/provenance manifest required | Required | SPECIFIED_NOT_AVAILABLE | Release ingest/viewer/DB certification |
| `benchmark-large-authorized-v1` | LARGE | Publicly licensed, internally generated or customer-approved non-versioned private benchmark | No customer data in repo; external manifest/checksum only | Required | SPECIFIED_NOT_AVAILABLE | Enterprise load/stress certification |

No customer IFC, schedule, BOQ, credentials or evidence files may be committed as fixtures.

## 6. API Budgets

Latency budgets are measured at API boundary with tenant/project scoping enabled.

| Operation | Dataset | p50 target | p95 target | p99 limit | Classification | Measurement |
|---|---|---:|---:|---:|---|---|
| `GET /health` | TINY | 25 ms | 100 ms | 200 ms | REQUIRED PR | k6 `http_req_duration` |
| project list | TINY/SMALL | 50 ms | 200 ms | 400 ms | REQUIRED PR when API available | k6/API integration |
| model list | SMALL | 75 ms | 250 ms | 500 ms | TARGET | API benchmark |
| revision summary | SMALL | 100 ms | 300 ms | 700 ms | TARGET | API benchmark |
| element query paginated | SMALL | 150 ms | 500 ms | 1,000 ms | TARGET | DB-backed API benchmark |
| element query paginated | MEDIUM | 250 ms | 900 ms | 2,000 ms | TARGET, requires calibration | Release benchmark |
| element detail | SMALL/MEDIUM | 100 ms | 350 ms | 800 ms | TARGET | API benchmark |
| selection resolve <=1k input IDs | SMALL | 150 ms | 500 ms | 1,000 ms | TARGET | API benchmark |
| selection resolve <=10k linked rows | MEDIUM | 300 ms | 1,200 ms | 2,500 ms | TARGET, requires calibration | Release benchmark |
| BOQ tree/query | SMALL | 150 ms | 500 ms | 1,000 ms | TARGET | API benchmark |
| schedule query | SMALL | 150 ms | 600 ms | 1,200 ms | TARGET | API benchmark |
| progress query | MEDIUM | 250 ms | 1,000 ms | 2,500 ms | FUTURE TARGET | Release benchmark |
| issue list/filter | SMALL | 150 ms | 500 ms | 1,000 ms | FUTURE TARGET | API benchmark |

## 7. API Throughput And Concurrency

| Scenario | Dataset | Concurrency | Throughput target | Response size assumption | Classification |
|---|---|---:|---:|---|---|
| read-heavy lightweight API | TINY/SMALL | 50 users | 150 req/s | <=25 KB | TARGET |
| health/liveness | TINY | 100 users | 500 req/s | <=2 KB | TARGET |
| filtered element query | SMALL | 25 users | 50 req/s | <=250 KB/page | TARGET |
| selection resolution | SMALL | 25 users | 40 req/s | <=100 KB | TARGET |
| work-area dashboard read | SMALL | 25 users | 30 req/s | <=500 KB | TARGET |

These are engineering budgets, not contractual capacity claims for the current starter.

## 8. Response Size Budgets

| Response | Preferred limit | Hard warning | Required strategy above warning |
|---|---:|---:|---|
| element list page | <=250 KB | >1 MB | cursor pagination, filtering, field selection |
| element property detail | <=100 KB | >500 KB | property grouping/lazy loading |
| BOQ tree/page | <=500 KB | >2 MB | pagination, aggregation, server-side expand |
| Gantt rows/page | <=750 KB | >3 MB | virtualization, time windowing |
| cross-selection result | <=100 KB | >500 KB | cap input, pagination or async result |
| issue list/filter | <=300 KB | >1 MB | pagination and metadata-only evidence |

No API should return 100k full elements in one unpaginated JSON response.

## 9. Database Budgets

| Query | Dataset | p95 target | Expected index strategy | N+1 policy |
|---|---|---:|---|---|
| element lookup by `(revision_id, global_id)` | SMALL/MEDIUM | 50 ms | unique btree `(revision_id, global_id)` | Forbidden |
| element filter by revision/class | SMALL | 150 ms | `revision_id, ifc_class` index | Forbidden |
| element filter by revision/class | MEDIUM | 400 ms | partition/index review if exceeded | Forbidden |
| storey/spatial filter | MEDIUM | 600 ms | btree storey or spatial index when implemented | Forbidden |
| element to BOQ lookup | SMALL | 150 ms | link table PK/FK indexes | Forbidden |
| element to Activity lookup | SMALL | 150 ms | link table PK/FK indexes | Forbidden |
| BOQ aggregation | MEDIUM | 750 ms | project/revision grouping indexes | Forbidden |
| schedule query | MEDIUM | 750 ms | project/date/WBS indexes | Forbidden |
| progress history by date | MEDIUM | 1,000 ms | project/date index, future partitioning | Forbidden |
| issue query | MEDIUM | 600 ms | project/status/priority indexes | Forbidden |
| revision summary | MEDIUM | 500 ms | precomputed summary when needed | Forbidden |

No speculative index batch is added during AUD-005. Missing indexes become findings when
measured queries exceed these targets.

## 10. IFC Upload Budgets

HTTP upload acceptance is separate from full IFC ingestion. The request must create a
`ModelRevision`, calculate checksum, store the source artifact, write audit/outbox and enqueue
the worker job; it must not parse the full IFC synchronously.

| Dataset | File size | Upload accepted + queued p95 | p99 limit | Classification | Notes |
|---|---:|---:|---:|---|---|
| TINY | <=1 MB | 500 ms | 1 s | REQUIRED | Local/dev smoke |
| SMALL | 10-75 MB | 5 s | 10 s | TARGET | Requires streaming before production if exceeded |
| MEDIUM | 150-500 MB | 20 s | 45 s | TARGET, requires calibration | Object storage adapter expected |
| LARGE | 1-3 GB | 90 s | 180 s | ASPIRATIONAL, requires calibration | Chunked/streaming upload likely required |

Current harness caveat: `upload_revision` reads the whole file into memory. That is allowed
for the starter but a P1 performance/design gap before production uploads.

## 11. IFC Ingestion Budgets

| Dataset | Products/sec target | Total ingest duration target | DB rows/sec target | Failure budget | Classification |
|---|---:|---:|---:|---:|---|
| TINY | >=50 | <=30 s | >=50 | 0 unexpected failures | REQUIRED smoke |
| SMALL | >=500 | <=10 min | >=500 | <1% system failures | TARGET nightly |
| MEDIUM | >=1,000 | <=60 min | >=1,000 | <1% system failures | TARGET release |
| LARGE | >=1,500 | <=6 h | >=1,500 | <1% system failures | ASPIRATIONAL/stress |

Metrics to record: products/sec, total duration, peak RSS, DB rows/sec, property extraction
duration, QTO extraction duration, failure reason, retry count and artifact size.

## 12. Worker Memory Budgets

| Dataset | Peak RSS target | Regression warning | Regression blocker |
|---|---:|---:|---:|
| TINY | <=512 MB | >20% over baseline | >50% over baseline |
| SMALL | <=2 GB | >15% over baseline | >35% over baseline |
| MEDIUM | <=8 GB | >15% over baseline | >30% over baseline |
| LARGE | <=24 GB | >10% over baseline | >25% over baseline |

The worker must not require memory proportional to multiple complete copies of the original
model plus all derived artifacts. Streaming/chunking is future work, not AUD-005 work.

## 13. Geometry Pipeline Budgets

The production geometry pipeline is a future target.

| Dataset | Geometry extraction | Mesh conversion | Compression/artifact generation | Manifest generation | Artifact size target |
|---|---:|---:|---:|---:|---:|
| TINY | <=30 s | <=30 s | <=15 s | <=2 s | <=10 MB |
| SMALL | <=15 min | <=15 min | <=10 min | <=30 s | <=250 MB |
| MEDIUM | <=90 min | <=90 min | <=45 min | <=2 min | <=2 GB |
| LARGE | <=8 h | <=8 h | <=4 h | <=10 min | <=10 GB |

Record triangle count, peak memory and compression ratio. Do not require entire LARGE
federated geometry to load before interaction.

## 14. Viewer Budgets

| Dataset | First usable shell | First geometry | Current-view full load | Preferred FPS | Minimum FPS | Browser memory target | Selection latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| TINY | <=2 s | <=2 s | <=3 s | 60 | 30 | <=500 MB | <=100 ms |
| SMALL | <=3 s | <=5 s | <=15 s | 45 | 24 | <=1.5 GB | <=200 ms |
| MEDIUM | <=5 s | <=10 s | <=45 s | 30 | 20 | <=3 GB | <=500 ms |
| LARGE | <=8 s | <=20 s | progressive only | 24 | 15 | <=6 GB | <=1,000 ms |

Interaction targets cover orbit, pan, zoom, hide, isolate and clipping. Values depend on
browser/GPU/LOD/compression and require calibration by VWR-013/ENT-015.

## 15. Federation

| Scenario | Target |
|---|---|
| SMALL federation | 3-5 models, <=50k elements, <=10M visible triangles |
| MEDIUM federation | 5-10 models, <=500k elements, <=30M visible triangles |
| LARGE federation | 10-25 models, <=3M elements, progressive loading, <=150M total triangles |

Cross-model selection must remain based on `(revision_id, GlobalId)` and must not use mesh
indexes as persistent identity.

## 16. BOQ / 5D Budgets

| Operation | Dataset | Target |
|---|---|---:|
| BOQ initial tree/page | SMALL <=1k items | p95 <=500 ms API, <=1 s UI render |
| expand/collapse | MEDIUM <=10k items | interaction <=150 ms with virtualization |
| filtered BOQ query | MEDIUM | p95 <=750 ms |
| element to BOQ traceability | SMALL/MEDIUM | p95 <=500 ms |
| rollup amount calculation | MEDIUM | p95 <=1,000 ms or async/materialized |

Money remains decimal in persistence. Read-model floats in the current demo are not allowed
for future financial write contracts.

## 17. Schedule / Gantt Budgets

| Operation | Size | Target |
|---|---:|---:|
| activity query | 1k activities | p95 <=500 ms |
| activity query | 10k activities | p95 <=1,500 ms with paging/windowing |
| Gantt initial render | 1k visible rows | <=2 s |
| Gantt scrolling | 10k+ rows | >=30 FPS with virtualization |
| filtering | 10k activities | <=500 ms client perceived after data loaded |
| critical path view | 10k activities | FUTURE TARGET, <=5 s or async |
| timeline zoom | 10k activities | interaction <=200 ms |

CPM is not implemented in AUD-005.

## 18. 4D Budgets

| Operation | Size | Target |
|---|---:|---:|
| timeline step computation | <=100k linked elements | <=500 ms |
| timeline step computation | <=1M linked elements | <=2 s or async/precomputed |
| viewer state update | <=25k changed elements | <=250 ms |
| planned-vs-actual update | MEDIUM progress set | p95 <=1,000 ms |

The target strategy must update changed element sets, not redraw/reprocess the full model at
each time step.

## 19. Progress / EVM Budgets

| Operation | Dataset | Target |
|---|---|---:|
| progress query by date/activity | MEDIUM | p95 <=1,000 ms |
| daily snapshot generation | MEDIUM | <=5 min batch |
| PV/EV/AC aggregation | MEDIUM | p95 <=2 s or async |
| S-curve generation | MEDIUM | p95 <=2 s with cached series |
| forecast calculation | MEDIUM | p95 <=3 s or async |

EVM calculations are not implemented in AUD-005.

## 20. QA / BCF Budgets

| Operation | Dataset | Target |
|---|---|---:|
| issue list/filter | SMALL | p95 <=500 ms |
| issue list/filter | MEDIUM | p95 <=1,000 ms |
| viewpoint metadata retrieval | SMALL/MEDIUM | p95 <=500 ms |
| BCF import | 1k issues | <=5 min async job |
| inspection queries | MEDIUM | p95 <=1,000 ms |
| evidence metadata retrieval | MEDIUM | p95 <=750 ms |

Binary evidence should not be embedded in metadata list responses.

## 21. Search Future Target

| Metric | Target |
|---|---:|
| query latency for indexed element/document search | p95 <=500 ms SMALL, <=1,000 ms MEDIUM |
| index freshness | <=5 min for normal updates; <=30 min for bulk ingest |
| indexed scope | tenant/project filtered, rebuildable from system of record |

Search is a future adapter target and must not bypass tenant authorization.

## 22. Multi-Tenancy And Security Overhead

Tenant authorization, project scoping, validation and safe parsing are part of the measured
production path. They must not be disabled to meet latency targets. Benchmarks that bypass
authorization may be useful microbenchmarks, but they cannot justify removing server-side
checks.

## 23. Background Jobs

| Job class | Queue delay target | Execution target | Retry/idempotency expectation |
|---|---:|---:|---|
| IFC ingest | p95 <=30 s | dataset-specific ingest budgets | retry must not duplicate elements |
| geometry generation | p95 <=60 s | dataset-specific geometry budgets | retry must replace only failed artifact attempt |
| IDS validation | p95 <=60 s | <=30 min MEDIUM target | retry must not duplicate findings |
| mapping/import jobs | p95 <=60 s | task-specific | retry must not duplicate links |

Dead jobs must be visible with reason, attempts, timestamps and correlation id.

## 24. Reliability NFR

- A retry must not duplicate elements, relationships, progress records or event deliveries.
- A retry must not overwrite the wrong historical revision.
- Partial failure must leave the revision/job in an observable failed state.
- Jobs must have correlation identifiers.
- Ingest failures must preserve safe error messages and not leak file contents.
- Historical records must not be recalculated silently without provenance/version.

## 25. Availability / SLO And Error Budgets

| Stage | Monthly availability target | Successful request target | System error budget | Notes |
|---|---:|---:|---:|---|
| Development | 95.0% during active dev hours | 98.0% | 2.0% | Local/dev only |
| Pilot | 99.0% | 99.5% | 0.5% | Requires FND/observability hardening |
| Production target | 99.5% | 99.9% | 0.1% | Engineering target, not SLA |

4xx validation errors are expected user/client outcomes and do not count as system 5xx error
budget unless they indicate a server bug.

## 26. Error Rate Budgets

| Area | Target |
|---|---:|
| HTTP 5xx | <=0.5% pilot, <=0.1% production target |
| job unexpected failures | <=1% by job class; retry success tracked separately |
| IFC ingest parser/data failures | reported separately from system failures |
| frontend runtime errors | <=0.1% of sessions for production target |
| failed benchmark iterations | 0 for PR gate; <=1% for noisy long-running release runs with rerun |

## 27. Observability Requirements

Future FND-012 instrumentation must expose:

- request duration, request count and response status;
- DB query timing and query class;
- queue depth and enqueue-to-start delay;
- job duration, job attempts and job failure reason;
- ingest products/sec and rows/sec;
- worker peak RSS memory;
- artifact sizes and compression ratio;
- frontend Web Vitals and Work Area/viewer custom timings;
- browser memory and FPS where supported by benchmark tooling.

## 28. Logging Constraints

- Do not log complete IFC/BCF files or large payloads.
- Do not log secrets, credentials or private customer data.
- Logs must be structured and include correlation id when implemented.
- Log rate must be controlled for per-element loops; aggregate counters are preferred.
- Failure logs should include safe stage/code/message, not raw binary content.

## 29. Storage NFR

| Artifact | Immutability | Checksum | Retention category | Size budget |
|---|---|---|---|---:|
| original IFC | immutable per revision | SHA-256 required | model source | dataset file size |
| derived geometry | immutable per generation/version | checksum required | derived artifact | dataset artifact budget |
| BCF/evidence | immutable object, mutable metadata workflow | checksum required | collaboration/evidence | metadata separate from binary |
| reports/exports | immutable generated output | checksum recommended | reporting/export | task-specific |

Lifecycle policies are future work and must respect legal hold/approved baselines.

## 30. Network Assumptions

| Profile | Latency | Bandwidth | Use |
|---|---:|---:|---|
| LOCAL/LAN | <=10 ms | >=500 Mbps | developer and lab measurements |
| FAST_BROADBAND | 20-80 ms | 50-200 Mbps | pilot office users |
| CONSTRAINED | 100-200 ms | 10-25 Mbps | field/constrained validation |

Viewer measurements must separate server processing, network transfer, browser parse and
render time.

## 31. Frontend Web Vitals

| Surface | LCP | INP | CLS | Custom timings |
|---|---:|---:|---:|---|
| normal app pages | <=2.5 s | <=200 ms | <=0.1 | route ready |
| Work Area shell | <=3 s | <=250 ms | <=0.1 | shell interactive <=3 s |
| BIM Work Area | N/A for full model | <=300 ms outside heavy viewer actions | <=0.1 | viewer usable/model usable per dataset budgets |

Work Area BIM is not judged like a static landing page; viewer and model milestones are
measured separately.

## 32. Concurrency Scenarios

| Scenario | Users | Purpose |
|---|---:|---|
| single user | 1 | functional smoke and profiling |
| team | 10 | interactive collaboration target |
| project office | 50 | read-heavy pilot target |
| enterprise burst | 100 | release/stress target |

Measure health, project/model reads, work-area reads, filtered queries, selection resolution
and background queue behavior under concurrency.

## 33. Large Project Target

A LARGE BIM Control X project means more than a large IFC:

- 10-25 federated models;
- 50-150 model revisions retained;
- 1M-3M current elements;
- 20k-100k BOQ items;
- 10k-50k activities;
- 2M-10M element-to-BOQ and element-to-Activity links;
- 5M-50M progress records;
- 10k-100k issues/QA records;
- 1-3 GB source IFC per major model and up to 10 GB derived artifacts per project snapshot.

## 34. Scale Ceiling Vs Target

| Category | Meaning | Current value |
|---|---|---|
| SUPPORTED TARGET | Size the architecture should support after planned MVP/Beta work | TINY/SMALL in PR/nightly, MEDIUM in release certification |
| STRESS TARGET | Used to expose limits; not required in every PR | LARGE |
| HARD LIMIT | Certified upper bound with failure behavior | TBD through ENT-015 |

## 35. Benchmark Procedure

1. Record metadata listed in section 2.
2. Verify clean git status or record local changes.
3. Confirm dataset checksum and class.
4. Run cold benchmark once when relevant.
5. Run warm benchmark for at least 5 iterations for short tests or 3 iterations for expensive
   ingest/viewer tests.
6. Report p50/p95/p99/max and throughput.
7. Record peak memory, artifact size and failure count.
8. Compare against budgets and previous comparable baseline.
9. Store results as CI artifacts or release certification records, not as hand-edited claims.

## 36. Regression Policy

| Area | Noise | Warning | Blocker |
|---|---:|---:|---:|
| API latency p95 | <10% | 10-25% reproducible | >25% reproducible or exceeds p99 limit |
| throughput | <10% loss | 10-20% loss | >20% loss on same dataset/profile |
| worker memory | dataset-specific table | dataset-specific warning | dataset-specific blocker |
| artifact size | <10% | 10-25% growth | >25% growth without quality/feature justification |
| viewer FPS/interactions | <10% | 10-20% regression | below minimum FPS or interaction-latency target |

Regressions must compare the same dataset, hardware profile, warm/cold state and commit range.

## 37. Performance Gates And CI Tiers

| Tier | Benchmarks | Purpose |
|---|---|---|
| PR GATE | static budget config validation, unit tests, lint/typecheck, health k6 only when API is available | short regression guard |
| NIGHTLY | SMALL API/DB query suite, SMALL ingest, Work Area frontend timings | trend detection |
| RELEASE CERTIFICATION | MEDIUM/LARGE ingest, geometry, viewer FPS/memory, load/soak, federation, 4D/progress/QA suites | go/no-go evidence |

Do not run 30-minute or multi-hour benchmarks in normal PR CI.

## 38. Current Baseline Vs Future Targets

| Area | Current status | Notes |
|---|---|---|
| API health/unit tests | MEASURED by tests, not latency benchmark | k6 requires API runtime |
| k6 health smoke | BLOCKED_EXTERNAL if API unavailable or k6 missing | Harness exists and is parametrized |
| Docker compose config | MEASURABLE without daemon | Validates stack shape only |
| IFC ingest TINY | BLOCKED_EXTERNAL in current environment when Docker/DB/Redis unavailable | Worker exists; runtime baseline pending |
| Geometry/viewer | FUTURE_TARGET | Viewer is placeholder; no production geometry pipeline |
| MEDIUM/LARGE datasets | MEASUREMENT_GAP | Specification exists; datasets not versioned yet |
| DB query budgets | FUTURE_TARGET | Require seeded DB and query benchmark harness |

## 39. Known Measurement Gaps

| Gap | Classification | Future task |
|---|---|---|
| Docker daemon unavailable in current Windows environment | MEASUREMENT_GAP / BLOCKED_EXTERNAL | Environment setup |
| k6 may be unavailable locally | MEASUREMENT_GAP / UNAVAILABLE | Install in developer/CI image later |
| No SMALL/MEDIUM/LARGE benchmark datasets versioned | MEASUREMENT_GAP | AUD-007, BIM-018, ENT-015 |
| No production viewer or geometry artifacts | FUTURE_TARGET | VWR-001..VWR-013 |
| No DB query benchmark harness | FUTURE_TARGET | FND-014 / domain slices |
| No observability metrics emitted yet | FUTURE_TARGET | FND-012 |

No P0 performance-specification gap remains after AUD-005.
