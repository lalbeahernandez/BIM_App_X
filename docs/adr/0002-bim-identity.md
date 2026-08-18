# ADR-0002: Revision-scoped IFC identity with lineage

Status: Accepted

## Decision

`(revision_id, GlobalId)` es único. La continuidad entre revisiones se representa mediante `element_lineage`, no asumiendo que el GlobalId siempre se conserva.
