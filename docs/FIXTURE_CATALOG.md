# Fixture Catalog - AUD-007

Date: 2026-08-19

## Purpose

This catalog makes repository test data reproducible, auditable and safe to version. It
covers the current BIM Control X harness fixtures for IFC, BOQ, schedule, BCF, domain
schema, API/event contracts, performance checks and golden outputs.

The catalog does not implement BIM ingestion, BOQ, scheduling, Foundation or AUD-008
functionality.

## Fixture Taxonomy

Canonical categories:

| Category | Scope | Owner |
|---|---|---|
| `IFC` | OpenBIM source models and negative model fixtures | BIM platform |
| `BOQ` | Quantity/cost import or expected cost data | Cost/5D |
| `SCHEDULE` | WBS/activity/dependency/progress planning data | Scheduling |
| `BCF` | Issue exchange metadata, viewpoints and component refs | Collaboration/QA |
| `PROGRESS` | Progress history/evidence fixtures | Progress/EVM |
| `SECURITY` | Benign security test descriptors or payload names | Security/Platform |
| `DOMAIN_SCHEMA` | SQL/domain bootstrap and seed data | Architecture/Data |
| `API` | OpenAPI and event-schema contract fixtures | API/Foundation |
| `PERFORMANCE` | k6 or benchmark harness datasets | Performance/QA |
| `GOLDEN_OUTPUT` | Deterministic expected output derived from a source fixture | QA/Data |

Classification statuses:

| Status | Meaning |
|---|---|
| `ACTIVE_FIXTURE` | Versioned artifact available for tests now |
| `GOLDEN_OUTPUT` | Deterministic expected result tied to a source fixture |
| `EXAMPLE` | Documentation/example artifact, not a test authority |
| `PLACEHOLDER` | Legacy or future placeholder; not treated as an active golden |
| `GENERATED` | Generated artifact checked in intentionally |
| `UNKNOWN` | Not acceptable for active fixtures; use only during quarantine |

## Manifest Format

Machine-readable source of truth:

```text
fixtures/manifest.json
```

The manifest uses JSON and schema version `1`. JSON is used deliberately to avoid adding
YAML dependencies for AUD-007.

Each fixture entry records:

```text
id, category, path, description, format, version, source, provenance, license,
redistribution_allowed, sha256, size_bytes, synthetic, contains_customer_data,
contains_personal_data, contains_secrets, deterministic, intended_tests, status
```

Additional fields are allowed when they add concrete value, such as `dataset_class`,
`availability`, `owner`, `source_fixture_id`, `generator`, `schema_version`, `encoding`
or `ifc_schema`.

## IDs

Fixture IDs are stable logical identifiers and must not be derived only from filenames.
Current examples:

```text
IFC-TINY-001
BOQ-TINY-001
SCH-TINY-001
BCF-TINY-001
DOMAIN-SCHEMA-001
GOLDEN-DOMAIN-001
```

Renaming a physical file does not necessarily require changing the fixture ID. Changing
the semantic content may require a new logical version and updated checksum.

## Provenance

Allowed provenance values:

```text
SYNTHETIC
GENERATED_IN_REPOSITORY
PUBLIC_OPEN_DATA
PUBLIC_STANDARD_EXAMPLE
THIRD_PARTY_LICENSED
QUARANTINED
```

Active fixtures must not use ambiguous provenance. If provenance cannot be proven, mark
the artifact `QUARANTINED` and do not use it as a golden source until resolved.

Current catalog result: no `UNKNOWN` or `QUARANTINED` fixtures.

## Licensing

Repository-owned synthetic data is redistributable inside this repository. Any future
fixture from outside the repository must record:

```text
source
license
redistribution_allowed
provenance
```

Do not add internet-downloaded or third-party project files without explicit license and
redistribution evidence.

## Checksums

Every physical fixture entry has a SHA-256 calculated from the exact file bytes. Do not
invent checksums and do not hash transformed content.

To list current bytes and hashes:

```bash
python scripts/check_fixtures.py --print-checksums
```

The fixture logical version and file checksum are different concepts:

- metadata-only documentation edits do not necessarily change fixture version;
- changing file bytes always requires a checksum update;
- semantic fixture changes should also review whether `version` must change.

## Sensitive-Data Policy

Rule:

```text
NO CUSTOMER DATA IN VERSIONED FIXTURES
```

Active versioned fixtures must declare:

```text
contains_customer_data = false
contains_personal_data = false
contains_secrets = false
```

AUD-007 inspection searched for obvious emails, credentials, private tokens, corporate
paths and non-example URLs in fixtures/tests/specs/db/script test surfaces. No obvious
sensitive data was found. This is a reasonable static/manual inspection, not a forensic
DLP certification.

## Security Fixture Policy

Security fixtures must be benign. Allowed examples include synthetic filenames with
path traversal markers, invalid UUID strings, fake oversized descriptors and explicitly
fake tokens such as `fake-token` or `example.invalid`.

Do not commit malware, weaponized parser exploits, real credentials or customer files.

Current catalog result: no active security fixture file exists yet; security fixture
needs are documented by AUD-006 and future FND/ENT tasks.

## Golden Outputs

A golden output is:

```text
a deterministic expected result, versioned in the repository, produced from a known
source fixture.
```

Goldens must record `source_fixture_id`. When applicable they also record generator,
schema version and checksum.

Current active golden:

| Golden ID | Source | Purpose |
|---|---|---|
| `GOLDEN-DOMAIN-001` | `DOMAIN-SCHEMA-001` | Expected structural summary for `db/init/010_schema.sql` |

`fixtures/golden/manifest.json` remains cataloged as a legacy `PLACEHOLDER` because
`scripts/verify_harness.py` still checks it for baseline harness compatibility.

## Determinism

The determinism rule is:

```text
same fixture + same implementation = same normalized golden output
```

Normalize only inherently variable values when appropriate, such as timestamps, random
UUIDs generated during tests, temp paths and OS-specific separators. Do not normalize
away meaningful data changes.

Do not create goldens from current timestamps, random UUIDs, absolute paths or unstable
query ordering unless the output is intentionally normalized and reviewed.

## Performance Dataset Mapping

AUD-005 defines `TINY`, `SMALL`, `MEDIUM` and `LARGE` dataset classes.

| Dataset class | Current status | Current fixture IDs |
|---|---|---|
| `TINY` | `AVAILABLE` | `IFC-TINY-001`, `BOQ-TINY-001`, `SCH-TINY-001`, `BCF-TINY-001`, `DOMAIN-SEED-001` |
| `SMALL` | `SPECIFIED_NOT_AVAILABLE` | None |
| `MEDIUM` | `SPECIFIED_NOT_AVAILABLE` | None |
| `LARGE` | `SPECIFIED_NOT_AVAILABLE` | None |

Do not commit artificial MEDIUM/LARGE binaries to make the catalog look complete. Larger
datasets should be specified by metadata until licensing, generation and storage strategy
are intentionally decided.

## Adding A Fixture

1. Prefer synthetic data generated inside the repository.
2. Keep the file small unless a task explicitly authorizes a larger dataset.
3. Place it under an appropriate fixture or test-data path.
4. Assign a stable logical ID.
5. Record provenance, license, redistribution, privacy flags and intended tests.
6. Calculate SHA-256 over the exact bytes.
7. Run `python scripts/dev.py fixtures`.
8. Review the diff for secrets, customer data and accidental binary bloat.

## Updating A Fixture

When fixture bytes change:

1. explain what changed and why in the PR;
2. update `sha256` and `size_bytes`;
3. review whether the logical `version` changes;
4. update affected goldens intentionally;
5. run all fixture and relevant domain tests.

Do not rewrite fixtures silently from failing tests.

## Updating Golden Outputs

Goldens are not automatically regenerated just because a test fails. Updating a golden
requires:

1. intentional behavior/schema change;
2. reviewed diff of the golden output;
3. explanation of expected impact;
4. checksum update in `fixtures/manifest.json`;
5. explicit reviewer acceptance.

Never implement `test fails -> silently rewrite expected output`.

## Current Inventory

Current manifest inventory:

| ID | Category | Status | Dataset | Path |
|---|---|---|---|---|
| `IFC-TINY-001` | `IFC` | `ACTIVE_FIXTURE` | `TINY` | `fixtures/ifc/tiny.ifc` |
| `BOQ-TINY-001` | `BOQ` | `ACTIVE_FIXTURE` | `TINY` | `fixtures/boq/demo_boq.csv` |
| `SCH-TINY-001` | `SCHEDULE` | `ACTIVE_FIXTURE` | `TINY` | `fixtures/schedules/demo_schedule.csv` |
| `BCF-TINY-001` | `BCF` | `ACTIVE_FIXTURE` | `TINY` | `fixtures/bcf/sample.bcfzip` |
| `DOMAIN-SCHEMA-001` | `DOMAIN_SCHEMA` | `ACTIVE_FIXTURE` | `TINY` | `db/init/010_schema.sql` |
| `DOMAIN-SEED-001` | `DOMAIN_SCHEMA` | `ACTIVE_FIXTURE` | `TINY` | `db/init/020_seed.sql` |
| `API-OPENAPI-001` | `API` | `ACTIVE_FIXTURE` | `TINY` | `specs/openapi.yaml` |
| `API-EVENT-001` | `API` | `ACTIVE_FIXTURE` | `TINY` | `specs/events/domain-event-envelope.schema.json` |
| `API-EVENT-002` | `API` | `ACTIVE_FIXTURE` | `TINY` | `specs/events/model-revision-ingest-requested.schema.json` |
| `PERF-K6-001` | `PERFORMANCE` | `ACTIVE_FIXTURE` | `TINY` | `tests/performance/k6-smoke.js` |
| `GOLDEN-LEGACY-MANIFEST-001` | `GOLDEN_OUTPUT` | `PLACEHOLDER` | `TINY` | `fixtures/golden/manifest.json` |
| `GOLDEN-DOMAIN-001` | `GOLDEN_OUTPUT` | `GOLDEN_OUTPUT` | `TINY` | `fixtures/golden/domain-schema-summary.v1.json` |

Inventory counts:

- fixtures/entries: 12
- active golden outputs: 1
- legacy golden placeholders: 1
- categories represented: 7 of 10

## Missing Datasets / Gaps

| Gap | Classification | Notes |
|---|---|---|
| No SMALL/MEDIUM/LARGE physical datasets | MEASUREMENT/DATASET GAP | Keep specified as unavailable until generated/licensed. |
| No progress fixture yet | P2 | Progress workflows are not implemented yet. |
| No active security fixture file yet | P2 | Security policy exists; future authorization/upload tests should add benign fixtures. |
| IFC fixture is minimal | P2 | It has one wall and containment only; future BIM golden suite needs richer IFC cases. |
| BCF fixture has no viewpoint/snapshot | P2 | Suitable only as tiny BCF metadata baseline. |
| Legacy golden manifest remains | P2 | Kept for `verify_harness.py` compatibility; not an active golden. |

No P0 provenance, licensing or privacy blocker is open after AUD-007.
