# Feature: model-ingestion

Priority: MUST

## Outcome

Immutable IFC revisions, async parsing, element index, artifact status and error reporting.

## Acceptance baseline

- Tenant isolation is enforced server-side.
- Domain provenance is preserved.
- API/events are versioned.
- Heavy work is asynchronous when applicable.
- Tests and observability are included.

## Non-goals

Do not couple core domain to a vendor-specific SDK.
