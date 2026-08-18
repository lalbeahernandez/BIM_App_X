# Domain model

Canonical chain:

```text
Organization -> Project
Project -> Model -> ModelRevision -> BimElement
BimElement <-> ClassificationNode
BimElement -> Quantity
BimElement <-> BoqItem -> CostRevision/Rate
Project -> WbsNode -> Activity -> ActivityRelation
BimElement <-> Activity
Activity <-> Resource/Crew/ProductivityRate
Activity -> ProgressRecord
BimElement/Activity -> Issue -> Comment/Viewpoint
BimElement/Activity -> Inspection/NCR/Punch
```

This document describes the target domain vocabulary and calls out the current harness
implementation where it is intentionally smaller than the target model.

## Identity and revisioning

`BimElement` is revision-scoped: `(revision_id, global_id)` is unique. `element_lineage`
maps logical continuity across revisions and records match method, confidence and manual
approval provenance.

Current implementation:

- `bim_elements.id` is the internal database UUID primary key.
- `bim_elements.global_id` is scoped by `revision_id` through `UNIQUE (revision_id, global_id)`.
- `element_lineage` exists as the continuity table; matching workflows are planned future work.
- `model_revisions` records source file metadata and status. The source artifact is treated
  as immutable, even though the current harness stores it through a development upload volume
  rather than the final object storage adapter.

## Many-to-many links

Links are first-class tables with provenance:

- `element_boq_links`: source manual/rule/import, rule_id, weight.
- `element_activity_links`: role construct/demolish/temporary/reference, source.
- `element_classifications`: system/code/source/confidence.

These links must not be collapsed into single foreign keys on `bim_elements`; doing so would
destroy many-to-many semantics and provenance.

## History

Progress, cost revisions, schedule baselines and model revisions are never destructively
overwritten. "Current" is a projection over immutable or historic records.

Current implementation:

- `progress_records` is the append-only conceptual source for progress history.
- `activities.percent_complete` is a temporary current-state projection/cache for the starter
  Work Area. It must not become the only source of progress truth as progress workflows evolve.
- BOQ revisioning is currently simplified with `boq_items.revision` and
  `UNIQUE (project_id, code, revision)`.
- Schedule baseline entities are not implemented yet; current activity planning fields
  represent the starter schedule surface only.
- Audit and outbox rows are append-oriented operational records, not ordinary mutable
  business state.
