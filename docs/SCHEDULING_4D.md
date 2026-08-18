# Scheduling / 4D

Modelo mínimo: WBS, Activity, Calendar, ActivityRelation, Constraint, Baseline, DataDate.

Relaciones: FS/SS/FF/SF con lag/lead. El motor debe calcular early/late dates, total/free float y critical path respetando calendarios. Baselines son snapshots inmutables.

4D: `element_activity_links.role` define construct/demolish/temporary/reference. Un resolver temporal genera `NOT_STARTED | IN_PROGRESS | COMPLETE | DELAYED | REMOVED` para una data date/scenario.

Importadores P6/MS Project son adapters; nunca hacer que el domain dependa del formato externo.
