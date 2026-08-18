# Project plan

Baseline de referencia: ~36 semanas hasta piloto avanzado; ajustar tras discovery y benchmark.

| Fase | Semanas | Resultado |
|---|---:|---|
| 0 Discovery/benchmarks | 1-3 | PRD, datasets, viewer benchmark, NFRs |
| 1 Foundation | 4-7 | tenancy, schema, API, audit/outbox, CI/CD |
| 2 BIM ingest/viewer | 8-13 | IFC revisions, index, artifacts, federated viewer |
| 3 BOQ/5D core | 14-18 | QTO, mapping rules, BOQ revisions/costs |
| 4 Scheduling/4D | 19-24 | CPM, baselines, Gantt, 4D simulation |
| 5 Progress/EVM | 25-28 | field progress, productivity, S-curves/EVM |
| 6 Collaboration/QA | 29-32 | BCF/issues, inspections, IDS |
| 7 Pilot/enterprise hardening | 33-36 | SSO, observability, perf, DR, integrations |

## Team baseline

1 Product/Domain lead, 1 UX, 2 frontend, 3 backend/platform, 2 BIM/geometry engineers, 1 QA automation, 0.5 DevOps/SRE, 0.5 security/data. En fases 3-6 sumar SME de planning/cost/project controls.

## Ruta crítica

Identity/domain -> IFC ingestion -> stable element identity -> viewer selection -> element links -> 4D/5D/progress. No construir dashboards “finales” antes de estabilizar semántica y provenance.
