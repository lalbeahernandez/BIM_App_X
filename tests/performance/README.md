# Performance Harness

This directory contains lightweight performance smoke checks only. It is not a full load
certification suite.

## k6 health smoke

```bash
k6 run tests/performance/k6-smoke.js
```

Optional environment:

```bash
API_BASE_URL=http://localhost:8000
DATASET_ID=tiny-health-smoke
GIT_COMMIT=<commit>
K6_VUS=5
K6_DURATION=20s
```

The smoke threshold is intentionally small: health p95 below 300 ms and failed request rate
below 1%. It can be a PR gate only when the API service and `k6` are available. Heavier API,
IFC ingest, viewer, geometry and project-controls benchmarks belong to nightly or release
certification tiers described in `docs/PERFORMANCE_BUDGETS.md`.
