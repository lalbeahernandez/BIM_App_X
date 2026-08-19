# Security tests

Automate authorization-matrix tests first. In staging run DAST (e.g. ZAP) and
container/IaC/dependency scanning. Add malicious archive/IFC corpus under private
security fixtures; never publish weaponized samples casually.

## AUD-006 security checklist

Run:

```bash
python scripts/dev.py security-checklist
```

Checklist status values:

- `FUNCTIONAL`: verified by current code or executable tests.
- `PARTIAL`: verified baseline exists, but production hardening is still planned.
- `STUB`: documented extension point; no production implementation yet.

| Check ID | Surface | Expected evidence | Status | Owner |
|---|---|---|---|---|
| SEC-AUD006-TEN-001 | Tenant isolation | Implemented routes filter through `projects.organization_id`; selection resolver has a no-echo test for unscoped IDs. | FUNCTIONAL for implemented endpoints | Foundation / API platform |
| SEC-AUD006-UPL-001 | IFC upload gate | Upload endpoint restricts filenames to `.ifc`, stores under server-generated `revision_id`, records SHA-256, audit and outbox. | PARTIAL | BIM platform / Storage |
| SEC-AUD006-UPL-002 | Upload DoS guard | Upload endpoint enforces current 1 GiB development limit; NFR docs require streaming later. | PARTIAL | BIM platform |
| SEC-AUD006-JOB-001 | Async BIM processing | HTTP request enqueues `bim:ingest`; IfcOpenShell runs only in `services/bim-worker`. | FUNCTIONAL | BIM platform / Workers |
| SEC-AUD006-JOB-002 | Worker failure handling | Worker moves revision to `FAILED` and records bounded error text on exception. | FUNCTIONAL baseline | Workers |
| SEC-AUD006-AUD-001 | Provenance | Project/model writes audit; revision upload writes audit + outbox in the DB transaction. | PARTIAL | Foundation |
| SEC-AUD006-BIM-001 | Stable BIM identity | SQL keeps `UNIQUE (revision_id, global_id)` and `element_lineage` table. | FUNCTIONAL schema / STUB lineage workflow | BIM platform / Data platform |
| SEC-AUD006-API-001 | Request bounds | Selection resolver accepts only 1..1000 UUID IDs via Pydantic. | FUNCTIONAL | API platform |
| SEC-AUD006-FUT-001 | Future auth/RBAC | Real tenant context, RBAC and authorization matrix tests are deferred to FND-001/FND-002/FND-016. | STUB | Foundation |
| SEC-AUD006-FUT-002 | Future upload hardening | MIME sniffing, AV/content scanning, worker sandboxing, streaming upload and immutable object storage are deferred to BIM/FND/ENT tasks. | STUB | Security / BIM / Storage |

The checklist is intentionally not a substitute for production security testing. It is the
AUD-006 baseline that keeps known controls and gaps visible until executable security
suites are added.
