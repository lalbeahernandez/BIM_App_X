# Feature: boq-5d

Priority: MUST

## Outcome

Rule-based takeoff, BOQ hierarchy, cost revisions, rates and provenance.

## Acceptance baseline

- Tenant isolation is enforced server-side.
- Domain provenance is preserved.
- API/events are versioned.
- Heavy work is asynchronous when applicable.
- Tests and observability are included.

## Non-goals

Do not couple core domain to a vendor-specific SDK.
