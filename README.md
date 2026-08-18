# BIM Control X — Engineering Harness

Starter/harness para construir una plataforma BIM/OpenBIM enterprise con **3D + 4D + 5D + Project Controls + QA/QC + GIS + colaboración**.

> Estado: **harness ejecutable, no producto terminado**. Los componentes marcados `FUNCTIONAL` tienen implementación mínima verificable. Los marcados `ADAPTER/STUB` definen contratos y puntos de extensión para la implementación de producción.

## Arquitectura en una frase

Un **modular monolith** para API y dominio, workers asíncronos para IFC/trabajos pesados, PostgreSQL/PostGIS como system of record, Redis para colas/caché, object storage compatible S3, y un frontend web desacoplado del motor BIM mediante un `ViewerAdapter`.

## Quick start

Requisitos: Docker + Docker Compose v2.

```bash
cp .env.example .env
make dev
```

Servicios:

- Web: http://localhost:3000
- API: http://localhost:8000
- OpenAPI/Swagger: http://localhost:8000/docs
- MinIO console: http://localhost:9001
- PostgreSQL: localhost:5432
- Redis: localhost:6379

Comprobación rápida:

```bash
make smoke
make test
```

## Qué funciona ya

- `FUNCTIONAL`: stack local por Docker Compose.
- `FUNCTIONAL`: API FastAPI con health, proyectos, modelos, revisiones IFC y resolución de selección cruzada.
- `FUNCTIONAL`: esquema SQL central para BIM/BOQ/4D/progreso/issues/QA-QC/auditoría/outbox.
- `FUNCTIONAL`: carga de un IFC a volumen local + encolado Redis.
- `FUNCTIONAL`: worker que intenta parsear IFC con IfcOpenShell y persiste elementos básicos por `GlobalId`.
- `FUNCTIONAL`: demo de Work Area en Next.js con paneles Viewer/BOQ/Gantt y selección cruzada sobre datos demo/API.
- `FUNCTIONAL`: seed data, smoke tests y harness check.
- `FUNCTIONAL`: CI de ejemplo con quality gates.

## Qué es deliberadamente adapter/stub

- `ADAPTER`: renderer BIM web de producción. Se define contrato; debe elegirse tras benchmark.
- `ADAPTER`: object storage S3/MinIO. MinIO está en el stack, pero el primer upload usa un volumen compartido para facilitar desarrollo.
- `ADAPTER`: búsqueda enterprise (OpenSearch/Elastic/Meilisearch/etc.).
- `ADAPTER`: integraciones P6/MS Project/ERP/ACC.
- `ADAPTER`: motor CPM avanzado, EVM completo, clash, diff, IDS, BCF server, geoprocesamiento y motor de reglas.

## Orden recomendado de implementación

1. Foundation + tenancy + audit + contratos.
2. IFC ingest + revisión + índice de elementos.
3. Viewer real + federación + selection resolver.
4. BOQ/QTO + rules + 5D.
5. WBS/CPM + 4D.
6. Progreso + productividad + EVM.
7. BCF/Issues + QA/QC + IDS.
8. Diff/clash + GIS + integraciones.
9. Enterprise hardening, SSO, HA, DR, observabilidad y performance.

Lee primero: `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md` y `.ai/SESSION_BOOTSTRAP.md`.
