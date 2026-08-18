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

## Identity and revisioning

`BimElement` is revision-scoped: `(revision_id, global_id)` unique. `element_lineage` maps logical continuity across revisions and records match method/confidence/manual override.

## Many-to-many links

Links are first-class tables with provenance:

- `element_boq_links`: source manual/rule/import, rule_id, weight.
- `element_activity_links`: role construct/demolish/temporary/reference, source.
- `element_classifications`: system/code/source/confidence.

## History

Progress, cost revisions, schedule baselines and model revisions are never destructively overwritten. “Current” is a projection over immutable/historic records.
