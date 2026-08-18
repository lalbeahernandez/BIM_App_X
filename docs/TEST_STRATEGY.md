# Test strategy

Pirámide pragmática:

- Unit: domain/rules/CPM/math/unidades.
- Integration: PostgreSQL/Redis/object storage con containers.
- Contract: OpenAPI/event schemas + consumer tests.
- BIM golden: fixtures sintéticos y modelos autorizados con hashes/expected facts.
- E2E: upload -> ingest -> viewer index -> link -> Work Area.
- Visual: Gantt/Viewer legends/dashboards.
- Performance: k6 API + viewer benchmark manual/automatable.
- Security: dependency/container scan + DAST staging + authorization matrix tests.

Nunca usar sólo snapshots opacos para lógica de cálculo 4D/5D.
